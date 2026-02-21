#!/bin/bash
# Toggle Claude Code audio notifications on/off
# Usage: claude-mute        (toggle)
#        claude-mute on     (mute audio)
#        claude-mute off    (unmute audio)

QUIET_FILE="$HOME/.claude-quiet"

case "${1:-toggle}" in
    on)
        touch "$QUIET_FILE"
        echo "🔇 Claude audio muted (banners still show)"
        echo "   Mic-in-use detection still active"
        ;;
    off)
        rm -f "$QUIET_FILE"
        echo "🔊 Claude audio unmuted"
        ;;
    toggle)
        if [[ -f "$QUIET_FILE" ]]; then
            rm -f "$QUIET_FILE"
            echo "🔊 Claude audio unmuted"
        else
            touch "$QUIET_FILE"
            echo "🔇 Claude audio muted (banners still show)"
            echo "   Mic-in-use detection still active"
        fi
        ;;
    status)
        if [[ -f "$QUIET_FILE" ]]; then
            echo "🔇 Audio: MUTED (manual override active)"
        else
            echo "🔊 Audio: UNMUTED"
        fi
        MIC_STATUS=$("$HOME/.claude/hooks/mic-check" 2>/dev/null)
        if [[ "$MIC_STATUS" == "in_use" ]]; then
            echo "🎤 Mic: IN USE (audio auto-suppressed)"
        else
            echo "🎤 Mic: FREE (audio will play if unmuted)"
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
