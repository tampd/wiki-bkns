#!/usr/bin/env python3
"""
BKNS Agent Wiki — ingest_html.py
Fetch một trang HTML từ URL → Markdown → raw/html/

markitdown xử lý URL trực tiếp (requests + BeautifulSoup).
Output: raw/html/YYYY-MM-DD/<slug>.md với frontmatter chuẩn.

Usage:
    python3 tools/ingest_html.py <url>
    python3 tools/ingest_html.py <url> --dry-run
    python3 tools/ingest_html.py <url> --force
"""
import sys
import re
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.converters.markitdown_adapter import get_converter
from lib.config import RAW_DIR
from lib.utils import (
    url_to_slug, slugify, now_iso, today_str, sha256_content,
    write_markdown_with_frontmatter, count_words, ensure_dir,
)
from lib.logger import log_entry, log_intake

RAW_HTML_DIR = RAW_DIR / "html"


def _extract_title(markdown: str, url: str) -> str:
    """Best-effort title extraction from converted HTML markdown."""
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return url_to_slug(url).replace("-", " ").title()


def ingest_html(url: str, *, force: bool = False, dry_run: bool = False) -> dict:
    """Fetch an HTML page and convert to Markdown → raw/html/<date>/<slug>.md

    Args:
        url:     Full URL of page to ingest.
        force:   Overwrite existing output.
        dry_run: Print what would happen without writing.

    Returns:
        Result dict with keys: status, output, title, word_count, detail.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {"status": "error", "detail": f"URL không hợp lệ: {url}"}

    slug = url_to_slug(url)[:60]
    date_str = today_str()
    output_dir = RAW_HTML_DIR / date_str
    output_name = f"html-{slug}-{date_str}.md"
    output_path = output_dir / output_name

    if output_path.exists() and not force:
        return {"status": "skip", "detail": f"Đã tồn tại: {output_name}"}

    if dry_run:
        print(f"[DRY-RUN] Sẽ ingest: {url}")
        print(f"          Output: raw/html/{date_str}/{output_name}")
        return {"status": "dry_run", "detail": "dry-run — không ghi file"}

    # Convert via markitdown (handles HTTP fetch internally)
    try:
        converter = get_converter()
        result = converter.convert(url)
        markdown = (result.text_content or "").strip()
    except Exception as e:
        return {"status": "error", "detail": f"markitdown lỗi: {e}"}

    if not markdown or len(markdown) < 20:
        return {"status": "error", "detail": "Nội dung rỗng sau convert"}

    # Clean up excess blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    title = _extract_title(markdown, url)
    word_count = count_words(markdown)
    content_hash = sha256_content(markdown)

    frontmatter = {
        "source_url":   url,
        "crawled_at":   now_iso(),
        "content_type": "html_page",
        "page_title":   title,
        "content_hash": content_hash,
        "word_count":   word_count,
        "status":       "pending_extract",
        "crawl_method": "ingest_html",
        "source_date":  date_str,
        "converter":    "markitdown",
    }

    ensure_dir(output_dir)
    write_markdown_with_frontmatter(output_path, frontmatter, markdown)
    log_intake("ingest-html", url, str(output_path), word_count)
    log_entry("ingest-html", "success",
              f"Ingested {url} → {output_name} (~{word_count} words)")

    return {
        "status":     "success",
        "output":     str(output_path.relative_to(RAW_DIR.parent)),
        "title":      title,
        "word_count": word_count,
    }


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print(__doc__)
        sys.exit(1)

    url = args[0]
    force   = "--force"   in args
    dry_run = "--dry-run" in args

    result = ingest_html(url, force=force, dry_run=dry_run)
    status = result["status"]
    if status == "success":
        print(f"✓ {result['title'][:60]}")
        print(f"  → {result['output']} ({result['word_count']} từ)")
    elif status == "skip":
        print(f"⏭  Bỏ qua: {result['detail']}")
    elif status == "dry_run":
        pass  # already printed
    else:
        print(f"✗ Lỗi: {result['detail']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
