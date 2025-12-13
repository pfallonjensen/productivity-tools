# Meeting Transcript Automation System

> **Automatically sync Google Meet transcripts from Google Drive to your Obsidian vault**
>
> Version: 1.0
> Last Updated: 2025-11-17

---

## What This Does

This automation system:
1. **Watches** Google Drive for meeting transcript `.txt` files
2. **Syncs** them to your Obsidian vault hourly
3. **Preserves** file timestamps and only copies new/updated files
4. **Logs** all activity for troubleshooting
5. **Runs automatically** in the background via macOS LaunchAgent

---

## Prerequisites

Before using this automation:

✅ **Google Meet** with recording and transcription enabled
✅ **Google Apps Script** converting transcripts to `.txt` files in Google Drive
✅ **Google Drive Desktop** installed and syncing
✅ **Obsidian** vault on your Mac
✅ **macOS** with LaunchAgent support

---

## What's Included

```
meeting-transcript-system/
├── README.md (this file)
├── INSTALLATION-GUIDE.md (detailed setup)
├── START-HERE.md (quick start)
├── scripts/
│   └── sync-transcripts.sh (main sync script)
├── config/
│   └── com.obsidian.synctranscripts.plist (LaunchAgent config)
└── docs/
    └── TROUBLESHOOTING.md (common issues)
```

---

## Quick Start

1. **Read**: [START-HERE.md](./START-HERE.md) for overview
2. **Follow**: [INSTALLATION-GUIDE.md](./INSTALLATION-GUIDE.md) for setup
3. **Run**: The script will sync automatically hourly at :30

---

## How It Works

```
Google Drive (Meeting Transcripts as Text)
  ↓ (rsync, hourly at :30)
Obsidian Vault (Meeting Transcripts folder)
  ↓ (via auto-backup.sh, daily 3 AM)
GitHub (private repo backup)
```

**Key Features:**
- ✅ Only syncs new or modified files
- ✅ Preserves file timestamps
- ✅ Runs automatically in background
- ✅ Logs all activity
- ✅ No manual intervention needed

---

## System Requirements

- **OS**: macOS 10.15 or later
- **Tools**: rsync (built-in), launchctl (built-in)
- **Storage**: ~5-10 MB per year of transcripts
- **Google Drive Desktop**: Required

---

## Live Version

This is the **packaged, shareable** version.

**Working version** (actively running on my system):
`/Users/fallonjensen/Obsidian Vault/Automations/meeting-transcript-system/`

---

## Related Systems

This automation works alongside:

1. **Google Apps Script** - Converts meeting recordings to `.txt` files
2. **Google Drive Desktop** - Syncs files to Mac
3. **Obsidian Backup** - Pushes vault to GitHub daily

Together, these create an end-to-end pipeline: Meeting → GitHub in <24 hours.

---

## Support

- **Documentation**: See INSTALLATION-GUIDE.md and TROUBLESHOOTING.md
- **Logs**: Check `transcript-sync.log` in your automation folder
- **Issues**: Review common problems in docs/TROUBLESHOOTING.md

---

## License

Personal use. Feel free to adapt for your own setup.

---

*This is a packaged, self-contained version ready for sharing or duplication*
