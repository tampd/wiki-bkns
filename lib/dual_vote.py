"""
BKNS Agent Wiki — Dual-Agent Voting Engine (PART 06)
Importable as: from lib.dual_vote import run_dual

Runs Gemini 3.1 Pro + GPT-5.4 in parallel, compares outputs,
returns consensus OR flags for human review.

Agreement thresholds:
    AGREE    : sim ≥ 0.9  → confidence HIGH  → auto-approve
    PARTIAL  : 0.6–0.89   → confidence MEDIUM → needs_review
    DISAGREE : sim < 0.6   → confidence LOW   → human_review_required
    DEGRADED : one failed  → use survivor     → reduced confidence
    BOTH_FAILED            → propagate error

Usage:
    from skills.dual_vote.scripts.vote import run_dual
    result = run_dual(prompt, system="...", skill="extract-claims")
"""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from lib.config import (
    LOGS_DIR,
    REVIEW_QUEUE_DIR,
    get_pro_model,
    OPENAI_MODEL,
    DUAL_VOTE_THRESHOLD_AGREE,
    DUAL_VOTE_THRESHOLD_PARTIAL,
)
from lib.gemini import generate as gemini_generate
from lib.openai_client import generate as openai_generate
from lib.utils import semantic_similarity

VN_TZ = timezone(timedelta(hours=7))
AGENT_TIMEOUT = 180  # seconds per agent


# ── Public API ─────────────────────────────────────────────

def run_dual(
    prompt: str,
    system: str = "",
    skill: str = "dual-vote",
    model_a: Optional[str] = None,
    model_b: Optional[str] = None,
) -> dict:
    """Run Gemini (A) + GPT (B) in parallel, return voting result.

    Args:
        prompt:  User prompt sent to both agents.
        system:  System instruction (optional).
        skill:   Skill name for structured logging.
        model_a: Gemini model override (default: get_pro_model()).
        model_b: OpenAI model override (default: OPENAI_MODEL from .env).

    Returns dict with keys:
        status        : AGREE | PARTIAL | DISAGREE | DEGRADED_USE_A |
                        DEGRADED_USE_B | BOTH_FAILED
        confidence    : HIGH | MEDIUM | LOW | DEGRADED | NONE
        flag          : None | needs_review | human_review_required |
                        agent_a_failed | agent_b_failed | both_agents_failed
        score         : float 0–1 (None if one/both failed)
        consensus     : agent result used as canonical (AGREE / DEGRADED)
        agent_a       : Gemini raw result (PARTIAL / DISAGREE)
        agent_b       : GPT raw result   (PARTIAL / DISAGREE)
        model_a       : Gemini model name used
        model_b       : GPT model name used
        cost_usd_total: sum of both agents' costs
        cost_usd_a    : Gemini cost
        cost_usd_b    : GPT cost
        elapsed_ms    : wall-clock time (parallel)
    """
    model_a = model_a or get_pro_model()
    model_b = model_b or OPENAI_MODEL

    start = time.time()

    result_a: Optional[dict] = None
    result_b: Optional[dict] = None
    error_a: Optional[str] = None
    error_b: Optional[str] = None

    # ── Parallel execution ─────────────────────────────────
    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_a = executor.submit(
            gemini_generate, prompt,
            model=model_a,
            skill=skill,
            system_instruction=system or None,
        )
        fut_b = executor.submit(
            openai_generate, prompt,
            model=model_b,
            skill=skill,
            system=system or None,
        )

        try:
            result_a = fut_a.result(timeout=AGENT_TIMEOUT)
        except Exception as e:
            error_a = str(e)

        try:
            result_b = fut_b.result(timeout=AGENT_TIMEOUT)
        except Exception as e:
            error_b = str(e)

    elapsed_ms = int((time.time() - start) * 1000)

    # ── Analyze agreement ──────────────────────────────────
    vote = _analyze(result_a, result_b, error_a, error_b)
    vote["model_a"] = model_a
    vote["model_b"] = model_b
    vote["elapsed_ms"] = elapsed_ms
    vote["cost_usd_a"] = (result_a or {}).get("cost_usd", 0.0)
    vote["cost_usd_b"] = (result_b or {}).get("cost_usd", 0.0)
    vote["cost_usd_total"] = round(vote["cost_usd_a"] + vote["cost_usd_b"], 6)

    # ── Write review queue item if flagged ─────────────────
    if vote.get("flag") in ("needs_review", "human_review_required"):
        _write_review_queue(vote, prompt, skill)

    # ── Audit log ──────────────────────────────────────────
    _log_vote(vote, prompt, skill)

    return vote


# ── Internal ───────────────────────────────────────────────

def _analyze(
    a: Optional[dict],
    b: Optional[dict],
    error_a: Optional[str],
    error_b: Optional[str],
) -> dict:
    """Compute agreement outcome from agent results."""
    # Both failed
    if error_a and error_b:
        return {
            "status": "BOTH_FAILED",
            "confidence": "NONE",
            "flag": "both_agents_failed",
            "score": None,
            "error_a": error_a,
            "error_b": error_b,
        }

    # Agent A (Gemini) failed — use GPT
    if error_a:
        return {
            "status": "DEGRADED_USE_B",
            "confidence": "DEGRADED",
            "flag": "agent_a_failed",
            "score": None,
            "consensus": b,
            "error_a": error_a,
        }

    # Agent B (GPT) failed — use Gemini
    if error_b:
        return {
            "status": "DEGRADED_USE_A",
            "confidence": "DEGRADED",
            "flag": "agent_b_failed",
            "score": None,
            "consensus": a,
            "error_b": error_b,
        }

    # Both succeeded — measure similarity
    text_a = (a or {}).get("text", "")
    text_b = (b or {}).get("text", "")
    sim = semantic_similarity(text_a, text_b)

    if sim >= DUAL_VOTE_THRESHOLD_AGREE:
        return {
            "status": "AGREE",
            "confidence": "HIGH",
            "flag": None,
            "score": sim,
            "consensus": a,  # Gemini as canonical when agreement
            "agent_b": b,
        }

    if sim >= DUAL_VOTE_THRESHOLD_PARTIAL:
        return {
            "status": "PARTIAL",
            "confidence": "MEDIUM",
            "flag": "needs_review",
            "score": sim,
            "agent_a": a,
            "agent_b": b,
        }

    return {
        "status": "DISAGREE",
        "confidence": "LOW",
        "flag": "human_review_required",
        "score": sim,
        "agent_a": a,
        "agent_b": b,
    }


QUEUE_ALERT_THRESHOLD = 5  # Send Telegram when pending items reach this count


def _write_review_queue(vote: dict, prompt: str, skill: str) -> None:
    """Write flagged item to .review-queue/ for human review."""
    REVIEW_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(VN_TZ).strftime("%Y%m%d-%H%M%S")
    item_file = REVIEW_QUEUE_DIR / f"{ts}-{skill}-{vote['status'].lower()}.json"

    item = {
        "ts": datetime.now(VN_TZ).isoformat(),
        "skill": skill,
        "status": vote["status"],
        "flag": vote["flag"],
        "score": vote["score"],
        "model_a": vote.get("model_a"),
        "model_b": vote.get("model_b"),
        "text_a": vote.get("agent_a", {}).get("text", "") if "agent_a" in vote else "",
        "text_b": vote.get("agent_b", {}).get("text", "") if "agent_b" in vote else "",
        "prompt_preview": prompt[:500],
    }
    item_file.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

    # Count pending items (exclude resolved/) and alert if threshold hit
    _check_queue_threshold(skill)


def _check_queue_threshold(skill: str) -> None:
    """Count pending review items. If ≥ QUEUE_ALERT_THRESHOLD, send Telegram alert."""
    try:
        if not REVIEW_QUEUE_DIR.exists():
            return
        pending = [
            f for f in REVIEW_QUEUE_DIR.iterdir()
            if f.is_file() and f.suffix == ".json"
        ]
        count = len(pending)
        if count >= QUEUE_ALERT_THRESHOLD:
            _send_queue_alert(count, skill)
    except Exception as e:
        print(f"[WARN] Queue threshold check failed: {e}")


def _send_queue_alert(count: int, trigger_skill: str) -> None:
    """Send Telegram notification that review queue is overflowing."""
    try:
        from lib.telegram import send_message
        text = (
            f"⚠️ *Dual-Vote Review Queue*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 Có *{count} items* đang chờ human review\n"
            f"🔍 Trigger skill: `{trigger_skill}`\n"
            f"🕐 {datetime.now(VN_TZ).strftime('%Y-%m-%d %H:%M %Z')}\n\n"
            f"👉 Vào Web Portal → Review → Dual-Vote Queue để xử lý."
        )
        send_message(text)
    except Exception as e:
        print(f"[WARN] Telegram queue alert failed: {e}")


def _log_vote(vote: dict, prompt: str, skill: str) -> None:
    """Append vote summary to logs/dual-vote-YYYY-MM.jsonl."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    month_str = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"dual-vote-{month_str}.jsonl"

    entry = {
        "ts": datetime.now(VN_TZ).isoformat(),
        "skill": skill,
        "status": vote.get("status"),
        "confidence": vote.get("confidence"),
        "flag": vote.get("flag"),
        "score": vote.get("score"),
        "model_a": vote.get("model_a"),
        "model_b": vote.get("model_b"),
        "cost_usd_total": vote.get("cost_usd_total"),
        "cost_usd_a": vote.get("cost_usd_a"),
        "cost_usd_b": vote.get("cost_usd_b"),
        "elapsed_ms": vote.get("elapsed_ms"),
        "prompt_len": len(prompt),
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── CLI ────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dual-agent vote on a prompt")
    parser.add_argument("prompt", nargs="?", default="Dịch vụ hosting BKNS có giá bao nhiêu?")
    parser.add_argument("--system", default="Bạn là AI tư vấn dịch vụ BKNS.")
    parser.add_argument("--skill", default="dual-vote-cli")
    args = parser.parse_args()

    print(f"Running dual-vote on: {args.prompt[:80]}")
    result = run_dual(args.prompt, system=args.system, skill=args.skill)

    print(f"\nStatus    : {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Score     : {result['score']}")
    print(f"Flag      : {result['flag']}")
    print(f"Cost      : ${result['cost_usd_total']:.6f} (A=${result['cost_usd_a']:.6f} B=${result['cost_usd_b']:.6f})")
    print(f"Elapsed   : {result['elapsed_ms']} ms")

    if "consensus" in result:
        print(f"\n── Consensus (from {result['model_a']}) ──")
        print(result["consensus"]["text"][:300])
    elif "agent_a" in result:
        print(f"\n── Agent A ({result['model_a']}) ──")
        print(result["agent_a"]["text"][:200])
        print(f"\n── Agent B ({result['model_b']}) ──")
        print(result["agent_b"]["text"][:200])
