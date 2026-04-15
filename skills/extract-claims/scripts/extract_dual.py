#!/usr/bin/env python3
"""
BKNS Agent Wiki — extract-claims Dual-Vote Adapter (PART 06)

Wraps extract.py: replaces single-Gemini call with dual-vote (Gemini + GPT).
Adds `dual_vote: {status, score, confidence}` to every saved claim.
DISAGREE/PARTIAL items land in .review-queue/ for human review.

Usage:
    # Same as extract.py but uses dual-vote for the LLM step:
    python3 skills/extract-claims/scripts/extract_dual.py
    python3 skills/extract-claims/scripts/extract_dual.py [raw_file]
    python3 skills/extract-claims/scripts/extract_dual.py --force

Feature flag:
    DUAL_VOTE_ENABLED=true  in .env  → all categories use dual-vote
    DUAL_VOTE_ENABLED=false           → only DUAL_VOTE_HIGH_STAKES categories
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.config import (
    RAW_CRAWL_DIR, RAW_MANUAL_DIR,
    CLAIM_REQUIRED_FIELDS, CLAIM_HIGH_RISK_ATTRIBUTES,
    DUAL_VOTE_ENABLED, DUAL_VOTE_HIGH_STAKES,
    get_pro_model, OPENAI_MODEL,
)
from lib.logger import log_entry
from lib.telegram import notify_error
from lib.utils import parse_frontmatter, now_iso, ensure_dir

# Import helpers from the existing extract.py (avoid copy-paste)
from skills.extract_claims.scripts.extract import (  # noqa: F401 — re-export
    EXTRACTION_PROMPT,
    _load_cache, _save_cache, _is_cached, _update_cache,
    find_pending_files,
    parse_claims_json,
    detect_conflicts,
    determine_claim_category,
    write_claim_yaml,
)
from lib.dual_vote import run_dual

# ── Dual-extract entry point ───────────────────────────────

def extract_claims_dual(raw_file: Path, force: bool = False) -> dict:
    """Extract claims using dual-vote (Gemini + GPT) instead of single-Gemini.

    Identical pipeline to extract_claims_from_file(), except:
    1. LLM call → run_dual() instead of generate()
    2. Each saved claim gets: dual_vote: {status, score, confidence}
    3. DISAGREE/PARTIAL → added to .review-queue/ (handled inside vote.py)
    4. BOTH_FAILED → return error (same as single-model failure)

    Returns:
        Same dict as extract_claims_from_file():
        {status, claims_count, cost_usd, ...} + dual_vote_summary
    """
    # ── SHA256 cache check ─────────────────────────────────
    if not force:
        cache = _load_cache()
        if _is_cached(raw_file, cache):
            cached_info = cache.get(str(raw_file.resolve()), {})
            log_entry("extract-dual", "cache-hit",
                      f"Cache hit: {raw_file.name} ({cached_info.get('claims_count', '?')} claims)")
            return {
                "status": "cache-hit",
                "detail": f"Unchanged since {cached_info.get('extracted_at', '?')}",
                "claims_count": cached_info.get("claims_count", 0),
                "cost_usd": 0,
                "cached": True,
            }

    log_entry("extract-dual", "start", f"Dual-extract: {raw_file.name}")

    content = raw_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    if not body or len(body.strip()) < 50:
        return {"status": "skip", "detail": "Content too short"}

    source_url = fm.get("source_url", "unknown")
    crawled_at = fm.get("crawled_at", now_iso())
    category = fm.get("suggested_category", "uncategorized")
    cat_short = category.split("/")[-1] if "/" in category else category

    # Decide whether to use dual-vote for this category
    use_dual = DUAL_VOTE_ENABLED or (cat_short in DUAL_VOTE_HIGH_STAKES)
    if not use_dual:
        # Fallback to regular extract for low-stakes content
        from skills.extract_claims.scripts.extract import extract_claims_from_file
        log_entry("extract-dual", "fallback",
                  f"{raw_file.name}: category={cat_short} not high-stakes + flag off → single-model")
        return extract_claims_from_file(raw_file, force=force)

    # Truncate body
    MAX_CHARS = 50_000
    if len(body) > MAX_CHARS:
        body_truncated = body[:MAX_CHARS].rsplit("\n", 1)[0]
    else:
        body_truncated = body

    prompt = EXTRACTION_PROMPT.format(
        raw_content=body_truncated,
        source_url=source_url,
        crawled_at=crawled_at,
    )

    # ── Dual-vote LLM call ─────────────────────────────────
    try:
        vote = run_dual(
            prompt=prompt,
            skill="extract-claims-dual",
            context={
                "source_file": str(raw_file),
                "category": category,
            },
        )
    except Exception as e:
        error_msg = f"Dual-vote error: {e}"
        log_entry("extract-dual", "error", error_msg, severity="critical")
        notify_error("extract-dual", error_msg)
        return {"status": "error", "detail": error_msg}

    # Handle failure cases
    if vote["status"] == "BOTH_FAILED":
        log_entry("extract-dual", "error", "Both agents failed", severity="critical")
        return {"status": "error", "detail": "Both agents failed", "vote": vote}

    # Get the text to parse (consensus or best available)
    if "consensus" in vote:
        text_to_parse = vote["consensus"]["text"]
    elif "agent_a" in vote:
        text_to_parse = vote["agent_a"]["text"]
        log_entry("extract-dual", "info",
                  f"Using Agent A text (status={vote['status']}, score={vote['score']})")
    else:
        text_to_parse = vote.get("agent_b", {}).get("text", "")
        log_entry("extract-dual", "info",
                  f"Using Agent B text (status={vote['status']})")

    # ── Parse claims JSON ──────────────────────────────────
    claims = parse_claims_json(text_to_parse)
    if claims is None:
        # Try agent_b as fallback if agent_a JSON is unparseable
        if vote.get("status") in ("PARTIAL", "DISAGREE") and "agent_b" in vote:
            claims = parse_claims_json(vote["agent_b"]["text"])
            if claims:
                log_entry("extract-dual", "info",
                          "Agent A JSON unparseable — fell back to Agent B output")

    if claims is None:
        log_entry("extract-dual", "error",
                  f"Cannot parse JSON output for {raw_file.name}", severity="high")
        return {"status": "error", "detail": "JSON parse error"}

    # Dual-vote metadata to attach to each claim
    dual_meta = {
        "status": vote["status"],
        "score": vote.get("score"),
        "confidence": vote["confidence"],
        "flag": vote.get("flag"),
    }

    # ── Save claims (same logic as extract.py) ─────────────
    cache = _load_cache()
    source_id = fm.get("source_id", f"SRC-{raw_file.stem.upper().replace('-', '_')}")

    saved_claims = []
    skipped = 0

    for claim_data in claims:
        missing = [f for f in CLAIM_REQUIRED_FIELDS if f not in claim_data]
        if missing:
            skipped += 1
            continue

        attribute = claim_data.get("attribute", "")
        if attribute in CLAIM_HIGH_RISK_ATTRIBUTES:
            claim_data["risk_class"] = "high"
        elif "risk_class" not in claim_data:
            claim_data["risk_class"] = "low"

        # Attach dual-vote metadata
        claim_data["dual_vote"] = dual_meta

        write_claim_yaml(claim_data, source_id, cat_short, crawled_at)
        saved_claims.append(claim_data)

    total_cost = vote.get("cost_usd_total", 0.0)
    _update_cache(raw_file, cache, len(saved_claims), total_cost)
    _save_cache(cache)

    log_entry(
        "extract-dual", "done",
        f"{raw_file.name}: {len(saved_claims)} claims | "
        f"vote={vote['status']} score={vote.get('score')} "
        f"cost=${total_cost:.6f}",
    )

    return {
        "status": "ok",
        "claims_count": len(saved_claims),
        "skipped": skipped,
        "cost_usd": total_cost,
        "dual_vote_summary": dual_meta,
    }


# ── CLI ────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract claims with dual-vote")
    parser.add_argument("raw_file", nargs="?", help="Specific raw file to process")
    parser.add_argument("--force", action="store_true", help="Bypass SHA256 cache")
    args = parser.parse_args()

    if args.raw_file:
        files = [Path(args.raw_file)]
    else:
        files = find_pending_files()
        print(f"Found {len(files)} pending files")

    total_claims = 0
    total_cost = 0.0
    agree_count = 0
    disagree_count = 0

    for f in files:
        print(f"  Processing: {f.name}")
        res = extract_claims_dual(f, force=args.force)
        if res["status"] == "ok":
            total_claims += res["claims_count"]
            total_cost += res.get("cost_usd", 0)
            vote_status = res.get("dual_vote_summary", {}).get("status", "")
            if vote_status == "AGREE":
                agree_count += 1
            elif vote_status in ("DISAGREE", "PARTIAL"):
                disagree_count += 1
        print(f"    → {res['status']} | {res.get('claims_count', 0)} claims")

    print(f"\nDone: {total_claims} claims | cost=${total_cost:.4f}")
    print(f"AGREE={agree_count} DISAGREE/PARTIAL={disagree_count}")
