#!/usr/bin/env python3
"""
Scout (OpenAI-compatible) Automated PR Accessibility Review Script

Env required:
- PR_NUMBER
- GITHUB_TOKEN
- FRAMEWORK_PATH (optional)

Scout env:
- SCOUT_API_KEY
- SCOUT_BASE_URL  (OpenAI compatibility base url, must end with /v1)
- SCOUT_MODEL     (e.g. gpt-4-1-mini)
Optional:
- SCOUT_MAX_TOKENS (default 8000)
- SCOUT_TEMPERATURE (default 0)
"""

import os
import sys
import json
import subprocess
from pathlib import Path


# --- GitHub / CI env ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
PR_NUMBER = os.environ.get("PR_NUMBER")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
FRAMEWORK_PATH = os.environ.get("FRAMEWORK_PATH", "/tmp/accessibility-fixer")

# --- Scout env (OpenAI-compatible) ---
SCOUT_API_KEY = os.environ.get("SCOUT_API_KEY")
SCOUT_BASE_URL = os.environ.get("SCOUT_BASE_URL")  # ex: https://.../v1
SCOUT_MODEL = os.environ.get("SCOUT_MODEL", "gpt-4-1-mini")
SCOUT_MAX_TOKENS = int(os.environ.get("SCOUT_MAX_TOKENS", "8000"))
SCOUT_TEMPERATURE = float(os.environ.get("SCOUT_TEMPERATURE", "0"))

# Exit codes
EXIT_SUCCESS = 0
EXIT_CRITICAL_ISSUES = 1
EXIT_HIGH_PRIORITY = 2


def run_command(cmd, capture_output=True):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True
    )
    return result.stdout.strip() if capture_output else None


def get_pr_diff():
    print(f"📥 Fetching PR #{PR_NUMBER} diff...")
    return run_command(f"gh pr diff {PR_NUMBER}")


def get_pr_files():
    print("📄 Getting changed files...")
    files_json = run_command(f"gh pr view {PR_NUMBER} --json files")
    files_data = json.loads(files_json)
    return [f["path"] for f in files_data.get("files", [])]


def detect_platforms(files):
    platforms = set()
    for file in files:
        ext = Path(file).suffix.lower()
        if ext in [".swift", ".m", ".mm"]:
            platforms.add("iOS")
        elif ext in [".kt", ".java"]:
            platforms.add("Android")
        elif ext in [".tsx", ".jsx", ".ts", ".js", ".html", ".css"]:
            platforms.add("Web")
        elif ext == ".dart":
            platforms.add("Flutter")
    return list(platforms)


def load_guides(platforms):
    guides = {}
    framework_path = Path(FRAMEWORK_PATH)

    core_guides = [
        "guides/GUIDE_WCAG_REFERENCE.md",
        "guides/wcag/QUICK_LOOKUP.md",
        "guides/wcag/SEVERITY_GUIDELINES.md",
        "guides/COMMON_ISSUES.md",
    ]

    print("📚 Loading accessibility guides...")

    for guide_path in core_guides:
        full_path = framework_path / guide_path
        if full_path.exists():
            with open(full_path, "r") as f:
                guides[guide_path] = f.read()

    platform_guide_map = {
        "iOS": "guides/GUIDE_IOS.md",
        "Android": "guides/GUIDE_ANDROID.md",
        "Web": "guides/GUIDE_WEB.md",
        "Flutter": "guides/GUIDE_FLUTTER.md",
    }

    for platform in platforms:
        guide_path = platform_guide_map.get(platform)
        if guide_path:
            full_path = framework_path / guide_path
            if full_path.exists():
                with open(full_path, "r") as f:
                    guides[guide_path] = f.read()

    return guides


def create_review_prompt(pr_diff, files, platforms, guides):
    guides_text = "\n\n".join([f"## {path}\n\n{content}" for path, content in guides.items()])
    files_list = "\n".join([f"- {f}" for f in files])
    platforms_list = ", ".join(platforms) if platforms else "Unknown"

    return f"""You are performing an automated accessibility review on a GitHub Pull Request.

# PR Information
**Platforms detected:** {platforms_list}
**Files changed:** {len(files)}
{files_list}

# Your Task
Review ONLY the changed code in this PR for accessibility issues. Focus on:
1. New UI components, labels/hints/roles
2. Modified accessibility properties
3. Interactive elements
4. Images/icons alt text / content descriptions
5. Semantic text/labels
6. Form inputs labels/errors
7. Touch targets
8. Contrast

# Guidelines to Follow
{guides_text}

# PR Diff
```diff
{pr_diff}
