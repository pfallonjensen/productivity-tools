---
name: name-session
description: Label the current session for audio notifications — you'll hear this name when the session needs attention
user_invocable: true
---

# Name Session

Label this session so audio notifications say its name instead of a generic ID.

## Instructions

### Usage:
- `/name-session` — check current label (if no args provided)
- `/name-session <name>` — set label to `<name>`

### Steps:

1. **Find this session's ID:**
   ```bash
   grep -l "name-session" ~/.claude/projects/-Users-fallonjensen-Obsidian-Vault/*.jsonl 2>/dev/null | xargs ls -t | head -1
   ```
   Extract the UUID from the filename (everything between the last `/` and `.jsonl`).

   If that doesn't work, use the most recently modified JSONL and confirm by grepping for a unique string from the conversation.

2. **If no argument provided → CHECK mode:**
   ```bash
   if [[ -f "$HOME/.claude/session-labels/SESSION_UUID" ]]; then
       echo "✓ This session is labeled: \"$(cat "$HOME/.claude/session-labels/SESSION_UUID")\""
   else
       echo "✗ This session has no label yet"
   fi
   ```
   Then ask: "What would you like to name it?"

3. **If argument provided → SET mode:**
   Create `~/.claude/session-labels/` if needed, then:
   ```bash
   echo "THE_NAME" > ~/.claude/session-labels/SESSION_UUID
   ```

4. **Confirm:** `✓ Labeled: "THE_NAME"`
