# ⚠️ IMPORTANT: Audit Requirements
## Critical Information for All Audits

---

## 📅 CRITICAL: Use Correct Date in Reports

**⚠️ ALWAYS check the `<env>` section for "Today's date" before generating reports!**

- **Current date:** October 29, 2025
- **Format options:**
  - YYYY-MM-DD: `2025-10-29`
  - Month Day, Year: `October 29, 2025`
- **DO NOT use:** January 2025 or any other incorrect month
- **Source:** Check `<env>Today's date: YYYY-MM-DD</env>` at conversation start

---

## 📝 CRITICAL: Descriptive Report Filenames

**⚠️ ALWAYS use descriptive filenames that include date, platform, and what was tested!**

**Required Format:**
```
Accessibility_Audit_[Platform]_[FeatureOrArea]_[Date].md
```

**Components:**
1. **Platform:** Web, Android, iOS, tvOS, AndroidTV, ReactNative, Flutter, etc.
2. **FeatureOrArea:** What you tested (Login, Checkout, Navigation, Forms, Dashboard, etc.)
3. **Date:** YYYY-MM-DD format (e.g., 2025-10-30)

**Examples:**
- ✅ `Accessibility_Audit_Android_LoginScreen_2025-10-30.md`
- ✅ `Accessibility_Audit_Web_CheckoutFlow_2025-10-30.md`
- ✅ `Accessibility_Audit_iOS_NavigationBar_2025-10-30.md`
- ✅ `Accessibility_Audit_Web_FormsAndInputs_2025-10-30.md`
- ✅ `Accessibility_Audit_Android_HomeScreen_2025-10-30.md`

**❌ BAD Examples (Not Descriptive):**
- ❌ `Accessibility_Audit_Web_2025-10-30.md` (missing feature/area)
- ❌ `report.md` (no context)
- ❌ `audit1.md` (meaningless)
- ❌ `Accessibility_Audit_Android.md` (missing date and feature)

**Why This Matters:**
- **Searchable:** Easy to find specific audits later
- **Organized:** Clear what each report covers
- **Trackable:** Date shows progression and freshness
- **Professional:** Demonstrates systematic approach
- **Multiple audits:** Can have multiple reports per platform for different features

**Special Cases:**

**Interim Summary Reports:**
```
Accessibility_Audit_[Platform]_InterimSummary_[Date].md
Example: Accessibility_Audit_Web_InterimSummary_2025-10-30.md
```

**Critical-Only Scans:**
```
Accessibility_Audit_[Platform]_CriticalScan_[Date].md
Example: Accessibility_Audit_Android_CriticalScan_2025-10-30.md
```

**Specific Issue Type Audits:**
```
Accessibility_Audit_[Platform]_[IssueType]_[Date].md
Example: Accessibility_Audit_iOS_ColorContrast_2025-10-30.md
```

**Multi-Word Features:**
Use CamelCase or underscores:
- ✅ `Accessibility_Audit_Web_UserProfile_2025-10-30.md`
- ✅ `Accessibility_Audit_Android_SettingsScreen_2025-10-30.md`

---

## 🚫 CRITICAL: Avoid Role Names in Labels

**⚠️ ALWAYS check that accessible labels do NOT include the role name!**

**The Problem:**
Screen readers automatically announce element roles. Including the role in labels causes redundant announcements:

- ❌ "Close Button" → Screen reader: **"Close Button, button"** (says "button" twice!)
- ❌ "Home Link" → Screen reader: **"Home Link, link"** (says "link" twice!)
- ❌ "Agree Checkbox" → Screen reader: **"Agree Checkbox, checkbox"** (says "checkbox" twice!)

**The Solution:**
Remove role names from labels:

- ✅ "Close" → Screen reader: **"Close, button"** (clean!)
- ✅ "Home" → Screen reader: **"Home, link"** (clean!)
- ✅ "Agree" → Screen reader: **"Agree, checkbox"** (clean!)

**What to Check:**

Search for labels ending with these words:
- ❌ "Button" / "button" / "btn"
- ❌ "Link" / "link"
- ❌ "Tab" / "tab"
- ❌ "Checkbox" / "checkbox"
- ❌ "Input" / "input" / "field" / "textfield"
- ❌ "Menu" / "menu"
- ❌ "Toggle" / "switch"

**Common Offenders:**
- "Submit Button" → Should be "Submit"
- "Close Button" → Should be "Close"
- "Home Link" → Should be "Home"
- "Email Text Field" → Should be "Email"
- "Agree Checkbox" → Should be "Agree"
- "Settings Tab" → Should be "Settings"

**Exception:**
Role words ARE acceptable when describing what the element **affects**, not what it **is**:
- ✅ "Open Menu" (button) - "Menu" is what opens
- ✅ "Choose File" (button) - "File" is what you choose
- ❌ "Close Button" - "Button" describes what it is

**Pattern Detection:**
```
Android: contentDescription=".*[Bb]utton"
iOS: accessibilityLabel=".*[Bb]utton"
Web: aria-label=".*[Bb]utton" or >.*Button</button>
```

**See full guide:** `guides/patterns/AVOID_ROLE_IN_LABEL.md`

---

## 🎯 Non-Negotiable Requirements

Every issue found during an accessibility audit **MUST** include:

### 1. Exact Source Code Reference

✅ **Required:**
- **File path** (project-relative): `src/components/Button.tsx`
- **Line number** (exact): `45`
- **Current code** (actual code from that line)
- **Recommended fix** (copy-pasteable replacement code)

❌ **Not Acceptable:**
- "In the login page" (too vague)
- "Around line 40-50" (not exact)
- "The button component" (no file path)
- No code snippets shown

---

### 2. Predetermined Screenshot Filename

✅ **Required Pattern:**
```
issue_[###]_[short_description].png

Examples:
- issue_001_button_no_label.png
- issue_002_low_contrast_text.png
- issue_015_missing_form_label.png
```

❌ **Not Acceptable:**
- `screenshot1.png`
- `IMG_1234.png`
- `issue1.png` (missing leading zeros)
- `button-no-label.png` (missing issue number)

---

## 📋 Complete Issue Template

Use this template for EVERY issue:

```markdown
#### Issue #001: [Brief Title]

**WCAG SC Violated:**
- **Primary:** [SC X.X.X - Name] (Level X)
- **Secondary:** [SC Y.Y.Y - Name] (Level Y)

**Severity:** [Critical/High/Medium/Low]

**Location:** ⚠️ MUST BE EXACT
- **File:** `path/to/file.ext`
- **Line:** `123`
- **Component:** [Component/Function name]

**Current Code:** ⚠️ MUST SHOW ACTUAL CODE
```[language]
[Exact code from the file]
```

**Recommended Fix:** ⚠️ MUST BE COPY-PASTEABLE
```[language]
[Fixed code that developer can copy/paste]
```

**Visual Evidence:** ⚠️ MUST USE NAMING PATTERN
![Screenshot](screenshots/[platform]/issue_001_[description].png)
```

---

## 🔍 Example: Properly Documented Issue

```markdown
#### Issue #001: Play Button Missing Accessible Label

**WCAG SC Violated:**
- **Primary:** 4.1.2 Name, Role, Value (Level A)
- **Secondary:** 2.4.4 Link Purpose (Level A)

**Severity:** Critical
**Impact:** Screen reader users cannot determine button purpose

**Location:**
- **File:** `src/components/VideoPlayer.tsx`
- **Line:** 45
- **Screen:** Video Player
- **Component:** PlayButton

**Description:**
The play button contains only an icon without an accessible label.
Screen readers announce "button" without context.

**Current Code:**
```tsx
// src/components/VideoPlayer.tsx:45
<button onClick={handlePlay}>
  <PlayIcon />
</button>
```

**Recommended Fix:**
```tsx
<button onClick={handlePlay} aria-label="Play video">
  <PlayIcon aria-hidden="true" />
</button>
```

**Steps to Reproduce:**
1. Navigate to /video/12345
2. Enable screen reader (NVDA/VoiceOver)
3. Tab to play button
4. Notice it only announces "button"

**Visual Evidence:**
![Play button showing icon without label](screenshots/web/issue_001_button_no_label.png)

**Screen Reader Behavior:**
- **Current:** "button"
- **Expected:** "Play video, button"

**Resources:**
- https://www.w3.org/WAI/WCAG22/Understanding/name-role-value
```

---

## 🚫 Common Mistakes - DO NOT DO THIS

### ❌ Mistake 1: Vague Location

```markdown
**Location:**
The button on the login page

**Fix:** Use specific file path and line number
```

### ❌ Mistake 2: No Code Shown

```markdown
The image needs alt text.

**Fix:** Show current code AND recommended fix with code snippets
```

### ❌ Mistake 3: Bad Screenshot Names

```markdown
![Screenshot](screenshots/web/screenshot1.png)
![Screenshot](screenshots/web/IMG_5678.png)

**Fix:** Use pattern: issue_001_description.png
```

### ❌ Mistake 4: No Line Number

```markdown
File: src/App.tsx
The button is in the render function.

**Fix:** Provide exact line number
```

---

## ✅ Quality Checklist

Before finalizing any audit report, verify EVERY issue has:

- [ ] **File path** (project-relative)
- [ ] **Line number** (exact)
- [ ] **Current code** (from that file/line)
- [ ] **Recommended fix** (copy-pasteable)
- [ ] **Screenshot filename** (issue_###_description.png pattern)
- [ ] **WCAG SC** (primary and secondary)
- [ ] **Severity** (Critical/High/Medium/Low)
- [ ] **Impact** (who is affected)
- [ ] **Screen reader behavior** (current vs expected)

---

## 📸 Screenshot Naming Rules

### Pattern
```
issue_[###]_[short_description].png
```

### Rules
1. **Number:** 3 digits with leading zeros (001, 002, 015, 099, 100)
2. **Description:** lowercase, underscores, 2-5 words max
3. **Extension:** .png (or .jpg if necessary)

### Examples by Issue Type

```
Web:
- issue_001_button_no_label.png
- issue_002_low_contrast_text.png
- issue_003_missing_form_label.png
- issue_004_keyboard_trap_modal.png
- issue_005_missing_alt_text.png

Android:
- issue_001_missing_content_desc.png
- issue_002_small_touch_target.png
- issue_003_edittext_no_label.png
- issue_004_image_no_description.png

iOS:
- issue_001_missing_accessibility_label.png
- issue_002_wrong_trait.png
- issue_003_no_voiceover_support.png
```

---

## 🎯 When Creating Audit Reports

### Prompt Template

Always include these requirements in your audit request:

```
Audit [feature/screen] for accessibility issues.

Platform: [web/android/ios]
Follow: guides/GUIDE_[PLATFORM].md

CRITICAL REQUIREMENTS:
1. Every issue MUST include:
   - Exact file path (project-relative)
   - Exact line number
   - Current code snippet
   - Recommended fix (copy-pasteable)

2. Screenshots MUST use naming pattern:
   - issue_###_short_description.png
   - Example: issue_001_button_no_label.png

3. Create report at:
   accessibility-audit/reports/[platform]/Accessibility_Audit_[Platform]_[Feature]_[Date].md
```

---

## 📚 Related Documentation

- **CODE_REFERENCES_AND_SCREENSHOTS.md** - Detailed guide on code references
- **AUDIT_REPORT_TEMPLATE.md** - Full report template
- **guides/GUIDE_[PLATFORM].md** - Platform-specific code patterns

---

## 💡 Why This Matters

### For Developers
- Know **exactly** where to fix issues
- No time wasted searching for problems
- Copy-paste fixes directly
- Faster remediation

### For Auditors
- Professional, actionable reports
- Clear traceability
- Easy to verify fixes
- Standardized documentation

### For Project Managers
- Track issues precisely
- Assign to specific files/components
- Monitor fix progress
- Quality assurance

---

## ⚡ Quick Reference

**Every issue needs:**
1. 📍 File path + line number
2. 📝 Current code
3. ✅ Fix code
4. 📸 Screenshot (issue_###_description.png)

**No exceptions. No shortcuts.**

---

**Read Full Guide:** CODE_REFERENCES_AND_SCREENSHOTS.md
