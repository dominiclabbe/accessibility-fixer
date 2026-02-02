# Auditor Quick Start Guide
## Start here for your first comprehensive accessibility audit

---

## 🚀 Quick Start (5 minutes)

### 1. Load These Guides FIRST
Before touching any code, read these in order:

**Essential (20 min):**
1. ✅ `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` - Your main process guide
2. ✅ `guides/GUIDE_[PLATFORM].md` - Platform-specific patterns (iOS, Android, Web, etc.)

**Reference (keep open):**
3. ✅ `guides/wcag/QUICK_LOOKUP.md` - Quick WCAG reference
4. ✅ `guides/wcag/TESTING_CHECKLIST.md` - Component examination checklist
5. ✅ `AUDIT_REPORT_TEMPLATE.md` - Report format

### 2. Set Up Your Environment
```bash
# Navigate to the project you're auditing
cd /path/to/project

# Enable screen reader
# iOS: Settings → Accessibility → VoiceOver
# Android: Settings → Accessibility → TalkBack

# Open code editor
# Have search capabilities ready
```

### 3. Start the 4-Phase Process

**Phase 1: Discovery (30-60 min)**
- Navigate with screen reader
- Note obvious issues
- List all custom components

**Phase 2: Deep Dive (2-4 hours)**
- Check EVERY custom component file
- Find ALL instances of each issue
- Document with file paths

**Phase 3: Verification (1-2 hours)**
- Search for patterns
- Ensure no components missed
- Cross-check against checklist

**Phase 4: Report (2-3 hours)**
- Use enhanced template
- Include implementation strategy
- Include strings list
- Include test examples

---

## 📋 The Golden Rules

### Rule 1: Check ALL Instances
❌ **Wrong:** Found one play button without label → reported one issue
✅ **Right:** Found one play button → searched codebase → found 5 play buttons → reported 5 locations

### Rule 2: Examine ALL Components
❌ **Wrong:** Checked main screen files
✅ **Right:** Checked all custom Button files, View files, Cell files

### Rule 3: Document Everything
❌ **Wrong:** "Play buttons need labels"
✅ **Right:**
- `PlayButton.swift:36` - play button in poster
- `PromotionalBannerView.swift:20` - play button in banner
- `VideoPlayerControls.swift:45` - play button in controls

### Rule 4: Provide Implementation Plan
❌ **Wrong:** Just list issues
✅ **Right:** Include phased rollout, strings list, test examples

---

## 🔍 Essential Search Commands

### Find All Custom Components

**iOS:**
```bash
# Find all custom buttons
find . -name "*.swift" -exec grep -l "class.*Button" {} \;

# Find all custom views
find . -name "*.swift" -exec grep -l "class.*View" {} \;

# Find all collection cells
find . -name "*.swift" -exec grep -l "class.*Cell" {} \;
```

**Android:**
```bash
# Find all custom buttons
find . -name "*.kt" -exec grep -l "class.*Button" {} \;

# Find all custom views
find . -name "*.kt" -exec grep -l "class.*View" {} \;

# Find all view holders
find . -name "*.kt" -exec grep -l "ViewHolder" {} \;
```

### Search for Patterns

**Find all instances of a component:**
```bash
# Example: Find all FavoriteButton usages
grep -r "FavoriteButton" --include="*.swift" --include="*.kt"

# Find all channel logos
grep -ri "channellogo\|channel_logo\|channelicon" --include="*.swift" --include="*.kt"
```

---

## ✅ Component Examination Checklist

For EACH custom component found:

### Custom Buttons
- [ ] Read entire component file
- [ ] Check `accessibilityLabel` set
- [ ] Check proper trait/role
- [ ] Check state changes announced
- [ ] Find ALL usages in codebase
- [ ] Document EACH usage location

### Images/Icons
- [ ] Determine: Decorative or informational?
- [ ] Check proper labeling or hidden
- [ ] Search for ALL instances
- [ ] Check in: tiles, banners, headers, cells

### Collection Items
- [ ] Find ALL tile/cell types
- [ ] Check parent is single focusable unit
- [ ] Check children hidden from assistive tech
- [ ] Check merged label complete

### Navigation
- [ ] Tab bar: labels, states, position
- [ ] Top nav bar: all buttons labeled
- [ ] Drawer/menu: all items labeled

---

## 📝 Report Structure Checklist

Your report MUST include:

### Core Sections
- [ ] **Executive Summary** with issue counts
- [ ] **Methodology** section
- [ ] **Issues by Severity** (Critical → High → Medium → Low)
- [ ] **Issues by WCAG Guideline** (grouped)

### NEW Required Sections
- [ ] **Implementation Strategy** (phased 4-week plan)
- [ ] **Localized Strings Required** (complete list)
- [ ] **Automated Testing Examples** (sample test code)
- [ ] **Files Audited** (complete list)
- [ ] **Components Examined** (list of all checked)

### Quality Checks
- [ ] Issues ordered by severity (NOT location)
- [ ] Every issue has file path + line number
- [ ] Current and corrected code provided
- [ ] ALL instances documented separately

---

## ⚠️ Common Mistakes to Avoid

### ❌ Mistake 1: Stopping at First Instance
**Problem:** Found one issue, moved on
**Solution:** Search entire codebase for pattern

### ❌ Mistake 2: Skipping Custom Components
**Problem:** Didn't examine FavoriteButton.swift
**Solution:** List ALL custom components first, check each

### ❌ Mistake 3: Missing Variants
**Problem:** Checked PortraitTile, missed LandscapeTile
**Solution:** Use glob patterns to find ALL variants

### ❌ Mistake 4: No Implementation Plan
**Problem:** Just listed issues
**Solution:** Use enhanced template with strategy section

### ❌ Mistake 5: Ordering by Location
**Problem:** Issues ordered by file location
**Solution:** Always order by severity

---

## 🎯 Success Criteria

Your audit is comprehensive if:

✅ **Coverage**
- Examined 100% of custom component types
- Found and documented ALL instances of each issue
- Checked all variants (Portrait, Landscape, etc.)

✅ **Documentation**
- Every issue has file:line reference
- All instances documented separately
- Code examples (current + corrected) provided

✅ **Actionability**
- Implementation strategy included
- Localized strings list included
- Test examples included
- Clear priorities and timeline

---

## 📚 Reference Card

Keep this handy during audits:

### WCAG Severity Mapping
- **Critical:** Blocks core functionality (buttons without labels)
- **High:** Degrades experience (missing headings, contrast)
- **Medium:** Usability issues (unclear labels, small targets)
- **Low:** Polish issues (ambiguous decorative status)

### Quick Component Checks
- **Buttons:** Label, trait, state?
- **Images:** Decorative or labeled?
- **Collections:** Grouped as single unit?
- **Forms:** Persistent labels?
- **Headings:** Proper trait?
- **Navigation:** Labels, states, consistent?

### Documentation Pattern
```markdown
#### Issue #XXX: Component - Problem

**Severity:** Critical
**WCAG SC:** X.X.X (Level X)

**All Instances:**
1. File.swift:123
2. OtherFile.swift:456

**Impact:** User cannot...
**Current Code:** [show code]
**Recommended Fix:** [show fix]
```

---

## 🆘 Need Help?

### During Audit
1. Check `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md` for process
2. Check `guides/wcag/QUICK_LOOKUP.md` for WCAG reference
3. Check pattern guides in `guides/patterns/` for specific patterns
4. Check platform guide for platform-specific patterns

### Common Questions

**Q: How do I know if an image is decorative?**
A: See `guides/patterns/DECORATIVE_IMAGE_DECISION_TREE.md`

**Q: How do I handle collection items?**
A: See `guides/patterns/COLLECTION_ITEMS_PATTERN.md`

**Q: How do I check text scaling?**
A: See `guides/patterns/FONT_SCALING_SUPPORT.md`

**Q: How many instances should I document?**
A: ALL of them. If you find 5, document all 5 with file paths.

**Q: How long should an audit take?**
A: 6-10 hours for comprehensive home screen audit

---

## 🏁 Final Checklist Before Submitting

- [ ] Followed 4-phase process completely
- [ ] Examined ALL custom components
- [ ] Documented ALL instances of each issue
- [ ] Used enhanced report template
- [ ] Included Implementation Strategy
- [ ] Included Localized Strings list
- [ ] Included Test Examples
- [ ] Included Files Audited list
- [ ] Issues ordered by severity
- [ ] Every issue has file:line reference
- [ ] Spell-checked and proofread

---

**Remember:** A comprehensive audit takes time but ensures nothing is missed. Quality over speed!

**Estimated Time:** 6-10 hours for thorough home screen audit

**Next Steps:**
1. Open `guides/COMPREHENSIVE_AUDIT_WORKFLOW.md`
2. Follow Phase 1: Discovery
3. Create component checklist
4. Begin systematic examination

Good luck! 🚀
