---
name: session-audio
description: Control audio notifications globally (mute/unmute/status/override) from within Claude Code
user_invocable: true
---

# Session Audio Control

Control Claude Code audio notifications from within any session.

## Instructions

Parse the argument and execute the corresponding mode:

### Usage:
- `/session-audio` or `/session-audio status` — show current state
- `/session-audio mute` — mute audio
- `/session-audio unmute` — unmute audio
- `/session-audio toggle` — switch between muted/unmuted

### Implementation:

Just call the command and show the output:

```bash
$HOME/.claude/commands/claude-mute.sh ${ARG:-status}
```

**For status mode with interactive prompts**, the script handles stdin automatically. Just run it and pass through any user responses.

### Examples:

**User: `/session-audio`**
→ Run: `$HOME/.claude/commands/claude-mute.sh status`
→ If interactive prompt appears, let user respond

**User: `/session-audio mute`**
→ Run: `$HOME/.claude/commands/claude-mute.sh mute`
→ Show confirmation message

**User: `/session-audio unmute`**
→ Run: `$HOME/.claude/commands/claude-mute.sh unmute`
→ Show confirmation message

**User: `/session-audio toggle`**
→ Run: `$HOME/.claude/commands/claude-mute.sh toggle`
→ Show confirmation message

That's it. The command does all the work.
