#!/bin/bash
# Bug & Enhancement Tracker — Installer
# Run from your project root:
#   bash <(curl -fsSL https://raw.githubusercontent.com/pfallonjensen/productivity-tools/main/tools/bug-tracker/install.sh)
#
# Or download and run locally:
#   curl -fsSL https://raw.githubusercontent.com/pfallonjensen/productivity-tools/main/tools/bug-tracker/install.sh -o install-bug-tracker.sh
#   bash install-bug-tracker.sh [install|uninstall|--dry-run]

set -e

MODE="${1:-install}"
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    MODE="install"
fi

REPO_BASE="https://raw.githubusercontent.com/pfallonjensen/productivity-tools/main/tools/bug-tracker"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Detect project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
TRACKER_DIR="$PROJECT_ROOT/.claude/Bugs-to-Fix"
SKILLS_DIR="$PROJECT_ROOT/.claude/skills"
CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

if [[ "$MODE" == "install" ]]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Bug & Enhancement Tracker — Installer"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Project root: $PROJECT_ROOT"
    echo ""

    if [[ "$DRY_RUN" == true ]]; then
        log_warn "DRY RUN MODE — No files will be modified"
        echo ""
    fi

    # Step 1: Create tracker directory
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$TRACKER_DIR"
    fi
    log_info "Created .claude/Bugs-to-Fix/"

    # Step 2: Download templates
    echo ""
    echo "Downloading templates..."
    for template in BUG-TEMPLATE.md ENH-TEMPLATE.md README.md; do
        if [[ ! -f "$TRACKER_DIR/$template" ]]; then
            if [[ "$DRY_RUN" == false ]]; then
                curl -fsSL "$REPO_BASE/templates/$template" -o "$TRACKER_DIR/$template"
            fi
            log_info "Downloaded $template"
        else
            log_warn "$template already exists, skipping"
        fi
    done

    # Step 3: Install skills (optional)
    echo ""
    read -r -p "Install Claude Code skills? (/log-bug, /log-enh, /review-tickets) [Y/n] " INSTALL_SKILLS
    INSTALL_SKILLS="${INSTALL_SKILLS:-Y}"

    if [[ "$INSTALL_SKILLS" =~ ^[Yy]$ ]]; then
        if [[ "$DRY_RUN" == false ]]; then
            mkdir -p "$SKILLS_DIR"
        fi
        for skill in log-bug log-enh review-tickets; do
            SKILL_DEST="$SKILLS_DIR/$skill"
            if [[ ! -d "$SKILL_DEST" ]]; then
                if [[ "$DRY_RUN" == false ]]; then
                    mkdir -p "$SKILL_DEST"
                    curl -fsSL "$REPO_BASE/skills/$skill/skill.md" -o "$SKILL_DEST/skill.md"
                fi
                log_info "Installed /$skill"
            else
                log_warn "/$skill already exists, skipping"
            fi
        done
    fi

    # Step 4: CLAUDE.md snippet (optional)
    echo ""
    SNIPPET='## Bug & Enhancement Tracker

When a bug, error, or broken behavior comes up mid-conversation, offer to file a ticket:
> "Want me to file a bug ticket for this?"

When the user has an idea or improvement request, offer to file an ENH ticket:
> "Want me to file an enhancement for this?"

If yes, use the /log-bug or /log-enh skill. If skills are not installed, copy the
appropriate template from .claude/Bugs-to-Fix/, fill it in using the current session
context (session ID, timestamp, search terms), capture the user'"'"'s words with minimal
editing, and save the file with the correct naming convention.'

    if [[ -f "$CLAUDE_MD" ]]; then
        if grep -q "Bug & Enhancement Tracker" "$CLAUDE_MD" 2>/dev/null; then
            log_info "CLAUDE.md already has the tracker snippet"
        else
            read -r -p "Append tracker snippet to CLAUDE.md? [Y/n] " ADD_SNIPPET
            ADD_SNIPPET="${ADD_SNIPPET:-Y}"
            if [[ "$ADD_SNIPPET" =~ ^[Yy]$ ]]; then
                if [[ "$DRY_RUN" == false ]]; then
                    echo "" >> "$CLAUDE_MD"
                    echo "$SNIPPET" >> "$CLAUDE_MD"
                fi
                log_info "Snippet appended to CLAUDE.md"
            else
                log_warn "Skipped. Add snippet manually — see CLAUDE.md.example or README.md."
            fi
        fi
    else
        read -r -p "No CLAUDE.md found. Create one with the tracker snippet? [Y/n] " CREATE_CLAUDE
        CREATE_CLAUDE="${CREATE_CLAUDE:-Y}"
        if [[ "$CREATE_CLAUDE" =~ ^[Yy]$ ]]; then
            if [[ "$DRY_RUN" == false ]]; then
                echo "# Project Instructions" > "$CLAUDE_MD"
                echo "" >> "$CLAUDE_MD"
                echo "$SNIPPET" >> "$CLAUDE_MD"
            fi
            log_info "Created CLAUDE.md with tracker snippet"
        else
            log_warn "Skipped. Without CLAUDE.md, file tickets manually or by asking Claude."
        fi
    fi

    # Done
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Installation complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Getting started:"
    echo "  /log-bug          — file a bug conversationally"
    echo "  /log-enh          — file an enhancement conversationally"
    echo "  /review-tickets   — see all open tickets"
    echo ""
    echo "Or just tell Claude: \"log a bug for [describe problem]\""
    echo ""
    echo "Next: Customize category prefixes for your project:"
    echo "  Open Claude Code and say: \"Read .claude/Bugs-to-Fix/README.md"
    echo "  and update the category prefixes to match my actual project folders.\""
    echo ""

elif [[ "$MODE" == "uninstall" ]]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Bug & Enhancement Tracker — Uninstaller"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Project root: $PROJECT_ROOT"
    echo ""

    # Remove skills
    for skill in log-bug log-enh review-tickets; do
        if [[ -d "$SKILLS_DIR/$skill" ]]; then
            rm -rf "$SKILLS_DIR/$skill"
            log_info "Removed /$skill skill"
        fi
    done

    # Ticket files — ask before deleting
    if [[ -d "$TRACKER_DIR" ]]; then
        echo ""
        echo "Remove .claude/Bugs-to-Fix/? This deletes all your ticket files."
        read -r -p "  Choice [y/N] " REMOVE_TICKETS
        REMOVE_TICKETS="${REMOVE_TICKETS:-N}"
        if [[ "$REMOVE_TICKETS" =~ ^[Yy]$ ]]; then
            rm -rf "$TRACKER_DIR"
            log_info "Removed .claude/Bugs-to-Fix/"
        else
            log_info "Ticket files preserved in .claude/Bugs-to-Fix/"
        fi
    fi

    echo ""
    log_warn "Manual step: Remove the '## Bug & Enhancement Tracker' section from CLAUDE.md if present"
    echo ""
    log_info "Uninstall complete!"
    echo ""

else
    echo "Usage: install.sh [install|uninstall|--dry-run]"
    exit 1
fi
