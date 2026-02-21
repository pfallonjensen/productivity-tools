#!/bin/bash

# Run Extract Tasks — Two-Step Pipeline
# Step 1: Python collects from all sources + noise filter (~30 seconds)
# Step 2: Claude Code semantic triage on candidates
#
# Architecture: Python handles I/O (fast, parallel, no context limit).
# Claude Code handles reasoning (semantic triage, implied asks, context).
#
# Usage:
#   ./run-extract-tasks.sh                          # Uses default paths
#   ./run-extract-tasks.sh --persona /path/to/persona.yaml --config /path/to/config.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CANDIDATES_DIR="/tmp/action-item-candidates"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"
TRIAGE_PROMPT="$SCRIPT_DIR/prompts/triage.md"
LOG_FILE="$SCRIPT_DIR/extract-tasks.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
COLLECT_TIMEOUT=120   # 2 minutes for Python collection
TRIAGE_TIMEOUT=300    # 5 minutes per Claude triage batch
MAX_RETRIES=2

# Default persona/config paths (override with --persona / --config)
PERSONA_PATH="$SCRIPT_DIR/persona.yaml"
CONFIG_PATH="$SCRIPT_DIR/config.yaml"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --persona) PERSONA_PATH="$2"; shift 2 ;;
        --config)  CONFIG_PATH="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Ensure PATH includes homebrew binaries (required for LaunchAgent environment)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Load environment variables from .env if it exists (look in script dir and parent)
for envfile in "$SCRIPT_DIR/.env" "$SCRIPT_DIR/../.env"; do
    if [ -f "$envfile" ]; then
        source "$envfile"
        break
    fi
done

# --- Prerequisite Checks ---

if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: Python venv not found at $VENV_PYTHON"
    echo "  Set up with: cd $SCRIPT_DIR && python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

if [ ! -f "$PERSONA_PATH" ]; then
    echo "ERROR: Persona file not found at $PERSONA_PATH"
    echo "  Copy persona.example.yaml to persona.yaml and customize it."
    exit 1
fi

if [ ! -f "$CONFIG_PATH" ]; then
    echo "ERROR: Config file not found at $CONFIG_PATH"
    echo "  Copy config.example.yaml to config.yaml and customize it."
    exit 1
fi

if [ ! -f "$TRIAGE_PROMPT" ]; then
    echo "ERROR: Triage prompt not found at $TRIAGE_PROMPT"
    exit 1
fi

# Find claude CLI
CLAUDE_BIN=""
for bin in /opt/homebrew/bin/claude /usr/local/bin/claude; do
    if [ -x "$bin" ]; then
        CLAUDE_BIN="$bin"
        break
    fi
done

if [ -z "$CLAUDE_BIN" ]; then
    # Try PATH
    if command -v claude &> /dev/null; then
        CLAUDE_BIN="$(command -v claude)"
    else
        echo "ERROR: Claude CLI not found"
        echo "  Install with: npm install -g @anthropic-ai/claude-code"
        exit 1
    fi
fi

# Check authentication
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo "Using ANTHROPIC_API_KEY for authentication"
elif [ -n "${CLAUDE_CODE_USE_BEDROCK:-}" ] || [ -n "${CLAUDE_CODE_USE_VERTEX:-}" ]; then
    echo "Using cloud provider authentication"
else
    echo "Using OAuth authentication (tokens expire in 8-12 hours)"
    echo "  For reliable automation, set ANTHROPIC_API_KEY in .env"
fi

log "=========================================="
log "Starting Task Extraction (Two-Step Pipeline)"
log "=========================================="

# ============================================
# STEP 1: Python Data Collection + Noise Filter
# ============================================
log "Step 1: Collecting from all sources + noise filter..."

rm -rf "$CANDIDATES_DIR"

COLLECT_OUTPUT=$("$VENV_PYTHON" "$SCRIPT_DIR/collect.py" "$CANDIDATES_DIR" \
    --persona "$PERSONA_PATH" \
    --config "$CONFIG_PATH" 2>&1)
COLLECT_EXIT=$?

echo "$COLLECT_OUTPUT" | tee -a "$LOG_FILE"

if [ $COLLECT_EXIT -ne 0 ]; then
    log "Step 1 failed: Data collection error (exit code $COLLECT_EXIT)"
    exit 1
fi

# Count batch files
BATCH_COUNT=$(ls "$CANDIDATES_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$BATCH_COUNT" -eq 0 ]; then
    log "No candidates produced — nothing to triage"
    exit 0
fi

log "Step 1 complete: $BATCH_COUNT batch file(s) in $CANDIDATES_DIR"

# ============================================
# STEP 2: Claude Code Semantic Triage
# ============================================
log "Step 2: Claude Code semantic triage..."

# Read the triage prompt template
TRIAGE_TEMPLATE=$(cat "$TRIAGE_PROMPT")

TRIAGE_EXIT=0
BATCH_NUM=0
TEMP_OUTPUT=$(mktemp)

for BATCH_FILE in "$CANDIDATES_DIR"/*.json; do
    BATCH_NUM=$((BATCH_NUM + 1))
    log "  Processing batch $BATCH_NUM/$BATCH_COUNT: $(basename "$BATCH_FILE")"

    # Inject the batch file path into the prompt
    PROMPT="${TRIAGE_TEMPLATE//__BATCH_FILE__/$BATCH_FILE}"

    RETRY_COUNT=0
    BATCH_EXIT=1

    while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ $BATCH_EXIT -ne 0 ]; do
        if [ $RETRY_COUNT -gt 0 ]; then
            log "  Retry attempt $RETRY_COUNT for batch $BATCH_NUM..."
            sleep 5
        fi

        # Run Claude triage with timeout
        # MCP tools enabled for Google source collection (Gmail, Docs) during triage
        "$CLAUDE_BIN" -p "$PROMPT" \
            --allowedTools "Read,Write,Glob,mcp__google-workspace__search_gmail_messages,mcp__google-workspace__get_gmail_messages_content_batch,mcp__google-workspace__get_gmail_message_content,mcp__google-workspace__get_doc_as_markdown,mcp__google-workspace__get_doc_content" > "$TEMP_OUTPUT" 2>&1 &
        CLAUDE_PID=$!

        # Wait with timeout
        WAITED=0
        while kill -0 $CLAUDE_PID 2>/dev/null && [ $WAITED -lt $TRIAGE_TIMEOUT ]; do
            sleep 5
            WAITED=$((WAITED + 5))
        done

        if kill -0 $CLAUDE_PID 2>/dev/null; then
            log "  Triage timed out after ${TRIAGE_TIMEOUT}s - killing process"
            kill -9 $CLAUDE_PID 2>/dev/null
            wait $CLAUDE_PID 2>/dev/null
            BATCH_EXIT=124
            OUTPUT="Timed out after ${TRIAGE_TIMEOUT}s"
        else
            wait $CLAUDE_PID
            BATCH_EXIT=$?
            OUTPUT=$(cat "$TEMP_OUTPUT")
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))

        # Check for auth errors — don't retry
        if echo "$OUTPUT" | grep -q "OAuth token has expired\|authentication_error\|401"; then
            log "  Authentication error during triage"
            break
        fi

        if [ $BATCH_EXIT -ne 0 ] && ! echo "$OUTPUT" | grep -q "OAuth\|authentication"; then
            log "  Triage failed, may retry..."
        fi
    done

    echo "$OUTPUT" | tee -a "$LOG_FILE"

    if [ $BATCH_EXIT -ne 0 ]; then
        log "  Batch $BATCH_NUM failed (exit code $BATCH_EXIT)"
        TRIAGE_EXIT=$BATCH_EXIT
    else
        log "  Batch $BATCH_NUM complete"
    fi
done

rm -f "$TEMP_OUTPUT"

log "=========================================="
if [ $TRIAGE_EXIT -eq 0 ]; then
    log "Extraction completed successfully ($BATCH_COUNT batch(es) triaged)"
else
    log "Extraction failed with exit code $TRIAGE_EXIT"
fi

exit $TRIAGE_EXIT
