#!/bin/bash
# Claude Code Smart Notification Hook (unified)
# Handles: Notification + Stop events (via $1 argument)
# Features:
#   - Session name identification (session-labels → sessions-index → truncated ID)
#   - Subagent idle filtering (skip idle_prompt from subagent processes)
#   - Per-session idle cooldown (15 min between repeat idle notifications)
#   - Auto-suppresses audio when mic is in use (meeting detection)
#   - Manual mute via ~/.claude-quiet
#   - macOS notification banner (always shown)
#
# Toggle audio:  touch ~/.claude-quiet (mute) / rm ~/.claude-quiet (unmute)
# Set labels:    /name-session <name> (from within any Claude session)

EVENT_TYPE="${1:-notification}"  # "notification" or "stop"

# Read JSON input from stdin
INPUT=$(cat)

# Extract fields
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null)
MESSAGE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Needs attention'))" 2>/dev/null)
NOTIF_TYPE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('notification_type','unknown'))" 2>/dev/null)
TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('transcript_path',''))" 2>/dev/null)

# --- Subagent idle filter ---
# Subagent transcripts contain /subagents/ in the path
# Only filter idle_prompt — permission_prompt and elicitation_dialog still need attention
if [[ "$TRANSCRIPT_PATH" == *"/subagents/"* ]] && [[ "$NOTIF_TYPE" == "idle_prompt" ]]; then
    exit 0
fi

# --- Idle cooldown (15 min per session) ---
# Prevents notification storms when multiple idle sessions re-fire simultaneously
if [[ "$NOTIF_TYPE" == "idle_prompt" ]] && [[ -n "$SESSION_ID" ]]; then
    COOLDOWN_FILE="/tmp/claude-idle-${SESSION_ID:0:8}"
    NOW=$(date +%s)
    if [[ -f "$COOLDOWN_FILE" ]]; then
        LAST=$(cat "$COOLDOWN_FILE" 2>/dev/null)
        ELAPSED=$(( NOW - LAST ))
        if [[ $ELAPSED -lt 900 ]]; then  # 900s = 15 min
            exit 0
        fi
    fi
    echo "$NOW" > "$COOLDOWN_FILE"
fi

# --- Resolve session name (priority order) ---
SESSION_NAME=""

# 1. Our own label file (instant, set via /name-session)
if [[ -n "$SESSION_ID" ]] && [[ -f "$HOME/.claude/session-labels/$SESSION_ID" ]]; then
    SESSION_NAME=$(cat "$HOME/.claude/session-labels/$SESSION_ID")
fi

# 2. sessions-index.json customTitle or summary (covers older sessions)
if [[ -z "$SESSION_NAME" ]] && [[ -n "$SESSION_ID" ]]; then
    SESSION_NAME=$(python3 -c "
import json, glob, os
session_id = '$SESSION_ID'
for idx_file in glob.glob(os.path.join(os.path.expanduser('~/.claude/projects'), '*/sessions-index.json')):
    try:
        with open(idx_file) as f:
            data = json.load(f)
        for entry in data.get('entries', []):
            if entry.get('sessionId') == session_id:
                name = entry.get('customTitle') or entry.get('summary') or ''
                if name:
                    print(name)
                    exit(0)
    except:
        pass
" 2>/dev/null)
fi

# 3. Fallback: truncated session ID
if [[ -z "$SESSION_NAME" ]]; then
    SESSION_NAME="Session ${SESSION_ID:0:8}"
fi

# Truncate long names for audio (keep full for visual banner)
AUDIO_NAME="$SESSION_NAME"
if [[ ${#AUDIO_NAME} -gt 40 ]]; then
    AUDIO_NAME="${AUDIO_NAME:0:40}"
fi

# --- Determine type label ---
if [[ "$EVENT_TYPE" == "stop" ]]; then
    TYPE_LABEL="Finished"
else
    case "$NOTIF_TYPE" in
        permission_prompt)  TYPE_LABEL="Permission needed" ;;
        idle_prompt)        TYPE_LABEL="Waiting for input" ;;
        auth_success)       TYPE_LABEL="Auth complete" ;;
        elicitation_dialog) TYPE_LABEL="Question for you" ;;
        *)                  TYPE_LABEL="Needs attention" ;;
    esac
fi

# --- Visual notification (always) ---
osascript -e "display notification \"$TYPE_LABEL\" with title \"Claude: $SESSION_NAME\"" 2>/dev/null &

# --- Audio notification ---
# Play audio unless manually muted
if [[ ! -f "$HOME/.claude-quiet" ]]; then
    say "$AUDIO_NAME — $TYPE_LABEL" &
fi

exit 0
