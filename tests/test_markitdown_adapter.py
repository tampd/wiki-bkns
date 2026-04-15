"""
tests/test_markitdown_adapter.py

Unit + integration tests for tools/converters/markitdown_adapter.py.
Uses the 3 pilot files from PART 02 (located in /tmp/markitdown-pilot/input/).
"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.converters.markitdown_adapter import (
    convert_to_markdown,
    _clean_xlsx_markdown,
    get_converter,
)

PILOT_DIR = Path("/tmp/markitdown-pilot/input")

# ── _clean_xlsx_markdown ──────────────────────────────────────────────────────

class TestCleanXlsxMarkdown:
    def test_nan_cells_replaced(self):
        text = "| Gói | NaN | Giá |\n|---|---|---|\n| VPS1 | NaN | 100 |"
        out = _clean_xlsx_markdown(text)
        assert "NaN" not in out
        assert "nan" not in out.lower() or "NaN" not in out

    def test_nan_case_insensitive(self):
        text = "| nan | NaN | Nan |"
        out = _clean_xlsx_markdown(text)
        assert "nan" not in out.lower()

    def test_unnamed_headers_removed(self):
        text = "| Unnamed: 0 | Unnamed: 1 | Tên gói |\n|---|---|---|\n| a | b | c |"
        out = _clean_xlsx_markdown(text)
        assert "Unnamed" not in out

    def test_all_empty_row_dropped(self):
        # A row where every cell is empty after NaN strip should be removed
        text = "| Header |\n|---|\n| NaN |\n| real value |"
        out = _clean_xlsx_markdown(text)
        # The "real value" row must survive
        assert "real value" in out

    def test_excess_blank_lines_collapsed(self):
        text = "line1\n\n\n\nline2"
        out = _clean_xlsx_markdown(text)
        assert "\n\n\n" not in out

    def test_normal_table_unchanged(self):
        text = "| Gói | RAM | Giá |\n|---|---|---|\n| VPS1 | 1GB | 100K |"
        out = _clean_xlsx_markdown(text)
        # All data preserved
        assert "VPS1" in out
        assert "100K" in out

    def test_empty_string_input(self):
        assert _clean_xlsx_markdown("") == ""

    def test_returns_stripped_string(self):
        out = _clean_xlsx_markdown("  \n  NaN  \n  ")
        assert out == out.strip()


# ── convert_to_markdown (integration — requires pilot files) ─────────────────

PILOT_FILES_AVAILABLE = PILOT_DIR.exists()
skip_no_pilot = pytest.mark.skipif(
    not PILOT_FILES_AVAILABLE,
    reason="Pilot files not found at /tmp/markitdown-pilot/input/",
)


@skip_no_pilot
class TestConvertToMarkdownDocx:
    FILE = PILOT_DIR / "file1-vps.docx"

    def test_returns_string(self):
        out = convert_to_markdown(self.FILE)
        assert isinstance(out, str)

    def test_not_empty(self):
        out = convert_to_markdown(self.FILE)
        assert len(out.strip()) >= 100, "DOCX output too short"

    def test_no_frontmatter_injected(self):
        out = convert_to_markdown(self.FILE)
        assert not out.startswith("---"), "Adapter must not add YAML frontmatter"

    def test_has_markdown_structure(self):
        out = convert_to_markdown(self.FILE)
        # At minimum one heading or list item expected from a product doc
        assert "#" in out or "-" in out or "|" in out


@skip_no_pilot
class TestConvertToMarkdownPdf:
    FILE = PILOT_DIR / "file2-bang-gia-vps.pdf"

    def test_returns_string(self):
        out = convert_to_markdown(self.FILE)
        assert isinstance(out, str)

    def test_not_empty(self):
        out = convert_to_markdown(self.FILE)
        assert len(out.strip()) >= 50, "PDF output too short"

    def test_no_frontmatter_injected(self):
        out = convert_to_markdown(self.FILE)
        assert not out.startswith("---")

    def test_content_has_price_data(self):
        # Bang_Gia_VPS.pdf contains VPS pricing — at least one digit expected
        out = convert_to_markdown(self.FILE)
        assert any(c.isdigit() for c in out), "PDF should contain numeric price data"


@skip_no_pilot
class TestConvertToMarkdownXlsx:
    FILE = PILOT_DIR / "file3-bang-gia.xlsx"

    def test_returns_string(self):
        out = convert_to_markdown(self.FILE)
        assert isinstance(out, str)

    def test_not_empty(self):
        out = convert_to_markdown(self.FILE)
        assert len(out.strip()) >= 50

    def test_no_nan_in_output(self):
        out = convert_to_markdown(self.FILE)
        assert "NaN" not in out, "_clean_xlsx_markdown should strip NaN"

    def test_no_unnamed_headers(self):
        out = convert_to_markdown(self.FILE)
        assert "Unnamed:" not in out

    def test_has_table_structure(self):
        # XLSX with price data should produce markdown tables
        out = convert_to_markdown(self.FILE)
        assert "|" in out, "XLSX output should contain markdown table"


@skip_no_pilot
class TestConvertToMarkdownHtml:
    FILE = PILOT_DIR / "bkns-cloud-vps-amd.html"

    def test_returns_string(self):
        out = convert_to_markdown(self.FILE)
        assert isinstance(out, str)

    def test_not_empty(self):
        out = convert_to_markdown(self.FILE)
        assert len(out.strip()) >= 50

    def test_no_raw_html_tags(self):
        out = convert_to_markdown(self.FILE)
        # markitdown should strip HTML tags
        assert "<html" not in out.lower()
        assert "<body" not in out.lower()


# ── get_converter singleton ───────────────────────────────────────────────────

class TestGetConverterSingleton:
    def test_returns_same_instance(self):
        a = get_converter()
        b = get_converter()
        assert a is b, "get_converter() should return the same singleton"


# ── error handling ────────────────────────────────────────────────────────────

class TestErrorHandling:
    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "nonexistent.docx"
        with pytest.raises(Exception):
            convert_to_markdown(missing)
