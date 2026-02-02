# Fix Accessibility Issues

You are fixing accessibility issues from a previously generated audit report.

## Workflow

### Step 1: Detect and List Available Reports

**First, check if user specified report in their message:**
```
User: /fix-accessibility from the iOS home screen report
User: /fix-accessibility iOS HomeScreen
User: /fix-accessibility report #1
```

If specified, try to identify the report and skip to Step 2.

**Otherwise, search for all audit reports:**
```
accessibility-audit/reports/**/*.md
```

**For each report found, extract:**
- Platform (from path or filename)
- Feature/area (from filename)
- Date (from filename)
- Issue count (parse report to count Critical/High/Medium/Low)

**Present as numbered choices with details:**
```
I've found 4 audit reports in this project:

iOS Reports:
  1. Home Screen (2025-12-22) - 45 issues
     • 5 Critical, 12 High, 20 Medium, 8 Low
     File: Accessibility_Audit_iOS_HomeScreen_2025-12-22.md

  2. Settings (2025-12-15) - 23 issues
     • 2 Critical, 8 High, 10 Medium, 3 Low
     File: Accessibility_Audit_iOS_Settings_2025-12-15.md

Android Reports:
  3. Home Screen (2025-12-20) - 32 issues
     • 4 Critical, 10 High, 15 Medium, 3 Low
     File: Accessibility_Audit_Android_HomeScreen_2025-12-20.md

Web Reports:
  4. Login Page (2025-12-18) - 12 issues
     • 1 Critical, 4 High, 5 Medium, 2 Low
     File: Accessibility_Audit_Web_Login_2025-12-18.md

Which report would you like to fix? (Enter number or describe)
```

**If no reports found:**
```
❌ No audit reports found in accessibility-audit/reports/

Have you run an audit yet? Try:
  /audit

Once you have a report, run /fix-accessibility to fix the issues.
```

**If only one report found:**
```
I found 1 audit report:

iOS Home Screen (2025-12-22) - 45 issues
• 5 Critical, 12 High, 20 Medium, 8 Low

Would you like to fix issues from this report? (yes/no)
```

### Step 2: Load, Parse, and Present Fix Options

Once user selects a report:
1. Read the selected report file
2. Parse all issues from the report
3. Extract for each issue:
   - Issue number
   - Title
   - Severity
   - File path and line number
   - Current code
   - Recommended fix
   - WCAG SC violated

**Display detailed summary with options:**
```
✓ Loaded: Accessibility_Audit_iOS_HomeScreen_2025-12-22.md

Found 45 issues:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical (5 issues):
  • Issue #001: Play button missing accessibility label
  • Issue #002: Channel logos not hidden from screen reader
  • Issue #008: Tab bar selected state not announced
  • Issue #015: Form inputs missing persistent labels
  • Issue #023: Collection items require multiple swipes

High (12 issues):
  • Issue #003: Text contrast below 4.5:1
  • Issue #005: Missing heading structure
  ...

Medium (20 issues): [collapsed, showing first 3]
  • Issue #012: Decorative images not marked
  • Issue #018: Button labels include role name
  ...

Low (8 issues): [collapsed]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What would you like to fix?

1. ⚡ Critical issues only (5 issues) - Start here!
2. 🔥 Critical + High (17 issues) - Recommended
3. ✅ All issues (45 issues) - Complete fix
4. 🎯 Specific issues (I'll show the full list)
5. 📋 Review issue details first (then decide)

Enter number (or describe what you want):
```

**If user chooses "Review details first" (#5):**
Show complete list with file paths:
```
Full Issue List:

Critical:
  #001: Play button missing label
        File: VideoTileView.swift:45

  #002: Channel logos not hidden
        File: ChannelLogoView.swift:23
  ...

[After showing full list]
What would you like to fix? (Choose from options 1-4 above)
```

**If user chooses "Specific issues" (#4):**
```
Which issues would you like to fix?

Options:
• Enter issue numbers: 1,2,5,8
• Enter range: 1-10
• Enter severity: critical, high
• Describe: "all button issues", "only forms"

What would you like to fix?
```

### Step 3: Fix Issues

Use TodoWrite to track progress:
```
- Fix Issue #001: [Title] (Critical)
- Fix Issue #002: [Title] (High)
- Fix Issue #003: [Title] (Medium)
...
```

For each issue to fix:

1. **Read the file** mentioned in the issue
2. **Verify the issue** still exists (code might have changed)
3. **Apply the recommended fix** from the report
4. **Mark todo as completed**
5. **Track the fix** in memory for summary

If the current code doesn't match what's in the report:
- Inform the user
- Show current code vs expected code
- Ask if they want to skip or attempt fix anyway

### Step 4: Generate Fix Summary

After all fixes are applied, create a summary report:

**Filename:** `[original-report-name]_FIXES_[DATE].md`
**Location:** Same folder as the original report

**Template:**
```markdown
# Accessibility Fixes Summary
## [Original Report Name]

**Original Report:** [filename]
**Fix Date:** [YYYY-MM-DD]
**Fixed By:** Claude Code (AI Assistant)

---

## Summary

**Total Issues in Report:** X
**Issues Fixed:** X
**Issues Skipped:** X (with reasons)
**Success Rate:** X%

### By Severity
- **Critical:** X fixed / X total
- **High:** X fixed / X total
- **Medium:** X fixed / X total
- **Low:** X fixed / X total

---

## Fixes Applied

### Issue #XXX: [Title] ✅ FIXED

**Severity:** Critical
**WCAG SC:** X.X.X (Level X)
**File:** `path/to/file.ext:123`

**Original Code:**
```[language]
[original code]
```

**Applied Fix:**
```[language]
[fixed code]
```

**Status:** ✅ Successfully applied

---

### Issue #XXX: [Title] ⚠️ SKIPPED

**Severity:** High
**File:** `path/to/file.ext:456`

**Reason:** Code has changed since audit. Current code doesn't match expected code from report.

**Action Required:** Manual review needed.

---

## Issues Skipped (Detail)

If any issues were skipped, provide details:
- Why they were skipped
- What needs to be done manually
- Current vs expected state

---

## Next Steps

1. **Test the fixes:**
   - [ ] Run the application
   - [ ] Test with screen reader (VoiceOver/TalkBack)
   - [ ] Verify all fixed issues work correctly

2. **Run tests:**
   - [ ] Run unit tests
   - [ ] Run integration tests
   - [ ] Check for regressions

3. **Commit changes:**
   ```bash
   git add .
   git commit -m "fix: accessibility issues from [report-name]

   Fixes [X] accessibility issues:
   - [X] Critical issues
   - [X] High issues
   - [X] Medium issues
   - [X] Low issues

   🤖 Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

4. **Verify fixes:**
   - Review the fixes summary above
   - Test each fix manually
   - Update audit tracking if applicable

---

## Files Modified

List of all files that were changed:
- `path/to/file1.ext` (X issues fixed)
- `path/to/file2.ext` (X issues fixed)
- `path/to/file3.ext` (X issues fixed)

**Total files modified:** X

---

## Recommendations

- Run automated accessibility tests if available
- Perform manual testing with assistive technologies
- Consider updating documentation if UI changed significantly
- If any issues were skipped, review them manually

---

**Generated:** [YYYY-MM-DD HH:MM]
**Tool:** Claude Code - Accessibility Fixer
```

---

## Important Guidelines

### Before Fixing
1. **Always read the file first** - Never edit without reading
2. **Verify the issue exists** - Code might have changed
3. **Use exact matches** - Make sure old_string matches exactly
4. **Check file paths** - Ensure paths are still valid

### While Fixing
1. **Use Edit tool** - Never use Write for existing files
2. **Preserve formatting** - Match existing indentation and style
3. **One issue at a time** - Don't batch multiple changes in one edit
4. **Update TodoWrite** - Mark each issue as completed immediately

### Error Handling
If you encounter errors:
- **File not found:** Note in summary, mark as skipped
- **Code doesn't match:** Show difference, ask user
- **Syntax errors:** Warn user, offer alternative
- **Build failures:** Stop, report to user

### Code Quality
1. **Don't over-engineer** - Apply the fix from the report, nothing more
2. **Match existing style** - Follow the project's coding conventions
3. **Preserve functionality** - Only change accessibility properties
4. **Don't refactor** - This is not a refactoring session

### Safety Checks
- ✅ Never delete code unless explicitly in the fix
- ✅ Never modify logic beyond accessibility fixes
- ✅ Never introduce new dependencies
- ✅ Never change file structure
- ⚠️ If a fix seems risky, ask the user first

---

## Example Session

```
User: /fix-accessibility

Claude: I'll help you fix accessibility issues from a previous audit.

        Let me search for audit reports...

        Found 3 audit reports:

        iOS:
          1. Accessibility_Audit_iOS_HomeScreen_2025-12-22.md (45 issues)

        Android:
          2. Accessibility_Audit_Android_HomeScreen_2025-12-20.md (32 issues)

        Which report would you like to fix issues from?

User: 1

Claude: Loading Accessibility_Audit_iOS_HomeScreen_2025-12-22.md...

        Found 45 issues:
        - Critical: 5
        - High: 12
        - Medium: 20
        - Low: 8

        Would you like to fix:
        1. All issues (45 total)
        2. Critical and High only (17 issues)
        3. Specific issues (I'll ask which)
        4. Let me review the list first

User: 2

Claude: I'll fix all Critical and High severity issues (17 total).

        [Creates TodoList with 17 items]

        Starting fixes...

        [Fixes each issue, marks todos as completed]

        ✅ Fixed 16 of 17 issues!
        ⚠️  1 issue skipped (code changed since audit)

        Summary saved to:
        accessibility-audit/reports/ios/Accessibility_Audit_iOS_HomeScreen_2025-12-22_FIXES_2025-12-22.md
```

---

## Start

Begin by searching for audit reports and listing them for the user to select.
