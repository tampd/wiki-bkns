#!/usr/bin/env python3
"""
BKNS Agent Wiki — A/B Test: gemini-2.5-pro vs gemini-3.1-pro-preview (PART 04)

So sánh 2 model trên tập test PART 01 (5 categories × 1 raw file).
Kết quả ghi vào trienkhai/upgrade-v0.4/ab-test-extract.md và ab-test-compile.md.

Usage:
    # Bước 1: Verify model availability
    python3 tools/ab_test_models.py verify

    # Bước 3: A/B test extract
    python3 tools/ab_test_models.py extract

    # Bước 4: A/B test compile
    python3 tools/ab_test_models.py compile

    # Chạy cả 3
    python3 tools/ab_test_models.py all

Cost estimate per run:
    extract: ~5 files × 2 models × ~0.01$ = ~$0.10
    compile: ~5 categories × 2 models × ~0.05$ = ~$0.50
"""
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from lib.config import (
    WORKSPACE, MODEL_PRO, MODEL_PRO_NEW,
    CLAIMS_APPROVED_DIR, RAW_CRAWL_DIR,
)
from lib.gemini import generate
from tools.check_cost_budget import assert_within_budget

WIKI_ROOT = WORKSPACE
AB_OUT_DIR = WIKI_ROOT / "trienkhai" / "upgrade-v0.4"

# ── Test set categories ─────────────────────────────────────────────────────
# Maps category slug → raw/website-crawl file pattern + approved claims subdir
TEST_CATEGORIES = {
    "hosting": {
        "raw_pattern": "hosting-2026*.md",
        "claims_dir": "products/hosting",
    },
    "vps": {
        "raw_pattern": "cloud-vps-amd-web-*.md",
        "claims_dir": "products/vps",
    },
    "ssl": {
        "raw_pattern": "ssl-*.md",
        "claims_dir": "products/ssl",
    },
    "ten-mien": {
        "raw_pattern": "dang-ky-ten-mien-*.md",
        "claims_dir": "products/ten-mien",
    },
    "email": {
        "raw_pattern": "email-hosting-web-*.md",
        "claims_dir": "products/email",
    },
}

EXTRACT_PROMPT_TEMPLATE = """Bạn là chuyên gia trích xuất thông tin sản phẩm BKNS.

Từ nội dung dưới đây, hãy trích xuất MỌI facts về sản phẩm/dịch vụ.
Mỗi fact = 1 JSON object trong mảng "claims".

Yêu cầu:
- Mỗi claim có: entity_name, attribute, value, unit (nếu có), confidence (0-1)
- confidence: 1.0 = số liệu rõ ràng, 0.7 = suy diễn, 0.5 = không rõ
- Bao gồm: giá, thông số kỹ thuật, tính năng, chính sách, so sánh

Trả về JSON THUẦN (không markdown):
{{"claims": [{{"entity_name": "...", "attribute": "...", "value": "...", "unit": null, "confidence": 0.9}}, ...]}}

Nội dung:
---
{content}
---"""

COMPILE_PROMPT_TEMPLATE = """Bạn là chuyên gia biên soạn wiki BKNS.

Từ các claims sau, hãy compile thành 1 wiki page Markdown hoàn chỉnh.
Yêu cầu:
- Frontmatter YAML với title, category, updated
- Nội dung rõ ràng, có bảng giá nếu có
- Không thêm thông tin ngoài claims
- Self-review: kiểm tra số liệu trước khi kết thúc

Claims:
---
{claims_text}
---

Category: {category}"""


# ── Helpers ─────────────────────────────────────────────────────────────────

def find_raw_file(category: str) -> Path | None:
    """Find the first matching raw file for a category."""
    pattern = TEST_CATEGORIES[category]["raw_pattern"]
    matches = sorted(RAW_CRAWL_DIR.glob(pattern))
    return matches[0] if matches else None


def find_claims_for_category(category: str, max_claims: int = 10) -> list[dict]:
    """Load up to max_claims YAML files from approved claims for a category."""
    claims_subdir = CLAIMS_APPROVED_DIR / TEST_CATEGORIES[category]["claims_dir"]
    if not claims_subdir.exists():
        return []
    claim_files = sorted(claims_subdir.glob("*.yaml"))[:max_claims]
    claims = []
    for cf in claim_files:
        try:
            data = yaml.safe_load(cf.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                claims.append(data)
        except Exception:
            continue
    return claims


def run_model(prompt: str, model: str, skill: str) -> dict:
    """Run a single generate() call and return metrics."""
    start = time.time()
    try:
        result = generate(
            prompt=prompt,
            model=model,
            skill=skill,
            temperature=0.1,
            max_output_tokens=32768,  # increased: 2.5-pro thinking tokens reduce effective budget
        )
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "ok": True,
            "text": result["text"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cached_tokens": result.get("cached_tokens", 0),
            "cost_usd": result["cost_usd"],
            "elapsed_ms": elapsed_ms,
            "model": model,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "model": model,
            "cost_usd": 0,
            "elapsed_ms": int((time.time() - start) * 1000),
        }


def count_claims_in_json(text: str) -> int:
    """Try to parse JSON response and count extracted claims."""
    try:
        text = text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        data = json.loads(text)
        if isinstance(data, dict) and "claims" in data:
            return len(data["claims"])
        if isinstance(data, list):
            return len(data)
    except (json.JSONDecodeError, ValueError):
        pass
    return -1  # parse failed


# ── Bước 1: Verify ──────────────────────────────────────────────────────────

def cmd_verify():
    """Bước 1: Verify gemini-3.1-pro-preview is accessible."""
    print("=" * 60)
    print("BƯỚC 1 — Verify model availability")
    print("=" * 60)

    for model in [MODEL_PRO, MODEL_PRO_NEW]:
        print(f"\nTesting: {model}")
        try:
            result = generate(
                prompt="Trả lời ngắn: 2+2=? Chỉ trả về số.",
                model=model,
                skill="ab-test-verify",
                temperature=0.0,
                max_output_tokens=512,  # 32 quá nhỏ — thinking tokens của 2.5-pro chiếm hết quota
            )
            print(f"  ✅ OK — response: '{result['text'].strip()}'")
            print(f"     tokens in={result['input_tokens']} out={result['output_tokens']}"
                  f" cost=${result['cost_usd']:.6f}")
        except Exception as e:
            print(f"  ❌ FAIL — {e}")

    print("\nKết quả verify:")
    print("  Nếu cả 2 đều OK → tiếp tục extract + compile A/B test")
    print("  Nếu 3.1-pro-preview FAIL → thử region us-east5 (đổi GOOGLE_CLOUD_LOCATION)")


# ── Bước 3: Extract A/B ─────────────────────────────────────────────────────

def cmd_extract_ab():
    """Bước 3: A/B test extract-claims trên 5 test files."""
    print("=" * 60)
    print("BƯỚC 3 — A/B Test: extract-claims")
    print(f"  Model A (cũ): {MODEL_PRO}")
    print(f"  Model B (mới): {MODEL_PRO_NEW}")
    print("=" * 60)

    assert_within_budget(skill="ab-test-extract", max_per_build=5.00)

    results = []
    for category, cfg in TEST_CATEGORIES.items():
        raw_file = find_raw_file(category)
        if raw_file is None:
            print(f"\n[{category}] ⚠️ raw file not found (pattern: {cfg['raw_pattern']}), skip")
            continue

        content = raw_file.read_text(encoding="utf-8")
        # Trim content to keep costs reasonable (~20K chars max)
        content_trimmed = content[:20_000]
        prompt = EXTRACT_PROMPT_TEMPLATE.format(content=content_trimmed)
        file_size_kb = round(len(content) / 1024, 1)

        print(f"\n[{category}] {raw_file.name} ({file_size_kb} KB)")

        row = {"category": category, "raw_file": raw_file.name}
        for label, model in [("2.5-pro", MODEL_PRO), ("3.1-preview", MODEL_PRO_NEW)]:
            print(f"  → {label} ...", end="", flush=True)
            m = run_model(prompt, model, "ab-test-extract")  # uses max_output_tokens=8192 via run_model
            n_claims = count_claims_in_json(m.get("text", "")) if m["ok"] else -1
            status = f"✅ {n_claims} claims" if m["ok"] and n_claims >= 0 else (
                f"⚠️ parse fail (ok={m['ok']})" if m["ok"] else f"❌ {m.get('error', '')[:60]}"
            )
            print(f" {status} | in={m.get('input_tokens',0)} out={m.get('output_tokens',0)}"
                  f" ${m.get('cost_usd',0):.4f} {m.get('elapsed_ms',0)}ms")
            row[label] = {
                "ok": m["ok"],
                "n_claims": n_claims,
                "input_tokens": m.get("input_tokens", 0),
                "output_tokens": m.get("output_tokens", 0),
                "cost_usd": m.get("cost_usd", 0),
                "elapsed_ms": m.get("elapsed_ms", 0),
            }
            if m["ok"]:
                # Save raw output for manual inspection
                out_dir = AB_OUT_DIR / f"ab-claims-{label.replace('.', '-')}"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / f"{category}.json"
                out_file.write_text(m["text"], encoding="utf-8")
        results.append(row)

    _save_extract_report(results)
    print(f"\n✅ Báo cáo: {AB_OUT_DIR / 'ab-test-extract.md'}")


def _save_extract_report(results: list[dict]):
    """Save ab-test-extract.md report."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "---",
        "artifact: ab-test-extract",
        "part: 04",
        f"generated: {ts}",
        f"model_old: {MODEL_PRO}",
        f"model_new: {MODEL_PRO_NEW}",
        "---",
        "",
        "# A/B Test — Extract Claims",
        "",
        f"> Chạy: {ts}  ",
        f"> Model cũ: `{MODEL_PRO}`  ",
        f"> Model mới: `{MODEL_PRO_NEW}`",
        "",
        "## Kết Quả Theo Category",
        "",
        "| Category | File | Claims (cũ) | Claims (mới) | Δ Claims | Cost cũ | Cost mới | Δ Cost% |",
        "|---|---|---|---|---|---|---|---|",
    ]
    total_cost_old = 0.0
    total_cost_new = 0.0
    total_claims_old = 0
    total_claims_new = 0

    for row in results:
        cat = row["category"]
        fname = row.get("raw_file", "N/A")
        old = row.get("2.5-pro", {})
        new = row.get("3.1-preview", {})
        nc_old = old.get("n_claims", -1)
        nc_new = new.get("n_claims", -1)
        c_old = old.get("cost_usd", 0)
        c_new = new.get("cost_usd", 0)
        delta_claims = (nc_new - nc_old) if nc_old >= 0 and nc_new >= 0 else "N/A"
        delta_cost_pct = (
            f"+{round((c_new - c_old) / c_old * 100, 1)}%"
            if c_old > 0 else "N/A"
        )
        lines.append(
            f"| {cat} | {fname} | {nc_old} | {nc_new} | {delta_claims} "
            f"| ${c_old:.4f} | ${c_new:.4f} | {delta_cost_pct} |"
        )
        if nc_old >= 0:
            total_claims_old += nc_old
        if nc_new >= 0:
            total_claims_new += nc_new
        total_cost_old += c_old
        total_cost_new += c_new

    delta_c_pct = (
        f"+{round((total_cost_new - total_cost_old) / total_cost_old * 100, 1)}%"
        if total_cost_old > 0 else "N/A"
    )
    lines += [
        f"| **TOTAL** | — | **{total_claims_old}** | **{total_claims_new}** "
        f"| **{total_claims_new - total_claims_old}** "
        f"| **${total_cost_old:.4f}** | **${total_cost_new:.4f}** | **{delta_c_pct}** |",
        "",
        "## Token Usage",
        "",
        "| Category | In (cũ) | Out (cũ) | In (mới) | Out (mới) | Elapsed cũ | Elapsed mới |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in results:
        cat = row["category"]
        old = row.get("2.5-pro", {})
        new = row.get("3.1-preview", {})
        lines.append(
            f"| {cat} | {old.get('input_tokens',0)} | {old.get('output_tokens',0)} "
            f"| {new.get('input_tokens',0)} | {new.get('output_tokens',0)} "
            f"| {old.get('elapsed_ms',0)}ms | {new.get('elapsed_ms',0)}ms |"
        )

    lines += [
        "",
        "## Acceptance Criteria",
        "",
        "| Criteria | Result |",
        "|---|---|",
        f"| Claims mới ≥ claims cũ | {'✅' if total_claims_new >= total_claims_old else '❌'} "
        f"({total_claims_old} → {total_claims_new}) |",
        f"| Cost tăng ≤ 35% | {'✅' if total_cost_old == 0 or (total_cost_new - total_cost_old) / total_cost_old <= 0.35 else '❌'} ({delta_c_pct}) |",
        "",
        "## Verdict",
        "",
        "<!-- Điền sau khi review manual: GO / NO-GO / NEEDS-ADJUSTMENT -->",
        "**Verdict**: _(chưa review)_",
        "",
        "## Raw Output",
        f"- Claims gemini-2.5-pro: `trienkhai/upgrade-v0.4/ab-claims-2-5-pro/`",
        f"- Claims gemini-3.1-pro-preview: `trienkhai/upgrade-v0.4/ab-claims-3-1-preview/`",
        "",
        "## Notes",
        "*(Điền nhận xét thủ công sau khi đọc output JSON)*",
    ]

    out = AB_OUT_DIR / "ab-test-extract.md"
    out.write_text("\n".join(lines), encoding="utf-8")


# ── Bước 4: Compile A/B ─────────────────────────────────────────────────────

def cmd_compile_ab():
    """Bước 4: A/B test compile-wiki trên 5 test categories."""
    print("=" * 60)
    print("BƯỚC 4 — A/B Test: compile-wiki")
    print(f"  Model A (cũ): {MODEL_PRO}")
    print(f"  Model B (mới): {MODEL_PRO_NEW}")
    print("=" * 60)

    assert_within_budget(skill="ab-test-compile", max_per_build=10.00)

    results = []
    for category, cfg in TEST_CATEGORIES.items():
        claims = find_claims_for_category(category, max_claims=8)
        if not claims:
            print(f"\n[{category}] ⚠️ no approved claims found, skip")
            continue

        claims_text = yaml.dump(claims, allow_unicode=True, default_flow_style=False)
        prompt = COMPILE_PROMPT_TEMPLATE.format(
            claims_text=claims_text[:15_000],
            category=category,
        )
        print(f"\n[{category}] {len(claims)} claims")

        row = {"category": category, "n_claims_input": len(claims)}
        for label, model in [("2.5-pro", MODEL_PRO), ("3.1-preview", MODEL_PRO_NEW)]:
            print(f"  → {label} ...", end="", flush=True)
            m = run_model(prompt, model, "ab-test-compile")
            output_len = len(m.get("text", ""))
            status = (f"✅ {output_len} chars" if m["ok"]
                      else f"❌ {m.get('error', '')[:60]}")
            print(f" {status} | in={m.get('input_tokens',0)} out={m.get('output_tokens',0)}"
                  f" ${m.get('cost_usd',0):.4f} {m.get('elapsed_ms',0)}ms")
            row[label] = {
                "ok": m["ok"],
                "output_chars": output_len,
                "input_tokens": m.get("input_tokens", 0),
                "output_tokens": m.get("output_tokens", 0),
                "cost_usd": m.get("cost_usd", 0),
                "elapsed_ms": m.get("elapsed_ms", 0),
            }
            if m["ok"]:
                out_dir = AB_OUT_DIR / f"ab-compile-{label.replace('.', '-')}"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{category}.md").write_text(m["text"], encoding="utf-8")
        results.append(row)

    _save_compile_report(results)
    print(f"\n✅ Báo cáo: {AB_OUT_DIR / 'ab-test-compile.md'}")


def _save_compile_report(results: list[dict]):
    """Save ab-test-compile.md report."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "---",
        "artifact: ab-test-compile",
        "part: 04",
        f"generated: {ts}",
        f"model_old: {MODEL_PRO}",
        f"model_new: {MODEL_PRO_NEW}",
        "---",
        "",
        "# A/B Test — Compile Wiki",
        "",
        f"> Chạy: {ts}  ",
        f"> Model cũ: `{MODEL_PRO}`  ",
        f"> Model mới: `{MODEL_PRO_NEW}`",
        "",
        "## Kết Quả Theo Category",
        "",
        "| Category | Claims in | Output (cũ) | Output (mới) | Cost cũ | Cost mới | Δ Cost% |",
        "|---|---|---|---|---|---|---|",
    ]
    total_cost_old = 0.0
    total_cost_new = 0.0

    for row in results:
        cat = row["category"]
        n_in = row.get("n_claims_input", 0)
        old = row.get("2.5-pro", {})
        new = row.get("3.1-preview", {})
        c_old = old.get("cost_usd", 0)
        c_new = new.get("cost_usd", 0)
        delta_cost_pct = (
            f"+{round((c_new - c_old) / c_old * 100, 1)}%"
            if c_old > 0 else "N/A"
        )
        lines.append(
            f"| {cat} | {n_in} | {old.get('output_chars',0):,} chars "
            f"| {new.get('output_chars',0):,} chars "
            f"| ${c_old:.4f} | ${c_new:.4f} | {delta_cost_pct} |"
        )
        total_cost_old += c_old
        total_cost_new += c_new

    delta_total_pct = (
        f"+{round((total_cost_new - total_cost_old) / total_cost_old * 100, 1)}%"
        if total_cost_old > 0 else "N/A"
    )
    lines += [
        f"| **TOTAL** | — | — | — | **${total_cost_old:.4f}** | **${total_cost_new:.4f}** "
        f"| **{delta_total_pct}** |",
        "",
        "## Manual Review Checklist",
        "",
        "So sánh output của 2 model cho mỗi category:",
        "",
    ]
    for row in results:
        cat = row["category"]
        lines += [
            f"### {cat}",
            f"- [ ] Thông tin nào bị mất ở model mới?",
            f"- [ ] Có thông tin sai mới nào không?",
            f"- [ ] Self-review marker `[OK]/[CORRECTION]` có đúng format không?",
            f"- Files: `ab-compile-2-5-pro/{cat}.md` vs `ab-compile-3-1-preview/{cat}.md`",
            "",
        ]

    lines += [
        "## Acceptance Criteria",
        "",
        "| Criteria | Result |",
        "|---|---|",
        f"| Cost tăng ≤ 35% | {'✅' if total_cost_old == 0 or (total_cost_new - total_cost_old) / total_cost_old <= 0.35 else '❌'} ({delta_total_pct}) |",
        "| Không mất thông tin quan trọng | _(cần manual review)_ |",
        "| Không có thông tin sai mới | _(cần manual review)_ |",
        "",
        "## Verdict",
        "",
        "**Verdict**: _(chưa review — điền GO / NO-GO / NEEDS-ADJUSTMENT sau khi đọc output)_",
    ]

    out = AB_OUT_DIR / "ab-test-compile.md"
    out.write_text("\n".join(lines), encoding="utf-8")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PART 04 A/B Test: gemini-2.5-pro vs gemini-3.1-pro-preview"
    )
    parser.add_argument(
        "task",
        choices=["verify", "extract", "compile", "all"],
        help="Subcommand: verify=endpoint check, extract=A/B extract, compile=A/B compile, all=all 3",
    )
    args = parser.parse_args()

    if args.task in ("verify", "all"):
        cmd_verify()
    if args.task in ("extract", "all"):
        cmd_extract_ab()
    if args.task in ("compile", "all"):
        cmd_compile_ab()


if __name__ == "__main__":
    main()
