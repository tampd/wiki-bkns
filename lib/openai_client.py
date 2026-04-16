"""
BKNS Agent Wiki — OpenAI GPT-5.4 Wrapper (PART 05)
Mirrors lib/gemini.py interface for drop-in use in dual-vote (PART 06).

Auth: Bearer API key via OPENAI_API_KEY in .env
Retry: exponential backoff (1s → 2s → 4s) on rate limit / timeout
Logging: all calls written to logs/openai-calls-YYYY-MM.jsonl
"""
import time
from typing import Optional
from pathlib import Path

from openai import OpenAI, RateLimitError, APITimeoutError, APIConnectionError, APIStatusError

from lib.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_MODEL_MINI,
    OPENAI_BASE_URL,
    OPENAI_MAX_RETRIES,
    OPENAI_TIMEOUT,
    LOGS_DIR,
)
from lib.logger import log_entry

import json
from datetime import datetime, timezone, timedelta

VN_TZ = timezone(timedelta(hours=7))

# Lazy singleton
_client: Optional[OpenAI] = None

# ── Pricing per 1M tokens (USD) — updated 2026-04 ──────────
PRICING: dict[str, dict[str, float]] = {
    "gpt-5.4": {
        "input": 2.50,
        "input_cached": 0.25,
        "output": 15.00,
    },
    "gpt-5.4-mini": {
        "input": 0.40,
        "input_cached": 0.04,
        "output": 1.60,
    },
    "gpt-5.4-nano": {
        "input": 0.10,
        "input_cached": 0.01,
        "output": 0.40,
    },
}


def get_client() -> OpenAI:
    """Return the singleton OpenAI client.

    Raises:
        RuntimeError: if OPENAI_API_KEY is not set in .env
    """
    global _client
    if _client is None:
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-your"):
            raise RuntimeError(
                "OPENAI_API_KEY chưa được cấu hình. "
                "Vào https://platform.openai.com/api-keys → tạo key → "
                "điền vào OPENAI_API_KEY trong /wiki/.env"
            )
        _client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            timeout=OPENAI_TIMEOUT,
            max_retries=0,  # We handle retries manually for logging
        )
    return _client


def calculate_cost(
    model: str,
    in_tok: int,
    cached_tok: int,
    out_tok: int,
) -> float:
    """Calculate USD cost for an OpenAI API call."""
    p = PRICING.get(model, PRICING["gpt-5.4"])
    non_cached = in_tok - cached_tok
    cost = (
        non_cached * p["input"]
        + cached_tok * p["input_cached"]
        + out_tok * p["output"]
    ) / 1_000_000
    return round(cost, 6)


def _log_openai_call(
    skill: str,
    model: str,
    in_tok: int,
    cached_tok: int,
    out_tok: int,
    cost: float,
    success: bool,
    error: str = "",
    elapsed_ms: int = 0,
    attempt: int = 1,
) -> None:
    """Write structured log to logs/openai-calls-YYYY-MM.jsonl."""
    month_str = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"openai-calls-{month_str}.jsonl"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.now(VN_TZ).isoformat(),
        "skill": skill,
        "model": model,
        "in_tok": in_tok,
        "cached_tok": cached_tok,
        "out_tok": out_tok,
        "cost": cost,
        "success": success,
        "error": error,
        "elapsed_ms": elapsed_ms,
        "attempt": attempt,
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate(
    prompt: str,
    *,
    model: str = None,
    system: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 8000,
    skill: str = "unknown",
) -> dict:
    """Generate text with OpenAI GPT model.

    Mirrors lib/gemini.generate() interface for dual-vote compatibility.

    Args:
        prompt: User message
        model: Model name (default: OPENAI_MODEL from .env)
        system: System prompt
        temperature: Sampling temperature (0.0–1.0)
        max_tokens: Max output tokens
        skill: Skill name for structured logging

    Returns:
        dict with keys: text, input_tokens, cached_tokens, output_tokens,
                        cost_usd, model, elapsed_ms

    Raises:
        RuntimeError: if all retries exhausted
    """
    if model is None:
        model = OPENAI_MODEL

    client = get_client()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    last_error: Optional[Exception] = None

    for attempt in range(OPENAI_MAX_RETRIES + 1):
        try:
            start_time = time.time()

            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            usage = resp.usage
            in_tok = usage.prompt_tokens if usage else 0
            # OpenAI reports cached tokens under prompt_tokens_details
            cached_tok = 0
            if usage and hasattr(usage, "prompt_tokens_details") and usage.prompt_tokens_details:
                cached_tok = getattr(usage.prompt_tokens_details, "cached_tokens", 0) or 0
            out_tok = usage.completion_tokens if usage else 0

            cost = calculate_cost(model, in_tok, cached_tok, out_tok)

            _log_openai_call(
                skill=skill, model=model,
                in_tok=in_tok, cached_tok=cached_tok, out_tok=out_tok,
                cost=cost, success=True, elapsed_ms=elapsed_ms, attempt=attempt + 1,
            )

            log_entry(
                skill=skill,
                action="openai_call",
                detail=f"model={model} in={in_tok} cached={cached_tok} out={out_tok}",
                cost_usd=cost,
                extra={
                    "model": model,
                    "input_tokens": in_tok,
                    "cached_tokens": cached_tok,
                    "output_tokens": out_tok,
                    "elapsed_ms": elapsed_ms,
                    "attempt": attempt + 1,
                },
            )

            return {
                "text": resp.choices[0].message.content,
                "input_tokens": in_tok,
                "cached_tokens": cached_tok,
                "output_tokens": out_tok,
                "cost_usd": cost,
                "model": model,
                "elapsed_ms": elapsed_ms,
            }

        except (RateLimitError, APITimeoutError, APIConnectionError) as e:
            last_error = e
            delay = 2 ** attempt  # 1s, 2s, 4s
            error_str = str(e)

            _log_openai_call(
                skill=skill, model=model,
                in_tok=0, cached_tok=0, out_tok=0,
                cost=0.0, success=False, error=error_str[:200],
                elapsed_ms=0, attempt=attempt + 1,
            )
            log_entry(
                skill=skill,
                action="error",
                detail=f"OpenAI retryable error (attempt {attempt + 1}/{OPENAI_MAX_RETRIES + 1}): {error_str}",
                severity="high" if attempt < OPENAI_MAX_RETRIES else "critical",
            )

            if attempt < OPENAI_MAX_RETRIES:
                time.sleep(delay)

        except APIStatusError as e:
            # Non-retryable (4xx except 429)
            error_str = str(e)
            _log_openai_call(
                skill=skill, model=model,
                in_tok=0, cached_tok=0, out_tok=0,
                cost=0.0, success=False, error=error_str[:200],
                elapsed_ms=0, attempt=attempt + 1,
            )
            log_entry(
                skill=skill,
                action="error",
                detail=f"OpenAI API error (non-retryable): {error_str}",
                severity="critical",
            )
            raise RuntimeError(f"OpenAI API non-retryable error: {e}") from e

    raise RuntimeError(
        f"OpenAI API failed after {OPENAI_MAX_RETRIES + 1} attempts: {last_error}"
    )
