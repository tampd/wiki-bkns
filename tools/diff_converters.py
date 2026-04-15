#!/usr/bin/env python3
"""
diff_converters.py — So sánh output của markitdown vs legacy converter.

Đọc tất cả file .md trong raw/manual/ và raw/manual-legacy/ cùng slug,
tính % khác biệt theo difflib, in báo cáo.

Usage:
    python3 tools/diff_converters.py
    python3 tools/diff_converters.py --json      # JSON output
    python3 tools/diff_converters.py --threshold 5  # chỉ show file > 5% diff
"""
import sys
import json
import difflib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import RAW_MANUAL_DIR
from lib.utils import parse_frontmatter

RAW_MANUAL_LEGACY_DIR = RAW_MANUAL_DIR.parent / "manual-legacy"

# Acceptance threshold from PART 03 spec: ≤ 5% difference is OK
DEFAULT_THRESHOLD = 5.0


def _body(md_path: Path) -> str:
    """Return body text (no frontmatter) from a markdown file."""
    try:
        content = md_path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(content)
        return body.strip()
    except Exception:
        return ""


def _diff_ratio(a: str, b: str) -> float:
    """Return similarity ratio 0.0–1.0 between two strings (difflib)."""
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def compare_dirs(threshold: float = DEFAULT_THRESHOLD) -> list[dict]:
    """Compare markitdown output (manual/) vs legacy (manual-legacy/).

    Returns list of result dicts, one per matched slug.
    """
    if not RAW_MANUAL_LEGACY_DIR.exists():
        print(f"[WARN] {RAW_MANUAL_LEGACY_DIR} không tồn tại. "
              f"Chạy convert_manual.py --dual-write trước.")
        return []

    new_files  = {f.name: f for f in RAW_MANUAL_DIR.glob("*.md")}
    leg_files  = {f.name: f for f in RAW_MANUAL_LEGACY_DIR.glob("*.md")}
    common     = sorted(set(new_files) & set(leg_files))

    if not common:
        print("[WARN] Không tìm thấy file nào khớp slug giữa 2 thư mục.")
        return []

    results = []
    for name in common:
        body_new = _body(new_files[name])
        body_leg = _body(leg_files[name])
        similarity = _diff_ratio(body_new, body_leg)
        diff_pct   = round((1 - similarity) * 100, 1)
        char_delta = len(body_new) - len(body_leg)

        results.append({
            "file":         name,
            "diff_pct":     diff_pct,
            "char_new":     len(body_new),
            "char_legacy":  len(body_leg),
            "char_delta":   char_delta,
            "ok":           diff_pct <= threshold,
        })

    return results


def print_report(results: list[dict], threshold: float = DEFAULT_THRESHOLD) -> None:
    """Print human-readable diff report."""
    if not results:
        return
    ok      = sum(1 for r in results if r["ok"])
    fail    = len(results) - ok
    avg     = sum(r["diff_pct"] for r in results) / len(results)

    print(f"\n{'='*60}")
    print(f"Converter Diff Report  (threshold ≤{threshold}%)")
    print(f"{'='*60}")
    print(f"Files compared : {len(results)}")
    print(f"Within threshold : {ok}  |  Exceeding : {fail}")
    print(f"Average diff   : {avg:.1f}%")
    print(f"{'='*60}")
    print(f"{'File':<50} {'Diff%':>6}  {'ΔChars':>8}  {'Status':>8}")
    print(f"{'-'*50} {'-'*6}  {'-'*8}  {'-'*8}")
    for r in sorted(results, key=lambda x: -x["diff_pct"]):
        status = "OK" if r["ok"] else "REVIEW"
        delta  = f"+{r['char_delta']}" if r["char_delta"] >= 0 else str(r["char_delta"])
        print(f"{r['file']:<50} {r['diff_pct']:>5.1f}%  {delta:>8}  {status:>8}")
    print(f"{'='*60}\n")

    if fail:
        print(f"⚠️  {fail} file(s) vượt ngưỡng {threshold}% — kiểm tra thủ công")
    else:
        print(f"✅ Tất cả file trong ngưỡng {threshold}% — markitdown output acceptable")


def main():
    as_json   = "--json"      in sys.argv
    threshold = DEFAULT_THRESHOLD
    for arg in sys.argv[1:]:
        if arg.startswith("--threshold"):
            parts = arg.split("=")
            if len(parts) == 2:
                threshold = float(parts[1])

    results = compare_dirs(threshold=threshold)

    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_report(results, threshold=threshold)


if __name__ == "__main__":
    main()
