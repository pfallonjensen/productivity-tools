# Start Here - Meeting Transcript Automation

> **Quick overview and getting started guide**

---

## What is This?

An automation system that automatically syncs Google Meet transcripts from Google Drive to your Obsidian vault.

**In plain English:**
- You have a meeting → Google records it
- Google Apps Script converts transcript to `.txt`
- This automation copies it to Obsidian
- Your backup system pushes it to GitHub

**Result**: Zero manual work. Meetings automatically documented and backed up.

---

## The Complete System

This is **Part 2** of a 3-part automation chain:

```
[System 1]              [System 2 - YOU ARE HERE]           [System 3]
Google Apps Script  →   Meeting Transcript Sync         →   Obsidian Backup
(Every 15 min)          (Hourly at :30)                     (Daily 3 AM)
Converts transcripts    Copies to Obsidian                  Pushes to GitHub
```

---

## What's In This Package?

| File/Folder | Purpose |
|-------------|---------|
| `README.md` | Overview and description |
| `INSTALLATION-GUIDE.md` | Step-by-step setup instructions |
| `START-HERE.md` | This file - quick overview |
| `scripts/sync-transcripts.sh` | Main sync script |
| `config/com.obsidian.synctranscripts.plist` | macOS automation config |
| `docs/` | Additional documentation |

---

## Do I Need This?

**You need this if:**
- ✅ You use Google Meet with recordings
- ✅ You have an Obsidian vault
- ✅ You want automatic meeting documentation
- ✅ You want transcripts in Git for version control

**You might NOT need this if:**
- ❌ You don't record meetings
- ❌ You prefer manual documentation
- ❌ You don't use Obsidian

---

## What You Need Before Starting

1. **Google Apps Script** set up (System 1)
   - Converts meeting recordings to `.txt` files
   - Stores in Google Drive folder
   - Runs every 15 minutes

2. **Google Drive Desktop**
   - Syncs Google Drive to your Mac
   - Required for this script to access files

3. **Obsidian Vault**
   - On your Mac
   - With a folder for transcripts

4. **macOS with Terminal Access**
   - For running bash scripts
   - For launchd automation

---

## Quick Start

### 1. Read the Overview
- Understand what this does ✓ (you're doing it!)

### 2. Check Prerequisites
- Go through the list above
- Make sure you have everything

### 3. Follow Installation Guide
- Open `INSTALLATION-GUIDE.md`
- Follow step-by-step instructions
- Takes ~15-20 minutes

### 4. Test It
- Run script manually
- Verify files appear in Obsidian
- Wait for automatic run at :30

### 5. Verify Automation
- Check logs after first automatic run
- Confirm files are syncing

---

## How Often Does It Run?

**Default**: Every hour at :30 minutes past the hour

- 12:30 PM
- 1:30 PM
- 2:30 PM
- etc.

**Why :30?**
- Google Apps Script runs every 15 minutes
- This gives 15-30 minutes for conversion
- Then sync picks up new files

**Can I change it?**
Yes! Edit the `StartCalendarInterval` in the plist file.

---

## What Happens Automatically?

Once set up, this happens without you doing anything:

1. **You have a meeting** (Google Meet with recording)
2. **15-30 min later**: Google Apps Script converts to `.txt`
3. **By next :30**: This script copies to Obsidian
4. **Next day at 3 AM**: Backup script pushes to GitHub

**Total time**: Meeting → GitHub in <24 hours
**Your effort**: Zero ✨

---

## Important Paths to Know

### Source (Google Drive):
```
/Users/YOUR_USERNAME/Library/CloudStorage/GoogleDrive-YOUR_EMAIL/My Drive/Meeting Transcripts as Text
```

### Destination (Obsidian):
```
/Users/YOUR_USERNAME/Obsidian Vault/Meeting Transcripts
```

### Log File:
```
/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log
```

### LaunchAgent:
```
~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

---

## After Installation

### Check if it's running:
```bash
launchctl list | grep obsidian
```

### View recent activity:
```bash
tail -20 ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log
```

### Run manually:
```bash
~/Obsidian\ Vault/Automations/meeting-transcript-system/sync-transcripts.sh
```

---

## Common Questions

### "How much storage does this use?"
- Current: ~4-12 MB for 200+ transcripts
- Growth: ~5-10 MB per year
- Negligible for modern storage

### "What if I edit a transcript?"
- Script uses `rsync -u` (update)
- Only copies if source is newer
- Your edits in Obsidian are safe

### "Can I run it more/less frequently?"
- Yes! Edit the plist file
- Change the `Minute` value
- Reload launchd

### "What if Google Drive isn't syncing?"
- Script will log an error
- Check Google Drive Desktop is running
- Verify folder path in script

---

## Need Help?

1. **Installation Issues**: See INSTALLATION-GUIDE.md
2. **Script Errors**: Check transcript-sync.log
3. **LaunchAgent Problems**: Use `launchctl list | grep obsidian`
4. **Troubleshooting**: See docs/TROUBLESHOOTING.md

---

## Next: Install It!

Ready to set up? → **Open `INSTALLATION-GUIDE.md` and follow the steps**

---

*This automation is part of a larger system for automatic meeting documentation*
