#!/usr/bin/env python3
"""
BKNS Wiki — Telegram Bot Handler
Polling loop để nhận commands từ Telegram.

Commands:
    /hoi [câu hỏi]     — Hỏi wiki
    /them [URL]         — Crawl URL mới
    /extract            — Extract claims từ raw files
    /compile [category] — Compile wiki cho category
    /build              — Tạo build snapshot mới
    /lint               — Chạy lint wiki
    /status             — Xem trạng thái hệ thống

Usage:
    python3 bot/wiki_bot.py              # Run once
    python3 bot/wiki_bot.py --daemon     # Daemon mode (loop)
"""
import sys
import json
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import TELEGRAM_BOT_TOKEN as TELEGRAM_TOKEN, ADMIN_TELEGRAM_ID, WORKSPACE
from lib.logger import log_entry


API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OFFSET_FILE = WORKSPACE / "bot" / ".last_offset"


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
    """Send reply to Telegram."""
    # Split long messages
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": parse_mode,
            }, timeout=10)
        except Exception as e:
            log_entry("wiki-bot", "error", f"sendMessage failed: {e}")


def send_typing(chat_id: int):
    """Send typing indicator."""
    try:
        requests.post(f"{API_URL}/sendChatAction", json={
            "chat_id": chat_id,
            "action": "typing",
        }, timeout=5)
    except Exception:
        pass


def handle_hoi(chat_id: int, question: str):
    """Handle /hoi query."""
    if not question:
        send_message(chat_id, "❓ Cú pháp: `/hoi [câu hỏi]`\nVí dụ: `/hoi Giá hosting rẻ nhất BKNS?`")
        return

    send_typing(chat_id)

    try:
        sys.path.insert(0, str(WORKSPACE / "skills" / "query-wiki" / "scripts"))
        from query import query
        result = query(question)

        answer = result["answer"]
        cost = result["cost_usd"]
        cache = result["cache_hit_rate"]

        reply = f"{answer}\n\n_💰 Cost: ${cost:.5f} | Cache: {cache}%_"
        send_message(chat_id, reply)
    except Exception as e:
        send_message(chat_id, f"❌ Lỗi query: {str(e)}")
        log_entry("wiki-bot", "error", f"Query error: {e}", severity="high")


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
        sys.path.insert(0, str(WORKSPACE / "skills" / "build-snapshot" / "scripts"))
        from snapshot import create_snapshot
        result = create_snapshot()
        send_message(chat_id,
                      f"🔨 *Build thành công!*\n\n"
                      f"ID: `{result['build_id']}`\n"
                      f"Version: `{result['version']}`\n"
                      f"Files: {result['wiki_files']}\n"
                      f"Tokens: ~{result['token_estimate']:,}")
    except Exception as e:
        send_message(chat_id, f"❌ Build failed: {str(e)}")


def handle_lint(chat_id: int):
    """Handle /lint command."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Admin only.")
        return

    send_typing(chat_id)
    try:
        sys.path.insert(0, str(WORKSPACE / "skills" / "lint-wiki" / "scripts"))
        from lint import lint_all
        report = lint_all(semantic=False)
        syntax_issues = report.get("syntax_issues", 0)
        send_message(chat_id,
                      f"🔍 *Lint Report*\n\n"
                      f"Syntax issues: {syntax_issues}\n"
                      f"Cost: $0.0000 (syntax only)")
    except Exception as e:
        send_message(chat_id, f"❌ Lint failed: {str(e)}")


def handle_help(chat_id: int):
    """Send help message."""
    help_text = (
        "📚 *BKNS Wiki Bot — Trợ lý thông tin sản phẩm*\n\n"
        "*Lệnh có sẵn:*\n"
        "`/hoi [câu hỏi]` — Hỏi về sản phẩm BKNS\n"
        "`/status` — Xem trạng thái wiki\n"
        "`/build` — Tạo build mới (admin)\n"
        "`/lint` — Kiểm tra chất lượng wiki (admin)\n"
        "`/help` — Xem hướng dẫn\n\n"
        "*Ví dụ:*\n"
        "• `/hoi Giá hosting rẻ nhất?`\n"
        "• `/hoi Tên miền .com giá bao nhiêu?`\n"
        "• `/hoi So sánh VPS AMD và VPS SSD`\n\n"
        "_Gõ câu hỏi trực tiếp (không /hoi) cũng được!_"
    )
    send_message(chat_id, help_text)


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
    elif text.startswith("/status"):
        handle_status(chat_id)
    elif text.startswith("/build"):
        handle_build(chat_id)
    elif text.startswith("/lint"):
        handle_lint(chat_id)
    elif text.startswith("/help") or text.startswith("/start"):
        handle_help(chat_id)
    elif not text.startswith("/"):
        # Treat as question (auto /hoi)
        handle_hoi(chat_id, text)
    else:
        send_message(chat_id, f"❓ Lệnh không nhận diện: `{text}`\nGõ /help để xem hướng dẫn.")


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
