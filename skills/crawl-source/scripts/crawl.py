#!/usr/bin/env python3
"""
BKNS Agent Wiki — crawl-source
Thu thập nội dung từ URL → raw/website-crawl/ với metadata.
Không dùng LLM — chỉ crawl, clean HTML, lưu Markdown.

Usage:
    python3 scripts/crawl.py [URL1] [URL2] ...
    python3 scripts/crawl.py --batch  # Crawl 5 trang mặc định
"""
import sys
import re
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import html2text

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    RAW_CRAWL_DIR, SOURCES_REGISTRY, CRAWL_RULES, CATEGORY_MAP,
    WORKSPACE,
)
from lib.logger import log_entry, log_intake
from lib.telegram import notify_skill, notify_error
from lib.utils import (
    sha256_content, url_to_slug, today_str, now_iso,
    read_yaml, write_yaml, write_markdown_with_frontmatter,
    count_words, ensure_dir,
)


# ── Default batch URLs ─────────────────────────────────────
BATCH_URLS = [
    "https://bkns.vn",
    "https://bkns.vn/hosting",
    "https://bkns.vn/ten-mien",
    "https://bkns.vn/vps",
    "https://bkns.vn/lien-he",
]

# HTTP headers
HEADERS = {
    "User-Agent": "BKNSWikiBot/1.0 (+https://bkns.vn)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


def validate_url(url: str) -> tuple[bool, str]:
    """Validate URL scheme and domain.

    Returns:
        (is_valid, message)
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, f"URL không hợp lệ: {url}"

    if parsed.scheme not in CRAWL_RULES["url_scheme"]:
        return False, f"Scheme không hợp lệ: {parsed.scheme} (cần http/https)"

    if not parsed.netloc:
        return False, f"URL thiếu domain: {url}"

    return True, ""


def is_bkns_domain(url: str) -> bool:
    """Check if URL belongs to bkns.vn domain."""
    parsed = urlparse(url)
    return "bkns.vn" in parsed.netloc


def check_duplicate(slug: str) -> bool:
    """Check if content was crawled within 24h window."""
    window = timedelta(hours=CRAWL_RULES["duplicate_window_hours"])
    cutoff = datetime.now() - window

    for f in RAW_CRAWL_DIR.glob(f"{slug}-*.md"):
        # Parse date from filename: {slug}-{YYYY-MM-DD}.md
        try:
            date_part = f.stem.split("-")[-3:]  # YYYY, MM, DD
            file_date = datetime(
                int(date_part[0]), int(date_part[1]), int(date_part[2])
            )
            if file_date.date() >= cutoff.date():
                return True
        except (ValueError, IndexError):
            continue
    return False


def check_hash_unchanged(slug: str, new_hash: str) -> bool:
    """Check if content hash matches most recent crawl of same slug."""
    files = sorted(RAW_CRAWL_DIR.glob(f"{slug}-*.md"), reverse=True)
    if not files:
        return False

    # Read frontmatter of most recent file
    try:
        content = files[0].read_text(encoding="utf-8")
        if "content_hash:" in content:
            old_hash = re.search(r"content_hash:\s*(.+)", content)
            if old_hash and old_hash.group(1).strip() == new_hash:
                return True
    except Exception:
        pass
    return False


def detect_category(url: str, title: str = "") -> str:
    """Auto-detect category from URL path and title."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").lower()

    # Check URL path
    for keyword, category in CATEGORY_MAP.items():
        if keyword in path:
            return category

    # Check title
    title_lower = title.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in title_lower:
            return category

    return "uncategorized"


def fetch_and_clean(url: str) -> tuple[str, str, str]:
    """Fetch URL and clean HTML to Markdown.

    Returns:
        (title, markdown_content, raw_html_for_hash)
    """
    timeout = CRAWL_RULES["timeout_seconds"]
    max_retries = CRAWL_RULES["max_retries"]

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            break
        except requests.RequestException as e:
            last_error = e
            if attempt < max_retries:
                import time
                time.sleep(2)
    else:
        raise RuntimeError(f"HTTP error after {max_retries + 1} attempts: {last_error}")

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)

    # Remove unwanted elements
    for tag in soup.find_all(["nav", "footer", "script", "style", "aside",
                               "header", "noscript", "iframe"]):
        tag.decompose()

    # Remove common noise classes
    for cls in ["menu", "sidebar", "advertisement", "cookie", "popup"]:
        for tag in soup.find_all(class_=re.compile(cls, re.I)):
            tag.decompose()

    # Convert to Markdown
    converter = html2text.HTML2Text()
    converter.body_width = 0  # No line wrapping
    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_emphasis = False
    converter.skip_internal_links = False

    markdown = converter.handle(str(soup))

    # Clean up excessive whitespace
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    return title, markdown, html


def crawl_url(url: str, force: bool = False) -> dict:
    """Crawl a single URL and save to raw/.

    Args:
        url: URL to crawl
        force: Skip duplicate/hash checks

    Returns:
        Result dict with status and details
    """
    log_entry("crawl-source", "start", f"Crawling: {url}")

    # 1. Validate URL
    valid, msg = validate_url(url)
    if not valid:
        log_entry("crawl-source", "error", msg, severity="high")
        notify_error("crawl-source", msg)
        return {"status": "error", "detail": msg}

    # 2. Check domain
    if not is_bkns_domain(url) and CRAWL_RULES["warn_if_not_bkns"]:
        notify_skill("crawl-source",
                      f"URL ngoài bkns.vn: {url}. Tiếp tục crawl...",
                      severity="medium")

    slug = url_to_slug(url)

    # 3. Check duplicate (24h window)
    if not force and check_duplicate(slug):
        log_entry("crawl-source", "skip", f"Đã crawl trong 24h: {slug}")
        return {"status": "skip", "detail": f"Đã crawl gần đây: {slug}"}

    # 4. Fetch and clean
    try:
        title, markdown, raw_html = fetch_and_clean(url)
    except Exception as e:
        error_msg = f"Không truy cập được {url}: {str(e)}"
        log_entry("crawl-source", "error", error_msg, severity="high")
        notify_error("crawl-source", error_msg)
        return {"status": "error", "detail": error_msg}

    # 5. Hash check
    content_hash = sha256_content(markdown)
    if not force and CRAWL_RULES["content_hash_check"]:
        if check_hash_unchanged(slug, content_hash):
            log_entry("crawl-source", "skip", f"Content unchanged: {slug}")
            return {"status": "skip", "detail": f"Nội dung không đổi: {slug}"}

    # 6. Word count check
    word_count = count_words(markdown)
    if word_count < CRAWL_RULES["min_word_count"]:
        notify_skill("crawl-source",
                      f"Trang {url} chỉ có {word_count} từ (min: {CRAWL_RULES['min_word_count']})",
                      severity="medium")

    # 7. Detect category
    category = detect_category(url, title)

    # 8. Save to raw/
    ensure_dir(RAW_CRAWL_DIR)
    filename = f"{slug}-{today_str()}.md"
    filepath = RAW_CRAWL_DIR / filename

    frontmatter = {
        "source_url": url,
        "crawled_at": now_iso(),
        "content_type": "webpage",
        "domain": urlparse(url).netloc,
        "page_title": title,
        "content_hash": content_hash,
        "word_count": word_count,
        "status": "pending_extract",
        "suggested_category": category,
        "crawl_method": "http_get",
    }

    write_markdown_with_frontmatter(filepath, frontmatter, markdown)

    # 9. Update sources/registry.yaml
    source_id = f"SRC-BKNS-WEB-{slug.upper().replace('-', '_')}"
    update_sources_registry(source_id, url, slug, filename, content_hash)

    # 10. Log intake
    log_intake("crawl-source", url, str(filepath), word_count)
    log_entry("crawl-source", "success",
              f"Saved {filename} (~{word_count} words, category: {category})")

    # 11. Notify admin
    notify_skill("crawl-source",
                  f"Đã lưu [{url}]({url}) → `raw/website-crawl/{filename}`\n"
                  f"~{word_count} từ | Category: {category}\n"
                  f"Gõ /extract để trích claims.",
                  severity="success")

    return {
        "status": "success",
        "filename": filename,
        "filepath": str(filepath),
        "word_count": word_count,
        "category": category,
        "content_hash": content_hash,
        "source_id": source_id,
    }


def update_sources_registry(
    source_id: str,
    url: str,
    slug: str,
    filename: str,
    content_hash: str,
):
    """Add or update entry in sources/registry.yaml."""
    data = read_yaml(SOURCES_REGISTRY)
    if not isinstance(data, dict):
        data = {"sources": []}
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        sources = []

    # Check if source exists
    for src in sources:
        if src.get("source_id") == source_id:
            src["last_crawled"] = today_str()
            src["raw_file"] = f"raw/website-crawl/{filename}"
            src["hash"] = content_hash
            break
    else:
        # New source
        sources.append({
            "source_id": source_id,
            "type": "official_product_page",
            "url": url,
            "authority_level": 3,
            "freshness_sla_days": 7,
            "last_crawled": today_str(),
            "raw_file": f"raw/website-crawl/{filename}",
            "hash": content_hash,
        })

    data["sources"] = sources
    write_yaml(data, SOURCES_REGISTRY)


def crawl_batch(urls: list[str], force: bool = False) -> list[dict]:
    """Crawl multiple URLs."""
    results = []
    total = len(urls)

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{total}] Crawling: {url}")
        result = crawl_url(url, force=force)
        results.append({"url": url, **result})
        print(f"  → {result['status']}: {result.get('detail', result.get('filename', ''))}")

        # Small delay between requests
        if i < total:
            import time
            time.sleep(1)

    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skip")
    errors = sum(1 for r in results if r["status"] == "error")

    print(f"\n{'='*50}")
    print(f"Crawl Summary: {success} success, {skipped} skipped, {errors} errors")
    print(f"{'='*50}")

    return results


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Crawler")
    parser.add_argument("urls", nargs="*", help="URLs to crawl")
    parser.add_argument("--batch", action="store_true",
                        help="Crawl default batch URLs")
    parser.add_argument("--force", action="store_true",
                        help="Ignore duplicate/hash checks")
    args = parser.parse_args()

    if args.batch:
        urls = BATCH_URLS
    elif args.urls:
        urls = args.urls
    else:
        print("Usage: python3 crawl.py [URL1] [URL2] ... | --batch")
        sys.exit(1)

    results = crawl_batch(urls, force=args.force)

    # Return non-zero if any errors
    errors = sum(1 for r in results if r["status"] == "error")
    sys.exit(1 if errors == len(results) else 0)


if __name__ == "__main__":
    main()
