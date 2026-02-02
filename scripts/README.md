# PR Review CI Script

This script enables automated PR accessibility reviews without requiring Claude Code CLI. It uses the Anthropic API directly.

## Overview

The `pr-review-ci.py` script:
- ✅ Works in any CI/CD environment
- ✅ Uses Anthropic API directly (no CLI needed)
- ✅ Analyzes PR diffs for accessibility issues
- ✅ Posts comments on GitHub PRs
- ✅ Returns exit codes to gate merges
- ✅ Loads accessibility guides automatically

## Requirements

- Python 3.8+
- Anthropic API key
- GitHub CLI (`gh`)
- GitHub token with PR write permissions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### In GitHub Actions

```yaml
- name: Install dependencies
  run: |
    pip install -r /tmp/accessibility-fixer/scripts/requirements.txt

- name: Run PR Review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    FRAMEWORK_PATH: /tmp/accessibility-fixer
  run: |
    python /tmp/accessibility-fixer/scripts/pr-review-ci.py
```

### Locally

```bash
export ANTHROPIC_API_KEY="your-api-key"
export GITHUB_TOKEN="your-github-token"
export PR_NUMBER=123
export GITHUB_REPOSITORY="owner/repo"
export FRAMEWORK_PATH="/path/to/accessibility-fixer"

python pr-review-ci.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `GITHUB_TOKEN` | Yes | GitHub token for API access |
| `PR_NUMBER` | Yes | Pull request number to review |
| `GITHUB_REPOSITORY` | Yes | Repository in format `owner/repo` |
| `FRAMEWORK_PATH` | No | Path to accessibility-fixer (default: `/tmp/accessibility-fixer`) |

## Exit Codes

- `0` - Success, no critical issues
- `1` - Critical issues found (blocks merge)
- `2` - High priority issues found (warning)

## How It Works

1. **Fetches PR diff** using GitHub CLI
2. **Detects platforms** from file extensions
3. **Loads accessibility guides** based on platforms
4. **Sends to Claude API** with structured prompt
5. **Parses JSON response** with accessibility issues
6. **Posts GitHub comments** for each issue
7. **Posts summary comment** with overview
8. **Returns exit code** based on severity

## Features

### Platform Detection

Automatically detects platforms from file extensions:
- iOS: `.swift`, `.m`, `.mm`
- Android: `.kt`, `.java`
- Web: `.tsx`, `.jsx`, `.ts`, `.js`, `.html`
- Flutter: `.dart`

### Severity Levels

- 🔴 **Critical** - Blocks merge
- 🟠 **High** - Should be fixed before merge
- 🟡 **Medium** - Can be addressed in follow-up
- 🔵 **Low** - Nice to have improvements

### WCAG Compliance

Reviews against WCAG 2.2 Level AA standards using:
- Core WCAG guidelines
- Platform-specific guides
- Common accessibility patterns
- Severity guidelines

## Output

### PR Comments

The script posts:
1. **Individual comments** for each issue with:
   - Severity and WCAG SC
   - File location and line number
   - Description and impact
   - Current code vs suggested fix
   - Resources and documentation links

2. **Summary comment** with:
   - Total issue count by severity
   - WCAG criteria affected
   - Recommended actions
   - Review timestamp

### Example Comment

```markdown
## 🔴 Accessibility Issue: Button missing label

**WCAG SC:** 4.1.2 - Name, Role, Value (Level A)
**Severity:** Critical
**Location:** `app/src/Button.kt:23`

**Issue:**
Icon-only button without accessibility label

**Impact:**
Screen reader users cannot understand button purpose

**Current code:**
```kotlin
IconButton(onClick = { }) {
    Icon(Icons.Default.Star, contentDescription = null)
}
```

**Suggested fix:**
```kotlin
IconButton(onClick = { }) {
    Icon(Icons.Default.Star, contentDescription = "Add to favorites")
}
```

**Resources:**
- https://www.w3.org/WAI/WCAG22/Understanding/name-role-value

---
🤖 Automated review by accessibility-fixer
```

## Limitations

- Requires Anthropic API access (costs apply)
- Limited to code-level analysis (doesn't test running app)
- May miss runtime-only accessibility issues
- Depends on accuracy of Claude's analysis

## Cost Considerations

Each PR review costs approximately:
- Small PR (< 500 lines): ~$0.10-0.20
- Medium PR (500-2000 lines): ~$0.20-0.50
- Large PR (> 2000 lines): ~$0.50-1.00

Costs depend on:
- Size of PR diff
- Number of guides loaded
- Response length

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

Add the API key to your repository secrets:
```bash
gh secret set ANTHROPIC_API_KEY
```

### "gh: command not found"

Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux
sudo apt install gh
```

### "Permission denied posting comments"

Ensure `GITHUB_TOKEN` has PR write permissions:
```yaml
permissions:
  pull-requests: write
  contents: read
```

### JSON parsing errors

If Claude returns non-JSON:
- Check API key is valid
- Verify model name is correct
- Check for API rate limits

## Development

### Testing Locally

```bash
# Set environment
export ANTHROPIC_API_KEY="..."
export GITHUB_TOKEN="..."
export PR_NUMBER=123

# Run script
python pr-review-ci.py
```

### Debugging

Add `--verbose` flag (if implemented) or check:
- PR diff fetching
- Guide loading
- API request/response
- Comment posting

## Contributing

Improvements welcome! Consider:
- Better error handling
- Retry logic for API calls
- Rate limiting
- Caching of guides
- More detailed line-specific comments
- Support for inline PR review comments

## License

MIT License - See main repository LICENSE file
