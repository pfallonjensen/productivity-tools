# Making This Public - Meeting Transcript Automation

> **Guide to converting this personal automation into a shareable public repository**

---

## Overview

This folder currently contains a working automation system with **your actual paths and configuration**. To share it publicly, you need to:

1. **Genericize paths** - Replace personal usernames and emails
2. **Remove private information** - Clean out any sensitive data
3. **Add public-ready documentation** - Explain setup for others
4. **Test portability** - Verify it works on a fresh machine

---

## Current State (Personal)

### Paths That Need Genericization:

**In `scripts/sync-transcripts.sh`:**
```bash
# Current (personal):
GOOGLE_DRIVE_SOURCE="/Users/fallonjensen/Library/CloudStorage/GoogleDrive-fallon.jensen@daybreak.ai/My Drive/Meeting Transcripts as Text"
OBSIDIAN_DEST="/Users/fallonjensen/Obsidian Vault/Meeting Transcripts"
LOG_FILE="/Users/fallonjensen/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log"

# Public version should be:
GOOGLE_DRIVE_SOURCE="/Users/YOUR_USERNAME/Library/CloudStorage/GoogleDrive-YOUR_EMAIL/My Drive/Meeting Transcripts as Text"
OBSIDIAN_DEST="/Users/YOUR_USERNAME/Obsidian Vault/Meeting Transcripts"
LOG_FILE="/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log"
```

**In `config/com.obsidian.synctranscripts.plist`:**
```xml
<!-- Current (personal): -->
<string>/Users/fallonjensen/Obsidian Vault/Automations/meeting-transcript-system/sync-transcripts.sh</string>
<string>/Users/fallonjensen/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log</string>

<!-- Public version should be: -->
<string>/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/sync-transcripts.sh</string>
<string>/Users/YOUR_USERNAME/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log</string>
```

---

## Step-by-Step Conversion Process

### Step 1: Copy to Public Location

**Create a clean working directory:**
```bash
# Copy to Desktop for processing
cp -r ~/Obsidian\ Vault/Open-Source/meeting-transcript-system ~/Desktop/meeting-transcript-system-public

cd ~/Desktop/meeting-transcript-system-public
```

### Step 2: Genericize All Files

**A. Update sync-transcripts.sh:**
```bash
# Edit the script
nano scripts/sync-transcripts.sh

# Find and replace:
# /Users/fallonjensen → /Users/YOUR_USERNAME
# fallon.jensen@daybreak.ai → YOUR_EMAIL
```

**B. Update plist file:**
```bash
nano config/com.obsidian.synctranscripts.plist

# Find and replace:
# /Users/fallonjensen → /Users/YOUR_USERNAME
```

**C. Check all documentation:**
```bash
# Search for your username in all .md files
grep -r "fallonjensen" .

# Search for your email
grep -r "daybreak.ai" .

# Replace all occurrences
```

### Step 3: Add Public README

**Create a new README.md specifically for public use:**

```markdown
# Meeting Transcript Automation System

Automatically sync Google Meet transcripts from Google Drive to your Obsidian vault.

## What This Does

- Watches Google Drive for meeting transcript `.txt` files
- Syncs them to your Obsidian vault hourly
- Preserves timestamps and only copies new/updated files
- Runs automatically via macOS LaunchAgent

## Prerequisites

- macOS 10.15 or later
- Google Meet with recording enabled
- Google Apps Script converting transcripts to `.txt` files
- Google Drive Desktop installed and syncing
- Obsidian vault on your Mac

## Installation

See [INSTALLATION-GUIDE.md](./INSTALLATION-GUIDE.md) for complete setup instructions.

## Quick Start

1. Clone this repository
2. Configure paths in `scripts/sync-transcripts.sh`
3. Configure paths in `config/com.obsidian.synctranscripts.plist`
4. Follow installation guide

## License

MIT License - Feel free to use and modify for your own purposes.

## Related Projects

This works great with:
- [Google Apps Script for transcript conversion](#)
- [Obsidian backup automation](#)
```

### Step 4: Add LICENSE File

**Create MIT License:**
```bash
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

### Step 5: Add .gitignore

**Create appropriate .gitignore:**
```bash
cat > .gitignore << 'EOF'
# Logs
*.log
transcript-sync.log
transcript-sync.log.old

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Personal configuration (if you add it later)
config.local.sh

# Backup files
*.bak
*.backup
EOF
```

### Step 6: Remove Personal Data

**Check for and remove:**
- Personal meeting transcripts
- Any sample log files
- Screenshots with personal information
- Folder references to your specific Google Drive

```bash
# Remove log files if present
rm -f transcript-sync.log*

# Check for any sample files
ls -la docs/
ls -la examples/
```

### Step 7: Test Portability

**Create a test checklist:**

- [ ] All paths use `YOUR_USERNAME` placeholder
- [ ] All emails use `YOUR_EMAIL` placeholder
- [ ] No personal meeting transcripts included
- [ ] No actual log files included
- [ ] All documentation references generic paths
- [ ] LICENSE file added
- [ ] .gitignore file added
- [ ] README.md is public-friendly

### Step 8: Create GitHub Repository

**Initialize Git:**
```bash
cd ~/Desktop/meeting-transcript-system-public

# Initialize Git
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Meeting transcript automation system"
```

**Create and push to GitHub:**
```bash
# Create repo (requires GitHub CLI)
gh repo create meeting-transcript-system --public --source=. --remote=origin

# Push to GitHub
git push -u origin main
```

---

## Optional Enhancements for Public Release

### Add Examples Folder

```bash
mkdir examples
```

**Create example configuration:**
```bash
cat > examples/example-config.sh << 'EOF'
# Example Configuration
# Copy this to sync-transcripts.sh and update with your paths

GOOGLE_DRIVE_SOURCE="/Users/johndoe/Library/CloudStorage/GoogleDrive-john@example.com/My Drive/Meeting Transcripts as Text"
OBSIDIAN_DEST="/Users/johndoe/Obsidian Vault/Meeting Transcripts"
LOG_FILE="/Users/johndoe/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log"
EOF
```

### Add Screenshots

Take clean screenshots showing:
- Folder structure
- LaunchAgent status (`launchctl list | grep obsidian`)
- Sample log output (with no personal info)
- Obsidian with transcript files

Place in `docs/images/` folder.

### Add CONTRIBUTING.md

```markdown
# Contributing

Contributions are welcome! Here's how you can help:

## Reporting Issues

- Use GitHub Issues
- Include your macOS version
- Include relevant log output (remove personal info)

## Pull Requests

- Fork the repository
- Create a feature branch
- Test your changes
- Submit PR with clear description

## Code Style

- Use clear variable names
- Add comments for complex logic
- Follow existing bash script conventions
```

### Add CHANGELOG.md

```markdown
# Changelog

## [1.0.0] - 2025-11-17

### Added
- Initial release
- Automatic transcript syncing from Google Drive to Obsidian
- LaunchAgent for hourly automation
- Comprehensive documentation

### Features
- rsync-based sync (update only)
- Timestamp preservation
- Logging system
- macOS LaunchAgent integration
```

---

## Final Checklist

Before making public:

### Code Quality
- [ ] All paths genericized
- [ ] No hardcoded personal information
- [ ] Scripts have proper error handling
- [ ] Clear variable names and comments

### Documentation
- [ ] README.md is clear and comprehensive
- [ ] INSTALLATION-GUIDE.md has step-by-step instructions
- [ ] TROUBLESHOOTING.md covers common issues
- [ ] START-HERE.md provides quick overview

### Legal & Safety
- [ ] LICENSE file added
- [ ] No proprietary/confidential information
- [ ] No API keys or credentials
- [ ] .gitignore covers sensitive files

### Polish
- [ ] Screenshots added (optional)
- [ ] Examples provided
- [ ] CONTRIBUTING.md added (optional)
- [ ] CHANGELOG.md added (optional)

---

## Maintenance After Public Release

### Keep It Updated

1. **Monitor Issues**: Respond to user-reported problems
2. **Update Documentation**: As you learn edge cases
3. **Version Releases**: Tag releases with semantic versioning
4. **Test on Other Machines**: Verify portability

### Promote It

1. **Add to GitHub Topics**: `obsidian`, `automation`, `google-meet`, `macos`
2. **Share on Reddit**: r/ObsidianMD, r/automation
3. **Blog Post**: Write about your automation workflow
4. **Link from Other Projects**: Cross-reference with backup system

---

## Repository Structure for Public Release

```
meeting-transcript-system/
├── README.md (public-friendly)
├── LICENSE (MIT)
├── .gitignore
├── INSTALLATION-GUIDE.md
├── START-HERE.md
├── CHANGELOG.md (optional)
├── CONTRIBUTING.md (optional)
├── scripts/
│   └── sync-transcripts.sh (genericized)
├── config/
│   └── com.obsidian.synctranscripts.plist (genericized)
├── docs/
│   ├── TROUBLESHOOTING.md
│   ├── MAKING-IT-PUBLIC.md (this file)
│   └── images/ (optional screenshots)
└── examples/
    └── example-config.sh
```

---

## Example GitHub Description

**Repository Description:**
```
🤖 Automatically sync Google Meet transcripts from Google Drive to your Obsidian vault using rsync and macOS LaunchAgent
```

**Topics:**
```
obsidian automation google-meet macos bash rsync productivity knowledge-management meeting-notes launchd
```

**README Badges:**
```markdown
![macOS](https://img.shields.io/badge/macOS-10.15+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Bash](https://img.shields.io/badge/bash-5.0+-orange)
```

---

## Alternative: Keep It Private But Shareable

If you don't want a public repo but want to share with specific people:

1. **Create private GitHub repo**
2. **Genericize paths** (same as above)
3. **Add collaborators** as needed
4. **Share repo link** directly

This gives you version control and easy sharing without making it fully public.

---

*This guide helps you convert your personal automation into a shareable project while maintaining privacy and professionalism.*
