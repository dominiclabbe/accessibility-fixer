# PR Review - Quick Start

Get automated accessibility reviews on your Pull Requests in 5 minutes.

## 1. Install Prerequisites (One-time)

### Install GitHub CLI
```bash
# macOS
brew install gh

# Linux
sudo apt install gh

# Windows
winget install --id GitHub.cli
```

### Authenticate
```bash
gh auth login
```

## 2. Setup Your Project (One-time)

```bash
cd /path/to/your-project
bash /path/to/accessibilityFixer/setup-audit.sh
```

This creates:
- `.claude/commands/pr-review.md`
- `accessibility-audit/reports/pr/` directory

## 3. Update Permissions (One-time)

Create or update `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(gh:*)",
      "Bash(git:*)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:api.github.com)"
    ]
  }
}
```

## 4. Review a PR

### Manual Review
```bash
# Open Claude Code in your project
claude-code

# Auto-detect PR from current branch
/pr-review

# OR specify PR number
/pr-review 123

# OR dry-run (no comments posted)
/pr-review --no-post
```

### Automated Review (CI/CD)

Create `.github/workflows/accessibility-pr-review.yml`:

```yaml
name: Accessibility PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  pull-requests: write
  contents: read

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup
        run: |
          sudo apt-get install gh
          npm install -g @anthropic/claude-code
          git clone https://github.com/YOUR_ORG/accessibilityFixer.git /tmp/a11y
          bash /tmp/a11y/setup-audit.sh

      - name: Review PR
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          echo "$GITHUB_TOKEN" | gh auth login --with-token
          claude-code "/pr-review ${{ github.event.pull_request.number }}"
```

Add `ANTHROPIC_API_KEY` to repository secrets.

## 5. Review Results

The command will:
1. ✅ Analyze all changed files
2. 💬 Post inline comments on issues
3. 📊 Post summary comment on PR
4. 📄 Save report to `accessibility-audit/reports/pr/`

### Exit Codes (CI)
- `0` = ✅ No critical issues
- `1` = ❌ Critical issues (blocks merge)
- `2` = ⚠️ High priority issues (warning)

## 6. Fix Issues

Two options:

### Option A: Manual fixes
Review PR comments and apply suggested code changes.

### Option B: Automated fixes
```bash
/fix-accessibility
```
Select the PR review report to auto-apply fixes.

## Examples

### Example PR Comment

```markdown
### ⚠️ Accessibility Issue: Button missing label

**WCAG SC:** 4.1.2 - Name, Role, Value (Level A)
**Severity:** Critical

**Issue:** Icon-only button without accessibility label

**Current code:**
```swift
Button(action: { share() }) {
    Image(systemName: "square.and.arrow.up")
}
```

**Fix:**
```swift
Button(action: { share() }) {
    Image(systemName: "square.and.arrow.up")
}
.accessibilityLabel("Share")
```

**Resources:**
- [WCAG 4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value)
```

## What Gets Checked

✅ **Reviewed:**
- New UI components
- Modified accessibility properties
- Interactive elements (buttons, links, inputs)
- Text labels and hints
- Images and alt text
- Layout/navigation changes

❌ **Skipped:**
- Unchanged code
- Non-UI code (business logic, APIs)
- Configuration files

## Common Issues Detected

🔴 **Critical** (blocks merge):
- Icon-only buttons without labels
- Form inputs without labels
- Keyboard traps

🟠 **High Priority** (fix before merge):
- Poor color contrast
- Touch targets too small
- Missing focus indicators

🟡 **Medium/Low** (nice to have):
- Label clarity improvements
- Additional hints

## Troubleshooting

### "GitHub CLI not found"
```bash
gh --version || brew install gh
gh auth login
```

### "Could not find PR"
```bash
gh pr list  # verify PR exists
/pr-review 123  # specify PR number
```

### "Permission denied"
```bash
gh auth refresh -h github.com -s write:discussion
```

## Next Steps

- **Full Documentation**: See `PR_REVIEW_GUIDE.md`
- **CI Examples**: See `ci-examples/` directory
- **Full Audit**: Use `/audit` for comprehensive review
- **Apply Fixes**: Use `/fix-accessibility` to auto-fix issues

## Commands Summary

| Command | Purpose | Time |
|---------|---------|------|
| `/pr-review` | Review changed files in PR | 30-60 min |
| `/audit` | Comprehensive codebase audit | 6-10 hours |
| `/fix-accessibility` | Apply automated fixes | 15-30 min |

---

**Ready to use!** 🚀

For detailed information, see [PR_REVIEW_GUIDE.md](PR_REVIEW_GUIDE.md)
