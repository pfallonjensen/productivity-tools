# Smart Notifications for Claude Code

Intelligent notification system that identifies which Claude Code session needs your attention and automatically mutes during meetings.

## The Problem

Running 10+ concurrent Claude Code sessions with default notifications:
- ❌ All notifications sound identical — no way to tell which session
- ❌ Notification storms when multiple sessions complete simultaneously
- ❌ Can't mute during meetings without terminal commands
- ❌ Subagent processes create notification noise

## The Solution

Multi-layer intelligent notification system:
- ✅ **Session identification** — hear the session name you set
- ✅ **Auto-mute during meetings** — detects mic in use
- ✅ **Manual mute control** — simple on/off toggle
- ✅ **Notification cooldown** — 15-min dedup per session
- ✅ **Subagent filtering** — only real alerts, not idle noise

## Installation

**One-line install:**
```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main/install.sh | bash
```

**Requirements:**
- macOS 10.13 or later
- Claude Code installed
- Python 3 (built into macOS)

**What gets installed:**
- Notification hooks in `~/.claude/hooks/`
- Session labeling skill in `~/.claude/skills/`
- Mute control command in `~/.claude/commands/`
- Hook configuration in `~/.claude/settings.json`

## Usage

### Label Your Sessions

From within any Claude Code session:
```
/session-name
```

Then provide a name like "trading analysis" or "DDS sprint work".

**What you'll hear:**
- Before: "Claude Code needs your attention"
- After: "Trading analysis — Waiting for input"

**Pro tip:** Type `/session-` and both session tools appear in autocomplete.

### Control Audio

**From within Claude Code:**
```
/session-audio          # Check status (interactive override)
/session-audio on       # Mute
/session-audio off      # Unmute
/session-audio toggle   # Switch
```

**From terminal:**
```bash
claude-mute            # Same options as above
claude-mute status     # Check state
```

**Example status output:**
```
🔊 Audio: UNMUTED
🎤 Mic: FREE (audio will play if unmuted)
```

### Override Mic Detection (Brainstorm Sessions)

When you're in a brainstorm or jam session and want notifications even though you're on a call:

```bash
$ claude-mute status

🔊 Audio: UNMUTED
🎤 Mic: IN USE (audio currently suppressed)

Want notifications during this meeting? (y/n): y

✓ Override active - you'll hear notifications during meetings
  Run 'claude-mute off' to return to normal
```

**The tool discovers itself** — when mic blocks audio, status command offers to override. No flags to remember.

**Return to normal:**
```bash
claude-mute off     # Clears override and manual mute
```

Or run `status` again after the meeting — it will suggest disabling override when mic becomes free.

### How It Works

**Audio plays only when ALL conditions are met:**
1. ✅ Manual mute OFF
2. ✅ Mic not in use (no Zoom/Teams/Meet) OR force override active
3. ✅ Not a subagent idle reminder
4. ✅ Not within 15-min cooldown

**Notification banners always show** — only audio is controlled.

## Troubleshooting

**"claude-mute: command not found"**

Open a new terminal or run:
```bash
source ~/.zshrc
```

**"No audio even when unmuted"**

Check status:
```bash
claude-mute status
```

If mic shows "IN USE", you're in a meeting or recording. If "FREE", check `~/.claude-quiet` doesn't exist.

**"Session name not announced"**

Check if session is labeled:
```
/session-name
```

If unlabeled, it will say "Session 322fe521" (truncated ID).

**"Still getting notification storms"**

Restart all Claude Code sessions — they need to reload the new hooks.

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main/install.sh | bash -s uninstall
```

Removes all files except session labels (prompts before deleting).

## How It Works (Technical)

**Architecture:**

1. **notify.sh** — Unified hook handler (Notification + Stop events)
   - Reads JSON from stdin (Claude Code hook format)
   - Filters subagent idle noise
   - Checks 15-min cooldown per session
   - Resolves session name (3-tier lookup)
   - Always shows macOS banner
   - Conditionally plays audio (manual mute + mic-check)

2. **mic-check** — Python CoreAudio wrapper
   - Uses ctypes to call `AudioObjectGetPropertyData`
   - Checks `kAudioDevicePropertyDeviceIsRunningSomewhere`
   - Returns "in_use" or "free" to stdout

3. **claude-mute.sh** — Simple toggle script
   - Creates/removes `~/.claude-quiet` file
   - Shows combined manual + mic status

4. **session-name skill** — Session labeling
   - Auto-detects session ID from JSONL files
   - Writes to `~/.claude/session-labels/{uuid}`

5. **session-audio skill** — Audio control from within Claude Code
   - Wraps claude-mute.sh command
   - Works from any session (global setting)

**Session name resolution priority:**
1. Session labels (`~/.claude/session-labels/{uuid}`)
2. sessions-index.json customTitle/summary
3. Fallback: truncated session ID

## Files Modified

- `~/.claude/settings.json` — adds Notification + Stop hooks
- `~/.zshrc` (optional) — adds claude-mute alias
- `~/.claude/session-labels/` — created for label storage

## License

MIT License - use freely, no warranty provided.
