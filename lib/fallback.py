"""
BKNS Agent Wiki — LLM Fallback Chain

Provides a `generate_with_fallback()` wrapper that tries providers in order
and transparently falls back on failure. Keeps call site simple and raises
only when ALL providers in the chain are exhausted.

Chain (default): Gemini Pro → Gemini Flash → OpenAI (GPT-5.4)

Usage:
    from lib.fallback import generate_with_fallback

    result = generate_with_fallback(
        prompt="...",
        skill="query-wiki",
        system_instruction="...",
    )

Design notes:
- No Claude integration yet — reserved for a future lib/anthropic_client.py
- `result` shape mirrors lib.gemini.generate() output so callers are agnostic
- Cross-provider fallback logs every attempt to logs/fallback-YYYY-MM.jsonl
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable

from lib.config import MODEL_FLASH, MODEL_PRO, LOGS_DIR, OPENAI_MODEL, get_pro_model
from lib.logger import log_entry

VN_TZ = timezone(timedelta(hours=7))


class AllProvidersFailed(RuntimeError):
    """Raised when every provider in the fallback chain raises."""


@dataclass(frozen=True)
class ProviderSpec:
    name: str                       # Human label, e.g. "gemini-pro"
    model: str                      # Model string passed to underlying client
    call: Callable[..., dict]       # Low-level generate() function


def _gemini_call(prompt: str, model: str, skill: str, system_instruction: str | None,
                 temperature: float, max_output_tokens: int) -> dict:
    from lib.gemini import generate as gemini_generate
    return gemini_generate(
        prompt=prompt,
        model=model,
        skill=skill,
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


def _openai_call(prompt: str, model: str, skill: str, system_instruction: str | None,
                 temperature: float, max_output_tokens: int) -> dict:
    from lib.openai_client import generate as openai_generate
    return openai_generate(
        prompt=prompt,
        model=model,
        skill=skill,
        system=system_instruction,
        temperature=temperature,
        max_tokens=max_output_tokens,
    )


def default_chain() -> list[ProviderSpec]:
    """Return the default provider chain.

    Order matters: cheapest + most-reliable-first. Gemini Pro is primary
    because it has implicit caching and is already instrumented for cost
    tracking. GPT-5.4 is the last resort.
    """
    return [
        ProviderSpec(name="gemini-pro", model=get_pro_model(), call=_gemini_call),
        ProviderSpec(name="gemini-flash", model=MODEL_FLASH, call=_gemini_call),
        ProviderSpec(name="openai", model=OPENAI_MODEL, call=_openai_call),
    ]


def _log_fallback(skill: str, attempts: list[dict[str, Any]], final_provider: str | None) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    month = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"fallback-{month}.jsonl"
    entry = {
        "ts": datetime.now(VN_TZ).isoformat(),
        "skill": skill,
        "attempts": attempts,
        "final_provider": final_provider,
        "success": final_provider is not None,
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate_with_fallback(
    prompt: str,
    skill: str = "unknown",
    system_instruction: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 8192,
    chain: Iterable[ProviderSpec] | None = None,
) -> dict:
    """Run `prompt` against provider chain, returning the first success.

    Returns:
        dict shaped like lib.gemini.generate() with an extra `provider` key.

    Raises:
        AllProvidersFailed: if every provider in the chain raised.
    """
    providers = list(chain) if chain is not None else default_chain()
    attempts: list[dict[str, Any]] = []

    for provider in providers:
        try:
            result = provider.call(
                prompt=prompt,
                model=provider.model,
                skill=skill,
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            result["provider"] = provider.name
            attempts.append({"provider": provider.name, "status": "ok"})
            _log_fallback(skill, attempts, provider.name)
            return result
        except Exception as exc:  # noqa: BLE001 — we want any-exception fallback here
            attempts.append({
                "provider": provider.name,
                "status": "error",
                "error": str(exc)[:300],
            })
            log_entry(
                skill=skill,
                action="fallback",
                detail=f"{provider.name} failed → next provider: {exc}",
                severity="medium",
            )

    _log_fallback(skill, attempts, None)
    raise AllProvidersFailed(
        f"All providers exhausted for skill={skill}. Attempts: {attempts}"
    )
