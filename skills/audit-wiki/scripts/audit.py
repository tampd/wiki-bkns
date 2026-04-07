#!/usr/bin/env python3
"""
BKNS Wiki — Atomic Fact Audit (HaluCheck-inspired)

Decomposes compiled wiki pages into atomic facts and verifies
each fact against the claims database.

Inspired by HaluCheck (NeurIPS 2024) and AutoFactNLI.

Usage:
    python3 scripts/audit.py                              # Audit all wiki pages
    python3 scripts/audit.py wiki/products/hosting         # Audit specific category
    python3 scripts/audit.py wiki/products/vps/bang-gia.md # Audit specific page
"""
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    WIKI_DIR, CLAIMS_APPROVED_DIR, LOGS_DIR,
    MODEL_FLASH,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.utils import (
    ensure_dir, now_iso, today_str, parse_frontmatter, read_text_safe,
)

VN_TZ = timezone(timedelta(hours=7))


# ── Atomic Fact Decomposition (via Gemini) ─────────────────
DECOMPOSE_PROMPT = """Bạn là fact-checker chuyên nghiệp.

Phân tích trang wiki sau và tách thành từng "atomic fact" — mỗi fact là 1 câu khẳng định đơn lẻ, có thể verify được.

TRANG WIKI:
{content}

QUY TẮC:
- Mỗi atomic fact chỉ chứa 1 thông tin DUY NHẤT
- Ưu tiên extract: giá cả, thông số kỹ thuật, chính sách, tên sản phẩm
- Bỏ qua: tiêu đề trang, link liên kết, footer, text "Đang cập nhật"
- Format giá: giữ nguyên số (ví dụ: 29000, không format) 

OUTPUT (JSON array):
[
  {{
    "fact": "VPS EPYC 1 có giá 165.000 VND/tháng",
    "type": "price",
    "entity_hint": "product.vps.epyc_1",
    "attribute_hint": "monthly_price",
    "value_hint": "165000"
  }},
  {{
    "fact": "Hosting BKCP01 có 1 Core CPU",
    "type": "spec",
    "entity_hint": "product.hosting.bkcp01",
    "attribute_hint": "cpu_cores",
    "value_hint": "1 Core"
  }}
]

Trả về TẤT CẢ facts, không bỏ sót."""


def decompose_page(content: str) -> list[dict]:
    """Break wiki page into atomic facts using Gemini."""
    if len(content.strip()) < 100:
        return []
    
    # Remove frontmatter
    _, body = parse_frontmatter(content)
    if len(body.strip()) < 50:
        return []
    
    prompt = DECOMPOSE_PROMPT.format(content=body[:20000])
    
    try:
        result = generate(
            prompt=prompt,
            model=MODEL_FLASH,
            skill="audit-wiki",
            temperature=0.1,
            max_output_tokens=8192,
        )
    except Exception as e:
        print(f"  ⚠️ Decompose error: {e}")
        return []
    
    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    
    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except (json.JSONDecodeError, AttributeError):
        pass
    
    return []


# ── Ground Truth Verification ──────────────────────────────

def load_claims_index() -> dict:
    """Load all approved claims indexed by entity_id::attribute."""
    index = {}
    for yaml_file in CLAIMS_APPROVED_DIR.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                claim = yaml.safe_load(f)
            if claim and isinstance(claim, dict):
                key = f"{claim['entity_id']}::{claim['attribute']}"
                # Prefer ground_truth over other claims
                if key not in index or claim.get("confidence") == "ground_truth":
                    index[key] = claim
        except Exception:
            continue
    return index


def _normalize_value(val) -> str:
    """Normalize a value for comparison."""
    s = str(val).strip().lower()
    # Remove currency symbols and formatting
    s = re.sub(r'[đ₫vndk\s,.]', '', s)
    # Remove "/ tháng", "/năm" etc
    s = re.sub(r'/\s*(tháng|năm|ngày)', '', s)
    return s


def verify_fact(fact: dict, claims_index: dict) -> dict:
    """Verify a single atomic fact against claims database.
    
    Returns: {status: grounded|hallucinated|distorted|unverifiable, ...}
    """
    entity_hint = fact.get("entity_hint", "")
    attribute_hint = fact.get("attribute_hint", "")
    value_hint = fact.get("value_hint", "")
    
    # Try direct lookup
    key = f"{entity_hint}::{attribute_hint}"
    claim = claims_index.get(key)
    
    if claim is None:
        # Try fuzzy match on entity_id
        for k, c in claims_index.items():
            if entity_hint and entity_hint in k and attribute_hint in k:
                claim = c
                break
    
    if claim is None:
        return {
            "fact": fact["fact"],
            "status": "unverifiable",
            "detail": f"No matching claim for {entity_hint}.{attribute_hint}",
        }
    
    # Compare values
    claim_val = _normalize_value(claim.get("value", ""))
    fact_val = _normalize_value(value_hint)
    
    if not fact_val or not claim_val:
        return {
            "fact": fact["fact"],
            "status": "unverifiable",
            "detail": "Cannot extract comparable values",
        }
    
    # Numeric comparison
    try:
        cv = float(re.sub(r'[^0-9.]', '', claim_val))
        fv = float(re.sub(r'[^0-9.]', '', fact_val))
        
        if cv == fv:
            return {
                "fact": fact["fact"],
                "status": "grounded",
                "detail": f"Matches claim: {claim.get('value')} (confidence: {claim.get('confidence')})",
                "confidence": claim.get("confidence", "unknown"),
            }
        else:
            diff_pct = abs(cv - fv) / cv * 100 if cv else 100
            if diff_pct < 1:  # Rounding tolerance
                return {
                    "fact": fact["fact"],
                    "status": "grounded",
                    "detail": f"Close match (~{diff_pct:.1f}%): claim={claim.get('value')}",
                }
            else:
                return {
                    "fact": fact["fact"],
                    "status": "distorted",
                    "detail": f"Value mismatch: wiki says '{value_hint}', claim says '{claim.get('value')}' (diff {diff_pct:.1f}%)",
                    "claim_value": claim.get("value"),
                    "wiki_value": value_hint,
                }
    except (ValueError, TypeError):
        # String comparison
        if claim_val == fact_val or claim_val in fact_val or fact_val in claim_val:
            return {
                "fact": fact["fact"],
                "status": "grounded",
                "detail": f"Text matches claim: {claim.get('value')}",
            }
        else:
            return {
                "fact": fact["fact"],
                "status": "distorted",
                "detail": f"Text mismatch: wiki='{value_hint}', claim='{claim.get('value')}'",
            }


# ── Page Audit ─────────────────────────────────────────────

def audit_page(page_path: Path, claims_index: dict) -> dict:
    """Full audit of a single wiki page."""
    content = read_text_safe(str(page_path))
    if not content or len(content.strip()) < 100:
        return {
            "page": str(page_path.relative_to(WIKI_DIR)),
            "total_facts": 0,
            "score": 0,
            "status": "skipped",
            "detail": "Page too short or empty",
        }
    
    fm, body = parse_frontmatter(content)
    
    # Skip skeleton pages
    if "Đang cập nhật" in body and len(body.strip()) < 200:
        return {
            "page": str(page_path.relative_to(WIKI_DIR)),
            "total_facts": 0,
            "score": 0,
            "status": "skeleton",
            "detail": "Skeleton page — no content to audit",
        }
    
    # Decompose into atomic facts
    facts = decompose_page(content)
    
    if not facts:
        return {
            "page": str(page_path.relative_to(WIKI_DIR)),
            "total_facts": 0,
            "score": 100,
            "status": "no_facts",
            "detail": "No verifiable facts found",
        }
    
    # Verify each fact
    fact_results = []
    for fact in facts:
        result = verify_fact(fact, claims_index)
        fact_results.append(result)
    
    # Calculate scores
    grounded = len([r for r in fact_results if r["status"] == "grounded"])
    hallucinated = len([r for r in fact_results if r["status"] == "hallucinated"])
    distorted = len([r for r in fact_results if r["status"] == "distorted"])
    unverifiable = len([r for r in fact_results if r["status"] == "unverifiable"])
    total = len(fact_results)
    
    verifiable = total - unverifiable
    score = (grounded / verifiable * 100) if verifiable > 0 else 100
    
    return {
        "page": str(page_path.relative_to(WIKI_DIR)),
        "total_facts": total,
        "grounded": grounded,
        "hallucinated": hallucinated,
        "distorted": distorted,
        "unverifiable": unverifiable,
        "score": round(score, 1),
        "status": "pass" if score >= 95 else ("warning" if score >= 80 else "fail"),
        "facts": fact_results,
    }


# ── Main ───────────────────────────────────────────────────

def audit_wiki(target: str = None) -> dict:
    """Run audit on wiki pages."""
    print("🔍 Loading claims index...")
    claims_index = load_claims_index()
    print(f"   Indexed {len(claims_index)} claims")
    
    # Determine pages to audit
    pages = []
    if target:
        target_path = Path(target) if Path(target).is_absolute() else WIKI_DIR / target
        if target_path.is_file():
            pages = [target_path]
        elif target_path.is_dir():
            pages = sorted(target_path.rglob("*.md"))
    else:
        pages = sorted(WIKI_DIR.rglob("*.md"))
    
    # Filter out drafts
    pages = [p for p in pages if ".drafts" not in str(p)]
    print(f"   Auditing {len(pages)} pages\n")
    
    all_results = []
    total_cost = 0
    
    for page in pages:
        rel = page.relative_to(WIKI_DIR)
        print(f"  📄 {rel}...", end=" ", flush=True)
        
        result = audit_page(page, claims_index)
        all_results.append(result)
        
        status_icon = {
            "pass": "✅",
            "warning": "⚠️",
            "fail": "❌",
            "skeleton": "💀",
            "skipped": "⏭️",
            "no_facts": "📝",
        }.get(result["status"], "❓")
        
        print(f"{status_icon} score={result['score']} ({result['total_facts']} facts)")
    
    # Summary
    passed = len([r for r in all_results if r["status"] == "pass"])
    warned = len([r for r in all_results if r["status"] == "warning"])
    failed = len([r for r in all_results if r["status"] == "fail"])
    skeletons = len([r for r in all_results if r["status"] == "skeleton"])
    
    avg_score = sum(r["score"] for r in all_results if r["total_facts"] > 0) / max(1, len([r for r in all_results if r["total_facts"] > 0]))
    
    # Save report
    ensure_dir(LOGS_DIR / "audit")
    report = {
        "ts": now_iso(),
        "total_pages": len(pages),
        "passed": passed,
        "warnings": warned,
        "failed": failed,
        "skeletons": skeletons,
        "avg_score": round(avg_score, 1),
        "pages": all_results,
    }
    
    report_path = LOGS_DIR / "audit" / f"audit-{today_str()}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n{'═' * 50}")
    print(f"📊 Audit Summary")
    print(f"   Total pages: {len(pages)}")
    print(f"   ✅ Pass: {passed} | ⚠️ Warning: {warned} | ❌ Fail: {failed} | 💀 Skeleton: {skeletons}")
    print(f"   Average score: {avg_score:.1f}/100")
    print(f"   Report: {report_path}")
    
    if failed:
        print(f"\n🚨 FAILED PAGES:")
        for r in all_results:
            if r["status"] == "fail":
                distorted = [f for f in r.get("facts", []) if f["status"] == "distorted"]
                print(f"   ❌ {r['page']} — score={r['score']}, {len(distorted)} distorted facts")
                for d in distorted[:3]:
                    print(f"      → {d['detail']}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Atomic Fact Audit")
    parser.add_argument("target", nargs="?", help="File or directory to audit")
    args = parser.parse_args()
    
    audit_wiki(target=args.target)


if __name__ == "__main__":
    main()
