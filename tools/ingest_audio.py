#!/usr/bin/env python3
"""
BKNS Agent Wiki — ingest_audio.py
Transcribe .mp3 / .wav → Markdown → raw/audio/

markitdown dùng openai-whisper cục bộ (nếu cài) hoặc OpenAI Whisper API
(nếu OPENAI_API_KEY có trong .env) để transcribe audio.

Output: raw/audio/YYYY-MM-DD/<slug>.md với frontmatter chuẩn.

Usage:
    python3 tools/ingest_audio.py <file.mp3>
    python3 tools/ingest_audio.py <file.wav> --dry-run
    python3 tools/ingest_audio.py <file.mp3> --force
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.converters.markitdown_adapter import get_converter
from lib.config import RAW_DIR
from lib.utils import (
    slugify, now_iso, today_str, sha256_content,
    write_markdown_with_frontmatter, count_words, ensure_dir,
)
from lib.logger import log_entry, log_intake

RAW_AUDIO_DIR = RAW_DIR / "audio"

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


def _extract_title(markdown: str, filepath: Path) -> str:
    """Best-effort title extraction from transcript markdown."""
    match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return filepath.stem.replace("_", " ").replace("-", " ").title()


def ingest_audio(file_path: str | Path, *, force: bool = False,
                 dry_run: bool = False) -> dict:
    """Transcribe an audio file → raw/audio/<date>/<slug>.md

    Args:
        file_path: Path to .mp3 or .wav file.
        force:     Overwrite existing output.
        dry_run:   Print what would happen without writing.

    Returns:
        Result dict with keys: status, output, title, word_count, detail.
    """
    filepath = Path(file_path).resolve()
    if not filepath.exists():
        return {"status": "error", "detail": f"File không tồn tại: {filepath}"}

    suffix = filepath.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return {
            "status": "error",
            "detail": (
                f"Định dạng {suffix} không hỗ trợ. "
                f"Hỗ trợ: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            ),
        }

    slug = slugify(filepath.stem)[:60]
    date_str = today_str()
    output_dir = RAW_AUDIO_DIR / date_str
    output_name = f"audio-{slug}-{date_str}.md"
    output_path = output_dir / output_name

    if output_path.exists() and not force:
        return {"status": "skip", "detail": f"Đã tồn tại: {output_name}"}

    if dry_run:
        print(f"[DRY-RUN] Sẽ transcribe: {filepath.name}")
        print(f"          Output: raw/audio/{date_str}/{output_name}")
        return {"status": "dry_run", "detail": "dry-run — không ghi file"}

    # Convert via markitdown (Whisper backend)
    try:
        converter = get_converter()
        result = converter.convert(str(filepath))
        markdown = (result.text_content or "").strip()
    except Exception as e:
        return {"status": "error", "detail": f"markitdown/Whisper lỗi: {e}"}

    if not markdown or len(markdown) < 20:
        return {"status": "error",
                "detail": "Transcript rỗng — file audio có thể bị hỏng hoặc im lặng"}

    # Clean up excess blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    title = _extract_title(markdown, filepath)
    word_count = count_words(markdown)
    content_hash = sha256_content(markdown)
    file_size_mb = round(filepath.stat().st_size / 1024 / 1024, 2)

    frontmatter = {
        "source_url":       f"audio://{filepath.name}",
        "crawled_at":       now_iso(),
        "content_type":     "audio_transcript",
        "original_file":    filepath.name,
        "original_format":  suffix.lstrip("."),
        "file_size_mb":     file_size_mb,
        "page_title":       title,
        "content_hash":     content_hash,
        "word_count":       word_count,
        "status":           "pending_extract",
        "crawl_method":     "ingest_audio",
        "source_date":      date_str,
        "converter":        "markitdown",
    }

    ensure_dir(output_dir)
    write_markdown_with_frontmatter(output_path, frontmatter, markdown)
    log_intake("ingest-audio", f"audio://{filepath.name}",
               str(output_path), word_count)
    log_entry("ingest-audio", "success",
              f"Transcribed {filepath.name} → {output_name} (~{word_count} words)")

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

    file_path = args[0]
    force   = "--force"   in args
    dry_run = "--dry-run" in args

    result = ingest_audio(file_path, force=force, dry_run=dry_run)
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
