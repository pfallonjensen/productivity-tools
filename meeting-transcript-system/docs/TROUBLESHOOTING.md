# Troubleshooting - Meeting Transcript Automation

> **Common issues and solutions**

---

## Issue 1: Permission Errors (Exit Code 23)

### Symptom:
```
ERROR: Rsync failed with exit code 23
rsync: opendir "...Meeting Transcripts as Text/." failed: Operation not permitted (1)
```

### Causes:
1. **Google Drive Desktop Not Running**
   - The Google Drive folder isn't accessible because the app isn't syncing

2. **macOS Security Permissions**
   - Terminal/launchd doesn't have Full Disk Access

3. **Google Drive Still Syncing**
   - Files are locked while Google Drive is updating them

### Solutions:

**A. Check Google Drive Desktop:**
```bash
# Verify Google Drive folder is accessible
ls -la ~/Library/CloudStorage/
```

Make sure you see your Google Drive folder listed. If not, start Google Drive Desktop.

**B. Grant Full Disk Access:**
1. Open System Preferences → Security & Privacy → Privacy
2. Select "Full Disk Access" from the left sidebar
3. Add `/bin/bash` or the specific terminal app you're using
4. Restart the LaunchAgent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
   launchctl load ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
   ```

**C. Wait and Retry:**
- Sometimes Google Drive is temporarily locking files
- The error is usually transient
- Next scheduled run (at :30) will likely succeed

**D. Run Manually to Test:**
```bash
~/Obsidian\ Vault/Automations/meeting-transcript-system/sync-transcripts.sh
```

If manual run succeeds but LaunchAgent fails, it's a permissions issue.

---

## Issue 2: No Files Being Synced

### Symptom:
```
SUCCESS: Sync completed. Files transferred: 0
```

### Causes:
1. **All Files Already Synced**
   - Normal behavior when nothing has changed

2. **Wrong Source Path**
   - Script is looking in the wrong Google Drive folder

3. **No New Transcripts**
   - Google Apps Script hasn't created new transcripts yet

### Solutions:

**A. Verify Source Path:**
```bash
ls "/Users/$USER/Library/CloudStorage/GoogleDrive-YOUR_EMAIL/My Drive/Meeting Transcripts as Text/"
```

Replace `YOUR_EMAIL` with your actual email. You should see `.txt` files listed.

**B. Check Google Apps Script:**
1. Go to Google Apps Script project
2. Check execution log
3. Verify triggers are running (every 15 minutes)
4. Confirm transcripts are being created in Google Drive

**C. Force a New File:**
1. Create a test file in Google Drive source folder
2. Run sync manually
3. Check if it appears in Obsidian

---

## Issue 3: LaunchAgent Not Running

### Symptom:
```bash
launchctl list | grep obsidian
# No output
```

### Solutions:

**A. Load the LaunchAgent:**
```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

**B. Check for Errors:**
```bash
launchctl list | grep obsidian
```

Look for the status code. If it shows a negative number, there's an error.

**C. Check Plist Syntax:**
```bash
plutil -lint ~/Library/LaunchAgents/com.obsidian.synctranscripts.plist
```

Should output: `OK`

**D. Check Plist Paths:**
Open the plist file and verify:
- Script path exists and is executable
- Log path directory exists
- All paths use your correct username

---

## Issue 4: Script Runs But Files Not Appearing

### Symptom:
- Log shows success
- No files in Obsidian Meeting Transcripts folder

### Solutions:

**A. Check Destination Path:**
```bash
ls -la ~/Obsidian\ Vault/Meeting\ Transcripts/
```

**B. Verify Script Paths:**
```bash
cat ~/Obsidian\ Vault/Automations/meeting-transcript-system/sync-transcripts.sh
```

Check the `OBSIDIAN_DEST` variable matches your actual folder.

**C. Check Directory Permissions:**
```bash
ls -la ~/Obsidian\ Vault/ | grep "Meeting Transcripts"
```

Should show `drwx------` (directory with read/write/execute for owner).

---

## Issue 5: Edited Files Being Overwritten

### Symptom:
- You edit a transcript in Obsidian
- Next sync overwrites your changes

### Explanation:
- Script uses `rsync -au` (update only)
- Only copies if source file is newer than destination
- **Your edits should be safe** if they're newer

### Prevention:

**Option A: Edit in Google Docs**
- Make changes in the original Google Doc
- Google Apps Script will reconvert
- Sync will update with your changes

**Option B: Rename in Obsidian**
- Add suffix: `transcript-name-EDITED.txt`
- Script won't overwrite files it doesn't recognize

**Option C: Move to Different Folder**
- Create `Meeting Transcripts/Edited/`
- Move edited transcripts there
- They won't be touched by sync

---

## Issue 6: Google Drive Desktop Stopped Syncing

### Symptom:
- New meetings happened
- Google Drive shows new transcripts
- Local folder not updating

### Solutions:

**A. Restart Google Drive Desktop:**
1. Quit Google Drive Desktop
2. Relaunch it
3. Wait for sync to complete
4. Run transcript sync manually to test

**B. Check Google Drive Settings:**
1. Open Google Drive Desktop preferences
2. Verify "Meeting Transcripts as Text" folder is set to sync
3. Make sure "Stream files" isn't enabled (we need local copies)

**C. Verify Sync Status:**
```bash
ls -la ~/Library/CloudStorage/GoogleDrive-YOUR_EMAIL/My\ Drive/Meeting\ Transcripts\ as\ Text/
```

Check the modification times. They should be recent if syncing is working.

---

## Issue 7: Log File Growing Too Large

### Symptom:
- Log file is several MB
- Taking up space

### Solutions:

**A. Rotate Log File:**
```bash
# Backup old log
cp ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log.old

# Clear current log
> ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log
```

**B. Implement Log Rotation:**
Add this to the beginning of `sync-transcripts.sh`:

```bash
# Keep only last 1000 lines
tail -1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
```

---

## Diagnostic Commands

### Check Everything At Once:

```bash
echo "=== Checking LaunchAgent ==="
launchctl list | grep obsidian

echo "\n=== Checking Script ==="
ls -la ~/Obsidian\ Vault/Automations/meeting-transcript-system/sync-transcripts.sh

echo "\n=== Checking Source ==="
ls -la ~/Library/CloudStorage/ | grep GoogleDrive

echo "\n=== Checking Destination ==="
ls -la ~/Obsidian\ Vault/ | grep "Meeting Transcripts"

echo "\n=== Recent Log Entries ==="
tail -20 ~/Obsidian\ Vault/Automations/meeting-transcript-system/transcript-sync.log
```

---

## Still Having Issues?

1. **Check the log file** - Most errors are logged with details
2. **Run manually** - See if it works outside of LaunchAgent
3. **Verify permissions** - Make sure all folders are accessible
4. **Test Google Drive** - Confirm files are actually syncing locally

---

## Common Patterns

### Intermittent Failures
- **Usually**: Google Drive locking files temporarily
- **Action**: None needed, next run will succeed

### Consistent Failures
- **Usually**: Path or permission problem
- **Action**: Fix paths in script and plist, grant Full Disk Access

### Files Not Syncing
- **Usually**: Everything is up to date
- **Action**: Check Google Apps Script is creating new transcripts

---

*Most issues resolve themselves or are fixed by verifying paths and permissions*
