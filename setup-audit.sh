#!/bin/bash

# Accessibility Audit Framework Setup Script
# Creates output directories and installs /audit command

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default target is current directory, but can be overridden
TARGET_DIR="${1:-.}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Accessibility Audit Setup                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Convert to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo -e "${GREEN}✓${NC} Target directory: ${TARGET_DIR}"
echo ""

# Step 1: Create output directories
echo -e "${BLUE}[1/2]${NC} Creating output directories..."

mkdir -p "${TARGET_DIR}/accessibility-audit/reports"
mkdir -p "${TARGET_DIR}/accessibility-audit/reports/pr"
mkdir -p "${TARGET_DIR}/accessibility-audit/screenshots"

echo -e "${GREEN}✓${NC} Created accessibility-audit/ directory structure"
echo -e "${YELLOW}ℹ${NC}  Platform folders (web/, android/, ios/, etc.) will be created"
echo -e "${YELLOW}ℹ${NC}  automatically when you generate your first report"
echo ""

# Step 2: Install commands
echo -e "${BLUE}[2/2]${NC} Installing commands..."

mkdir -p "${TARGET_DIR}/.claude/commands"

# Install /audit command
if [ -f "${SCRIPT_DIR}/.claude/commands/audit.md" ]; then
    cp "${SCRIPT_DIR}/.claude/commands/audit.md" "${TARGET_DIR}/.claude/commands/"
    echo -e "${GREEN}✓${NC} Installed /audit command"
else
    echo -e "${RED}⚠${NC}  Warning: audit.md not found"
fi

# Install /fix-accessibility command
if [ -f "${SCRIPT_DIR}/.claude/commands/fix-accessibility.md" ]; then
    cp "${SCRIPT_DIR}/.claude/commands/fix-accessibility.md" "${TARGET_DIR}/.claude/commands/"
    echo -e "${GREEN}✓${NC} Installed /fix-accessibility command"
else
    echo -e "${RED}⚠${NC}  Warning: fix-accessibility.md not found"
fi

# Install /pr-review command
if [ -f "${SCRIPT_DIR}/.claude/commands/pr-review.md" ]; then
    cp "${SCRIPT_DIR}/.claude/commands/pr-review.md" "${TARGET_DIR}/.claude/commands/"
    echo -e "${GREEN}✓${NC} Installed /pr-review command"
else
    echo -e "${RED}⚠${NC}  Warning: pr-review.md not found"
fi

echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Setup Complete!                                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓${NC} Project configured for accessibility audits"
echo ""
echo -e "${YELLOW}📁 What was created:${NC}"
echo "   .claude/commands/"
echo "   ├── audit.md                    (/audit command)"
echo "   ├── fix-accessibility.md        (/fix-accessibility command)"
echo "   └── pr-review.md                (/pr-review command)"
echo ""
echo "   accessibility-audit/"
echo "   ├── reports/                    (audit reports saved here)"
echo "   │   ├── web/                   (created on first web report)"
echo "   │   ├── android/               (created on first android report)"
echo "   │   ├── ios/                   (created on first ios report)"
echo "   │   └── pr/                    (PR review reports)"
echo "   └── screenshots/                (screenshots saved here)"
echo ""
echo -e "${YELLOW}📖 Next Steps:${NC}"
echo "   1. Open this project in Claude Code"
echo "   2. Run: /audit (to audit for issues)"
echo "   3. Run: /fix-accessibility (to fix issues from a report)"
echo "   4. Run: /pr-review (to review a PR for accessibility issues)"
echo "   5. Reports saved to accessibility-audit/reports/[platform]/"
echo ""
echo -e "${GREEN}Ready to audit! 🚀${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} The /audit command references guidelines from:"
echo "      ${SCRIPT_DIR}/"
echo ""
