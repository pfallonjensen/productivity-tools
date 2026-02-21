#!/bin/bash

# Claude Code Session Backup System
# Backs up all Claude Code session data to Obsidian Vault

set -euo pipefail

# Configuration
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/Obsidian Vault/Claude Sessions"
LOG_FILE="$HOME/Obsidian Vault/Automations/claude-session-backup/backup.log"
MAX_BACKUPS=50  # Keep last 50 backups

# Create backup directory structure
mkdir -p "$BACKUP_DIR"/{history,shell-snapshots,file-history,session-env,conversations,plans,plan-session-maps}
mkdir -p "$(dirname "$LOG_FILE")"

# Timestamp for this backup
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

# Detect terminal session name
detect_session_name() {
    # Try tmux first
    if [ -n "${TMUX:-}" ]; then
        tmux display-message -p '#S' 2>/dev/null && return
    fi

    # Try to get from terminal title or process name
    # Check common environment variables
    if [ -n "${TERM_SESSION_NAME:-}" ]; then
        echo "$TERM_SESSION_NAME" && return
    fi

    # Get parent process name (often shows terminal title)
    local parent_cmd=$(ps -o comm= -p $PPID 2>/dev/null | xargs basename 2>/dev/null)
    if [ -n "$parent_cmd" ] && [ "$parent_cmd" != "bash" ] && [ "$parent_cmd" != "zsh" ]; then
        echo "$parent_cmd" && return
    fi

    # Fallback: use current directory name
    basename "$(pwd)" 2>/dev/null || echo "default"
}

SESSION_NAME=$(detect_session_name | tr ' /' '_' | sed 's/[^a-zA-Z0-9_-]//g')
[ -z "$SESSION_NAME" ] && SESSION_NAME="default"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting Claude Code session backup... (Terminal: $SESSION_NAME)"

# Backup history.jsonl (chat history and commands)
if [ -f "$CLAUDE_DIR/history.jsonl" ]; then
    HISTORY_SIZE=$(wc -l < "$CLAUDE_DIR/history.jsonl")
    cp "$CLAUDE_DIR/history.jsonl" "$BACKUP_DIR/history/history-$TIMESTAMP.jsonl"

    # Also keep a "latest" copy for easy access
    cp "$CLAUDE_DIR/history.jsonl" "$BACKUP_DIR/history-latest.jsonl"

    log "✓ Backed up history.jsonl ($HISTORY_SIZE lines)"
else
    log "⚠ No history.jsonl found"
fi

# Backup shell snapshots (last 10 recent ones)
if [ -d "$CLAUDE_DIR/shell-snapshots" ]; then
    SNAPSHOT_COUNT=$(find "$CLAUDE_DIR/shell-snapshots" -name "*.sh" | wc -l | tr -d ' ')

    # Copy the 10 most recent snapshots
    find "$CLAUDE_DIR/shell-snapshots" -name "*.sh" -type f -print0 | \
        xargs -0 ls -t | \
        head -10 | \
        xargs -I {} cp {} "$BACKUP_DIR/shell-snapshots/"

    log "✓ Backed up recent shell snapshots ($SNAPSHOT_COUNT total)"
fi

# Backup file history
if [ -d "$CLAUDE_DIR/file-history" ]; then
    rsync -a --quiet "$CLAUDE_DIR/file-history/" "$BACKUP_DIR/file-history/"
    log "✓ Backed up file-history"
fi

# Backup session environment data (recent sessions)
if [ -d "$CLAUDE_DIR/session-env" ]; then
    find "$CLAUDE_DIR/session-env" -type f -mtime -7 -exec cp {} "$BACKUP_DIR/session-env/" \;
    log "✓ Backed up recent session-env data"
fi

# Backup FULL conversation history (this is the key for session recovery!)
if [ -d "$CLAUDE_DIR/projects" ]; then
    # Backup ALL conversation files from the last 7 days (these contain EVERYTHING)
    CONVERSATION_COUNT=$(find "$CLAUDE_DIR/projects" -name "*.jsonl" -mtime -7 | wc -l | tr -d ' ')

    if [ "$CONVERSATION_COUNT" -gt 0 ]; then
        # Copy recent conversation files, preserving directory structure
        find "$CLAUDE_DIR/projects" -name "*.jsonl" -mtime -7 -type f | while read -r file; do
            # Extract the project directory name and filename
            PROJECT_NAME=$(basename "$(dirname "$file")")
            FILENAME=$(basename "$file")

            # Create project subdirectory in backup
            mkdir -p "$BACKUP_DIR/conversations/$PROJECT_NAME"

            # Copy the file
            cp "$file" "$BACKUP_DIR/conversations/$PROJECT_NAME/"

            # Also create a timestamped archive of the most recent session
            if [ "$(stat -f %m "$file")" -gt "$(date -v-1H +%s)" ]; then
                # File modified in last hour - this is likely the current session
                # Remove old LATEST-SESSION files for this session ID
                rm -f "$BACKUP_DIR/conversations/LATEST-SESSION-"*"-$FILENAME" 2>/dev/null || true

                # Create new timestamped latest session file with terminal name
                cp "$file" "$BACKUP_DIR/conversations/LATEST-SESSION-${SESSION_NAME}-${TIMESTAMP}-$FILENAME"
            fi
        done

        log "✓ Backed up $CONVERSATION_COUNT conversation files (FULL CONTEXT)"

        # Find and highlight the most recent session
        LATEST_SESSION=$(find "$CLAUDE_DIR/projects" -name "*.jsonl" -type f -mtime -1 -exec ls -t {} + | head -1)
        if [ -n "$LATEST_SESSION" ]; then
            LATEST_SIZE=$(du -h "$LATEST_SESSION" | cut -f1)
            LATEST_NAME=$(basename "$LATEST_SESSION")
            log "  → Most recent: $LATEST_NAME ($LATEST_SIZE)"
        fi

        # Cleanup old LATEST-SESSION files (keep only the most recent for each session ID)
        # Group by session ID and remove older timestamped versions
        for session_id in $(ls "$BACKUP_DIR/conversations/LATEST-SESSION-"*".jsonl" 2>/dev/null | sed 's/.*LATEST-SESSION-[0-9_-]*-\(.*\)\.jsonl/\1/' | sort -u); do
            # Find all LATEST-SESSION files for this session ID, keep newest, delete rest
            ls -t "$BACKUP_DIR/conversations/LATEST-SESSION-"*"-${session_id}.jsonl" 2>/dev/null | tail -n +2 | xargs rm -f 2>/dev/null || true
        done
    fi
fi

# Backup plans directory (NEW - critical for session context!)
if [ -d "$CLAUDE_DIR/plans" ]; then
    PLAN_COUNT=$(find "$CLAUDE_DIR/plans" -name "*.md" -type f | wc -l | tr -d ' ')

    if [ "$PLAN_COUNT" -gt 0 ]; then
        # Copy all plan files
        rsync -a --quiet "$CLAUDE_DIR/plans/" "$BACKUP_DIR/plans/"
        log "✓ Backed up $PLAN_COUNT plan files"

        # Create plan-to-session mapping for recent conversations
        PLAN_MAP_FILE="$BACKUP_DIR/plan-session-maps/plan-mapping-$TIMESTAMP.json"
        TEMP_MAPPINGS=$(mktemp)

        # Build mappings - find conversation files and check each for plan references
        CONV_FILES=$(find "$CLAUDE_DIR/projects" -name "*.jsonl" -mtime -7 -type f 2>/dev/null || true)

        for conv_file in $CONV_FILES; do
            [ -f "$conv_file" ] || continue
            SESSION_ID=$(basename "$conv_file" .jsonl)

            # Extract unique plan references from this conversation
            PLAN_REFS=$(grep -oE '\.claude/plans/[a-zA-Z0-9_-]+\.md' "$conv_file" 2>/dev/null | sort -u || true)

            if [ -n "$PLAN_REFS" ]; then
                # Build plan array
                PLAN_ARRAY=""
                for plan in $PLAN_REFS; do
                    PLAN_NAME=$(basename "$plan" .md)
                    [ -n "$PLAN_ARRAY" ] && PLAN_ARRAY="$PLAN_ARRAY, "
                    PLAN_ARRAY="$PLAN_ARRAY\"$PLAN_NAME\""
                done
                echo "{\"session\": \"$SESSION_ID\", \"plans\": [$PLAN_ARRAY]}" >> "$TEMP_MAPPINGS"
            fi
        done

        # Generate final JSON
        {
            echo "{"
            echo '  "generated": "'$(date -Iseconds)'",'
            echo '  "mappings": ['
            if [ -s "$TEMP_MAPPINGS" ]; then
                # Add proper commas between entries
                sed 's/^/    /' "$TEMP_MAPPINGS" | sed '$ ! s/$/,/'
            fi
            echo "  ]"
            echo "}"
        } > "$PLAN_MAP_FILE"

        rm -f "$TEMP_MAPPINGS"

        # Also keep a latest copy
        cp "$PLAN_MAP_FILE" "$BACKUP_DIR/plan-session-maps/plan-mapping-latest.json"
        log "✓ Created plan-session mapping"
    fi
fi

# Create a human-readable summary of recent activity
SUMMARY_FILE="$BACKUP_DIR/Recent-Activity.md"
{
    echo "# Claude Code Recent Activity"
    echo ""
    echo "Last updated: $(date)"
    echo ""

    # NEW: Active Plans Section
    echo "## Active Plans"
    echo ""
    if [ -d "$CLAUDE_DIR/plans" ]; then
        RECENT_PLANS=$(find "$CLAUDE_DIR/plans" -name "*.md" -mtime -7 -type f 2>/dev/null)
        if [ -n "$RECENT_PLANS" ]; then
            echo "Plans modified in the last 7 days:"
            echo ""
            echo "| Plan Name | Last Modified | Size |"
            echo "|-----------|---------------|------|"
            for plan_file in $RECENT_PLANS; do
                PLAN_NAME=$(basename "$plan_file" .md)
                PLAN_DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$plan_file")
                PLAN_SIZE=$(du -h "$plan_file" | cut -f1)
                echo "| $PLAN_NAME | $PLAN_DATE | $PLAN_SIZE |"
            done
            echo ""
        else
            echo "No plans modified in the last 7 days."
            echo ""
        fi
    else
        echo "No plans directory found."
        echo ""
    fi

    # Plan-Session Mapping
    if [ -f "$BACKUP_DIR/plan-session-maps/plan-mapping-latest.json" ]; then
        echo "### Plan-Session Links"
        echo ""
        echo "Recent sessions with linked plans:"
        echo '```json'
        cat "$BACKUP_DIR/plan-session-maps/plan-mapping-latest.json" | jq -r '.mappings[:5]' 2>/dev/null || echo "[]"
        echo '```'
        echo ""
    fi

    echo "## Recent Commands"
    echo '```json'
    tail -20 "$CLAUDE_DIR/history.jsonl" 2>/dev/null | jq -s '.' || echo "[]"
    echo '```'
    echo ""
    echo "## Stats"
    echo "- Total history entries: $(wc -l < "$CLAUDE_DIR/history.jsonl" 2>/dev/null || echo "0")"
    echo "- Shell snapshots: $(find "$CLAUDE_DIR/shell-snapshots" -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')"
    echo "- Plan files: $(find "$CLAUDE_DIR/plans" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
    echo "- Latest backup: $(date)"
    echo ""
    echo "## Recovery Instructions"
    echo ""
    echo "If Claude Code crashes, you can review recent activity here."
    echo ""
    echo "To restore a session:"
    echo "1. Run \`/backup-restore\` in Claude Code"
    echo "2. Or manually: Review history-latest.jsonl for recent commands"
    echo "3. Check \`plans/\` for any active implementation plans"
    echo "4. Check shell-snapshots/ for environment state"
    echo "5. Review file-history/ for what files were changed"
    echo ""
    echo "**NEW**: Session exports now include linked plan content automatically!"
} > "$SUMMARY_FILE"

log "✓ Created activity summary"

# Cleanup old backups (keep last MAX_BACKUPS)
BACKUP_COUNT=$(find "$BACKUP_DIR/history" -name "history-*.jsonl" 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    find "$BACKUP_DIR/history" -name "history-*.jsonl" -type f -print0 | \
        xargs -0 ls -t | \
        tail -n +$((MAX_BACKUPS + 1)) | \
        xargs rm -f
    log "✓ Cleaned up old backups (kept $MAX_BACKUPS)"
fi

# Calculate session statistics
SESSION_COUNT=$(grep -c '"display"' "$CLAUDE_DIR/history.jsonl" 2>/dev/null || echo "0")
LAST_SESSION=$(tail -1 "$CLAUDE_DIR/history.jsonl" 2>/dev/null | jq -r '.display // "N/A"')

log "Session stats: $SESSION_COUNT commands total, last: $LAST_SESSION"
log "Backup complete! Saved to: $BACKUP_DIR"
