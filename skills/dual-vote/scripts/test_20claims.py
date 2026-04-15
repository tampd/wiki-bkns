#!/usr/bin/env python3
"""
PART 06 — Bước 7: Test dual-vote trên 20 claims từ test-set.yaml

Chạy:
  cd /home/openclaw/wiki
  python3 skills/dual-vote/scripts/test_20claims.py [--dry-run] [--limit N]

Output:
  trienkhai/upgrade-v0.4/dual-vote-test-results.md
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import yaml

VN_TZ = timezone(timedelta(hours=7))

TESTSET_FILE = ROOT / "trienkhai" / "upgrade-v0.4" / "test-set.yaml"
CLAIMS_DIR = ROOT / "claims" / "approved"
OUTPUT_FILE = ROOT / "trienkhai" / "upgrade-v0.4" / "dual-vote-test-results.md"

# Extraction prompt (same as extract.py)
SYSTEM_PROMPT = (
    "You are an expert data extractor for BKNS — a Vietnamese web hosting provider. "
    "Extract factual claims from the given YAML claim record. "
    "Return JSON with keys: attribute, value, confidence (0.0-1.0). "
    "Be precise and factual."
)


def build_prompt(claim: dict) -> str:
    """Build a test prompt from an existing claim — ask both agents to verify the value."""
    return (
        f"Verify the following claim about BKNS products and return JSON:\n"
        f"Entity: {claim.get('entity_name', '')}\n"
        f"Attribute: {claim.get('attribute', '')}\n"
        f"Claimed value: {claim.get('value', '')}\n\n"
        f"Return JSON: {{\"attribute\": \"...\", \"value\": \"...\", \"confidence\": 0.0-1.0, "
        f"\"agrees\": true/false, \"reason\": \"brief explanation\"}}"
    )


def load_test_claims(testset: dict) -> list:
    """Load claim YAML files referenced in the test set."""
    claims = []
    categories = testset.get("categories", {})

    for cat_name, cat_data in categories.items():
        for claim_spec in cat_data.get("claims", []):
            file_path = ROOT / claim_spec["file"]
            if not file_path.exists():
                print(f"  [WARN] Missing claim file: {file_path}")
                claims.append({
                    "claim_id": claim_spec["claim_id"],
                    "_category": cat_name,
                    "_file_missing": True,
                    "entity_name": claim_spec.get("entity_name", ""),
                    "attribute": claim_spec.get("attribute", ""),
                    "value": claim_spec.get("expected_value", ""),
                    "risk_class": claim_spec.get("risk_class", ""),
                    "_expected": claim_spec,
                })
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    claim = yaml.safe_load(f)
                claim["_category"] = cat_name
                claim["_expected"] = claim_spec
                claim["_file"] = str(file_path)
                claims.append(claim)
            except Exception as e:
                print(f"  [ERROR] Load {file_path}: {e}")

    return claims


def run_tests(claims: list, dry_run: bool = False, limit: int = 0) -> list:
    """Run dual-vote on each claim and collect results."""
    if limit:
        claims = claims[:limit]

    if not dry_run:
        from lib.dual_vote import run_dual

    results = []
    total = len(claims)

    print(f"\n{'='*60}")
    print(f"Running dual-vote on {total} claims{'  [DRY-RUN]' if dry_run else ''}")
    print(f"{'='*60}")

    for i, claim in enumerate(claims, 1):
        cid = claim.get("claim_id", "?")
        cat = claim.get("_category", "?")
        attr = claim.get("attribute", "?")
        val = claim.get("value", "?")
        print(f"\n[{i:02d}/{total}] {cid}")
        print(f"       {cat} / {attr} = {val}")

        if claim.get("_file_missing"):
            results.append({
                "claim_id": cid,
                "category": cat,
                "attribute": attr,
                "expected": val,
                "status": "SKIP",
                "reason": "claim file missing",
                "score": None,
                "cost": 0.0,
                "elapsed_ms": 0,
            })
            print(f"       → SKIP (file missing)")
            continue

        if dry_run:
            # Simulate a result
            import random
            sim_status = random.choice(["AGREE", "AGREE", "AGREE", "PARTIAL", "DISAGREE"])
            sim_score = {"AGREE": 0.95, "PARTIAL": 0.72, "DISAGREE": 0.28}[sim_status]
            results.append({
                "claim_id": cid,
                "category": cat,
                "attribute": attr,
                "expected": val,
                "status": sim_status,
                "score": sim_score,
                "cost": round(0.002 + random.random() * 0.005, 5),
                "elapsed_ms": int(2000 + random.random() * 3000),
                "model_a": "gemini-2.5-pro [simulated]",
                "model_b": "gpt-5.4 [simulated]",
                "reason": "DRY RUN — no real API call",
            })
            print(f"       → {sim_status} (score={sim_score:.2f}) [simulated]")
            continue

        # Real API call
        try:
            prompt = build_prompt(claim)
            t0 = time.time()
            vote = run_dual(prompt, system=SYSTEM_PROMPT, skill="test-20claims")
            elapsed_ms = int((time.time() - t0) * 1000)

            results.append({
                "claim_id": cid,
                "category": cat,
                "attribute": attr,
                "expected": str(val),
                "status": vote["status"],
                "confidence": vote["confidence"],
                "score": vote.get("score"),
                "cost": vote.get("cost_usd_total", 0.0),
                "elapsed_ms": elapsed_ms,
                "model_a": vote.get("model_a", ""),
                "model_b": vote.get("model_b", ""),
                "flag": vote.get("flag"),
            })

            score_str = f"{vote['score']:.2f}" if vote.get("score") is not None else "—"
            print(f"       → {vote['status']} (score={score_str}, cost=${vote.get('cost_usd_total', 0):.4f})")

            # Small delay to avoid rate limits
            time.sleep(1)

        except Exception as e:
            print(f"       → ERROR: {e}")
            results.append({
                "claim_id": cid,
                "category": cat,
                "attribute": attr,
                "expected": str(val),
                "status": "ERROR",
                "score": None,
                "cost": 0.0,
                "elapsed_ms": 0,
                "error": str(e),
            })

    return results


def compute_stats(results: list) -> dict:
    valid = [r for r in results if r["status"] not in ("SKIP", "ERROR")]
    total = len(valid)
    if total == 0:
        return {"total": 0}

    by_status = {}
    for r in valid:
        s = r["status"]
        by_status[s] = by_status.get(s, 0) + 1

    scores = [r["score"] for r in valid if r.get("score") is not None]
    costs = [r["cost"] for r in results if r.get("cost")]

    return {
        "total": total,
        "total_with_skip_error": len(results),
        "by_status": by_status,
        "agree_rate": round(by_status.get("AGREE", 0) / total * 100, 1),
        "partial_rate": round(by_status.get("PARTIAL", 0) / total * 100, 1),
        "disagree_rate": round(by_status.get("DISAGREE", 0) / total * 100, 1),
        "avg_score": round(sum(scores) / len(scores), 3) if scores else None,
        "total_cost": round(sum(costs), 5),
        "avg_cost_per_claim": round(sum(costs) / total, 5) if costs else 0,
        "skipped": sum(1 for r in results if r["status"] == "SKIP"),
        "errors": sum(1 for r in results if r["status"] == "ERROR"),
    }


def write_markdown(results: list, stats: dict, dry_run: bool) -> None:
    """Write results to dual-vote-test-results.md."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M %Z")

    lines = [
        "# Dual-Vote Test Results — 20 Claims",
        "",
        f"**Ngày chạy:** {now}  ",
        f"**Chế độ:** {'DRY RUN (simulated)' if dry_run else 'REAL API CALLS'}",
        "",
        "---",
        "",
        "## Tóm Tắt",
        "",
        f"| Metric | Giá trị |",
        f"|---|---|",
        f"| Tổng claims test | {stats.get('total_with_skip_error', 0)} |",
        f"| Claims chạy được | {stats.get('total', 0)} |",
        f"| Bỏ qua (SKIP) | {stats.get('skipped', 0)} |",
        f"| Lỗi (ERROR) | {stats.get('errors', 0)} |",
        f"| AGREE | {stats.get('by_status', {}).get('AGREE', 0)} ({stats.get('agree_rate', 0)}%) |",
        f"| PARTIAL | {stats.get('by_status', {}).get('PARTIAL', 0)} ({stats.get('partial_rate', 0)}%) |",
        f"| DISAGREE | {stats.get('by_status', {}).get('DISAGREE', 0)} ({stats.get('disagree_rate', 0)}%) |",
        f"| Avg similarity score | {stats.get('avg_score', '—')} |",
        f"| Total cost | ${stats.get('total_cost', 0):.5f} |",
        f"| Cost/claim | ${stats.get('avg_cost_per_claim', 0):.5f} |",
        "",
        "## Acceptance Criteria Check",
        "",
    ]

    agree_rate = stats.get("agree_rate", 0)
    disagree_rate = stats.get("disagree_rate", 0)

    lines += [
        f"- {'✅' if agree_rate >= 70 else '❌'} AGREE rate ≥ 70%: **{agree_rate}%**",
        f"- {'✅' if disagree_rate <= 10 else '❌'} DISAGREE rate ≤ 10%: **{disagree_rate}%**",
        f"- {'✅' if stats.get('errors', 0) == 0 else '⚠️'} Zero errors: **{stats.get('errors', 0)} errors**",
        "",
        "---",
        "",
        "## Chi Tiết Per Claim",
        "",
        "| # | Claim ID | Category | Attribute | Status | Score | Cost ($) |",
        "|---|---|---|---|---|---|---|",
    ]

    for i, r in enumerate(results, 1):
        status = r["status"]
        emoji = {"AGREE": "✅", "PARTIAL": "🟡", "DISAGREE": "❌", "ERROR": "💥", "SKIP": "⏭️"}.get(status, "?")
        score = f"{r['score']:.2f}" if r.get("score") is not None else "—"
        cost = f"{r['cost']:.5f}" if r.get("cost") else "—"
        lines.append(
            f"| {i} | `{r['claim_id']}` | {r['category']} | {r['attribute']} "
            f"| {emoji} {status} | {score} | {cost} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Raw JSON",
        "",
        "```json",
        json.dumps(results, ensure_ascii=False, indent=2),
        "```",
    ]

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Results written to: {OUTPUT_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Test dual-vote on 20 claims")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without real API calls")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of claims to test")
    args = parser.parse_args()

    # Load test set
    print(f"Loading test set from {TESTSET_FILE}...")
    with open(TESTSET_FILE, encoding="utf-8") as f:
        testset = yaml.safe_load(f)

    claims = load_test_claims(testset)
    print(f"Loaded {len(claims)} claims from {len(testset.get('categories', {}))} categories")

    # Run tests
    results = run_tests(claims, dry_run=args.dry_run, limit=args.limit)

    # Stats
    stats = compute_stats(results)

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Total:    {stats.get('total_with_skip_error', 0)} claims")
    print(f"  AGREE:    {stats.get('by_status', {}).get('AGREE', 0)} ({stats.get('agree_rate', 0)}%)")
    print(f"  PARTIAL:  {stats.get('by_status', {}).get('PARTIAL', 0)}")
    print(f"  DISAGREE: {stats.get('by_status', {}).get('DISAGREE', 0)} ({stats.get('disagree_rate', 0)}%)")
    print(f"  Avg score: {stats.get('avg_score', '—')}")
    print(f"  Total cost: ${stats.get('total_cost', 0):.5f}")
    print(f"  Cost/claim: ${stats.get('avg_cost_per_claim', 0):.5f}")

    # Check acceptance criteria
    agree_ok = stats.get("agree_rate", 0) >= 70
    disagree_ok = stats.get("disagree_rate", 0) <= 10
    print(f"\n  AGREE ≥70%:    {'PASS ✅' if agree_ok else 'FAIL ❌'}")
    print(f"  DISAGREE ≤10%: {'PASS ✅' if disagree_ok else 'FAIL ❌'}")

    # Write report
    write_markdown(results, stats, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
