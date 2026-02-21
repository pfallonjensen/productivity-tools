# Installation Guide - Meeting Transcript Automation

> **Complete step-by-step guide to set up meeting transcript syncing**

---

## Overview

This guide will help you set up automatic syncing of Google Meet transcripts from Google Drive to your Obsidian vault.

**Time Required**: ~15-20 minutes
**Difficulty**: Intermediate (requires terminal commands)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Google Meet with recording enabled
- [ ] Google Apps Script converting transcripts to `.txt` (see System 1 setup)
- [ ] Google Drive Desktop installed and syncing
- [ ] Obsidian vault on your Mac
- [ ] Terminal access (macOS)

---

## Step 1: Configure Folder Paths

### A. Find Your Google Drive Path

Your Google Drive transcripts folder should be at:
```
/Users/YOUR_USERNAME/Library/CloudStorage/GoogleDrive-YOUR_EMAIL/My Drive/Meeting Transcripts as Text
```

**Verify it exists:**
```bash
ls -la "/Users/$USER/Library/CloudStorage/"
```

Look for a folder like: `GoogleDrive-yourname@gmail.com`

### B. Find Your Obsidian Vault Path

Your Obsidian vault is likely at:
```
/Users/YOUR_USERNAME/Obsidian Vault
```

**Verify:**
```bash
ls -la ~/ | grep Obsidian
```

### C. Update the Script

1. Open `scripts/sync-transcripts.sh`
2. Update these lines with YOUR paths:

```bash
GOOGLE_DRIVE_SOURCE="/Users/YOUR_USERNAME/Library/CloudStorage/GoogleDrive-YOUR_EMAIL/My Drive/Meeting Transcripts as Text"
OBSIDIAN_DEST="/Users/YOUR_USERNAME/Obsidian Vault/Meeting Transcripts"
LOG_FILE="/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log"
```

---

## Step 2: Create Folder Structure

### Create automation folder in your vault:

```bash
mkdir -p ~/Obsidian\ Vault/Automations/meeting-transcript-system
```

### Create transcripts folder:

```bash
mkdir -p ~/Obsidian\ Vault/Meeting\ Transcripts
```

---

## Step 3: Copy Files

### Copy the sync script:

```bash
cp scripts/sync-transcripts.sh ~/Obsidian\ Vault/Automations/meeting-transcript-system/
```

### Make it executable:

```bash
chmod +x ~/Obsidian\ Vault/Automations/meeting-transcript-system/sync-transcripts.sh
```

---

## Step 4: Configure LaunchAgent

### A. Update the plist file

1. Open `config/com.obsidian.synctranscripts.plist`
2. Update the path to match YOUR username:

```xml
<string>/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/sync-transcripts.sh</string>
```

And:

```xml
<string>/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log</string>
```

### B. Copy to LaunchAgents:

```bash
cp config/com.obsidian.synctranscripts.plist ~/Library/LaunchAgents/
```

### C. Load the LaunchAgent:

```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

---

## Step 5: Test

### Run manually to test:

```bash
~/Obsidian\ Vault/Automations/meeting-transcript-system/sync-transcripts.sh
```

**Expected output:**
```
✓ Sync completed successfully. Files transferred: X
```

### Check the log:

```bash
cat ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log
```

### Verify files appeared:

```bash
ls ~/Obsidian\ Vault/Meeting\ Transcripts/
```

---

## Step 6: Verify Automation

### Check if LaunchAgent is running:

```bash
launchctl list | grep obsidian
```

You should see: `com.obsidian.synctranscripts`

### Wait for next :30 mark

The script runs hourly at :30 (1:30, 2:30, 3:30, etc.)

After the next :30, check the log again to see if it ran automatically.

---

## Configuration Options

### Change Sync Frequency

Edit the plist file and change the minute value:

```xml
<key>StartCalendarInterval</key>
<array>
    <dict>
        <key>Minute</key>
        <integer>30</integer>  <!-- Change this! -->
    </dict>
</array>
```

After editing, reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
launchctl load ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

---

## Troubleshooting

### Script says "Directory not found"

**Check Google Drive Desktop is running:**
```bash
ls -la ~/Library/CloudStorage/
```

If you don't see your Google Drive folder, start Google Drive Desktop.

### Files not syncing

**Check the log for errors:**
```bash
tail -20 ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log
```

### LaunchAgent not running

**Reload it:**
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
launchctl load ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

**Check for errors:**
```bash
launchctl list | grep obsidian
```

---

## Uninstallation

If you want to remove this automation:

### 1. Stop the LaunchAgent:
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

### 2. Remove files:
```bash
rm ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
rm -rf ~/Obsidian\ Vault/Automations/meeting-transcript-system/
```

### 3. (Optional) Remove transcript files:
```bash
rm -rf ~/Obsidian\ Vault/Meeting\ Transcripts/
```

---

## Next Steps

After installation:

1. ✅ Let it run for a day to verify it's working
2. ✅ Set up your backup system (to push transcripts to GitHub)
3. ✅ Use Claude Code to analyze transcripts
4. ✅ Build custom workflows for meeting synthesis

---

## Integration with Backup System

This automation works great with the **obsidian-backup-system**:

1. Transcripts sync to Obsidian hourly (this system)
2. Obsidian backs up to GitHub daily at 3 AM (backup system)
3. Result: Meeting → GitHub in <24 hours

See: `../obsidian-backup-system/` for backup setup.

---

*Installation complete! Your transcripts will now sync automatically.*
