#!/usr/bin/env python3
"""
Multi-Provider Automated PR Accessibility Review Script
Supports: Anthropic Claude, GitHub Models (OpenAI, etc.)
Uses AI APIs directly to review PRs for accessibility issues.
Designed to run in CI/CD without Claude Code CLI.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Configuration
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'anthropic').lower()  # 'anthropic' or 'github'
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Optional, for non-GitHub OpenAI
PR_NUMBER = os.environ.get('PR_NUMBER')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY', '')
FRAMEWORK_PATH = os.environ.get('FRAMEWORK_PATH', '/tmp/accessibility-fixer')

# Model configuration
AI_MODELS = {
    'anthropic': {
        'model': os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514'),
        'max_tokens': 8000,
        'library': 'anthropic'
    },
    'github': {
        'model': os.environ.get('GITHUB_MODEL', 'gpt-4o'),  # or 'claude-3-5-sonnet'
        'max_tokens': 8000,
        'library': 'openai',
        'base_url': 'https://models.inference.ai.azure.com'
    },
    'openai': {
        'model': os.environ.get('OPENAI_MODEL', 'gpt-4'),
        'max_tokens': 8000,
        'library': 'openai',
        'base_url': None  # Use default OpenAI endpoint
    }
}

# Exit codes
EXIT_SUCCESS = 0
EXIT_CRITICAL_ISSUES = 1
EXIT_HIGH_PRIORITY = 2

def run_command(cmd, capture_output=True):
    """Run a shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True
    )
    return result.stdout.strip() if capture_output else None

def get_pr_diff():
    """Get the PR diff using GitHub CLI."""
    print(f"📥 Fetching PR #{PR_NUMBER} diff...")
    diff = run_command(f"gh pr diff {PR_NUMBER}")
    return diff

def get_pr_files():
    """Get list of changed files in PR."""
    print(f"📄 Getting changed files...")
    files_json = run_command(f"gh pr view {PR_NUMBER} --json files")
    files_data = json.loads(files_json)
    return [f['path'] for f in files_data.get('files', [])]

def detect_platforms(files):
    """Detect which platforms are affected by file extensions."""
    platforms = set()

    for file in files:
        ext = Path(file).suffix.lower()

        if ext in ['.swift', '.m', '.mm']:
            platforms.add('iOS')
        elif ext in ['.kt', '.java']:
            platforms.add('Android')
        elif ext in ['.tsx', '.jsx', '.ts', '.js', '.html', '.css']:
            platforms.add('Web')
        elif ext == '.dart':
            platforms.add('Flutter')

    return list(platforms)

def load_guides(platforms):
    """Load relevant accessibility guides from framework."""
    guides = {}
    framework_path = Path(FRAMEWORK_PATH)

    # Always load core guides
    core_guides = [
        'guides/GUIDE_WCAG_REFERENCE.md',
        'guides/wcag/QUICK_LOOKUP.md',
        'guides/wcag/SEVERITY_GUIDELINES.md',
        'guides/COMMON_ISSUES.md'
    ]

    print(f"📚 Loading accessibility guides...")

    for guide_path in core_guides:
        full_path = framework_path / guide_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                guides[guide_path] = f.read()

    # Load platform-specific guides
    platform_guide_map = {
        'iOS': 'guides/GUIDE_IOS.md',
        'Android': 'guides/GUIDE_ANDROID.md',
        'Web': 'guides/GUIDE_WEB.md',
        'Flutter': 'guides/GUIDE_FLUTTER.md'
    }

    for platform in platforms:
        if platform in platform_guide_map:
            guide_path = platform_guide_map[platform]
            full_path = framework_path / guide_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    guides[guide_path] = f.read()

    return guides

def create_review_prompt(pr_diff, files, platforms, guides):
    """Create the prompt for AI to review the PR."""

    guides_text = "\n\n".join([
        f"## {path}\n\n{content}"
        for path, content in guides.items()
    ])

    files_list = "\n".join([f"- {f}" for f in files])
    platforms_list = ", ".join(platforms) if platforms else "Unknown"

    prompt = f"""You are performing an automated accessibility review on a GitHub Pull Request.

# PR Information

**Platforms detected:** {platforms_list}
**Files changed:** {len(files)}
{files_list}

# Your Task

Review ONLY the changed code in this PR for accessibility issues. Focus on:

1. **New UI components** - Check for proper accessibility labels, hints, roles
2. **Modified accessibility properties** - Verify changes don't break accessibility
3. **Interactive elements** - Buttons, links, inputs need proper accessibility
4. **Images and icons** - Check for alt text and content descriptions
5. **Text and labels** - Verify semantic structure and clarity
6. **Form inputs** - Check for labels, hints, and error messages
7. **Touch targets** - Verify minimum size requirements
8. **Contrast** - Check color contrast for text and UI elements

# Guidelines to Follow

{guides_text}

# PR Diff

```diff
{pr_diff}
```

# Output Format

Provide your review as a JSON array of issues. Each issue should have:

```json
{{
  "file": "path/to/file.ext",
  "line": 123,
  "severity": "Critical|High|Medium|Low",
  "wcag_sc": "X.X.X - Name",
  "wcag_level": "A|AA|AAA",
  "title": "Brief title",
  "description": "Detailed description",
  "impact": "Who is affected and how",
  "current_code": "code snippet",
  "suggested_fix": "corrected code snippet",
  "resources": ["URL1", "URL2"]
}}
```

**IMPORTANT:**
- Only report issues found in the CHANGED code
- Do NOT report issues in unchanged code
- Focus on accessibility only
- Be specific with file paths and line numbers
- Provide actionable fixes
- If no issues found, return empty array: []

Review the PR now and provide your findings as JSON.
"""

    return prompt

def review_pr_with_anthropic(prompt):
    """Send review request to Anthropic Claude API."""
    try:
        import anthropic
    except ImportError:
        print("❌ Error: anthropic library not installed. Run: pip install anthropic")
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print(f"🤖 Analyzing with Anthropic Claude...")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    config = AI_MODELS['anthropic']

    try:
        message = client.messages.create(
            model=config['model'],
            max_tokens=config['max_tokens'],
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text
        return parse_json_response(response_text)

    except Exception as e:
        print(f"❌ Error calling Anthropic API: {e}")
        sys.exit(1)

def review_pr_with_github_models(prompt):
    """Send review request to GitHub Models API."""
    try:
        import openai
    except ImportError:
        print("❌ Error: openai library not installed. Run: pip install openai")
        sys.exit(1)

    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN not set")
        sys.exit(1)

    print(f"🤖 Analyzing with GitHub Models...")

    config = AI_MODELS['github']

    client = openai.OpenAI(
        base_url=config['base_url'],
        api_key=GITHUB_TOKEN
    )

    try:
        response = client.chat.completions.create(
            model=config['model'],
            max_tokens=config['max_tokens'],
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.choices[0].message.content
        return parse_json_response(response_text)

    except Exception as e:
        print(f"❌ Error calling GitHub Models API: {e}")
        print(f"💡 Tip: Ensure GITHUB_TOKEN has access to GitHub Models")
        print(f"💡 Available models: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, etc.")
        sys.exit(1)

def review_pr_with_openai(prompt):
    """Send review request to OpenAI API."""
    try:
        import openai
    except ImportError:
        print("❌ Error: openai library not installed. Run: pip install openai")
        sys.exit(1)

    api_key = OPENAI_API_KEY or GITHUB_TOKEN
    if not api_key:
        print("❌ Error: OPENAI_API_KEY or GITHUB_TOKEN not set")
        sys.exit(1)

    print(f"🤖 Analyzing with OpenAI...")

    config = AI_MODELS['openai']

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=config['model'],
            max_tokens=config['max_tokens'],
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.choices[0].message.content
        return parse_json_response(response_text)

    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        sys.exit(1)

def parse_json_response(response_text):
    """Parse JSON from AI response (might be wrapped in markdown)."""
    # Extract JSON from response (might be wrapped in markdown code block)
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()

    try:
        issues = json.loads(response_text)
        return issues
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        print(f"Response was: {response_text[:500]}...")
        return []

def review_pr_with_ai(prompt):
    """Route to appropriate AI provider based on configuration."""
    if AI_PROVIDER == 'anthropic':
        return review_pr_with_anthropic(prompt)
    elif AI_PROVIDER == 'github':
        return review_pr_with_github_models(prompt)
    elif AI_PROVIDER == 'openai':
        return review_pr_with_openai(prompt)
    else:
        print(f"❌ Error: Unknown AI_PROVIDER '{AI_PROVIDER}'")
        print(f"💡 Valid options: 'anthropic', 'github', 'openai'")
        sys.exit(1)

def post_pr_comments(issues):
    """Post issues as comments on the PR using GitHub CLI."""
    if not issues:
        print("✅ No accessibility issues found!")
        post_summary_comment(issues)
        return EXIT_SUCCESS

    print(f"💬 Posting {len(issues)} issue(s) to PR...")

    # Group issues by severity
    critical = [i for i in issues if i['severity'] == 'Critical']
    high = [i for i in issues if i['severity'] == 'High']
    medium = [i for i in issues if i['severity'] == 'Medium']
    low = [i for i in issues if i['severity'] == 'Low']

    # Post individual comments for each issue
    for issue in issues:
        comment = format_issue_comment(issue)

        try:
            escaped_comment = comment.replace('"', '\\"').replace('\n', '\\n')
            run_command(f'gh pr comment {PR_NUMBER} --body "{escaped_comment}"')
        except Exception as e:
            print(f"⚠️  Failed to post comment: {e}")

    # Post summary comment
    post_summary_comment(issues)

    # Return appropriate exit code
    if critical:
        return EXIT_CRITICAL_ISSUES
    elif high:
        return EXIT_HIGH_PRIORITY
    else:
        return EXIT_SUCCESS

def format_issue_comment(issue):
    """Format an issue as a GitHub comment."""
    severity_emoji = {
        'Critical': '🔴',
        'High': '🟠',
        'Medium': '🟡',
        'Low': '🔵'
    }

    emoji = severity_emoji.get(issue['severity'], '⚪')

    resources = ""
    if issue.get('resources'):
        resources = "\n\n**Resources:**\n" + "\n".join([f"- {url}" for url in issue['resources']])

    provider_info = {
        'anthropic': 'Anthropic Claude',
        'github': 'GitHub Models',
        'openai': 'OpenAI'
    }
    provider_name = provider_info.get(AI_PROVIDER, AI_PROVIDER)

    comment = f"""## {emoji} Accessibility Issue: {issue['title']}

**WCAG SC:** {issue['wcag_sc']} (Level {issue['wcag_level']})
**Severity:** {issue['severity']}
**Location:** `{issue['file']}:{issue['line']}`

**Issue:**
{issue['description']}

**Impact:**
{issue['impact']}

**Current code:**
```
{issue['current_code']}
```

**Suggested fix:**
```
{issue['suggested_fix']}
```{resources}

---
🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer) using {provider_name}
"""

    return comment

def post_summary_comment(issues):
    """Post a summary comment on the PR."""
    provider_info = {
        'anthropic': 'Anthropic Claude',
        'github': 'GitHub Models',
        'openai': 'OpenAI'
    }
    provider_name = provider_info.get(AI_PROVIDER, AI_PROVIDER)

    if not issues:
        summary = f"""## ✅ Accessibility Review Complete

**No accessibility issues found!**

All changes in this PR follow accessibility best practices.

**Files reviewed:** {len(get_pr_files())}

---
🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)
📅 Reviewed: {run_command('date -u +"%Y-%m-%d %H:%M UTC"')}
🔧 Powered by: {provider_name}
"""
    else:
        # Group by severity
        critical = [i for i in issues if i['severity'] == 'Critical']
        high = [i for i in issues if i['severity'] == 'High']
        medium = [i for i in issues if i['severity'] == 'Medium']
        low = [i for i in issues if i['severity'] == 'Low']

        # Get unique WCAG SCs
        wcag_scs = list(set([i['wcag_sc'] for i in issues]))

        summary = f"""## 🔍 Accessibility Review Summary

**Total Issues Found:** {len(issues)}
- 🔴 Critical: {len(critical)}
- 🟠 High: {len(high)}
- 🟡 Medium: {len(medium)}
- 🔵 Low: {len(low)}

**WCAG Success Criteria Affected:**
{chr(10).join([f'- {sc}' for sc in wcag_scs[:10]])}

**Files Reviewed:** {len(get_pr_files())}

### 📋 Recommended Actions

"""

        if critical:
            summary += "1. **🔴 Critical issues must be fixed before merge**\n"
        if high:
            summary += "2. **🟠 High priority issues should be addressed**\n"
        if medium or low:
            summary += "3. **Medium/Low issues can be addressed in follow-up**\n"

        summary += f"""
---
🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)
📅 Reviewed: {run_command('date -u +"%Y-%m-%d %H:%M UTC"')}
🔧 Powered by: {provider_name}
"""

    # Post the summary
    escaped_summary = summary.replace('"', '\\"').replace('\n', '\\n').replace('$', '\\$')
    run_command(f'gh pr comment {PR_NUMBER} --body "{escaped_summary}"')

def main():
    """Main execution flow."""
    print("=" * 60)
    print("🔍 Multi-Provider PR Accessibility Review")
    print("=" * 60)

    # Validate environment
    if not PR_NUMBER:
        print("❌ Error: PR_NUMBER not set")
        sys.exit(1)

    # Display provider info
    provider_display = {
        'anthropic': f"Anthropic Claude ({AI_MODELS['anthropic']['model']})",
        'github': f"GitHub Models ({AI_MODELS['github']['model']})",
        'openai': f"OpenAI ({AI_MODELS['openai']['model']})"
    }

    print(f"\n🤖 AI Provider: {provider_display.get(AI_PROVIDER, AI_PROVIDER)}")
    print(f"📊 PR: #{PR_NUMBER}")
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"📁 Framework: {FRAMEWORK_PATH}\n")

    # Validate API keys based on provider
    if AI_PROVIDER == 'anthropic' and not ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    elif AI_PROVIDER == 'github' and not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN not set")
        sys.exit(1)
    elif AI_PROVIDER == 'openai' and not (OPENAI_API_KEY or GITHUB_TOKEN):
        print("❌ Error: OPENAI_API_KEY or GITHUB_TOKEN not set")
        sys.exit(1)

    # Get PR information
    pr_diff = get_pr_diff()
    files = get_pr_files()
    platforms = detect_platforms(files)

    print(f"🎯 Platforms: {', '.join(platforms) if platforms else 'None detected'}")
    print(f"📄 Files changed: {len(files)}\n")

    # Load accessibility guides
    guides = load_guides(platforms)
    print(f"✓ Loaded {len(guides)} guide(s)\n")

    # Create review prompt
    prompt = create_review_prompt(pr_diff, files, platforms, guides)

    # Review with AI
    issues = review_pr_with_ai(prompt)
    print(f"\n✓ Review complete: {len(issues)} issue(s) found\n")

    # Post comments
    exit_code = post_pr_comments(issues)

    print("\n" + "=" * 60)
    if exit_code == EXIT_CRITICAL_ISSUES:
        print("❌ CRITICAL issues found - blocking merge")
    elif exit_code == EXIT_HIGH_PRIORITY:
        print("⚠️  HIGH priority issues found")
    else:
        print("✅ Review complete")
    print("=" * 60)

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
