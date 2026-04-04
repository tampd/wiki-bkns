#!/usr/bin/env python3
"""
BKNS Agent Wiki — cross-link
Phân tích wiki pages → đề xuất internal links.

Usage:
    python3 scripts/crosslink.py           # Analyze all pages
    python3 scripts/crosslink.py --apply   # Apply suggested links (draft mode)
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import WIKI_DIR, MODEL_FLASH
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import send_report
from lib.utils import read_text_safe, parse_frontmatter


CROSSLINK_PROMPT = """Bạn là SEO specialist cho Wiki BKNS.

Dưới đây là danh sách các trang wiki và nội dung tóm tắt:
{pages_summary}

NHIỆM VỤ: Đề xuất internal links giữa các trang.

QUY TẮC:
1. Mỗi trang nên link đến 2-5 trang liên quan
2. Link phải tự nhiên, có ý nghĩa
3. Ưu tiên: sản phẩm liên quan, FAQ, hỗ trợ
4. Tránh link loop vô ích

OUTPUT (JSON):
{{
  "suggestions": [
    {{
      "from_page": "products/hosting/tong-quan.md",
      "to_page": "products/ssl/tong-quan.md",
      "anchor_text": "SSL Certificate cho hosting",
      "context": "Thêm vào section bảo mật",
      "relevance": "high" | "medium" | "low"
    }}
  ],
  "orphan_pages": ["page.md"],
  "hub_pages": ["index.md"],
  "link_density": 0.5,
  "summary": "Nhận xét"
}}"""


def analyze_wiki_graph() -> dict:
    """Analyze wiki link graph and suggest cross-links."""
    log_entry("cross-link", "start", "Analyzing wiki link graph")

    pages = {}
    for md in sorted(WIKI_DIR.rglob("*.md")):
        if ".drafts" in str(md):
            continue
        rel = str(md.relative_to(WIKI_DIR))
        content = read_text_safe(str(md))
        fm, body = parse_frontmatter(content)

        # Extract existing links
        links = re.findall(r"\]\((.*?\.md)\)", body)

        pages[rel] = {
            "title": fm.get("title", rel),
            "category": fm.get("category", ""),
            "links_to": links,
            "body_preview": body[:200],
        }

    if len(pages) < 2:
        return {"status": "skip", "detail": "Cần ít nhất 2 wiki pages"}

    # Build summary for prompt
    pages_summary = []
    for path, info in pages.items():
        pages_summary.append(
            f"- {path}: {info['title']} (category: {info['category']})\n"
            f"  Links: {info['links_to']}\n"
            f"  Preview: {info['body_preview'][:100]}"
        )

    prompt = CROSSLINK_PROMPT.format(
        pages_summary="\n".join(pages_summary),
    )

    try:
        result = generate(
            prompt=prompt,
            model=MODEL_FLASH,
            skill="cross-link",
            temperature=0.2,
            max_output_tokens=4096,
        )
    except Exception as e:
        return {"status": "error", "detail": str(e)}

    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        analysis = json.loads(match.group(0)) if match else {}
    except (json.JSONDecodeError, AttributeError):
        analysis = {"suggestions": [], "summary": "Parse error"}

    analysis["cost_usd"] = result.get("cost_usd", 0)
    analysis["pages_analyzed"] = len(pages)

    # Report
    suggestions = analysis.get("suggestions", [])
    high_rel = [s for s in suggestions if s.get("relevance") == "high"]

    if high_rel:
        report = "\n".join(
            f"• `{s['from_page']}` → `{s['to_page']}`: {s.get('anchor_text', '')}"
            for s in high_rel[:5]
        )
        send_report("Cross-Link Suggestions",
                     f"{len(high_rel)} high-relevance links:\n{report}")

    log_entry("cross-link", "success",
              f"{len(suggestions)} link suggestions for {len(pages)} pages",
              cost_usd=analysis.get("cost_usd", 0))

    return analysis


def main():
    result = analyze_wiki_graph()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
