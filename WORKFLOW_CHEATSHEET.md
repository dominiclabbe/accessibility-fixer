# Accessibility Audit Workflow - Cheat Sheet

## 📋 The Simple 5-Step Process

### Step 1: Setup (One Time)

**Option A: Automated (Recommended)**
```bash
cd your-project
/path/to/framework/setup-audit.sh
```

**Option B: With Claude Code**
```
Set up accessibility audit framework in this project.
Copy from: /path/to/accessibility-fixer/
```

**Option C: Manual**
```bash
cd your-project
mkdir -p accessibility-audit/{reports,screenshots}/{web,android,ios,tvos,android-tv}
cp /path/to/framework/*.md accessibility-audit/
```

📖 See INSTALLATION.md for details

### Step 2: Choose ONE Platform + ONE Feature
❌ "Audit my entire app"
✅ "Audit web authentication flow"
✅ "Audit Android checkout screens"

### Step 3: Use This Prompt
```
I want to audit ONLY [FEATURE] for accessibility issues.

Platform: [PLATFORM]

Follow ACCESSIBILITY_AUDIT_GUIDE.md

Create report at:
accessibility-audit/reports/[PLATFORM]/Accessibility_Audit_[PLATFORM]_[FEATURE]_[DATE].md

Ignore other parts of the app for now.
```

### Step 4: Capture Screenshots
- Run your app
- Navigate to each issue location
- Take screenshots
- Save as: `accessibility-audit/screenshots/[platform]/issue_###_description.png`

### Step 5: Next Phase
Repeat Steps 2-4 for next feature/platform.

---

## 🎯 Scope Templates

### By Feature
```
✅ "Audit ONLY the checkout flow"
✅ "Audit ONLY the authentication screens"
✅ "Audit ONLY the settings page"
```

### By Component Type
```
✅ "Audit ONLY form components"
✅ "Audit ONLY navigation elements"
✅ "Audit ONLY image and media components"
```

### By Directory
```
✅ "Audit ONLY files in src/components/forms/"
✅ "Audit ONLY files in src/pages/checkout/"
```

### By Severity (Quick Scan)
```
✅ "Quick scan: identify ONLY Critical and High severity issues"
```

---

## 📊 Session Size Guide

| Scope | Time | Issues | Status |
|-------|------|--------|--------|
| Single screen | 15-30 min | 5-15 | ✅ Perfect |
| Feature area | 30-60 min | 15-30 | ✅ Good |
| Component type | 30-60 min | 20-40 | ✅ Good |
| Full small app | 1-2 hours | 30-60 | ⚠️ OK for small apps |
| Full large app | 3+ hours | 100+ | ❌ Too big - split it! |

**Golden Rule:** If it takes more than 1 hour, break it down further.

---

## 🗓️ Example Project Plans

### Small Web App (1 Week)
```
Mon: Auth flow → Report #1
Tue: Main features → Report #2
Wed: Forms → Report #3
Thu: Fix issues + screenshots
Fri: Final report
```

### Medium App: Web + Mobile (3 Weeks)
```
Week 1: Web (4 phases)
├─ Mon: Critical flow
├─ Tue: Forms
├─ Wed: Navigation
└─ Thu: Media + screenshots

Week 2: Android (4 phases)
[Same pattern]

Week 3: iOS (4 phases)
[Same pattern]
```

### Large Multi-Platform (8 Weeks)
```
Week 1-2: Web critical features
Week 3-4: Android critical features
Week 5-6: iOS critical features
Week 7: Secondary features all platforms
Week 8: Consolidation + master report
```

---

## ✅ Checklist for Each Phase

**Before Starting:**
- [ ] Chose ONE platform
- [ ] Defined clear feature/component scope
- [ ] Created report directory structure
- [ ] Have ACCESSIBILITY_AUDIT_GUIDE.md available

**During Audit:**
- [ ] Used focused prompt with clear scope
- [ ] Reviewed generated report
- [ ] Verified file paths are accurate
- [ ] Checked WCAG SC references

**After Audit:**
- [ ] Ran the app/site
- [ ] Captured screenshots for each issue
- [ ] Saved screenshots with correct naming
- [ ] Verified screenshot paths in report

**Moving On:**
- [ ] Document what was completed
- [ ] Plan next phase
- [ ] Track progress

---

## 🚨 Common Mistakes to Avoid

❌ Auditing all platforms at once
✅ One platform at a time

❌ "Audit the whole app"
✅ "Audit the checkout flow"

❌ No clear stopping point
✅ Clear feature boundaries

❌ Waiting to capture all screenshots at end
✅ Capture screenshots per phase

❌ Starting with entire app
✅ Starting with critical user flow

---

## 📁 File Organization

```
accessibility-audit/
├── reports/
│   ├── web/
│   │   ├── Accessibility_Audit_Web_Auth_2025-01-29.md
│   │   ├── Accessibility_Audit_Web_Checkout_2025-01-30.md
│   │   └── Accessibility_Audit_Web_Forms_2025-01-31.md
│   ├── android/
│   │   └── Accessibility_Audit_Android_Auth_2025-02-01.md
│   └── MASTER_SUMMARY.md
└── screenshots/
    ├── web/
    │   ├── issue_001_button_no_label.png
    │   └── issue_002_low_contrast.png
    └── android/
        └── issue_001_missing_desc.png
```

---

## 🎯 Platform-Specific Quick Reference

### Web
**Check:** alt text, ARIA, semantic HTML, keyboard nav, focus, contrast
**Test with:** Chrome DevTools, axe, WAVE, NVDA/JAWS
**Common issues:** Missing alt text, unlabeled buttons, keyboard traps

### Android
**Check:** contentDescription, touch targets (48dp), TalkBack, EditText labels
**Test with:** Accessibility Scanner, TalkBack
**Common issues:** Missing contentDescription, small touch targets

### iOS
**Check:** accessibilityLabel, accessibilityTraits, VoiceOver, Dynamic Type
**Test with:** Xcode Inspector, VoiceOver
**Common issues:** Missing labels, incorrect traits, grouping issues

### React Native
**Check:** accessibilityLabel, accessibilityRole, accessibilityState
**Test with:** TalkBack (Android), VoiceOver (iOS)
**Common issues:** Missing labels on images/touchables

---

## 💬 Quick Prompts Library

### Start Feature Audit
```
Audit ONLY [FEATURE] for accessibility issues.
Platform: [PLATFORM]
Create report at: accessibility-audit/reports/[PLATFORM]/Accessibility_Audit_[PLATFORM]_[FEATURE]_[DATE].md
```

### Quick Critical Scan
```
Quick scan: identify ONLY Critical severity accessibility issues.
Platform: [PLATFORM]
Feature: [FEATURE]
```

### Deep Dive After Scan
```
Provide detailed analysis and fixes for all Critical issues from the previous scan.
Add code examples for each fix.
```

### Focus on Specific Issue Type
```
Audit ONLY for missing accessibility labels on interactive elements.
Platform: [PLATFORM]
Check: buttons, links, images, custom controls
```

### Focus on Specific WCAG SC
```
Audit ONLY for WCAG 2.1.1 Keyboard accessibility issues.
Platform: Web
Check: tab order, keyboard traps, focus management
```

### Add to Existing Report
```
I found another issue manually. Add to the report:
- Location: [file:line]
- Issue: [description]
- WCAG SC: [X.X.X]
```

### Create Master Summary
```
Create master summary from all platform reports:
accessibility-audit/reports/MASTER_SUMMARY.md

Include total issues, cross-platform patterns, priorities.
```

---

## 📚 Document Quick Links

| Need | Read This |
|------|-----------|
| Just starting | QUICK_START.md |
| Large project | PHASED_AUDIT_STRATEGY.md |
| Platform prompts | HOW_TO_START_AUDIT.md |
| WCAG reference | ACCESSIBILITY_AUDIT_GUIDE.md |
| Overview | README.md |

---

## 🎓 Remember

**The key to success:**
1. ✅ Small phases (30-60 min each)
2. ✅ One platform at a time
3. ✅ Clear boundaries (feature/component/screen)
4. ✅ Capture screenshots as you go
5. ✅ Build coverage progressively

**Better to have:**
- 5 complete, detailed reports on specific features
- Than 1 incomplete report trying to cover everything

---

**Ready? Pick your first small phase and go!**
