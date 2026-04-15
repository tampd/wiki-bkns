#!/usr/bin/env python3
"""
BKNS Wiki — Claim Conflict Detector
Phát hiện các claims mâu thuẫn: cùng entity_id + attribute nhưng giá trị khác nhau.

Usage:
    python3 tools/detect_conflicts.py
    python3 tools/detect_conflicts.py --json
    python3 tools/detect_conflicts.py --category vps
    python3 tools/detect_conflicts.py --export conflicts_report.json
"""
import sys
import json
import argparse
import hashlib
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml")
    sys.exit(1)

from lib.config import CLAIMS_APPROVED_DIR


def load_all_claims(category: str = None) -> list[dict]:
    """Load all approved claims, optionally filtered by category."""
    claims = []
    base_dir = CLAIMS_APPROVED_DIR / "products"

    if not base_dir.exists():
        print(f"ERROR: Claims dir not found: {base_dir}")
        return []

    categories = [category] if category else [d.name for d in base_dir.iterdir() if d.is_dir()]

    for cat in sorted(categories):
        cat_dir = base_dir / cat
        if not cat_dir.is_dir():
            print(f"WARN: Category not found: {cat}")
            continue

        for yaml_file in sorted(cat_dir.rglob("*.yaml")):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    continue
                data["_file"] = str(yaml_file.relative_to(CLAIMS_APPROVED_DIR))
                data["_category"] = cat
                claims.append(data)
            except Exception as e:
                print(f"WARN: Could not load {yaml_file}: {e}")

    return claims


def _normalize_value(val) -> str:
    """Normalize a value for comparison."""
    if val is None:
        return ""
    if isinstance(val, dict):
        # Sort dict keys for consistent comparison
        return json.dumps(val, sort_keys=True, ensure_ascii=False)
    return str(val).strip().lower()


def detect_conflicts(claims: list[dict]) -> list[dict]:
    """Find claims with same entity_id + attribute but different values."""
    # Group by (entity_id, attribute)
    grouped = defaultdict(list)
    for claim in claims:
        entity_id = claim.get("entity_id", "").strip()
        attribute = claim.get("attribute", "").strip()
        if not entity_id or not attribute:
            continue
        key = f"{entity_id}::{attribute}"
        grouped[key].append(claim)

    conflicts = []
    for key, group in sorted(grouped.items()):
        if len(group) < 2:
            continue

        # Check if any values differ
        unique_values = {}
        for claim in group:
            norm = _normalize_value(claim.get("value"))
            if norm not in unique_values:
                unique_values[norm] = []
            unique_values[norm].append(claim)

        if len(unique_values) < 2:
            continue  # All values are the same — no conflict

        entity_id, attribute = key.split("::", 1)
        conflict = {
            "entity_id": entity_id,
            "attribute": attribute,
            "conflict_count": len(unique_values),
            "values": [],
        }

        for norm_val, val_claims in sorted(unique_values.items(), key=lambda x: -len(x[1])):
            # Use first claim as representative
            rep = val_claims[0]
            conflict["values"].append({
                "value": rep.get("value"),
                "confidence": rep.get("confidence"),
                "source_url": rep.get("source_url", ""),
                "extracted_at": rep.get("extracted_at", ""),
                "claim_ids": [c.get("claim_id", "?") for c in val_claims],
                "files": [c.get("_file", "?") for c in val_claims],
                "category": rep.get("_category", "?"),
            })

        conflicts.append(conflict)

    # Sort by severity: more unique values = higher priority
    conflicts.sort(key=lambda x: -x["conflict_count"])
    return conflicts


def print_report(conflicts: list[dict], total_claims: int):
    """Print human-readable conflict report."""
    print(f"\n{'='*65}")
    print(f"  BKNS Wiki — Claim Conflict Report")
    print(f"{'='*65}")
    print(f"  Scanned {total_claims} claims | Found {len(conflicts)} conflicts")
    print(f"{'='*65}\n")

    if not conflicts:
        print("✅ Không có conflicts — tất cả claims nhất quán!\n")
        return

    # Group by category
    by_category = defaultdict(list)
    for c in conflicts:
        cats = list({v["category"] for v in c["values"]})
        cat_label = cats[0] if len(cats) == 1 else "multi-category"
        by_category[cat_label].append(c)

    for cat, cat_conflicts in sorted(by_category.items()):
        print(f"📂 {cat.upper()} ({len(cat_conflicts)} conflicts)")
        print("-" * 55)

        for conflict in cat_conflicts:
            entity = conflict["entity_id"]
            attr = conflict["attribute"]
            n = conflict["conflict_count"]

            severity = "🔴" if n >= 3 else "🟡"
            print(f"\n  {severity} {entity} → {attr}")

            for i, v in enumerate(conflict["values"], 1):
                val_display = str(v["value"])
                if len(val_display) > 60:
                    val_display = val_display[:57] + "..."
                conf = v.get("confidence", "?")
                extracted = str(v.get("extracted_at", ""))[:10]
                ids = ", ".join(v["claim_ids"][:2])
                print(f"     [{i}] Value: {val_display}")
                print(f"         Conf: {conf} | Date: {extracted}")
                print(f"         ID(s): {ids}")
                if v.get("source_url"):
                    print(f"         Source: {v['source_url'][:70]}")

        print()

    # Summary stats
    high = sum(1 for c in conflicts if c["conflict_count"] >= 3)
    med = len(conflicts) - high
    print(f"{'='*65}")
    print(f"  Summary: {high} high-severity (3+ values), {med} medium (2 values)")
    print(f"  Next step: Review conflicts, update source claims, re-compile")
    print(f"{'='*65}\n")


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Conflict Detector")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--category", "-c", help="Filter by category (e.g. vps, hosting)")
    parser.add_argument("--export", "-e", metavar="FILE", help="Export conflicts to JSON file")
    parser.add_argument("--only-high", action="store_true", help="Show only high-severity (3+ values)")
    args = parser.parse_args()

    claims = load_all_claims(args.category)
    if not claims:
        print("No claims found.")
        sys.exit(1)

    conflicts = detect_conflicts(claims)

    if args.only_high:
        conflicts = [c for c in conflicts if c["conflict_count"] >= 3]

    if args.export:
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump({"total_claims": len(claims), "conflicts": conflicts}, f, indent=2, ensure_ascii=False)
        print(f"✅ Exported {len(conflicts)} conflicts to {args.export}")
        return

    if args.json:
        print(json.dumps({"total_claims": len(claims), "conflicts": conflicts}, indent=2, ensure_ascii=False))
    else:
        print_report(conflicts, len(claims))


if __name__ == "__main__":
    main()
