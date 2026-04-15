#!/usr/bin/env python3
"""
BKNS Wiki — Telegram Bot Handler
Polling loop để nhận commands từ Telegram.

Commands:
    /hoi [câu hỏi]     — Hỏi wiki
    /them [URL]         — Crawl URL mới (admin)
    /extract            — Extract claims từ raw files (admin)
    /compile [category] — Compile wiki cho category (admin)
    /build              — Tạo build snapshot mới (admin)
    /lint               — Chạy lint wiki (admin)
    /status             — Xem trạng thái hệ thống

Usage:
    python3 bot/wiki_bot.py              # Run once
    python3 bot/wiki_bot.py --daemon     # Daemon mode (loop)
"""
import sys
import json
import time
import re
import importlib.util
import subprocess
import os
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import TELEGRAM_BOT_TOKEN as TELEGRAM_TOKEN, ADMIN_TELEGRAM_ID, WORKSPACE
from lib.logger import log_entry


API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OFFSET_FILE = WORKSPACE / "bot" / ".last_offset"

# Allowlist for /compile category
VALID_CATEGORIES = {"hosting", "vps", "email", "ssl", "ten-mien", "server", "software"}


# ── Helpers ────────────────────────────────────────────────


def _load_skill(script_path: Path, module_name: str):
    """Load a skill module from file path without polluting sys.path."""
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _safe_error(e: Exception) -> str:
    """Return user-safe error message, masking internal file paths."""
    msg = str(e)
    msg = re.sub(r"(/[\w./-]+\.py)", "[internal]", msg)
    return msg[:200]


def _validate_url(url: str) -> tuple:
    """Validate URL. Returns (is_valid: bool, error_msg: str)."""
    url = url.strip()[:2000]
    if not url.startswith(("http://", "https://")):
        return False, "❌ URL không hợp lệ. Phải bắt đầu bằng `http://` hoặc `https://`"
    return True, ""


def _validate_category(cat: str) -> bool:
    """Check category is in the known allowlist."""
    return cat in VALID_CATEGORIES or cat == "--all"


# ── Telegram API ───────────────────────────────────────────


def get_updates(offset: int = None) -> list:
    """Get new Telegram updates."""
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        data = r.json()
        return data.get("result", [])
    except Exception as e:
        log_entry("wiki-bot", "error", f"getUpdates failed: {e}")
        return []


def send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Send reply to Telegram with retry on network errors."""
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        for attempt in range(3):
            try:
                r = requests.post(
                    f"{API_URL}/sendMessage",
                    json={"chat_id": chat_id, "text": chunk, "parse_mode": parse_mode},
                    timeout=10,
                )
                if r.status_code == 200:
                    break
                # Non-network error (e.g. 400 bad request) — don't retry
                log_entry("wiki-bot", "error", f"sendMessage HTTP {r.status_code}: {r.text[:200]}")
                break
            except requests.RequestException as e:
                log_entry("wiki-bot", "error", f"sendMessage attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))


def send_typing(chat_id: int):
    """Send typing indicator."""
    try:
        requests.post(f"{API_URL}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing",
        }, timeout=5)
    except Exception:
        pass


# ── Command Handlers ───────────────────────────────────────


def handle_hoi(chat_id: int, question: str):
    """Handle /hoi query."""
    if not question:
        send_message(chat_id, "❓ Cú pháp: `/hoi [câu hỏi]`\nVí dụ: `/hoi Giá hosting rẻ nhất BKNS?`")
        return

    # Sanitize: strip whitespace, limit length
    question = question.strip()[:500]

    send_typing(chat_id)

    try:
        skill = _load_skill(
            WORKSPACE / "skills" / "query-wiki" / "scripts" / "query.py",
            "query_wiki",
        )
        result = skill.query(question)

        answer = result["answer"]
        cost = result["cost_usd"]
        cache = result["cache_hit_rate"]

        reply = f"{answer}\n\n_💰 Cost: ${cost:.5f} | Cache: {cache}%_"
        send_message(chat_id, reply)
    except Exception as e:
        log_entry("wiki-bot", "error", f"Query error: {e}", severity="high")
        send_message(chat_id, f"❌ Lỗi khi truy vấn wiki: {_safe_error(e)}")


def handle_status(chat_id: int):
    """Handle /status command."""
    from lib.config import ACTIVE_BUILD, WIKI_DIR, CLAIMS_APPROVED_DIR
    from lib.utils import read_yaml

    build = read_yaml(ACTIVE_BUILD)
    wiki_files = len(list(WIKI_DIR.rglob("*.md")))
    claims = len(list(CLAIMS_APPROVED_DIR.rglob("*.yaml"))) if CLAIMS_APPROVED_DIR.exists() else 0

    status_text = (
        f"📊 *BKNS Wiki Status*\n\n"
        f"Build: `{build.get('build_id', 'N/A')}`\n"
        f"Version: `{build.get('version', 'N/A')}`\n"
        f"Wiki files: {wiki_files}\n"
        f"Tokens: ~{build.get('wiki_token_estimate', 0):,}\n"
        f"Approved claims: {claims}\n"
        f"Status: {build.get('status', 'N/A')}\n"
        f"Last build: {build.get('build_date', 'N/A')}"
    )
    send_message(chat_id, status_text)


def handle_build(chat_id: int):
    """Handle /build command."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Chỉ admin mới được sử dụng lệnh này.")
        return

    send_typing(chat_id)
    try:
        skill = _load_skill(
            WORKSPACE / "skills" / "build-snapshot" / "scripts" / "snapshot.py",
            "build_snapshot",
        )
        result = skill.create_snapshot()
        send_message(chat_id,
                      f"🔨 *Build thành công!*\n\n"
                      f"ID: `{result['build_id']}`\n"
                      f"Version: `{result['version']}`\n"
                      f"Files: {result['wiki_files']}\n"
                      f"Tokens: ~{result['token_estimate']:,}")
    except Exception as e:
        log_entry("wiki-bot", "error", f"Build error: {e}", severity="high")
        send_message(chat_id, f"❌ Build thất bại: {_safe_error(e)}")


def handle_extract(chat_id: int):
    """Handle /extract command — extract claims from all pending raw files."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Chỉ admin mới được sử dụng lệnh này.")
        return

    send_typing(chat_id)
    send_message(chat_id, "⏳ Đang extract claims từ raw files...")
    try:
        skill = _load_skill(
            WORKSPACE / "skills" / "extract-claims" / "scripts" / "extract.py",
            "extract_claims",
        )
        results = skill.extract_all_pending()
        total_claims = sum(r.get("claims_count", 0) for r in results)
        total_cost = sum(r.get("cost_usd", 0) for r in results)
        total_conflicts = sum(r.get("conflicts", 0) for r in results)
        cached = sum(1 for r in results if r.get("cached"))
        send_message(
            chat_id,
            f"✅ *Extract hoàn tất!*\n\n"
            f"Files xử lý: {len(results)}\n"
            f"Cache hits: {cached}\n"
            f"Total claims: {total_claims}\n"
            f"Conflicts: {total_conflicts}\n"
            f"Cost: ${total_cost:.4f}",
        )
    except Exception as e:
        log_entry("wiki-bot", "error", f"Extract error: {e}", severity="high")
        send_message(chat_id, f"❌ Extract thất bại: {_safe_error(e)}")


def handle_compile(chat_id: int, category: str):
    """Handle /compile [category] command."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Chỉ admin mới được sử dụng lệnh này.")
        return

    if not category:
        send_message(
            chat_id,
            "❓ Cú pháp: `/compile [category]`\n"
            "Categories: hosting, vps, email, ssl, ten-mien, server, software\n"
            "Hoặc: `/compile --all` để compile tất cả",
        )
        return

    # Sanitize category input
    category = category.strip().lower()[:50]
    if not _validate_category(category):
        send_message(
            chat_id,
            f"❌ Category không hợp lệ: `{category}`\n"
            f"Categories hợp lệ: {', '.join(sorted(VALID_CATEGORIES))}, --all",
        )
        return

    send_typing(chat_id)
    send_message(chat_id, f"⏳ Đang compile wiki cho *{category}*...")
    try:
        skill = _load_skill(
            WORKSPACE / "skills" / "compile-wiki" / "scripts" / "compile.py",
            "compile_wiki",
        )

        if category == "--all":
            total_cost = 0.0
            total_pages = 0
            errors = []
            for cat in skill.SUBPAGE_DEFS.keys():
                result = skill.compile_category(cat)
                if result["status"] == "success":
                    total_pages += result.get("pages_compiled", 0)
                    total_cost += result.get("cost_usd", 0)
                elif result["status"] not in ("skip",):
                    errors.append(cat)
            reply = (
                f"✅ *Compile ALL hoàn tất!*\n\n"
                f"Total pages: {total_pages}\n"
                f"Cost: ${total_cost:.4f}"
            )
            if errors:
                reply += f"\n⚠️ Errors: {', '.join(errors)}"
        else:
            result = skill.compile_category(category)
            if result["status"] == "success":
                reply = (
                    f"✅ *Compile {category} hoàn tất!*\n\n"
                    f"Pages: {result['pages_compiled']}\n"
                    f"Skeletons: {result.get('pages_skipped', 0)}\n"
                    f"Claims: {result['total_claims']}\n"
                    f"Cost: ${result['cost_usd']:.4f}"
                )
            else:
                reply = f"⚠️ {result.get('detail', result['status'])}"

        send_message(chat_id, reply)
    except Exception as e:
        log_entry("wiki-bot", "error", f"Compile error: {e}", severity="high")
        send_message(chat_id, f"❌ Compile thất bại: {_safe_error(e)}")


def handle_lint(chat_id: int):
    """Handle /lint command."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Admin only.")
        return

    send_typing(chat_id)
    try:
        skill = _load_skill(
            WORKSPACE / "skills" / "lint-wiki" / "scripts" / "lint.py",
            "lint_wiki",
        )
        report = skill.lint_all(semantic=False)
        syntax_issues = report.get("syntax_issues", 0)
        send_message(chat_id,
                      f"🔍 *Lint Report*\n\n"
                      f"Syntax issues: {syntax_issues}\n"
                      f"Cost: $0.0000 (syntax only)")
    except Exception as e:
        log_entry("wiki-bot", "error", f"Lint error: {e}", severity="high")
        send_message(chat_id, f"❌ Lint thất bại: {_safe_error(e)}")


def handle_them(chat_id: int, url: str):
    """Handle /them [URL] — crawl URL mới vào raw/ (admin only)."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Chỉ admin mới được sử dụng lệnh này.")
        return

    if not url:
        send_message(chat_id, "❓ Cú pháp: `/them [URL]`\nVí dụ: `/them https://bkns.vn/hosting`")
        return

    is_valid, error_msg = _validate_url(url)
    if not is_valid:
        send_message(chat_id, error_msg)
        return

    # Normalize URL after validation
    url = url.strip()[:2000]

    send_typing(chat_id)
    send_message(chat_id, f"⏳ Đang crawl: `{url}`")
    try:
        result = subprocess.run(
            [sys.executable, str(WORKSPACE / "skills" / "crawl-source" / "scripts" / "crawl.py"), url],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "PYTHONPATH": str(WORKSPACE)},
        )
        if result.returncode == 0:
            send_message(chat_id, f"✅ Crawl thành công!\n\nChạy `/extract` để xử lý file mới.")
        else:
            stderr_preview = result.stderr[:500] if result.stderr else "Không có output"
            send_message(chat_id, f"⚠️ Crawl gặp vấn đề:\n`{stderr_preview}`")
            log_entry("wiki-bot", "error", f"Crawl failed for {url}: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        send_message(chat_id, "⏰ Crawl timeout (60s). URL có thể quá lớn — vui lòng thử lại sau.")
    except Exception as e:
        log_entry("wiki-bot", "error", f"Crawl error for {url}: {e}", severity="high")
        send_message(chat_id, f"❌ Lỗi crawl: {_safe_error(e)}")


def handle_help(chat_id: int):
    """Send help message."""
    help_text = (
        "📚 *BKNS Wiki Bot — Trợ lý thông tin sản phẩm*\n\n"
        "*Lệnh công khai:*\n"
        "`/hoi [câu hỏi]` — Hỏi về sản phẩm BKNS\n"
        "`/status` — Xem trạng thái wiki\n"
        "`/help` — Xem hướng dẫn\n\n"
        "*Lệnh admin:*\n"
        "`/them [URL]` — Crawl URL mới vào raw/\n"
        "`/extract` — Extract claims từ raw files mới\n"
        "`/compile [category]` — Compile wiki (hoặc `--all`)\n"
        "`/build` — Tạo build snapshot mới\n"
        "`/lint` — Kiểm tra chất lượng wiki\n\n"
        "*Ví dụ:*\n"
        "• `/hoi Giá hosting rẻ nhất?`\n"
        "• `/hoi Tên miền .com giá bao nhiêu?`\n"
        "• `/them https://bkns.vn/hosting`\n"
        "• `/compile hosting`\n\n"
        "_Gõ câu hỏi trực tiếp (không /hoi) cũng được!_"
    )
    send_message(chat_id, help_text)


# ── Message Router ─────────────────────────────────────────


def process_message(message: dict):
    """Process a single Telegram message."""
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    username = message.get("from", {}).get("username", "unknown")

    if not text:
        return

    log_entry("wiki-bot", "message",
              f"From {username} ({chat_id}): {text[:100]}")

    # Route commands
    if text.startswith("/hoi"):
        question = text[4:].strip()
        handle_hoi(chat_id, question)
    elif text.startswith("/them"):
        url = text[5:].strip()
        handle_them(chat_id, url)
    elif text.startswith("/status"):
        handle_status(chat_id)
    elif text.startswith("/build"):
        handle_build(chat_id)
    elif text.startswith("/lint"):
        handle_lint(chat_id)
    elif text.startswith("/extract"):
        handle_extract(chat_id)
    elif text.startswith("/compile"):
        category = text[8:].strip()
        handle_compile(chat_id, category)
    elif text.startswith("/help") or text.startswith("/start"):
        handle_help(chat_id)
    elif not text.startswith("/"):
        # Treat as question (auto /hoi)
        handle_hoi(chat_id, text)
    else:
        send_message(chat_id, f"❓ Lệnh không nhận diện: `{text}`\nGõ /help để xem hướng dẫn.")


# ── Offset Management ──────────────────────────────────────


def load_offset() -> int:
    """Load last processed update offset."""
    try:
        return int(OFFSET_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_offset(offset: int):
    """Save last processed update offset."""
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(offset))


# ── Run Modes ──────────────────────────────────────────────


def run_once():
    """Process pending updates once."""
    offset = load_offset()
    updates = get_updates(offset)

    if not updates:
        print("No new messages.")
        return

    for update in updates:
        msg = update.get("message")
        if msg:
            process_message(msg)
        offset = update["update_id"] + 1

    save_offset(offset)
    print(f"Processed {len(updates)} update(s)")


def run_daemon():
    """Run in daemon mode (long polling loop)."""
    print("🤖 BKNS Wiki Bot started (daemon mode)")
    print("Press Ctrl+C to stop\n")

    offset = load_offset()

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                msg = update.get("message")
                if msg:
                    process_message(msg)
                offset = update["update_id"] + 1
                save_offset(offset)

        except KeyboardInterrupt:
            print("\n👋 Bot stopped.")
            break
        except Exception as e:
            log_entry("wiki-bot", "error", f"Daemon error: {e}")
            time.sleep(5)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Wiki Telegram Bot")
    parser.add_argument("--daemon", "-d", action="store_true",
                        help="Run in daemon mode")
    args = parser.parse_args()

    if args.daemon:
        run_daemon()
    else:
        run_once()


if __name__ == "__main__":
    main()
