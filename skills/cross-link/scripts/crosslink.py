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


CROSSLINK_PROMPT = """Bạn là SEO specialist cho Wiki BKNS. Phân tích danh sách trang wiki và trả về JSON GỢI Ý internal links.

CÁC TRANG WIKI:
{pages_summary}

OUTPUT — CHỈ JSON, không giải thích:
{{
  "suggestions": [
    {{
      "from_page": "products/hosting/tong-quan.md",
      "to_page": "products/ssl/tong-quan.md",
      "anchor_text": "SSL Certificate miễn phí",
      "context": "Thêm cuối section bảo mật",
      "relevance": "high"
    }}
  ],
  "orphan_pages": [],
  "hub_pages": [],
  "link_density": 0.3,
  "summary": "Tóm tắt đề xuất"
}}

QUY TẮC: Mỗi trang link đến 2-4 trang liên quan, tự nhiên, có ý nghĩa. relevance: high/medium/low."""


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

    # Build summary for prompt — keep concise to avoid token overflow
    pages_summary = []
    for path, info in pages.items():
        pages_summary.append(
            f"- {path}: {info['title']} (category: {info['category']})"
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
            max_output_tokens=8192,
        )
    except Exception as e:
        return {"status": "error", "detail": str(e)}

    text = result["text"].strip()
    # Strip markdown fences
    cleaned = re.sub(r"```json\s*", "", text)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    analysis = {}
    try:
        analysis = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: find outermost {...}
        first = cleaned.find("{")
        if first != -1:
            depth = 0
            for i in range(first, len(cleaned)):
                if cleaned[i] == "{":
                    depth += 1
                elif cleaned[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            analysis = json.loads(cleaned[first:i + 1])
                        except json.JSONDecodeError:
                            analysis = {"suggestions": [], "summary": "Parse error"}
                        break
        if not analysis:
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
