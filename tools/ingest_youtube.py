#!/usr/bin/env python3
"""
BKNS Agent Wiki — ingest_youtube.py
Tải transcript YouTube → Markdown → raw/youtube/

markitdown xử lý YouTube URL trực tiếp (dùng youtube-transcript-api).
Output: raw/youtube/YYYY-MM-DD/<slug>.md với frontmatter chuẩn.

Usage:
    python3 tools/ingest_youtube.py <youtube_url>
    python3 tools/ingest_youtube.py <youtube_url> --dry-run
    python3 tools/ingest_youtube.py <youtube_url> --force
"""
import sys
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.converters.markitdown_adapter import get_converter
from lib.config import RAW_DIR
from lib.utils import (
    slugify, now_iso, today_str, sha256_content,
    write_markdown_with_frontmatter, count_words, ensure_dir,
)
from lib.logger import log_entry, log_intake

RAW_YOUTUBE_DIR = RAW_DIR / "youtube"


def _extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    parsed = urlparse(url)
    # https://www.youtube.com/watch?v=ID
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        # https://www.youtube.com/shorts/ID
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] in ("shorts", "embed", "v"):
            return parts[1]
    # https://youtu.be/ID
    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")
    return None


def _extract_title(markdown: str, url: str) -> str:
    """Best-effort title extraction from transcript markdown."""
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if match:
        return match.group(1).strip()
    video_id = _extract_video_id(url)
    return f"YouTube transcript {video_id or 'unknown'}"


def ingest_youtube(url: str, *, force: bool = False, dry_run: bool = False) -> dict:
    """Ingest a YouTube video transcript → raw/youtube/<date>/<slug>.md

    Args:
        url:     YouTube video URL.
        force:   Overwrite existing output.
        dry_run: Print what would happen without writing.

    Returns:
        Result dict with keys: status, output, title, word_count, detail.
    """
    video_id = _extract_video_id(url)
    if not video_id:
        return {"status": "error", "detail": f"Không phân tích được YouTube URL: {url}"}

    slug = f"youtube-{video_id}"
    date_str = today_str()
    output_dir = RAW_YOUTUBE_DIR / date_str
    output_name = f"{slug}-{date_str}.md"
    output_path = output_dir / output_name

    if output_path.exists() and not force:
        return {"status": "skip", "detail": f"Đã tồn tại: {output_name}"}

    if dry_run:
        print(f"[DRY-RUN] Sẽ ingest: {url}")
        print(f"          Output: raw/youtube/{date_str}/{output_name}")
        return {"status": "dry_run", "detail": "dry-run — không ghi file"}

    # Convert via markitdown
    try:
        converter = get_converter()
        result = converter.convert(url)
        markdown = (result.text_content or "").strip()
    except Exception as e:
        return {"status": "error", "detail": f"markitdown lỗi: {e}"}

    if not markdown or len(markdown) < 20:
        return {"status": "error", "detail": "Transcript rỗng — video có thể không có phụ đề"}

    # Clean up excess blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    title = _extract_title(markdown, url)
    word_count = count_words(markdown)
    content_hash = sha256_content(markdown)

    frontmatter = {
        "source_url":     url,
        "crawled_at":     now_iso(),
        "content_type":   "youtube_transcript",
        "video_id":       video_id,
        "page_title":     title,
        "content_hash":   content_hash,
        "word_count":     word_count,
        "status":         "pending_extract",
        "crawl_method":   "ingest_youtube",
        "source_date":    date_str,
        "converter":      "markitdown",
    }

    ensure_dir(output_dir)
    write_markdown_with_frontmatter(output_path, frontmatter, markdown)
    log_intake("ingest-youtube", url, str(output_path), word_count)
    log_entry("ingest-youtube", "success",
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

    result = ingest_youtube(url, force=force, dry_run=dry_run)
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
