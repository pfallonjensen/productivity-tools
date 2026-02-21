# Making This a Public Repository - Guide

> **Goal:** Convert this private, personalized backup system into a generic, shareable public repository that others can use.

---

## Overview

This guide explains how to take your working backup system and prepare it for public release. You'll:
1. Genericize all personal paths and account names
2. Remove sensitive information
3. Create templates for others to customize
4. Set up a public GitHub repository

---

## Step 1: Create a New Public Repository

### Option A: New Separate Repo (Recommended)

```bash
# Create a new directory for the public version
mkdir ~/Projects/obsidian-auto-backup
cd ~/Projects/obsidian-auto-backup

# Copy all files from this package
cp -r "/Users/fallonjensen/Obsidian Vault/Automation/obsidian-backup-system/"* .

# Initialize as a new git repo
git init

# Create public repo on GitHub
gh repo create obsidian-auto-backup --public --source=. --description "Automatic backup system for Obsidian vaults to GitHub"
```

### Option B: Copy This Folder Structure

Simply copy this entire `obsidian-backup-system` folder to a new location outside your private vault.

---

## Step 2: Genericize File Paths

### Files to Update:

#### 1. `scripts/auto-backup.sh`

**Change:**
```bash
cd "/Users/fallonjensen/Obsidian Vault" || exit 1
```

**To:**
```bash
# UPDATE THIS PATH to your Obsidian Vault location
VAULT_PATH="/Users/YOUR_USERNAME/Obsidian Vault"
cd "$VAULT_PATH" || exit 1
```

**Change:**
```bash
CURRENT_ACCOUNT=$(gh auth status 2>&1 | grep "Active account: true" -B 1 | grep "Logged in" | sed 's/.*account \(.*\) (.*/\1/')
```

**To:**
```bash
# Get current GitHub account (if you have multiple accounts)
CURRENT_ACCOUNT=$(gh auth status 2>&1 | grep "Active account: true" -B 1 | grep "Logged in" | sed 's/.*account \(.*\) (.*/\1/')
```

**Change:**
```bash
gh auth switch -u pfallonjensen 2>/dev/null
```

**To:**
```bash
# UPDATE THIS to your personal GitHub username
PERSONAL_GITHUB_ACCOUNT="YOUR_GITHUB_USERNAME"
gh auth switch -u "$PERSONAL_GITHUB_ACCOUNT" 2>/dev/null
```

**Change:**
```bash
if [ "$CURRENT_ACCOUNT" = "fallonjensen-Daybreak" ]; then
    gh auth switch -u fallonjensen-Daybreak 2>/dev/null
```

**To:**
```bash
# UPDATE THIS to your work GitHub username (or remove if you only have one account)
WORK_GITHUB_ACCOUNT="YOUR_WORK_GITHUB_USERNAME"
if [ "$CURRENT_ACCOUNT" = "$WORK_GITHUB_ACCOUNT" ]; then
    gh auth switch -u "$WORK_GITHUB_ACCOUNT" 2>/dev/null
```

#### 2. `config/com.obsidian.autobackup.plist`

**Change:**
```xml
<string>/Users/fallonjensen/Obsidian Vault/Scripts/auto-backup.sh</string>
```

**To:**
```xml
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh</string>
```

**Change:**
```xml
<string>/Users/fallonjensen/Obsidian Vault/Scripts/backup.log</string>
<string>/Users/fallonjensen/Obsidian Vault/Scripts/backup-error.log</string>
```

**To:**
```xml
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/backup.log</string>
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/backup-error.log</string>
```

Or better yet, add comments:
```xml
<!-- UPDATE ALL PATHS BELOW to match your system -->
<string>/Users/YOUR_USERNAME/Obsidian Vault/Scripts/auto-backup.sh</string>
```

---

## Step 3: Remove Sensitive Information

### Review and Remove:

1. **GitHub Account Names**
   - Remove `pfallonjensen` and `fallonjensen-Daybreak`
   - Replace with `YOUR_GITHUB_USERNAME` and `YOUR_WORK_GITHUB_USERNAME`

2. **Personal Paths**
   - Remove `/Users/fallonjensen/`
   - Replace with `/Users/YOUR_USERNAME/`

3. **Repository URLs**
   - Remove `https://github.com/pfallonjensen/obsidian-vault`
   - Replace with `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`

4. **Email Addresses**
   - Remove `pfallonjensen@gmail.com`
   - Replace with `your-email@example.com`

### Files to Check:

- ✅ `README.md`
- ✅ `START-HERE.md`
- ✅ `VERIFICATION-GUIDE.md`
- ✅ `INSTALLATION-GUIDE.md`
- ✅ `scripts/auto-backup.sh`
- ✅ `config/com.obsidian.autobackup.plist`

---

## Step 4: Create a Public-Friendly README

Create a new `README.md` for the public repo:

```markdown
# Obsidian Auto-Backup to GitHub

Automatically backup your Obsidian vault to a private GitHub repository every night at 3 AM using macOS LaunchAgent.

## Features

- 🔄 Automatic nightly backups at 3 AM
- 🔐 Works with private GitHub repositories
- 🔀 Smart GitHub account switching (if you have work/personal accounts)
- 📝 Comprehensive logging
- 🚫 No workflow interruption
- 🍎 macOS LaunchAgent (runs even when app is closed)

## Quick Start

1. **Prerequisites:**
   - macOS
   - Git installed
   - GitHub CLI installed (`brew install gh`)
   - Obsidian vault

2. **Clone this repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/obsidian-auto-backup.git
   cd obsidian-auto-backup
   ```

3. **Follow the installation guide:**
   - See [INSTALLATION-GUIDE.md](INSTALLATION-GUIDE.md)

## Documentation

- **[INSTALLATION-GUIDE.md](INSTALLATION-GUIDE.md)** - Complete setup instructions
- **[START-HERE.md](START-HERE.md)** - Quick overview
- **[VERIFICATION-GUIDE.md](VERIFICATION-GUIDE.md)** - How to verify it works

## How It Works

1. A bash script commits and pushes changes to your GitHub repo
2. macOS LaunchAgent runs the script at 3 AM daily
3. Logs are created for verification
4. Smart account switching if you have multiple GitHub accounts

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions welcome! Please open an issue or PR.

## Author

Created by [Your Name]

Based on a real working system managing an Obsidian vault with 100+ notes.
```

---

## Step 5: Add a License

Create a `LICENSE` file:

```bash
# For MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

---

## Step 6: Create a Configuration Template

Create a `config.template.sh` file that users can copy:

```bash
#!/bin/bash
# Configuration Template - Copy this to config.sh and customize

# Your Obsidian Vault path
export VAULT_PATH="/Users/YOUR_USERNAME/Obsidian Vault"

# Your GitHub usernames (if you have multiple accounts)
export PERSONAL_GITHUB_ACCOUNT="YOUR_PERSONAL_GITHUB_USERNAME"
export WORK_GITHUB_ACCOUNT="YOUR_WORK_GITHUB_USERNAME"  # Optional

# Backup schedule (24-hour format)
export BACKUP_HOUR="3"  # 3 AM
export BACKUP_MINUTE="0"
```

Then update `auto-backup.sh` to source this config:

```bash
# Load configuration
if [ -f "$(dirname "$0")/config.sh" ]; then
    source "$(dirname "$0")/config.sh"
else
    echo "Error: config.sh not found. Copy config.template.sh to config.sh and customize it."
    exit 1
fi
```

---

## Step 7: Create Installation Script

Create an `install.sh` script:

```bash
#!/bin/bash
# Easy installation script

echo "Obsidian Auto-Backup Installer"
echo "==============================="
echo ""

# Check if config exists
if [ ! -f "config.sh" ]; then
    echo "❌ Please copy config.template.sh to config.sh and customize it first"
    exit 1
fi

# Source config
source config.sh

# Create Scripts directory
mkdir -p "$VAULT_PATH/Scripts"

# Copy script
cp scripts/auto-backup.sh "$VAULT_PATH/Scripts/"
chmod +x "$VAULT_PATH/Scripts/auto-backup.sh"

# Update LaunchAgent plist with user's path
sed "s|/Users/YOUR_USERNAME|$HOME|g" config/com.obsidian.autobackup.plist > ~/Library/LaunchAgents/com.obsidian.autobackup.plist

# Load LaunchAgent
launchctl load ~/Library/LaunchAgents/com.obsidian.autobackup.plist

echo "✅ Installation complete!"
echo ""
echo "Test your backup with:"
echo "  $VAULT_PATH/Scripts/auto-backup.sh"
```

---

## Step 8: Prepare for Release

### Create Checklist:

- [ ] All personal information removed
- [ ] All paths genericized
- [ ] README.md written for public audience
- [ ] INSTALLATION-GUIDE.md updated
- [ ] LICENSE file added
- [ ] Configuration template created
- [ ] Installation script created (optional)
- [ ] Test on a fresh system (if possible)

### Git Ignore:

Add a `.gitignore`:

```
# User configuration (don't commit personal info)
config.sh

# Logs
*.log

# macOS
.DS_Store
```

---

## Step 9: Publish to GitHub

```bash
# Make sure everything is committed
git add .
git commit -m "Initial public release: Obsidian Auto-Backup system"

# Push to public repo
git push -u origin main

# Add topics/tags on GitHub
gh repo edit --add-topic obsidian
gh repo edit --add-topic backup
gh repo edit --add-topic automation
gh repo edit --add-topic macos
gh repo edit --add-topic github-actions
```

---

## Step 10: Announce and Share

### Places to Share:

1. **Obsidian Forum:** https://forum.obsidian.md/
2. **Reddit:** r/ObsidianMD
3. **Twitter/X:** #ObsidianMD #PKM
4. **Your blog/website**
5. **Dev.to or Medium** (write a tutorial)

### Sample Announcement:

> "I've open-sourced my Obsidian vault backup system! 🎉
>
> Automatically backs up to GitHub every night at 3 AM using macOS LaunchAgent. Works with multiple GitHub accounts and includes comprehensive logging.
>
> https://github.com/YOUR_USERNAME/obsidian-auto-backup
>
> Features:
> - Automatic nightly backups
> - Smart account switching
> - Easy installation
> - Well documented
>
> Feel free to use and contribute!"

---

## Maintenance

### Keep Both Versions:

1. **Private version** (in your Obsidian Vault): Your working system with actual paths
2. **Public version** (separate repo): Generic version for others

When you make improvements to your private version:
1. Test them thoroughly
2. Genericize the changes
3. Update the public repo
4. Tag a new release

### Versioning:

Use semantic versioning:
- v1.0.0 - Initial release
- v1.1.0 - Added feature
- v1.0.1 - Bug fix

```bash
git tag -a v1.0.0 -m "Initial public release"
git push origin v1.0.0
```

---

## Checklist for Making This Public

```bash
# Use this checklist when you're ready:

# 1. Review all files
grep -r "fallonjensen" .
grep -r "pfallonjensen" .
grep -r "/Users/fallonjensen" .

# 2. Replace with generic versions
find . -type f -exec sed -i '' 's/fallonjensen/YOUR_USERNAME/g' {} +
find . -type f -exec sed -i '' 's/pfallonjensen/YOUR_GITHUB_USERNAME/g' {} +

# 3. Add templates and installation scripts
# (See steps above)

# 4. Create public repo
gh repo create obsidian-auto-backup --public

# 5. Push
git push -u origin main

# 6. Test installation on another machine (if possible)

# 7. Announce!
```

---

*Guide created: 2025-11-17*
*For questions or improvements, open an issue on the public repo!*
