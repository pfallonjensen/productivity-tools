# Obsidian Vault Automation Scripts

## Auto-Backup Script

### What It Does
Automatically commits and pushes your Obsidian Vault changes to GitHub.

### Manual Usage
Run anytime to backup your changes:
```bash
"/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/auto-backup.sh"
```

### Automatic Schedule
**Currently runs once daily at 3:00 AM**

The script is scheduled using macOS LaunchAgent and will run automatically every night at 3 AM. This timing ensures:
- Backups happen when you're not actively working
- No workflow interruption
- Your work is automatically backed up before you start each day

**Smart Account Switching:**
- If you're using your work account (fallonjensen-Daybreak), the script will temporarily switch to your personal account for the backup, then restore your work account
- If you're using your personal account (pfallonjensen), it will stay on the personal account
- This ensures the backup always works without disrupting your current workflow

### Checking If It's Running
```bash
launchctl list | grep obsidian
```

### View Backup Logs
```bash
# View successful backups
cat "/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup.log"

# View any errors
cat "/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup-error.log"
```

## Customizing the Schedule

### Change Backup Time
Edit the plist file:
```bash
nano ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

Change the Hour and Minute values:
- `Hour`: 0-23 (24-hour format, e.g., 18 = 6 PM)
- `Minute`: 0-59

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Run Multiple Times Per Day
Add multiple `StartCalendarInterval` entries. Example for 9 AM and 6 PM:
```xml
<key>StartCalendarInterval</key>
<array>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</array>
```

### Run Every Hour
Replace `StartCalendarInterval` with:
```xml
<key>StartInterval</key>
<integer>3600</integer>  <!-- 3600 seconds = 1 hour -->
```

## Managing the Automation

### Stop Automatic Backups
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Start Automatic Backups
```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Remove Automation Completely
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist
rm ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

## Troubleshooting

### Script doesn't run automatically
1. Check if it's loaded: `launchctl list | grep obsidian`
2. Check error log: `cat Scripts/backup-error.log`
3. Test manually: `./Scripts/auto-backup.sh`

### Push fails
- Check internet connection
- Verify GitHub authentication: `gh auth status`
- Re-authenticate if needed: `gh auth login`

### Want to test it right now?
```bash
launchctl start com.obsidian.autobackup
```

---

## Future Script Ideas
- Script to clean up old/duplicate files
- Script to organize notes by date
- Script to generate weekly summaries
- Script to backup to multiple locations
