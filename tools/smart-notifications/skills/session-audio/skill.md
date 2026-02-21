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
- `/session-audio on` — mute audio (for meetings)
- `/session-audio off` — unmute audio (return to normal)
- `/session-audio force` — force audio ON (plays even when muted - for important brainstorm sessions)
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

**User: `/session-audio on`**
→ Run: `$HOME/.claude/commands/claude-mute.sh on`
→ Show confirmation message

**User: `/session-audio off`**
→ Run: `$HOME/.claude/commands/claude-mute.sh off`
→ Show confirmation message

**User: `/session-audio toggle`**
→ Run: `$HOME/.claude/commands/claude-mute.sh toggle`
→ Show confirmation message

That's it. The command does all the work.
