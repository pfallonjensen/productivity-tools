#!/bin/bash

# Export Claude Code Session to Readable Context
# Converts .jsonl session files into markdown that can be fed back to Claude
# Enhanced: Now includes plan files linked to the session

set -euo pipefail

# Configuration
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/Obsidian Vault/Claude Sessions"

# Get the session file (either passed as argument or find the most recent)
if [ $# -eq 0 ]; then
    SESSION_FILE=$(find "$HOME/Obsidian Vault/Claude Sessions/conversations" -name "LATEST-SESSION-*.jsonl" -type f -exec stat -f "%m %N" {} \; | sort -rn | head -1 | cut -d' ' -f2-)
    if [ -z "$SESSION_FILE" ]; then
        echo "Error: No LATEST-SESSION files found!"
        exit 1
    fi
    echo "No session file specified. Using most recent: $(basename "$SESSION_FILE")"
else
    SESSION_FILE="$1"
fi

if [ ! -f "$SESSION_FILE" ]; then
    echo "Error: Session file not found: $SESSION_FILE"
    exit 1
fi

# Output file
OUTPUT_DIR="$HOME/Obsidian Vault/Claude Sessions/Restored Contexts"
mkdir -p "$OUTPUT_DIR"

SESSION_NAME=$(basename "$SESSION_FILE" .jsonl)
OUTPUT_FILE="$OUTPUT_DIR/${SESSION_NAME}-context.md"

echo "Exporting session: $SESSION_NAME"
echo "Output: $OUTPUT_FILE"

# Extract plan references from the session file
extract_plan_refs() {
    local session_file="$1"
    # Pattern: match .claude/plans/[simple-filename].md (no spaces, slashes, or complex chars)
    grep -oE '\.claude/plans/[a-zA-Z0-9_-]+\.md' "$session_file" 2>/dev/null | \
        sed 's/.*\.claude\/plans\///' | \
        sed 's/\.md$//' | \
        sort -u
}

# Get plan file content if it exists
get_plan_content() {
    local plan_name="$1"
    local plan_file="$CLAUDE_DIR/plans/${plan_name}.md"
    local backup_plan_file="$BACKUP_DIR/plans/${plan_name}.md"

    if [ -f "$plan_file" ]; then
        cat "$plan_file"
    elif [ -f "$backup_plan_file" ]; then
        cat "$backup_plan_file"
    else
        echo "[Plan file not found: $plan_name]"
    fi
}

# Find linked plans
LINKED_PLANS=$(extract_plan_refs "$SESSION_FILE")
PLAN_COUNT=$(echo "$LINKED_PLANS" | grep -c . || echo "0")

echo "Found $PLAN_COUNT linked plan(s)"
echo ""

# Parse the JSONL and create a readable markdown conversation
{
    echo "# Claude Code Session Context"
    echo ""
    echo "**Session ID**: $SESSION_NAME"
    echo "**Exported**: $(date)"
    echo "**Original File**: $SESSION_FILE"
    echo "**Linked Plans**: $PLAN_COUNT"
    echo ""
    echo "---"
    echo ""

    # Include linked plan content FIRST (critical context!)
    if [ -n "$LINKED_PLANS" ] && [ "$PLAN_COUNT" -gt 0 ]; then
        echo "## Session Plans"
        echo ""
        echo "The following plan(s) were active during this session. This structured context is critical for understanding the work being done."
        echo ""

        for plan_name in $LINKED_PLANS; do
            echo "### Plan: $plan_name"
            echo ""
            echo "<details>"
            echo "<summary>Click to expand plan content</summary>"
            echo ""
            echo '```markdown'
            get_plan_content "$plan_name"
            echo '```'
            echo ""
            echo "</details>"
            echo ""
        done

        echo "---"
        echo ""
    fi

    echo "## Conversation History"
    echo ""
    echo "This is the complete conversation history that can be used to restore context."
    echo ""
    echo "---"
    echo ""

    # Process each line of the JSONL
    jq -r '
        # Skip file-history-snapshot entries
        if .type == "file-history-snapshot" then empty
        # Process user messages
        elif .type == "user" then
            if (.message.content | type) == "string" then
                "## User\n\n" + .message.content
            elif (.message.content | type) == "array" then
                "## User\n\n" + (.message.content | map(select(.type == "text") | .text) | join("\n\n"))
            else
                "## User\n\n[Complex message content]"
            end
        # Process assistant messages
        elif .type == "assistant" then
            if .message.content then
                # Extract text and tool uses
                (.message.content[] |
                    if .type == "text" then
                        "## Assistant\n\n" + .text
                    elif .type == "thinking" then
                        "## Assistant (Thinking)\n\n" + .thinking
                    elif .type == "tool_use" then
                        "## Assistant (Tool Use: " + .name + ")\n\n```json\n" + (.input | tojson) + "\n```"
                    else
                        empty
                    end
                )
            else
                empty
            end
        # Process tool results
        elif .type == "tool_result" then
            if .toolResult.output then
                "## Tool Result: " + (.toolUse.name // "unknown") + "\n\n```\n" + .toolResult.output + "\n```"
            else
                empty
            end
        else
            empty
        end
    ' "$SESSION_FILE" 2>/dev/null || {
        echo "Note: Some entries couldn't be parsed. Showing raw conversation..."
        echo ""
        jq -r 'select(.message.content) |
            if .type == "user" then
                "## User\n\n" + (.message.content // "")
            elif .type == "assistant" then
                "## Assistant\n\n" + (
                    if (.message.content | type) == "array" then
                        (.message.content[] | select(.type == "text") | .text)
                    else
                        (.message.content // "")
                    end
                )
            else
                empty
            end
        ' "$SESSION_FILE"
    }

    echo ""
    echo "---"
    echo ""
    echo "## Session Statistics"
    echo ""
    echo "- Total messages: $(wc -l < "$SESSION_FILE")"
    echo "- File size: $(du -h "$SESSION_FILE" | cut -f1)"
    echo "- Session ID: $SESSION_NAME"
    echo "- Linked plans: $PLAN_COUNT"
    if [ -n "$LINKED_PLANS" ] && [ "$PLAN_COUNT" -gt 0 ]; then
        echo "- Plan names: $(echo $LINKED_PLANS | tr '\n' ', ' | sed 's/,$//')"
    fi
    echo ""
    echo "## How to Use This Context"
    echo ""
    echo "To restore context in a new Claude Code session:"
    echo ""
    echo "1. Open a new Claude Code terminal"
    echo "2. Paste this file as context or reference it:"
    echo '   ```'
    echo "   Please read this file to understand our previous conversation:"
    echo "   $OUTPUT_FILE"
    echo '   ```'
    echo ""
    echo "3. Or use the Quick Restore command:"
    echo '   ```bash'
    echo "   cat \"$OUTPUT_FILE\" | pbcopy"
    echo '   ```'
    echo "   Then paste into Claude Code with: \"Please review this conversation history and continue where we left off\""
    echo ""

} > "$OUTPUT_FILE"

echo "✓ Session exported successfully!"
echo ""
echo "Output saved to:"
echo "$OUTPUT_FILE"
echo ""
echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "Lines: $(wc -l < "$OUTPUT_FILE")"
if [ -n "$LINKED_PLANS" ] && [ "$PLAN_COUNT" -gt 0 ]; then
    echo "Plans included: $PLAN_COUNT ($(echo $LINKED_PLANS | tr '\n' ', ' | sed 's/,$//'))"
fi
echo ""
echo "To copy to clipboard and restore:"
echo "  cat \"$OUTPUT_FILE\" | pbcopy"
