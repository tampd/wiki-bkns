#!/usr/bin/env python3
"""
Librarian Processor — batch-process .librarian/inbox/ → wiki targets

Modes:
  --mode cron   : nightly run (00:00 VN), Telegram digest
  --mode now    : on-demand (triggered from web UI), prints JSON report
  --mode dry    : scan + plan only, no file moves

Routing rules (mirror tools/librarian_gemini.py classify):
  - type=wiki-page      → wiki/products/<category>/<slug>.md
  - type=claim          → claims/staging/<slug>.yaml
  - type=raw-doc        → raw/librarian/<YYYY-MM-DD>/<filename>
  - type=note           → wiki/products/<category>/_notes/<slug>.md
  - type=asset          → wiki/assets/images/<filename>

Outputs:
  - .librarian/processed/<YYYY-MM-DD>/<id>.{ext,meta.json}
  - .librarian/logs/last-run.json
  - Telegram digest (cron mode only)
"""
import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

LIB_ROOT = ROOT / ".librarian"
INBOX_ROOT = LIB_ROOT / "inbox"
PROCESSED_ROOT = LIB_ROOT / "processed"
LOGS_ROOT = LIB_ROOT / "logs"
LOCK_FILE = LIB_ROOT / ".processor.lock"

WIKI_PRODUCTS = ROOT / "wiki" / "products"
CLAIMS_STAGING = ROOT / "claims" / "staging"
RAW_LIBRARIAN = ROOT / "raw" / "librarian"
WIKI_ASSETS = ROOT / "wiki" / "assets" / "images"

CATEGORIES = {
    "email", "hosting", "other", "server", "software",
    "ssl", "ten-mien", "uncategorized", "vps",
}


def slugify(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"\.[a-z0-9]+$", "", s)  # strip ext
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "item"


def acquire_lock() -> bool:
    LIB_ROOT.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists():
        try:
            age = time.time() - LOCK_FILE.stat().st_mtime
            if age < 1800:  # 30 min stale threshold
                return False
        except OSError:
            pass
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def collect_items() -> list[dict]:
    """Find every .meta.json in inbox/* (excluding _review)."""
    items = []
    if not INBOX_ROOT.exists():
        return items
    for day_dir in sorted(INBOX_ROOT.iterdir()):
        if not day_dir.is_dir():
            continue
        if day_dir.name == "_review":
            continue  # skip — needs human triage
        for meta_path in sorted(day_dir.glob("*.meta.json")):
            try:
                meta = json.loads(meta_path.read_text())
            except Exception as e:
                items.append({"_error": f"bad meta {meta_path}: {e}", "meta_path": str(meta_path)})
                continue
            stored = day_dir / meta.get("stored_name", "")
            if not stored.exists():
                items.append({"_error": f"missing payload {stored}", "meta_path": str(meta_path)})
                continue
            meta["_meta_path"] = str(meta_path)
            meta["_stored_path"] = str(stored)
            items.append(meta)
    return items


def resolve_target(meta: dict) -> Path:
    """Determine final target path on disk."""
    cls = meta.get("classification") or {}
    cat = cls.get("category", "uncategorized")
    if cat not in CATEGORIES:
        cat = "uncategorized"
    typ = cls.get("type", "raw-doc")
    name = meta.get("original_name") or meta.get("stored_name") or "item"
    slug = slugify(name)
    ext = (meta.get("ext") or Path(name).suffix or "").lower()
    today = datetime.now().strftime("%Y-%m-%d")

    suggested = (cls.get("suggested_path") or "").strip()
    # Prefer LLM suggestion if it lives under a sane base
    if suggested:
        sp = Path(suggested)
        first = sp.parts[0] if sp.parts else ""
        if first in {"wiki", "claims", "raw"}:
            cand = ROOT / sp
            return _dedupe(cand)

    if typ == "wiki-page":
        return _dedupe(WIKI_PRODUCTS / cat / f"{slug}.md")
    if typ == "claim":
        return _dedupe(CLAIMS_STAGING / f"{slug}.yaml")
    if typ == "raw-doc":
        return _dedupe(RAW_LIBRARIAN / today / f"{slug}{ext}")
    if typ == "note":
        return _dedupe(WIKI_PRODUCTS / cat / "_notes" / f"{slug}.md")
    if typ == "asset":
        return _dedupe(WIKI_ASSETS / f"{slug}{ext}")
    return _dedupe(RAW_LIBRARIAN / today / f"{slug}{ext}")


def _dedupe(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    parent = target.parent
    n = 2
    while True:
        cand = parent / f"{stem}-{n}{suffix}"
        if not cand.exists():
            return cand
        n += 1


def process_item(meta: dict, dry: bool) -> dict:
    src = Path(meta["_stored_path"])
    target = resolve_target(meta)
    target.parent.mkdir(parents=True, exist_ok=True)

    plan = {
        "id": meta.get("id"),
        "from": str(src.relative_to(ROOT)),
        "to": str(target.relative_to(ROOT)),
        "category": (meta.get("classification") or {}).get("category"),
        "type": (meta.get("classification") or {}).get("type"),
    }
    if dry:
        plan["dry_run"] = True
        return plan

    shutil.move(str(src), str(target))

    # Move meta to processed/
    today = datetime.now().strftime("%Y-%m-%d")
    archive_dir = PROCESSED_ROOT / today
    archive_dir.mkdir(parents=True, exist_ok=True)
    meta["processed"] = True
    meta["processed_at"] = datetime.now().isoformat()
    meta["target_path"] = str(target.relative_to(ROOT))
    archive_meta = archive_dir / f"{meta.get('id', 'unknown')}.meta.json"
    archive_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    # Remove the original .meta.json from inbox
    try:
        Path(meta["_meta_path"]).unlink()
    except Exception:
        pass

    return plan


def count_review() -> int:
    review_dir = INBOX_ROOT / "_review"
    if not review_dir.exists():
        return 0
    return sum(1 for _ in review_dir.glob("*.meta.json"))


def write_last_run(report: dict):
    LOGS_ROOT.mkdir(parents=True, exist_ok=True)
    (LOGS_ROOT / "last-run.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))


def send_telegram_digest(report: dict):
    try:
        from lib.telegram import send_message
    except Exception:
        return
    lines = [
        "🤖 *Librarian — Daily Digest*",
        f"📥 Đã xử lý: *{report['processed']}*",
        f"⚠️ Cần review: *{report['review']}*",
        f"❌ Lỗi: *{report['errors']}*",
        f"⏱ Mode: `{report['mode']}` · {report.get('elapsed_ms', 0)}ms",
    ]
    if report.get("by_category"):
        cats = ", ".join(f"{k}={v}" for k, v in report["by_category"].items())
        lines.append(f"📂 {cats}")
    send_message("\n".join(lines))


def run(mode: str) -> dict:
    start = time.time()
    items = collect_items()
    plans = []
    errors = []
    by_category = {}

    for it in items:
        if it.get("_error"):
            errors.append(it["_error"])
            continue
        try:
            plan = process_item(it, dry=(mode == "dry"))
            plans.append(plan)
            cat = plan.get("category") or "uncategorized"
            by_category[cat] = by_category.get(cat, 0) + 1
        except Exception as e:
            errors.append(f"{it.get('id')}: {e}")

    report = {
        "mode": mode,
        "ran_at": datetime.now().isoformat(),
        "processed": len(plans),
        "review": count_review(),
        "errors": len(errors),
        "by_category": by_category,
        "plans": plans[:50],  # cap for size
        "error_details": errors[:20],
        "elapsed_ms": int((time.time() - start) * 1000),
    }

    if mode != "dry":
        write_last_run(report)
    if mode == "cron":
        send_telegram_digest(report)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["cron", "now", "dry"], default="now")
    args = ap.parse_args()

    if args.mode != "dry":
        if not acquire_lock():
            print(json.dumps({"ok": False, "error": "processor already running"}))
            sys.exit(2)

    try:
        report = run(args.mode)
        print(json.dumps(report, ensure_ascii=False))
    finally:
        if args.mode != "dry":
            release_lock()


if __name__ == "__main__":
    main()
