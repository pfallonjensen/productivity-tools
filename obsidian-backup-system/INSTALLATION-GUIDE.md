# Obsidian Backup System - Installation Guide

> **This is Fallon Jensen's actual working setup as of 2025-11-17**
>
> This guide documents the exact configuration running on Fallon's system.
> You can use this to replicate the setup on another machine or as a reference.

---

## Overview

This system automatically backs up an Obsidian Vault to a private GitHub repository every night at 3:00 AM.

**Key Features:**
- Automatic nightly backups at 3 AM
- Smart GitHub account switching (personal/work)
- macOS LaunchAgent for scheduling
- Logging for verification
- No workflow interruption

---

## Current Working Setup (Fallon's System)

### GitHub Accounts
- **Personal Account:** `pfallonjensen` (pfallonjensen@gmail.com)
  - Repository: https://github.com/pfallonjensen/obsidian-vault (private)
- **Work Account:** `fallonjensen-Daybreak`

### File Locations

**Obsidian Vault:**
```
/Users/fallonjensen/Obsidian Vault/
```

**Backup Script:**
```
/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/auto-backup.sh
```

**LaunchAgent Configuration:**
```
/Users/fallonjensen/Library/LaunchAgents/com.obsidian.autobackup.plist
```

**Logs:**
```
/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup.log
/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup-error.log
```

**Documentation:**
```
/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/START-HERE.md
/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/VERIFICATION-GUIDE.md
/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/README.md
/Users/fallonjensen/Obsidian Vault/Git-Quick-Reference.md
```

---

## Installation Steps (To Replicate on Another System)

### Prerequisites

1. **macOS** (for LaunchAgent support)
2. **Git** installed (`git --version` to verify)
3. **GitHub CLI** installed (`gh --version` to verify)
   - Install via: `brew install gh`
4. **Obsidian Vault** in a known location
5. **GitHub Account** authenticated

### Step 1: Set Up Git in Your Vault

```bash
# Navigate to your Obsidian Vault
cd "/Users/YOUR_USERNAME/Obsidian Vault"

# Initialize git (if not already done)
git init

# Configure git with your info
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Create .gitignore
cat > .gitignore << 'EOF'
# Obsidian workspace files
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# Mac system files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes

# Sensitive files (add your own)
*.env
credentials.json
secrets/
EOF

# Initial commit
git add .
git commit -m "Initial commit: Obsidian Vault"
```

### Step 2: Create GitHub Repository

```bash
# Authenticate with GitHub CLI
gh auth login

# Create private repository and push
gh repo create obsidian-vault --private --source=. --push
```

### Step 3: Install the Backup Script

```bash
# Create Scripts directory if it doesn't exist
mkdir -p "/Users/YOUR_USERNAME/Obsidian Vault/Scripts"

# Copy the backup script from this package
cp scripts/auto-backup.sh "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/"

# Make it executable
chmod +x "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh"

# IMPORTANT: Edit the script to update paths
# Change "/Users/fallonjensen/" to "/Users/YOUR_USERNAME/"
nano "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh"
```

**Required edits in auto-backup.sh:**
```bash
# Line 7: Update this path
cd "/Users/YOUR_USERNAME/Obsidian Vault" || exit 1
```

### Step 4: Install LaunchAgent

```bash
# Copy the plist file
cp config/com.obsidian.autobackup.plist ~/Library/LaunchAgents/

# IMPORTANT: Edit the plist to update paths
nano ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

**Required edits in com.obsidian.autobackup.plist:**
```xml
<!-- Line 10: Update script path -->
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh</string>

<!-- Line 42: Update log path -->
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/backup.log</string>

<!-- Line 45: Update error log path -->
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/backup-error.log</string>
```

### Step 5: Configure GitHub Account Switching (Optional)

If you have multiple GitHub accounts (personal/work), update the script:

```bash
# Edit auto-backup.sh
nano "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh"

# Line 10: Update to your actual account name
CURRENT_ACCOUNT=$(gh auth status 2>&1 | grep "Active account: true" -B 1 | grep "Logged in" | sed 's/.*account \(.*\) (.*/\1/')

# Line 26: Update to your personal account
gh auth switch -u YOUR_PERSONAL_GITHUB_USERNAME 2>/dev/null

# Line 33 & 41: Update to your work account (if applicable)
if [ "$CURRENT_ACCOUNT" = "YOUR_WORK_GITHUB_USERNAME" ]; then
    gh auth switch -u YOUR_WORK_GITHUB_USERNAME 2>/dev/null
```

### Step 6: Load the LaunchAgent

```bash
# Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist

# Verify it's loaded
launchctl list | grep obsidian
```

You should see:
```
-	0	com.obsidian.autobackup
```

### Step 7: Test the Backup

```bash
# Run a test backup manually
"/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh"

# Check the output - you should see:
# ✓ Successfully backed up to GitHub at YYYY-MM-DD HH:MM:SS
```

### Step 8: Copy Documentation (Optional)

```bash
# Copy all documentation to your vault
cp START-HERE.md "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/"
cp VERIFICATION-GUIDE.md "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/"
cp README.md "/Users/YOUR_USERNAME/Obsidian Vault/Scripts/"
```

---

## Verification

After installation, verify everything is working:

```bash
# 1. Check LaunchAgent is loaded
launchctl list | grep obsidian

# 2. Check schedule (should show Hour: 3)
cat ~/Library/LaunchAgents/com.obsidian.autobackup.plist | grep -A 3 "Hour"

# 3. Run manual backup test
~/Obsidian\ Vault/Scripts/auto-backup.sh

# 4. Check logs
tail -10 ~/Obsidian\ Vault/Scripts/backup.log

# 5. Verify on GitHub
# Visit your repository and check for recent commits
```

---

## Fallon's Specific Configuration

For reference, here's exactly how Fallon's system is configured:

| Component | Value |
|-----------|-------|
| Vault Path | `/Users/fallonjensen/Obsidian Vault/` |
| GitHub Personal Account | `pfallonjensen` |
| GitHub Work Account | `fallonjensen-Daybreak` |
| Repository URL | `https://github.com/pfallonjensen/obsidian-vault` |
| Repository Type | Private |
| Backup Schedule | 3:00 AM daily |
| Script Location | `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/auto-backup.sh` |
| LaunchAgent Location | `/Users/fallonjensen/Library/LaunchAgents/com.obsidian.autobackup.plist` |
| Log File | `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup.log` |
| Error Log | `/Users/fallonjensen/Obsidian Vault/Automations/obsidian-backup-system/backup-error.log` |

---

## Troubleshooting

### LaunchAgent not running
```bash
# Unload and reload
launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Push fails
```bash
# Check GitHub authentication
gh auth status

# Re-authenticate if needed
gh auth login
```

### Script has wrong paths
```bash
# Edit the script
nano ~/Obsidian\ Vault/Scripts/auto-backup.sh

# Update all paths to match your system
# Then test again
~/Obsidian\ Vault/Scripts/auto-backup.sh
```

---

## Customization

### Change Backup Time

Edit the LaunchAgent plist:
```bash
nano ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

Change the Hour and Minute values, then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.obsidian.autobackup.plist
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist
```

### Add Multiple Backup Times

Replace `StartCalendarInterval` dict with an array:
```xml
<key>StartCalendarInterval</key>
<array>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <dict>
        <key>Hour</key>
        <integer>15</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</array>
```

---

## Files in This Package

```
obsidian-backup-system/
├── README.md                          # Overview and documentation
├── START-HERE.md                      # Quick start guide
├── VERIFICATION-GUIDE.md              # How to verify and troubleshoot
├── INSTALLATION-GUIDE.md              # This file - setup instructions
├── scripts/
│   └── auto-backup.sh                 # The backup script
├── config/
│   └── com.obsidian.autobackup.plist  # LaunchAgent configuration
└── docs/
    └── MAKING-IT-PUBLIC.md            # Guide for making this public

```

---

## Next Steps

1. ✅ Complete installation steps above
2. ✅ Test manual backup
3. ✅ Wait until after 3 AM the next day
4. ✅ Check logs to verify automatic backup ran
5. ✅ Check GitHub for commit

---

*Installation guide created: 2025-11-17*
*System Owner: Fallon Jensen*
*Repository: https://github.com/pfallonjensen/obsidian-vault (private)*
