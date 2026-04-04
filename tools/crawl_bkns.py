#!/usr/bin/env python3
"""
BKNS Agent Wiki — Batch crawl ban đầu (Phase 0.5)
Crawl 5 trang ưu tiên: index, hosting, ten-mien, vps, lien-he

Usage:
    python3 tools/crawl_bkns.py
    python3 tools/crawl_bkns.py --force  # Bỏ qua duplicate check
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skills.crawl_source_runner import run_batch_crawl


def main():
    force = "--force" in sys.argv
    run_batch_crawl(force=force)


def run_batch_crawl_direct(force=False):
    """Direct import fallback."""
    from skills.crawl_source.scripts.crawl import crawl_batch, BATCH_URLS
    return crawl_batch(BATCH_URLS, force=force)


if __name__ == "__main__":
    # Direct execution
    force = "--force" in sys.argv

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from skills.crawl_source.scripts.crawl import crawl_batch, BATCH_URLS

    print("=" * 50)
    print("BKNS Wiki — Batch Crawl Ban Đầu (Phase 0.5)")
    print("=" * 50)
    print(f"URLs to crawl: {len(BATCH_URLS)}")
    print(f"Force mode: {force}")
    print()

    results = crawl_batch(BATCH_URLS, force=force)
