# Claude Code Session Memory System

> **Never lose your Claude Code conversation context from crashes - automatic backups every 15 minutes with one-command recovery**
>
> **NEW in v1.1**: Now includes plan file backup and automatic plan-session linking!
>
> Version: 1.1
> Last Updated: 2025-12-13

---

## What This Does

This session memory system:
1. **Backs up** all Claude Code sessions automatically every 15 minutes
2. **Preserves** complete conversation history (messages, tool calls, thinking, file changes)
3. **Backs up plan files** from `~/.claude/plans/` (structured implementation plans)
4. **Links plans to sessions** - automatically maps which plans were used in which sessions
5. **Exports** sessions to readable markdown for easy restoration, **including plan content**
6. **Enables** one-command recovery (`/backup-restore`) after crashes
7. **Integrates** with your Obsidian vault for long-term session archiving

---

## Why We Use This

**Problem**: Windsurf/Claude Code crashes lose your entire conversation context, forcing you to rebuild context manually.

**Solution**: Automatic session backups every 15 minutes + instant clipboard restore workflow.

**Result**: Never lose work. Crash → restore → continue in <30 seconds.

---

## Prerequisites

Before using this system:

✅ **macOS** 10.15 or later with LaunchAgent support
✅ **Claude Code** installed and working
✅ **Obsidian Vault** (or any directory for backups)
✅ **jq** installed (`brew install jq`) for JSON parsing
✅ **500 MB** free disk space for backups

---

## What's Included

```
claude-session-memory-system/
├── README.md (this file)
├── INSTALLATION-GUIDE.md (detailed setup + verification)
├── USAGE-GUIDE.md (recovery workflows + troubleshooting)
├── scripts/
│   ├── backup-claude-sessions.sh (main backup script - now includes plans!)
│   ├── export-session-context.sh (JSONL → markdown converter - now includes plan content!)
│   └── quick-restore.sh (one-command recovery)
└── config/
    └── com.user.claude-session-backup.plist (LaunchAgent config)
```

### Backup Directory Structure

```
Claude Sessions/
├── conversations/          # Session JSONL files
├── history/               # History snapshots
├── plans/                 # Plan file backups (NEW!)
├── plan-session-maps/     # Plan-to-session mapping JSON (NEW!)
├── shell-snapshots/       # Shell environment
├── file-history/          # File change history
├── session-env/           # Session metadata
├── Restored Contexts/     # Exported markdown files
└── Recent-Activity.md     # Summary with plan info (enhanced!)
```

---

## Quick Start

1. **Install**: Follow [INSTALLATION-GUIDE.md](./INSTALLATION-GUIDE.md) (~10 min setup)
2. **Verify**: Confirm backups are running (instructions in installation guide)
3. **Use**: Run `/backup-restore` in Claude Code after any crash

---

## How It Works

**Backup Flow (Every 15 Minutes)**:
```
Claude Code (~/.claude/)
  ↓ (backup-claude-sessions.sh, 15 min)
Obsidian Vault (Claude Sessions folder)
  ↓ (JSONL conversation files)
Markdown Export (Restored Contexts folder)
  ↓ (quick-restore.sh, on demand)
Clipboard → New Claude Code Session
```

**Recovery Flow**:
```
1. Run: /backup-restore (in Claude Code)
2. Script: Backs up → Exports → Copies to clipboard
3. Start: New Claude Code terminal
4. Paste: Context (Cmd+V) + "Continue where we left off"
5. Done: Full context restored in seconds
```

**Key Features:**
- ✅ Automatic 15-minute backups (no manual intervention)
- ✅ Complete conversation history (messages, tool calls, thinking)
- ✅ **Plan file backup** - preserves `~/.claude/plans/` structured plans
- ✅ **Plan-session linking** - maps which plans were used in each session
- ✅ **Plan content in exports** - restored sessions include full plan context
- ✅ Smart retention (keeps 50 snapshots, 7 days of conversations)
- ✅ One-command restore (`/backup-restore`)
- ✅ Markdown export for easy reading
- ✅ tmux integration for crash-proof sessions
- ✅ Git integration (auto-backup to GitHub at 3 AM)

---

## System Requirements

- **OS**: macOS 10.15 or later
- **Tools**: bash, jq, pbcopy (all standard on macOS)
- **Storage**: ~50-100 MB per month of active usage
- **Claude Code**: Tested with Claude Code CLI
- **Disk Space**: 500 MB recommended for backups

---

## Live Version

This is the **packaged, shareable** version.

**Working version** (actively running on my system):
`/Users/fallonjensen/Obsidian Vault/Automations/claude-session-backup/`

**Fallon's Stats** (as of Dec 2024):
- 1,541 command history entries
- 331 conversation files backed up
- 888 history snapshots (50 retained)
- 691 KB current session file
- Zero context loss since implementation

---

## Related Systems

This automation works alongside:

1. **Obsidian Backup System** - Daily Git backup at 3 AM
2. **Claude Code** - Session data source (~/.claude/)
3. **tmux** - Optional crash-proof terminal sessions

Together, these create a complete context preservation pipeline: Sessions → Obsidian → GitHub.

---

## Documentation

- **[INSTALLATION-GUIDE.md](./INSTALLATION-GUIDE.md)** - Complete setup instructions with verification
- **[USAGE-GUIDE.md](./USAGE-GUIDE.md)** - Recovery workflows, troubleshooting, advanced usage

---

## Support

- **Logs**: Check `~/Obsidian Vault/Automations/claude-session-backup/backup.log`
- **Verification**: See INSTALLATION-GUIDE.md verification section
- **Troubleshooting**: See USAGE-GUIDE.md troubleshooting section
- **Recent Activity**: Check `~/Obsidian Vault/Claude Sessions/Recent-Activity.md`

---

## License

Personal/team use. Adapt freely for your own setup.

---

*This is a packaged, self-contained version ready for team onboarding and duplication*
