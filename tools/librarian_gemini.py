#!/usr/bin/env python3
"""
Librarian Gemini Bridge
─────────────────────────────────────────────────────────────
Thin CLI wrapper around lib.gemini.generate() so the Node web
server can call Gemini Pro for chat + classification without
re-implementing Vertex AI auth in JS.

Modes:
  --mode chat      → conversational reply (Gemini Pro)
  --mode classify  → strict-JSON classification (Gemini Pro)

Input: JSON on stdin
Output: JSON on stdout (single line, no markdown fences)

Always strips markdown fences from Gemini output (LESSONS #BUG-003).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# Ensure project root on path (script lives in tools/)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from lib.gemini import generate
from lib.config import MODEL_PRO


CATEGORIES = [
    "email", "hosting", "other", "server", "software",
    "ssl", "ten-mien", "uncategorized", "vps",
]

DOC_TYPES = ["wiki-page", "claim", "raw-doc", "note", "asset"]


SYSTEM_CHAT = """Bạn là **AI Thủ thư** (Librarian) cho hệ thống wiki nội bộ BKNS.

Vai trò:
- Trò chuyện thân thiện bằng tiếng Việt với quản trị viên
- Nhận file/ghi chú/yêu cầu, xác nhận đã staging vào inbox
- Đề xuất phân loại (category, type) trước khi lưu
- Trả lời ngắn gọn, rõ ràng (≤ 4 câu khi không cần dài)
- Khi user nói "xử lý ngay", "process now" → nhắc họ bấm nút Process Now

Categories khả dụng: email, hosting, other, server, software, ssl, ten-mien, uncategorized, vps
Types: wiki-page (markdown), claim (yaml fact), raw-doc (pdf/docx), note (text), asset (image)

KHÔNG bịa thông tin sản phẩm. KHÔNG hứa xử lý gì ngoài staging."""


SYSTEM_CLASSIFY = f"""Bạn là bộ phân loại tài liệu cho wiki BKNS.

Trả về CHỈ MỘT object JSON hợp lệ, không markdown, không giải thích:
{{
  "category": "<one of: {', '.join(CATEGORIES)}>",
  "type": "<one of: {', '.join(DOC_TYPES)}>",
  "suggested_path": "<relative path under wiki/, vd: wiki/products/email/foo.md>",
  "summary": "<≤ 30 từ tiếng Việt mô tả nội dung>",
  "confidence": <float 0.0-1.0>,
  "tags": ["<keyword1>", "<keyword2>"]
}}

Quy tắc:
- File .md → type=wiki-page, path=wiki/products/<category>/<slug>.md
- File .yaml/.yml chứa claim → type=claim, path=claims/staging/<slug>.yaml
- File .pdf/.docx/.txt → type=raw-doc, path=raw/librarian/<YYYY-MM-DD>/<filename>
- Hình ảnh → type=asset, path=wiki/assets/images/<filename>
- Text note ngắn → type=note, path=wiki/products/<category>/_notes/<slug>.md
- Nếu không chắc category → "uncategorized" và confidence ≤ 0.5"""


_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```\s*$", re.MULTILINE)


def strip_fence(text: str) -> str:
    """Remove ```json ... ``` fences (LESSONS #BUG-003)."""
    if not text:
        return text
    cleaned = _FENCE_RE.sub("", text.strip())
    return cleaned.strip()


def chat(payload: dict) -> dict:
    """Conversational reply using full session history."""
    history = payload.get("history", [])  # [{role, content}, ...]
    user_msg = payload.get("message", "").strip()
    if not user_msg:
        return {"ok": False, "error": "empty message"}

    # Build prompt: history flattened + current message
    convo = []
    for turn in history[-10:]:  # last 10 turns max
        role = "Người dùng" if turn.get("role") == "user" else "Thủ thư"
        convo.append(f"{role}: {turn.get('content', '')}")
    convo.append(f"Người dùng: {user_msg}")
    convo.append("Thủ thư:")
    prompt = "\n\n".join(convo)

    result = generate(
        prompt=prompt,
        model=MODEL_PRO,
        skill="librarian-chat",
        system_instruction=SYSTEM_CHAT,
        temperature=0.6,
        max_output_tokens=4096,  # gemini-2.5-pro consumes thinking tokens too
    )
    return {
        "ok": True,
        "reply": (result["text"] or "").strip(),
        "model": result["model"],
        "tokens_in": result["input_tokens"],
        "tokens_out": result["output_tokens"],
        "cost_usd": result["cost_usd"],
    }


def classify(payload: dict) -> dict:
    """Strict-JSON classify of an item."""
    name = payload.get("name", "")
    ext = payload.get("ext", "")
    excerpt = payload.get("excerpt", "")[:4000]  # cap
    user_hint = payload.get("user_hint", "")

    prompt_parts = [
        f"Tên file: {name}",
        f"Phần mở rộng: {ext}",
    ]
    if user_hint:
        prompt_parts.append(f"Gợi ý từ user: {user_hint}")
    if excerpt:
        prompt_parts.append(f"Trích nội dung:\n---\n{excerpt}\n---")

    prompt = "\n".join(prompt_parts)

    result = generate(
        prompt=prompt,
        model=MODEL_PRO,
        skill="librarian-classify",
        system_instruction=SYSTEM_CLASSIFY,
        temperature=0.1,
        max_output_tokens=2048,  # thinking tokens included
    )

    raw = strip_fence(result["text"] or "")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return {
            "ok": False,
            "error": f"invalid JSON: {e}",
            "raw": raw[:500],
        }

    # Validate enums; fall back to safe defaults
    if parsed.get("category") not in CATEGORIES:
        parsed["category"] = "uncategorized"
        parsed["confidence"] = min(parsed.get("confidence", 0.5), 0.5)
    if parsed.get("type") not in DOC_TYPES:
        parsed["type"] = "note"

    return {
        "ok": True,
        "classification": parsed,
        "model": result["model"],
        "cost_usd": result["cost_usd"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["chat", "classify"], required=True)
    args = ap.parse_args()

    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"bad stdin JSON: {e}"}))
        sys.exit(2)

    try:
        if args.mode == "chat":
            out = chat(payload)
        else:
            out = classify(payload)
    except Exception as e:
        out = {"ok": False, "error": str(e), "type": type(e).__name__}

    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
