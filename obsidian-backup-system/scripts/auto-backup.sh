#!/bin/bash

# Obsidian Vault Auto-Backup Script
# Automatically commits and pushes changes to GitHub

# Change to vault directory
cd "/Users/fallonjensen/Obsidian Vault" || exit 1

# Save current active GitHub account
CURRENT_ACCOUNT=$(gh auth status 2>&1 | grep "Active account: true" -B 1 | grep "Logged in" | sed 's/.*account \(.*\) (.*/\1/')

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet; then
    echo "✓ No changes to commit"
    exit 0
fi

# Add all changes
git add .

# Create commit with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Auto-backup: $TIMESTAMP"

# Switch to personal GitHub account for this repo
gh auth switch -u pfallonjensen 2>/dev/null

# Push to GitHub
if git push; then
    echo "✓ Successfully backed up to GitHub at $TIMESTAMP"

    # Restore original account if it was the work account
    if [ "$CURRENT_ACCOUNT" = "fallonjensen-Daybreak" ]; then
        gh auth switch -u fallonjensen-Daybreak 2>/dev/null
        echo "✓ Restored work account (fallonjensen-Daybreak)"
    fi
else
    echo "✗ Failed to push to GitHub. Check your connection."

    # Restore original account even on failure
    if [ "$CURRENT_ACCOUNT" = "fallonjensen-Daybreak" ]; then
        gh auth switch -u fallonjensen-Daybreak 2>/dev/null
    fi
    exit 1
fi
