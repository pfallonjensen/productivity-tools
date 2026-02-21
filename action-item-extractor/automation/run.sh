#!/bin/bash
# Run Action Item Extractor
# This script runs the extraction pipeline using your config files.
#
# Usage:
#   ./automation/run.sh                    # Uses default paths
#   ./automation/run.sh -p /path/to/persona.yaml -c /path/to/config.yaml

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default config paths
PERSONA_PATH="${PROJECT_DIR}/persona.yaml"
CONFIG_PATH="${PROJECT_DIR}/config.yaml"

# Parse arguments
while getopts "p:c:" opt; do
    case $opt in
        p) PERSONA_PATH="$OPTARG" ;;
        c) CONFIG_PATH="$OPTARG" ;;
        *) echo "Usage: $0 [-p persona.yaml] [-c config.yaml]"; exit 1 ;;
    esac
done

# Validate config files exist
if [ ! -f "$PERSONA_PATH" ]; then
    echo "ERROR: persona.yaml not found at $PERSONA_PATH"
    echo "  Copy persona.example.yaml to persona.yaml and fill it out"
    exit 1
fi

if [ ! -f "$CONFIG_PATH" ]; then
    echo "ERROR: config.yaml not found at $CONFIG_PATH"
    echo "  Copy config.example.yaml to config.yaml and fill it out"
    exit 1
fi

# Activate venv if it exists
if [ -d "${PROJECT_DIR}/venv" ]; then
    source "${PROJECT_DIR}/venv/bin/activate"
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Starting action item extraction..."

# Run the extractor
python3 -c "
from engine.extractor import Extractor
import sys

extractor = Extractor(
    persona_path='${PERSONA_PATH}',
    config_path='${CONFIG_PATH}'
)
result = extractor.run()
print(f'Extracted: {result[\"raw_items\"]} raw items -> {result[\"extracted\"]} filtered -> {result[\"saved\"]} saved')
"

EXIT_CODE=$?

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$TIMESTAMP] Extraction completed successfully"
else
    echo "[$TIMESTAMP] Extraction failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
