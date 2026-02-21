#!/bin/bash
# Toggle Claude Code audio notifications
# Usage: claude-mute          (toggle)
#        claude-mute mute     (mute audio)
#        claude-mute unmute   (unmute audio)
#        claude-mute status   (check state)

QUIET_FILE="$HOME/.claude-quiet"

case "${1:-toggle}" in
    mute)
        touch "$QUIET_FILE"
        echo "🔇 Audio muted"
        ;;
    unmute)
        rm -f "$QUIET_FILE"
        echo "🔊 Audio unmuted"
        ;;
    toggle)
        if [[ -f "$QUIET_FILE" ]]; then
            rm -f "$QUIET_FILE"
            echo "🔊 Audio unmuted"
        else
            touch "$QUIET_FILE"
            echo "🔇 Audio muted"
        fi
        ;;
    status)
        if [[ -f "$QUIET_FILE" ]]; then
            echo "🔇 Audio: MUTED"
        else
            echo "🔊 Audio: UNMUTED"
        fi
        ;;
    *)
        echo "Usage: claude-mute [on|off|toggle|status]"
        echo ""
        echo "  on      - Mute audio (banners still show)"
        echo "  off     - Unmute audio"
        echo "  toggle  - Switch between muted/unmuted"
        echo "  status  - Show current state"
        exit 1
        ;;
esac
