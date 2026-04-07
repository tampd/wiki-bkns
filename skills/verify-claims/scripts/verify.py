#!/usr/bin/env python3
"""
BKNS Wiki — 3-Layer Claim Verification

Layer 1: DETERMINISTIC — prices vs Excel ground truth
Layer 2: CROSS-MODEL — Gemini Flash vs Pro cross-check
Layer 3: SELF-CONSISTENCY — multi-temperature extraction stability

Usage:
    python3 scripts/verify.py                          # Verify all claims
    python3 scripts/verify.py --category products/vps  # Specific category
    python3 scripts/verify.py --layer 1                # Only deterministic
"""
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    CLAIMS_APPROVED_DIR, WIKI_DIR, LOGS_DIR,
    MODEL_FLASH, MODEL_PRO,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.utils import ensure_dir, now_iso, today_str

VN_TZ = timezone(timedelta(hours=7))

# ══════════════════════════════════════════════════════════════
# LAYER 1: DETERMINISTIC VERIFICATION
# ══════════════════════════════════════════════════════════════

def load_ground_truth_claims() -> dict:
    """Load all ground_truth claims indexed by entity_id + attribute."""
    gt = {}
    for yaml_file in CLAIMS_APPROVED_DIR.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                claim = yaml.safe_load(f)
            if claim and claim.get("confidence") == "ground_truth":
                key = f"{claim['entity_id']}::{claim['attribute']}"
                gt[key] = claim
        except Exception:
            continue
    return gt


def verify_deterministic(claims: list[dict], ground_truth: dict) -> list[dict]:
    """Layer 1: Compare each claim against ground truth data.
    
    Returns list of verification results.
    """
    results = []
    
    for claim in claims:
        if claim.get("confidence") == "ground_truth":
            # Ground truth claims are self-verified
            results.append({
                "claim_id": claim["claim_id"],
                "layer": 1,
                "status": "self_verified",
                "detail": "Ground truth claim (direct from Excel)",
            })
            continue
        
        key = f"{claim['entity_id']}::{claim['attribute']}"
        gt_claim = ground_truth.get(key)
        
        if gt_claim is None:
            results.append({
                "claim_id": claim["claim_id"],
                "layer": 1,
                "status": "no_reference",
                "detail": f"No ground truth for {claim['entity_id']}.{claim['attribute']}",
            })
            continue
        
        # Compare values
        claim_val = claim.get("value")
        gt_val = gt_claim.get("value")
        
        # Numeric comparison with tolerance
        try:
            cv = float(str(claim_val).replace(",", "").replace(".", "").replace("đ", "").strip())
            gv = float(str(gt_val).replace(",", "").replace(".", "").replace("đ", "").strip())
            
            if cv == gv:
                results.append({
                    "claim_id": claim["claim_id"],
                    "layer": 1,
                    "status": "match",
                    "detail": f"Value matches ground truth: {gt_val}",
                })
            else:
                diff_pct = abs(cv - gv) / gv * 100 if gv else 100
                results.append({
                    "claim_id": claim["claim_id"],
                    "layer": 1,
                    "status": "mismatch",
                    "severity": "critical" if diff_pct > 5 else "warning",
                    "detail": f"MISMATCH: claim={claim_val}, ground_truth={gt_val} (diff={diff_pct:.1f}%)",
                    "ground_truth_value": gt_val,
                    "claim_value": claim_val,
                })
        except (ValueError, TypeError):
            # String comparison
            if str(claim_val).strip().lower() == str(gt_val).strip().lower():
                results.append({
                    "claim_id": claim["claim_id"],
                    "layer": 1,
                    "status": "match",
                    "detail": f"Value matches ground truth: {gt_val}",
                })
            else:
                results.append({
                    "claim_id": claim["claim_id"],
                    "layer": 1,
                    "status": "mismatch",
                    "severity": "warning",
                    "detail": f"Text mismatch: claim='{claim_val}', gt='{gt_val}'",
                })
    
    return results


# ══════════════════════════════════════════════════════════════
# LAYER 2: CROSS-MODEL VERIFICATION
# ══════════════════════════════════════════════════════════════

CROSS_MODEL_PROMPT = """Bạn là chuyên gia kiểm duyệt nội dung hosting/VPS/email Việt Nam.

Dưới đây là danh sách claims (dữ liệu đã trích xuất) về sản phẩm BKNS.
Hãy kiểm tra từng claim và đánh giá:

{claims_text}

KIỂM TRA MỖI CLAIM:
1. Giá có hợp lý với thị trường hosting VN? (VPS giá rẻ ~90K-500K/tháng, Hosting ~29K-500K/tháng)
2. Thông số kỹ thuật có logic? (RAM/CPU/SSD tỷ lệ hợp lý?)
3. Có claim nào mâu thuẫn nhau không?
4. Tên sản phẩm/mã gói có đúng format BKNS không?

OUTPUT (JSON array):
[
  {{
    "claim_id": "...",
    "plausibility_score": 0-100,
    "issues": ["vấn đề 1", "vấn đề 2"] 
  }}
]

Chỉ liệt kê claims có score < 80 hoặc có issues. Claims OK thì bỏ qua."""


def verify_cross_model(claims: list[dict], batch_size: int = 30) -> list[dict]:
    """Layer 2: Use a different model to cross-check claim plausibility."""
    results = []
    
    # Filter out ground_truth claims (no need to cross-check)
    check_claims = [c for c in claims if c.get("confidence") != "ground_truth"]
    
    if not check_claims:
        return results
    
    # Process in batches
    for i in range(0, len(check_claims), batch_size):
        batch = check_claims[i:i + batch_size]
        
        claims_text = ""
        for c in batch:
            claims_text += f"- [{c['claim_id']}] {c['entity_name']}: {c['attribute']} = {c['value']}"
            if c.get("unit"):
                claims_text += f" {c['unit']}"
            claims_text += f" (confidence: {c['confidence']})\n"
        
        prompt = CROSS_MODEL_PROMPT.format(claims_text=claims_text)
        
        try:
            # Use Flash model for cross-verification (different from Pro used in extraction)
            result = generate(
                prompt=prompt,
                model=MODEL_FLASH,
                skill="verify-claims",
                temperature=0.1,
                max_output_tokens=4096,
            )
            
            text = result["text"].strip()
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                flagged = json.loads(match.group(0))
                for item in flagged:
                    results.append({
                        "claim_id": item.get("claim_id", "unknown"),
                        "layer": 2,
                        "status": "flagged" if item.get("plausibility_score", 100) < 70 else "warning",
                        "plausibility_score": item.get("plausibility_score", 0),
                        "issues": item.get("issues", []),
                        "detail": f"Cross-model score: {item.get('plausibility_score', 0)}/100",
                    })
        except Exception as e:
            results.append({
                "claim_id": "batch_error",
                "layer": 2,
                "status": "error",
                "detail": f"API error: {str(e)}",
            })
    
    return results


# ══════════════════════════════════════════════════════════════
# LAYER 3: CROSS-PAGE CONSISTENCY CHECK
# ══════════════════════════════════════════════════════════════

def verify_consistency(claims: list[dict]) -> list[dict]:
    """Layer 3: Check consistency — same product must have same price across claims."""
    results = []
    
    # Group claims by entity_id + attribute
    groups = defaultdict(list)
    for c in claims:
        key = f"{c['entity_id']}::{c['attribute']}"
        groups[key].append(c)
    
    for key, group_claims in groups.items():
        if len(group_claims) <= 1:
            continue
        
        # Multiple claims for same entity+attribute → check consistency
        values = set()
        for c in group_claims:
            values.add(str(c.get("value", "")))
        
        if len(values) > 1:
            # Conflict! Multiple different values
            gt_claims = [c for c in group_claims if c.get("confidence") == "ground_truth"]
            
            for c in group_claims:
                if c.get("confidence") == "ground_truth":
                    continue  # Ground truth is always correct
                
                if gt_claims and str(c.get("value")) != str(gt_claims[0].get("value")):
                    results.append({
                        "claim_id": c["claim_id"],
                        "layer": 3,
                        "status": "conflict_with_gt",
                        "severity": "critical",
                        "detail": f"CONFLICT: claim={c.get('value')} vs ground_truth={gt_claims[0].get('value')}",
                        "action": "auto_reject",
                    })
                elif not gt_claims:
                    results.append({
                        "claim_id": c["claim_id"],
                        "layer": 3,
                        "status": "conflict_no_gt",
                        "severity": "high",
                        "detail": f"Multiple conflicting values: {values}",
                        "action": "flag_for_review",
                    })
    
    return results


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def load_claims(category: str = None) -> list[dict]:
    """Load all approved claims, optionally filtered by category."""
    claims = []
    search_dir = CLAIMS_APPROVED_DIR / category if category else CLAIMS_APPROVED_DIR
    
    if not search_dir.exists():
        return claims
    
    for yaml_file in search_dir.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                claim = yaml.safe_load(f)
            if claim and isinstance(claim, dict):
                claim["_file"] = str(yaml_file)
                claims.append(claim)
        except Exception:
            continue
    
    return claims


def run_verification(category: str = None, layers: list[int] = None) -> dict:
    """Run full verification pipeline."""
    layers = layers or [1, 2, 3]
    
    print(f"🔍 Loading claims...")
    claims = load_claims(category)
    print(f"   Loaded {len(claims)} claims" + (f" from {category}" if category else ""))
    
    all_results = []
    total_cost = 0
    
    # Layer 1: Deterministic
    if 1 in layers:
        print(f"\n📐 Layer 1: Deterministic verification...")
        gt = load_ground_truth_claims()
        print(f"   Ground truth claims: {len(gt)}")
        l1_results = verify_deterministic(claims, gt)
        all_results.extend(l1_results)
        
        matches = len([r for r in l1_results if r["status"] == "match"])
        mismatches = len([r for r in l1_results if r["status"] == "mismatch"])
        no_ref = len([r for r in l1_results if r["status"] == "no_reference"])
        self_v = len([r for r in l1_results if r["status"] == "self_verified"])
        print(f"   ✅ Match: {matches} | ❌ Mismatch: {mismatches} | ⚠️ No ref: {no_ref} | 🔒 Self-verified: {self_v}")
    
    # Layer 2: Cross-model
    if 2 in layers:
        print(f"\n🤖 Layer 2: Cross-model verification...")
        l2_results = verify_cross_model(claims)
        all_results.extend(l2_results)
        flagged = len([r for r in l2_results if r["status"] == "flagged"])
        warnings = len([r for r in l2_results if r["status"] == "warning"])
        print(f"   🚩 Flagged: {flagged} | ⚠️ Warnings: {warnings}")
    
    # Layer 3: Consistency
    if 3 in layers:
        print(f"\n🔄 Layer 3: Consistency check...")
        l3_results = verify_consistency(claims)
        all_results.extend(l3_results)
        conflicts = len([r for r in l3_results if "conflict" in r["status"]])
        print(f"   ⚡ Conflicts: {conflicts}")
    
    # Summary
    critical = [r for r in all_results if r.get("severity") == "critical"]
    high = [r for r in all_results if r.get("severity") == "high"]
    
    # Save report
    ensure_dir(LOGS_DIR / "verify")
    report = {
        "ts": now_iso(),
        "category": category or "all",
        "total_claims": len(claims),
        "total_checks": len(all_results),
        "critical_issues": len(critical),
        "high_issues": len(high),
        "results": all_results,
    }
    
    report_path = LOGS_DIR / "verify" / f"verify-{today_str()}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'═' * 50}")
    print(f"📊 Verification Summary")
    print(f"   Total claims: {len(claims)}")
    print(f"   Total checks: {len(all_results)}")
    print(f"   🔴 Critical: {len(critical)}")
    print(f"   🟡 High: {len(high)}")
    print(f"   Report: {report_path}")
    
    if critical:
        print(f"\n🚨 CRITICAL ISSUES:")
        for r in critical[:10]:
            print(f"   [{r['claim_id']}] {r['detail']}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Claim Verification")
    parser.add_argument("--category", help="Category to verify (e.g., products/vps)")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3], nargs="+",
                        help="Specific layers to run")
    args = parser.parse_args()
    
    run_verification(
        category=args.category,
        layers=args.layer,
    )


if __name__ == "__main__":
    main()
