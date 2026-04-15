"""Tests for bot/wiki_bot.py — _validate_url, _safe_error, handle_them."""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# Import helpers under test — no Telegram token needed for unit tests.
# bot/wiki_bot.py imports lib.config which loads .env; that's fine.
from bot.wiki_bot import _validate_url, _safe_error, handle_them, ADMIN_TELEGRAM_ID


# ── _validate_url ──────────────────────────────────────────

class TestValidateUrl:
    def test_https_url_is_valid(self):
        valid, err = _validate_url("https://bkns.vn/hosting")
        assert valid is True
        assert err == ""

    def test_http_url_is_valid(self):
        valid, err = _validate_url("http://bkns.vn/hosting")
        assert valid is True
        assert err == ""

    def test_no_scheme_is_invalid(self):
        valid, err = _validate_url("bkns.vn/hosting")
        assert valid is False
        assert err != ""

    def test_ftp_scheme_is_invalid(self):
        valid, err = _validate_url("ftp://bkns.vn/file.txt")
        assert valid is False
        assert err != ""

    def test_empty_string_is_invalid(self):
        valid, err = _validate_url("")
        assert valid is False

    def test_url_truncated_at_2000_chars(self):
        long_url = "https://bkns.vn/" + "a" * 3000
        valid, err = _validate_url(long_url)
        # Starts with https:// → valid (truncation happens internally)
        assert valid is True

    def test_whitespace_stripped(self):
        valid, err = _validate_url("  https://bkns.vn/  ")
        assert valid is True


# ── _safe_error ────────────────────────────────────────────

class TestSafeError:
    def test_masks_file_paths(self):
        err = Exception("Error in /home/openclaw/wiki/lib/gemini.py line 42")
        result = _safe_error(err)
        assert "/home/openclaw/wiki/lib/gemini.py" not in result
        assert "[internal]" in result

    def test_truncates_at_200_chars(self):
        err = Exception("x" * 500)
        result = _safe_error(err)
        assert len(result) <= 200

    def test_normal_message_unchanged(self):
        err = Exception("Connection refused")
        result = _safe_error(err)
        assert "Connection refused" in result


# ── handle_them ────────────────────────────────────────────

class TestHandleThem:
    """Tests for the /them command handler."""

    def _admin_id(self):
        """Return a numeric admin ID (use ADMIN_TELEGRAM_ID or a fallback)."""
        return int(ADMIN_TELEGRAM_ID) if ADMIN_TELEGRAM_ID else 999999

    def test_non_admin_is_rejected(self):
        non_admin_id = 12345
        # Ensure non_admin_id != admin
        assert str(non_admin_id) != str(ADMIN_TELEGRAM_ID)

        with patch("bot.wiki_bot.send_message") as mock_send:
            handle_them(non_admin_id, "https://bkns.vn/hosting")
            msg = mock_send.call_args[0][1]
            assert "admin" in msg.lower() or "⛔" in msg

    def test_empty_url_triggers_usage_hint(self):
        admin_id = self._admin_id()
        with patch("bot.wiki_bot.ADMIN_TELEGRAM_ID", str(admin_id)), \
             patch("bot.wiki_bot.send_message") as mock_send:
            handle_them(admin_id, "")
            msg = mock_send.call_args[0][1]
            assert "/them" in msg

    def test_invalid_url_scheme_rejected(self):
        admin_id = self._admin_id()
        with patch("bot.wiki_bot.ADMIN_TELEGRAM_ID", str(admin_id)), \
             patch("bot.wiki_bot.send_message") as mock_send:
            handle_them(admin_id, "ftp://bad.com/file")
            msg = mock_send.call_args[0][1]
            assert "http" in msg.lower() or "❌" in msg

    def test_valid_url_invokes_crawl_subprocess(self):
        admin_id = self._admin_id()
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""

        with patch("bot.wiki_bot.ADMIN_TELEGRAM_ID", str(admin_id)), \
             patch("bot.wiki_bot.send_message"), \
             patch("bot.wiki_bot.send_typing"), \
             patch("bot.wiki_bot.subprocess.run", return_value=mock_proc) as mock_run:
            handle_them(admin_id, "https://bkns.vn/hosting")
            assert mock_run.called
            # URL should appear in the subprocess args
            cmd_args = mock_run.call_args[0][0]
            assert "https://bkns.vn/hosting" in cmd_args

    def test_crawl_success_sends_success_message(self):
        admin_id = self._admin_id()
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""

        with patch("bot.wiki_bot.ADMIN_TELEGRAM_ID", str(admin_id)), \
             patch("bot.wiki_bot.send_message") as mock_send, \
             patch("bot.wiki_bot.send_typing"), \
             patch("bot.wiki_bot.subprocess.run", return_value=mock_proc):
            handle_them(admin_id, "https://bkns.vn/hosting")
            # Last message should mention success
            last_msg = mock_send.call_args_list[-1][0][1]
            assert "✅" in last_msg or "thành công" in last_msg.lower()

    def test_crawl_timeout_sends_timeout_message(self):
        import subprocess
        admin_id = self._admin_id()

        with patch("bot.wiki_bot.ADMIN_TELEGRAM_ID", str(admin_id)), \
             patch("bot.wiki_bot.send_message") as mock_send, \
             patch("bot.wiki_bot.send_typing"), \
             patch("bot.wiki_bot.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("crawl.py", 60)):
            handle_them(admin_id, "https://bkns.vn/hosting")
            last_msg = mock_send.call_args_list[-1][0][1]
            assert "timeout" in last_msg.lower() or "⏰" in last_msg
