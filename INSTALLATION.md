# Installation Guide

This guide shows you how to set up the accessibility audit framework for use with Claude Code.

---

## Overview

The framework works by:
1. **accessibility-fixer** stays in one location (contains all guides and tools)
2. **Projects** get minimal output directories created (for reports and screenshots)
3. **`/audit` command** references guides directly from accessibility-fixer location

---

## Step 1: Install accessibility-fixer (One-Time Setup)

Choose a standard location for the framework:

```bash
# Clone to your preferred location
git clone https://github.com/dominiclabbe/accessibility-fixer.git accessibility-fixer
cd accessibility-fixer

# Or if you already have it somewhere, note the path
# e.g., /path/to/accessibility-fixer
```

**Important:** The `/audit` command is configured to reference guides from:
```
/path/to/accessibility-fixer/
```

If you install it elsewhere, update `.claude/commands/audit.md` with your path.

---

## Step 2: Set Up Claude Code Slash Command (One-Time Setup)

The `/audit` command is already configured in `.claude/commands/audit.md` and references the accessibility-fixer location directly.

**To verify it's working:**
1. Open any project in Claude Code
2. Type `/audit`
3. If it works, you're done!

**If `/audit` isn't available:**
The `.claude/commands/audit.md` file needs to be in your Claude Code configuration. This is already included in the accessibility-fixer repository.

---

## Step 3: Set Up a Project for Auditing

For each project you want to audit, create output directories:

### Method A: Using the Setup Script (Recommended)

```bash
# Navigate to your project
cd /path/to/your-project

# Run setup script
/path/to/accessibility-fixer/setup-audit.sh
```

This creates:
```
your-project/
├── .claude/commands/
│   └── audit.md              (/audit command)
└── accessibility-audit/
    ├── reports/              (audit reports saved here)
    └── screenshots/          (screenshots saved here)
```

### Method B: Manual Setup

```bash
cd /path/to/your-project

# Create output directories
mkdir -p accessibility-audit/{reports,screenshots}

# Install /audit command
mkdir -p .claude/commands
cp /path/to/accessibility-fixer/.claude/commands/audit.md .claude/commands/
```

---

## Step 4: Start Auditing

```bash
# In Claude Code, navigate to your project
cd /path/to/your-project

# Run the audit command
> /audit
```

The `/audit` command will:
1. Ask which platform to audit
2. Load guidelines from `/path/to/accessibility-fixer/`
3. Guide you through the audit process
4. Save reports to `./accessibility-audit/reports/[platform]/`

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│ accessibility-fixer (Framework)                          │
│ Location: /path/to/accessibility-fixer/                     │
│                                                          │
│ Contains:                                                │
│ ├── .claude/commands/audit.md  (/audit command)        │
│ ├── guides/                     (all guidelines)        │
│ ├── AUDIT_REPORT_TEMPLATE.md                           │
│ ├── setup-audit.sh                                      │
│ └── [all other documentation]                           │
└─────────────────────────────────────────────────────────┘
                            ▼
                   (references guides)
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Your Project                                             │
│ Location: /path/to/your-project/                        │
│                                                          │
│ Contains:                                                │
│ └── accessibility-audit/       (outputs only)           │
│     ├── reports/                                         │
│     │   └── ios/Accessibility_Audit_iOS_Home_2025.md   │
│     └── screenshots/                                     │
│         └── ios/issue_001_button_no_label.png          │
└─────────────────────────────────────────────────────────┘
```

---

## Benefits of This Approach

✅ **Single source of truth** - One accessibility-fixer location for all projects
✅ **Always up-to-date** - `git pull` in accessibility-fixer updates for everyone
✅ **Clean projects** - Projects only contain audit outputs, not framework files
✅ **Simple setup** - Just create output directories, no copying needed
✅ **No duplication** - Don't copy 2MB+ of guides to every project

---

## Updating the Framework

```bash
cd /path/to/accessibility-fixer
git pull
```

All projects using `/audit` will automatically use the updated guidelines.

---

## Verification

After setup, verify everything works:

```bash
# 1. Check accessibility-fixer location
ls /path/to/accessibility-fixer/guides/

# 2. Navigate to a project
cd /path/to/your-project

# 3. Check output directories exist
ls accessibility-audit/

# 4. Run /audit command in Claude Code
> /audit
```

---

## Troubleshooting

### `/audit` command not found

The `.claude/commands/audit.md` file should be in the accessibility-fixer repository. Make sure Claude Code can access it.

### Wrong guidelines path

If you installed accessibility-fixer in a different location, update the path in `.claude/commands/audit.md`:

```markdown
## Guidelines Location
The accessibility guidelines are located at: /your/custom/path/accessibility-fixer/
```

### Reports not saving

Make sure `accessibility-audit/` directories exist in your project:
```bash
mkdir -p accessibility-audit/{reports,screenshots}
```

---

## Multiple Machines

To use on multiple machines:

1. **Clone accessibility-fixer** on each machine to the same location:
   ```bash
   git clone https://github.com/dominiclabbe/accessibility-fixer.git
   ```

2. **Set up each project** with output directories:
   ```bash
   /path/to/accessibility-fixer/setup-audit.sh
   ```

---

## Summary

**One-time:**
1. Install accessibility-fixer to `/path/to/accessibility-fixer/`
2. Verify `/audit` command works in Claude Code

**Per-project:**
1. Run `/path/to/accessibility-fixer/setup-audit.sh` (creates output directories)
2. Run `/audit` command in Claude Code

**No file copying needed!**
