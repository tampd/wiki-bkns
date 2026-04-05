"""
BKNS Agent Wiki — Vertex AI Gemini Wrapper
Supports Flash + Pro model switching, token counting, cost tracking, retry logic.
"""
import os
import time
import json
from typing import Optional

from lib.config import (
    GOOGLE_CREDENTIALS, GOOGLE_PROJECT, GOOGLE_LOCATION,
    MODEL_FLASH, MODEL_PRO, SKILL_MODELS,
)
from lib.logger import log_entry

# Set credentials before importing google libs
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS

from google import genai
from google.genai import types


# ── Client Singleton ───────────────────────────────────────
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """Get or create Vertex AI Genai client."""
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=GOOGLE_PROJECT,
            location=GOOGLE_LOCATION,
        )
    return _client


# ── Cost Calculator ────────────────────────────────────────
# Pricing per 1M tokens (USD)
PRICING = {
    MODEL_FLASH: {"input": 0.30, "input_cached": 0.030, "output": 2.50},
    MODEL_PRO: {"input": 1.25, "input_cached": 0.125, "output": 10.00},
}


def calculate_cost(
    model: str,
    input_tokens: int,
    cached_tokens: int,
    output_tokens: int,
) -> float:
    """Calculate USD cost for a Gemini API call."""
    prices = PRICING.get(model, PRICING[MODEL_FLASH])
    non_cached = input_tokens - cached_tokens

    cost = (
        (non_cached / 1_000_000) * prices["input"]
        + (cached_tokens / 1_000_000) * prices["input_cached"]
        + (output_tokens / 1_000_000) * prices["output"]
    )
    return round(cost, 6)


# ── Generate Text ──────────────────────────────────────────
def generate(
    prompt: str,
    model: str = None,
    skill: str = "unknown",
    system_instruction: str = None,
    temperature: float = 0.2,
    max_output_tokens: int = 8192,
    retry_count: int = 2,
    retry_interval: float = 5.0,
) -> dict:
    """Generate text with Gemini model.

    Args:
        prompt: User prompt text
        model: Model name (defaults to skill's assigned model)
        skill: Skill name for logging
        system_instruction: System prompt
        temperature: Sampling temperature
        max_output_tokens: Max output tokens
        retry_count: Number of retries on failure
        retry_interval: Seconds between retries

    Returns:
        dict with keys: text, input_tokens, cached_tokens, output_tokens, cost_usd, model
    """
    if model is None:
        model = SKILL_MODELS.get(skill, MODEL_FLASH)

    if model is None:
        raise ValueError(f"Skill '{skill}' does not use LLM")

    client = get_client()
    last_error = None

    for attempt in range(retry_count + 1):
        try:
            start_time = time.time()

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Extract token usage
            usage = response.usage_metadata
            input_tokens = getattr(usage, "prompt_token_count", 0) or 0
            cached_tokens = getattr(usage, "cached_content_token_count", 0) or 0
            output_tokens = getattr(usage, "candidates_token_count", 0) or 0

            cost = calculate_cost(model, input_tokens, cached_tokens, output_tokens)

            result = {
                "text": response.text,
                "input_tokens": input_tokens,
                "cached_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "model": model,
                "elapsed_ms": elapsed_ms,
            }

            log_entry(
                skill=skill,
                action="llm_call",
                detail=f"model={model} in={input_tokens} cached={cached_tokens} out={output_tokens}",
                cost_usd=cost,
                extra={
                    "model": model,
                    "input_tokens": input_tokens,
                    "cached_tokens": cached_tokens,
                    "output_tokens": output_tokens,
                    "elapsed_ms": elapsed_ms,
                    "attempt": attempt + 1,
                }
            )

            return result

        except Exception as e:
            last_error = e
            log_entry(
                skill=skill,
                action="error",
                detail=f"Gemini API error (attempt {attempt + 1}): {str(e)}",
                severity="high" if attempt < retry_count else "critical",
            )
            if attempt < retry_count:
                time.sleep(retry_interval)

    raise RuntimeError(
        f"Gemini API failed after {retry_count + 1} attempts: {last_error}"
    )


# ── Generate with Prefix Caching ───────────────────────────
def generate_with_cache(
    prefix_content: str,
    question: str,
    model: str = None,
    skill: str = "query-wiki",
    system_instruction: str = None,
    temperature: float = 0.2,
    max_output_tokens: int = 4096,
    retry_count: int = 2,
    retry_interval: float = 5.0,
) -> dict:
    """Generate text using implicit caching pattern.

    Sends prefix (wiki content) as first turn, question as second turn.
    Gemini automatically caches the prefix for 90% discount.

    Args:
        prefix_content: Large content to cache (wiki)
        question: User question (changes each time)
        model: Model name
        skill: Skill name for logging
        system_instruction: System prompt
        temperature: Sampling temperature
        max_output_tokens: Max output tokens
        retry_count: Number of retries on failure
        retry_interval: Seconds between retries

    Returns:
        dict with same keys as generate() plus cache_hit_rate
    """
    if model is None:
        model = SKILL_MODELS.get(skill, MODEL_FLASH)

    client = get_client()

    contents = [
        types.Content(role="user", parts=[
            types.Part.from_text(text=f"Tài liệu wiki BKNS:\n\n{prefix_content}")
        ]),
        types.Content(role="model", parts=[
            types.Part.from_text(text="Đã đọc tài liệu. Sẵn sàng trả lời.")
        ]),
        types.Content(role="user", parts=[
            types.Part.from_text(text=question)
        ]),
    ]

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    last_error = None

    for attempt in range(retry_count + 1):
        try:
            start_time = time.time()

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            usage = response.usage_metadata
            input_tokens = getattr(usage, "prompt_token_count", 0) or 0
            cached_tokens = getattr(usage, "cached_content_token_count", 0) or 0
            output_tokens = getattr(usage, "candidates_token_count", 0) or 0

            cost = calculate_cost(model, input_tokens, cached_tokens, output_tokens)

            cache_hit_rate = 0.0
            if input_tokens > 0:
                cache_hit_rate = round(cached_tokens / input_tokens * 100, 1)

            log_entry(
                skill=skill,
                action="llm_call_cached",
                detail=f"model={model} in={input_tokens} cached={cached_tokens} out={output_tokens} cache_hit={cache_hit_rate}%",
                cost_usd=cost,
                extra={
                    "model": model,
                    "input_tokens": input_tokens,
                    "cached_tokens": cached_tokens,
                    "output_tokens": output_tokens,
                    "elapsed_ms": elapsed_ms,
                    "cache_hit_rate": cache_hit_rate,
                    "attempt": attempt + 1,
                }
            )

            return {
                "text": response.text,
                "input_tokens": input_tokens,
                "cached_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "model": model,
                "elapsed_ms": elapsed_ms,
                "cache_hit_rate": cache_hit_rate,
            }

        except Exception as e:
            last_error = e
            log_entry(
                skill=skill,
                action="error",
                detail=f"generate_with_cache error (attempt {attempt + 1}): {str(e)}",
                severity="high" if attempt < retry_count else "critical",
            )
            if attempt < retry_count:
                time.sleep(retry_interval)

    raise RuntimeError(
        f"generate_with_cache failed after {retry_count + 1} attempts: {last_error}"
    )


# ── Generate with Image (Vision) ──────────────────────────
def generate_with_image(
    image_path: str,
    prompt: str,
    model: str = None,
    skill: str = "ingest-image",
    temperature: float = 0.1,
    max_output_tokens: int = 8192,
) -> dict:
    """Generate text from image using Gemini Vision.

    Args:
        image_path: Path to image file
        prompt: Extraction prompt
        model: Model name (defaults to Flash)
        skill: Skill name for logging

    Returns:
        dict with same keys as generate()
    """
    if model is None:
        model = SKILL_MODELS.get(skill, MODEL_FLASH)

    client = get_client()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Determine MIME type
    ext = image_path.lower().rsplit(".", 1)[-1]
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")

    contents = [
        types.Content(role="user", parts=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(text=prompt),
        ]),
    ]

    start_time = time.time()

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    usage = response.usage_metadata
    input_tokens = getattr(usage, "prompt_token_count", 0) or 0
    cached_tokens = getattr(usage, "cached_content_token_count", 0) or 0
    output_tokens = getattr(usage, "candidates_token_count", 0) or 0

    cost = calculate_cost(model, input_tokens, cached_tokens, output_tokens)

    return {
        "text": response.text,
        "input_tokens": input_tokens,
        "cached_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
        "model": model,
        "elapsed_ms": elapsed_ms,
    }
