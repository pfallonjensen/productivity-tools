#!/bin/bash

# Quick Restore - One-command session recovery for Claude Code

set -euo pipefail

echo "🔄 Claude Code Session Quick Restore"
echo ""

# Run backup to capture current state
echo "1. Backing up current session..."
"$HOME/Obsidian Vault/Automations/claude-session-backup/backup-claude-sessions.sh" 2>&1 | grep "✓"

echo ""
echo "2. Exporting to readable format..."

# Export the most recent session
"$HOME/Obsidian Vault/Automations/claude-session-backup/export-session-context.sh"

echo ""
echo "3. Finding most recent context file..."

# Find the most recent exported context
LATEST_CONTEXT=$(find "$HOME/Obsidian Vault/Claude Sessions/Restored Contexts" -name "*-context.md" -type f -exec ls -t {} + | head -1)

if [ -z "$LATEST_CONTEXT" ]; then
    echo "❌ No session context found!"
    exit 1
fi

echo "   Found: $(basename "$LATEST_CONTEXT")"
echo ""

# Get file stats
FILE_SIZE=$(du -h "$LATEST_CONTEXT" | cut -f1)
LINE_COUNT=$(wc -l < "$LATEST_CONTEXT")

echo "📊 Session Info:"
echo "   Size: $FILE_SIZE"
echo "   Lines: $LINE_COUNT"
echo ""

# Copy to clipboard
cat "$LATEST_CONTEXT" | pbcopy

echo "✅ Session context copied to clipboard!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start a new Claude Code terminal"
echo "2. Paste (Cmd+V) the context"
echo "3. Add this message:"
echo ""
echo "   'Please review this session history and continue where we left off.'"
echo ""
echo "───────────────────────────────────────────────────────────"
echo ""
echo "Or view the context file:"
echo "   open \"$LATEST_CONTEXT\""
echo ""
echo "Recent activity summary:"
echo "   open \"$HOME/Obsidian Vault/Claude Sessions/Recent-Activity.md\""
echo ""
