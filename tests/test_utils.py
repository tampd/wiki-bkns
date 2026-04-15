"""Tests for lib/utils.py — core utility functions."""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.utils import (
    slugify,
    generate_claim_id,
    parse_frontmatter,
    now_iso,
    today_str,
)


class TestSlugify:
    def test_basic_ascii(self):
        assert slugify("Hello World") == "hello-world"

    def test_vietnamese_chars(self):
        result = slugify("Tiếng Việt có dấu")
        assert isinstance(result, str)
        assert len(result) > 0
        assert " " not in result

    def test_special_chars_removed(self):
        result = slugify("hello! world@2024")
        assert "!" not in result
        assert "@" not in result

    def test_empty_string(self):
        result = slugify("")
        assert isinstance(result, str)

    def test_multiple_spaces(self):
        result = slugify("a  b  c")
        assert "--" not in result


class TestGenerateClaimId:
    def test_basic_format(self):
        claim_id = generate_claim_id("hosting", "bkh01", "monthly_price")
        assert isinstance(claim_id, str)
        assert len(claim_id) > 0

    def test_unique_for_different_inputs(self):
        id1 = generate_claim_id("hosting", "bkh01", "monthly_price")
        id2 = generate_claim_id("hosting", "bkh02", "monthly_price")
        assert id1 != id2

    def test_consistent_for_same_inputs(self):
        id1 = generate_claim_id("hosting", "bkh01", "monthly_price")
        id2 = generate_claim_id("hosting", "bkh01", "monthly_price")
        assert id1 == id2


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\ntitle: Test Page\ncategory: hosting\n---\n\n# Content"
        fm, body = parse_frontmatter(content)
        assert fm["title"] == "Test Page"
        assert fm["category"] == "hosting"
        assert "# Content" in body

    def test_no_frontmatter(self):
        content = "# Just content\nNo frontmatter here."
        fm, body = parse_frontmatter(content)
        assert fm == {}
        assert "# Just content" in body

    def test_empty_content(self):
        fm, body = parse_frontmatter("")
        assert fm == {}
        assert body == ""

    def test_frontmatter_only(self):
        content = "---\ntitle: Test\n---\n"
        fm, body = parse_frontmatter(content)
        assert fm["title"] == "Test"


class TestDateFunctions:
    def test_now_iso_format(self):
        ts = now_iso()
        assert isinstance(ts, str)
        assert "T" in ts
        assert len(ts) > 10

    def test_today_str_format(self):
        today = today_str()
        assert isinstance(today, str)
        # Should be YYYY-MM-DD format
        parts = today.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # year
