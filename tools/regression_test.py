#!/usr/bin/env python3
"""
BKNS Agent Wiki — Regression Test Runner (PART 07)

Orchestrates extract_dual + compile_dual for all 7 categories to produce
wiki-v0.4/ output for comparison against v0.3 snapshot.

Usage:
    # Dry-run: extract + compile for 'hosting' only
    python3 tools/regression_test.py --dry-run

    # Full rebuild for all 7 categories
    python3 tools/regression_test.py --full

    # Single step on a specific category
    python3 tools/regression_test.py --step extract --category hosting
    python3 tools/regression_test.py --step compile --category hosting

    # Run diff after rebuild
    python3 tools/regression_test.py --step diff

Outputs:
    wiki-v0.4/products/<category>/    — rebuilt wiki pages
    trienkhai/upgrade-v0.4/benchmark.md (updated with v0.4 metrics)
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Path bootstrap ─────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE))

# Register module aliases for skill dirs that use hyphens (BUG-002)
# skills/extract-claims → importable as skills.extract_claims
import types as _types
for _skill_path, _mod_name in [
    ("skills/extract-claims", "skills.extract_claims"),
    ("skills/compile-wiki", "skills.compile_wiki"),
]:
    if _mod_name not in sys.modules:
        _pkg = _types.ModuleType(_mod_name)
        _pkg.__path__ = [str(WORKSPACE / _skill_path)]  # type: ignore[attr-defined]
        sys.modules[_mod_name] = _pkg
        _scripts = _types.ModuleType(f"{_mod_name}.scripts")
        _scripts.__path__ = [str(WORKSPACE / _skill_path / "scripts")]  # type: ignore[attr-defined]
        sys.modules[f"{_mod_name}.scripts"] = _scripts

from lib.config import (
    RAW_MANUAL_DIR, RAW_CRAWL_DIR,
    CLAIMS_DRAFTS_DIR, CLAIMS_APPROVED_DIR,
    DUAL_VOTE_ENABLED, DUAL_VOTE_HIGH_STAKES,
    WORKSPACE as WS,
)
from lib.utils import parse_frontmatter, now_iso, ensure_dir
from lib.logger import log_entry

VN_TZ = timezone(timedelta(hours=7))

# ── Output directories ─────────────────────────────────────
WIKI_V04_DIR = WS / "wiki-v0.4" / "products"
SNAPSHOT_V03_DIR = WS / "build" / "snapshots" / "v0.3-pre-upgrade-2026-04-13" / "wiki" / "products"
TRIENKHAI_DIR = WS / "trienkhai" / "upgrade-v0.4"

# 7 regression categories (excludes 'other', 'uncategorized')
REGRESSION_CATEGORIES = ["hosting", "vps", "ssl", "ten-mien", "email", "server", "software"]


# ── Helpers ────────────────────────────────────────────────

def find_raw_files_for_category(category: str) -> list[Path]:
    """Find raw files whose suggested_category matches the given category."""
    target = f"products/{category}"
    results = []
    for raw_dir in [RAW_MANUAL_DIR, RAW_CRAWL_DIR]:
        if not raw_dir.exists():
            continue
        for f in raw_dir.rglob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(content)
                if fm.get("suggested_category", "") == target:
                    results.append(f)
            except Exception:
                continue
    return sorted(results)


def _now_vn() -> str:
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M")


# ── Step: Extract (dual-vote) ──────────────────────────────

def step_extract(category: str, force: bool = False) -> dict:
    """Run extract_dual on all raw files for the given category."""
    from skills.extract_claims.scripts.extract_dual import extract_claims_dual

    files = find_raw_files_for_category(category)
    if not files:
        return {"status": "no-files", "category": category, "files": 0}

    print(f"\n[extract] {category}: {len(files)} raw files")
    stats = {
        "category": category,
        "files": len(files),
        "ok": 0, "cached": 0, "error": 0, "skip": 0,
        "claims_count": 0,
        "cost_usd": 0.0,
        "agree": 0, "partial": 0, "disagree": 0,
        "elapsed_s": 0.0,
    }

    t0 = time.time()
    for f in files:
        print(f"  → {f.name[:60]}", end=" ", flush=True)
        try:
            res = extract_claims_dual(f, force=force)
        except Exception as e:
            print(f"ERROR: {e}")
            stats["error"] += 1
            continue

        status = res.get("status", "?")
        if status == "ok":
            stats["ok"] += 1
            stats["claims_count"] += res.get("claims_count", 0)
            stats["cost_usd"] += res.get("cost_usd", 0.0)
            vote = res.get("dual_vote_summary", {}).get("status", "")
            if vote == "AGREE":
                stats["agree"] += 1
            elif vote == "PARTIAL":
                stats["partial"] += 1
            elif vote in ("DISAGREE", "LOW"):
                stats["disagree"] += 1
        elif status == "cache-hit":
            stats["cached"] += 1
            stats["claims_count"] += res.get("claims_count", 0)
        elif status == "skip":
            stats["skip"] += 1
        else:
            stats["error"] += 1

        print(f"[{status}] {res.get('claims_count', 0)} claims ${res.get('cost_usd', 0):.5f}")

    stats["elapsed_s"] = round(time.time() - t0, 1)
    total = stats["ok"] + stats["partial"] + stats["disagree"]
    print(f"\n  ✓ {category}: {stats['claims_count']} claims | "
          f"cost=${stats['cost_usd']:.4f} | "
          f"AGREE={stats['agree']} PARTIAL={stats['partial']} DISAGREE={stats['disagree']} | "
          f"{stats['elapsed_s']}s")
    return stats


# ── Step: Compile (dual-vote) ──────────────────────────────

def step_compile(category: str, force: bool = False) -> dict:
    """Run compile_dual on the given category and write output to wiki-v0.4/."""
    from skills.compile_wiki.scripts.compile_dual import compile_category_dual

    print(f"\n[compile] {category}")
    t0 = time.time()

    try:
        result = compile_category_dual(category, force=force)
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"status": "error", "category": category, "detail": str(e)}

    # Copy generated pages into wiki-v0.4/
    wiki_src = WS / "wiki" / ".drafts" / "products" / category
    wiki_dst = WIKI_V04_DIR / category
    ensure_dir(wiki_dst)

    pages_copied = 0
    if wiki_src.exists():
        import shutil
        for page in wiki_src.glob("*.md"):
            shutil.copy2(page, wiki_dst / page.name)
            pages_copied += 1

    elapsed = round(time.time() - t0, 1)
    print(f"  ✓ {category}: {pages_copied} pages | "
          f"cost=${result.get('cost_usd', 0):.4f} | {elapsed}s")

    return {
        "status": "ok",
        "category": category,
        "pages": pages_copied,
        "cost_usd": result.get("cost_usd", 0.0),
        "elapsed_s": elapsed,
    }


# ── Step: Diff ─────────────────────────────────────────────

def step_diff() -> None:
    """Run wiki_diff.py comparing v0.3 snapshot vs wiki-v0.4/."""
    import subprocess
    diff_script = WORKSPACE / "tools" / "wiki_diff.py"
    if not diff_script.exists():
        print("ERROR: tools/wiki_diff.py not found — run PART 07 setup first")
        return

    print("\n[diff] Comparing v0.3 snapshot vs wiki-v0.4 ...")
    result = subprocess.run(
        [sys.executable, str(diff_script),
         "--v03", str(SNAPSHOT_V03_DIR),
         "--v04", str(WIKI_V04_DIR),
         "--html", str(TRIENKHAI_DIR / "diff-report.html"),
         "--json", str(TRIENKHAI_DIR / "diff-report.json")],
        capture_output=False,
    )
    if result.returncode != 0:
        print("  diff failed — check output above")


# ── Main orchestration ─────────────────────────────────────

def run_regression(categories: list[str], force: bool = False,
                   steps: list[str] = None) -> dict:
    """Run the full regression pipeline for the given categories."""
    if steps is None:
        steps = ["extract", "compile", "diff"]

    ensure_dir(WIKI_V04_DIR)

    all_extract_stats = []
    all_compile_stats = []

    print(f"\n{'='*60}")
    print(f"PART 07 — Regression Test (v0.4)")
    print(f"Categories: {', '.join(categories)}")
    print(f"Steps: {', '.join(steps)}")
    print(f"Started: {_now_vn()}")
    print(f"{'='*60}")

    if "extract" in steps:
        for cat in categories:
            stats = step_extract(cat, force=force)
            all_extract_stats.append(stats)

    if "compile" in steps:
        for cat in categories:
            stats = step_compile(cat, force=force)
            all_compile_stats.append(stats)

    if "diff" in steps:
        step_diff()

    # ── Summary ────────────────────────────────────────────
    total_claims = sum(s.get("claims_count", 0) for s in all_extract_stats)
    total_cost_extract = sum(s.get("cost_usd", 0) for s in all_extract_stats)
    total_cost_compile = sum(s.get("cost_usd", 0) for s in all_compile_stats)
    total_cost = total_cost_extract + total_cost_compile
    total_agree = sum(s.get("agree", 0) for s in all_extract_stats)
    total_partial = sum(s.get("partial", 0) for s in all_extract_stats)
    total_disagree = sum(s.get("disagree", 0) for s in all_extract_stats)

    summary = {
        "run_at": _now_vn(),
        "categories": categories,
        "steps": steps,
        "extract": {
            "total_files": sum(s.get("files", 0) for s in all_extract_stats),
            "total_claims": total_claims,
            "total_cost_usd": round(total_cost_extract, 4),
            "agree": total_agree,
            "partial": total_partial,
            "disagree": total_disagree,
            "agree_rate_pct": round(
                total_agree / max(total_agree + total_partial + total_disagree, 1) * 100, 1
            ),
        },
        "compile": {
            "total_pages": sum(s.get("pages", 0) for s in all_compile_stats),
            "total_cost_usd": round(total_cost_compile, 4),
        },
        "total_cost_usd": round(total_cost, 4),
        "per_category": all_extract_stats,
    }

    print(f"\n{'='*60}")
    print(f"SUMMARY — {_now_vn()}")
    print(f"  Claims extracted : {total_claims}")
    print(f"  Total cost       : ${total_cost:.4f}")
    print(f"  AGREE rate       : {summary['extract']['agree_rate_pct']}% "
          f"({total_agree}A / {total_partial}P / {total_disagree}D)")
    print(f"  Wiki pages built : {summary['compile'].get('total_pages', '?')}")
    print(f"{'='*60}\n")

    # Save summary JSON
    summary_path = TRIENKHAI_DIR / "regression-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Summary saved → {summary_path}")

    return summary


# ── CLI ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PART 07 — Regression Test Runner")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="Run on 'hosting' only (1 category, fast)")
    mode.add_argument("--full", action="store_true",
                      help="Run on all 7 regression categories")

    parser.add_argument("--step", choices=["extract", "compile", "diff", "all"],
                        default="all",
                        help="Which step(s) to run (default: all)")
    parser.add_argument("--category",
                        help="Override category for single-category run (with --full or --dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="Bypass SHA256 cache, re-extract everything")

    args = parser.parse_args()

    # Determine categories
    if args.category:
        categories = [args.category]
    elif args.dry_run:
        categories = ["hosting"]
    else:
        categories = REGRESSION_CATEGORIES

    # Determine steps
    if args.step == "all":
        steps = ["extract", "compile", "diff"]
    else:
        steps = [args.step]

    # Guard: warn if dual-vote is disabled
    if not DUAL_VOTE_ENABLED:
        print("\n⚠️  WARNING: DUAL_VOTE_ENABLED=false in .env")
        print("   Dual-vote will only activate for DUAL_VOTE_HIGH_STAKES categories.")
        print("   To enable fully: add DUAL_VOTE_ENABLED=true to .env\n")

    run_regression(categories=categories, force=args.force, steps=steps)


if __name__ == "__main__":
    main()
