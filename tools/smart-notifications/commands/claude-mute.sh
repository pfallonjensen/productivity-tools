#!/bin/bash
# Toggle Claude Code audio notifications on/off
# Usage: claude-mute        (toggle - mute/unmute)
#        claude-mute on     (mute audio for meetings)
#        claude-mute off    (unmute audio)
#        claude-mute status (check state)
#        claude-mute force  (force audio ON even when muted)

QUIET_FILE="$HOME/.claude-quiet"
FORCE_FILE="$HOME/.claude-force-audio"

case "${1:-toggle}" in
    on)
        touch "$QUIET_FILE"
        rm -f "$FORCE_FILE"
        echo "🔇 Claude audio muted"
        ;;
    off)
        rm -f "$QUIET_FILE"
        rm -f "$FORCE_FILE"
        echo "🔊 Claude audio unmuted"
        ;;
    force)
        touch "$FORCE_FILE"
        rm -f "$QUIET_FILE"
        echo "⚡ Force mode ACTIVE"
        echo "   Audio will play even when manually muted"
        echo "   Run '/session-audio off' to return to normal"
        ;;
    toggle)
        if [[ -f "$QUIET_FILE" ]]; then
            rm -f "$QUIET_FILE"
            rm -f "$FORCE_FILE"
            echo "🔊 Claude audio unmuted"
        else
            touch "$QUIET_FILE"
            rm -f "$FORCE_FILE"
            echo "🔇 Claude audio muted"
        fi
        ;;
    status)
        # Show current state
        if [[ -f "$FORCE_FILE" ]]; then
            echo "⚡ Audio: FORCE ON (always plays)"
        elif [[ -f "$QUIET_FILE" ]]; then
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
