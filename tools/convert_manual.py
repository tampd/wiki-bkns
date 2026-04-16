#!/usr/bin/env python3
"""
BKNS Agent Wiki — Convert raw/manual/ documents to Markdown
Chuyển đổi DOCX, PDF, XLSX, HTML, EPUB, PPTX, ZIP → Markdown với frontmatter đúng format.

Backend: markitdown (Microsoft) thay mammoth+pdfminer (v0.4+).
Legacy fallback: mammoth cho .doc (markitdown không support tốt).

Usage:
    python3 tools/convert_manual.py              # Convert all
    python3 tools/convert_manual.py --force      # Overwrite existing
    python3 tools/convert_manual.py --dual-write # Ghi song song legacy + markitdown (pilot mode)
"""
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.converters.markitdown_adapter import convert_to_markdown as md_convert

from lib.config import RAW_MANUAL_DIR, RAW_CRAWL_DIR
from lib.utils import (
    slugify, now_iso, today_str, sha256_content,
    write_markdown_with_frontmatter, count_words, ensure_dir,
    parse_frontmatter,
)
from lib.logger import log_entry, log_intake

# ── Format dispatch ────────────────────────────────────────────────────────────
# markitdown handles all modern formats well; keep legacy mammoth only for .doc
MARKITDOWN_FORMATS = {".docx", ".pdf", ".pptx", ".xlsx", ".html", ".epub", ".zip"}
LEGACY_FORMATS     = {".doc"}   # mammoth, markitdown support poor for old binary .doc

# Legacy output dir (dual-write mode)
RAW_MANUAL_LEGACY_DIR = RAW_MANUAL_DIR.parent / "manual-legacy"


def detect_category(filename: str) -> str:
    """Auto-detect category from filename."""
    name = filename.lower()
    category_keywords = {
        "products/hosting": ["hosting", "wordpress", "platinum", "reseller", "litespeed"],
        "products/vps":     ["vps", "cloud vps", "máy chủ ảo", "storage vps", "vpn"],
        "products/ten-mien": ["tên miền", "ten mien", "domain", "transfer tên miền"],
        "products/email":   ["email", "e-mail", "mail"],
        "products/ssl":     ["ssl", "chứng chỉ", "certificate", "rapidssl", "geotrust",
                              "comodo", "positivessl", "essentialssl", "instantssl",
                              "businessid"],
        "products/server":  ["máy chủ", "colocation", "server", "quản trị"],
        "products/software": ["phần mềm", "directadmin", "plesk", "litespeed",
                               "dti", "bản quyền"],
        "products/other":   ["backup", "cloud meeting", "e-meeting", "n8n", "misa"],
    }
    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in name:
                return category
    return "uncategorized"


def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename pattern: '... - YYYY-MM-DD HH_MM.docx'."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return match.group(1)
    return today_str()


def _extract_title(markdown: str, filepath: Path) -> str:
    """Best-effort title extraction from converted markdown."""
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return filepath.stem.rsplit(" - ", 1)[0].strip()


# ── markitdown backend ─────────────────────────────────────────────────────────

def convert_with_markitdown(filepath: Path) -> tuple[str, str]:
    """Convert any MARKITDOWN_FORMATS file → (title, markdown).

    Raises on empty output (propagates from adapter).
    """
    markdown = md_convert(filepath)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    title = _extract_title(markdown, filepath)
    return title, markdown


# ── legacy backend (mammoth — .doc only) ──────────────────────────────────────

def _convert_legacy_doc(filepath: Path) -> tuple[str, str]:
    """Convert .doc using mammoth (legacy fallback)."""
    try:
        import mammoth
    except ImportError:
        raise ImportError("mammoth not installed — run: pip install mammoth")
    with open(filepath, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    markdown = re.sub(r"\n{3,}", "\n\n", result.value).strip()
    title = _extract_title(markdown, filepath)
    return title, markdown


# ── dual-write legacy helper (for --dual-write mode only) ─────────────────────

def _convert_legacy_for_dual_write(filepath: Path) -> tuple[str, str]:
    """Run legacy mammoth/pdfminer for dual-write comparison."""
    suffix = filepath.suffix.lower()
    if suffix == ".docx":
        try:
            import mammoth
            with open(filepath, "rb") as f:
                result = mammoth.convert_to_markdown(f)
            markdown = re.sub(r"\n{3,}", "\n\n", result.value).strip()
        except ImportError:
            return "", ""
    elif suffix == ".pdf":
        try:
            from pdfminer.high_level import extract_text as pdf_extract_text
            text = pdf_extract_text(str(filepath))
            markdown = re.sub(r"\n{3,}", "\n\n", text).strip()
        except ImportError:
            return "", ""
    else:
        return "", ""   # format not supported by legacy
    title = _extract_title(markdown, filepath)
    return title, markdown


# ── core convert_file ──────────────────────────────────────────────────────────

def convert_file(filepath: Path, force: bool = False,
                 dual_write: bool = False) -> dict:
    """Convert a single file to Markdown with proper frontmatter.

    Deduplication: checks ALL existing .md files with the same slug prefix.
    If any existing file has the same content_hash, skip conversion.

    Args:
        filepath:   Source document path.
        force:      Overwrite existing output.
        dual_write: Also write legacy output to raw/manual-legacy/ for diffing.

    Returns:
        Result dict with keys: status, output, title, category, word_count, detail.
    """
    suffix = filepath.suffix.lower()
    slug = slugify(filepath.stem.rsplit(" - ", 1)[0][:60])

    # Determine converter
    if suffix in MARKITDOWN_FORMATS:
        converter = "markitdown"
    elif suffix in LEGACY_FORMATS:
        converter = "legacy"
    else:
        return {"status": "skip", "detail": f"Unsupported format: {suffix}"}

    # Output path
    output_name = f"{slug}-{today_str()}.md"
    output_path = RAW_MANUAL_DIR / output_name

    if output_path.exists() and not force:
        return {"status": "skip", "detail": f"Already exists: {output_name}"}

    # Skip if already extracted
    if not force:
        for existing_md in RAW_MANUAL_DIR.glob(f"{slug}-*.md"):
            if existing_md == output_path:
                continue
            try:
                existing_content = existing_md.read_text(encoding="utf-8")
                existing_fm, _ = parse_frontmatter(existing_content)
                if existing_fm.get("status") == "extracted":
                    return {"status": "skip",
                            "detail": f"Already extracted: {existing_md.name}"}
            except Exception:
                continue

    # Convert
    try:
        if converter == "markitdown":
            title, markdown = convert_with_markitdown(filepath)
        else:
            title, markdown = _convert_legacy_doc(filepath)
    except Exception as e:
        return {"status": "error", "detail": f"Convert error: {e}"}

    if not markdown or len(markdown.strip()) < 20:
        return {"status": "skip", "detail": "Content too short after conversion"}

    # Metadata
    category     = detect_category(filepath.name)
    source_date  = extract_date_from_filename(filepath.name)
    word_count   = count_words(markdown)
    content_hash = sha256_content(markdown)

    frontmatter = {
        "source_url":       f"manual://{filepath.name}",
        "crawled_at":       now_iso(),
        "content_type":     "manual_document",
        "original_file":    filepath.name,
        "original_format":  suffix.lstrip("."),
        "page_title":       title,
        "content_hash":     content_hash,
        "word_count":       word_count,
        "status":           "pending_extract",
        "suggested_category": category,
        "crawl_method":     "manual_upload",
        "source_date":      source_date,
        "converter":        converter,          # new in v0.4 — tracks which backend was used
    }

    write_markdown_with_frontmatter(output_path, frontmatter, markdown)
    log_intake("convert-manual", f"manual://{filepath.name}",
               str(output_path), word_count)
    log_entry("convert-manual", "success",
              f"Converted {filepath.name} → {output_name} "
              f"(~{word_count} words, {category}, via {converter})")

    # Dual-write: also produce legacy output for comparison
    if dual_write and suffix in {".docx", ".pdf"}:
        _write_legacy_output(filepath, slug, source_date, category)

    return {
        "status":     "success",
        "output":     output_name,
        "title":      title,
        "category":   category,
        "word_count": word_count,
        "converter":  converter,
    }


def _write_legacy_output(filepath: Path, slug: str,
                          source_date: str, category: str) -> None:
    """Write legacy converter output to raw/manual-legacy/ (dual-write mode)."""
    ensure_dir(RAW_MANUAL_LEGACY_DIR)
    try:
        title_l, markdown_l = _convert_legacy_for_dual_write(filepath)
    except Exception:
        return
    if not markdown_l or len(markdown_l.strip()) < 20:
        return

    output_name_l = f"{slug}-{today_str()}.md"
    output_path_l = RAW_MANUAL_LEGACY_DIR / output_name_l
    if output_path_l.exists():
        return

    frontmatter_l = {
        "source_url":      f"manual://{filepath.name}",
        "crawled_at":      now_iso(),
        "content_type":    "manual_document",
        "original_file":   filepath.name,
        "original_format": filepath.suffix.lower().lstrip("."),
        "page_title":      title_l,
        "content_hash":    sha256_content(markdown_l),
        "word_count":      count_words(markdown_l),
        "status":          "dual_write_legacy",
        "suggested_category": category,
        "crawl_method":    "manual_upload",
        "source_date":     source_date,
        "converter":       "legacy",
    }
    write_markdown_with_frontmatter(output_path_l, frontmatter_l, markdown_l)


# ── batch driver ───────────────────────────────────────────────────────────────

def convert_all(force: bool = False, dual_write: bool = False) -> list[dict]:
    """Convert all supported files in raw/manual/."""
    ensure_dir(RAW_MANUAL_DIR)

    files = []
    for ext in [f"*{e}" for e in sorted(MARKITDOWN_FORMATS | LEGACY_FORMATS)]:
        files.extend(sorted(RAW_MANUAL_DIR.glob(ext)))

    if not files:
        print("Không tìm thấy file hỗ trợ trong raw/manual/")
        return []

    mode_label = " [DUAL-WRITE]" if dual_write else ""
    print(f"{'='*60}")
    print(f"BKNS Wiki — Converting {len(files)} manual documents{mode_label}")
    print(f"{'='*60}")

    results = []
    categories: dict[str, int] = {}

    for i, f in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {f.name[:60]}...")
        result = convert_file(f, force=force, dual_write=dual_write)
        results.append({"file": f.name, **result})

        status = result["status"]
        cat    = result.get("category", "unknown")
        conv   = result.get("converter", "")
        label  = f"[{conv}] " if conv else ""
        print(f"  → {status}: {label}{result.get('title', result.get('detail', ''))[:50]}")

        if status == "success":
            categories[cat] = categories.get(cat, 0) + 1

    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skip")
    errors  = sum(1 for r in results if r["status"] == "error")

    print(f"\n{'='*60}")
    print(f"Summary: {success} converted, {skipped} skipped, {errors} errors")
    print(f"\nBy category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} files")
    print(f"{'='*60}")

    if dual_write:
        print(f"\n📁 Legacy output → raw/manual-legacy/")
        print(f"   Run: python3 tools/diff_converters.py để xem diff")

    print(f"\n📋 Bước tiếp theo:")
    print(f"   PYTHONPATH=/wiki python3 skills/extract-claims/scripts/extract.py")

    return results


def main():
    force      = "--force"      in sys.argv
    dual_write = "--dual-write" in sys.argv
    convert_all(force=force, dual_write=dual_write)


if __name__ == "__main__":
    main()
