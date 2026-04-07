#!/bin/bash
# Quick status check for BKNS Wiki Pipeline
# Usage: bash tools/check_overnight.sh

echo "=========================================="
echo "BKNS Wiki Pipeline — Morning Check"
echo "Time: $(date)"
echo "=========================================="

echo ""
echo "📋 Process Status:"
ps aux | grep batch_pipeline | grep -v grep
if [ $? -ne 0 ]; then
    echo "  ✅ Pipeline finished (no running process)"
fi

echo ""
echo "📊 Last 20 lines of batch log:"
tail -20 /home/openclaw/wiki/logs/batch_pipeline.log

echo ""
echo "📊 Pipeline overnight log summary:"
if [ -f /home/openclaw/wiki/logs/pipeline_overnight_20260406.log ]; then
    echo "  Lines: $(wc -l < /home/openclaw/wiki/logs/pipeline_overnight_20260406.log)"
    echo "  Last 10 lines:"
    tail -10 /home/openclaw/wiki/logs/pipeline_overnight_20260406.log
fi

echo ""
echo "📊 Quick claims count:"
echo "  Draft claims: $(find /home/openclaw/wiki/claims/.drafts -name '*.yaml' 2>/dev/null | wc -l)"
echo "  Approved claims: $(find /home/openclaw/wiki/claims/approved -name '*.yaml' 2>/dev/null | wc -l)"

echo ""
echo "📊 Pending vs Extracted raw files:"
echo "  Pending: $(find /home/openclaw/wiki/raw -name '*.md' -exec grep -l 'status: pending_extract' {} \; 2>/dev/null | wc -l)"
echo "  Extracted: $(find /home/openclaw/wiki/raw -name '*.md' -exec grep -l 'status: extracted' {} \; 2>/dev/null | wc -l)"

echo ""
echo "📊 Wiki drafts:"
find /home/openclaw/wiki/wiki/.drafts -name '*.md' 2>/dev/null -exec echo "  {}" \;

echo ""
echo "=========================================="
echo "Full status:"
cd /home/openclaw/wiki && PYTHONPATH=/home/openclaw/wiki python3 tools/batch_pipeline.py status
