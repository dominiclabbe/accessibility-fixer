# 🚀 Start Here - Accessibility Audit Framework

Welcome! This framework helps you audit any application for accessibility issues using Claude Code's `/audit` command.

---

## ⚡ 2-Minute Quick Start

### Step 1: Install accessibilityFixer (one-time)

```bash
# Clone to a standard location
git clone https://github.com/dominiclabbe/accessibility-fixer.git
```

### Step 2: Set up your project

```bash
# Navigate to project you want to audit
cd /path/to/your-project

# Create output directories
/path/to/accessibility-fixer/setup-audit.sh
```

### Step 3: Start auditing

In Claude Code:
```
/audit
```

The command will:
1. Ask which platform to audit
2. Ask which feature/screen to focus on
3. Load guidelines from `/path/to/accessibility-fixer/`
4. Guide you through a comprehensive 4-phase audit
5. Generate a detailed report in `./accessibility-audit/reports/[platform]/`

---

## 📚 What Should I Read Next?

**If you want to...**

| Goal | Read This | Time |
|------|-----------|------|
| Understand /audit command | COMMANDS_DOCUMENTATION.md | 10 min |
| Prepare for comprehensive audit | AUDITOR_QUICK_START.md | 5 min |
| Learn about phased audits | PHASED_AUDIT_STRATEGY.md | 10 min |
| Get platform-specific prompts | HOW_TO_START_AUDIT.md | 5 min |
| Quick reference | WORKFLOW_CHEATSHEET.md | 3 min |
| Understand why thoroughness matters | AUDIT_IMPROVEMENTS_SUMMARY.md | 10 min |
| See complete installation guide | INSTALLATION.md | 5 min |

---

## 🎯 Key Concepts

### The /audit Command

The `/audit` command is a Claude Code slash command that:
- ✅ Loads all essential accessibility guidelines automatically
- ✅ Follows a systematic 4-phase audit process
- ✅ Checks ALL custom components (not just screens)
- ✅ Finds ALL instances of each issue (not just first one)
- ✅ Generates enhanced reports with implementation strategy

**Example workflow:**
```
You: /audit

Claude: Which platform would you like to audit?
        - iOS
        - Android
        - Web
        ...

You: iOS, focusing on the home screen

Claude: [Loads guides]
        [Creates component checklist]
        [Examines all custom components]
        [Generates comprehensive report]
```

### No File Copying

The framework uses a **reference-based approach**:
- ✅ Guidelines live in one place: `/path/to/accessibility-fixer/`
- ✅ Projects only get output directories: `accessibility-audit/{reports,screenshots}`
- ✅ `/audit` command references guidelines directly
- ✅ Update once with `git pull`, all projects use latest version

### Phased Approach

**❌ Don't do this:**
```
"Audit my entire multi-platform app"
```

**✅ Do this instead:**
```
"Audit ONLY the iOS home screen"
"Audit ONLY the Android checkout flow"
"Audit ONLY the web login page"
```

Small, focused audits produce better results.

---

## ⚠️ Critical Requirements

Before auditing, understand these non-negotiable requirements:

**Every issue must have:**
1. ✅ Exact file path and line number
2. ✅ Current code snippet
3. ✅ Recommended fix (copy-pasteable)
4. ✅ Screenshot with pattern: `issue_###_description.png`

**Reports must:**
1. ✅ Order issues by severity (Critical → High → Medium → Low)
2. ✅ Document ALL instances of each issue
3. ✅ Include implementation strategy
4. ✅ Include localized strings list
5. ✅ Include automated test examples

See **IMPORTANT_AUDIT_REQUIREMENTS.md** for complete details.

---

## 🚀 Your First Audit

### Using the /audit Command (Recommended)

1. Navigate to your project in Claude Code
2. Type `/audit`
3. Answer the prompts (platform, feature to audit)
4. Review the generated report
5. Capture screenshots
6. Move to next feature

### Manual Prompt (Alternative)

If you want to customize, use this template:

```
I want to audit ONLY [FEATURE] for accessibility issues.

Platform: [PLATFORM]

Create report at:
accessibility-audit/reports/[PLATFORM]/Accessibility_Audit_[PLATFORM]_[FEATURE]_2025-12-22.md

Focus only on this feature. Ignore other parts of the app for now.
```

Replace:
- `[FEATURE]` = login page, checkout flow, home screen, etc.
- `[PLATFORM]` = web, android, ios, etc.

---

## 📊 After the Audit

### Step 1: Review Report

Claude generates a comprehensive report at:
```
./accessibility-audit/reports/[platform]/Accessibility_Audit_[Platform]_[Feature]_YYYY-MM-DD.md
```

### Step 2: Capture Screenshots

1. Run your app/website
2. Navigate to each issue location
3. Take screenshots
4. Save as: `accessibility-audit/screenshots/[platform]/issue_###_description.png`

**Example:**
- `issue_001_button_no_label.png`
- `issue_002_low_contrast_text.png`

### Step 3: Fix Issues

Use the report's implementation strategy to prioritize fixes:
- Start with Critical issues
- Move to High
- Then Medium and Low

### Step 4: Next Audit

Choose your next feature/screen/platform and repeat.

---

## 🆘 Common Questions

### Where are guidelines stored?

In `/path/to/accessibility-fixer/`. The `/audit` command references them directly.

### Where are reports saved?

In your project: `./accessibility-audit/reports/[platform]/`

### Can I audit multiple platforms at once?

No. Audit one platform at a time for better focus and manageable reports.

### How long does an audit take?

- Small feature: 30-60 minutes
- Home screen (comprehensive): 6-10 hours
- Full platform: Break into phases

### How do I update guidelines?

```bash
cd accessibility-fixer
git pull
```

All projects automatically use the updated version.

### What if I get stuck?

1. Check COMMANDS_DOCUMENTATION.md for `/audit` details
2. Check AUDITOR_QUICK_START.md for audit tips
3. Check platform guide: `guides/GUIDE_[PLATFORM].md`

---

## ✅ You're Ready!

**Quick recap:**
1. ✅ Install accessibilityFixer to `/path/to/accessibility-fixer/`
2. ✅ Run setup script in your project
3. ✅ Type `/audit` in Claude Code
4. ✅ Start with a small, focused feature

**Next steps:**
- Read AUDITOR_QUICK_START.md before your first comprehensive audit
- Read COMMANDS_DOCUMENTATION.md to understand the /audit workflow
- Check PHASED_AUDIT_STRATEGY.md for large projects

**Happy auditing!** 🚀
