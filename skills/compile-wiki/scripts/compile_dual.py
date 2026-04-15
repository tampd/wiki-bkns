#!/usr/bin/env python3
"""
BKNS Agent Wiki — compile-wiki Dual-Vote Adapter (PART 06)

Wraps compile.py: adds dual-vote validation for high-stakes wiki pages.
For DISAGREE/PARTIAL, adds <!-- ⚠️ NEEDS REVIEW --> marker to page
and writes item to .review-queue/ for human resolution.

Strategy:
- Run compile_category() as normal (Gemini generates wiki page)
- For high-stakes categories: ALSO run GPT on the same prompt
- If outputs agree (sim ≥ 0.9): mark page dual_vote=AGREE in frontmatter
- If partial/disagree: add NEEDS REVIEW marker + queue for human
- This avoids monkey-patching compile.py (thread-safe, no duplication)

Usage:
    python3 skills/compile-wiki/scripts/compile_dual.py hosting
    python3 skills/compile-wiki/scripts/compile_dual.py --all
    DUAL_VOTE_ENABLED=true python3 ... --all
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.config import (
    WIKI_DRAFTS_DIR,
    DUAL_VOTE_ENABLED,
    DUAL_VOTE_HIGH_STAKES,
    REVIEW_QUEUE_DIR,
    LOGS_DIR,
    get_pro_model,
)
from lib.logger import log_entry
from lib.utils import now_iso, ensure_dir

# Import compile utilities
from skills.compile_wiki.scripts.compile import (
    compile_category,
    collect_claims,
    _deduplicate_claims,
    SUBPAGE_DEFS,
    SUBPAGE_COMPILE_PROMPT,
    _filter_claims,
    _format_claims_text,
    _generate_cross_links,
)
from lib.dual_vote import run_dual
from lib.utils import today_str, write_markdown_with_frontmatter

VN_TZ = timezone(timedelta(hours=7))
REVIEW_MARKER = "\n\n<!-- ⚠️ NEEDS REVIEW: Dual-vote conflict — human review required -->\n"


def compile_category_dual(category: str, force: bool = False) -> dict:
    """Compile wiki category, with dual-vote validation for high-stakes pages.

    For low-stakes categories (not in DUAL_VOTE_HIGH_STAKES and flag off):
        Delegates entirely to compile_category() — no overhead.

    For high-stakes categories:
        1. Compile normally with Gemini (compile_category)
        2. For each sub-page, also call GPT via run_dual on the same prompt
        3. If AGREE → add dual_vote=AGREE to frontmatter
        4. If PARTIAL/DISAGREE → add NEEDS REVIEW marker + queue for human

    Returns:
        compile_category() result + dual_vote_summary
    """
    use_dual = DUAL_VOTE_ENABLED or (category in DUAL_VOTE_HIGH_STAKES)

    if not use_dual:
        log_entry("compile-dual", "fallback",
                  f"{category}: not high-stakes + flag off → single-model")
        return compile_category(category, force=force)

    log_entry("compile-dual", "start", f"Dual-compile: {category}")

    # Step 1: Standard compile (Gemini)
    compile_result = compile_category(category, force=force)
    if compile_result.get("status") not in ("ok", "done"):
        return compile_result

    # Step 2: Dual-vote validation per sub-page
    claims_raw, _ = collect_claims(category)
    claims = _deduplicate_claims(claims_raw)
    subpages = SUBPAGE_DEFS.get(category, [])
    cross_links_text = _generate_cross_links(category)

    total_dual_cost = 0.0
    agree_count = 0
    review_count = 0
    vote_summaries = []

    for sp in subpages:
        page_claims = _filter_claims(claims, sp["filter"])
        if not page_claims:
            continue  # skeleton pages don't need dual-vote

        claims_text = _format_claims_text(page_claims)
        prompt = SUBPAGE_COMPILE_PROMPT.format(
            category=category,
            claims_content=claims_text,
            title=sp["title"],
            page_desc=sp["desc"],
            prompt_hint=sp["prompt_hint"],
            date=today_str(),
            cross_links=cross_links_text,
        )

        vote = run_dual(prompt, skill="compile-wiki-dual")
        total_dual_cost += vote.get("cost_usd_total", 0.0)

        vote_summary = {
            "filename": sp["filename"],
            "status": vote["status"],
            "score": vote.get("score"),
            "confidence": vote["confidence"],
            "flag": vote.get("flag"),
        }
        vote_summaries.append(vote_summary)

        # Find the compiled draft file
        draft_file = WIKI_DRAFTS_DIR / "products" / category / sp["filename"]
        if not draft_file.exists():
            continue

        if vote["status"] == "AGREE":
            agree_count += 1
            _tag_page_frontmatter(draft_file, vote)
        else:
            review_count += 1
            _tag_page_frontmatter(draft_file, vote)
            _add_review_marker(draft_file)
            _write_review_queue_compile(vote, category, sp, prompt)

    # Log dual-vote summary for this category
    _log_compile_vote(category, vote_summaries, total_dual_cost)

    compile_result["dual_vote_summary"] = {
        "total_pages": len(vote_summaries),
        "agree": agree_count,
        "needs_review": review_count,
        "total_dual_cost_usd": round(total_dual_cost, 6),
        "pages": vote_summaries,
    }

    log_entry(
        "compile-dual", "done",
        f"{category}: {agree_count} AGREE, {review_count} needs review | "
        f"dual_cost=${total_dual_cost:.4f}",
    )

    return compile_result


def _tag_page_frontmatter(draft_file: Path, vote: dict) -> None:
    """Add dual_vote metadata to wiki page frontmatter."""
    try:
        content = draft_file.read_text(encoding="utf-8")
        dual_block = (
            f"\ndual_vote:\n"
            f"  status: {vote['status']}\n"
            f"  score: {vote.get('score')}\n"
            f"  confidence: {vote['confidence']}\n"
            f"  validated_at: {now_iso()}\n"
        )
        # Insert before closing --- of frontmatter
        if content.startswith("---"):
            # Find the closing ---
            end_fm = content.find("\n---", 3)
            if end_fm != -1:
                content = content[:end_fm] + dual_block + content[end_fm:]
                draft_file.write_text(content, encoding="utf-8")
    except Exception as e:
        log_entry("compile-dual", "warn",
                  f"Could not tag frontmatter for {draft_file.name}: {e}")


def _add_review_marker(draft_file: Path) -> None:
    """Append NEEDS REVIEW comment to the wiki page."""
    try:
        content = draft_file.read_text(encoding="utf-8")
        if "NEEDS REVIEW" not in content:
            draft_file.write_text(content + REVIEW_MARKER, encoding="utf-8")
    except Exception as e:
        log_entry("compile-dual", "warn",
                  f"Could not add review marker to {draft_file.name}: {e}")


def _write_review_queue_compile(
    vote: dict, category: str, sp: dict, prompt: str
) -> None:
    """Write compile conflict to .review-queue/ for human review."""
    REVIEW_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(VN_TZ).strftime("%Y%m%d-%H%M%S")
    item_file = REVIEW_QUEUE_DIR / f"{ts}-compile-{category}-{sp['filename'].replace('/', '_')}.json"

    item = {
        "ts": datetime.now(VN_TZ).isoformat(),
        "type": "compile",
        "category": category,
        "filename": sp["filename"],
        "title": sp["title"],
        "status": vote["status"],
        "flag": vote["flag"],
        "score": vote.get("score"),
        "text_a": vote.get("agent_a", {}).get("text", "")[:2000] if "agent_a" in vote else "",
        "text_b": vote.get("agent_b", {}).get("text", "")[:2000] if "agent_b" in vote else "",
        "prompt_preview": prompt[:500],
    }
    item_file.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


def _log_compile_vote(category: str, summaries: list, total_cost: float) -> None:
    """Append compile dual-vote summary to logs/dual-vote-YYYY-MM.jsonl."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    month_str = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"dual-vote-{month_str}.jsonl"

    entry = {
        "ts": datetime.now(VN_TZ).isoformat(),
        "skill": "compile-wiki-dual",
        "category": category,
        "pages": len(summaries),
        "agree": sum(1 for s in summaries if s["status"] == "AGREE"),
        "partial": sum(1 for s in summaries if s["status"] == "PARTIAL"),
        "disagree": sum(1 for s in summaries if s["status"] == "DISAGREE"),
        "cost_usd_total": round(total_cost, 6),
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── CLI ────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    VALID_CATEGORIES = list(SUBPAGE_DEFS.keys())

    parser = argparse.ArgumentParser(description="Compile wiki with dual-vote validation")
    parser.add_argument("category", nargs="?", help=f"Category: {VALID_CATEGORIES}")
    parser.add_argument("--all", action="store_true", help="Compile all categories")
    parser.add_argument("--force", action="store_true", help="Force recompile")
    args = parser.parse_args()

    if args.all:
        categories = VALID_CATEGORIES
    elif args.category:
        categories = [args.category]
    else:
        parser.print_help()
        sys.exit(1)

    total_cost = 0.0
    for cat in categories:
        print(f"\nCompiling: {cat}")
        result = compile_category_dual(cat, force=args.force)
        cost = result.get("cost_usd", 0) + result.get("dual_vote_summary", {}).get("total_dual_cost_usd", 0)
        total_cost += cost
        dv = result.get("dual_vote_summary", {})
        print(f"  Status: {result.get('status')} | "
              f"AGREE={dv.get('agree', '-')} REVIEW={dv.get('needs_review', '-')} | "
              f"cost=${cost:.4f}")

    print(f"\nTotal cost: ${total_cost:.4f}")
