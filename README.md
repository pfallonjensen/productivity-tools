# Claude Code Tools

Productivity enhancements and custom skills for [Claude Code](https://claude.com/claude-code).

## Available Tools

### 🔔 Smart Notifications
**Description:** Intelligent notification system for Claude Code with session identification and auto-mute

**What's Included:**
- Unified notification hook (handles Notification + Stop events)
- Mic-in-use detection (Python CoreAudio wrapper)
- Manual mute/unmute control command
- Session labeling skill
- One-line installer with auto-config

**Features:**
- 🏷️ Session identification (hear which session needs attention)
- 🎤 Auto-mute during meetings (mic-in-use detection)
- 🔇 Manual mute control
- ⏱️ Notification storm prevention (15-min cooldown)
- 🤖 Subagent noise filtering

**Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main/install.sh | bash
```

**Full Documentation:** [tools/smart-notifications/README.md](tools/smart-notifications/README.md)

**Documentation:** [Full README →](tools/smart-notifications/README.md)

---

### 💾 Claude Session Memory System

Session backup and restore system for Claude Code.

**Documentation:** See `claude-session-memory-system/` directory

---

## Installation

Each tool has its own installation method. See tool-specific documentation for details.

**Uninstall:**
```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main/install.sh | bash -s uninstall
```

## Contributing

Personal productivity tools for Claude Code. Feel free to fork and adapt.

## License

MIT License - use freely, no warranty provided.
