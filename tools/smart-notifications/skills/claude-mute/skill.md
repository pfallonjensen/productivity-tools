---
name: claude-mute
description: Control audio notifications globally (mute/unmute/status/override) from within Claude Code
user_invocable: true
---

# Claude Mute - Audio Control

Control Claude Code audio notifications from within any session.

## Instructions

Parse the argument and execute the corresponding mode:

### Usage:
- `/claude-mute` or `/claude-mute status` — show current state (interactive override if applicable)
- `/claude-mute on` — mute audio globally
- `/claude-mute off` — unmute audio globally (clears override too)
- `/claude-mute toggle` — switch between muted/unmuted

### Implementation:

Just call the command and show the output:

```bash
$HOME/.claude/commands/claude-mute.sh ${ARG:-status}
```

**For status mode with interactive prompts**, the script handles stdin automatically. Just run it and pass through any user responses.

### Examples:

**User: `/claude-mute`**
→ Run: `$HOME/.claude/commands/claude-mute.sh status`
→ If interactive prompt appears, let user respond

**User: `/claude-mute on`**
→ Run: `$HOME/.claude/commands/claude-mute.sh on`
→ Show confirmation message

**User: `/claude-mute off`**
→ Run: `$HOME/.claude/commands/claude-mute.sh off`
→ Show confirmation message

**User: `/claude-mute toggle`**
→ Run: `$HOME/.claude/commands/claude-mute.sh toggle`
→ Show confirmation message

That's it. The command does all the work.
