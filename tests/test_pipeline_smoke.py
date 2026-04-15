"""Smoke test: full pipeline extract → compile → query (mock LLM calls)."""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Helpers ────────────────────────────────────────────────

def _make_generate_result(text="test output"):
    """Build a minimal dict that mirrors lib.gemini.generate() return value."""
    return {
        "text": text,
        "input_tokens": 100,
        "cached_tokens": 0,
        "output_tokens": 50,
        "cost_usd": 0.0001,
        "model": "gemini-2.5-flash",
        "elapsed_ms": 200,
    }


# ── 4.4.1 — extract_all_pending returns list ──────────────

def test_extract_claims_returns_list():
    """extract_all_pending() returns a list (empty when no pending files)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "extract_claims",
        Path(__file__).resolve().parent.parent
        / "skills" / "extract-claims" / "scripts" / "extract.py",
    )
    mod = importlib.util.module_from_spec(spec)

    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"), \
         patch("lib.telegram.send_conflict_alert"):
        spec.loader.exec_module(mod)
        # Patch find_pending_files on the loaded module to return empty list
        with patch.object(mod, "find_pending_files", return_value=[]):
            result = mod.extract_all_pending()

    assert isinstance(result, list)


# ── 4.4.2 — compile_category returns dict with status key ─

def test_compile_category_returns_success():
    """compile_category() returns dict with 'status' key when claims present."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "compile_wiki",
        Path(__file__).resolve().parent.parent
        / "skills" / "compile-wiki" / "scripts" / "compile.py",
    )
    mod = importlib.util.module_from_spec(spec)

    mock_result = _make_generate_result(text="# Hosting wiki content")

    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"), \
         patch("lib.gemini.generate", return_value=mock_result):
        spec.loader.exec_module(mod)
        # No approved claims exist → status should be 'skip' or 'success'
        result = mod.compile_category("hosting")

    assert isinstance(result, dict)
    assert "status" in result


# ── 4.4.3 — query() returns dict with 'answer' key ────────

def test_query_returns_answer():
    """query() with mock LLM returns dict with key 'answer'."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "query_wiki",
        Path(__file__).resolve().parent.parent
        / "skills" / "query-wiki" / "scripts" / "query.py",
    )
    mod = importlib.util.module_from_spec(spec)

    mock_result = {
        **_make_generate_result(text="Giá hosting BKNS từ 26.000đ/tháng."),
        "cache_hit_rate": 0.0,
    }

    # Stub yaml read for active-build.yaml (returns minimal dict)
    mock_build_info = {"build_id": "test-build", "version": "0.0.1"}

    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"), \
         patch("lib.gemini.generate_with_cache", return_value=mock_result), \
         patch("lib.utils.read_yaml", return_value=mock_build_info):
        spec.loader.exec_module(mod)
        result = mod.query(
            question="Hosting BKNS giá bao nhiêu?",
            wiki_content="# Hosting\nGiá từ 26.000đ/tháng.",
        )

    assert isinstance(result, dict)
    assert "answer" in result


# ── 4.6 — Smoke tests for ingest-image and auto-file ──────

def test_ingest_image_import_does_not_crash():
    """ingest-image module loads without import errors."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ingest_image",
        Path(__file__).resolve().parent.parent
        / "skills" / "ingest-image" / "scripts" / "ingest.py",
    )
    mod = importlib.util.module_from_spec(spec)
    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"):
        spec.loader.exec_module(mod)
    # Module exposes ingest_image function
    assert callable(mod.ingest_image)


def test_ingest_image_missing_file_returns_error():
    """ingest_image() with nonexistent path returns error dict (no API call)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ingest_image_b",
        Path(__file__).resolve().parent.parent
        / "skills" / "ingest-image" / "scripts" / "ingest.py",
    )
    mod = importlib.util.module_from_spec(spec)
    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"):
        spec.loader.exec_module(mod)

    result = mod.ingest_image("/tmp/nonexistent_test_image_xyz.png")
    assert isinstance(result, dict)
    assert result.get("status") == "error"


def test_auto_file_import_does_not_crash():
    """auto-file module loads without import errors."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "auto_file",
        Path(__file__).resolve().parent.parent
        / "skills" / "auto-file" / "scripts" / "auto_file.py",
    )
    mod = importlib.util.module_from_spec(spec)
    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"), \
         patch("lib.telegram.send_report"):
        spec.loader.exec_module(mod)
    assert callable(mod.scan_faq_candidates)


def test_auto_file_scan_skips_when_insufficient_questions():
    """scan_faq_candidates() returns skip dict when < 3 questions in logs."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "auto_file_b",
        Path(__file__).resolve().parent.parent
        / "skills" / "auto-file" / "scripts" / "auto_file.py",
    )
    mod = importlib.util.module_from_spec(spec)
    with patch("lib.telegram.notify_skill"), \
         patch("lib.telegram.notify_error"), \
         patch("lib.telegram.send_report"):
        spec.loader.exec_module(mod)

    # Patch load_query_logs to return only 1 question (below threshold of 3)
    with patch.object(mod, "load_query_logs", return_value=["Câu hỏi duy nhất"]):
        result = mod.scan_faq_candidates()

    assert isinstance(result, dict)
    assert result.get("status") == "skip"
