# Code References and Screenshots Guide
## Ensuring Actionable, Traceable Audit Reports

---

## Critical Requirements

### Every Issue MUST Include:

1. ✅ **Exact file path** (project-relative)
2. ✅ **Exact line number** where the issue occurs
3. ✅ **Current code snippet** from that location
4. ✅ **Recommended fix code** (copy-pasteable)
5. ✅ **Screenshot filename** (predetermined pattern)

**Why?** Developers need to know EXACTLY where to fix the issue. Vague references like "in the login page" are not acceptable.

---

## File Path References

### Format

Always use **project-relative paths** starting from the project root:

```
✅ CORRECT: src/components/Header.tsx
✅ CORRECT: app/src/main/java/com/example/MainActivity.kt
✅ CORRECT: lib/screens/home_screen.dart

❌ WRONG: ../../../Header.tsx
❌ WRONG: Header.tsx (no path context)
❌ WRONG: ~/projects/myapp/src/Header.tsx (absolute path)
```

### Examples by Platform

**Web/React:**
```
File: src/components/auth/LoginForm.tsx
Line: 45
```

**Android:**
```
File: app/src/main/res/layout/activity_main.xml
Line: 23
```

**iOS/Swift:**
```
File: MyApp/Views/ProfileViewController.swift
Line: 67
```

**React Native:**
```
File: src/screens/HomeScreen.js
Line: 34
```

**Flutter:**
```
File: lib/widgets/custom_button.dart
Line: 12
```

---

## Line Numbers

### Requirements

- **MUST be exact** - The line where the issue occurs
- **MUST be current** - Based on the code at audit time
- **MUST be specific** - Not a range unless the issue spans multiple lines

### Examples

```
✅ CORRECT:
File: src/components/Button.tsx
Line: 45

❌ WRONG:
File: src/components/Button.tsx
Line: somewhere around line 40-50
```

### Multi-Line Issues

If an issue spans multiple lines, specify the starting line and range:

```
✅ CORRECT:
File: src/components/Modal.tsx
Line: 89-95 (7 lines)
```

---

## Code Snippets

### Current Code

**MUST show the actual code** from the file at the specified line number.

#### Example: Missing Alt Text

```
**File:** src/pages/Home.tsx
**Line:** 23

**Current Code:**
```tsx
<img src="/logo.png" />
```
```

#### Example: Missing Content Description (Android)

```
**File:** app/src/main/res/layout/fragment_home.xml
**Line:** 45-49

**Current Code:**
```xml
<ImageButton
    android:id="@+id/playButton"
    android:src="@drawable/ic_play"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```
```

### Recommended Fix

**MUST be copy-pasteable** - Developer should be able to copy and replace the code.

#### Example: Alt Text Fix

```
**Recommended Fix:**
```tsx
<img src="/logo.png" alt="Company name logo" />
```
```

#### Example: Content Description Fix (Android)

```
**Recommended Fix:**
```xml
<ImageButton
    android:id="@+id/playButton"
    android:src="@drawable/ic_play"
    android:contentDescription="@string/play_button"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

Don't forget to add to res/values/strings.xml:
```xml
<string name="play_button">Play</string>
```
```

### Context

For complex issues, show surrounding code for context:

```
**File:** src/components/Form.tsx
**Line:** 67

**Current Code (with context):**
```tsx
// Lines 65-70
function LoginForm() {
  return (
    <form>
      <input type="email" placeholder="Email" />  {/* ← Line 67: Issue here */}
      <button>Submit</button>
    </form>
  );
}
```
```

---

## Screenshot Naming Convention

### Standard Pattern

```
issue_[NUMBER]_[SHORT_DESCRIPTION].png
```

**Rules:**
- Number must be **3 digits** with leading zeros: `001`, `002`, `099`, `100`
- Description must be **lowercase with underscores**
- Description should be **2-5 words** max
- Extension is always **.png** (or .jpg if needed)

### Examples

```
✅ CORRECT:
- issue_001_button_no_label.png
- issue_002_low_contrast_text.png
- issue_003_missing_form_label.png
- issue_015_keyboard_trap_modal.png
- issue_042_small_touch_target.png

❌ WRONG:
- Issue1.png (missing zeros, wrong case)
- issue_1_button-no-label.png (hyphens instead of underscores)
- button_without_label.png (missing issue number)
- issue_001_this_button_does_not_have_a_proper_label_for_screen_readers.png (too long)
```

### Platform-Specific Paths

Screenshots are organized by platform:

```
screenshots/
├── web/
│   ├── issue_001_button_no_label.png
│   ├── issue_002_low_contrast.png
│   └── issue_003_missing_alt_text.png
├── android/
│   ├── issue_001_missing_content_desc.png
│   ├── issue_002_small_touch_target.png
│   └── issue_003_unlabeled_edittext.png
├── ios/
│   ├── issue_001_missing_accessibility_label.png
│   └── issue_002_incorrect_trait.png
└── react-native/
    └── issue_001_image_no_label.png
```

### In Report References

Always use relative paths from the report location:

```markdown
**Visual Evidence:**
![Screenshot showing button without label](screenshots/web/issue_001_button_no_label.png)
```

Or with just the filename if using HTML comment for reference:

```markdown
**Visual Evidence:**
<!-- Screenshot: issue_001_button_no_label.png -->
![Button without accessibility label](screenshots/web/issue_001_button_no_label.png)
```

---

## Complete Issue Example

Here's a properly documented issue with all requirements met:

```markdown
#### Issue #001: Image Button Missing Accessibility Label

**WCAG SC Violated:**
- **Primary:** 1.1.1 Non-text Content (Level A)
- **Secondary:** 4.1.2 Name, Role, Value (Level A)

**Severity:** Critical
**Impact:** Screen reader users cannot understand the button's purpose

**Location:**
- **File:** `src/components/player/Controls.tsx`
- **Line:** 45
- **Screen:** Video Player
- **Component:** `PlayButton`

**Description:**
The play button uses an icon without an accessible label. Screen readers announce "button" without describing its purpose, leaving users unable to understand that it controls video playback.

**Current Code:**
```tsx
// src/components/player/Controls.tsx:45
<button onClick={handlePlay}>
  <PlayIcon />
</button>
```

**Recommended Fix:**
```tsx
// Add aria-label to provide accessible name
<button onClick={handlePlay} aria-label="Play video">
  <PlayIcon />
</button>

// Or use visually-hidden text:
<button onClick={handlePlay}>
  <span className="visually-hidden">Play video</span>
  <PlayIcon aria-hidden="true" />
</button>
```

**Steps to Reproduce:**
1. Navigate to video player page
2. Enable VoiceOver (macOS) or NVDA (Windows)
3. Tab to the play button
4. Observe that it announces "button" with no context

**Visual Evidence:**
![Play button with icon but no label](screenshots/web/issue_001_button_no_label.png)

**Screen Reader Behavior:**
- **Current:** "button"
- **Expected:** "Play video, button"

**Resources:**
- [WCAG 1.1.1 Understanding](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content)
- [WCAG 4.1.2 Understanding](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value)
- [MDN: ARIA button role](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/button_role)
```

---

## Quality Checklist

Before submitting an audit report, verify each issue has:

- [ ] **Exact file path** (project-relative)
- [ ] **Exact line number** (not a range unless necessary)
- [ ] **Current code snippet** (shows the actual problem)
- [ ] **Recommended fix** (copy-pasteable solution)
- [ ] **Screenshot filename** (follows naming convention)
- [ ] **Screenshot placeholder** (in markdown with correct path)
- [ ] **WCAG SC references** (primary and secondary if applicable)
- [ ] **Severity level** (Critical, High, Medium, Low)
- [ ] **Impact description** (who is affected and how)
- [ ] **Screen reader behavior** (current vs expected)

---

## Common Mistakes to Avoid

### ❌ Vague Location References

```
BAD:
Location: The login page
File: LoginForm
```

```
GOOD:
Location:
- File: src/pages/auth/LoginForm.tsx
- Line: 67
- Component: EmailInput
```

### ❌ No Code Shown

```
BAD:
The image is missing alt text.

Fix: Add alt text to the image.
```

```
GOOD:
Current Code:
```tsx
<img src="/hero.jpg" />
```

Recommended Fix:
```tsx
<img src="/hero.jpg" alt="Team celebrating project launch" />
```
```

### ❌ Generic Screenshot Names

```
BAD:
- screenshot1.png
- IMG_1234.png
- Screen Shot 2025-01-29 at 2.30.45 PM.png
```

```
GOOD:
- issue_001_button_no_label.png
- issue_002_low_contrast_text.png
- issue_003_missing_form_label.png
```

### ❌ Missing Line Numbers

```
BAD:
File: src/App.tsx
The button is somewhere in the render function.
```

```
GOOD:
File: src/App.tsx
Line: 145
The button element at line 145 is missing an accessible name.
```

---

## Screenshot Capture Guide

### What to Capture

1. **The problematic element** - Clearly visible
2. **Context** - Enough surrounding UI to understand location
3. **Highlight** - Optional: Add red box or arrow to indicate issue
4. **Screen reader output** - If showing SR behavior, capture that too

### Tools

**Web:**
- Browser DevTools screenshot feature
- OS screenshot tool (Cmd+Shift+4 on Mac, Win+Shift+S on Windows)
- Browser extensions (Awesome Screenshot, etc.)

**Mobile:**
- Device screenshot (Power+Volume on Android, Power+Home/Side on iOS)
- Emulator/Simulator screenshot tools
- With TalkBack/VoiceOver visible if showing SR behavior

### Naming When Capturing

Use the predetermined names from the report:

1. Take screenshot
2. Immediately rename to match report: `issue_001_button_no_label.png`
3. Move to correct platform folder: `screenshots/web/`

### Organization

```
accessibility-audit/
├── reports/
│   └── web/
│       └── Accessibility_Audit_Web_Login_2025-01-29.md
└── screenshots/
    └── web/
        ├── issue_001_button_no_label.png        ← Referenced in report
        ├── issue_002_low_contrast_text.png      ← Referenced in report
        └── issue_003_missing_form_label.png     ← Referenced in report
```

---

## Automation Support

### For Claude Code Audits

When requesting an audit, emphasize code references:

```
Audit the login page for accessibility issues.

Platform: Web
File: src/pages/LoginPage.tsx

IMPORTANT:
- Provide EXACT file paths and line numbers for every issue
- Show current code and recommended fix for each issue
- Use screenshot naming pattern: issue_###_description.png
- Reference platform guide: guides/GUIDE_WEB.md
```

### Template for Issues

Use this template when documenting issues:

```markdown
#### Issue #[NNN]: [Title]

**Location:**
- File: `[path/to/file.ext]`
- Line: `[line-number]`

**Current Code:**
```[lang]
[actual code from the file]
```

**Recommended Fix:**
```[lang]
[fixed code]
```

**Screenshot:**
![Description](screenshots/[platform]/issue_[NNN]_[description].png)
```

---

## Summary

**Every issue needs:**
1. 📍 **Exact location** - File path + line number
2. 📝 **Current code** - What's wrong
3. ✅ **Fix code** - How to solve it
4. 📸 **Screenshot** - Visual evidence with standard name

**Why it matters:**
- Developers know exactly where to fix
- No guesswork or searching
- Faster remediation
- Professional, actionable reports

---

**Related:**
- AUDIT_REPORT_TEMPLATE.md - Full report template
- Platform-specific guides (guides/) - Code patterns by platform
