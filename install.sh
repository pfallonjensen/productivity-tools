#!/bin/bash
# Claude Code Tools - Universal Installer
# Usage:
#   install.sh              # Install/upgrade
#   install.sh uninstall    # Remove
#   install.sh --dry-run    # Show what would be installed

set -e  # Exit on error

MODE="${1:-install}"
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    MODE="install"
fi

REPO_BASE="https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main"
TOOL_NAME="smart-notifications"
TOOL_PATH="tools/$TOOL_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Detect OS
if [[ "$OSTYPE" != "darwin"* ]]; then
    log_error "macOS required (mic-check uses CoreAudio)"
fi

# Check dependencies
command -v python3 >/dev/null 2>&1 || log_error "Python 3 required"
command -v osascript >/dev/null 2>&1 || log_error "osascript required (macOS built-in)"
command -v say >/dev/null 2>&1 || log_error "say command required (macOS built-in)"

if [[ "$MODE" == "install" ]]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Claude Code Smart Notifications Installer"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if [[ "$DRY_RUN" == true ]]; then
        log_warn "DRY RUN MODE - No files will be modified"
        echo ""
    fi

    # Create directories
    log_info "Creating directories..."
    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p ~/.claude/hooks
        mkdir -p ~/.claude/commands
        mkdir -p ~/.claude/skills/name-session
        mkdir -p ~/.claude/session-labels
    fi

    # Backup settings.json if it exists
    if [[ -f ~/.claude/settings.json ]]; then
        BACKUP_FILE=~/.claude/settings.json.backup-$(date +%Y%m%d-%H%M%S)
        log_info "Backing up settings.json to $BACKUP_FILE"
        if [[ "$DRY_RUN" == false ]]; then
            cp ~/.claude/settings.json "$BACKUP_FILE"
        fi
    fi

    # Download and install files
    log_info "Installing notification hook..."
    if [[ "$DRY_RUN" == false ]]; then
        curl -fsSL "$REPO_BASE/$TOOL_PATH/hooks/notify.sh" -o ~/.claude/hooks/notify.sh
        chmod +x ~/.claude/hooks/notify.sh
    fi

    log_info "Installing claude-mute command..."
    if [[ "$DRY_RUN" == false ]]; then
        curl -fsSL "$REPO_BASE/$TOOL_PATH/commands/claude-mute.sh" -o ~/.claude/commands/claude-mute.sh
        chmod +x ~/.claude/commands/claude-mute.sh
    fi

    log_info "Installing name-session skill..."
    if [[ "$DRY_RUN" == false ]]; then
        curl -fsSL "$REPO_BASE/$TOOL_PATH/skills/name-session/skill.md" -o ~/.claude/skills/name-session/skill.md
    fi

    # Settings.json hooks (interactive)
    echo ""
    if [[ -f ~/.claude/settings.json ]]; then
        # Check if jq is available
        if command -v jq >/dev/null 2>&1; then
            echo "Add hooks to ~/.claude/settings.json automatically?"
            echo "  (y) Auto-merge with jq (recommended)"
            echo "  (n) Show manual instructions"
            read -p "Choice [y/n]: " -n 1 -r
            echo ""

            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if [[ "$DRY_RUN" == false ]]; then
                    log_info "Merging hooks into settings.json..."

                    # Use jq to add/update hooks
                    TEMP_FILE=$(mktemp)
                    jq '.hooks.Notification = [{"matcher": "", "hooks": [{"type": "command", "command": "$HOME/.claude/hooks/notify.sh notification"}]}] |
                        .hooks.Stop = [{"matcher": "", "hooks": [{"type": "command", "command": "$HOME/.claude/hooks/notify.sh stop"}]}]' \
                        ~/.claude/settings.json > "$TEMP_FILE"

                    # Validate JSON
                    if jq empty "$TEMP_FILE" 2>/dev/null; then
                        mv "$TEMP_FILE" ~/.claude/settings.json
                        log_info "Hooks added to settings.json"
                    else
                        rm "$TEMP_FILE"
                        log_error "Failed to merge settings.json - check backup at $BACKUP_FILE"
                    fi
                fi
            else
                echo ""
                log_info "Add these hooks to ~/.claude/settings.json manually:"
                cat <<'EOF'

"hooks": {
  "Notification": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "$HOME/.claude/hooks/notify.sh notification"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "$HOME/.claude/hooks/notify.sh stop"
        }
      ]
    }
  ]
}
EOF
            fi
        else
            log_warn "jq not installed - showing manual instructions"
            echo ""
            log_info "Install jq with: brew install jq"
            log_info "Or add these hooks to ~/.claude/settings.json manually:"
            cat <<'EOF'

"hooks": {
  "Notification": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "$HOME/.claude/hooks/notify.sh notification"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "$HOME/.claude/hooks/notify.sh stop"
        }
      ]
    }
  ]
}
EOF
        fi
    else
        log_warn "~/.claude/settings.json not found - create it with the hooks section above"
    fi

    # Shell alias (optional)
    echo ""
    SHELL_RC=""
    if [[ -f ~/.zshrc ]]; then
        SHELL_RC=~/.zshrc
    elif [[ -f ~/.bashrc ]]; then
        SHELL_RC=~/.bashrc
    fi

    if [[ -n "$SHELL_RC" ]]; then
        if ! grep -q "claude-mute" "$SHELL_RC" 2>/dev/null; then
            echo "Add claude-mute alias to $SHELL_RC?"
            read -p "Choice [y/n]: " -n 1 -r
            echo ""

            if [[ $REPLY =~ ^[Yy]$ ]] && [[ "$DRY_RUN" == false ]]; then
                echo 'alias claude-mute="$HOME/.claude/commands/claude-mute.sh"' >> "$SHELL_RC"
                log_info "Alias added to $SHELL_RC"
            fi
        else
            log_info "claude-mute alias already in $SHELL_RC"
        fi
    fi

    # Success
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Installation complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Next steps:"
    echo "  1. Restart Claude Code sessions (they need to reload hooks)"
    echo "  2. Label your sessions: /name-session"
    echo "  3. Control audio: claude-mute [on|off|status]"
    echo ""
    echo "Docs: https://github.com/pfallonjensen/claude-code-tools/tree/main/tools/smart-notifications"
    echo ""

elif [[ "$MODE" == "uninstall" ]]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Claude Code Smart Notifications Uninstaller"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Backup settings.json
    if [[ -f ~/.claude/settings.json ]]; then
        BACKUP_FILE=~/.claude/settings.json.backup-uninstall-$(date +%Y%m%d-%H%M%S)
        log_info "Backing up settings.json to $BACKUP_FILE"
        cp ~/.claude/settings.json "$BACKUP_FILE"
    fi

    # Remove files
    log_info "Removing hook files..."
    rm -f ~/.claude/hooks/notify.sh

    log_info "Removing command files..."
    rm -f ~/.claude/commands/claude-mute.sh

    log_info "Removing skill files..."
    rm -rf ~/.claude/skills/name-session

    # Session labels (ask first)
    if [[ -d ~/.claude/session-labels ]] && [[ -n "$(ls -A ~/.claude/session-labels 2>/dev/null)" ]]; then
        echo ""
        echo "Delete session labels in ~/.claude/session-labels/?"
        echo "  (You'll lose custom session names)"
        read -p "Choice [y/n]: " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf ~/.claude/session-labels
            log_info "Session labels deleted"
        else
            log_info "Session labels preserved"
        fi
    fi

    # Clean up cooldown files
    log_info "Removing cooldown files..."
    rm -f /tmp/claude-idle-*

    # Instructions for settings.json
    echo ""
    log_warn "Manual step: Remove hooks from ~/.claude/settings.json"
    echo "  Remove the 'Notification' and 'Stop' hook entries"
    echo ""

    # Instructions for shell alias
    if [[ -f ~/.zshrc ]] && grep -q "claude-mute" ~/.zshrc 2>/dev/null; then
        log_warn "Manual step: Remove alias from ~/.zshrc"
        echo "  Remove line: alias claude-mute=\"\$HOME/.claude/commands/claude-mute.sh\""
        echo ""
    fi

    log_info "Uninstall complete!"
    echo ""
else
    echo "Usage: install.sh [install|uninstall|--dry-run]"
    exit 1
fi
