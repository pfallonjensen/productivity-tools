# Productivity Tools

Collection of automation systems and productivity enhancements for development workflows.

## Available Tools

### 🔔 Smart Notifications (Claude Code)

Intelligent notification system for Claude Code with session identification and mute control.

**Features:**
- 🏷️ Session identification (hear which session needs attention)
- 🔇 Simple mute/unmute control
- ⏱️ Notification storm prevention (15-min cooldown)
- 🤖 Subagent noise filtering

**Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/pfallonjensen/productivity-tools/main/install.sh | bash
```

**[Full Documentation →](tools/smart-notifications/README.md)**

---

### 💾 Claude Session Memory System (Claude Code)

Session backup and restore system for Claude Code.

**[Documentation →](claude-session-memory-system/)**

---

### 📝 Meeting Transcript System

Automatic sync of Google Meet transcripts from Google Drive to local folders.

**What it does:**
- Syncs `.txt` transcripts from Google Drive
- Runs hourly via LaunchAgent (macOS)
- Preserves structure and timestamps

**[Documentation →](meeting-transcript-system/README.md)**

---

### 🔄 Obsidian Backup System

Automatic Git backup system for Obsidian vaults.

**What it does:**
- Daily automated commits and push to GitHub
- Runs at 3 AM via LaunchAgent (macOS)
- Handles large vaults efficiently

**[Documentation →](obsidian-backup-system/README.md)**

---

### 🐛 Bug & Enhancement Tracker (Claude Code)

Lightweight ticket system for tracking bugs and enhancements in any Claude Code project.

**Features:**
- 📋 Structured tickets with session context (resume in any future session)
- 🏷️ Category-prefixed naming for easy filtering
- 💬 Conversational intake via `/log-bug` and `/log-enh` skills
- 🔍 `/review-tickets` — see all open tickets grouped by category

**Installation:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/pfallonjensen/productivity-tools/main/tools/bug-tracker/install.sh)
```

**[Full Documentation →](tools/bug-tracker/README.md)**

---

### 📋 Action Item Extractor

Semantic extraction of action items from meetings and Slack using high-leverage filtering.

**What it does:**
- Extracts action items from meeting transcripts and Slack threads
- VP/PM hybrid theme filtering (only high-leverage work)
- Smart reply detection (skips threads where you already responded)
- Outputs to Obsidian task dashboard

**[Documentation →](action-item-extractor/README.md)**

---

## Installation

Each tool has its own installation method. See tool-specific documentation for details.

## Contributing

Personal productivity tools I've built for my workflows. Feel free to fork and adapt.

## License

MIT License - use freely, no warranty provided.
