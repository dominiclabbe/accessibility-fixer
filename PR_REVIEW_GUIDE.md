# PR Accessibility Review Guide

## Overview

The `/pr-review` command provides **automated accessibility review** for GitHub Pull Requests. It analyzes only the changed code in a PR and provides immediate feedback through PR comments, making it ideal for CI/CD pipelines.

## Key Features

- 🔍 **Focused Review**: Only analyzes changed files (not entire codebase)
- 💬 **Inline Comments**: Posts issues directly on PR lines
- 🤖 **CI/CD Ready**: Designed for automated workflows
- ⚡ **Fast**: 30-60 minutes vs 6-10 hours for full audit
- 📊 **Summary Reports**: Provides overview of all issues found
- 🎯 **Severity-Based**: Critical issues can block PR merges
- 🌐 **Multi-Platform**: Supports iOS, Android, Web, React Native, Flutter, TV platforms

## Differences from `/audit`

| Feature | `/audit` | `/pr-review` |
|---------|----------|--------------|
| **Scope** | Entire codebase section | Only changed files in PR |
| **Time** | 6-10 hours | 30-60 minutes |
| **Output** | Markdown report file | PR comments + optional report |
| **Automation** | Manual/interactive | CI/CD automated |
| **Usage** | Comprehensive audits | Quick PR validation |
| **When to use** | New features, major changes | Every PR before merge |

## Prerequisites

### Required Software

1. **GitHub CLI (`gh`)**
   ```bash
   # macOS
   brew install gh

   # Linux (Debian/Ubuntu)
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh

   # Windows
   winget install --id GitHub.cli
   ```

2. **GitHub CLI Authentication**
   ```bash
   gh auth login
   ```

3. **Claude Code CLI**
   - Follow installation instructions for Claude Code

### Repository Setup

1. **Run setup script in your project:**
   ```bash
   cd /path/to/your-project
   bash /path/to/accessibilityFixer/setup-audit.sh
   ```

2. **Verify installation:**
   ```bash
   # Check if commands are installed
   ls .claude/commands/
   # Should show: audit.md, fix-accessibility.md, pr-review.md
   ```

3. **Update Claude Code permissions:**

   Add to `.claude/settings.local.json`:
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

## Usage

### Interactive Mode (Manual Review)

#### Option 1: Auto-detect current branch PR
```bash
cd /path/to/your-project
claude-code
```
Then in Claude Code:
```
/pr-review
```

Claude Code will:
1. Detect your current branch
2. Find the associated PR
3. Analyze changed files
4. Ask for confirmation before posting comments

#### Option 2: Specify PR number
```
/pr-review 123
```

This reviews PR #123 directly.

#### Option 3: Dry-run (review without posting)
```
/pr-review --no-post
```

This analyzes the PR but doesn't post comments to GitHub. Useful for:
- Testing the review process
- Seeing what issues would be found
- Generating a local report only

### CI/CD Mode (Automated)

The command detects CI environment automatically and runs without interaction.

#### GitHub Actions

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
  accessibility-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install dependencies
        run: |
          # Install gh, Claude Code, and setup audit framework
          gh --version || sudo apt-get install gh
          npm install -g @anthropic/claude-code
          git clone https://github.com/YOUR_ORG/accessibilityFixer.git /tmp/accessibilityFixer
          bash /tmp/accessibilityFixer/setup-audit.sh

      - name: Run PR Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          echo "$GITHUB_TOKEN" | gh auth login --with-token
          claude-code "/pr-review ${{ github.event.pull_request.number }}"
```

See `ci-examples/github-actions.yml` for complete example.

#### Exit Codes

The command uses exit codes to control CI behavior:

- `0`: ✅ No critical issues found (pass)
- `1`: ❌ Critical issues found (fail/block merge)
- `2`: ⚠️ High priority issues found (warning, don't fail)

You can configure branch protection rules to require this check to pass.

## How It Works

### 1. PR Detection

The command detects the PR in multiple ways:
1. **CI Environment**: Reads `GITHUB_EVENT_PATH` or similar env vars
2. **Command Argument**: `/pr-review 123`
3. **Current Branch**: Uses `gh pr view --json` to find PR
4. **Interactive**: Asks user for PR number

### 2. Changed Files Analysis

```bash
# Gets list of changed files
gh pr diff PR_NUMBER --name-only

# Gets full diff with context
gh pr diff PR_NUMBER
```

### 3. Platform Detection

Automatically detects platform from file extensions:
- `.swift`, `.m`: iOS
- `.kt`, `.java`: Android
- `.jsx`, `.tsx`: Web/React
- `.dart`: Flutter
- And more...

Loads appropriate accessibility guidelines.

### 4. Accessibility Analysis

For each changed file, checks:
- ✅ New UI components
- ✅ Modified accessibility properties
- ✅ Layout/structure changes
- ✅ Text/label modifications
- ✅ Interactive elements
- ❌ Unchanged code (skipped)

Identifies issues:
- Missing accessibility labels
- Poor contrast ratios
- Touch target sizes
- Keyboard navigation
- Focus management
- Form input labels
- Image alt text
- And more...

### 5. PR Comments

Posts two types of comments:

#### A. Inline Comments (on specific lines)
```markdown
### ⚠️ Accessibility Issue: Button missing label

**WCAG SC:** 4.1.2 - Name, Role, Value (Level A)
**Severity:** Critical

**Issue:**
This button has no accessible label, making it unusable for screen reader users.

**Current code:**
```swift
Button(action: { ... }) {
    Image(systemName: "star")
}
```

**Suggested fix:**
```swift
Button(action: { ... }) {
    Image(systemName: "star")
}
.accessibilityLabel("Add to favorites")
```
```

#### B. Summary Comment (on PR)
Shows overview of all issues with quick stats.

## What Gets Reviewed

### ✅ Reviewed (Changed Code)

- New UI components added in PR
- Modified accessibility properties
- Layout changes affecting navigation
- New or updated labels/text
- Interactive elements (buttons, links, inputs)
- Images and visual content
- Form fields and validation
- Custom components
- Navigation changes

### ❌ Not Reviewed (Unchanged Code)

- Existing code not touched by PR
- Business logic without UI impact
- Backend/API code
- Configuration files (unless accessibility-related)
- Tests (unless testing accessibility)
- Documentation

## Common Issues Detected

### Critical
- Icon-only buttons without labels
- Form inputs without labels
- Keyboard traps
- Missing alt text on informative images

### High Priority
- Poor color contrast
- Touch targets too small
- Missing focus indicators
- Incorrect heading structure

### Medium Priority
- Non-ideal label wording
- Missing hints on complex inputs
- Redundant announcements

### Low Priority
- Label clarity improvements
- Additional context suggestions

## Best Practices

### For Developers

1. **Run before pushing:**
   ```bash
   /pr-review --no-post
   ```
   Fix issues locally before creating PR.

2. **Address critical issues immediately:**
   Critical issues should block merge.

3. **Plan for high priority:**
   Fix before merge or create follow-up tasks.

4. **Consider medium/low:**
   Nice to have, but don't block progress.

### For Reviewers

1. **Check automated comments:**
   Review accessibility issues alongside code review.

2. **Verify fixes:**
   Ask developer to confirm fixes with assistive technology testing.

3. **Use full audit for major changes:**
   If PR has significant UI changes, run `/audit` for comprehensive review.

### For Teams

1. **Add to CI pipeline:**
   Automate reviews on every PR.

2. **Set branch protection:**
   Require accessibility checks to pass.

3. **Create fix workflow:**
   Use `/fix-accessibility` to apply automated fixes.

4. **Track trends:**
   Monitor common issues across PRs.

## Troubleshooting

### "GitHub CLI (gh) not found"

```bash
# Install GitHub CLI
brew install gh  # macOS
# OR see installation instructions above

# Authenticate
gh auth login
```

### "Could not find PR"

```bash
# Verify PR exists
gh pr list

# Specify PR number explicitly
/pr-review 123
```

### "Permission denied" when posting comments

```bash
# Re-authenticate with write permissions
gh auth refresh -h github.com -s write:discussion
```

### "No accessibility issues found"

This is good! But verify:
- PR actually has UI changes
- Changed files are in supported platforms
- Changes involve user-facing components

### CI failing with exit code 1

Critical accessibility issues were found. Options:
1. Fix the issues (recommended)
2. Review if severity is correct
3. Add exception for specific case (document why)

## Examples

### Example 1: Simple Button Fix

**Changed code in PR:**
```swift
Button(action: { viewModel.favorite() }) {
    Image(systemName: "star")
}
```

**PR Review Comment:**
```markdown
⚠️ **Critical**: Button missing accessibility label

This icon-only button needs a label for screen readers.

**Fix:**
```swift
Button(action: { viewModel.favorite() }) {
    Image(systemName: "star")
}
.accessibilityLabel("Add to favorites")
```
```

### Example 2: Multiple Issues

**Summary Comment:**
```markdown
## 🔍 Accessibility Review Summary

**Total Issues Found:** 5
- 🔴 Critical: 2
- 🟠 High: 2
- 🟡 Medium: 1

**WCAG Success Criteria Affected:**
- 1.4.3 Contrast (Minimum)
- 4.1.2 Name, Role, Value
- 2.5.5 Target Size

**Recommended Actions:**
1. Fix 2 critical issues before merge
2. Address 2 high priority issues
3. Medium priority can be follow-up
```

## Advanced Usage

### Custom Severity Thresholds

Modify exit codes in CI:
```bash
# Only fail on critical
if [ $EXIT_CODE -eq 1 ]; then
  exit 1
else
  exit 0
fi
```

### Generate Report Only

```bash
/pr-review --no-post --report
```

Generates report file without posting to GitHub.

### Review Specific Files

```bash
# In command, can specify focus
/pr-review 123 --focus "src/components/*.tsx"
```

### Integration with Other Tools

Combine with other accessibility tools:
```yaml
- name: Automated tests
  run: npm test

- name: Accessibility PR review
  run: claude-code "/pr-review"

- name: Lint accessibility
  run: npm run lint:a11y
```

## Resources

- **WCAG 2.2 Guidelines**: https://www.w3.org/WAI/WCAG22/quickref/
- **Platform Guides**: See `guides/GUIDE_[PLATFORM].md`
- **Common Issues**: See `guides/COMMON_ISSUES.md`
- **Full Audit**: Use `/audit` for comprehensive review

## Support

For issues or questions:
1. Check this guide
2. Review command documentation: `.claude/commands/pr-review.md`
3. Check CI examples: `ci-examples/`
4. Run full audit: `/audit`

## FAQ

### Q: How long does a PR review take?
A: Typically 30-60 minutes for standard PRs with 5-20 changed files.

### Q: Can I review PRs from forks?
A: Yes, but you need read access to the fork repository.

### Q: Will it review non-UI changes?
A: It focuses on UI changes. Non-UI code is skipped automatically.

### Q: Can I customize what gets checked?
A: Yes, modify `.claude/commands/pr-review.md` to adjust focus areas.

### Q: Does it work offline?
A: No, requires GitHub API access and Claude AI API.

### Q: Can it auto-fix issues?
A: Not automatically. Use `/fix-accessibility` after review to apply fixes.

### Q: How accurate is it?
A: High accuracy for code-level issues. Manual testing still recommended for UX.

### Q: What about false positives?
A: Rate is low. If found, you can comment on the PR to discuss.
