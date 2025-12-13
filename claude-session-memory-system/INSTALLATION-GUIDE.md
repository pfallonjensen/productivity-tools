# Installation Guide - Claude Code Session Memory System

Complete step-by-step installation instructions with verification.

---

## Overview

This guide will help you install the Claude Code session memory system on your Mac. Installation takes approximately **10-15 minutes** and includes:

- Creating backup directory structure
- Installing 3 automation scripts
- Configuring LaunchAgent for automatic backups
- Verifying everything works
- Optional slash command setup

**v1.1 New Features:**
- **Plan Backup**: Automatically backs up `~/.claude/plans/` directory
- **Plan-Session Mapping**: Links plans to their associated sessions for better context restoration
- **Export with Plans**: Session exports now include full plan content for complete context recovery

---

## Prerequisites

Before starting installation, verify you have:

### Required

- [ ] **macOS 10.15 or later**
  ```bash
  sw_vers
  # Should show ProductVersion: 10.15 or higher
  ```

- [ ] **Claude Code installed and working**
  ```bash
  ls ~/.claude
  # Should show: history.jsonl, projects/, etc.
  ```

- [ ] **jq installed** (for JSON parsing)
  ```bash
  jq --version
  # Should show: jq-1.6 or similar
  # If not installed: brew install jq
  ```

- [ ] **Obsidian Vault location known**
  ```bash
  ls ~/Obsidian\ Vault
  # Should show your vault contents
  # If different location, note the path for customization
  ```

- [ ] **500 MB free disk space**
  ```bash
  df -h ~
  # Check "Avail" column
  ```

### Optional but Recommended

- [ ] **tmux installed** (for crash-proof sessions)
  ```bash
  tmux -V
  # If not installed: brew install tmux
  ```

---

## Fallon's Working Setup (Reference)

This is the configuration running on Fallon's system:

```
Backup Location: ~/Obsidian Vault/Claude Sessions/
Scripts Location: ~/Obsidian Vault/Automations/claude-session-backup/
Backup Frequency: Every 15 minutes (900 seconds)
Retention: Last 50 snapshots, 7 days of conversations
Status: Running since Nov 2024, zero issues
Stats: 1,541 entries, 331 conversations, 888 snapshots
```

Your installation will create a similar setup adapted to your system.

---

## Installation Steps

### Step 1: Create Directory Structure

Create the necessary directories for backups and automation:

```bash
# Create backup storage directories
mkdir -p ~/Obsidian\ Vault/Claude\ Sessions/{conversations,history,shell-snapshots,file-history,session-env,plans,plan-session-maps,"Restored Contexts"}

# Create automation directory
mkdir -p ~/Obsidian\ Vault/Automations/claude-session-backup

# Verify directories created
ls ~/Obsidian\ Vault/Claude\ Sessions/
ls ~/Obsidian\ Vault/Automations/claude-session-backup/
```

**Expected Output**: You should see the directory names listed.

**Troubleshooting**: If you get "No such file or directory", your Obsidian Vault might be in a different location. Adjust the path accordingly.

---

### Step 2: Install Backup Script

Copy the main backup script to your automation directory:

```bash
# Copy from package
cp claude-session-memory-system/scripts/backup-claude-sessions.sh \
   ~/Obsidian\ Vault/Automations/claude-session-backup/

# Make executable
chmod +x ~/Obsidian\ Vault/Automations/claude-session-backup/backup-claude-sessions.sh

# Verify
ls -l ~/Obsidian\ Vault/Automations/claude-session-backup/backup-claude-sessions.sh
```

**Expected Output**: `-rwx------` (executable permissions)

---

### Step 3: Install Export Script

Copy the session export script:

```bash
# Copy from package
cp claude-session-memory-system/scripts/export-session-context.sh \
   ~/Obsidian\ Vault/Automations/claude-session-backup/

# Make executable
chmod +x ~/Obsidian\ Vault/Automations/claude-session-backup/export-session-context.sh

# Verify
ls -l ~/Obsidian\ Vault/Automations/claude-session-backup/export-session-context.sh
```

---

### Step 4: Install Quick-Restore Script

Copy the quick-restore wrapper script:

```bash
# Copy from package
cp claude-session-memory-system/scripts/quick-restore.sh \
   ~/Obsidian\ Vault/Automations/claude-session-backup/

# Make executable
chmod +x ~/Obsidian\ Vault/Automations/claude-session-backup/quick-restore.sh

# Verify all scripts
ls -l ~/Obsidian\ Vault/Automations/claude-session-backup/*.sh
```

**Expected Output**: Three .sh files, all executable

---

### Step 5: Test Scripts Manually (Before Automation)

Test each script to ensure they work before setting up automation:

**Test Backup Script**:
```bash
~/Obsidian\ Vault/Automations/claude-session-backup/backup-claude-sessions.sh
```

**Expected Output**:
```
[2024-12-09 14:30:45] Starting Claude Code session backup... (Terminal: default)
[2024-12-09 14:30:45] ✓ Backed up history.jsonl (xxxx lines)
[2024-12-09 14:30:45] ✓ Backed up recent shell snapshots (xx total)
[2024-12-09 14:30:45] ✓ Backed up file-history
[2024-12-09 14:30:45] ✓ Backed up recent session-env data
[2024-12-09 14:30:46] ✓ Backed up xx conversation files (FULL CONTEXT)
[2024-12-09 14:30:46] ✓ Backed up xx plan files
[2024-12-09 14:30:46] ✓ Created plan-session mapping
[2024-12-09 14:30:46] ✓ Created activity summary
[2024-12-09 14:30:46] Session stats: xxxx commands total, last: [command]
[2024-12-09 14:30:46] Backup complete! Saved to: /Users/YOUR_USERNAME/Obsidian Vault/Claude Sessions
```

**Verify Backup Files Created**:
```bash
ls ~/Obsidian\ Vault/Claude\ Sessions/history-latest.jsonl
ls ~/Obsidian\ Vault/Claude\ Sessions/Recent-Activity.md
```

**Test Export Script** (if you have existing sessions):
```bash
~/Obsidian\ Vault/Automations/claude-session-backup/export-session-context.sh
```

**Expected Output**: Should export to `~/Obsidian Vault/Claude Sessions/Restored Contexts/`
- Shows "Found X linked plan(s)" if session has plan references
- Includes plan content in exported markdown (v1.1 feature)

**Test Quick-Restore** (combines both):
```bash
~/Obsidian\ Vault/Automations/claude-session-backup/quick-restore.sh
```

**Expected Output**: Should backup, export, and copy to clipboard with success message.

**Troubleshooting**:
- **"jq: command not found"**: Install jq with `brew install jq`
- **"No such file or directory"**: Check vault path is correct
- **Permission denied**: Re-run chmod +x commands from Steps 2-4

---

### Step 6: Install LaunchAgent Configuration

The LaunchAgent will run the backup script automatically every 15 minutes.

**Copy the plist file**:
```bash
cp claude-session-memory-system/config/com.user.claude-session-backup.plist \
   ~/Library/LaunchAgents/
```

**IMPORTANT - Edit Paths**:

Open the plist file in an editor:
```bash
nano ~/Library/LaunchAgents/com.user.claude-session-backup.plist
```

Find and replace `YOUR_USERNAME` with your actual username in these lines:
- Line 11: Script path
- Line 21: stdout log path
- Line 24: stderr log path

**Example**:
```xml
<!-- Before -->
<string>/Users/YOUR_USERNAME/Obsidian Vault/...</string>

<!-- After (if your username is "john") -->
<string>/Users/john/Obsidian Vault/...</string>
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

**Quick Username Check**:
```bash
whoami
# This shows your username
```

---

### Step 7: Load LaunchAgent

Load the LaunchAgent to start automatic backups:

```bash
launchctl load ~/Library/LaunchAgents/com.user.claude-session-backup.plist
```

**Verify it's loaded**:
```bash
launchctl list | grep claude-session-backup
```

**Expected Output**:
```
-	0	com.user.claude-session-backup
```

The `-` means it's not currently running (scheduled), `0` means no errors, and the label name confirms it's loaded.

**Troubleshooting**:
- **No output**: LaunchAgent didn't load. Check plist syntax: `plutil ~/Library/LaunchAgents/com.user.claude-session-backup.plist`
- **Error loading**: Check paths in plist are correct with your username
- **Permission denied**: plist file needs correct permissions: `chmod 644 ~/Library/LaunchAgents/com.user.claude-session-backup.plist`

---

### Step 8: Verify Automatic Backups Start Working

Wait 1-2 minutes, then check if the first automatic backup ran:

```bash
# Check if log file exists and has content
tail -20 ~/Obsidian\ Vault/Automations/claude-session-backup/backup.log
```

**Expected Output**: Should show timestamps and "Backup complete!" messages

**Check stderr log (should be empty if working)**:
```bash
cat ~/Obsidian\ Vault/Automations/claude-session-backup/launchagent-stderr.log
```

**Expected Output**: Empty or minimal warnings

**Force immediate backup (optional test)**:
```bash
launchctl start com.user.claude-session-backup
```

Then check logs again.

---

### Step 9: Install Slash Command (Optional)

Add `/backup-restore` command to Claude Code for easy restoration:

```bash
# Create commands directory if it doesn't exist
mkdir -p ~/.claude/commands

# Create slash command file
cat > ~/.claude/commands/backup-restore.md << 'EOF'
---
description: Quick restore - export session context to clipboard
---

Please run the Claude Code session quick restore script:

**Script**: `~/Obsidian Vault/Automations/claude-session-backup/quick-restore.sh`

This will:
1. Backup current session first
2. Export the most recent session to readable markdown format
3. Copy the session context to your clipboard
4. Show you the file size, line count, and next steps

Execute the quick restore now and report:
- Session context file location
- File size and line count
- Confirmation that content is copied to clipboard
- Next steps for pasting into a new Claude Code session
EOF

# Verify
cat ~/.claude/commands/backup-restore.md
```

**Test**: In Claude Code terminal, type `/backup-restore` and it should run the script.

---

### Step 10: Final Verification Checklist

Run through this checklist to confirm everything is working:

**LaunchAgent Running**:
```bash
launchctl list | grep claude-session-backup
# Expected: Shows com.user.claude-session-backup with PID or -
```

**Scripts Executable**:
```bash
ls -l ~/Obsidian\ Vault/Automations/claude-session-backup/*.sh
# Expected: All show -rwx------ (executable)
```

**First Backup Successful**:
```bash
ls ~/Obsidian\ Vault/Claude\ Sessions/history-latest.jsonl
# Expected: File exists and is recent
```

**Logs Show Activity**:
```bash
tail -5 ~/Obsidian\ Vault/Automations/claude-session-backup/backup.log
# Expected: Recent timestamps with "Backup complete!"
```

**No Errors**:
```bash
tail ~/Obsidian\ Vault/Automations/claude-session-backup/launchagent-stderr.log
# Expected: Empty or minimal warnings
```

**Storage Structure Exists**:
```bash
ls ~/Obsidian\ Vault/Claude\ Sessions/
# Expected: conversations/, history/, shell-snapshots/, plans/, plan-session-maps/, etc.
```

---

## Configuration Reference

| Component | Location | Purpose | Notes |
|-----------|----------|---------|-------|
| Backup Script | ~/Obsidian Vault/Automations/claude-session-backup/backup-claude-sessions.sh | Main backup logic | Runs every 15 min |
| Export Script | ~/Obsidian Vault/Automations/claude-session-backup/export-session-context.sh | JSONL → Markdown | On-demand |
| Quick Restore | ~/Obsidian Vault/Automations/claude-session-backup/quick-restore.sh | One-command recovery | On-demand |
| LaunchAgent | ~/Library/LaunchAgents/com.user.claude-session-backup.plist | Automation schedule | 900s interval |
| Backup Storage | ~/Obsidian Vault/Claude Sessions/ | All backup data | ~50-100 MB/month |
| Plans Storage | ~/Obsidian Vault/Claude Sessions/plans/ | Backed up plan files | From ~/.claude/plans/ |
| Plan Mappings | ~/Obsidian Vault/Claude Sessions/plan-session-maps/ | Plan-to-session links | JSON mapping files |
| Success Log | ~/Obsidian Vault/Automations/claude-session-backup/backup.log | Backup history | Check this first |
| Error Log | ~/Obsidian Vault/Automations/claude-session-backup/launchagent-stderr.log | Error messages | Should be empty |
| Slash Command | ~/.claude/commands/backup-restore.md | Claude Code integration | Optional |

---

## Customization Options

### Change Backup Frequency

Edit the LaunchAgent plist:
```bash
nano ~/Library/LaunchAgents/com.user.claude-session-backup.plist
```

Find `<key>StartInterval</key>` (line 14-15) and change the value:
```xml
<key>StartInterval</key>
<integer>900</integer>  <!-- 900 = 15 min, 1800 = 30 min, 3600 = 1 hour -->
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.claude-session-backup.plist
launchctl load ~/Library/LaunchAgents/com.user.claude-session-backup.plist
```

### Change Backup Retention

Edit the backup script:
```bash
nano ~/Obsidian\ Vault/Automations/claude-session-backup/backup-claude-sessions.sh
```

Find `MAX_BACKUPS=50` (line 12) and change to keep more or fewer snapshots:
```bash
MAX_BACKUPS=100  # Keep last 100 instead of 50
```

### Change Conversation Retention

In the same backup script, find the conversation backup section (line 94) and change `-mtime -7` (7 days) to a different value:
```bash
find "$CLAUDE_DIR/projects" -name "*.jsonl" -mtime -14  # Keep 14 days instead
```

---

## Troubleshooting Installation

### Problem: Scripts Don't Run

**Symptoms**: Error messages when running scripts manually

**Diagnosis**:
```bash
# Check if scripts are executable
ls -l ~/Obsidian\ Vault/Automations/claude-session-backup/*.sh

# Try running with bash explicitly
bash ~/Obsidian\ Vault/Automations/claude-session-backup/backup-claude-sessions.sh
```

**Solution**: Re-run chmod commands from Steps 2-4

### Problem: LaunchAgent Won't Load

**Symptoms**: No output from `launchctl list | grep claude`

**Diagnosis**:
```bash
# Check plist syntax
plutil ~/Library/LaunchAgents/com.user.claude-session-backup.plist

# Check permissions
ls -l ~/Library/LaunchAgents/com.user.claude-session-backup.plist
```

**Solution**:
```bash
# Fix permissions
chmod 644 ~/Library/LaunchAgents/com.user.claude-session-backup.plist

# Try loading again
launchctl load ~/Library/LaunchAgents/com.user.claude-session-backup.plist
```

### Problem: "jq: command not found"

**Solution**: Install jq via Homebrew:
```bash
brew install jq
```

### Problem: Backups Not Running Automatically

**Symptoms**: Manual runs work, but no automatic backups

**Diagnosis**:
```bash
# Check if LaunchAgent is loaded
launchctl list | grep claude-session-backup

# Check stderr log for errors
cat ~/Obsidian\ Vault/Automations/claude-session-backup/launchagent-stderr.log
```

**Solution**: Verify paths in plist are correct (no YOUR_USERNAME placeholders left)

### Problem: Permission Denied Errors

**Solution**: Check directory permissions:
```bash
ls -ld ~/Obsidian\ Vault/Claude\ Sessions
ls -ld ~/Obsidian\ Vault/Automations/claude-session-backup

# Should show drwx------ (your user has access)
```

---

## Next Steps

✅ **Installation Complete!**

Now you're ready to:

1. **Let it run**: Backups happen automatically every 15 minutes
2. **Test recovery**: See [USAGE-GUIDE.md](./USAGE-GUIDE.md) for recovery workflows
3. **Monitor logs**: Check backup.log occasionally to confirm it's working
4. **Use /backup-restore**: Try the slash command after a crash

**Optional Enhancements**:
- Install tmux for crash-proof sessions (see USAGE-GUIDE.md)
- Set up git backup for long-term archiving
- Customize retention settings (see Customization Options above)

---

## Support

- **Logs**: `~/Obsidian Vault/Automations/claude-session-backup/backup.log`
- **Recent Activity**: `~/Obsidian Vault/Claude Sessions/Recent-Activity.md`
- **Troubleshooting**: See [USAGE-GUIDE.md](./USAGE-GUIDE.md)
- **Verify Working**: Run `launchctl list | grep claude` and check logs

---

*Installation time: 10-15 minutes | Automated backups save hours of context rebuilding*
