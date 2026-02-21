# Open-Source Projects

This folder contains **PUBLIC-READY** versions of automations and scripts that can be shared publicly.

## What This Is

- 📦 **Shareable**: Documented, self-contained packages
- 🌐 **Public-Ready**: Can be turned into public repos
- 📚 **Documented**: Complete installation guides and documentation
- 🔄 **Portable**: Can be used to set up on other machines

## vs. /Automations/ Folder

| Folder | Purpose | Status |
|--------|---------|--------|
| `/Automations/` | Live, working scripts that run on this system | 🔴 ACTIVE |
| `/Open-Source/` | Documented, shareable versions for others | 📦 PACKAGED |

**Think of it like this:**
- `/Automations/` = Your actual running code (don't break it!)
- `/Open-Source/` = Snapshots/packages you can share or use to set up elsewhere

## Current Projects

### meeting-transcript-system/
**Description:** Automatic sync of Google Meet transcripts from Google Drive to Obsidian

**What's Included:**
- Sync script (rsync-based, hourly automation)
- LaunchAgent configuration for macOS
- Complete installation guide
- START-HERE quick reference
- All documentation

**Use Cases:**
1. Set up on another Mac (follow INSTALLATION-GUIDE.md)
2. Share with others (already documented!)
3. Integrate with backup system for full pipeline

**Live Version:** `/Automations/meeting-transcript-system/`

---

### obsidian-backup-system/
**Description:** Automatic backup system for Obsidian vaults to GitHub

**What's Included:**
- Complete working backup script
- LaunchAgent configuration for macOS
- Installation guide with actual paths
- Guide for making it public
- All documentation

**Use Cases:**
1. Set up on another Mac (follow INSTALLATION-GUIDE.md)
2. Share with others (already documented!)
3. Make a public GitHub repo (follow docs/MAKING-IT-PUBLIC.md)

**Live Version:** `/Automations/obsidian-backup-system/`

---

### smart-notifications/
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

**Live Version:** `~/.claude/hooks/` + `~/.claude/skills/name-session/`

---

## How These Work Together

**Complete Automation Pipeline:**
```
Google Meet Recording
  ↓ (Google Apps Script, 15 min)
Google Drive (.txt files)
  ↓ (meeting-transcript-system, hourly)
Obsidian Vault
  ↓ (obsidian-backup-system, daily 3 AM)
GitHub (private repo)
```

**Result**: Meetings automatically documented and backed up in <24 hours!

---

## How This Works

### Workflow:

1. **Create automation** in `/Automations/` - build and test your script
2. **Package it** for `/Open-Source/` - when it works, create a documented copy here
3. **Share** or **duplicate** - use this version to share or set up elsewhere

### Adding a New Project

When you create a new automation and want to share it:

1. Build and test in `/Automations/[project-name]/`
2. Create package structure:
   ```
   Open-Source/[project-name]/
   ├── README.md
   ├── INSTALLATION-GUIDE.md
   ├── scripts/
   │   └── [your-script].sh
   ├── config/
   │   └── [config-files]
   └── docs/
       └── MAKING-IT-PUBLIC.md (optional)
   ```
3. Document with your actual paths (for self-reference)
4. Add genericization guide for making it public

---

## Projects Ready for Public Release

Check each project's `docs/MAKING-IT-PUBLIC.md` to see how to convert it for public sharing.

### Steps to Make Public:

1. Copy project folder outside this vault
2. Genericize paths (replace your username with placeholders)
3. Remove personal information
4. Create public GitHub repo
5. Share with community!

---

## Benefits

✅ **Backup of your working setup** - Documented snapshots of what's working
✅ **Easy duplication** - Set up on new machines quickly
✅ **Shareable** - Help others with working examples
✅ **Portfolio** - Show off your automation skills

---

*This folder is for sharing and documentation - edit freely!*
