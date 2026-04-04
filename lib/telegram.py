"""
BKNS Agent Wiki — Telegram Notifier
Send alerts, reports, and notifications to admin.
"""
import requests
from lib.config import TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID


# Emoji map per severity
EMOJI_MAP = {
    "critical": "❌",
    "high": "⚠️",
    "medium": "🟡",
    "low": "ℹ️",
    "info": "📋",
    "success": "✅",
    "report": "📊",
    "image": "📷",
    "build": "🔨",
}


def send_message(
    text: str,
    chat_id: str = None,
    parse_mode: str = "Markdown",
    silent: bool = False,
) -> bool:
    """Send a message via Telegram bot.

    Args:
        text: Message text (supports Markdown)
        chat_id: Target chat ID (defaults to admin)
        parse_mode: 'Markdown' or 'HTML'
        silent: If True, send without notification sound

    Returns:
        True if sent successfully, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN:
        print(f"[WARN] Telegram bot token not set. Message: {text[:100]}")
        return False

    chat_id = chat_id or ADMIN_TELEGRAM_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": silent,
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")
        return False


def notify_skill(
    skill: str,
    message: str,
    severity: str = "info",
    chat_id: str = None,
) -> bool:
    """Send a skill notification with standard format.

    Format: {emoji} {skill}: {message}
    """
    emoji = EMOJI_MAP.get(severity, "📋")
    text = f"{emoji} *{skill}*: {message}"

    # Truncate to 300 chars for alerts
    if len(text) > 300:
        text = text[:297] + "..."

    return send_message(text, chat_id=chat_id)


def notify_error(
    skill: str,
    detail: str,
    log_path: str = "",
    chat_id: str = None,
) -> bool:
    """Send an error notification."""
    text = f"❌ *{skill}*: {detail}"
    if log_path:
        text += f"\n📁 Xem log: `{log_path}`"
    return send_message(text, chat_id=chat_id)


def notify_success(
    skill: str,
    detail: str,
    chat_id: str = None,
) -> bool:
    """Send a success notification."""
    return notify_skill(skill, detail, severity="success", chat_id=chat_id)


def send_report(
    title: str,
    content: str,
    chat_id: str = None,
) -> bool:
    """Send a longer report (can exceed 300 chars)."""
    text = f"📊 *{title}*\n━━━━━━━━━━━━━━━━━━━━\n{content}"

    # Telegram max: 4096 chars
    if len(text) > 4000:
        text = text[:3997] + "..."

    return send_message(text, chat_id=chat_id)


def send_conflict_alert(
    entity_id: str,
    attribute: str,
    old_value: str,
    new_value: str,
    chat_id: str = None,
) -> bool:
    """Send a conflict detection alert."""
    text = (
        f"⚠️ *Conflict Detected*\n"
        f"Entity: `{entity_id}`\n"
        f"Attribute: `{attribute}`\n"
        f"Wiki: `{old_value}`\n"
        f"Mới: `{new_value}`\n\n"
        f"Cần admin review để resolve."
    )
    return send_message(text, chat_id=chat_id)
