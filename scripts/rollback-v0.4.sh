#!/bin/bash
# =============================================================================
# BKNS Wiki — Rollback v0.4 → v0.3
# Dùng khi v0.4 gặp sự cố production nghiêm trọng
# Usage: bash scripts/rollback-v0.4.sh [--dry-run]
# =============================================================================
set -e

WIKI_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$WIKI_ROOT"

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY-RUN mode — không có thay đổi thực tế"
fi

run() {
    if $DRY_RUN; then
        echo "  [dry-run] $*"
    else
        "$@"
    fi
}

echo "======================================================"
echo "  BKNS Wiki Rollback: v0.4 → v0.3"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================"

# ── 1. Kiểm tra backup tồn tại ─────────────────────────────
echo ""
echo "Step 1 — Verify backup exists..."
if [ ! -d "wiki/products.v0.3-backup" ]; then
    if $DRY_RUN; then
        echo "  ⚠️  [dry-run] wiki/products.v0.3-backup CHƯA tồn tại"
        echo "  ⚠️  Backup sẽ được tạo khi chạy Bước 1 (promote wiki v0.4)"
        echo "  ℹ️  Snapshot v0.3 vẫn còn trong: build/snapshots/v0.3-pre-upgrade-2026-04-13/"
        echo "  ℹ️  [dry-run] Giả sử backup tồn tại → tiếp tục dry-run..."
    else
        echo "❌ ERROR: wiki/products.v0.3-backup không tồn tại!"
        echo "   Kiểm tra: ls wiki/products*.v0.3*"
        echo "   Snapshot v0.3 vẫn còn trong: build/snapshots/v0.3-pre-upgrade-2026-04-13/"
        exit 1
    fi
else
    echo "✅ Backup confirmed: wiki/products.v0.3-backup"
fi

# ── 2. Lưu v0.4 (nếu cần debug sau) ───────────────────────
echo ""
echo "Step 2 — Archive failed v0.4 wiki..."
if [ -d "wiki/products" ]; then
    V04_ARCHIVE="wiki/products.v0.4-failed-$(date +%Y%m%d-%H%M%S)"
    run mv wiki/products "$V04_ARCHIVE"
    echo "✅ Archived: $V04_ARCHIVE"
else
    echo "  ℹ️  wiki/products không tồn tại, bỏ qua"
fi

# ── 3. Restore v0.3 ────────────────────────────────────────
echo ""
echo "Step 3 — Restore v0.3 wiki..."
run cp -r wiki/products.v0.3-backup wiki/products
echo "✅ Restored: wiki/products (from backup)"

# ── 4. Tắt v0.4 feature flags ─────────────────────────────
echo ""
echo "Step 4 — Disable v0.4 feature flags..."
if [ -f ".env" ]; then
    run sed -i 's/^USE_PRO_NEW=true/USE_PRO_NEW=false/' .env
    run sed -i 's/^DUAL_VOTE_ENABLED=true/DUAL_VOTE_ENABLED=false/' .env
    echo "✅ Flags disabled: USE_PRO_NEW=false, DUAL_VOTE_ENABLED=false"
else
    echo "  ⚠️  .env không tìm thấy, bỏ qua flag reset"
fi

# ── 5. Tạo restore snapshot ────────────────────────────────
echo ""
echo "Step 5 — Create restore snapshot..."
if [ -f "skills/build-snapshot/scripts/snapshot.py" ]; then
    run python3 skills/build-snapshot/scripts/snapshot.py --version v0.3-restored
    echo "✅ Restore snapshot created"
else
    echo "  ⚠️  snapshot.py không tìm thấy, bỏ qua"
fi

# ── 6. Restart services ────────────────────────────────────
echo ""
echo "Step 6 — Restart PM2 services..."
if command -v pm2 &>/dev/null; then
    run pm2 restart all
    echo "✅ PM2 restarted"
else
    echo "  ⚠️  pm2 không tìm thấy — restart thủ công nếu cần"
fi

# ── 7. Log rollback event ──────────────────────────────────
echo ""
echo "Step 7 — Log rollback event..."
LOG_FILE="logs/rollback-v0.4.log"
ENTRY="{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"rollback_v04_to_v03\",\"dry_run\":$DRY_RUN,\"operator\":\"$USER\"}"
if ! $DRY_RUN; then
    echo "$ENTRY" >> "$LOG_FILE"
fi
echo "✅ Logged to $LOG_FILE"

# ── Done ───────────────────────────────────────────────────
echo ""
echo "======================================================"
if $DRY_RUN; then
    echo "  ✅ DRY-RUN completed — không có thay đổi"
else
    echo "  ✅ Rollback hoàn tất — v0.3 đang active"
    echo ""
    echo "  Xác minh: pm2 logs bkns-wiki-bot --lines 50"
    echo "  Xác minh: grep DUAL_VOTE .env"
fi
echo "======================================================"
