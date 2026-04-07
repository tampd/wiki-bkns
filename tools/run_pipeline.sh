#!/bin/bash
# BKNS Wiki — Pipeline Runner (for cronjob)
# Chạy full pipeline: dedup → extract → approve → compile
# Usage: bash tools/run_pipeline.sh [--limit N]

set -euo pipefail

WIKI_DIR="/home/openclaw/wiki"
LOG_DIR="$WIKI_DIR/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/pipeline_run_${TIMESTAMP}.log"

# Ensure log dir exists
mkdir -p "$LOG_DIR"

echo "=== BKNS Wiki Pipeline Started: $(date) ===" | tee "$LOG_FILE"

# Set environment
export PYTHONPATH="$WIKI_DIR"
cd "$WIKI_DIR"

# Parse args
LIMIT_ARG=""
if [ "${1:-}" = "--limit" ] && [ -n "${2:-}" ]; then
    LIMIT_ARG="--limit $2"
fi

# Run full pipeline
python3 tools/batch_pipeline.py full $LIMIT_ARG 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "=== Pipeline Finished: $(date) (exit: $EXIT_CODE) ===" | tee -a "$LOG_FILE"

# Rotate old logs (keep last 30)
cd "$LOG_DIR"
ls -t pipeline_run_*.log 2>/dev/null | tail -n +31 | xargs -r rm --

exit $EXIT_CODE
