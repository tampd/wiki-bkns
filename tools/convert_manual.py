#!/usr/bin/env python3
"""
BKNS Agent Wiki — Convert raw/manual/ documents to Markdown
Chuyển đổi DOCX và PDF → Markdown với frontmatter đúng format.

Usage:
    python3 tools/convert_manual.py              # Convert all
    python3 tools/convert_manual.py --force      # Overwrite existing
"""
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mammoth
from pdfminer.high_level import extract_text as pdf_extract_text

from lib.config import RAW_MANUAL_DIR, RAW_CRAWL_DIR
from lib.utils import (
    slugify, now_iso, today_str, sha256_content,
    write_markdown_with_frontmatter, count_words, ensure_dir,
)
from lib.logger import log_entry, log_intake


def detect_category(filename: str) -> str:
    """Auto-detect category from filename."""
    name = filename.lower()
    
    category_keywords = {
        "products/hosting": ["hosting", "wordpress", "platinum", "reseller", "litespeed"],
        "products/vps": ["vps", "cloud vps", "máy chủ ảo", "storage vps", "vpn"],
        "products/ten-mien": ["tên miền", "ten mien", "domain", "transfer tên miền"],
        "products/email": ["email", "e-mail", "mail"],
        "products/ssl": ["ssl", "chứng chỉ", "certificate", "rapidssl", "geotrust",
                          "comodo", "positivessl", "essentialssl", "instantssl",
                          "businessid"],
        "products/server": ["máy chủ", "colocation", "server", "quản trị"],
        "products/software": ["phần mềm", "directadmin", "plesk", "litespeed",
                               "dti", "bản quyền"],
        "products/other": ["backup", "cloud meeting", "e-meeting", "n8n", "misa"],
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


def convert_docx(filepath: Path) -> tuple[str, str]:
    """Convert DOCX to Markdown using mammoth.
    
    Returns: (title, markdown_content)
    """
    with open(filepath, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    
    markdown = result.value
    
    # Extract title from first heading or filename
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Use filename as title
        title = filepath.stem.rsplit(" - ", 1)[0].strip()
    
    # Clean up
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    
    return title, markdown


def convert_pdf(filepath: Path) -> tuple[str, str]:
    """Convert PDF to text using pdfminer.
    
    Returns: (title, text_content)
    """
    text = pdf_extract_text(str(filepath))
    
    # Extract title from first non-empty line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = lines[0] if lines else filepath.stem
    
    # Clean up
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    
    return title, text


def convert_file(filepath: Path, force: bool = False) -> dict:
    """Convert a single file to Markdown with proper frontmatter.
    
    Returns: Result dict
    """
    suffix = filepath.suffix.lower()
    slug = slugify(filepath.stem.rsplit(" - ", 1)[0][:60])
    
    # Output path
    output_name = f"{slug}-{today_str()}.md"
    output_path = RAW_MANUAL_DIR / output_name
    
    if output_path.exists() and not force:
        return {"status": "skip", "detail": f"Already exists: {output_name}"}
    
    # Convert based on file type
    try:
        if suffix == ".docx":
            title, markdown = convert_docx(filepath)
        elif suffix == ".pdf":
            title, markdown = convert_pdf(filepath)
        else:
            return {"status": "skip", "detail": f"Unsupported: {suffix}"}
    except Exception as e:
        return {"status": "error", "detail": f"Convert error: {str(e)}"}
    
    if not markdown or len(markdown.strip()) < 20:
        return {"status": "skip", "detail": "Content too short after conversion"}
    
    # Detect metadata
    category = detect_category(filepath.name)
    source_date = extract_date_from_filename(filepath.name)
    word_count = count_words(markdown)
    content_hash = sha256_content(markdown)
    
    # Write with frontmatter
    frontmatter = {
        "source_url": f"manual://{filepath.name}",
        "crawled_at": now_iso(),
        "content_type": "manual_document",
        "original_file": filepath.name,
        "original_format": suffix.lstrip("."),
        "page_title": title,
        "content_hash": content_hash,
        "word_count": word_count,
        "status": "pending_extract",
        "suggested_category": category,
        "crawl_method": "manual_upload",
        "source_date": source_date,
    }
    
    write_markdown_with_frontmatter(output_path, frontmatter, markdown)
    
    # Log intake
    log_intake("convert-manual", f"manual://{filepath.name}",
               str(output_path), word_count)
    
    log_entry("convert-manual", "success",
              f"Converted {filepath.name} → {output_name} "
              f"(~{word_count} words, {category})")
    
    return {
        "status": "success",
        "output": output_name,
        "title": title,
        "category": category,
        "word_count": word_count,
    }


def convert_all(force: bool = False) -> list[dict]:
    """Convert all DOCX/PDF files in raw/manual/."""
    ensure_dir(RAW_MANUAL_DIR)
    
    files = []
    for ext in ["*.docx", "*.pdf"]:
        files.extend(sorted(RAW_MANUAL_DIR.glob(ext)))
    
    if not files:
        print("Không tìm thấy file DOCX/PDF trong raw/manual/")
        return []
    
    print(f"{'='*60}")
    print(f"BKNS Wiki — Converting {len(files)} manual documents")
    print(f"{'='*60}")
    
    results = []
    categories = {}
    
    for i, f in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {f.name[:60]}...")
        result = convert_file(f, force=force)
        results.append({"file": f.name, **result})
        
        status = result["status"]
        cat = result.get("category", "unknown")
        print(f"  → {status}: {result.get('title', result.get('detail', ''))[:50]}")
        
        if status == "success":
            categories[cat] = categories.get(cat, 0) + 1
    
    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skip")
    errors = sum(1 for r in results if r["status"] == "error")
    
    print(f"\n{'='*60}")
    print(f"Conversion Summary: {success} converted, {skipped} skipped, {errors} errors")
    print(f"\nBy category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} files")
    print(f"{'='*60}")
    
    print(f"\n📋 Bước tiếp theo:")
    print(f"   PYTHONPATH=/home/openclaw/wiki python3 skills/extract-claims/scripts/extract.py")
    
    return results


def main():
    force = "--force" in sys.argv
    convert_all(force=force)


if __name__ == "__main__":
    main()
