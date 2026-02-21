# Claude Code Tools

Collection of productivity tools and enhancements for [Claude Code](https://claude.com/claude-code).

## Available Tools

### 🔔 Smart Notifications

Intelligent notification system for Claude Code with:
- Session identification (hear which session needs attention)
- Auto-mute during meetings (mic-in-use detection)
- Manual mute/unmute control
- Notification storm prevention (15-min cooldown)
- Subagent noise filtering

**Install:**
```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main/install.sh | bash
```

**Requirements:** macOS 10.13+, Claude Code installed

**[Full Documentation →](tools/smart-notifications/README.md)**

---

## Installation

Each tool has its own installer. See tool-specific README for details.

**Uninstall any tool:**
```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/claude-code-tools/main/install.sh | bash -s uninstall
```

## Contributing

These are personal productivity tools I've built for my own use. Feel free to fork and adapt for your workflow.

## License

MIT License - use freely, no warranty provided.
