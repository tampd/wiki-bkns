#!/usr/bin/env python3
"""
BKNS Agent Wiki — lint-wiki
Two-layer quality check: Python syntax + Gemini Pro semantic analysis.

Usage:
    python3 scripts/lint.py              # Lint all wiki files
    python3 scripts/lint.py [file.md]    # Lint specific file
"""
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    WIKI_DIR, LINT_RULES, LOGS_LINT_DIR, get_pro_model,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import send_report
from lib.utils import (
    parse_frontmatter, read_text_safe, today_str, now_iso, ensure_dir,
)


# ── Layer 1: Python Syntax Lint ────────────────────────────
def lint_syntax(file_path: Path) -> list[dict]:
    """Run syntax checks on a wiki Markdown file.

    Returns list of lint issues.
    """
    issues = []
    content = read_text_safe(str(file_path))
    if not content:
        issues.append({
            "type": "error",
            "rule": "empty_file",
            "message": f"File trống: {file_path.name}",
            "line": 0,
        })
        return issues

    fm, body = parse_frontmatter(content)

    # Check frontmatter exists
    if LINT_RULES["require_frontmatter"] and not fm:
        issues.append({
            "type": "error",
            "rule": "missing_frontmatter",
            "message": f"Thiếu YAML frontmatter",
            "line": 1,
        })
        return issues

    # Check required fields
    for field in LINT_RULES.get("required_fields", []):
        if field not in fm:
            issues.append({
                "type": "warning",
                "rule": "missing_field",
                "message": f"Thiếu field '{field}' trong frontmatter",
                "line": 1,
            })

    # Check stale content
    updated = fm.get("updated", "")
    if updated:
        try:
            update_date = datetime.strptime(str(updated), "%Y-%m-%d")
            threshold = timedelta(days=LINT_RULES.get("stale_threshold_days", 30))
            if datetime.now() - update_date > threshold:
                issues.append({
                    "type": "warning",
                    "rule": "stale_content",
                    "message": f"Nội dung cũ: cập nhật lần cuối {updated} "
                               f"(>{LINT_RULES['stale_threshold_days']} ngày)",
                    "line": 1,
                })
        except ValueError:
            pass

    # Check body length
    if len(body.strip()) < LINT_RULES.get("min_body_length", 50):
        issues.append({
            "type": "warning",
            "rule": "short_body",
            "message": f"Body quá ngắn: {len(body)} chars (min: {LINT_RULES['min_body_length']})",
            "line": 1,
        })

    # Check broken image references
    if LINT_RULES.get("check_broken_images"):
        image_refs = re.findall(r"!\[.*?\]\((.*?)\)", body)
        for img in image_refs:
            if img.startswith("http"):
                continue
            img_path = file_path.parent / img
            if not img_path.exists():
                issues.append({
                    "type": "error",
                    "rule": "broken_image",
                    "message": f"Ảnh không tồn tại: {img}",
                    "line": 0,
                })

    return issues


def lint_orphan_check() -> list[dict]:
    """Find orphan wiki files not linked from index."""
    issues = []
    if not LINT_RULES.get("check_orphan_files"):
        return issues

    index = WIKI_DIR / "index.md"
    if not index.exists():
        return issues

    index_content = read_text_safe(str(index))
    linked_files = set(re.findall(r"\]\((.*?\.md)\)", index_content))

    for md in WIKI_DIR.rglob("*.md"):
        if ".drafts" in str(md):
            continue
        if md.name == "index.md":
            continue
        rel = str(md.relative_to(WIKI_DIR))
        if rel not in linked_files:
            issues.append({
                "type": "info",
                "rule": "orphan_file",
                "message": f"File chưa được link từ index: {rel}",
                "line": 0,
            })

    return issues


# ── Layer 2: Gemini Semantic Lint ──────────────────────────
SEMANTIC_LINT_PROMPT = """Bạn là QA editor cho Wiki BKNS.

Phân tích trang wiki sau và tìm các vấn đề:

{content}

KIỂM TRA:
1. Giá cả có xung đột nhau không? (cùng sản phẩm, khác giá)
2. Thông tin nào có thể đã lỗi thời?
3. Có claim nào thiếu nguồn?
4. Có mâu thuẫn logic nào?
5. TOP {suggest_count} cải thiện nên làm?

OUTPUT (JSON):
{{
  "issues": [
    {{
      "type": "price_conflict" | "outdated" | "missing_source" | "inconsistency" | "suggestion",
      "severity": "critical" | "high" | "medium" | "low",
      "message": "Mô tả vấn đề",
      "suggested_fix": "Gợi ý sửa"
    }}
  ],
  "overall_quality": 0-100,
  "summary": "Nhận xét tổng thể"
}}"""


def lint_semantic(file_path: Path) -> dict:
    """Run Gemini Pro semantic analysis on wiki file."""
    content = read_text_safe(str(file_path))
    if len(content) < 100:
        return {"issues": [], "overall_quality": 0, "summary": "File quá ngắn"}

    prompt = SEMANTIC_LINT_PROMPT.format(
        content=content[:30000],
        suggest_count=LINT_RULES.get("suggest_improvements", 5),
    )

    try:
        result = generate(
            prompt=prompt,
            model=get_pro_model(),
            skill="lint-wiki",
            temperature=0.1,
            max_output_tokens=4096,
        )
    except Exception as e:
        return {"issues": [], "overall_quality": 0,
                "summary": f"API error: {str(e)}",
                "cost_usd": 0}

    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        review = json.loads(match.group(0)) if match else {}
    except (json.JSONDecodeError, AttributeError):
        review = {"issues": [], "summary": "Parse error"}

    review["cost_usd"] = result.get("cost_usd", 0)
    return review


def lint_all(semantic: bool = False) -> dict:
    """Run full lint on all wiki files.

    Args:
        semantic: If True, also run Gemini semantic analysis

    Returns:
        Summary dict
    """
    log_entry("lint-wiki", "start", f"Linting wiki (semantic={semantic})")

    all_syntax_issues = []
    all_semantic_issues = []
    total_cost = 0

    # Syntax lint per file
    for md in sorted(WIKI_DIR.rglob("*.md")):
        if ".drafts" in str(md):
            continue
        issues = lint_syntax(md)
        for i in issues:
            i["file"] = str(md.relative_to(WIKI_DIR))
        all_syntax_issues.extend(issues)

    # Orphan check
    orphans = lint_orphan_check()
    all_syntax_issues.extend(orphans)

    # Semantic lint (optional, costs money)
    if semantic:
        for md in sorted(WIKI_DIR.rglob("*.md")):
            if ".drafts" in str(md):
                continue
            result = lint_semantic(md)
            total_cost += result.get("cost_usd", 0)
            for i in result.get("issues", []):
                i["file"] = str(md.relative_to(WIKI_DIR))
            all_semantic_issues.extend(result.get("issues", []))

    # Save lint report
    ensure_dir(LOGS_LINT_DIR)
    report = {
        "ts": now_iso(),
        "syntax_issues": len(all_syntax_issues),
        "semantic_issues": len(all_semantic_issues),
        "total_cost_usd": total_cost,
        "syntax": all_syntax_issues,
        "semantic": all_semantic_issues,
    }
    report_path = LOGS_LINT_DIR / f"lint-{today_str()}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Summary for Telegram
    errors = [i for i in all_syntax_issues if i["type"] == "error"]
    warnings = [i for i in all_syntax_issues if i["type"] == "warning"]

    report_text = (
        f"Syntax: {len(errors)} errors, {len(warnings)} warnings\n"
        f"Semantic: {len(all_semantic_issues)} issues\n"
        f"Cost: ${total_cost:.4f}\n"
        f"Report: `{report_path}`"
    )
    send_report("Wiki Lint Report", report_text)

    log_entry("lint-wiki", "success",
              f"{len(errors)} errors, {len(warnings)} warnings, "
              f"{len(all_semantic_issues)} semantic",
              cost_usd=total_cost)

    print(f"\nLint Summary:")
    print(f"  Syntax errors: {len(errors)}")
    print(f"  Syntax warnings: {len(warnings)}")
    print(f"  Semantic issues: {len(all_semantic_issues)}")
    print(f"  Cost: ${total_cost:.4f}")

    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Wiki Lint")
    parser.add_argument("file", nargs="?", help="Specific file to lint")
    parser.add_argument("--semantic", "-s", action="store_true",
                        help="Include Gemini semantic analysis")
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        issues = lint_syntax(path)
        for i in issues:
            print(f"  [{i['type']}] {i['rule']}: {i['message']}")
        if args.semantic:
            sem = lint_semantic(path)
            for i in sem.get("issues", []):
                print(f"  [semantic] {i['type']}: {i['message']}")
    else:
        lint_all(semantic=args.semantic)


if __name__ == "__main__":
    main()
