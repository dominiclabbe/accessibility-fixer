# PR Accessibility Review

You are performing an AUTOMATED accessibility review on a Pull Request.

## Purpose

This command reviews ONLY the code changes in a GitHub Pull Request and provides immediate feedback on accessibility issues. It's designed to run in CI/CD pipelines and post comments directly to the PR.

## Guidelines Location
The accessibility guidelines are located in the accessibility-fixer repository

## Key Differences from /audit

- **Scope:** Only changed files in the PR (not entire codebase)
- **Output:** GitHub PR comments + optional summary report
- **Speed:** Fast, focused review (30-60 min vs 6-10 hours)
- **Automation:** Designed to run in CI without human interaction

## Before Starting - Load Reference Guides

1. **Core references:**
   - `guides/GUIDE_WCAG_REFERENCE.md` - Main WCAG reference
   - `guides/wcag/QUICK_LOOKUP.md` - Quick reference tables
   - `guides/wcag/COMPONENT_WCAG_MAPPINGS.md` - Component mappings
   - `guides/wcag/SEVERITY_GUIDELINES.md` - Severity rules
   - `guides/COMMON_ISSUES.md` - Common accessibility issues

2. **Platform-specific guides (load based on detected platform):**
   - `guides/GUIDE_ANDROID.md` - For Android changes
   - `guides/GUIDE_IOS.md` - For iOS changes
   - `guides/GUIDE_WEB.md` - For Web changes
   - `guides/GUIDE_REACT_NATIVE.md` - For React Native changes
   - `guides/GUIDE_FLUTTER.md` - For Flutter changes
   - `guides/GUIDE_ANDROID_TV.md` - For Android TV changes
   - `guides/GUIDE_TVOS.md` - For tvOS changes

3. **Pattern guides (load as needed):**
   - `guides/patterns/COLLECTION_ITEMS_PATTERN.md`
   - `guides/patterns/FONT_SCALING_SUPPORT.md`
   - `guides/patterns/DECORATIVE_IMAGE_DECISION_TREE.md`
   - `guides/patterns/AVOID_ROLE_IN_LABEL.md`
   - `guides/patterns/BUTTONS_ACTING_AS_TABS.md`
   - `guides/patterns/REPEATED_ELEMENTS_CONTEXT.md`
   - `guides/patterns/NAVIGATION_BAR_ACCESSIBILITY.md`

## Workflow Overview

### Step 1: PR Detection and Setup

**Check for GitHub CLI availability:**
```bash
gh --version
```

If `gh` is not available:
```
❌ GitHub CLI (gh) is not installed or not available.

To use /pr-review, you need to install GitHub CLI:
- macOS: brew install gh
- Linux: See https://github.com/cli/cli#installation
- Windows: See https://github.com/cli/cli#installation

Then authenticate: gh auth login

Alternatively, provide PR number manually and I'll help you review the changes.
```

**Detect PR context:**

1. Check if we're in a CI environment (env vars: CI, GITHUB_ACTIONS, GITHUB_EVENT_NAME)
2. Check if PR number was provided in command
3. Try to detect current branch's PR
4. Interactive: Ask user for PR number

**Get PR information:**
```bash
# Get PR details
gh pr view [PR_NUMBER] --json number,title,author,headRefName,baseRefName,state

# Get changed files with their status
gh pr diff [PR_NUMBER] --name-only

# Get full diff for analysis
gh pr diff [PR_NUMBER]
```

### Step 2: Platform Detection

Based on changed files, detect platform(s):

- **iOS:** `.swift`, `.m`, `.mm`, `.xib`, `.storyboard`
- **Android:** `.kt`, `.java`, `.xml` (in res/ or layout/)
- **Web:** `.jsx`, `.tsx`, `.js`, `.ts`, `.vue`, `.html`, `.css`
- **React Native:** `.jsx`, `.tsx` with react-native imports
- **Flutter:** `.dart`
- **Android TV:** Android files in tv/ or leanback/
- **tvOS:** Swift files with tvOS imports

Load the appropriate platform guide(s).

### Step 3: Analyze Changed Code

**Use TodoWrite to track analysis:**

For each changed file:
1. Read the full diff for context
2. Identify accessibility-relevant changes:
   - New UI components (buttons, inputs, images, etc.)
   - Modified accessibility properties
   - Layout changes
   - Text/label changes
   - Interactive elements
3. Check against WCAG guidelines
4. Document issues with:
   - File path and line number
   - WCAG SC violated
   - Severity (Critical/High/Medium/Low)
   - Description of issue
   - Suggested fix
   - Code example

**Focus areas:**
- ✅ **New components:** All newly added UI elements
- ✅ **Modified components:** Changes to existing accessible elements
- ✅ **Text changes:** Labels, hints, descriptions
- ✅ **Interactive elements:** Buttons, links, inputs, gestures
- ✅ **Images:** Alt text, decorative vs informative
- ❌ **Unchanged code:** Don't review code that wasn't modified
- ❌ **Non-UI code:** Skip business logic, utils, models (unless accessibility-related)

**Common issues to check:**
1. **Missing labels:** Interactive elements without accessibility labels
2. **Poor contrast:** Color changes that affect readability
3. **Keyboard navigation:** New interactive elements without keyboard support
4. **Touch targets:** Elements too small (< 44x44pt iOS, < 48x48dp Android)
5. **Focus management:** Navigation changes affecting focus order
6. **Dynamic content:** Updates without accessibility announcements
7. **Form inputs:** Missing labels, hints, or error messages
8. **Images:** Missing alt text or incorrect decorative marking
9. **Headings:** Missing or incorrect semantic structure
10. **Custom controls:** New custom components without full accessibility

### Step 4: Post PR Comments

**For each issue found, post an inline comment:**

```bash
gh pr review [PR_NUMBER] --comment --body "
### ⚠️ Accessibility Issue: [Title]

**WCAG SC:** [SC X.X.X - Name] (Level X)
**Severity:** [Critical/High/Medium/Low]

**Issue:**
[Description of the problem]

**Impact:**
[How this affects users with disabilities]

**Current code:**
\`\`\`[language]
[code snippet]
\`\`\`

**Suggested fix:**
\`\`\`[language]
[corrected code]
\`\`\`

**Resources:**
- [Link to WCAG SC]
- [Link to platform guide if relevant]

---
🤖 Generated by /pr-review command
"
```

**Best practices for PR comments:**
- Use inline comments when possible (specific line references)
- Group related issues together
- Be concise but clear
- Always provide a code example fix
- Link to relevant documentation
- Use severity labels (emoji or text)

### Step 5: Post Summary Comment

After reviewing all files, post a summary comment to the PR:

```bash
gh pr comment [PR_NUMBER] --body "
## 🔍 Accessibility Review Summary

**Total Issues Found:** [X]
- 🔴 Critical: [X]
- 🟠 High: [X]
- 🟡 Medium: [X]
- 🔵 Low: [X]

**WCAG Success Criteria Affected:**
[List of violated SCs]

**Files Reviewed:**
- ✅ [file1.ext]
- ✅ [file2.ext]
- ⚠️ [file3.ext] - [X] issues found

**Quick Stats:**
- Changed files analyzed: [X]
- UI components checked: [X]
- Accessibility issues found: [X]

---

### 📋 Issues by Severity

#### 🔴 Critical Issues ([X])
[Brief list with file references]

#### 🟠 High Priority ([X])
[Brief list with file references]

#### 🟡 Medium Priority ([X])
[Brief list with file references]

#### 🔵 Low Priority ([X])
[Brief list with file references]

---

### 🎯 Recommended Actions

1. **Immediate fixes required:** [Critical issues that block merge]
2. **High priority:** [Should be fixed before merge]
3. **Can be addressed in follow-up:** [Medium/Low issues]

---

### 📚 Resources

- [Link to platform-specific accessibility guide]
- [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [Link to internal documentation]

---

🤖 Automated review by /pr-review command
📅 Reviewed: [Date]
🔖 Based on WCAG 2.2 Level AA
"
```

### Step 6: Optional - Generate Report File

If requested or if running in CI, also generate a markdown report file:

**Save to:** `./accessibility-audit/reports/pr/PR_[NUMBER]_Accessibility_Review_[DATE].md`

Use simplified template:
- PR metadata (number, title, author, branch)
- Files changed
- Issues found (grouped by severity)
- Suggestions for fixing
- Links to full WCAG documentation

## CI Integration Mode

When running in CI (detected by CI environment variables):

1. **Auto-detect PR number** from `GITHUB_EVENT_PATH` or similar
2. **Run silently** without interactive prompts
3. **Post all comments** automatically
4. **Exit with status code:**
   - `0` - No critical issues
   - `1` - Critical issues found (block merge)
   - `2` - High priority issues found (warning)

**Example CI usage:**
```bash
# In GitHub Actions workflow
- name: Accessibility PR Review
  run: |
    claude-code "/pr-review"
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Interactive Mode

When running manually (not in CI):

1. **Detect or ask for PR number:**
   ```
   Which PR would you like to review?

   Options:
   1. Current branch PR (auto-detect)
   2. Specific PR number
   3. Compare branches manually
   ```

2. **Confirm before posting:**
   ```
   Found [X] accessibility issues:
   - Critical: [X]
   - High: [X]
   - Medium: [X]
   - Low: [X]

   Post comments to PR #[NUMBER]? (yes/no)
   ```

3. **Show preview** of what will be posted

## Critical Requirements

⚠️ **IMPORTANT RULES:**

1. **Only review changed code** - Don't audit unchanged files
2. **Focus on accessibility** - Ignore non-accessibility code quality issues
3. **Provide fixes** - Always include suggested code corrections
4. **Be specific** - Include file paths and line numbers
5. **Use severity correctly** - Follow SEVERITY_GUIDELINES.md
6. **Post useful comments** - Actionable feedback, not generic advice
7. **Don't spam** - Group related issues, avoid duplicate comments
8. **Respect context** - Consider existing accessibility implementation

⚠️ **DON'T:**
- ❌ Review entire codebase (only changed files)
- ❌ Report issues in unchanged code
- ❌ Post comments on non-accessibility issues
- ❌ Create issues for working accessibility features
- ❌ Duplicate comments on same issue
- ❌ Post vague feedback without examples

⚠️ **DO:**
- ✅ Focus on changed lines and new code
- ✅ Check if changes break existing accessibility
- ✅ Verify new components have proper accessibility
- ✅ Provide specific code examples for fixes
- ✅ Link to relevant guidelines
- ✅ Group related issues in one comment
- ✅ Use appropriate severity levels

## Severity Guidelines for PR Reviews

Use these criteria from SEVERITY_GUIDELINES.md:

- **Critical:** Blocks users with disabilities from core functionality
  - Icon-only buttons without labels
  - Form inputs without labels
  - Keyboard traps
  - Complete loss of functionality with assistive tech

- **High:** Significant barriers, workarounds possible but difficult
  - Poor contrast ratios
  - Missing focus indicators
  - Incorrect heading structure
  - Missing alt text on informative images

- **Medium:** Accessibility issues that cause inconvenience
  - Non-ideal labels (but labels present)
  - Touch targets slightly too small
  - Missing hints on complex inputs
  - Redundant announcements

- **Low:** Minor issues, good UX improvements
  - Could improve label clarity
  - Could add additional context
  - Nice-to-have enhancements

## Error Handling

**If gh CLI fails:**
```
⚠️ Could not access PR via GitHub CLI.

Options:
1. Authenticate: gh auth login
2. Check repository access
3. Provide PR diff manually
4. Continue without posting comments (review only)
```

**If PR not found:**
```
⚠️ Could not find PR #[NUMBER]

Please verify:
- PR number is correct
- You're in the correct repository
- You have access to the PR
```

**If no accessibility issues found:**
```
✅ No accessibility issues found in this PR!

Changed files reviewed: [X]
All changes follow accessibility best practices.

Note: This is an automated review. Manual testing with assistive
technologies is still recommended for complex UI changes.
```

## Start - Command Execution

When user types `/pr-review`, follow these steps:

1. **Use TodoWrite** to create tracking tasks:
   - Detect PR and fetch information
   - Load appropriate platform guides
   - Analyze changed files
   - Post PR comments
   - Generate summary

2. **Check for arguments:**
   - `/pr-review` - Auto-detect PR
   - `/pr-review 123` - Review PR #123
   - `/pr-review --no-post` - Review without posting (dry-run)

3. **Execute workflow** (Steps 1-6 above)

4. **Provide feedback** to user:
   - Number of issues found
   - Link to PR with comments
   - Path to report file (if generated)

---

## Examples

### Example 1: Auto-detect PR
```
User: /pr-review

Bot:
Detected PR #456: "Add new login screen"
Branch: feature/login-ui → main
Files changed: 8 files

Loading guides...
✅ Loaded iOS accessibility guide
✅ Loaded WCAG reference

Analyzing changes...
⏳ Reviewing LoginViewController.swift
⏳ Reviewing LoginView.swift
...

Found 3 accessibility issues:
- Critical: 1
- High: 1
- Medium: 1

Posting comments to PR #456...
✅ Posted inline comments
✅ Posted summary comment

View PR: https://github.com/org/repo/pull/456
Report saved: ./accessibility-audit/reports/pr/PR_456_Accessibility_Review_2026-02-02.md
```

### Example 2: Specific PR number
```
User: /pr-review 789

Bot:
Fetching PR #789...
✅ PR #789: "Update settings screen"

[... continues with workflow ...]
```

### Example 3: No issues found
```
User: /pr-review

Bot:
Analyzed PR #123: "Fix typo in README"

Files changed: 1 (README.md)
No UI changes detected - skipping accessibility review.

✅ No accessibility review needed for this PR.
```

---

## Post-Review Actions

After review is complete:

1. **Notify user** with summary
2. **Provide links** to PR comments
3. **Suggest next steps** if critical issues found
4. **Offer to run full audit** if major changes detected

**Example:**
```
✅ PR review complete!

3 accessibility issues found and commented on PR #456.

⚠️ 1 critical issue blocks merge - please fix before merging.

Need more detailed review? Run:
- /audit - Full accessibility audit
- /fix-accessibility - Apply fixes from previous audit
```
