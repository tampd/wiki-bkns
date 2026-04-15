#!/usr/bin/env python3
"""
BKNS Agent Wiki — Diff Engine (PART 07)

Compares v0.3 snapshot vs v0.4 rebuild wiki pages.
Classifies each change as Improvement / Regression / Neutral.

Usage:
    python3 tools/wiki_diff.py \
        --v03 build/snapshots/v0.3-pre-upgrade-2026-04-13/wiki/products \
        --v04 wiki-v0.4/products \
        --html trienkhai/upgrade-v0.4/diff-report.html \
        --json trienkhai/upgrade-v0.4/diff-report.json

    # Quick text summary only:
    python3 tools/wiki_diff.py --v03 ... --v04 ...

Output:
    Improvements: new accurate information added
    Regressions:  correct information removed or changed to wrong
    Neutral:      rephrase, format, whitespace changes only
"""
import argparse
import difflib
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

VN_TZ = timezone(timedelta(hours=7))


# ── Markdown helpers ───────────────────────────────────────

def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter block from markdown."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].strip()
    return text.strip()


def extract_sections(text: str) -> dict[str, str]:
    """Split markdown into {heading: content} dict."""
    sections: dict[str, str] = {}
    current_heading = "__preamble__"
    current_lines: list[str] = []

    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = m.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    sections[current_heading] = "\n".join(current_lines).strip()
    return sections


def normalize_text(text: str) -> str:
    """Normalize for comparison: collapse whitespace, lowercase."""
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def extract_numbers(text: str) -> set[str]:
    """Extract all numeric sequences (prices, specs) for regression detection."""
    return set(re.findall(r"\b\d[\d,.]+\b", text))


# ── Change classification ──────────────────────────────────

def classify_change(old_text: str, new_text: str) -> dict:
    """Classify the nature of a change between old and new text.

    Returns:
        {
          "type": "improvement" | "regression" | "neutral" | "unchanged",
          "reason": str,
          "old_len": int,
          "new_len": int,
          "similarity": float,  # 0-1
          "numbers_lost": list[str],
          "numbers_added": list[str],
        }
    """
    old_norm = normalize_text(old_text)
    new_norm = normalize_text(new_text)

    if old_norm == new_norm:
        return {
            "type": "unchanged",
            "reason": "Identical content",
            "old_len": len(old_text),
            "new_len": len(new_text),
            "similarity": 1.0,
            "numbers_lost": [],
            "numbers_added": [],
        }

    # Similarity ratio
    sim = difflib.SequenceMatcher(None, old_norm, new_norm).ratio()

    old_nums = extract_numbers(old_text)
    new_nums = extract_numbers(new_text)
    numbers_lost = sorted(old_nums - new_nums)
    numbers_added = sorted(new_nums - old_nums)

    # Heuristics for classification
    # Regression signals: numbers lost, content significantly shorter, key phrases gone
    old_len = len(old_text.strip())
    new_len = len(new_text.strip())
    length_ratio = new_len / max(old_len, 1)

    if numbers_lost and not numbers_added and length_ratio < 0.9:
        change_type = "regression"
        reason = f"Numeric values lost: {', '.join(numbers_lost[:5])}"
    elif numbers_lost and length_ratio < 0.7:
        change_type = "regression"
        reason = f"Content significantly shorter ({old_len}→{new_len} chars), numbers lost: {numbers_lost[:3]}"
    elif not numbers_lost and numbers_added and length_ratio > 1.05:
        change_type = "improvement"
        reason = f"New numeric data added: {', '.join(numbers_added[:5])}"
    elif length_ratio > 1.2 and sim < 0.9:
        change_type = "improvement"
        reason = f"Content expanded ({old_len}→{new_len} chars)"
    elif length_ratio < 0.5:
        change_type = "regression"
        reason = f"Content severely reduced ({old_len}→{new_len} chars)"
    elif sim > 0.85:
        change_type = "neutral"
        reason = f"Minor rephrasing (similarity={sim:.2f})"
    else:
        change_type = "neutral"
        reason = f"Moderate changes (similarity={sim:.2f}, Δlen={new_len-old_len:+d})"

    return {
        "type": change_type,
        "reason": reason,
        "old_len": old_len,
        "new_len": new_len,
        "similarity": round(sim, 3),
        "numbers_lost": numbers_lost,
        "numbers_added": numbers_added,
    }


# ── Per-file diff ──────────────────────────────────────────

def diff_file(v03_path: Path, v04_path: Path) -> dict:
    """Compare a single wiki page (v0.3 vs v0.4)."""
    old_text = v03_path.read_text(encoding="utf-8") if v03_path.exists() else ""
    new_text = v04_path.read_text(encoding="utf-8") if v04_path.exists() else ""

    old_body = strip_frontmatter(old_text)
    new_body = strip_frontmatter(new_text)

    # Overall classification
    overall = classify_change(old_body, new_body)

    # Section-by-section diff
    old_sections = extract_sections(old_body)
    new_sections = extract_sections(new_body)
    all_headings = sorted(set(old_sections) | set(new_sections))

    section_diffs = []
    for heading in all_headings:
        old_sec = old_sections.get(heading, "")
        new_sec = new_sections.get(heading, "")
        change = classify_change(old_sec, new_sec)
        if change["type"] != "unchanged":
            section_diffs.append({
                "heading": heading,
                **change,
            })

    # Unified diff for HTML rendering
    old_lines = old_body.splitlines(keepends=True)
    new_lines = new_body.splitlines(keepends=True)
    unified = "".join(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"v0.3/{v03_path.name}",
        tofile=f"v0.4/{v04_path.name}",
        n=3,
    ))

    # Side-by-side HTML (word-level diff)
    differ = difflib.HtmlDiff(wrapcolumn=80)
    side_by_side_html = differ.make_table(
        old_lines, new_lines,
        fromdesc=f"v0.3 — {v03_path.name}",
        todesc=f"v0.4 — {v04_path.name}",
    )

    return {
        "file": v03_path.name if v03_path.exists() else v04_path.name,
        "exists_v03": v03_path.exists(),
        "exists_v04": v04_path.exists(),
        "overall": overall,
        "sections": section_diffs,
        "unified_diff": unified,
        "side_by_side_html": side_by_side_html,
    }


# ── Category-level diff ────────────────────────────────────

def diff_category(category: str, v03_root: Path, v04_root: Path) -> dict:
    """Diff all pages for a category."""
    v03_dir = v03_root / category
    v04_dir = v04_root / category

    v03_pages = {f.name for f in v03_dir.glob("*.md")} if v03_dir.exists() else set()
    v04_pages = {f.name for f in v04_dir.glob("*.md")} if v04_dir.exists() else set()
    all_pages = sorted(v03_pages | v04_pages)

    files = []
    counts = {"improvement": 0, "regression": 0, "neutral": 0, "unchanged": 0,
              "only_v03": 0, "only_v04": 0}

    for page in all_pages:
        v03_path = v03_dir / page
        v04_path = v04_dir / page
        result = diff_file(v03_path, v04_path)

        if not result["exists_v03"]:
            result["overall"]["type"] = "improvement"
            result["overall"]["reason"] = "New page in v0.4"
            counts["only_v04"] += 1
        elif not result["exists_v04"]:
            result["overall"]["type"] = "regression"
            result["overall"]["reason"] = "Page missing in v0.4"
            counts["only_v03"] += 1
        else:
            change_type = result["overall"]["type"]
            counts[change_type] = counts.get(change_type, 0) + 1

        files.append(result)

    total = sum(counts.values())
    regression_rate = round(counts["regression"] / max(total, 1) * 100, 1)
    improvement_rate = round(counts["improvement"] / max(total, 1) * 100, 1)

    return {
        "category": category,
        "pages_v03": len(v03_pages),
        "pages_v04": len(v04_pages),
        "counts": counts,
        "regression_rate_pct": regression_rate,
        "improvement_rate_pct": improvement_rate,
        "files": files,
    }


# ── HTML report ────────────────────────────────────────────

def generate_html_report(report: dict, output_path: Path) -> None:
    """Generate an HTML side-by-side diff report."""
    now_str = datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M")

    # Build page sections
    category_summaries = []
    page_sections = []

    for cat_result in report["categories"]:
        cat = cat_result["category"]
        counts = cat_result["counts"]
        status_emoji = "✅" if cat_result["regression_rate_pct"] == 0 else (
            "⚠️" if cat_result["regression_rate_pct"] < 30 else "❌"
        )
        category_summaries.append(
            f'<tr>'
            f'<td>{status_emoji} <b>{cat}</b></td>'
            f'<td>{cat_result["pages_v03"]}</td>'
            f'<td>{cat_result["pages_v04"]}</td>'
            f'<td style="color:green">+{counts.get("improvement", 0)}</td>'
            f'<td style="color:red">-{counts.get("regression", 0)}</td>'
            f'<td>{counts.get("neutral", 0)}</td>'
            f'<td>{counts.get("unchanged", 0)}</td>'
            f'<td>{cat_result["regression_rate_pct"]}%</td>'
            f'</tr>'
        )

        for file_result in cat_result["files"]:
            if file_result["overall"]["type"] == "unchanged":
                continue
            change_type = file_result["overall"]["type"]
            color = {"improvement": "#d4edda", "regression": "#f8d7da",
                     "neutral": "#fff3cd"}.get(change_type, "#fff")
            icon = {"improvement": "✅", "regression": "❌", "neutral": "🟡"}.get(change_type, "")

            page_sections.append(f"""
<div class="page-diff" style="background:{color};padding:12px;margin:8px 0;border-radius:6px">
    <h3>{icon} {cat}/{file_result['file']}
        <span style="font-size:12px;font-weight:normal;margin-left:8px">
            ({change_type.upper()}) — {file_result['overall']['reason']}
        </span>
    </h3>
    <div class="side-by-side" style="overflow-x:auto;font-size:12px">
        <table class="diff" style="width:100%">
            {file_result['side_by_side_html']}
        </table>
    </div>
</div>
""")

    overall = report["overall"]

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Wiki Diff Report — v0.3 vs v0.4 ({now_str})</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 1400px; margin: 0 auto; padding: 16px; }}
  h1 {{ color: #333; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #f5f5f5; }}
  .diff {{ font-family: monospace; font-size: 11px; }}
  .diff_header {{ background: #e8e8e8 !important; }}
  .diff_add td {{ background: #e6ffe6 !important; }}
  .diff_chg td {{ background: #ffffcc !important; }}
  .diff_sub td {{ background: #ffe6e6 !important; }}
  .summary-box {{ background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 24px; }}
</style>
</head>
<body>
<h1>📊 Wiki Diff Report — v0.3 vs v0.4</h1>
<p>Generated: {now_str} | Snapshot: {report.get('v03_path', 'v0.3')} → {report.get('v04_path', 'v0.4')}</p>

<div class="summary-box">
  <h2>Overall Summary</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Total pages compared</td><td>{overall['total_pages']}</td></tr>
    <tr><td style="color:green">✅ Improvements</td><td>{overall['improvement']}</td></tr>
    <tr><td style="color:red">❌ Regressions</td><td>{overall['regression']}</td></tr>
    <tr><td style="color:orange">🟡 Neutral changes</td><td>{overall['neutral']}</td></tr>
    <tr><td>⬜ Unchanged</td><td>{overall['unchanged']}</td></tr>
    <tr><td><b>Regression rate</b></td>
        <td style="color:{'red' if overall['regression_rate_pct'] > 10 else 'green'}">
            <b>{overall['regression_rate_pct']}%</b>
        </td></tr>
  </table>
  {'<p style="color:green;font-weight:bold">✅ PASS: Regression rate < 10%</p>'
   if overall['regression_rate_pct'] < 10 else
   '<p style="color:red;font-weight:bold">❌ FAIL: Regression rate ≥ 10% — investigate before promoting</p>'}
</div>

<h2>Category Summary</h2>
<table>
  <tr><th>Category</th><th>Pages v0.3</th><th>Pages v0.4</th>
      <th>+Improvement</th><th>-Regression</th><th>~Neutral</th>
      <th>=Unchanged</th><th>Regression%</th></tr>
  {''.join(category_summaries)}
</table>

<h2>Page-by-Page Diff (changed pages only)</h2>
{''.join(page_sections) or '<p style="color:green">No changes detected.</p>'}

</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"HTML report → {output_path}")


# ── Main ───────────────────────────────────────────────────

def main():
    WORKSPACE = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(description="PART 07 — Wiki Diff Engine")
    parser.add_argument("--v03", default=str(
        WORKSPACE / "build/snapshots/v0.3-pre-upgrade-2026-04-13/wiki/products"),
        help="Path to v0.3 wiki products dir")
    parser.add_argument("--v04", default=str(WORKSPACE / "wiki-v0.4/products"),
        help="Path to v0.4 wiki products dir")
    parser.add_argument("--html", default=str(
        WORKSPACE / "trienkhai/upgrade-v0.4/diff-report.html"),
        help="Output HTML report path")
    parser.add_argument("--json", default=str(
        WORKSPACE / "trienkhai/upgrade-v0.4/diff-report.json"),
        help="Output JSON report path")
    parser.add_argument("--categories", nargs="*",
        default=["hosting", "vps", "ssl", "ten-mien", "email", "server", "software"],
        help="Categories to diff")
    args = parser.parse_args()

    v03_root = Path(args.v03)
    v04_root = Path(args.v04)

    if not v03_root.exists():
        print(f"ERROR: v0.3 dir not found: {v03_root}")
        sys.exit(1)
    if not v04_root.exists():
        print(f"ERROR: v0.4 dir not found: {v04_root}")
        print("       Run regression_test.py --full first to generate wiki-v0.4/")
        sys.exit(1)

    print(f"\nDiff: {v03_root}")
    print(f"  vs: {v04_root}\n")

    category_results = []
    total_counts = {"improvement": 0, "regression": 0, "neutral": 0, "unchanged": 0}

    for category in args.categories:
        print(f"  [{category}]", end=" ", flush=True)
        result = diff_category(category, v03_root, v04_root)
        category_results.append(result)

        for k, v in result["counts"].items():
            if k in total_counts:
                total_counts[k] += v

        reg_pct = result["regression_rate_pct"]
        status = "✅" if reg_pct == 0 else ("⚠️" if reg_pct < 30 else "❌")
        print(f"{status} +{result['counts'].get('improvement', 0)} "
              f"-{result['counts'].get('regression', 0)} "
              f"~{result['counts'].get('neutral', 0)} "
              f"={result['counts'].get('unchanged', 0)}"
              f"  ({reg_pct}% regression)")

    total_pages = sum(v for v in total_counts.values())
    overall = {
        **total_counts,
        "total_pages": total_pages,
        "regression_rate_pct": round(
            total_counts["regression"] / max(total_pages, 1) * 100, 1
        ),
        "improvement_rate_pct": round(
            total_counts["improvement"] / max(total_pages, 1) * 100, 1
        ),
    }

    print(f"\nOVERALL: +{overall['improvement']} improvements, "
          f"-{overall['regression']} regressions, "
          f"~{overall['neutral']} neutral, "
          f"={overall['unchanged']} unchanged")
    print(f"Regression rate: {overall['regression_rate_pct']}%")

    if overall["regression_rate_pct"] < 10:
        print("✅ PASS: regression rate < 10%")
    else:
        print("❌ FAIL: regression rate ≥ 10% — investigate before promoting to production")

    report = {
        "generated_at": datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M"),
        "v03_path": str(v03_root),
        "v04_path": str(v04_root),
        "overall": overall,
        "categories": category_results,
    }

    # Save JSON (without side_by_side_html for size)
    json_report = {
        "generated_at": report["generated_at"],
        "v03_path": report["v03_path"],
        "v04_path": report["v04_path"],
        "overall": overall,
        "categories": [
            {
                "category": r["category"],
                "pages_v03": r["pages_v03"],
                "pages_v04": r["pages_v04"],
                "counts": r["counts"],
                "regression_rate_pct": r["regression_rate_pct"],
                "improvement_rate_pct": r["improvement_rate_pct"],
                "files": [
                    {k: v for k, v in f.items() if k not in ("unified_diff", "side_by_side_html")}
                    for f in r["files"]
                ],
            }
            for r in category_results
        ],
    }
    json_path = Path(args.json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(json_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON report → {json_path}")

    # Generate HTML
    generate_html_report(report, Path(args.html))


if __name__ == "__main__":
    main()
