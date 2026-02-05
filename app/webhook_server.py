"""
GitHub App Webhook Server

Receives webhook events from GitHub and orchestrates accessibility reviews.
"""

import os
import hmac
import hashlib
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from app.github_app_auth import create_auth_from_env
from app.guide_loader import GuideLoader
from app.pr_reviewer import create_reviewer_from_env, PRReviewer
from app.comment_poster import CommentPoster
from app.sarif_generator import generate_and_write_sarif

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
PORT = int(os.getenv("PORT", "8080"))

# Initialize components
github_auth = create_auth_from_env()
pr_reviewer = create_reviewer_from_env()
guide_loader = GuideLoader()

# Create reviewer config dict for debug footer
reviewer_config = None
if pr_reviewer:
    reviewer_config = {
        "model": pr_reviewer.model,
        "base_url": os.getenv("SCOUT_BASE_URL", ""),
        "files_per_batch": pr_reviewer.files_per_batch,
        "max_diff_chars": pr_reviewer.max_diff_chars,
    }

comment_poster = CommentPoster(reviewer_config=reviewer_config)


def filter_reviewable_files(files: list) -> list:
    """
    Filter out files that should not be reviewed for accessibility.

    Only review UI code files. Exclude:
    - Documentation (*.md)
    - Build/config files (gradle, json, yaml, plist, properties, etc.)
    - Project files (xcodeproj, xcworkspace, etc.)
    - CI/CD files (.github/workflows/*)

    Special handling for XML:
    - Include: Android layout files (res/layout/**/*.xml)
    - Exclude: AndroidManifest.xml, config XMLs, gradle XMLs

    Args:
        files: List of file paths

    Returns:
        Filtered list of reviewable file paths
    """
    excluded_extensions = {
        # Documentation
        ".md",
        ".txt",
        # Build/config files
        ".gradle",
        ".properties",
        ".json",  # Config files (google-services.json, etc.)
        ".yaml",
        ".yml",
        ".plist",  # iOS config
        # Project/IDE files
        ".pbxproj",  # Xcode project
        ".xcworkspace",
        ".xcscheme",
        # Other
        ".gitignore",
        ".disabled",
    }

    excluded_directories = {
        ".github",  # GitHub workflows and config
        "gradle/wrapper",  # Gradle wrapper files
        ".xcodeproj",  # Xcode project directory
        ".xcworkspace",  # Xcode workspace
        "build",  # Build output
        "dist",  # Distribution files
    }

    excluded_filenames = {
        "gradle.properties",
        "gradlew",
        "gradlew.bat",
        "google-services.json",
        "Info.plist",
        "Podfile",
        "Podfile.lock",
        "AndroidManifest.xml",  # Exclude Android manifest
    }

    excluded_patterns = [
        "settings.gradle",
        ".gradle.kts",
        "/wrapper/",  # Gradle wrapper
    ]

    # XML files to exclude (config/build files)
    excluded_xml_patterns = [
        "/res/values/",  # String/color/dimen resources
        "/res/drawable/",  # Drawable resources
        "/res/mipmap/",  # Mipmap resources
        "/res/xml/",  # XML preferences/configs
        "/res/raw/",  # Raw resources
        "/res/menu/",  # Menu resources
        "/res/anim/",  # Animation resources
        "/res/animator/",  # Animator resources
        "/res/color/",  # Color state lists
        "/res/font/",  # Font resources
        "gradle/",  # Gradle build files
        "maven/",  # Maven build files
    ]

    reviewable = []
    for file_path in files:
        filename = file_path.split("/")[-1]

        # Check if file is in excluded directory
        if any(
            f"/{excluded_dir}/" in file_path or file_path.startswith(f"{excluded_dir}/")
            for excluded_dir in excluded_directories
        ):
            logger.info(
                f"Skipping non-reviewable file: {file_path} (excluded directory)"
            )
            continue

        # Special handling for XML files
        if file_path.endswith(".xml"):
            # Check if it's an excluded filename
            if filename in excluded_filenames:
                logger.info(
                    f"Skipping non-reviewable file: {file_path} (excluded XML file)"
                )
                continue

            # Check if it's in an excluded XML directory
            if any(pattern in file_path for pattern in excluded_xml_patterns):
                logger.info(
                    f"Skipping non-reviewable file: {file_path} (excluded XML type)"
                )
                continue

            # Include Android layout XML files
            if "/res/layout/" in file_path or "/res/layout-" in file_path:
                logger.info(f"Including Android layout file: {file_path}")
                reviewable.append(file_path)
                continue

            # Exclude other XML files
            logger.info(f"Skipping non-reviewable file: {file_path} (non-layout XML)")
            continue

        # Check file extension
        if any(file_path.endswith(ext) for ext in excluded_extensions):
            logger.info(
                f"Skipping non-reviewable file: {file_path} (excluded extension)"
            )
            continue

        # Check exact filename matches
        if filename in excluded_filenames:
            logger.info(
                f"Skipping non-reviewable file: {file_path} (excluded filename)"
            )
            continue

        # Check pattern matches
        if any(pattern in file_path for pattern in excluded_patterns):
            logger.info(f"Skipping non-reviewable file: {file_path} (excluded pattern)")
            continue

        reviewable.append(file_path)

    return reviewable


def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verify webhook signature from GitHub.

    Args:
        payload_body: Raw request body
        signature_header: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set - skipping signature verification")
        return True

    if not signature_header:
        logger.error("No signature header provided")
        return False

    # Extract signature
    hash_name, signature = signature_header.split("=")
    if hash_name != "sha256":
        logger.error(f"Unsupported hash algorithm: {hash_name}")
        return False

    # Compute expected signature
    mac = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    )
    expected_signature = mac.hexdigest()

    # Compare signatures
    return hmac.compare_digest(expected_signature, signature)


def get_pr_diff(
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    base_sha: str,
    head_sha: str,
    headers: dict,
) -> str:
    """
    Get PR diff from GitHub API.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        pr_number: PR number
        base_sha: Base commit SHA
        head_sha: Head commit SHA
        headers: Headers with authorization

    Returns:
        Diff string
    """
    # Get diff using compare API
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/compare/{base_sha}...{head_sha}"
    headers_with_diff = dict(headers)
    headers_with_diff["Accept"] = "application/vnd.github.v3.diff"

    try:
        response = requests.get(url, headers=headers_with_diff)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching PR diff: {e}")
        return ""


@app.route("/", methods=["GET"])
def index():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "ok",
            "service": "accessibility-reviewer",
            "version": "1.0.0",
        }
    )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    checks = {
        "webhook_secret": bool(WEBHOOK_SECRET),
        "github_auth": github_auth is not None,
        "pr_reviewer": pr_reviewer is not None,
    }

    all_ok = all(checks.values())

    return jsonify(
        {
            "status": "healthy" if all_ok else "degraded",
            "checks": checks,
        }
    ), (200 if all_ok else 503)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Webhook endpoint for GitHub events.
    """
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_webhook_signature(request.data, signature):
        logger.error("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 401

    # Parse event
    event_type = request.headers.get("X-GitHub-Event", "")
    payload = request.json

    logger.info(f"Received webhook: {event_type}")

    # Handle pull_request events
    if event_type == "pull_request":
        return handle_pull_request(payload)

    # Ignore other events
    return jsonify({"message": "Event ignored"}), 200


def handle_pull_request(payload: dict):
    """
    Handle pull_request webhook event.

    Args:
        payload: Webhook payload

    Returns:
        Flask response
    """
    action = payload.get("action", "")
    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})
    installation_id = payload.get("installation", {}).get("id")

    # Only process opened, synchronize, reopened
    if action not in ["opened", "synchronize", "reopened"]:
        logger.info(f"Ignoring PR action: {action}")
        return jsonify({"message": "Action ignored"}), 200

    # Extract data
    repo_owner = repo_data.get("owner", {}).get("login", "")
    repo_name = repo_data.get("name", "")
    pr_number = pr_data.get("number")
    pr_title = pr_data.get("title", "")
    base_sha = pr_data.get("base", {}).get("sha", "")
    head_sha = pr_data.get("head", {}).get("sha", "")

    logger.info(f"Processing PR #{pr_number}: {pr_title}")
    logger.info(f"Repository: {repo_owner}/{repo_name}")
    logger.info(f"Base SHA: {base_sha}, Head SHA: {head_sha}")

    # Validate components
    if not github_auth:
        logger.error("GitHub auth not configured")
        return jsonify({"error": "GitHub auth not configured"}), 500

    if not pr_reviewer:
        logger.error("PR reviewer not configured")
        return jsonify({"error": "PR reviewer not configured"}), 500

    if not installation_id:
        logger.error("No installation ID in payload")
        return jsonify({"error": "No installation ID"}), 400

    try:
        # Get installation token
        headers = github_auth.get_authenticated_headers(installation_id)

        # Post pending status
        comment_poster.post_commit_status(
            repo_owner,
            repo_name,
            head_sha,
            "pending",
            "Accessibility review in progress...",
            headers,
        )

        # Get changed files
        files_url = pr_data.get("url", "") + "/files"
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        all_files = [f["filename"] for f in files_data]

        # Filter out non-reviewable files (docs, build config, etc.)
        changed_files = filter_reviewable_files(all_files)

        logger.info(
            f"Changed files: {len(changed_files)} (filtered from {len(all_files)} total)"
        )

        # Exit early if no reviewable files
        if not changed_files:
            logger.info("No reviewable files found after filtering. Skipping review.")
            set_commit_status(
                repo_owner,
                repo_name,
                head_sha,
                "success",
                "No reviewable files (docs/config only)",
                headers,
            )
            return jsonify({"message": "No reviewable files"}), 200

        # Detect platforms
        platforms = PRReviewer.detect_platforms(changed_files)
        logger.info(f"Detected platforms: {platforms}")

        # Load guides
        logger.info("Loading accessibility guides...")
        guides = guide_loader.load_platform_specific_guides(platforms)
        logger.info(f"Loaded guides: {len(guides)} characters")

        # Get PR diff
        logger.info("Fetching PR diff...")
        pr_diff = get_pr_diff(
            repo_owner, repo_name, pr_number, base_sha, head_sha, headers
        )
        logger.info(f"Diff size: {len(pr_diff)} characters")

        # Track all issues and posted locations for final status
        all_issues = []
        # Fetch existing comments once at the start to avoid re-posting
        existing_locations = comment_poster._get_existing_comment_locations(
            repo_owner, repo_name, pr_number, headers
        )
        logger.info(f"Found {len(existing_locations)} existing comment locations")
        posted_locations = set(existing_locations)  # Track what we've posted

        # Fetch review threads including replies for AI to validate resolutions
        review_threads = comment_poster.get_review_threads(
            repo_owner, repo_name, pr_number, headers
        )
        logger.info(
            f"Found {len(review_threads)} review threads (for resolution validation)"
        )

        def is_near_existing_comment(
            file_path: str, 
            line: int, 
            issue: Dict = None,
            range_threshold: int = 5
        ) -> tuple:
            """
            Check if a location is near any existing comment AND if it's the same issue.
            
            This refined logic prevents suppressing corrected anchors while still avoiding
            true duplicates. It checks:
            1. Same file AND same issue identity (title match or anchor signature match)
            2. Proximity alone is NOT sufficient to suppress
            
            Supports multiple entry shapes in posted_locations:
            - 2-tuples: (file, line)
            - 3+ tuples: (file, line, body_snippet, ...) - body_snippet used for title matching
            - dicts: {'file': ..., 'line': ...} or {'path': ..., 'line': ...}
            - Malformed entries are skipped safely
            
            Args:
                file_path: File path of the issue to check
                line: Line number of the issue to check
                issue: Issue dict with title, anchor_text, etc. (optional for backward compat)
                range_threshold: Line distance threshold (default: 5)
                
            Returns:
                Tuple of (should_skip: bool, skip_reason: str, matched_entry: dict or None)
            """
            # Extract issue identity for matching
            issue_title = ""
            issue_anchor = ""
            if issue:
                issue_title = str(issue.get("title", "")).strip()[:50].lower()
                # Get anchor signature
                if issue.get("_anchor_matched_text"):
                    issue_anchor = str(issue.get("_anchor_matched_text", "")).strip().lower()
                elif issue.get("anchor_text"):
                    issue_anchor = str(issue.get("anchor_text", "")).strip().lower()
            
            for entry in posted_locations:
                try:
                    # Parse entry based on type
                    existing_file = None
                    existing_line = None
                    existing_snippet = ""
                    
                    # Handle dictionary entries
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        existing_snippet = entry.get("snippet", "")
                        if not existing_file or not existing_line:
                            continue
                    # Handle tuple/list entries with 2+ values
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                        # Extract body snippet if available (3rd element)
                        if len(entry) >= 3:
                            existing_snippet = str(entry[2]) if entry[2] else ""
                    else:
                        # Skip malformed entries
                        continue

                    # Check if same file
                    if existing_file != file_path:
                        continue
                    
                    # Calculate distance
                    distance = abs(existing_line - line)
                    
                    # Check if within range
                    if distance > range_threshold:
                        continue
                    
                    # Within range - now check if it's the SAME issue
                    is_same_issue = False
                    match_reason = ""
                    
                    # If we have issue metadata, check for identity match
                    if issue and (issue_title or issue_anchor):
                        # Normalize existing snippet for comparison
                        existing_title = existing_snippet.strip()[:50].lower()
                        
                        # Check title match
                        if issue_title and existing_title:
                            # Fuzzy match: check if titles are similar enough
                            # (at least 30 chars match or 80% of shorter title)
                            if issue_title == existing_title:
                                is_same_issue = True
                                match_reason = "exact title match"
                            elif len(issue_title) >= 30 and len(existing_title) >= 30:
                                # For longer titles, check prefix match
                                min_len = min(len(issue_title), len(existing_title))
                                threshold = int(min_len * 0.8)
                                if issue_title[:threshold] == existing_title[:threshold]:
                                    is_same_issue = True
                                    match_reason = "fuzzy title match"
                        
                        # Check anchor match (if title didn't match)
                        if not is_same_issue and issue_anchor and existing_snippet:
                            # Check if anchor text appears in existing snippet
                            # Normalize both for comparison
                            anchor_normalized = "".join(issue_anchor.split()).lower()[:40]
                            snippet_normalized = "".join(existing_snippet.split()).lower()
                            
                            # Try substring match
                            if anchor_normalized and len(anchor_normalized) >= 3:
                                if anchor_normalized in snippet_normalized:
                                    is_same_issue = True
                                    match_reason = "anchor signature match"
                            
                            # Also try matching just the keyword (before parenthesis or special chars)
                            if not is_same_issue and anchor_normalized:
                                # Extract keyword: take alphanumeric part before special chars
                                import re
                                keyword_match = re.match(r'^([a-z0-9_]+)', anchor_normalized)
                                if keyword_match:
                                    keyword = keyword_match.group(1)
                                    if len(keyword) >= 4 and keyword in snippet_normalized:
                                        is_same_issue = True
                                        match_reason = "anchor signature match"
                    
                    # If same issue detected, skip it
                    if is_same_issue:
                        matched_entry = {
                            "file": existing_file,
                            "line": existing_line,
                            "distance": distance,
                            "snippet": existing_snippet[:100],
                        }
                        return (True, match_reason, matched_entry)
                    
                    # Within range but NOT same issue - this is likely a corrected anchor
                    # or different issue at nearby location. Do NOT suppress.
                    logger.debug(
                        f"Location {file_path}:{line} is near {existing_file}:{existing_line} "
                        f"(distance={distance}) but appears to be a different issue. Not suppressing."
                    )
                    
                except (TypeError, ValueError, IndexError, AttributeError):
                    # Skip malformed entries safely
                    continue
            
            # No matching existing comment found
            return (False, "", None)

        def post_batch_comments(issues):
            """Callback to post comments progressively as batches complete."""
            nonlocal all_issues, posted_locations

            # Filter out issues at locations we've already posted or near existing comments
            new_issues = []
            for issue in issues:
                file_path = issue.get("file", "")
                line = issue.get("line", 0)
                issue_title = issue.get("title", "Unknown")
                resolved_line = issue.get("_resolved_line")  # May be set by semantic anchor
                location = (file_path, line)

                # Check exact match first
                if location in posted_locations:
                    logger.info(f"Skipping already posted location: {file_path}:{line}")
                    continue

                # Check for nearby existing comments with smart identity matching
                should_skip, skip_reason, matched_entry = is_near_existing_comment(
                    file_path, line, issue
                )
                
                if should_skip:
                    # Log detailed skip information
                    matched_info = ""
                    if matched_entry:
                        matched_info = (
                            f"{matched_entry['file']}:{matched_entry['line']} "
                            f"(distance={matched_entry['distance']} lines)"
                        )
                        if matched_entry.get('snippet'):
                            matched_info += f" snippet='{matched_entry['snippet'][:50]}...'"
                    
                    logger.info(
                        f"Skipping issue at {file_path}:{line} - Title: '{issue_title[:60]}' "
                        f"| Proposed line: {line}"
                        + (f" | Resolved line: {resolved_line}" if resolved_line else "")
                        + f" | Reason: {skip_reason} with existing comment at {matched_info}"
                    )
                    continue

                # This is a new location, add it
                new_issues.append(issue)
                posted_locations.add(location)

            if not new_issues:
                logger.info("All issues in this batch already posted, skipping")
                return

            all_issues.extend(new_issues)
            logger.info(
                f"Posting {len(new_issues)} new comments from batch (total posted: {len(all_issues)})..."
            )
            comment_poster.post_review_comments(
                repo_owner,
                repo_name,
                pr_number,
                head_sha,
                new_issues,
                headers,
                skip_existing_check=True,  # We already filtered above
            )

        # Review PR with progressive commenting
        logger.info("Starting accessibility review...")
        remaining_issues = pr_reviewer.review_pr_diff(
            pr_diff,
            changed_files,
            platforms,
            guides,
            on_batch_complete=post_batch_comments,
            existing_comments=list(existing_locations),
            review_threads=review_threads,
        )

        # Add any remaining issues (if callback wasn't used)
        if remaining_issues:
            all_issues.extend(remaining_issues)

        logger.info(
            f"Review complete. Found {len(all_issues)} total accessibility issues"
        )

        # Generate SARIF output if requested
        if os.getenv("OUTPUT_SARIF", "").lower() in ["1", "true", "yes"]:
            sarif_path = os.getenv("SARIF_OUTPUT_PATH", "accessibility-report.sarif")
            repo_uri = f"https://github.com/{repo_owner}/{repo_name}"

            logger.info(f"Generating SARIF report to {sarif_path}...")
            sarif_success = generate_and_write_sarif(
                all_issues,
                sarif_path,
                repo_uri=repo_uri,
                repo_ref=head_sha,
            )

            if sarif_success:
                logger.info(f"✅ SARIF report generated: {sarif_path}")
            else:
                logger.warning(f"⚠️  Failed to generate SARIF report")

        # Determine final status based on severities
        if all_issues:
            severity_counts = comment_poster._count_severities(all_issues)
            critical_count = severity_counts.get("Critical", 0)
            high_count = severity_counts.get("High", 0)

            if critical_count > 0:
                status = "failure"
                description = f"Found {critical_count} critical accessibility issue(s)"
            elif high_count > 0:
                status = "success"  # Don't block on high priority
                description = f"Found {high_count} high priority issue(s)"
            else:
                status = "success"
                description = f"Found {len(all_issues)} accessibility issue(s)"

            comment_poster.post_commit_status(
                repo_owner, repo_name, head_sha, status, description, headers
            )
        else:
            logger.info("No issues found - posting success status")
            comment_poster.post_commit_status(
                repo_owner,
                repo_name,
                head_sha,
                "success",
                "No accessibility issues found",
                headers,
            )

        logger.info("✅ Review complete")

        return (
            jsonify(
                {
                    "message": "Review complete",
                    "issues_found": len(all_issues),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error processing PR: {e}", exc_info=True)

        # Try to post error status
        try:
            if github_auth and installation_id:
                headers = github_auth.get_authenticated_headers(installation_id)
                comment_poster.post_commit_status(
                    repo_owner,
                    repo_name,
                    head_sha,
                    "error",
                    f"Review failed: {str(e)[:100]}",
                    headers,
                )
        except Exception:
            pass

        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info("Starting Accessibility Reviewer GitHub App")
    logger.info(f"Port: {PORT}")
    logger.info(f"Webhook secret configured: {bool(WEBHOOK_SECRET)}")
    logger.info(f"GitHub auth configured: {github_auth is not None}")
    logger.info(f"PR reviewer configured: {pr_reviewer is not None}")

    app.run(host="0.0.0.0", port=PORT, debug=False)
