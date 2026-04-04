"""
BKNS Agent Wiki — JSONL Structured Logging
Format: {"ts", "skill", "action", "detail", "cost_usd", "extra"}
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from lib.config import LOGS_DIR, LOGS_ERRORS_DIR

# Vietnam timezone
VN_TZ = timezone(timedelta(hours=7))


def _now_iso() -> str:
    """Current time in ISO format with Vietnam timezone."""
    return datetime.now(VN_TZ).isoformat()


def _today_str() -> str:
    """Today's date as YYYY-MM-DD string."""
    return datetime.now(VN_TZ).strftime("%Y-%m-%d")


def _ensure_dir(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def log_entry(
    skill: str,
    action: str,
    detail: str = "",
    cost_usd: float = 0.0,
    severity: str = "info",
    extra: dict = None,
) -> dict:
    """Create and write a structured log entry.

    Args:
        skill: Skill name (e.g., 'crawl-source')
        action: Action type (e.g., 'start', 'success', 'error', 'skip')
        detail: Human-readable description
        cost_usd: Cost in USD for this action
        severity: critical|high|medium|low|info
        extra: Additional data dict

    Returns:
        The log entry dict
    """
    entry = {
        "ts": _now_iso(),
        "skill": skill,
        "action": action,
        "detail": detail,
        "cost_usd": cost_usd,
        "severity": severity,
        "extra": extra or {},
    }

    # Write to skill-specific log
    _ensure_dir(LOGS_DIR)
    log_file = LOGS_DIR / f"{skill}-{_today_str()}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Also write errors to error log
    if action == "error" or severity in ("critical", "high"):
        _ensure_dir(LOGS_ERRORS_DIR)
        err_file = LOGS_ERRORS_DIR / f"{_today_str()}.jsonl"
        with open(err_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def log_intake(
    skill: str,
    source_url: str,
    raw_file: str,
    word_count: int = 0,
    extra: dict = None,
) -> dict:
    """Log an intake (crawl/ingest) event."""
    from lib.config import LOGS_INTAKE_DIR
    _ensure_dir(LOGS_INTAKE_DIR)

    entry = {
        "ts": _now_iso(),
        "skill": skill,
        "action": "ingested",
        "source_url": source_url,
        "raw_file": raw_file,
        "word_count": word_count,
        "extra": extra or {},
    }

    log_file = LOGS_INTAKE_DIR / f"{_today_str()}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def log_query(
    build_id: str,
    question: str,
    model: str,
    total_input_tokens: int = 0,
    cached_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    response_time_ms: int = 0,
    had_fallback: bool = False,
) -> dict:
    """Log a query event with cache metrics."""
    _ensure_dir(LOGS_DIR)

    cache_hit_rate = 0.0
    if total_input_tokens > 0:
        cache_hit_rate = round(cached_tokens / total_input_tokens * 100, 1)

    entry = {
        "ts": _now_iso(),
        "skill": "query-wiki",
        "build_id": build_id,
        "question": question,
        "model": model,
        "total_input_tokens": total_input_tokens,
        "cached_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "cache_hit_rate": cache_hit_rate,
        "cost_usd": cost_usd,
        "response_time_ms": response_time_ms,
        "had_fallback": had_fallback,
    }

    log_file = LOGS_DIR / f"query-{_today_str()}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def log_approval(
    filename: str,
    approved_by: str,
    build_id: str = "",
    extra: dict = None,
) -> dict:
    """Log an approval event."""
    _ensure_dir(LOGS_DIR)

    entry = {
        "ts": _now_iso(),
        "action": "approved",
        "filename": filename,
        "approved_by": approved_by,
        "build_id": build_id,
        "extra": extra or {},
    }

    month_str = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"approvals-{month_str}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
