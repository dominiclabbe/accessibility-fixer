# Accessibility Audit Framework
## Complete System for Multi-Platform WCAG Audits with Claude Code

This framework enables comprehensive accessibility audits of any application by analyzing source code and generating detailed reports mapped to WCAG 2.2 guidelines.

---

## 🚀 Getting Started

### **Quick Setup for Claude Code**

**Want to use this with Claude Code? Two simple steps:**

**Step 1: Install accessibility-fixer (one-time)**
```bash
# Clone to a standard location
git clone https://github.com/dominiclabbe/accessibility-fixer.git
```

**Step 2: Set up your project**
```bash
# Navigate to project you want to audit
cd your-project

# Create output directories
/path/to/accessibility-fixer/setup-audit.sh

# Use the /audit command in Claude Code
> /audit
```

**That's it!** The `/audit` and `/pr-review` commands reference guidelines directly from the accessibility-fixer installation directory.

See **[INSTALLATION.md](INSTALLATION.md)** for complete instructions and **[COMMANDS_DOCUMENTATION.md](COMMANDS_DOCUMENTATION.md)** for command details.

---

## 🎯 Using the /audit Command

### What is /audit?

The `/audit` command is a **Claude Code slash command** that triggers a comprehensive accessibility audit workflow. When you type `/audit` in Claude Code, it automatically:

1. ✅ Loads all essential accessibility guidelines
2. ✅ Asks which platform to audit (iOS, Android, Web, etc.)
3. ✅ Loads platform-specific patterns and best practices
4. ✅ Follows a systematic 4-phase audit process
5. ✅ Generates a comprehensive report with implementation strategy

### How to Use /audit

**In Claude Code, simply type:**
```
/audit
```

**The command will:**
1. Ask which platform you want to audit
2. Ask which screen/feature to focus on
3. Load the comprehensive workflow guide
4. Guide you through a systematic audit process
5. Generate a detailed report in the audited project folder

### What Makes /audit Comprehensive?

The `/audit` command follows best practices learned from comparing multiple audits:

✅ **Exhaustive Coverage**
- Checks ALL custom components (not just screens)
- Finds ALL instances of each issue (not just first one)
- Examines ALL variants (Portrait, Landscape, Large, Small)

✅ **Component-Level Examination**
- Systematically checks every custom button class
- Reviews every custom view component
- Examines all collection item implementations

✅ **Enhanced Reporting**
- Implementation Strategy (phased 4-week plan)
- Localized Strings Required (complete list)
- Automated Testing Examples (sample test code)
- Files Audited (complete list)
- Components Examined (what was checked)

### Example Workflow

```
You: /audit

Claude: I'm ready to perform a comprehensive accessibility audit.
        Which platform would you like to audit?
        - iOS
        - Android
        - Web
        ...

You: iOS, focusing on the home screen

Claude: [Loads guides]
        [Follows 4-phase systematic process]
        [Creates comprehensive component checklist]
        [Examines ALL custom components]
        [Finds ALL instances of issues]
        [Generates enhanced report]
```

### Time Estimates

- **Phase 1 - Discovery:** 30-60 minutes
- **Phase 2 - Deep Dive:** 2-4 hours
- **Phase 3 - Verification:** 1-2 hours
- **Phase 4 - Report:** 2-3 hours
- **Total:** 6-10 hours for comprehensive home screen audit

**Why it takes longer:** The `/audit` command ensures NO components are missed and ALL instances of issues are documented. This thoroughness prevents incomplete fixes.

### For Auditors

**Before using `/audit`, read:**
1. `AUDITOR_QUICK_START.md` - Quick reference for auditors
2. `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` - Full workflow details
3. `AUDIT_IMPROVEMENTS_SUMMARY.md` - Why comprehensiveness matters

### Command Location

The `/audit` command is defined in `.claude/commands/audit.md` in this repository.

**Implementation Options:**
For CI/CD integration, MCP server, and other advanced options, see the plan file at:
`~/.claude/plans/synthetic-soaring-whisper.md` (created after setup)

---

## 🤖 Automated PR Reviews with /pr-review

### What is /pr-review?

The `/pr-review` command provides **automated accessibility review for Pull Requests**. Unlike `/audit` which reviews entire codebase sections, `/pr-review` focuses only on changed files in a PR and posts feedback directly as PR comments.

**Perfect for:**
- 🔄 **CI/CD Pipelines**: Run automatically on every PR
- ⚡ **Fast Feedback**: 30-60 minutes vs 6-10 hours
- 💬 **Inline Comments**: Issues posted directly on PR lines
- 🚦 **Gate Merges**: Block PRs with critical accessibility issues

### Quick Start

**Manual PR Review:**
```bash
# In Claude Code
/pr-review              # Auto-detect current branch PR
/pr-review 123          # Review PR #123
/pr-review --no-post    # Dry-run without posting comments
```

**Automated CI/CD:**
Add to `.github/workflows/accessibility-pr-review.yml`:
```yaml
name: Accessibility PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run PR Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Setup (one-time per workflow)
          gh --version || sudo apt-get install gh
          npm install -g @anthropic/claude-code
          git clone https://github.com/YOUR_ORG/accessibilityFixer.git /tmp/a11y
          bash /tmp/a11y/setup-audit.sh

          # Run review
          echo "$GITHUB_TOKEN" | gh auth login --with-token
          claude-code "/pr-review ${{ github.event.pull_request.number }}"
```

### What Gets Reviewed

✅ **Reviewed (Changed Code Only):**
- New UI components
- Modified accessibility properties
- Interactive elements (buttons, links, inputs)
- Text labels and hints
- Images and alt text

❌ **Skipped:**
- Unchanged code
- Non-UI code (business logic, APIs)

### PR Comments Example

The command posts inline comments like:
```markdown
⚠️ **Critical**: Button missing accessibility label

**WCAG SC:** 4.1.2 - Name, Role, Value (Level A)

**Issue:** Icon-only button without label
**Fix:**
```swift
Button(action: { share() }) {
    Image(systemName: "square.and.arrow.up")
}
.accessibilityLabel("Share")
```
```

Plus a summary comment with all issues grouped by severity.

### Exit Codes (CI)

- `0` = ✅ No critical issues (pass)
- `1` = ❌ Critical issues found (block merge)
- `2` = ⚠️ High priority issues (warning)

### Documentation

- **Quick Start**: [PR_REVIEW_QUICK_START.md](PR_REVIEW_QUICK_START.md) - 5-minute setup
- **Full Guide**: [PR_REVIEW_GUIDE.md](PR_REVIEW_GUIDE.md) - Complete documentation
- **CI Examples**: `ci-examples/` - GitHub Actions, GitLab CI, Bitbucket

### Prerequisites

```bash
# Install GitHub CLI (one-time)
brew install gh  # macOS
gh auth login

# Update .claude/settings.local.json permissions
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

### When to Use Which Command

| Use Case | Command | Time | Output |
|----------|---------|------|--------|
| Every PR before merge | `/pr-review` | 30-60 min | PR comments |
| New feature/major change | `/audit` | 6-10 hours | Detailed report |
| Apply fixes from audit | `/fix-accessibility` | 15-30 min | Code changes |

---

## 📚 Documentation Overview

### ⚡ **ABSOLUTE BEGINNER: [WORKFLOW_CHEATSHEET.md](WORKFLOW_CHEATSHEET.md)**
One-page visual guide with everything you need:
- Simple 5-step process
- Scope templates
- Session size guide
- Quick prompts library
- Common mistakes to avoid

**Use this when:** You want the simplest possible reference with no extra reading.

---

### 🚀 **START HERE: [QUICK_START.md](QUICK_START.md)**
Quick reference for starting an audit. Includes:
- One-command setup
- Ready-to-use prompt templates
- Platform-specific focus areas

**Use this when:** You want to start immediately with minimal reading.

---

### ⭐ **ESSENTIAL: [PHASED_AUDIT_STRATEGY.md](PHASED_AUDIT_STRATEGY.md)**
**READ THIS for large projects!**

Explains how to break down audits into manageable chunks:
- One platform at a time approach
- Breaking by feature area, component type, or screen
- Breaking by WCAG principle or severity
- Sample workflows for large projects
- Progress tracking

**Use this when:** Your project has multiple platforms or is large/complex.

---

### 📖 **REFERENCE: [ACCESSIBILITY_AUDIT_GUIDE.md](ACCESSIBILITY_AUDIT_GUIDE.md)**
Complete WCAG 2.2 framework and code analysis guide:
- WCAG 2.2 principles and success criteria
- Platform-specific code patterns (Web, Android, iOS, React Native, Flutter)
- Detailed audit report template
- Common issues reference with code examples
- Testing tools and resources

**Use this when:**
- You need WCAG reference information
- Looking for platform-specific code patterns
- Want to understand common accessibility issues
- Creating detailed audit reports

---

### 🎯 **DETAILED: [HOW_TO_START_AUDIT.md](HOW_TO_START_AUDIT.md)**
Step-by-step instructions with platform-specific prompts:
- Project setup commands
- Complete prompt templates for each platform
- Interactive workflow examples
- Screenshot capture guide
- Troubleshooting tips

**Use this when:**
- First time using the framework
- Need platform-specific prompt examples
- Want detailed workflow guidance

---

## 🎯 Quick Decision Tree

```
START
│
├─ First time using framework?
│  └─ YES → Read START_HERE.md + AUDITOR_QUICK_START.md
│  └─ NO  → Continue
│
├─ Large/multi-platform project?
│  └─ YES → Read PHASED_AUDIT_STRATEGY.md
│  └─ NO  → Use prompts from HOW_TO_START_AUDIT.md
│
├─ Need WCAG reference or code examples?
│  └─ YES → Reference guides/GUIDE_WCAG_REFERENCE.md
│  └─ NO  → Continue
│
└─ Ready to audit → Use /audit command or prompts from WORKFLOW_CHEATSHEET.md
```

---

## 💡 Key Concepts

### The Phased Approach

**❌ DON'T DO THIS:**
```
"Audit my entire multi-platform app for all accessibility issues"
```
→ Overwhelming, resource-intensive, produces massive reports

**✅ DO THIS INSTEAD:**
```
Phase 1: "Audit ONLY web authentication flow"
Phase 2: "Audit ONLY web checkout flow"
Phase 3: "Audit ONLY Android authentication flow"
[etc.]
```
→ Manageable, actionable, clear scope

### Platform Separation

**Each platform gets its own report:**
```
accessibility-audit/reports/
├── web/Accessibility_Audit_Web_Authentication_2025-10-29.md
├── android/Accessibility_Audit_Android_Authentication_2025-10-29.md
└── ios/Accessibility_Audit_iOS_Authentication_2025-10-29.md
```

### Progressive Coverage

Build comprehensive coverage over time through multiple focused sessions rather than one massive session.

---

## 🚀 Installation

### Quick Install

**Step 1: Install accessibilityFixer (one-time)**
```bash
git clone https://github.com/dominiclabbe/accessibility-fixer.git
```

**Step 2: Set up a project for auditing**
```bash
# Navigate to project
cd /path/to/your-project

# Create output directories
/path/to/accessibility-fixer/setup-audit.sh
```

**Step 3: Run `/audit` in Claude Code**
```bash
> /audit
```

The `/audit` command will reference guides from the accessibility-fixer installation directory and save reports to `./accessibility-audit/reports/`.

**📖 See [INSTALLATION.md](INSTALLATION.md) for detailed instructions and troubleshooting.**

---

## 🛠️ System Components

### 1. Directory Structure

**In your project (outputs only):**
```
your-project/
└── accessibility-audit/
    ├── reports/                      (audit reports)
    │   ├── web/                     (created when you generate web reports)
    │   ├── android/                 (created when you generate android reports)
    │   └── ios/                     (created when you generate ios reports)
    └── screenshots/                  (screenshots)
        ├── web/                     (created when you add web screenshots)
        ├── android/                 (created when you add android screenshots)
        └── ios/                     (created when you add ios screenshots)
```

**In accessibilityFixer (framework):**
```
/path/to/accessibility-fixer/
├── .claude/commands/audit.md        (/audit command)
├── guides/                           (all guidelines)
├── AUDIT_REPORT_TEMPLATE.md
├── setup-audit.sh
└── [all documentation]
```

**Note:**
- Platform-specific folders are created automatically when you generate your first report
- Guidelines are referenced from the accessibility-fixer installation, not copied to projects
- Projects only contain audit outputs (reports and screenshots)

### 2. Report Format

Each report includes:
- **Executive Summary** - Issue counts by severity
- **Issues by Severity** - Detailed documentation per issue
- **Issues by WCAG Guideline** - Organized by Success Criteria
- **Recommendations** - Prioritized action items

### 3. Issue Documentation

**⚠️ CRITICAL:** Each issue **MUST** contain:

```markdown
### Issue #XXX: [Title]

**WCAG SC Violated:**
- Primary: [SC X.X.X]
- Secondary: [SC Y.Y.Y]

**Severity:** Critical/High/Medium/Low

**Location:** ← REQUIRED: Exact file path and line number
- File: `src/components/Button.tsx`
- Line: `45`

**Current Code:** ← REQUIRED: Actual code from that location
```tsx
<button><Icon /></button>
```

**Recommended Fix:** ← REQUIRED: Copy-pasteable solution
```tsx
<button aria-label="Play"><Icon /></button>
```

**Visual Evidence:** ← REQUIRED: Predetermined filename pattern
![Screenshot](screenshots/web/issue_001_button_no_label.png)

**Impact:** [who is affected]
```

**📖 See:** `IMPORTANT_AUDIT_REQUIREMENTS.md` for complete requirements

---

## 🎬 Getting Started

### 1. Copy Framework to Your Project
```bash
cd /path/to/your-project
mkdir -p accessibility-audit/{reports,screenshots}/{web,android,ios,tvos,android-tv}
cp /path/to/ACCESSIBILITY_AUDIT_GUIDE.md accessibility-audit/
```

### 2. Start with One Platform, One Feature
```
I want to audit ONLY the web authentication flow for accessibility issues.

Follow ACCESSIBILITY_AUDIT_GUIDE.md

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_Auth_2025-10-29.md

Focus only on login/signup screens. Ignore other features.
```

### 3. Review Report and Capture Screenshots
- Claude analyzes code and creates report
- You run the app and capture screenshots
- Screenshots saved to `accessibility-audit/screenshots/web/`

### 4. Next Phase
```
Now audit the web checkout flow.

Create report at:
accessibility-audit/reports/web/Accessibility_Audit_Web_Checkout_2025-10-29.md
```

### 5. Repeat Until Complete

Continue with additional phases for:
- Other features on the same platform
- Other platforms
- Detailed analysis of critical issues

---

## 📊 What Gets Analyzed

### Code Analysis
- Missing accessibility labels/descriptions
- Semantic structure issues
- Color contrast problems
- Keyboard navigation issues
- Form label associations
- Focus management
- Dynamic content announcements
- Touch target sizes
- Screen reader compatibility

### Platforms Supported
- **Web** (HTML, React, Vue, Angular, etc.)
- **Android** (XML layouts, Jetpack Compose)
- **iOS** (UIKit, SwiftUI)
- **Android TV**
- **tvOS**
- **React Native**
- **Flutter**

### WCAG Coverage
- **Level A** - Basic requirements
- **Level AA** - Standard compliance target
- **Level AAA** - Enhanced accessibility (optional)

All 4 principles: Perceivable, Operable, Understandable, Robust

---

## 🎓 Best Practices

### 1. Always Start Small
Begin with critical user flows or high-traffic features.

### 2. One Platform at a Time
Never mix platforms in a single audit session.

### 3. Clear Boundaries
Define exact scope: "authentication flow" not "the whole app."

### 4. Iterative Refinement
- Phase 1: Quick scan for Critical issues
- Phase 2: Detailed analysis with fixes
- Phase 3: Review and screenshot capture

### 5. Track Progress
Maintain a checklist of completed phases.

### 6. Test as You Go
Don't wait until all audits are complete. Test and fix incrementally.

---

## 📝 Example Workflows

### Small Project (Single Platform)
```
Week 1: Audit web app in 3 phases
├── Phase 1: Critical user flows
├── Phase 2: Forms and inputs
└── Phase 3: Navigation and media

Week 2: Fix issues and capture screenshots
Week 3: Final report delivery
```

### Medium Project (2-3 Platforms)
```
Week 1: Web critical flows
Week 2: Web secondary features
Week 3: Android critical flows
Week 4: Android secondary features
Week 5: iOS critical flows
Week 6: iOS secondary features
Week 7: Consolidation and master summary
```

### Large Project (Many Platforms/Features)
```
Sprint 1: Web checkout (all issues)
Sprint 2: Android checkout (all issues)
Sprint 3: iOS checkout (all issues)
[Repeat for each major feature area]

Final Sprint: Cross-platform analysis and prioritization
```

---

## 🔧 Tools and Resources

### Automated Testing Tools
- **Web:** axe DevTools, WAVE, Lighthouse
- **Android:** Accessibility Scanner, Espresso
- **iOS:** Xcode Accessibility Inspector

### Manual Testing
- **Screen Readers:** TalkBack (Android), VoiceOver (iOS), NVDA/JAWS (Web)
- **Keyboard Navigation:** Tab key, arrow keys, Enter/Space
- **Contrast Checkers:** WebAIM, TPGI

### WCAG Resources
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/)
- [WCAG on Mobile](https://www.w3.org/TR/wcag2mobile-22/)

---

## 📤 Deliverables

### For Each Platform:
- Detailed audit report (Markdown format)
- Screenshots of issues
- Code snippets with fixes
- Prioritized recommendations

### Cross-Platform:
- Master summary report
- Common issues analysis
- Prioritized fix roadmap
- Compliance scorecard

---

## ❓ FAQ

**Q: Can I audit multiple platforms at once?**
A: Not recommended. Audit one platform at a time for better focus and manageable reports.

**Q: How long does an audit take?**
A: Depends on scope. A focused feature audit: 30-60 min. Full platform: 2-4+ hours. Use phased approach for large projects.

**Q: Does Claude capture screenshots?**
A: No. Claude analyzes source code. You must capture screenshots from the running app.

**Q: What WCAG level should I target?**
A: Level AA is the standard target for most compliance requirements.

**Q: Can I focus on specific WCAG criteria?**
A: Yes! You can audit for specific Success Criteria (e.g., "only check keyboard accessibility - WCAG 2.1.1").

**Q: Do I need to audit everything?**
A: No. Use risk-based approach: start with critical paths and high-traffic features.

---

## 📞 Support

This framework is designed to be used with **Claude Code** for source code analysis.

For questions about:
- **WCAG Guidelines:** https://www.w3.org/WAI/
- **Platform APIs:** See platform-specific documentation links in ACCESSIBILITY_AUDIT_GUIDE.md
- **This Framework:** Review the documentation files or ask Claude Code

---

## 📄 License and Usage

This framework can be copied to any project and customized as needed. The reports generated are yours to use and deliver to clients.

---

## 🗂️ File Index

### Command Files
| File | Purpose | When to Use |
|------|---------|-------------|
| **.claude/commands/audit.md** | `/audit` slash command | Triggering comprehensive audits |

### Documentation Files
| File | Purpose | When to Use |
|------|---------|-------------|
| **README.md** (this file) | System overview & /audit docs | Understanding the framework |
| **START_HERE.md** | 2-minute quick start | First time using framework |
| **AUDITOR_QUICK_START.md** | Quick start for auditors | Before first comprehensive audit |
| **COMMANDS_DOCUMENTATION.md** | Complete /audit command reference | Understanding /audit workflow |
| **AUDIT_IMPROVEMENTS_SUMMARY.md** | Why comprehensiveness matters | Understanding audit quality |
| **AUDIT_REPORT_TEMPLATE.md** | Enhanced report template | Creating audit reports |
| **INSTALLATION.md** | Detailed setup instructions | Installing the framework |
| **USAGE_GUIDE.md** | Integration patterns | Setting up with Claude Code |
| **setup-audit.sh** | Automated setup script | Quick installation |
| **WORKFLOW_CHEATSHEET.md** | One-page visual guide | Quickest reference, common prompts |
| **PHASED_AUDIT_STRATEGY.md** | Breaking down large audits | Large/complex projects |
| **HOW_TO_START_AUDIT.md** | Platform-specific prompts | Detailed audit instructions |
| **IMPORTANT_AUDIT_REQUIREMENTS.md** | Critical audit requirements | Before starting any audit |
| **ACCESSIBILITY_AUDIT_GUIDE.md** | Comprehensive methodology guide | Reference during audits |
| **CHANGELOG.md** | Framework change history | Understanding updates |

### Core Guides
| File | Purpose | When to Use |
|------|---------|-------------|
| **guides/COMPREHENSIVE_AUDIT_WORKFLOW.md** | Systematic audit process | Following 4-phase workflow (NEW) |
| **guides/GUIDE_WEB.md** | Web accessibility patterns | Web audits |
| **guides/GUIDE_ANDROID.md** | Android accessibility patterns | Android audits |
| **guides/GUIDE_IOS.md** | iOS accessibility patterns | iOS audits (UPDATED with workflow) |
| **guides/GUIDE_WCAG_REFERENCE.md** | WCAG principles | WCAG lookup |
| **guides/COMMON_ISSUES.md** | Cross-platform patterns | Common issues reference |
| **guides/wcag/TESTING_CHECKLIST.md** | Component examination checklist | During audits (UPDATED) |

---

## ✅ You're Ready!

### Absolute Fastest Start (2 minutes)
1. Read START_HERE.md
2. Run `/audit` command in Claude Code
3. Done!

### Recommended Start (10 minutes)
1. Read AUDITOR_QUICK_START.md (if doing comprehensive audit)
2. Read COMMANDS_DOCUMENTATION.md (understand /audit workflow)
3. Navigate to your project in Claude Code
4. Run `/audit` command
5. Choose platform and feature to audit
6. Review the generated report
7. Capture screenshots
8. Move to next phase

**Remember: Small, focused phases are better than trying to audit everything at once!**
# accessibility-fixer
