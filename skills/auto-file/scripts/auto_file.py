#!/usr/bin/env python3
"""
BKNS Agent Wiki — auto-file
Phân tích query logs → phát hiện FAQ candidates.

Usage:
    python3 scripts/auto_file.py           # Scan logs
    python3 scripts/auto_file.py --days 7  # Scan last 7 days
"""
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import LOGS_DIR, WIKI_DIR, MODEL_FLASH
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import send_report
from lib.utils import now_iso, today_str, ensure_dir


FAQ_PROMPT = """Bạn là chuyên gia nội dung BKNS.

Dưới đây là danh sách câu hỏi thường gặp từ khách hàng:
{questions}

WIKI HIỆN TẠI CÓ CÁC TRANG:
{wiki_pages}

NHIỆM VỤ: Phân tích và đề xuất FAQ mới.

1. Gom nhóm câu hỏi tương tự
2. Xếp hạng theo số lần được hỏi
3. So sánh vs wiki hiện tại — câu nào chưa có câu trả lời?
4. Đề xuất TOP 5 FAQ nên tạo trang mới

OUTPUT (JSON):
{{
  "clusters": [
    {{
      "topic": "Tên chủ đề",
      "count": 5,
      "sample_questions": ["q1", "q2"],
      "has_wiki_page": false,
      "suggested_page": "faq/topic-name.md",
      "priority": "high" | "medium" | "low"
    }}
  ],
  "total_questions_analyzed": 50,
  "gaps_found": 3,
  "summary": "Nhận xét tổng thể"
}}"""


def load_query_logs(days: int = 7) -> list[str]:
    """Load recent query questions from logs."""
    questions = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for log_file in sorted(LOGS_DIR.glob("query-*.jsonl")):
        try:
            for line in log_file.read_text(encoding="utf-8").strip().split("\n"):
                if not line.strip():
                    continue
                entry = json.loads(line)
                q = entry.get("question", "")
                if q:
                    questions.append(q)
        except (json.JSONDecodeError, KeyError):
            continue

    return questions


def list_wiki_pages() -> list[str]:
    """List all current wiki pages."""
    pages = []
    for md in sorted(WIKI_DIR.rglob("*.md")):
        if ".drafts" in str(md):
            continue
        pages.append(str(md.relative_to(WIKI_DIR)))
    return pages


def scan_faq_candidates(days: int = 7) -> dict:
    """Scan query logs and find FAQ candidates."""
    log_entry("auto-file", "start", f"Scanning last {days} days")

    questions = load_query_logs(days)
    if len(questions) < 3:
        return {"status": "skip",
                "detail": f"Chỉ có {len(questions)} questions. Cần ít nhất 3."}

    wiki_pages = list_wiki_pages()

    prompt = FAQ_PROMPT.format(
        questions="\n".join(f"- {q}" for q in questions[:100]),
        wiki_pages="\n".join(f"- {p}" for p in wiki_pages),
    )

    try:
        result = generate(
            prompt=prompt,
            model=MODEL_FLASH,
            skill="auto-file",
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
        analysis = {"clusters": [], "summary": "Parse error"}

    analysis["cost_usd"] = result.get("cost_usd", 0)

    # Report
    clusters = analysis.get("clusters", [])
    high_priority = [c for c in clusters if c.get("priority") == "high"]

    if high_priority:
        report = "\n".join(
            f"• *{c['topic']}* ({c.get('count', 0)} queries) → `{c.get('suggested_page', 'N/A')}`"
            for c in high_priority
        )
        send_report("FAQ Candidates", f"{len(high_priority)} high-priority topics:\n{report}")

    log_entry("auto-file", "success",
              f"{len(clusters)} clusters, {len(high_priority)} high-priority",
              cost_usd=analysis.get("cost_usd", 0))

    return analysis


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Auto-File FAQ")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    result = scan_faq_candidates(args.days)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
