#!/usr/bin/env python3
"""
BKNS Wiki — Scheduled Cron Tasks
Các tác vụ tự động chạy định kỳ: lint, health check, auto-file, conflict report.

Được gọi từ system cron hoặc PM2 cron_restart.

Usage:
    python3 tools/cron_tasks.py --task lint              # Weekly wiki lint
    python3 tools/cron_tasks.py --task health            # Daily health check
    python3 tools/cron_tasks.py --task auto-file         # Weekly FAQ gap analysis
    python3 tools/cron_tasks.py --task conflicts         # Daily conflict scan
    python3 tools/cron_tasks.py --task dual-vote-check   # Hourly: alert if DISAGREE > 20
    python3 tools/cron_tasks.py --task daily-digest      # Daily 8h: v0.4 metrics digest
    python3 tools/cron_tasks.py --task all               # Run all tasks

Cron schedule suggestions:
    # Daily health check + conflict scan + digest at 7-8am
    0 7 * * * /usr/bin/python3 /wiki/tools/cron_tasks.py --task health 2>&1
    0 7 * * * /usr/bin/python3 /wiki/tools/cron_tasks.py --task conflicts 2>&1
    0 8 * * * /usr/bin/python3 /wiki/tools/cron_tasks.py --task daily-digest 2>&1

    # Hourly dual-vote DISAGREE alert (v0.4+)
    0 * * * * /usr/bin/python3 /wiki/tools/cron_tasks.py --task dual-vote-check 2>&1

    # Weekly lint + auto-file + promo-scrape on Monday 8-9am
    0 8 * * 1 /usr/bin/python3 /wiki/tools/cron_tasks.py --task lint 2>&1
    0 8 * * 1 /usr/bin/python3 /wiki/tools/cron_tasks.py --task auto-file 2>&1
    0 9 * * 1 /usr/bin/python3 /wiki/tools/cron_tasks.py --task promo-scrape 2>&1
"""
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.logger import log_entry
from lib.telegram import notify_skill, notify_error

WIKI_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = WIKI_ROOT / "logs"
CRON_LOG = LOGS_DIR / "cron-tasks.log"


def _run_python(script_path: str, args: list[str] = None) -> tuple[int, str]:
    """Run a Python script and return (returncode, output)."""
    cmd = [sys.executable, str(WIKI_ROOT / script_path)] + (args or [])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(WIKI_ROOT),
        timeout=300,  # 5 minute timeout per task
    )
    output = result.stdout + result.stderr
    return result.returncode, output


def _log_cron(task: str, status: str, detail: str):
    """Append entry to cron task log."""
    entry = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "task": task,
        "status": status,
        "detail": detail[:200],
    }
    try:
        with open(CRON_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def task_health_check():
    """Run wiki health check and notify if issues found."""
    print("🔍 Running wiki health check...")
    returncode, output = _run_python("tools/check_wiki_health.py")

    if returncode != 0:
        msg = f"❌ Health check failed:\n{output[:500]}"
        notify_error("cron-tasks", msg)
        _log_cron("health", "error", output[:200])
        return False

    # Count issues from output
    fail_count = output.count("🔴")
    warn_count = output.count("🟡")

    if fail_count > 0 or warn_count > 0:
        summary = f"⚠️ Wiki Health: {fail_count} errors, {warn_count} warnings\n"
        # Extract first few lines after the header
        lines = [l.strip() for l in output.split("\n") if l.strip() and "=" not in l]
        summary += "\n".join(lines[:10])
        notify_skill("cron-tasks", summary, severity="medium")

    _log_cron("health", "success", f"fail={fail_count} warn={warn_count}")
    print(f"✅ Health check done: {fail_count} errors, {warn_count} warnings")
    return True


def task_conflict_scan():
    """Scan for claim conflicts and notify if new ones found."""
    print("🔍 Scanning claim conflicts...")
    returncode, output = _run_python("tools/detect_conflicts.py", ["--json"])

    if returncode != 0:
        _log_cron("conflicts", "error", output[:200])
        return False

    try:
        result = json.loads(output)
        conflict_count = len(result.get("conflicts", []))
    except (json.JSONDecodeError, KeyError):
        conflict_count = -1

    if conflict_count > 0:
        notify_skill(
            "cron-tasks",
            f"📊 Conflict Scan: {conflict_count} claim conflicts detected.\n"
            f"Run: python3 tools/detect_conflicts.py để xem chi tiết",
            severity="medium",
        )

    _log_cron("conflicts", "success", f"conflicts={conflict_count}")
    print(f"✅ Conflict scan done: {conflict_count} conflicts")
    return True


def task_lint():
    """Run wiki lint check."""
    print("🔍 Running wiki lint...")
    returncode, output = _run_python("skills/lint-wiki/scripts/lint.py")

    status = "success" if returncode == 0 else "error"
    _log_cron("lint", status, output[:200])

    if returncode != 0:
        notify_error("cron-tasks", f"❌ Wiki lint failed:\n{output[:300]}")
        return False

    print("✅ Wiki lint done")
    return True


def task_auto_file():
    """Run auto-file FAQ gap analysis."""
    print("🔍 Running auto-file analysis...")
    returncode, output = _run_python("skills/auto-file/scripts/auto_file.py")

    status = "success" if returncode == 0 else "error"
    _log_cron("auto-file", status, output[:200])

    if returncode != 0:
        notify_error("cron-tasks", f"❌ Auto-file failed:\n{output[:300]}")
        return False

    print("✅ Auto-file analysis done")
    return True


def task_promo_scrape():
    """Weekly scrape of BKNS promotion page → update wiki/khuyen-mai/index.md."""
    print("🔍 Scraping BKNS promotions...")
    returncode, output = _run_python("tools/scrape_promotions.py")

    status = "success" if returncode == 0 else "error"
    _log_cron("promo-scrape", status, output[:200])

    if returncode != 0:
        notify_error("cron-tasks", f"❌ Promo scrape failed:\n{output[:300]}")
        return False

    # Check if new promos were found in output
    if "NEW promotions" in output:
        print("🆕 New promotions detected and wiki updated!")
    else:
        print("✅ Promo scrape done, no new promotions")
    return True


def _read_dual_vote_logs_since(hours: int) -> list[dict]:
    """Read dual-vote JSONL logs from the last N hours."""
    cutoff = datetime.now(tz=timezone.utc) - __import__("datetime").timedelta(hours=hours)
    entries = []
    log_dir = WIKI_ROOT / "logs"
    # dual-vote-YYYY-MM.jsonl — check current and previous month file
    from datetime import date
    today = date.today()
    candidates = [
        log_dir / f"dual-vote-{today.strftime('%Y-%m')}.jsonl",
        log_dir / f"extract-dual-{today.strftime('%Y-%m-%d')}.jsonl",
        log_dir / f"compile-dual-{today.strftime('%Y-%m-%d')}.jsonl",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        # Parse ts — handles +07:00 offset
                        ts_str = entry.get("ts", "")
                        if ts_str:
                            from datetime import datetime as _dt
                            ts = _dt.fromisoformat(ts_str).astimezone(timezone.utc)
                            if ts >= cutoff:
                                entries.append(entry)
                    except (json.JSONDecodeError, ValueError):
                        continue
        except OSError:
            continue
    return entries


def _read_openai_cost_since(hours: int) -> float:
    """Return total OpenAI cost (USD) from logs in the last N hours."""
    cutoff = datetime.now(tz=timezone.utc) - __import__("datetime").timedelta(hours=hours)
    total = 0.0
    from datetime import date
    today = date.today()
    log_path = WIKI_ROOT / "logs" / f"openai-calls-{today.strftime('%Y-%m')}.jsonl"
    if not log_path.exists():
        return 0.0
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    ts_str = entry.get("ts", "")
                    if ts_str:
                        from datetime import datetime as _dt
                        ts = _dt.fromisoformat(ts_str).astimezone(timezone.utc)
                        if ts >= cutoff:
                            total += float(entry.get("cost_usd", 0))
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
    except OSError:
        pass
    return total


def task_dual_vote_disagree_check():
    """Check dual-vote DISAGREE rate in last 1 hour. Alert if > 20."""
    print("🗳️  Checking dual-vote DISAGREE rate (last 1h)...")
    entries = _read_dual_vote_logs_since(hours=1)
    disagree_count = sum(1 for e in entries if e.get("status") == "DISAGREE")
    total_count = len(entries)

    _log_cron("dual-vote-check", "success", f"disagree={disagree_count} total={total_count}")

    if disagree_count > 20:
        msg = (
            f"⚠️ Dual-Vote ALERT: {disagree_count} DISAGREE trong 1h gần nhất "
            f"({total_count} total)\n"
            f"Kiểm tra .review-queue/ để xử lý thủ công"
        )
        notify_skill("cron-tasks", msg, severity="high")
        print(f"📱 Alert sent: {disagree_count} DISAGREE votes")
    else:
        print(f"✅ Dual-vote OK: {disagree_count}/{total_count} DISAGREE (threshold=20)")
    return True


def task_daily_v04_digest():
    """Daily 8h digest: builds, cost, reviews, bot questions (v0.4 metrics)."""
    print("📊 Generating daily v0.4 digest...")

    from datetime import date, timedelta
    yesterday = date.today()  # runs at 8h for "last 24h"

    # Dual-vote stats (last 24h)
    entries = _read_dual_vote_logs_since(hours=24)
    agree = sum(1 for e in entries if e.get("status") == "AGREE")
    partial = sum(1 for e in entries if e.get("status") == "PARTIAL")
    disagree = sum(1 for e in entries if e.get("status") == "DISAGREE")
    total_votes = len(entries)
    agree_rate = (agree / total_votes * 100) if total_votes else 0

    # Cost (Gemini from dual-vote logs, OpenAI separately)
    gemini_cost = sum(float(e.get("cost_usd_a", 0)) for e in entries)
    openai_cost = _read_openai_cost_since(hours=24)
    # Also pick up any direct cost from dual-vote log that aggregates both
    combined_cost = sum(float(e.get("cost_usd_total", 0)) for e in entries)
    display_cost = combined_cost if combined_cost > 0 else gemini_cost + openai_cost

    # Review queue (claims waiting for human)
    review_queue_dir = WIKI_ROOT / "claims" / ".review-queue"
    pending_reviews = len(list(review_queue_dir.glob("*.json"))) if review_queue_dir.exists() else 0

    # Bot queries (last 24h from query log)
    query_log = WIKI_ROOT / "logs" / f"wiki-bot-{yesterday.strftime('%Y-%m-%d')}.jsonl"
    bot_answered = 0
    bot_unanswered = 0
    if query_log.exists():
        try:
            with open(query_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        q = json.loads(line.strip())
                        if q.get("status") == "answered":
                            bot_answered += 1
                        elif q.get("status") in ("no_answer", "fallback", "error"):
                            bot_unanswered += 1
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            pass

    # Builds in last 24h
    pipeline_log = WIKI_ROOT / "logs" / "pipeline-runs.jsonl"
    builds_24h = 0
    if pipeline_log.exists():
        from datetime import datetime as _dt
        cutoff = _dt.now(tz=timezone.utc) - __import__("datetime").timedelta(hours=24)
        try:
            with open(pipeline_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        ts = _dt.fromisoformat(entry.get("ts", "")).astimezone(timezone.utc)
                        if ts >= cutoff:
                            builds_24h += 1
                    except (json.JSONDecodeError, ValueError):
                        continue
        except OSError:
            pass

    msg = (
        f"📊 BKNS Wiki Daily Digest — {yesterday.strftime('%Y-%m-%d')}\n"
        f"{'─' * 35}\n"
        f"🏗️  Builds (24h):      {builds_24h}\n"
        f"💰 Cost (24h):        ${display_cost:.3f} (Gemini+OpenAI)\n"
        f"🗳️  Dual-Vote (24h):   {total_votes} votes\n"
        f"   AGREE  {agree} ({agree_rate:.0f}%) | PARTIAL {partial} | DISAGREE {disagree}\n"
        f"📥 Review queue:      {pending_reviews} chờ duyệt\n"
        f"🤖 Bot (24h):         {bot_answered} answered / {bot_unanswered} unanswered"
    )

    notify_skill("cron-tasks", msg, severity="low")
    _log_cron("daily-digest", "success",
              f"builds={builds_24h} cost={display_cost:.3f} disagree={disagree} queue={pending_reviews}")
    print(f"✅ Daily digest sent")
    return True


TASKS = {
    "health": task_health_check,
    "conflicts": task_conflict_scan,
    "lint": task_lint,
    "auto-file": task_auto_file,
    "promo-scrape": task_promo_scrape,
    "dual-vote-check": task_dual_vote_disagree_check,
    "daily-digest": task_daily_v04_digest,
}


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Cron Tasks")
    parser.add_argument(
        "--task",
        choices=list(TASKS.keys()) + ["all"],
        required=True,
        help="Task to run",
    )
    args = parser.parse_args()

    start = datetime.now(tz=timezone.utc)
    print(f"\n[{start.strftime('%Y-%m-%d %H:%M UTC')}] Running cron task: {args.task}")

    tasks_to_run = list(TASKS.items()) if args.task == "all" else [(args.task, TASKS[args.task])]

    results = {}
    for name, func in tasks_to_run:
        try:
            results[name] = func()
        except subprocess.TimeoutExpired:
            results[name] = False
            _log_cron(name, "timeout", "Task exceeded 5 minute limit")
            print(f"⚠️ Task '{name}' timed out")
        except Exception as e:
            results[name] = False
            _log_cron(name, "error", str(e))
            print(f"❌ Task '{name}' failed: {e}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    elapsed = (datetime.now(tz=timezone.utc) - start).seconds
    print(f"\n✅ {passed}/{total} tasks passed in {elapsed}s")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
