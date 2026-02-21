#!/bin/bash
# Toggle Claude Code audio notifications on/off
# Usage: claude-mute        (toggle)
#        claude-mute on     (mute audio)
#        claude-mute off    (unmute audio)
#        claude-mute status (check state, interactive override)

QUIET_FILE="$HOME/.claude-quiet"
FORCE_FILE="$HOME/.claude-force-audio"

case "${1:-toggle}" in
    on)
        touch "$QUIET_FILE"
        echo "🔇 Claude audio muted (banners still show)"
        echo "   Mic-in-use detection still active"
        ;;
    off)
        rm -f "$QUIET_FILE"
        rm -f "$FORCE_FILE"
        echo "🔊 Claude audio unmuted (respects mic-in-use)"
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
        # Show current state
        if [[ -f "$QUIET_FILE" ]]; then
            echo "🔇 Audio: MUTED (manual override active)"
        else
            echo "🔊 Audio: UNMUTED"
        fi

        if [[ -f "$FORCE_FILE" ]]; then
            echo "⚡ Override: ACTIVE (ignores mic-in-use)"
        fi

        MIC_STATUS=$("$HOME/.claude/hooks/mic-check" 2>/dev/null)
        if [[ "$MIC_STATUS" == "in_use" ]]; then
            echo "🎤 Mic: IN USE (audio currently suppressed)"

            # Interactive override prompt (only if not already forced and not manually muted)
            if [[ ! -f "$FORCE_FILE" ]] && [[ ! -f "$QUIET_FILE" ]]; then
                echo ""
                read -p "Want notifications during this meeting? (y/n): " -n 1 -r
                echo ""

                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    touch "$FORCE_FILE"
                    echo ""
                    echo "✓ Override active - you'll hear notifications during meetings"
                    echo "  Run 'claude-mute off' to return to normal"
                fi
            fi
        else
            echo "🎤 Mic: FREE (audio will play if unmuted)"

            # If force mode is active but mic is free, offer to disable it
            if [[ -f "$FORCE_FILE" ]]; then
                echo ""
                echo "Override is active but mic is free."
                read -p "Disable override and return to normal? (y/n): " -n 1 -r
                echo ""

                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -f "$FORCE_FILE"
                    echo ""
                    echo "✓ Returned to normal (will auto-suppress during meetings)"
                fi
            fi
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
