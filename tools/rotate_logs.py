#!/usr/bin/env python3
"""
Log rotation script for BKNS Agent Wiki.
- Keeps last N lines of each JSONL log file
- Archives old logs to logs/archive/ with date suffix
- Run via cron: 0 3 * * 0 (weekly at 3am Sunday)
"""

import os
import gzip
import shutil
from datetime import datetime
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = WIKI_ROOT / 'logs'
ARCHIVE_DIR = LOGS_DIR / 'archive'
KEEP_LINES = 5000        # keep last N lines per file
MAX_ARCHIVE_DAYS = 30    # delete archives older than this

ROTATE_PATTERNS = [
    '*.jsonl',
    '*.log',
]

def rotate_file(filepath: Path) -> None:
    """Rotate a single log file: keep last KEEP_LINES, archive the rest."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
        lines = content.splitlines(keepends=True)

        if len(lines) <= KEEP_LINES:
            return  # nothing to rotate

        keep_lines = lines[-KEEP_LINES:]
        archive_lines = lines[:-KEEP_LINES]

        # Write archive
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d')
        archive_name = f"{filepath.stem}-{date_str}.log.gz"
        archive_path = ARCHIVE_DIR / archive_name

        with gzip.open(archive_path, 'wt', encoding='utf-8') as f:
            f.writelines(archive_lines)

        # Truncate original
        filepath.write_text(''.join(keep_lines), encoding='utf-8')
        print(f"  ✂️  Rotated {filepath.name}: {len(lines)} → {len(keep_lines)} lines, archived {len(archive_lines)} lines")

    except Exception as e:
        print(f"  ⚠️  Failed to rotate {filepath.name}: {e}")


def clean_old_archives() -> None:
    """Remove archive files older than MAX_ARCHIVE_DAYS."""
    if not ARCHIVE_DIR.exists():
        return
    cutoff = datetime.now().timestamp() - (MAX_ARCHIVE_DAYS * 86400)
    for f in ARCHIVE_DIR.iterdir():
        if f.stat().st_mtime < cutoff:
            f.unlink()
            print(f"  🗑️  Deleted old archive: {f.name}")


def main():
    print(f"\n📋 BKNS Log Rotation — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Logs dir: {LOGS_DIR}")
    print(f"  Keep: last {KEEP_LINES} lines per file")

    rotated = 0
    for pattern in ROTATE_PATTERNS:
        for filepath in sorted(LOGS_DIR.glob(pattern)):
            if filepath.is_file():
                rotate_file(filepath)
                rotated += 1

    clean_old_archives()
    print(f"\n✅ Done — checked {rotated} log files\n")


if __name__ == '__main__':
    main()
