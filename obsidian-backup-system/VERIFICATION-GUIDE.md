# Obsidian Vault Backup - Verification Guide

## Quick Reference: Where Everything Is

### Code Files
- **Backup Script:** `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/auto-backup.sh`
  - This is the actual code that runs every night at 3 AM
  - You can view it in Obsidian or any text editor

- **Scheduler Config:** `/Users/fallonjensen/Library/LaunchAgents/com.obsidian.autobackup.plist`
  - This tells macOS to run the backup script at 3 AM
  - It's an XML file that macOS LaunchAgent uses

### Documentation
- **Main Guide:** `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/README.md`
  - Complete documentation for the backup system
  - How to customize, troubleshoot, and manage backups

- **Git Reference:** `/Users/fallonjensen/Obsidian Vault/Git-Quick-Reference.md`
  - Quick git commands
  - Automated backup section
  - General git workflow help

### Logs (Proof of Execution)
- **Success Log:** `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup.log`
  - Shows every successful backup with timestamp
  - Shows account switching messages

- **Error Log:** `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup-error.log`
  - Only contains messages if something goes wrong
  - Check this if backups aren't working

---

## How to Verify It's Set Up Correctly

### 1. Check if LaunchAgent is Loaded and Running
```bash
launchctl list | grep obsidian
```

**What you should see:**
```
-	0	com.obsidian.autobackup
```

If you see this, it's loaded and will run at 3 AM.

### 2. Check the Schedule
```bash
cat ~/Library/LaunchAgents/com.obsidian.autobackup.plist | grep -A 3 "Hour"
```

**What you should see:**
```
<key>Hour</key>
<integer>3</integer>
<key>Minute</key>
<integer>0</integer>
```

This confirms it's set to run at 3:00 AM.

### 3. View the Backup Script
```bash
cat "/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/auto-backup.sh"
```

This shows you the actual code that will execute.

---

## How to Confirm It Ran (Check After 3 AM)

### Method 1: Check the Backup Log
```bash
tail -20 "/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup.log"
```

**What you'll see if it ran successfully:**
```
[main abc1234] Auto-backup: 2025-11-18 03:00:15
✓ Successfully backed up to GitHub at 2025-11-18 03:00:15
✓ Restored work account (fallonjensen-Daybreak)
```

**Or if no changes:**
```
✓ No changes to commit
```

### Method 2: Check GitHub
Visit: https://github.com/pfallonjensen/obsidian-vault

Look at the commit history - you'll see automatic commits with timestamps around 3 AM.

### Method 3: Check Git Locally
```bash
cd "/Users/fallonjensen/Obsidian Vault"
git log --oneline -5
```

You'll see commits like:
```
abc1234 Auto-backup: 2025-11-18 03:00:15
def5678 Auto-backup: 2025-11-17 03:00:12
```

---

## Daily Verification Routine (Optional)

After 3 AM each day, you can run this one-liner to check if backup worked:

```bash
tail -3 "/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup.log"
```

Or check if today's backup is on GitHub:
```bash
cd "/Users/fallonjensen/Obsidian Vault" && git log -1 --format="%h - %s (%ar)"
```

---

## Manual Test (Run It Now)

To test the backup right now and see it work:

```bash
"/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/auto-backup.sh"
```

Watch the output - you'll see it commit, push, and handle account switching.

---

## Troubleshooting

### LaunchAgent Not Loaded?
```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Want to See When It Will Run Next?
Unfortunately, macOS doesn't show this easily. But you know it's scheduled for 3 AM daily.

### Stop Automatic Backups
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Start Automatic Backups Again
```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

---

## Quick Command Cheatsheet

| What You Want | Command |
|---------------|---------|
| See if it's running | `launchctl list \| grep obsidian` |
| Check latest backup | `tail -5 ~/Obsidian\ Vault/Scripts/backup.log` |
| Run backup now | `~/Obsidian\ Vault/Scripts/auto-backup.sh` |
| View script code | `cat ~/Obsidian\ Vault/Scripts/auto-backup.sh` |
| Check GitHub | Visit https://github.com/pfallonjensen/obsidian-vault |
| Stop automation | `launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist` |
| Start automation | `launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist` |

---

## Where to Find This Guide

This file is located at:
**`/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/VERIFICATION-GUIDE.md`**

You can also find it in Obsidian under the `Scripts` folder.

Or open it from terminal:
```bash
open "/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/VERIFICATION-GUIDE.md"
```

---

*Last Updated: 2025-11-17*
