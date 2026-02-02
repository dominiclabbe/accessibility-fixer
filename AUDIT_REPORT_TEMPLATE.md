# Accessibility Audit Report
## [Platform Name] - [App Name]

> ⚠️ **FILENAME REQUIREMENT:** This report MUST be saved with a descriptive filename:
>
> **Format:** `Accessibility_Audit_[Platform]_[FeatureOrArea]_[Date].md`
>
> **Examples:**
> - `Accessibility_Audit_Android_LoginScreen_2025-10-30.md`
> - `Accessibility_Audit_Web_CheckoutFlow_2025-10-30.md`
> - `Accessibility_Audit_iOS_NavigationBar_2025-10-30.md`
>
> **DO NOT use generic names like:**
> - ❌ `Accessibility_Audit_Web_2025-10-30.md` (missing what was tested)
> - ❌ `report.md`
> - ❌ `audit1.md`

**Date:** [⚠️ USE TODAY'S DATE FROM <env> - Format: YYYY-MM-DD or "Month DD, YYYY"]
**Auditor:** [Name]
**WCAG Version:** 2.2
**Conformance Target:** Level AA
**Platform Version:** [OS/Browser versions tested]

> ⚠️ **IMPORTANT FOR DATE:** Always check the `<env>` section at the start of the conversation for "Today's date" and use that exact date. As of this template update, today is October 29, 2025 (2025-10-29 or "October 29, 2025").

---

## ⚠️ REPORT FORMATTING REQUIREMENTS

**Issue Ordering:**
- **CRITICAL FIRST**: Always list issues by SEVERITY, not by location or discovery order
- Order: Critical → High → Medium → Low
- Within each severity level, order by WCAG SC number or logical grouping

**Content Policy:**
- **ONLY report issues and problems**
- **DO NOT include positive findings** or "good practices observed"
- **DO NOT mention things that are working correctly**
- If something is implemented correctly, don't include it in the report
- Focus exclusively on what needs to be fixed

---

## Executive Summary

**Total Issues Found:** [Number]
- Critical: [Number]
- High: [Number]
- Medium: [Number]
- Low: [Number]

**WCAG Success Criteria Violated:**
- [List of unique SCs violated]

**Overall Assessment:**
[Brief paragraph summarizing accessibility state]

---

## Methodology

**Testing Environment:**
- Device/Browser: [Details]
- OS Version: [Version]
- Assistive Technologies: [TalkBack, VoiceOver, NVDA, etc.]
- Testing Tools: [Scanners, validators used]

**Scope:**
- Screens/Pages audited: [List]
- Code files reviewed: [Number/List]

---

## Issues by Severity

**⚠️ REMEMBER:** List in order: Critical → High → Medium → Low

### Critical Issues

**Count:** [X issues found]

[Examples: Icon-only buttons without labels, completely inaccessible navigation, form inputs without labels, keyboard traps]

#### Issue #001: [Brief Title]

**WCAG SC Violated:**
- **Primary:** [SC X.X.X - Name] (Level X)
- **Secondary:** [SC Y.Y.Y - Name] (Level Y)

**Severity:** Critical
**Impact:** [Who is affected and how]

**Location:** ⚠️ REQUIRED - Must include exact file path and line number
- **File:** `path/to/file.ext` ← Use project-relative path
- **Line:** `123` ← Exact line number where issue occurs
- **Screen:** [Screen name] ← User-facing screen name
- **Component:** [Component name] ← Component/function name

**Description:**
[Detailed description of the issue]

**Current Code:** ⚠️ REQUIRED - Show actual code from the file
```[language]
[Exact code snippet from the file at the line number specified above]
```

**Recommended Fix:** ⚠️ REQUIRED - Show how to fix it
```[language]
[Code snippet showing the solution - copy/pasteable]
```

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Visual Evidence:** ⚠️ Screenshot filename must match the pattern
![Screenshot showing issue](screenshots/[platform]/issue_001_[short_description].png)
<!-- Screenshot filename: issue_001_[short_description].png -->
<!-- Example: issue_001_button_no_label.png -->

**Screen Reader Behavior:**
- **Current:** "[What screen reader announces]"
- **Expected:** "[What it should announce]"

**Resources:**
- [WCAG Understanding doc link]
- [Platform-specific documentation]

---

### High Severity Issues

**Count:** [X issues found]

[Examples: Insufficient color contrast, missing focus indicators, repeated elements without context, collection items not grouped properly]

#### Issue #[number]: [Brief Title]

[Same format as Critical issues above]

---

### Medium Severity Issues

**Count:** [X issues found]

[Examples: Missing heading structure, unclear link purposes, touch targets slightly too small]

#### Issue #[number]: [Brief Title]

[Same format as above]

---

### Low Severity Issues

**Count:** [X issues found]

[Examples: Ambiguous whether image is decorative, minor labeling improvements needed]

#### Issue #[number]: [Brief Title]

[Same format as above]

---

## Issues by WCAG Guideline

### 1. Perceivable

#### 1.1 Text Alternatives

##### 1.1.1 Non-text Content (Level A)

**Issues:** #001, #005, #012

[Brief summary of these issues]

#### 1.3 Adaptable

##### 1.3.1 Info and Relationships (Level A)

**Issues:** #003, #007

[Brief summary]

#### 1.4 Distinguishable

##### 1.4.3 Contrast (Minimum) (Level AA)

**Issues:** #002, #008, #015

[Brief summary]

### 2. Operable

#### 2.1 Keyboard Accessible

##### 2.1.1 Keyboard (Level A)

**Issues:** #004, #010

[Brief summary]

#### 2.4 Navigable

##### 2.4.7 Focus Visible (Level AA)

**Issues:** #014

[Brief summary]

#### 2.5 Input Modalities

##### 2.5.8 Target Size (Minimum) (Level AA)

**Issues:** #017, #018

[Brief summary]

### 3. Understandable

#### 3.3 Input Assistance

##### 3.3.1 Error Identification (Level A)

**Issues:** #019

[Brief summary]

##### 3.3.2 Labels or Instructions (Level A)

**Issues:** #020, #021

[Brief summary]

### 4. Robust

#### 4.1 Compatible

##### 4.1.2 Name, Role, Value (Level A)

**Issues:** #001, #004, #005

[Brief summary]

##### 4.1.3 Status Messages (Level AA)

**Issues:** #022

[Brief summary]

---

## Implementation Strategy

### Phase 1: Critical Fixes (Week 1)
1. [Most impactful critical issue - usually collection item grouping]
2. [Blocking critical issues - buttons without labels, etc.]
3. [Critical navigation/interaction issues]

**Goal:** Make app basically usable with screen reader

### Phase 2: High Priority (Week 2)
1. [High severity issues]
2. [Missing context/labels]
3. [Heading structure]

**Goal:** Improve navigation and content understanding

### Phase 3: Medium & Low (Week 3)
1. [Medium severity improvements]
2. [Low severity polish]
3. [Decorative element cleanup]

**Goal:** Complete accessibility implementation

### Phase 4: Testing & Validation
1. Manual screen reader testing of all fixes
2. Accessibility Inspector audit
3. Automated UI test coverage
4. User testing with assistive technology users (if possible)

**Goal:** Verify all fixes work as intended

---

## Localized Strings Required

⚠️ **Add these to your localization files** (e.g., `Localizable.strings` for iOS, `strings.xml` for Android)

```
[Platform-specific format]

/* Button accessibility labels */
"button_add_to_favorites" = "Add to favorites";
"button_remove_from_favorites" = "Remove from favorites";
"button_play" = "Play";
"button_play_video" = "Play video";

/* Accessibility hints */
"hint_add_to_favorites" = "Adds this item to your favorites";
"hint_view_all_category" = "Double-tap to view all items in this category";

/* Status announcements */
"announcement_item_added" = "Item added to favorites";
"announcement_video_playing" = "Video playing";

/* [Add all strings needed based on issues found] */
```

---

## Automated Testing Examples

### Platform-Specific Test Code

**[Platform] - Example Accessibility Tests:**

```[language]
// Example test code that validates accessibility fixes
// Include specific tests for the issues found

[Provide 2-3 concrete test examples based on issues found]
```

**Test Coverage Recommendations:**
- [ ] Test that collection items are single focusable units
- [ ] Test that all buttons have accessibility labels
- [ ] Test that headings are marked with proper traits
- [ ] Test that decorative images are hidden from assistive tech
- [ ] [Add platform-specific test recommendations]

---

## Recommendations Summary

### High Priority Fixes (Weeks 1-2)
1. [Action item 1 - with specific issue reference]
2. [Action item 2 - with specific issue reference]
3. [Action item 3]

**Impact:** [Describe expected improvement]

### Process Improvements
1. **Code Review Checklist:** Add accessibility checks to PR review process
   - Verify all interactive elements have labels
   - Check collection items are grouped
   - Ensure decorative elements are hidden
2. **CI/CD Integration:** Add accessibility linting to build pipeline
3. **Component Library:** Create accessible base components for reuse

### Training Needs
**Required Training Topics:**
- [Platform] accessibility APIs (labels, traits, grouping)
- Screen reader testing procedures
- WCAG 2.2 Level AA requirements
- Collection item accessibility patterns
- [Specific topics based on issues found]

**Recommended Resources:**
- [Platform-specific accessibility documentation]
- [WCAG Understanding documents]
- Internal accessibility guidelines

---

## Appendix

### A. Testing Checklist Used
- [ ] All images have text alternatives or marked decorative
- [ ] All buttons have accessible labels
- [ ] Color contrast meets minimum ratios
- [ ] Keyboard/gesture navigation is functional
- [ ] Screen reader announces content correctly
- [ ] Touch targets meet minimum size requirements
- [ ] Form inputs have persistent labels
- [ ] Dynamic content updates are announced
- [ ] Headings structure is logical and marked
- [ ] Focus management is proper
- [ ] Collection items grouped as single units
- [ ] Repeated elements have contextual labels
- [ ] Text scales with system settings

### B. Automated Scan Results
[Summary or attachment of automated tool results]

**Tools Used:**
- [List tools used: Accessibility Scanner, axe, Lighthouse, etc.]
- [Include summary of automated findings]

### C. Platform-Specific Requirements Met
- [ ] [Platform requirement 1]
- [ ] [Platform requirement 2]
- [ ] Dynamic Type/Font scaling supported (iOS/Android)
- [ ] Proper semantic roles assigned
- [ ] Live regions configured for announcements
- [ ] Custom actions provided for gesture-only features

### D. Files Audited

**Full list of files reviewed:**
- [List all files examined during audit]
- [Group by feature/component area]

**Components Examined:**
- [List all custom components checked]
- [Include third-party libraries if applicable]

---

## Sign-off

**Auditor:** [Name]
**Date:** [Date]
**Next Review Date:** [Recommended date]

**Notes:** [Any additional context, limitations of audit, or follow-up items]
