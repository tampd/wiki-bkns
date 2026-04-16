#!/usr/bin/env python3
"""
Dual-Vote Daily Digest — gửi Telegram báo cáo hàng ngày lúc 8h sáng.

Cài cron:
  0 8 * * * cd /wiki && python skills/dual-vote/scripts/daily_digest.py >> logs/daily-digest.log 2>&1

Hoặc chạy thủ công:
  python skills/dual-vote/scripts/daily_digest.py
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.config import REVIEW_QUEUE_DIR, LOGS_DIR
from lib.telegram import send_report

VN_TZ = timezone(timedelta(hours=7))


def count_pending() -> int:
    """Count pending (unresolved) items in review queue."""
    if not REVIEW_QUEUE_DIR.exists():
        return 0
    return sum(
        1 for f in REVIEW_QUEUE_DIR.iterdir()
        if f.is_file() and f.suffix == ".json"
    )


def count_resolved_today() -> int:
    """Count items resolved today in the resolved/ folder."""
    resolved_dir = REVIEW_QUEUE_DIR / "resolved"
    if not resolved_dir.exists():
        return 0
    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    count = 0
    for f in resolved_dir.iterdir():
        if not f.is_file() or f.suffix != ".json":
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            decided_at = data.get("decided_at", "")
            if decided_at.startswith(today):
                count += 1
        except Exception:
            pass
    return count


def load_vote_stats_today() -> dict:
    """Read today's votes from dual-vote-YYYY-MM.jsonl."""
    month_str = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"dual-vote-{month_str}.jsonl"
    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")

    stats = {"total": 0, "AGREE": 0, "PARTIAL": 0, "DISAGREE": 0, "DEGRADED": 0, "cost": 0.0}

    if not log_file.exists():
        return stats

    for line in log_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if not entry.get("ts", "").startswith(today):
                continue
            stats["total"] += 1
            status = entry.get("status", "")
            if status in stats:
                stats[status] += 1
            elif "DEGRADED" in status:
                stats["DEGRADED"] += 1
            stats["cost"] += entry.get("cost_usd_total", 0.0) or 0.0
        except Exception:
            pass

    return stats


def send_daily_digest():
    now = datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M")
    pending = count_pending()
    resolved_today = count_resolved_today()
    today_stats = load_vote_stats_today()

    total = today_stats["total"]
    agree_rate = (today_stats["AGREE"] / total * 100) if total > 0 else 0
    disagree_rate = (today_stats["DISAGREE"] / total * 100) if total > 0 else 0

    lines = [
        f"📊 Dual-Vote Daily Report — {now}",
        "",
        f"🗂️ *Queue:* {pending} items chờ review",
        f"✅ *Đã xử lý hôm nay:* {resolved_today} items",
        "",
        f"📈 *Votes hôm nay:* {total} tổng",
    ]

    if total > 0:
        lines += [
            f"  • AGREE: {today_stats['AGREE']} ({agree_rate:.0f}%)",
            f"  • PARTIAL: {today_stats['PARTIAL']}",
            f"  • DISAGREE: {today_stats['DISAGREE']} ({disagree_rate:.0f}%)",
            f"  • DEGRADED: {today_stats['DEGRADED']}",
            f"  • Cost hôm nay: ${today_stats['cost']:.4f}",
        ]

    if pending >= 5:
        lines += ["", f"⚠️ *Cần review gấp:* {pending} items đang chờ!"]

    content = "\n".join(lines)
    success = send_report("Dual-Vote Daily Digest", content)

    if success:
        print(f"[OK] Daily digest sent at {now}")
    else:
        print(f"[WARN] Daily digest failed at {now}")

    return success


if __name__ == "__main__":
    send_daily_digest()
