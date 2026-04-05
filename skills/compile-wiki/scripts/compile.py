#!/usr/bin/env python3
"""
BKNS Agent Wiki — compile-wiki
Đọc claims/approved/ → Gemini Pro compile → wiki Markdown + self-review.
BẮT BUỘC: self-review vs nguồn claims. Block nếu hallucination.

Usage:
    python3 scripts/compile.py [category]    # e.g. hosting, vps
    python3 scripts/compile.py --all         # Compile tất cả categories
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    CLAIMS_APPROVED_DIR, CLAIMS_DRAFTS_DIR, WIKI_DRAFTS_DIR, WIKI_DIR,
    SELF_REVIEW_RULES, MODEL_PRO,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import notify_skill, notify_error
from lib.utils import (
    read_yaml, write_yaml, now_iso, today_str, ensure_dir,
    write_markdown_with_frontmatter, read_text_safe,
)


# ── Compile Prompt ─────────────────────────────────────────
COMPILE_PROMPT = """Bạn là biên tập viên chuyên nghiệp cho Wiki tri thức BKNS.

INPUT — Danh sách claims đã được duyệt:
{claims_content}

NHIỆM VỤ: Tổng hợp claims thành 1 trang wiki Markdown hoàn chỉnh.

QUY TẮC:
1. ✅ CHỈ sử dụng dữ liệu từ claims — KHÔNG thêm thông tin ngoài
2. ✅ Bảng giá → dùng Markdown table, giữ nguyên số liệu
3. ✅ Thông số kỹ thuật → nhóm theo gói/plan
4. ✅ Viết tiếng Việt tự nhiên, dễ hiểu
5. ❌ KHÔNG bịa thêm features, giá, chính sách
6. ❌ KHÔNG dùng từ "có lẽ", "có thể", "khoảng" cho số liệu cụ thể
7. ✅ Cuối trang ghi: "Compiled by BKNS Wiki Bot • {date}"
8. ✅ Ghi nguồn claim_id mà bạn đã sử dụng

CATEGORY: {category}
TITLE: {title}

OUTPUT: Markdown thuần (không frontmatter, không code fence)."""


# ── Self-Review Prompt ─────────────────────────────────────
SELF_REVIEW_PROMPT = """Bạn là auditor kiểm tra chất lượng wiki BKNS.

WIKI DRAFT:
{draft_content}

CLAIMS GỐC (nguồn đáng tin cậy):
{claims_content}

NHIỆM VỤ: Kiểm tra draft vs claims, tìm hallucination.

KIỂM TRA:
1. Mỗi con số trong draft CÓ KHỚP với claims không?
2. Có feature/tính năng nào trong draft mà KHÔNG CÓ trong claims?
3. Có thiếu thông tin quan trọng nào từ claims?
4. Hotline/email/URL có chính xác?

OUTPUT (JSON):
{{
  "verdict": "pass" | "fail",
  "issues": [
    {{
      "type": "hallucination" | "missing" | "mismatch",
      "detail": "mô tả cụ thể",
      "severity": "critical" | "high" | "medium" | "low",
      "location": "đoạn text liên quan",
      "suggested_fix": "gợi ý sửa"
    }}
  ],
  "corrected_text": "TOÀN BỘ bản wiki đã sửa (nếu có issue)" | null,
  "confidence": 0.0-1.0
}}

Nếu pass → issues = [], corrected_text = null.
Nếu fail + sửa được → ghi corrected_text (full wiki)."""


def collect_claims(category: str) -> tuple[list[dict], str]:
    """Collect all approved claims for a category.

    Returns:
        (list of claim dicts, formatted claims text for prompt)
    """
    claims = []

    # Only read from approved dir — never mix unreviewed drafts into compilation
    search_dir = CLAIMS_APPROVED_DIR / "products" / category
    if search_dir.exists():
        for f in sorted(search_dir.glob("*.yaml")):
            claim = read_yaml(f)
            if isinstance(claim, dict):
                claims.append(claim)

    if not claims:
        return [], ""

    # Format claims text for prompt
    formatted = []
    for c in claims:
        formatted.append(
            f"- claim_id: {c.get('claim_id', 'N/A')}\n"
            f"  entity: {c.get('entity_id', '')} ({c.get('entity_name', '')})\n"
            f"  attribute: {c.get('attribute', '')}\n"
            f"  value: {c.get('value', '')}\n"
            f"  unit: {c.get('unit', '')}\n"
            f"  confidence: {c.get('confidence', '')}\n"
            f"  note: {c.get('compiler_note', '')}"
        )

    return claims, "\n".join(formatted)


def compile_category(category: str, force: bool = False) -> dict:
    """Compile claims for a category into a wiki page.

    Args:
        category: Product category (hosting, vps, etc.)
        force: Skip existing draft check

    Returns:
        Result dict
    """
    log_entry("compile-wiki", "start", f"Compiling: {category}")

    # 1. Collect claims
    claims, claims_text = collect_claims(category)

    if not claims:
        msg = f"Không có claims approved cho category: {category}"
        log_entry("compile-wiki", "skip", msg)
        return {"status": "skip", "detail": msg}

    # Title mapping
    title_map = {
        "hosting": "Hosting BKNS — Tổng Quan",
        "vps": "VPS BKNS — Virtual Private Server",
        "ten-mien": "Tên Miền BKNS — Domain Registration",
        "email": "Email Hosting BKNS",
        "ssl": "SSL Certificate BKNS",
        "server": "Máy Chủ BKNS — Dedicated & Co-location",
        "software": "Phần Mềm & Bản Quyền BKNS",
    }
    title = title_map.get(category, f"BKNS — {category.title()}")

    # 2. Compile with Gemini Pro
    prompt = COMPILE_PROMPT.format(
        claims_content=claims_text,
        category=category,
        title=title,
        date=today_str(),
    )

    try:
        result = generate(
            prompt=prompt,
            model=MODEL_PRO,
            skill="compile-wiki",
            temperature=0.2,
            max_output_tokens=8192,
        )
    except Exception as e:
        error_msg = f"Compile error: {str(e)}"
        log_entry("compile-wiki", "error", error_msg, severity="critical")
        notify_error("compile-wiki", error_msg)
        return {"status": "error", "detail": error_msg}

    draft_content = result["text"]
    compile_cost = result.get("cost_usd", 0)

    # 3. Self-Review (MANDATORY)
    review_result = self_review(draft_content, claims_text, category)
    review_cost = review_result.get("cost_usd", 0)

    total_cost = compile_cost + review_cost

    # 4. Process review result
    final_content = draft_content
    corrections = 0

    if review_result.get("verdict") == "fail":
        issues = review_result.get("issues", [])
        critical = [i for i in issues if i.get("severity") == "critical"]

        if critical and SELF_REVIEW_RULES["block_if_hallucination"]:
            # Block if critical hallucination
            msg = f"❌ BLOCKED — {len(critical)} critical hallucination(s) detected"
            log_entry("compile-wiki", "blocked", msg, severity="critical",
                      cost_usd=total_cost)
            notify_error("compile-wiki",
                          f"Compile {category} bị BLOCK do hallucination:\n"
                          + "\n".join(f"• {i['detail']}" for i in critical[:3]))
            return {"status": "blocked", "detail": msg, "cost_usd": total_cost}

        # Auto-correct nếu có corrected_text
        corrected = review_result.get("corrected_text")
        if corrected and SELF_REVIEW_RULES["auto_correct"]:
            final_content = corrected
            corrections = len(issues)
            log_entry("compile-wiki", "auto_corrected",
                      f"Auto-corrected {corrections} issues")

    # 5. Save draft
    ensure_dir(WIKI_DRAFTS_DIR / "products" / category)
    draft_path = WIKI_DRAFTS_DIR / "products" / category / "tong-quan.md"

    frontmatter = {
        "page_id": f"wiki.products.{category}.tong-quan",
        "title": title,
        "category": f"products/{category}",
        "updated": today_str(),
        "review_state": "drafted",
        "sensitivity": "high",
        "compiled_from": [c.get("claim_id", "") for c in claims[:10]],
        "compile_cost_usd": round(total_cost, 4),
        "corrections": corrections,
        "self_review_verdict": review_result.get("verdict", "unknown"),
    }

    write_markdown_with_frontmatter(draft_path, frontmatter, final_content)

    # 6. Notify
    notify_skill("compile-wiki",
                  f"Draft wiki cho *{category}* sẵn sàng review:\n"
                  f"📄 `wiki/.drafts/products/{category}/tong-quan.md`\n"
                  f"• {len(claims)} claims sử dụng\n"
                  f"• Self-review: {review_result.get('verdict', 'unknown')}\n"
                  f"• Corrections: {corrections}\n"
                  f"• Cost: ${total_cost:.4f}\n\n"
                  f"Gõ /duyet {category} để publish.",
                  severity="success")

    log_entry("compile-wiki", "success",
              f"Draft compiled: {category} ({len(claims)} claims, "
              f"review={review_result.get('verdict')}, "
              f"corrections={corrections})",
              cost_usd=total_cost)

    return {
        "status": "success",
        "category": category,
        "claims_used": len(claims),
        "review_verdict": review_result.get("verdict"),
        "corrections": corrections,
        "cost_usd": total_cost,
        "draft_path": str(draft_path),
    }


def self_review(draft: str, claims_text: str, category: str) -> dict:
    """Run self-review: bot reads back draft vs claims.

    Returns:
        dict with verdict, issues, corrected_text, cost_usd
    """
    log_entry("compile-wiki", "self_review_start", f"Reviewing {category}")

    prompt = SELF_REVIEW_PROMPT.format(
        draft_content=draft,
        claims_content=claims_text,
    )

    try:
        result = generate(
            prompt=prompt,
            model=MODEL_PRO,
            skill="compile-wiki",
            system_instruction="Bạn là QA auditor. Trả lời bằng JSON DUY NHẤT.",
            temperature=0.1,
            max_output_tokens=8192,
        )
    except Exception as e:
        log_entry("compile-wiki", "error",
                  f"Self-review API error: {str(e)}", severity="high")
        return {"verdict": "error", "issues": [], "cost_usd": 0}

    # Parse JSON response
    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        review = json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                review = json.loads(match.group(0))
            except json.JSONDecodeError:
                review = {"verdict": "error", "issues": []}
        else:
            review = {"verdict": "error", "issues": []}

    review["cost_usd"] = result.get("cost_usd", 0)

    log_entry("compile-wiki", "self_review_done",
              f"Verdict: {review.get('verdict')} ({len(review.get('issues', []))} issues)",
              cost_usd=review["cost_usd"])

    return review


def approve_draft(category: str) -> dict:
    """Move draft from wiki/.drafts/ to wiki/ (publish).

    This is the /duyet command handler.
    """
    draft_path = WIKI_DRAFTS_DIR / "products" / category / "tong-quan.md"
    if not draft_path.exists():
        return {"status": "error", "detail": f"No draft for {category}"}

    content = draft_path.read_text(encoding="utf-8")
    from lib.utils import parse_frontmatter
    fm, body = parse_frontmatter(content)

    # Update frontmatter
    fm["review_state"] = "approved"
    fm["approved_at"] = now_iso()

    # Write to wiki/
    target_dir = WIKI_DIR / "products" / category
    ensure_dir(target_dir)
    target_path = target_dir / "tong-quan.md"
    write_markdown_with_frontmatter(target_path, fm, body)

    # Log approval
    from lib.logger import log_approval
    log_approval(str(target_path), "admin")

    notify_skill("compile-wiki",
                  f"✅ Wiki *{category}* đã publish!\n"
                  f"📄 `wiki/products/{category}/tong-quan.md`",
                  severity="success")

    return {"status": "approved", "published": str(target_path)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Compile Wiki")
    parser.add_argument("category", nargs="?", help="Category to compile")
    parser.add_argument("--all", action="store_true", help="Compile all categories")
    parser.add_argument("--approve", help="Approve draft: category name")
    args = parser.parse_args()

    if args.approve:
        result = approve_draft(args.approve)
        print(f"Approve result: {result}")
    elif args.all:
        for cat in ["hosting", "vps", "ten-mien", "email", "ssl", "server", "software"]:
            print(f"\n{'='*40}")
            print(f"Compiling: {cat}")
            result = compile_category(cat)
            print(f"Result: {result['status']}")
    elif args.category:
        result = compile_category(args.category)
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print("Usage: python3 compile.py [category|--all|--approve CATEGORY]")


if __name__ == "__main__":
    main()
