# How to Use These Accessibility Guidelines

This repository contains comprehensive accessibility audit documentation for mobile and web applications.

---

## What's Included

### Core Documentation (163KB total)
- ✅ 4 WCAG 2.2 Principle guides with mobile interpretations
- ✅ Component-to-WCAG mappings (which SC applies to which component)
- ✅ Severity assignment guidelines
- ✅ Mobile WCAG interpretation guide
- ✅ Quick lookup tables and testing checklists
- ✅ Platform-specific guides (Android, iOS, Web, React Native, Flutter)
- ✅ Pattern guides (collections, font scaling, decorative images, etc.)

---

## Quick Start Options

### Option 1: Use with Claude Code (Simplest - Start Here)

**Setup (one-time):**
```bash
# Clone this guidelines repo to a standard location
git clone <this-repo-url> ~/.accessibility-guidelines

# Or if you already have it somewhere:
# ln -s /path/to/accessibilityFixer ~/.accessibility-guidelines
```

**In your app project:**
```bash
cd ~/my-app-project

# Create .claude/commands directory
mkdir -p .claude/commands

# Create audit slash command
cat > .claude/commands/audit.md << 'EOF'
# Accessibility Audit

You are performing an accessibility audit on this codebase.

## Guidelines Location
Load accessibility guidelines from: `~/.accessibility-guidelines/`

## Required Files to Load
Before starting, load these key files:
- `~/.accessibility-guidelines/guides/GUIDE_WCAG_REFERENCE.md`
- `~/.accessibility-guidelines/guides/wcag/QUICK_LOOKUP.md`
- `~/.accessibility-guidelines/guides/wcag/COMPONENT_WCAG_MAPPINGS.md`
- `~/.accessibility-guidelines/guides/wcag/SEVERITY_GUIDELINES.md`
- `~/.accessibility-guidelines/guides/wcag/TESTING_CHECKLIST.md`

## Workflow
1. Ask user which platform to audit (Android, iOS, Web, React Native, Flutter)
2. Load the appropriate platform guide from `~/.accessibility-guidelines/guides/`
3. Load relevant pattern guides as needed
4. Use TodoWrite to track audit progress
5. Systematically check each component type using COMPONENT_WCAG_MAPPINGS.md
6. Generate report in `./accessibility-audit/reports/YYYY-MM-DD_[platform]_audit.md`
7. Use template from `~/.accessibility-guidelines/AUDIT_REPORT_TEMPLATE.md`
8. Order issues by severity: Critical → High → Medium → Low
9. Provide summary of findings

Start by asking which platform to audit.
EOF

# Create directory for audit reports
mkdir -p accessibility-audit/reports
```

**Usage:**
```bash
# In your app project
claude-code

# Then type:
> /audit
```

**To update guidelines:**
```bash
cd ~/.accessibility-guidelines
git pull
```

---

### Option 2: Manual Reference (No Setup)

Just open the files directly when auditing:

1. **Start here:** `guides/GUIDE_WCAG_REFERENCE.md`
2. **Quick lookup:** `guides/wcag/QUICK_LOOKUP.md`
3. **For each component:** `guides/wcag/COMPONENT_WCAG_MAPPINGS.md`
4. **Platform-specific:** `guides/GUIDE_[PLATFORM].md`
5. **Severity rules:** `guides/wcag/SEVERITY_GUIDELINES.md`

---

### Option 3: Use in CI/CD (Future)

See the plan file for CLI tool architecture and GitHub Actions examples:
`~/.claude/plans/synthetic-soaring-whisper.md`

**Coming soon:**
- CLI static analyzer for automated checks
- GitHub Actions integration
- Pre-commit hooks
- MCP server for interactive use

---

## File Structure

```
~/.accessibility-guidelines/
├── guides/
│   ├── wcag/                           ← WCAG 2.2 detailed references
│   │   ├── PRINCIPLE_1_PERCEIVABLE.md
│   │   ├── PRINCIPLE_2_OPERABLE.md
│   │   ├── PRINCIPLE_3_UNDERSTANDABLE.md
│   │   ├── PRINCIPLE_4_ROBUST.md
│   │   ├── COMPONENT_WCAG_MAPPINGS.md  ← Which SC for each component
│   │   ├── QUICK_LOOKUP.md             ← Fast reference tables
│   │   ├── SEVERITY_GUIDELINES.md      ← How to assign severity
│   │   ├── MOBILE_WCAG_INTERPRETATION.md
│   │   └── TESTING_CHECKLIST.md
│   │
│   ├── patterns/                       ← Implementation patterns
│   │   ├── COLLECTION_ITEMS_PATTERN.md
│   │   ├── FONT_SCALING_SUPPORT.md
│   │   ├── DECORATIVE_IMAGE_DECISION_TREE.md
│   │   ├── AVOID_ROLE_IN_LABEL.md
│   │   ├── BUTTONS_ACTING_AS_TABS.md
│   │   ├── REPEATED_ELEMENTS_CONTEXT.md
│   │   └── NAVIGATION_BAR_ACCESSIBILITY.md
│   │
│   ├── GUIDE_WCAG_REFERENCE.md        ← Start here!
│   ├── GUIDE_ANDROID.md
│   ├── GUIDE_IOS.md
│   ├── GUIDE_WEB.md
│   ├── GUIDE_REACT_NATIVE.md
│   ├── GUIDE_FLUTTER.md
│   ├── GUIDE_ANDROID_TV.md
│   ├── GUIDE_TVOS.md
│   └── COMMON_ISSUES.md
│
├── AUDIT_REPORT_TEMPLATE.md
├── HOW_TO_START_AUDIT.md
├── IMPORTANT_AUDIT_REQUIREMENTS.md
└── README.md
```

---

## Common Workflows

### Auditing a New App

1. **Identify platform** (Android, iOS, Web, etc.)
2. **Load platform guide** (`guides/GUIDE_[PLATFORM].md`)
3. **Use testing checklist** (`guides/wcag/TESTING_CHECKLIST.md`)
4. **Look up components** (`guides/wcag/COMPONENT_WCAG_MAPPINGS.md`)
5. **Check patterns** (`guides/patterns/` as needed)
6. **Assign severity** (`guides/wcag/SEVERITY_GUIDELINES.md`)
7. **Generate report** using `AUDIT_REPORT_TEMPLATE.md`

### Quick Reference During Audit

Need to know:
- **Which WCAG SC for a button?** → `COMPONENT_WCAG_MAPPINGS.md`
- **Is this Critical or High?** → `SEVERITY_GUIDELINES.md`
- **How to handle collections?** → `patterns/COLLECTION_ITEMS_PATTERN.md`
- **Text scaling requirements?** → `patterns/FONT_SCALING_SUPPORT.md`
- **All details about 4.1.2?** → `wcag/PRINCIPLE_4_ROBUST.md`

### Checking a Specific Issue

Example: "Missing contentDescription on ImageView"

1. Look up in `COMPONENT_WCAG_MAPPINGS.md` → Images section
2. See it violates: 1.1.1 (Level A), 4.1.2 (Level A)
3. Check `SEVERITY_GUIDELINES.md` → Level A + blocks functionality = Critical
4. Check platform guide for implementation
5. Check `DECORATIVE_IMAGE_DECISION_TREE.md` if unsure if decorative

---

## Integration Patterns

### Pattern 1: Local Clone (Recommended for now)
```bash
# One-time setup
git clone <this-repo> ~/.accessibility-guidelines

# Update regularly
cd ~/.accessibility-guidelines && git pull

# Use with Claude Code /audit command
```

### Pattern 2: Project-Specific (Not recommended)
```bash
# In your app repo
git submodule add <this-repo> .accessibility-guidelines

# Everyone on team needs to:
git submodule update --init --recursive
```

### Pattern 3: CI/CD (Future)
```yaml
# .github/workflows/accessibility.yml
- name: Fetch Guidelines
  run: git clone <this-repo> ./guidelines

- name: Run Audit
  run: ./guidelines/audit-script.sh
```

---

## Tips for Best Results

### For Auditors
1. **Always use the testing checklist** - Don't rely on memory
2. **Cross-reference pattern guides** - Especially for collections, tabs, etc.
3. **Assign severity consistently** - Use the severity guidelines
4. **Test with real screen readers** - Don't just read code
5. **Include file locations** - Always provide line numbers
6. **Use code examples** - Show current and corrected code

### For Developers
1. **Update guidelines regularly** - `git pull` weekly
2. **Read platform guide first** - Before starting development
3. **Check common issues** - See `COMMON_ISSUES.md`
4. **Use pattern guides** - Don't reinvent the wheel
5. **Test early, test often** - Don't wait until the end

---

## Getting Latest Guidelines

### If Cloned to ~/.accessibility-guidelines
```bash
cd ~/.accessibility-guidelines
git pull origin main
```

### If Using Submodule
```bash
cd your-app-project
git submodule update --remote .accessibility-guidelines
```

### Check Current Version
```bash
cd ~/.accessibility-guidelines
git log -1 --format="%H %s (%ar)"
```

---

## Official WCAG Resources

These guidelines are based on:
- **WCAG 2.2:** https://www.w3.org/TR/WCAG22/
- **WCAG 2.2 JSON:** https://www.w3.org/WAI/WCAG22/wcag.json
- **Understanding WCAG:** https://www.w3.org/WAI/WCAG22/Understanding/
- **Mobile Accessibility:** https://www.w3.org/TR/mobile-accessibility-mapping/

---

## Support and Questions

### Quick Answers
- **"How do I audit a button?"** → `COMPONENT_WCAG_MAPPINGS.md` → Buttons section
- **"Is this severe enough to block?"** → `SEVERITY_GUIDELINES.md`
- **"Collection items confusing?"** → `patterns/COLLECTION_ITEMS_PATTERN.md`
- **"What's new in WCAG 2.2?"** → Check principle guides for "NEW in WCAG 2.2"

### For detailed implementation help
- See platform-specific guides
- Check pattern guides for common scenarios
- Reference WCAG principle files for complete SC details

---

## Next Steps

1. ✅ Clone guidelines to `~/.accessibility-guidelines`
2. ✅ Create `/audit` slash command in your project
3. ✅ Read the platform guide for your target
4. ✅ Start auditing with testing checklist
5. 🔄 Update guidelines weekly

**Ready to start?** Run `/audit` in Claude Code!
