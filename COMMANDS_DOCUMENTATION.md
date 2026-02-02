# Slash Commands Documentation
## accessibility-fixer Framework

---

## Available Commands

### `/audit` - Comprehensive Accessibility Audit

**Location:** `.claude/commands/audit.md`

**Purpose:** Triggers a comprehensive, systematic accessibility audit following best practices learned from comparing multiple audit reports.

**Usage:**
```
/audit
```

**What it does:**
1. Loads all essential accessibility guidelines
2. Asks which platform to audit (iOS, Android, Web, etc.)
3. Loads platform-specific patterns and best practices
4. Follows a systematic 4-phase audit process
5. Generates a comprehensive report with implementation strategy

---

### `/pr-review` - Automated PR Accessibility Review

**Location:** `.claude/commands/pr-review.md`

**Purpose:** Provides automated accessibility review for GitHub Pull Requests. Analyzes only changed files and posts feedback directly as PR comments. Designed for CI/CD integration.

**Usage:**
```
/pr-review              # Auto-detect current branch PR
/pr-review 123          # Review specific PR number
/pr-review --no-post    # Dry-run without posting comments
```

**What it does:**
1. Fetches PR information using GitHub CLI (`gh`)
2. Analyzes only changed files in the PR
3. Detects platform(s) from file extensions
4. Checks for accessibility issues in changed code
5. Posts inline comments on specific issues
6. Posts summary comment with all findings
7. Generates optional report file

**Key Features:**
- ⚡ **Fast**: 30-60 minutes (vs 6-10 hours for full audit)
- 🎯 **Focused**: Only changed files (not entire codebase)
- 💬 **Interactive**: Posts comments directly on PR
- 🤖 **CI-Ready**: Automated mode for pipelines
- 🚦 **Gate Merges**: Exit codes to block/warn based on severity

**Exit Codes (CI):**
- `0` = No critical issues found (pass)
- `1` = Critical issues found (block merge)
- `2` = High priority issues (warning, don't block)

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Permissions in `.claude/settings.local.json`:
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

**Documentation:**
- Quick Start: [PR_REVIEW_QUICK_START.md](PR_REVIEW_QUICK_START.md)
- Full Guide: [PR_REVIEW_GUIDE.md](PR_REVIEW_GUIDE.md)
- CI Examples: See `ci-examples/` directory

---

### `/fix-accessibility` - Apply Fixes from Audit Reports

**Location:** `.claude/commands/fix-accessibility.md`

**Purpose:** Applies fixes from accessibility audit reports automatically.

**Usage:**
```
/fix-accessibility
```

**What it does:**
1. Lists available audit reports
2. Parses issues by severity
3. Applies fixes to source files
4. Generates fix summary report

---

## /audit Command Details

### Workflow Overview

The `/audit` command follows a **4-phase systematic process** designed to ensure comprehensive coverage:

#### Phase 1: Discovery (30-60 min)
- Navigate with screen reader (if possible)
- Quick code scan for accessibility properties
- Identify ALL custom components
- Create component checklist
- Use TodoWrite to track tasks

#### Phase 2: Deep Dive (2-4 hours)
- Examine EVERY custom component file
- Find all custom button, view, and cell classes
- For EACH component:
  - Read entire file
  - Check accessibility properties
  - Find ALL usages in codebase
  - Document EVERY issue with file path + line number

#### Phase 3: Pattern Verification (1-2 hours)
- For each issue found, search for ALL instances
- Don't stop at first occurrence
- Check all variants (Portrait, Landscape, etc.)
- Cross-reference pattern guides

#### Phase 4: Report Generation (2-3 hours)
- Use enhanced AUDIT_REPORT_TEMPLATE.md
- Order by severity (Critical → High → Medium → Low)
- Include ALL required sections:
  - Implementation Strategy
  - Localized Strings Required
  - Automated Testing Examples
  - Files Audited
  - Components Examined

**Total Time:** 6-10 hours for comprehensive home screen audit

---

## Key Features

### Exhaustive Coverage
✅ Checks ALL custom components (not just screens)
✅ Finds ALL instances of each issue (not just first one)
✅ Examines ALL variants (Portrait, Landscape, Large, Small)
✅ Documents ALL locations with file paths + line numbers

### Component-Level Examination
✅ Systematically checks every custom button class
✅ Reviews every custom view component
✅ Examines all collection item implementations
✅ Verifies base classes and inheritance

### Enhanced Reporting
✅ Implementation Strategy (phased 4-week plan)
✅ Localized Strings Required (complete list)
✅ Automated Testing Examples (sample test code)
✅ Files Audited (complete list of files examined)
✅ Components Examined (what was checked)

---

## Guidelines Loaded by /audit

### Essential Workflow Guide
- `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` - Systematic process (LOADED FIRST)

### Core References
- `guides/GUIDE_WCAG_REFERENCE.md` - WCAG 2.2 reference
- `guides/wcag/QUICK_LOOKUP.md` - Quick reference tables
- `guides/wcag/COMPONENT_WCAG_MAPPINGS.md` - Component-to-WCAG mappings
- `guides/wcag/SEVERITY_GUIDELINES.md` - How to assign severity
- `guides/wcag/TESTING_CHECKLIST.md` - Comprehensive examination checklist

### Platform-Specific Guides
Based on your platform choice, loads one of:
- `guides/GUIDE_ANDROID.md`
- `guides/GUIDE_IOS.md` (includes Systematic Audit Workflow)
- `guides/GUIDE_WEB.md`
- `guides/GUIDE_REACT_NATIVE.md`
- `guides/GUIDE_FLUTTER.md`
- `guides/GUIDE_ANDROID_TV.md`
- `guides/GUIDE_TVOS.md`

### Pattern Guides (as needed)
- `guides/patterns/COLLECTION_ITEMS_PATTERN.md`
- `guides/patterns/FONT_SCALING_SUPPORT.md`
- `guides/patterns/DECORATIVE_IMAGE_DECISION_TREE.md`
- `guides/patterns/AVOID_ROLE_IN_LABEL.md`
- `guides/patterns/BUTTONS_ACTING_AS_TABS.md`
- `guides/patterns/REPEATED_ELEMENTS_CONTEXT.md`
- `guides/patterns/NAVIGATION_BAR_ACCESSIBILITY.md`

---

## Golden Rules Enforced by /audit

### 1. Check ALL Instances
❌ Don't stop at finding one play button without label
✅ Search for ALL play buttons and document each one

### 2. Examine ALL Components
❌ Don't just check screens
✅ Find and check every custom button, view, and cell class

### 3. Document Everything
❌ Don't write "play buttons need labels"
✅ Write:
- `PlayButton.swift:36` - play button in poster
- `PromotionalBannerView.swift:20` - play button in banner
- `VideoPlayerControls.swift:45` - play button in controls

### 4. Provide Implementation Plan
❌ Don't just list issues
✅ Include:
- Phased 4-week implementation strategy
- Complete localized strings list
- Automated test examples
- Files audited list

---

## Report Location

**IMPORTANT:** Reports are saved to the **audited project**, NOT to the accessibility-fixer folder.

**Save location:**
```
[project-being-audited]/accessibility-audit/reports/[platform]/
```

**Example:**
```
/Users/you/dev/my-app/accessibility-audit/reports/ios/
Accessibility_Audit_iOS_HomeScreen_2025-12-22.md
```

---

## Common Mistakes Avoided

The `/audit` command specifically prevents these common mistakes:

❌ **Stopping at First Instance**
- Problem: Found one channel logo issue, missed 3 others
- Solution: Searches entire codebase for pattern

❌ **Skipping Custom Components**
- Problem: Didn't check FavoriteButton.swift file
- Solution: Lists ALL custom components first

❌ **Missing Variants**
- Problem: Checked PortraitTile, forgot LandscapeTile
- Solution: Uses glob patterns to find ALL variants

❌ **No Implementation Plan**
- Problem: Just listed issues, developers don't know where to start
- Solution: Includes phased strategy and strings list

❌ **Ordering by Location**
- Problem: Issues grouped by file
- Solution: Always orders by severity

---

## Example Session

```
You: /audit

Claude: I'm ready to perform a comprehensive accessibility audit.

Which platform would you like to audit?
- Android
- iOS
- Web
- React Native
- Flutter
- Android TV
- tvOS

You: iOS, focusing on the home screen

Claude: [Loads COMPREHENSIVE_AUDIT_WORKFLOW.md]
        [Loads GUIDE_IOS.md with Systematic Audit Workflow]
        [Loads reference guides]

        Great! I'll audit the iOS home screen comprehensively.

        Let me start by exploring the project structure...
        [Creates TodoList with 8 tasks]
        [Phase 1: Discovery - 30 min]
        [Phase 2: Deep Dive - 3 hours, checks ALL components]
        [Phase 3: Verification - 1 hour, finds ALL instances]
        [Phase 4: Report - 2 hours]

        Report created at:
        /path/to/your-project/accessibility-audit/reports/ios/
        Accessibility_Audit_iOS_HomeScreen_2025-12-22.md

        Found 24 issues:
        - Critical: 5
        - High: 10
        - Medium: 7
        - Low: 2

        Report includes:
        ✅ Implementation Strategy (4-week plan)
        ✅ Localized Strings list (23 strings needed)
        ✅ Test Examples (iOS XCTest code)
        ✅ Files Audited (15 files examined)
        ✅ Components Examined (12 custom components)
```

---

## Comparison to Quick Audits

| Feature | Quick Audit | /audit Command |
|---------|------------|----------------|
| **Time** | 3-5 hours | 6-10 hours |
| **Component Coverage** | Screens only | ALL custom components |
| **Instance Documentation** | First found | ALL found |
| **Implementation Plan** | No | Yes (4-week phased) |
| **Strings List** | No | Yes (complete) |
| **Test Examples** | No | Yes (platform-specific) |
| **Files Audited List** | No | Yes |
| **Thoroughness** | Partial | Complete |
| **Result** | May miss issues | Comprehensive coverage |

---

## For Auditors

**Before using `/audit`, read these guides:**

1. **Essential (5 min):**
   - `AUDITOR_QUICK_START.md` - Quick reference card

2. **Important (20 min):**
   - `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` - Full process

3. **Context (10 min):**
   - `AUDIT_IMPROVEMENTS_SUMMARY.md` - Why thoroughness matters

**These guides will help you:**
- Understand the systematic process
- Know what to search for
- Document issues properly
- Generate complete reports

---

## Modifying the Command

The `/audit` command is defined in:
```
.claude/commands/audit.md
```

You can customize:
- Which guides are loaded
- The workflow phases
- Required report sections
- Golden rules and reminders

**Note:** The command file is part of the Claude Code configuration. Edits apply to future invocations of `/audit`.

---

## Related Documentation

### Getting Started
- `README.md` - Framework overview (includes /audit section)
- `QUICKSTART.md` - 5-minute setup guide
- `USAGE_GUIDE.md` - Complete usage patterns

### Audit Process
- `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` - Systematic process
- `guides/GUIDE_IOS.md` - iOS patterns (includes workflow section)
- `guides/wcag/TESTING_CHECKLIST.md` - Component examination

### Report Templates
- `AUDIT_REPORT_TEMPLATE.md` - Enhanced template
- `AUDIT_IMPROVEMENTS_SUMMARY.md` - Why enhancements were made

### Quick References
- `AUDITOR_QUICK_START.md` - Auditor's quick reference
- `guides/wcag/QUICK_LOOKUP.md` - WCAG quick lookup

---

## FAQ

**Q: Can I use /audit on multiple platforms at once?**
A: No. Audit one platform at a time for better focus and manageable reports.

**Q: Why does /audit take 6-10 hours?**
A: Because it examines EVERY custom component and finds ALL instances. This thoroughness ensures complete fixes and prevents missing issues.

**Q: Can I skip phases?**
A: Not recommended. Each phase builds on the previous one. Skipping phases may result in incomplete coverage.

**Q: Where is the report saved?**
A: In the project being audited, NOT in the accessibility-fixer folder. Location: `[project]/accessibility-audit/reports/[platform]/`

**Q: Can I customize the /audit workflow?**
A: Yes, edit `.claude/commands/audit.md`. Changes apply to future audits.

**Q: What if I don't have 6-10 hours?**
A: Use a focused scope (e.g., "audit ONLY the login form" instead of "audit the home screen"). Focused audits take less time while maintaining thoroughness.

---

**Last Updated:** December 22, 2025
**Command Version:** Enhanced with comprehensive workflow (v2.0)
