# How to Start an Accessibility Audit
## Practical Guide for Using Claude Code

---

## Setup: Preparing Your Project

### 1. Create Output Directories

Run the setup script in your project:

```bash
cd your-project
/path/to/accessibility-fixer/setup-audit.sh
```

This creates:
```
your-project/
└── accessibility-audit/
    ├── reports/      (audit reports saved here)
    └── screenshots/  (screenshots saved here)
```

**Note:** Platform folders (web/, android/, ios/, etc.) are created automatically when you generate your first report.

### 2. Identify Your Platforms

First, determine which platforms your project uses:

**Example Prompt:**
```
I need to audit this project for accessibility issues. Can you analyze the project structure and tell me which platforms are present (web, Android, iOS, React Native, Flutter, etc.)?
```

---

## Starting the Audit: Platform-by-Platform Approach

### Recommended Workflow

**Audit ONE platform at a time** to maintain focus and clarity. Complete each platform's report before moving to the next.

---

## Prompt Templates by Platform

### For Web Platform

```
I want to perform a WCAG 2.2 Level AA accessibility audit on the web portion of this application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

Start by:
1. Identifying all web components and pages
2. Analyzing the code for common accessibility issues:
   - Missing alt text on images
   - Buttons/links without proper labels
   - Form inputs without labels
   - Color contrast issues
   - Keyboard accessibility problems
   - ARIA usage and semantic HTML
   - Focus management

3. Create a detailed audit report at:
   accessibility-audit/reports/web/Accessibility_Audit_Web_[FeatureOrArea]_[YYYY-MM-DD].md

   Examples:
   - Accessibility_Audit_Web_LoginPage_2025-10-30.md
   - Accessibility_Audit_Web_CheckoutFlow_2025-10-30.md
   - Accessibility_Audit_Web_Dashboard_2025-10-30.md

Document each issue with:
- WCAG SC violations
- File path and line number
- Current code snippet
- Recommended fix
- Severity level
- Note where screenshots should be placed (I'll capture them separately)

Focus on: [Specific pages/components - e.g., "Login and Registration", "Checkout Flow", "Dashboard"]
```

### For Android Platform

```
I want to perform a WCAG 2.2 Level AA accessibility audit on the Android portion of this application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

Start by:
1. Identifying all Android layouts, Composables, Activities, and Fragments
2. Analyzing the code for Android accessibility issues:
   - Missing contentDescription on ImageView/ImageButton/Icon
   - Touch target sizes (minimum 48dp)
   - Missing labels on EditText fields
   - Custom views without accessibility support
   - TalkBack compatibility issues
   - Heading structure using accessibility semantics
   - Live regions for dynamic content

3. Create a detailed audit report at:
   accessibility-audit/reports/android/Accessibility_Audit_Android_[FeatureOrArea]_[YYYY-MM-DD].md

   Examples:
   - Accessibility_Audit_Android_LoginScreen_2025-10-30.md
   - Accessibility_Audit_Android_HomeScreen_2025-10-30.md
   - Accessibility_Audit_Android_SettingsScreen_2025-10-30.md

Document each issue with:
- WCAG SC violations
- File path and line number
- Current code snippet
- Recommended fix with proper Android APIs
- Severity level
- Note where screenshots should be placed

Focus on: [Specific screens/features if needed, or "the entire application"]
```

### For iOS Platform

```
I want to perform a WCAG 2.2 Level AA accessibility audit on the iOS portion of this application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

Start by:
1. Identifying all View Controllers, SwiftUI Views, and custom UI components
2. Analyzing the code for iOS accessibility issues:
   - Missing accessibilityLabel on images and custom controls
   - Missing or incorrect accessibilityTraits
   - Accessibility element grouping issues
   - VoiceOver navigation problems
   - Dynamic Type support
   - Custom accessibility actions for gesture-based features
   - Focus management and announcements

3. Create a detailed audit report at:
   accessibility-audit/reports/ios/Accessibility_Audit_iOS_[FeatureOrArea]_[YYYY-MM-DD].md

   Examples:
   - Accessibility_Audit_iOS_LoginScreen_2025-10-30.md
   - Accessibility_Audit_iOS_ProfileView_2025-10-30.md
   - Accessibility_Audit_iOS_NavigationBar_2025-10-30.md

Document each issue with:
- WCAG SC violations
- File path and line number
- Current code snippet (UIKit or SwiftUI)
- Recommended fix with proper iOS accessibility APIs
- Severity level
- Note where screenshots should be placed

Focus on: [Specific screens/features if needed, or "the entire application"]
```

### For React Native Platform

```
I want to perform a WCAG 2.2 Level AA accessibility audit on this React Native application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

Start by:
1. Identifying all components and screens
2. Analyzing the code for React Native accessibility issues:
   - Missing accessibilityLabel on Image, TouchableOpacity, etc.
   - Missing accessibilityRole on interactive elements
   - accessibilityState for toggles and selected states
   - Form inputs without proper labels
   - Touch target sizes
   - Screen reader compatibility (both TalkBack and VoiceOver)
   - Platform-specific accessibility props

3. Create a detailed audit report at:
   accessibility-audit/reports/react-native/Accessibility_Audit_ReactNative_[FeatureOrArea]_[YYYY-MM-DD].md

   Examples:
   - Accessibility_Audit_ReactNative_HomeScreen_2025-10-30.md
   - Accessibility_Audit_ReactNative_CheckoutFlow_2025-10-30.md

Document each issue with:
- WCAG SC violations
- File path and line number
- Current code snippet
- Recommended fix
- Severity level
- Note where screenshots should be placed

Focus on: [Specific screens/features if needed, or "the entire application"]
```

### For Android TV Platform

```
I want to perform a WCAG 2.2 Level AA accessibility audit on the Android TV portion of this application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

Start by:
1. Identifying all Android TV layouts and Composables
2. Analyzing the code for Android TV specific accessibility issues:
   - D-pad navigation configuration
   - Focus management and focusability
   - TalkBack support for TV
   - Touch target sizes (larger for 10-foot UI)
   - Content descriptions for all interactive elements
   - Focus order and navigation flow

3. Create a detailed audit report at:
   accessibility-audit/reports/android-tv/Accessibility_Audit_AndroidTV_[FeatureOrArea]_[YYYY-MM-DD].md

   Examples:
   - Accessibility_Audit_AndroidTV_HomeScreen_2025-10-30.md
   - Accessibility_Audit_AndroidTV_VideoPlayer_2025-10-30.md

Document each issue with:
- WCAG SC violations
- File path and line number
- Current code snippet
- Recommended fix for TV interface
- Severity level
- Note where screenshots should be placed

Focus on: [Specific screens/features if needed, or "the entire application"]
```

### For tvOS Platform

```
I want to perform a WCAG 2.2 Level AA accessibility audit on the tvOS portion of this application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

Start by:
1. Identifying all tvOS View Controllers and SwiftUI Views
2. Analyzing the code for tvOS specific accessibility issues:
   - Focus engine configuration
   - VoiceOver support for TV
   - Accessibility labels for all focusable elements
   - Remote control navigation
   - Focus guides for complex layouts
   - Accessibility traits appropriate for TV interface

3. Create a detailed audit report at:
   accessibility-audit/reports/tvos/Accessibility_Audit_tvOS_[FeatureOrArea]_[YYYY-MM-DD].md

   Examples:
   - Accessibility_Audit_tvOS_HomeScreen_2025-10-30.md
   - Accessibility_Audit_tvOS_VideoPlayer_2025-10-30.md

Document each issue with:
- WCAG SC violations
- File path and line number
- Current code snippet
- Recommended fix for tvOS
- Severity level
- Note where screenshots should be placed

Focus on: [Specific screens/features if needed, or "the entire application"]
```

---

## Multi-Platform Project: Full Audit

If you want to audit all platforms at once:

```
I want to perform a comprehensive WCAG 2.2 Level AA accessibility audit on this multi-platform application.

Please follow the ACCESSIBILITY_AUDIT_GUIDE.md located in the accessibility-audit/ directory.

This project contains: [list platforms: web, Android, iOS, etc.]

Please audit each platform separately and create individual reports:
- accessibility-audit/reports/web/Accessibility_Audit_Web_[FeatureOrArea]_[YYYY-MM-DD].md
- accessibility-audit/reports/android/Accessibility_Audit_Android_[FeatureOrArea]_[YYYY-MM-DD].md
- accessibility-audit/reports/ios/Accessibility_Audit_iOS_[FeatureOrArea]_[YYYY-MM-DD].md

Examples:
- Accessibility_Audit_Web_LoginPage_2025-10-30.md
- Accessibility_Audit_Android_HomeScreen_2025-10-30.md
- Accessibility_Audit_iOS_ProfileView_2025-10-30.md

For each platform:
1. Identify relevant source files
2. Analyze code for platform-specific accessibility issues (see guide)
3. Document issues with WCAG SC, file locations, code snippets, and fixes
4. Organize by severity and WCAG guideline
5. Note where screenshots should be placed

Start with [platform name] first, then move to the next platform after completion.
```

---

## During the Audit: Interactive Prompts

### When You Need More Detail

```
Can you provide more specific code examples for issue #5 showing both the current problematic code and the recommended fix?
```

### When You Want to Focus on Specific Issues

```
Focus the audit on form accessibility issues - labels, error handling, and input descriptions.
```

```
Analyze just the color contrast issues throughout the [platform] codebase.
```

### When You Need Platform-Specific Guidance

```
For issue #3, what is the Android-specific API I should use to fix this TalkBack issue?
```

### When You Want to Add Issues

```
I found another issue manually. Can you add this to the report:
- Location: src/components/Header.tsx line 45
- Issue: The menu button has no accessible label
- Screenshot: screenshots/web/issue_015_menu_no_label.png
```

---

## After Code Analysis: Adding Screenshots

Claude Code analyzes the source code but cannot capture screenshots from running apps. You'll need to:

### 1. Run Your Application

Use the appropriate emulator/simulator/browser:
- **Web:** Browser DevTools (F12), take screenshots
- **Android:** Android Emulator + TalkBack
- **iOS:** Simulator + VoiceOver (Cmd+F5)

### 2. Capture Screenshots

For each issue in the report:
- Take a screenshot showing the problematic UI element
- Highlight the issue if needed (red box/arrow)
- For screen reader issues, capture the screen reader output

### 3. Name and Save Screenshots

Follow the naming convention from the report:
```bash
accessibility-audit/screenshots/web/issue_001_button_no_label.png
accessibility-audit/screenshots/android/issue_003_low_contrast.png
```

### 4. Update Report with Screenshot Paths

The report will have placeholders like:
```markdown
**Visual Evidence:**
![Screenshot showing issue](screenshots/web/issue_001_button_no_label.png)
```

Verify these paths match your actual screenshots.

---

## Reviewing and Finalizing Reports

### Quality Check Prompt

```
Please review the audit report at accessibility-audit/reports/[platform]/[filename].md and verify:
1. All issues have WCAG SC references
2. File paths and line numbers are accurate
3. Code snippets are correct
4. Severity levels are appropriate
5. The executive summary matches the issue count
6. Issues are properly grouped by WCAG guideline
```

### Generate Executive Summary Across All Platforms

```
I've completed audits for all platforms. Can you create a master executive summary document at:

accessibility-audit/reports/MASTER_SUMMARY.md

That includes:
- Total issues across all platforms
- Issues by platform breakdown
- Most common WCAG violations
- High priority fixes that affect multiple platforms
- Overall accessibility score/assessment
```

---

## Example: Complete Audit Session

Here's a full example workflow:

### Step 1: Initial Setup
```bash
cd /path/to/your-project
mkdir -p accessibility-audit/{reports,screenshots}/{web,android,ios}
```

### Step 2: Start with Claude Code
```
I want to audit this React web application for accessibility.

Follow the ACCESSIBILITY_AUDIT_GUIDE.md framework.

Create a report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_2025-01-15.md

Analyze all components in src/components/ and src/pages/ for:
- Missing alt text
- Unlabeled buttons
- Form accessibility
- Keyboard navigation
- Color contrast issues
- ARIA usage

Document each issue with WCAG SC, file location, code snippets, and fixes.
```

### Step 3: Review Progress
As Claude analyzes, you'll see issues being documented. You can:
- Ask for clarification on specific issues
- Request more examples
- Focus on certain areas

### Step 4: Capture Screenshots
- Run your app
- Navigate to each issue location
- Capture screenshots
- Save to `accessibility-audit/screenshots/web/`

### Step 5: Next Platform
```
Great work on the web audit. Now let's audit the iOS app.

Create a report at:
accessibility-audit/reports/ios/Accessibility_Audit_iOS_2025-01-15.md

Follow the same process for iOS-specific issues.
```

### Step 6: Final Summary
```
Create a master summary at:
accessibility-audit/reports/MASTER_SUMMARY.md

Include cross-platform analysis and prioritized fix recommendations.
```

---

## Where Reports Are Saved

All reports are saved in your project directory:

```
your-project/
├── accessibility-audit/
│   ├── reports/
│   │   ├── web/
│   │   │   └── Accessibility_Audit_Web_2025-01-15.md
│   │   ├── android/
│   │   │   └── Accessibility_Audit_Android_2025-01-15.md
│   │   ├── ios/
│   │   │   └── Accessibility_Audit_iOS_2025-01-15.md
│   │   └── MASTER_SUMMARY.md
│   ├── screenshots/
│   │   ├── web/
│   │   │   ├── issue_001_button_no_label.png
│   │   │   └── issue_002_low_contrast.png
│   │   ├── android/
│   │   │   └── issue_001_missing_content_desc.png
│   │   └── ios/
│   │       └── issue_001_missing_label.png
│   └── ACCESSIBILITY_AUDIT_GUIDE.md
```

You can then:
- **Version control:** Commit reports to git for tracking progress
- **Share with team:** Send the reports folder
- **Deliver to clients:** Package reports + screenshots as a deliverable
- **Track fixes:** Reference file paths and line numbers when implementing fixes

---

## Tips for Effective Audits

### 1. Start Small
If the project is large, audit one feature area or critical user flow first:
```
Audit the checkout flow for accessibility issues (web platform only).
```

### 2. Prioritize Critical Paths
Focus on the most important user journeys:
```
Focus on authentication, main navigation, and primary content consumption screens.
```

### 3. Iterative Approach
You can refine the audit:
```
Review the issues marked as "Critical" and provide more detailed fix instructions with code examples.
```

### 4. Get Automated Help First
```
What automated tools should I run before starting this audit? (e.g., axe, Accessibility Scanner)
```

Then supplement with Claude's code analysis for deeper issues.

### 5. Test as You Go
Don't wait until the end to test. As issues are found:
- Try to reproduce them in the running app
- Verify the issue exists
- Capture screenshot immediately

---

## Troubleshooting

### "The project is too large"
```
Let's audit in phases. Start with the src/components/forms/ directory only.
```

### "I need more context for an issue"
```
For issue #7, can you show me how this component is used elsewhere in the app? Search for usages of `CustomButton`.
```

### "The code has changed since the audit"
```
Issue #3 in the report references src/Login.tsx line 45, but that code has been modified. Can you re-audit that specific component and update the issue?
```

### "I want to focus on one WCAG guideline"
```
Audit only for WCAG 2.1.1 Keyboard accessibility issues across the web platform.
```

---

## Ready to Start?

Use the `/audit` command in Claude Code, or customize one of the prompt templates above and paste it into Claude Code. The audit report will be created in your accessibility-audit/reports/ directory, and you can capture screenshots as you test the application!
