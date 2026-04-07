#!/usr/bin/env python3
"""
BKNS Agent Wiki — Batch Pipeline Runner
Chạy extract → approve → compile từng file nhỏ để tránh tràn context.

Usage:
    python3 tools/batch_pipeline.py extract          # Extract all pending (1 file/lần)
    python3 tools/batch_pipeline.py extract --limit 5 # Extract max 5 files
    python3 tools/batch_pipeline.py approve           # Approve all drafts
    python3 tools/batch_pipeline.py compile           # Compile all categories
    python3 tools/batch_pipeline.py full              # Extract → Approve → Compile
    python3 tools/batch_pipeline.py dedup             # Remove duplicate pending files
    python3 tools/batch_pipeline.py status            # Show pipeline status
"""
import sys
import time
import argparse
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import (
    RAW_CRAWL_DIR, RAW_MANUAL_DIR, CLAIMS_DRAFTS_DIR, CLAIMS_APPROVED_DIR,
    WIKI_DRAFTS_DIR, WIKI_DIR,
)
from lib.utils import parse_frontmatter, now_iso
from lib.logger import log_entry


# ── Configuration ──────────────────────────────────────────
EXTRACT_DELAY_SECONDS = 3      # Delay between extract calls (avoid rate limit)
COMPILE_DELAY_SECONDS = 5      # Delay between compile calls
LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "batch_pipeline.log"


def log(msg: str, level: str = "INFO"):
    """Log to console and file."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Dedup: Remove duplicate pending files ──────────────────
def dedup_pending_files(dry_run: bool = False) -> dict:
    """Remove duplicate pending raw files (same slug, different dates).

    Strategy: For each slug, keep the NEWEST file, mark others as 'duplicate_skipped'.
    """
    log("Starting dedup of pending raw files...")

    # Group files by slug (strip date suffix)
    slug_groups = {}
    for raw_dir in [RAW_CRAWL_DIR, RAW_MANUAL_DIR]:
        if not raw_dir.exists():
            continue
        for f in raw_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            if fm.get("status") != "pending_extract":
                continue

            # Extract slug: remove date suffix like -2026-04-05
            slug = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", f.stem)
            if slug not in slug_groups:
                slug_groups[slug] = []
            slug_groups[slug].append(f)

    removed = 0
    kept = 0

    for slug, files in slug_groups.items():
        if len(files) <= 1:
            kept += len(files)
            continue

        # Sort by date in filename (newest first)
        files.sort(key=lambda f: f.stem, reverse=True)
        newest = files[0]
        kept += 1

        for old_file in files[1:]:
            if dry_run:
                log(f"  [DRY-RUN] Would skip: {old_file.name} (keep: {newest.name})")
            else:
                # Mark as duplicate_skipped instead of deleting
                content = old_file.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
                fm["status"] = "duplicate_skipped"
                fm["skipped_reason"] = f"Duplicate of {newest.name}"
                fm["skipped_at"] = now_iso()
                from lib.utils import write_markdown_with_frontmatter
                write_markdown_with_frontmatter(old_file, fm, body)
                log(f"  Skipped: {old_file.name} → duplicate of {newest.name}")
            removed += 1

    log(f"Dedup complete: {kept} kept, {removed} duplicates marked as skipped")
    return {"kept": kept, "removed": removed}


# ── Status ─────────────────────────────────────────────────
def show_status():
    """Show current pipeline status."""
    log("=" * 60)
    log("BKNS Wiki Pipeline Status")
    log("=" * 60)

    # Raw files
    pending = 0
    extracted = 0
    skipped = 0
    for raw_dir in [RAW_CRAWL_DIR, RAW_MANUAL_DIR]:
        if not raw_dir.exists():
            continue
        for f in raw_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            status = fm.get("status", "unknown")
            if status == "pending_extract":
                pending += 1
            elif status == "extracted":
                extracted += 1
            elif status in ("duplicate_skipped", "skip"):
                skipped += 1

    log(f"Raw files: {pending} pending | {extracted} extracted | {skipped} skipped")

    # Claims
    draft_count = 0
    approved_count = 0
    draft_cats = {}
    approved_cats = {}

    if CLAIMS_DRAFTS_DIR.exists():
        products = CLAIMS_DRAFTS_DIR / "products"
        if products.exists():
            for cat_dir in products.iterdir():
                if cat_dir.is_dir():
                    count = len(list(cat_dir.glob("*.yaml")))
                    draft_cats[cat_dir.name] = count
                    draft_count += count

    if CLAIMS_APPROVED_DIR.exists():
        products = CLAIMS_APPROVED_DIR / "products"
        if products.exists():
            for cat_dir in products.iterdir():
                if cat_dir.is_dir():
                    count = len(list(cat_dir.glob("*.yaml")))
                    approved_cats[cat_dir.name] = count
                    approved_count += count

    log(f"Claims: {draft_count} drafts | {approved_count} approved")

    # Categories breakdown
    all_cats = sorted(set(list(draft_cats.keys()) + list(approved_cats.keys())))
    for cat in all_cats:
        d = draft_cats.get(cat, 0)
        a = approved_cats.get(cat, 0)
        log(f"  {cat}: {d} drafts / {a} approved")

    # Wiki pages
    wiki_count = 0
    draft_wiki_count = 0
    if WIKI_DIR.exists():
        wiki_count = len(list(WIKI_DIR.rglob("*.md")))
    if WIKI_DRAFTS_DIR.exists():
        draft_wiki_count = len(list(WIKI_DRAFTS_DIR.rglob("*.md")))

    log(f"Wiki pages: {draft_wiki_count} drafts | {wiki_count} published")
    log("=" * 60)


# ── Load extract module ────────────────────────────────────
def _load_extract_module():
    """Dynamically load extract-claims module (avoid conflicts with skills/ package)."""
    import importlib.util
    extract_path = str(
        Path(__file__).resolve().parent.parent
        / "skills" / "extract-claims" / "scripts" / "extract.py"
    )
    spec = importlib.util.spec_from_file_location("extract_claims_script", extract_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Extract ────────────────────────────────────────────────
def run_extract(limit: int = None) -> dict:
    """Extract claims from pending raw files, one at a time."""
    extract_mod = _load_extract_module()

    pending = extract_mod.find_pending_files()

    if not pending:
        log("No pending files to extract.")
        return {"total": 0, "success": 0, "error": 0, "cost": 0, "claims": 0}

    if limit:
        pending = pending[:limit]

    log(f"Starting extract: {len(pending)} file(s)")

    success = 0
    errors = 0
    total_cost = 0
    total_claims = 0

    for i, raw_file in enumerate(pending, 1):
        log(f"[{i}/{len(pending)}] Extracting: {raw_file.name}")

        try:
            result = extract_mod.extract_claims_from_file(raw_file)
            status = result.get("status", "unknown")

            if status == "success":
                success += 1
                claims = result.get("claims_count", 0)
                cost = result.get("cost_usd", 0)
                total_claims += claims
                total_cost += cost
                log(f"  ✅ {claims} claims extracted (${cost:.4f})")
            elif status == "skip":
                log(f"  ⏭️ Skipped: {result.get('detail', '')}")
                success += 1  # skip is ok
            else:
                errors += 1
                log(f"  ❌ Error: {result.get('detail', 'Unknown')}", level="ERROR")

        except Exception as e:
            errors += 1
            log(f"  ❌ Exception: {str(e)[:200]}", level="ERROR")

        # Delay between files to avoid rate limiting
        if i < len(pending):
            time.sleep(EXTRACT_DELAY_SECONDS)

    log(f"\nExtract Summary: {success} success, {errors} errors, "
        f"{total_claims} claims, ${total_cost:.4f}")

    return {
        "total": len(pending),
        "success": success,
        "error": errors,
        "claims": total_claims,
        "cost": total_cost,
    }


# ── Approve ────────────────────────────────────────────────
def run_approve() -> dict:
    """Approve all drafted claims."""
    log("Starting batch approve...")

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from approve_and_compile import approve_all_drafts

    result = approve_all_drafts()
    log(f"Approved: {result['approved']} claims ({result.get('skipped', 0)} skipped)")
    return result


# ── Compile ────────────────────────────────────────────────
def run_compile() -> dict:
    """Compile all categories with wiki pages."""
    log("Starting compile for all categories...")

    # Import compile module
    compile_path = (Path(__file__).resolve().parent.parent
                    / "skills" / "compile-wiki" / "scripts")
    sys.path.insert(0, str(compile_path))

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "compile_wiki",
        str(compile_path / "compile.py")
    )
    compile_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compile_module)

    categories = ["hosting", "vps", "ten-mien", "email", "ssl", "server", "software"]
    results = {}
    total_cost = 0

    for i, cat in enumerate(categories):
        # Check if category has claims
        approved_dir = CLAIMS_APPROVED_DIR / "products" / cat
        drafts_dir = CLAIMS_DRAFTS_DIR / "products" / cat

        has_claims = False
        for d in [approved_dir, drafts_dir]:
            if d.exists() and list(d.glob("*.yaml")):
                has_claims = True
                break

        if not has_claims:
            log(f"  [{cat}] No claims → skip")
            results[cat] = {"status": "skip", "detail": "No claims"}
            continue

        log(f"  [{cat}] Compiling...")
        try:
            result = compile_module.compile_category(cat)
            status = result.get("status", "unknown")
            cost = result.get("cost_usd", 0)
            total_cost += cost
            log(f"  [{cat}] → {status} ({result.get('claims_used', 0)} claims, ${cost:.4f})")
            results[cat] = result
        except Exception as e:
            log(f"  [{cat}] → ERROR: {str(e)[:200]}", level="ERROR")
            results[cat] = {"status": "error", "detail": str(e)[:200]}

        # Delay between compiles
        if i < len(categories) - 1:
            time.sleep(COMPILE_DELAY_SECONDS)

    log(f"\nCompile Summary: total cost ${total_cost:.4f}")
    return {"categories": results, "total_cost": total_cost}


# ── Full Pipeline ──────────────────────────────────────────
def run_full(limit: int = None) -> dict:
    """Run full pipeline: dedup → extract → approve → compile."""
    log("=" * 60)
    log("BKNS Wiki — Full Pipeline Run")
    log(f"Started at: {now_iso()}")
    log("=" * 60)

    # Step 0: Status
    show_status()

    # Step 1: Dedup
    log("\n📋 Step 1/4: Dedup pending files...")
    dedup_result = dedup_pending_files()

    # Step 2: Extract
    log("\n📋 Step 2/4: Extracting claims...")
    extract_result = run_extract(limit=limit)

    # Step 3: Approve
    log("\n📋 Step 3/4: Approving claims...")
    approve_result = run_approve()

    # Step 4: Compile
    log("\n📋 Step 4/4: Compiling wiki pages...")
    compile_result = run_compile()

    # Final status
    log("\n" + "=" * 60)
    log("Pipeline Complete!")
    log(f"  Dedup: {dedup_result.get('removed', 0)} duplicates removed")
    log(f"  Extract: {extract_result.get('claims', 0)} claims from "
        f"{extract_result.get('success', 0)} files")
    log(f"  Approve: {approve_result.get('approved', 0)} claims approved")
    log(f"  Compile cost: ${compile_result.get('total_cost', 0):.4f}")
    log(f"Finished at: {now_iso()}")
    log("=" * 60)

    show_status()

    return {
        "dedup": dedup_result,
        "extract": extract_result,
        "approve": approve_result,
        "compile": compile_result,
    }


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Batch Pipeline")
    parser.add_argument("command", choices=[
        "extract", "approve", "compile", "full", "dedup", "status"
    ], help="Pipeline command")
    parser.add_argument("--limit", "-l", type=int, default=None,
                        help="Max files to extract")
    parser.add_argument("--dry-run", action="store_true",
                        help="Dry run for dedup")
    args = parser.parse_args()

    if args.command == "status":
        show_status()
    elif args.command == "dedup":
        dedup_pending_files(dry_run=args.dry_run)
    elif args.command == "extract":
        run_extract(limit=args.limit)
    elif args.command == "approve":
        run_approve()
    elif args.command == "compile":
        run_compile()
    elif args.command == "full":
        run_full(limit=args.limit)


if __name__ == "__main__":
    main()
