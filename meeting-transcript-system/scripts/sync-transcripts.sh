#!/bin/bash

# Meeting Transcript Sync Script
# Syncs meeting transcripts from Google Drive to Obsidian Vault
# Part of the Meeting Transcript Automation System

# Paths
GOOGLE_DRIVE_SOURCE="/Users/fallonjensen/Library/CloudStorage/GoogleDrive-fallon.jensen@daybreak.ai/My Drive/Meeting Transcripts as Text"
OBSIDIAN_DEST="/Users/fallonjensen/Obsidian Vault/Meeting Transcripts"
LOG_FILE="/Users/fallonjensen/Obsidian Vault/Automations/meeting-transcript-system/transcript-sync.log"

# Timestamp for logging
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# Start sync
log_message "=== Starting transcript sync ==="

# Check if source directory exists
if [ ! -d "$GOOGLE_DRIVE_SOURCE" ]; then
    log_message "ERROR: Google Drive source directory not found: $GOOGLE_DRIVE_SOURCE"
    echo "ERROR: Google Drive source directory not found"
    exit 1
fi

# Check if destination directory exists
if [ ! -d "$OBSIDIAN_DEST" ]; then
    log_message "ERROR: Obsidian destination directory not found: $OBSIDIAN_DEST"
    echo "ERROR: Obsidian destination directory not found"
    exit 1
fi

# Perform rsync
# -a: archive mode (preserves permissions, timestamps, etc.)
# -u: skip files that are newer on the receiver
# --delete: delete files in dest that don't exist in source (optional - commented out for safety)
# -v: verbose
# --stats: show statistics

log_message "Running rsync from Google Drive to Obsidian..."

RSYNC_OUTPUT=$(rsync -au --stats "$GOOGLE_DRIVE_SOURCE/" "$OBSIDIAN_DEST/" 2>&1)
RSYNC_EXIT_CODE=$?

if [ $RSYNC_EXIT_CODE -eq 0 ]; then
    # Extract number of transferred files from rsync output
    FILES_TRANSFERRED=$(echo "$RSYNC_OUTPUT" | grep "Number of files transferred" | awk '{print $5}')

    if [ -z "$FILES_TRANSFERRED" ]; then
        FILES_TRANSFERRED="0"
    fi

    log_message "SUCCESS: Sync completed. Files transferred: $FILES_TRANSFERRED"
    echo "✓ Sync completed successfully. Files transferred: $FILES_TRANSFERRED"
else
    log_message "ERROR: Rsync failed with exit code $RSYNC_EXIT_CODE"
    log_message "Output: $RSYNC_OUTPUT"
    echo "✗ Sync failed. Check log for details: $LOG_FILE"
    exit 1
fi

log_message "=== Sync complete ==="

# Optional: Show summary
FILE_COUNT=$(ls -1 "$OBSIDIAN_DEST" | wc -l)
log_message "Total files in Obsidian: $FILE_COUNT"

exit 0
