# Accessibility Audit

You are performing a COMPREHENSIVE accessibility audit on a codebase.

## Guidelines Location
The accessibility guidelines are located in the accessibility-fixer repository

## Before Starting - Essential Reading

1. **FIRST: Load the comprehensive workflow guide:**
   - `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` - Systematic audit process (READ THIS FIRST)

2. **Load these key reference files:**
   - `guides/GUIDE_WCAG_REFERENCE.md` - Main WCAG reference
   - `guides/wcag/QUICK_LOOKUP.md` - Quick reference tables
   - `guides/wcag/COMPONENT_WCAG_MAPPINGS.md` - Component mappings
   - `guides/wcag/SEVERITY_GUIDELINES.md` - Severity rules
   - `guides/wcag/TESTING_CHECKLIST.md` - Testing checklist (includes Comprehensive Component Examination section)

3. **Ask user which platform(s) to audit:**
   - Android
   - iOS
   - Web
   - React Native
   - Flutter
   - Android TV
   - tvOS

4. **Based on platform, load the appropriate platform guide:**
   - `guides/GUIDE_ANDROID.md`
   - `guides/GUIDE_IOS.md` (includes Systematic Audit Workflow section)
   - `guides/GUIDE_WEB.md`
   - `guides/GUIDE_REACT_NATIVE.md`
   - `guides/GUIDE_FLUTTER.md`
   - `guides/GUIDE_ANDROID_TV.md`
   - `guides/GUIDE_TVOS.md`

5. **Load pattern guides as needed during audit:**
   - `guides/patterns/COLLECTION_ITEMS_PATTERN.md`
   - `guides/patterns/FONT_SCALING_SUPPORT.md`
   - `guides/patterns/DECORATIVE_IMAGE_DECISION_TREE.md`
   - `guides/patterns/AVOID_ROLE_IN_LABEL.md`
   - `guides/patterns/BUTTONS_ACTING_AS_TABS.md`
   - `guides/patterns/REPEATED_ELEMENTS_CONTEXT.md`
   - `guides/patterns/NAVIGATION_BAR_ACCESSIBILITY.md`

## Comprehensive Audit Workflow (4 Phases)

Follow the systematic process from COMPREHENSIVE_AUDIT_WORKFLOW.md:

### Phase 1: Discovery (30-60 min)
1. Navigate with screen reader (if possible)
2. Quick code scan for accessibility properties
3. Identify ALL custom components (buttons, views, cells)
4. Create component checklist
5. **Use TodoWrite** to track audit tasks

### Phase 2: Deep Dive (2-4 hours)
1. **Examine EVERY custom component file**
   - Find all custom button classes (FavoriteButton, PlayButton, MoreInfoButton, etc.)
   - Find all custom view classes
   - Find all cell/tile classes
2. **For EACH component:**
   - Read entire file
   - Check accessibility properties
   - Find ALL usages in codebase
   - Document EVERY issue with file path + line number
3. **Systematically check each component type** using COMPONENT_WCAG_MAPPINGS.md
4. **Follow the testing checklist** - especially "Comprehensive Component Examination" section

### Phase 3: Pattern Verification (1-2 hours)
1. **For each issue found, search for ALL instances:**
   - Don't stop at first occurrence
   - Use grep/search to find pattern everywhere
   - Document ALL locations
2. **Check all variants:**
   - Portrait AND Landscape tiles
   - Small AND Large variants
   - Different states (disabled, selected, error)
3. **Cross-reference pattern guides** for complex patterns

### Phase 4: Report Generation (2-3 hours)
1. **Use ENHANCED template**: `AUDIT_REPORT_TEMPLATE.md`
2. **Order by severity**: Critical → High → Medium → Low (NOT by location)
3. **Include ALL new required sections:**
   - Implementation Strategy (phased 4-week plan)
   - Localized Strings Required (complete list)
   - Automated Testing Examples (sample test code)
   - Files Audited (complete list of all files reviewed)
   - Components Examined (list of all custom components checked)
4. **Assign severity consistently** using SEVERITY_GUIDELINES.md

## Critical Requirements for Comprehensive Audits

⚠️ **GOLDEN RULES:**
1. **Check ALL instances** - Don't stop at first occurrence of an issue
2. **Examine ALL components** - List and check every custom component file
3. **Document everything** - File path + line number for EVERY issue
4. **Provide implementation plan** - Phased strategy, strings list, test examples

⚠️ **Report Requirements:**
- **NEVER include positive findings** - only report issues
- **Order by severity** - Critical → High → Medium → Low (NOT by location)
- **Include file paths and line numbers** - for ALL issues
- **Document ALL instances** - If you find 5 play buttons with issues, document all 5 separately
- **Use pattern guides** - for complex patterns (collections, tabs, etc.)
- **Test with screen reader** - when possible, don't just review code
- **Be specific** - vague findings are not helpful

⚠️ **Common Mistakes to Avoid:**
- ❌ Stopping at first instance (find ALL occurrences)
- ❌ Skipping custom components (check FavoriteButton.swift, MoreInfoButton.swift, etc.)
- ❌ Missing variants (check Portrait AND Landscape tiles)
- ❌ No implementation plan (use enhanced template)
- ❌ Ordering by location (always order by severity)

## Report Generation - ENHANCED TEMPLATE

1. **Save report to audited project**: `./accessibility-audit/reports/[platform]/`
   - ⚠️ IMPORTANT: Save in the PROJECT being audited, NOT in accessibilityFixer folder
2. **Use ENHANCED template**: Load `AUDIT_REPORT_TEMPLATE.md`
3. **Filename format**: `Accessibility_Audit_[Platform]_[Feature]_YYYY-MM-DD.md`
4. **Order by severity**: Critical → High → Medium → Low

5. **Include for EACH issue:**
   - File path and line number (REQUIRED)
   - WCAG SC violated (with level)
   - Severity with rationale
   - Description of problem
   - User impact explanation
   - ALL instances found (list each file:line)
   - Current code example
   - Corrected code example
   - Screen reader behavior (current vs expected)
   - Link to pattern guide if applicable

6. **Include NEW required sections:**
   - ✅ **Implementation Strategy** - Phased 4-week rollout plan
   - ✅ **Localized Strings Required** - Complete list of strings needed
   - ✅ **Automated Testing Examples** - Platform-specific test code
   - ✅ **Files Audited** - Complete list of files examined
   - ✅ **Components Examined** - List of custom components checked

## Start - Interactive Discovery

When the user types `/audit`, help them specify what to audit through interactive discovery:

### Step 1: Detect Platforms

Quickly scan the project to detect platforms:

**iOS Detection:**
```bash
# Look for: *.swift, *.xcodeproj, SwiftUI, UIKit
# Common paths: Sources/, App/, Views/, ViewControllers/
```

**Android Detection:**
```bash
# Look for: *.kt, *.java, build.gradle, AndroidManifest.xml
# Common paths: app/src/main/, java/, kotlin/
```

**Web Detection:**
```bash
# Look for: *.jsx, *.tsx, *.vue, *.html, package.json
# Common paths: src/, components/, pages/
```

**React Native Detection:**
```bash
# Look for: *.jsx, *.tsx with react-native imports
```

**Flutter Detection:**
```bash
# Look for: *.dart, pubspec.yaml
```

Present findings as numbered choices:
```
I've detected the following platforms in this project:

1. iOS (Swift) - 145 .swift files found
2. Android (Kotlin) - 89 .kt files found
3. Web (React) - 67 .tsx files found

Which platform would you like to audit?
```

If user has already specified platform in their message, skip this step.

### Step 2: Detect Major Sections/Features

Based on selected platform, scan for major sections:

**For iOS:**
```bash
# Look for:
# - ViewControllers: HomeViewController, SettingsViewController, etc.
# - SwiftUI Views: HomeView, ProfileView, etc.
# - Storyboards: Main.storyboard, Settings.storyboard
# - Key directories: Home/, Settings/, Profile/, etc.
```

**For Android:**
```bash
# Look for:
# - Activities: MainActivity, SettingsActivity, etc.
# - Fragments: HomeFragment, ProfileFragment, etc.
# - Composables: @Composable functions
# - Key directories: home/, settings/, profile/, etc.
```

**For Web:**
```bash
# Look for:
# - Pages: HomePage, LoginPage, DashboardPage, etc.
# - Major components: Header, Navigation, Footer, etc.
# - Routes in routing files
# - Key directories: pages/, views/, features/
```

Present findings as numbered choices:
```
I've found these major sections in the iOS app:

Screens/Features:
1. Home Screen (HomeViewController.swift, HomeView.swift)
2. Settings (SettingsViewController.swift + 8 related files)
3. Profile/User (ProfileView.swift, UserDetailsView.swift)
4. Video Player (VideoPlayerViewController.swift + controls)
5. Search/Browse (SearchView.swift, BrowseView.swift)

Components:
6. Navigation Bar (CustomNavigationBar.swift)
7. Tab Bar (CustomTabBar.swift)
8. Collection/Grid Items (ChannelCell.swift, VideoTile.swift, etc.)
9. Custom Buttons (FavoriteButton.swift, PlayButton.swift, etc.)
10. Forms/Input (all form components)

What would you like to audit? (Enter number or describe)
```

If user has already specified feature/screen, skip this step.

### Step 3: Confirm Scope

Summarize what will be audited:
```
Perfect! I'll audit:

Platform: iOS
Focus: Home Screen
Files: HomeViewController.swift, HomeView.swift, related components

This is a focused audit. I will:
✓ Check ALL custom components used in Home Screen
✓ Find ALL instances of each issue
✓ Generate comprehensive report with fixes
✓ Include implementation strategy

Estimated time: 6-10 hours for thorough audit

Proceed? (yes/no)
```

### Step 4: Begin Audit

Once confirmed:
1. Load COMPREHENSIVE_AUDIT_WORKFLOW.md
2. Load appropriate platform guide
3. Load reference guides
4. Begin Phase 1: Discovery (create component checklist)
5. Use TodoWrite to track all audit phases
6. Follow the systematic 4-phase process
7. Generate comprehensive report with ALL required sections

### Special Cases

**If in accessibilityFixer repo:**
```
⚠️ You're currently in the accessibilityFixer guidelines repository.

This contains the audit framework itself, not an app to audit.

Please navigate to your actual app project first:
cd /path/to/your-app

Then run /audit again.
```

**If user provided detailed request:**
```
User: /audit the iOS home screen for accessibility issues

[Skip discovery, go directly to confirmation:]

I'll audit the iOS home screen for accessibility issues.
Let me start by loading the guidelines...
```

**If no platforms detected:**
```
I couldn't detect any common platforms in this project.

Please specify:
1. Which platform? (iOS, Android, Web, React Native, Flutter)
2. Which files/directories should I examine?
```

---

## After Interactive Discovery

Once platform and feature are determined, proceed with the standard audit workflow as documented above.
