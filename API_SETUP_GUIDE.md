# API-Based PR Review Setup Guide

## ✅ Working Solution Without CLI

The `/pr-review` command can now run automatically in CI/CD using the **Anthropic API directly** - no Claude Code CLI needed!

## How It Works

Instead of waiting for Claude Code CLI, we created a Python script that:
1. ✅ Uses Anthropic API directly
2. ✅ Fetches PR diffs using GitHub CLI
3. ✅ Loads accessibility guides from the framework
4. ✅ Sends structured prompts to Claude
5. ✅ Posts comments on GitHub PRs
6. ✅ Returns exit codes to gate merges

## Quick Setup (5 steps)

### 1. Get Anthropic API Key

Sign up at https://console.anthropic.com/ and create an API key.

### 2. Add API Key to GitHub Secrets

```bash
cd your-project
gh secret set ANTHROPIC_API_KEY
# Paste your API key when prompted
```

Or via GitHub UI:
- Go to: Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `ANTHROPIC_API_KEY`
- Value: Your API key

### 3. Copy Workflow File

Copy the working workflow to your project:

```bash
curl -o .github/workflows/accessibility-pr-review.yml \
  https://raw.githubusercontent.com/dominiclabbe/accessibility-fixer/main/ci-examples/github-actions-with-api.yml
```

Or manually create `.github/workflows/accessibility-pr-review.yml`:

```yaml
name: Accessibility PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  pull-requests: write
  contents: read

jobs:
  accessibility-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup framework
        run: |
          git clone https://github.com/dominiclabbe/accessibility-fixer.git /tmp/accessibility-fixer
          pip install -r /tmp/accessibility-fixer/scripts/requirements.txt
          echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-token

      - name: Run review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          FRAMEWORK_PATH: /tmp/accessibility-fixer
        run: python /tmp/accessibility-fixer/scripts/pr-review-ci.py
```

### 4. Commit and Push

```bash
git add .github/workflows/accessibility-pr-review.yml
git commit -m "Add automated accessibility PR reviews"
git push
```

### 5. Test with a PR

Create a test PR and watch it work!

```bash
git checkout -b test/accessibility
# Make some changes to UI files
git commit -am "Test accessibility review"
git push origin test/accessibility
# Create PR on GitHub
```

## What It Does

### On Every PR

1. **Detects platforms** (iOS, Android, Web, Flutter)
2. **Loads guides** based on detected platforms
3. **Analyzes changed code** using Claude AI
4. **Posts comments** on specific issues
5. **Blocks merge** if critical issues found

### Exit Codes

- `0` ✅ No critical issues (PR can merge)
- `1` ❌ Critical issues (blocks merge)
- `2` ⚠️ High priority issues (warning only)

### Example Output

**PR Comment:**
```markdown
## 🔴 Accessibility Issue: Button missing label

**WCAG SC:** 4.1.2 - Name, Role, Value (Level A)
**Severity:** Critical
**Location:** `app/src/Button.kt:23`

**Issue:**
Icon-only button without accessibility label

**Suggested fix:**
```kotlin
IconButton(onClick = { }) {
    Icon(Icons.Default.Star, contentDescription = "Add to favorites")
}
```

🤖 Automated by accessibility-fixer
```

## Cost Estimate

Using Anthropic API Claude Sonnet:

| PR Size | Est. Cost |
|---------|-----------|
| Small (< 500 lines) | $0.10-0.20 |
| Medium (500-2000 lines) | $0.20-0.50 |
| Large (> 2000 lines) | $0.50-1.00 |

**Monthly estimate:** $10-50 for typical development team

## Features

### ✅ Works Now
- Uses Anthropic API (no CLI needed)
- Automatic platform detection
- Posts PR comments
- Blocks merge on critical issues
- WCAG 2.2 Level AA compliance
- Multi-platform support

### 🎯 Platforms Supported
- iOS (Swift)
- Android (Kotlin/Java)
- Web (React, Vue, vanilla JS)
- Flutter (Dart)
- React Native

### 📋 What It Checks
- Missing accessibility labels
- Touch target sizes
- Color contrast
- Keyboard navigation
- Form input labels
- Image alt text
- Semantic structure
- Focus management

## Advanced Configuration

### Branch Protection

Require review to pass before merge:

1. Go to: Settings → Branches
2. Add rule for `main` branch
3. Enable: "Require status checks to pass"
4. Select: "accessibility-review"

### Custom Thresholds

Edit the script to change behavior:

```python
# Only block on critical, allow high/medium/low
if critical:
    return EXIT_CRITICAL_ISSUES
else:
    return EXIT_SUCCESS
```

### Skip Certain Files

Add to workflow:

```yaml
paths-ignore:
  - 'docs/**'
  - 'tests/**'
  - '**/*.md'
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

```bash
gh secret set ANTHROPIC_API_KEY
# Paste your key
```

### "Permission denied posting comments"

Check workflow permissions:
```yaml
permissions:
  pull-requests: write  # Required!
  contents: read
```

### "API rate limit exceeded"

Anthropic API limits:
- Tier 1: 50 requests/min
- Tier 2: 1000 requests/min

For high-traffic repos, consider caching or batching.

### "Script not found"

Ensure framework clones successfully:
```yaml
- name: Debug
  run: ls -la /tmp/accessibility-fixer/scripts/
```

## Comparison: CLI vs API

| Feature | CLI (Future) | API (Now) |
|---------|-------------|-----------|
| **Availability** | Not yet released | ✅ Works now |
| **Setup** | Simple | Requires API key |
| **Cost** | Unknown | ~$10-50/month |
| **Speed** | TBD | 30-60 seconds |
| **Reliability** | TBD | ✅ Production ready |
| **Offline** | Maybe | No (API required) |

## Migration Path

When Claude Code CLI is released:

1. **Option A:** Keep using API (if it works well)
2. **Option B:** Switch to CLI (update workflow)
3. **Option C:** Hybrid (API in CI, CLI locally)

The API-based solution is production-ready now!

## Examples

### Successful Review

```
✅ Accessibility Review Complete
No accessibility issues found!
Files reviewed: 3
```

### Issues Found

```
🔍 Accessibility Review Summary
Total Issues Found: 5
🔴 Critical: 2
🟠 High: 2
🟡 Medium: 1

Recommended Actions:
1. Fix critical issues before merge
2. Address high priority issues
```

### Critical Issue Blocking

```
❌ CRITICAL issues found - blocking merge
Review required before this PR can be merged
```

## Resources

- **Script Source:** `/scripts/pr-review-ci.py`
- **Workflow Template:** `/ci-examples/github-actions-with-api.yml`
- **Script Docs:** `/scripts/README.md`
- **Framework Repo:** https://github.com/dominiclabbe/accessibility-fixer

## Support

Issues? Questions?
- Check script logs in GitHub Actions
- Review `/scripts/README.md` for debugging
- Open issue on GitHub repo

---

**This solution works TODAY!** No need to wait for CLI. 🚀
