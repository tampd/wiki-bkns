#!/usr/bin/env python3
"""
BKNS Agent Wiki — query-wiki
Trả lời câu hỏi dựa trên wiki content + Implicit Context Caching.

Usage:
    python3 scripts/query.py "Hosting BKNS giá bao nhiêu?"
    python3 scripts/query.py --interactive  # Interactive mode
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    WIKI_DIR, BUILD_DIR, MODEL_FLASH, MAX_QUERY_COST_USD,
)
from lib.gemini import generate_with_cache
from lib.fallback import generate_with_fallback, AllProvidersFailed
from lib.logger import log_entry, log_query
from lib.telegram import notify_skill, notify_error
from lib.utils import (
    read_yaml, now_iso, today_str, read_text_safe,
)


# ── System Instruction for Query ──────────────────────────
SYSTEM_INSTRUCTION = """Bạn là trợ lý BKNS Wiki — chuyên viên tư vấn sản phẩm BKNS.

QUY TẮC TUYỆT ĐỐI:
1. ✅ CHỈ trả lời dựa trên tài liệu wiki được cung cấp
2. ❌ KHÔNG bịa thông tin — nếu wiki không có → nói rõ "tôi không có thông tin này trong wiki"
3. ✅ Trả lời ngắn gọn, chính xác, dễ hiểu
4. ✅ Nếu hỏi giá → trích dẫn CHÍNH XÁC từ wiki, ghi rõ nguồn page
5. ✅ Nếu hỏi hotline → 1900 63 68 09 (kỹ thuật) hoặc 1800 646 884 (tư vấn)
6. ✅ Cuối mỗi câu trả lời, ghi: "📖 Nguồn: [tên page wiki]"
7. ✅ Tiếng Việt tự nhiên, thân thiện

Nếu câu hỏi NGOÀI phạm vi BKNS → nói lịch sự "Tôi chỉ hỗ trợ thông tin về sản phẩm BKNS"."""


def load_wiki_content() -> str:
    """Load all wiki pages into a single string for caching prefix."""
    pages = []

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        # Skip drafts
        if ".drafts" in str(md_file):
            continue

        content = read_text_safe(str(md_file))
        if content:
            rel_path = md_file.relative_to(WIKI_DIR)
            pages.append(f"=== {rel_path} ===\n{content}")

    wiki_text = "\n\n".join(pages)

    log_entry("query-wiki", "wiki_loaded",
              f"Loaded {len(pages)} pages, ~{len(wiki_text)} chars")

    return wiki_text


def query(question: str, wiki_content: str = None) -> dict:
    """Answer a question using wiki content + caching.

    Args:
        question: User's question in Vietnamese
        wiki_content: Pre-loaded wiki content (optional, loaded if None)

    Returns:
        dict with answer, cost, cache metrics
    """
    if not wiki_content:
        wiki_content = load_wiki_content()

    if not wiki_content.strip():
        return {
            "answer": "Wiki hiện tại chưa có nội dung. Vui lòng chạy /compile trước.",
            "cost_usd": 0,
            "cache_hit_rate": 0,
        }

    log_entry("query-wiki", "start", f"Question: {question[:100]}")

    # Active build info
    build_info = read_yaml(BUILD_DIR / "active-build.yaml")
    build_id = build_info.get("build_id", "dev")

    try:
        result = generate_with_cache(
            prefix_content=wiki_content,
            question=question,
            model=MODEL_FLASH,
            skill="query-wiki",
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=4096,
        )
    except Exception as primary_err:
        # Primary (Gemini Flash with implicit cache) failed.
        # Fall back to the provider chain on a flat (non-cached) prompt so the
        # user still gets an answer instead of a hard failure.
        log_entry("query-wiki", "fallback",
                  f"Primary Gemini Flash failed, trying fallback chain: {primary_err}",
                  severity="medium")
        flat_prompt = f"Tài liệu wiki BKNS:\n\n{wiki_content}\n\nCâu hỏi: {question}"
        try:
            result = generate_with_fallback(
                prompt=flat_prompt,
                skill="query-wiki",
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=4096,
            )
            # generate() doesn't report cache_hit_rate — set to 0
            result.setdefault("cache_hit_rate", 0)
        except AllProvidersFailed as e:
            error_msg = f"All providers failed: {e}"
            log_entry("query-wiki", "error", error_msg, severity="critical")
            return {
                "answer": "Hệ thống tạm thời không phản hồi. Vui lòng thử lại sau ít phút.",
                "cost_usd": 0,
                "cache_hit_rate": 0,
            }

    answer = result["text"]
    cost = result.get("cost_usd", 0)
    cache_hit = result.get("cache_hit_rate", 0)

    # Cost alert
    if cost > MAX_QUERY_COST_USD:
        notify_skill("query-wiki",
                      f"⚠️ Query cost cao: ${cost:.4f} (max: ${MAX_QUERY_COST_USD})",
                      severity="medium")

    # Log query
    log_query(
        build_id=str(build_id),
        question=question,
        model=MODEL_FLASH,
        total_input_tokens=result.get("input_tokens", 0),
        cached_tokens=result.get("cached_tokens", 0),
        output_tokens=result.get("output_tokens", 0),
        cost_usd=cost,
        response_time_ms=result.get("elapsed_ms", 0),
    )

    log_entry("query-wiki", "success",
              f"Answered ({len(answer)} chars, cache={cache_hit}%, ${cost:.5f})",
              cost_usd=cost)

    return {
        "answer": answer,
        "cost_usd": cost,
        "cache_hit_rate": cache_hit,
        "input_tokens": result.get("input_tokens", 0),
        "cached_tokens": result.get("cached_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
        "elapsed_ms": result.get("elapsed_ms", 0),
    }


def interactive_mode():
    """Interactive Q&A mode."""
    print("=" * 50)
    print("BKNS Wiki — Interactive Query Mode")
    print("Gõ câu hỏi bằng tiếng Việt. 'exit' để thoát.")
    print("=" * 50)

    wiki_content = load_wiki_content()
    print(f"📚 Loaded wiki: {len(wiki_content)} chars\n")

    while True:
        try:
            question = input("❓ Câu hỏi: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not question or question.lower() in ("exit", "quit", "q"):
            print("👋 Tạm biệt!")
            break

        result = query(question, wiki_content)
        print(f"\n💡 {result['answer']}")
        print(f"\n📊 Cache: {result['cache_hit_rate']}% | "
              f"Cost: ${result['cost_usd']:.5f} | "
              f"Time: {result.get('elapsed_ms', 0)}ms")
        print("-" * 50)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Wiki Query")
    parser.add_argument("question", nargs="?", help="Question to ask")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.question:
        result = query(args.question)
        print(f"\n{result['answer']}")
        print(f"\n---\nCache: {result['cache_hit_rate']}% | Cost: ${result['cost_usd']:.5f}")
    else:
        print("Usage: python3 query.py 'câu hỏi' | --interactive")


if __name__ == "__main__":
    main()
