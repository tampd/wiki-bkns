#!/usr/bin/env python3
"""
BKNS Wiki — Wiki Health Check
Kiểm tra toàn bộ wiki pages và claims để phát hiện vấn đề chất lượng.

Reports:
  - Wiki pages with self_review: fail
  - Wiki pages needing human review
  - Claims with missing/invalid fields
  - Compiled categories vs available claims
  - Build freshness

Usage:
    python3 tools/check_wiki_health.py
    python3 tools/check_wiki_health.py --json   # Output JSON
    python3 tools/check_wiki_health.py --fix    # Auto-fix minor issues
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import WIKI_DIR, CLAIMS_APPROVED_DIR, BUILD_DIR
from lib.utils import read_yaml, parse_frontmatter

REQUIRED_CLAIM_FIELDS = {"claim_id", "entity_id", "attribute", "value", "confidence"}


def check_wiki_pages() -> dict:
    """Scan all wiki pages for quality issues."""
    issues = {
        "self_review_fail": [],
        "human_review_needed": [],
        "missing_frontmatter": [],
        "old_pages": [],
    }
    total = 0

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if ".drafts" in str(md_file):
            continue
        total += 1

        try:
            content = md_file.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)
        except Exception as e:
            issues["missing_frontmatter"].append({"file": str(md_file.relative_to(WIKI_DIR)), "error": str(e)})
            continue

        rel = str(md_file.relative_to(WIKI_DIR))

        if frontmatter.get("self_review") == "fail":
            issues["self_review_fail"].append({
                "file": rel,
                "corrections": frontmatter.get("corrections", 0),
                "claims_used": frontmatter.get("claims_used", 0),
                "updated": frontmatter.get("updated", "?"),
            })

        if frontmatter.get("human_review_needed"):
            issues["human_review_needed"].append({
                "file": rel,
                "note": frontmatter.get("review_note", ""),
            })

    return {"total_pages": total, "issues": issues}


def check_claims() -> dict:
    """Scan approved claims for quality issues."""
    stats = {
        "total": 0,
        "categories": {},
        "missing_fields": [],
        "string_confidence": 0,
    }

    for yaml_file in sorted(CLAIMS_APPROVED_DIR.rglob("*.yaml")):
        stats["total"] += 1
        cat = yaml_file.parent.name

        try:
            import yaml
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

        # Check required fields
        missing = REQUIRED_CLAIM_FIELDS - set(data.keys())
        if missing:
            stats["missing_fields"].append({
                "file": yaml_file.name,
                "missing": list(missing),
            })

        # Check confidence is string (expected behavior in this project)
        conf = data.get("confidence")
        if isinstance(conf, str):
            stats["string_confidence"] += 1

    return stats


def check_build() -> dict:
    """Check build freshness."""
    build_file = BUILD_DIR / "active-build.yaml"
    if not build_file.exists():
        return {"status": "no_build", "message": "No active build found"}

    build = read_yaml(build_file)
    build_id = build.get("build_id", "?")
    built_at = build.get("built_at", "?")

    return {
        "build_id": build_id,
        "built_at": built_at,
        "wiki_pages": build.get("wiki_pages", 0),
        "total_claims": build.get("total_claims", 0),
    }


def check_uncategorized_claims() -> dict:
    """Check for claims in draft categories not yet approved."""
    from lib.config import CLAIMS_DRAFTS_DIR
    import yaml

    draft_categories = set()
    approved_categories = set()

    if CLAIMS_DRAFTS_DIR.exists():
        for d in (CLAIMS_DRAFTS_DIR / "products").iterdir():
            if d.is_dir():
                draft_categories.add(d.name)

    if CLAIMS_APPROVED_DIR.exists():
        for d in (CLAIMS_APPROVED_DIR / "products").iterdir():
            if d.is_dir():
                approved_categories.add(d.name)

    unapproved = draft_categories - approved_categories
    return {
        "draft_only_categories": sorted(unapproved),
        "approved_categories": sorted(approved_categories),
    }


def print_report(wiki_result: dict, claims_result: dict, build_result: dict, uncategorized: dict):
    """Print a human-readable health report."""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*60}")
    print(f"  BKNS Wiki Health Report — {now}")
    print(f"{'='*60}")

    # Build info
    b = build_result
    if b.get("status") == "no_build":
        print("\n⚠️  BUILD: No active build found!")
    else:
        print(f"\n📦 BUILD: {b.get('build_id')} | built: {b.get('built_at','?')[:10]}")
        print(f"   Pages: {b.get('wiki_pages',0)} | Claims: {b.get('total_claims',0)}")

    # Wiki pages
    total = wiki_result.get("total_pages", 0)
    issues = wiki_result.get("issues", {})
    fail_count = len(issues.get("self_review_fail", []))
    review_count = len(issues.get("human_review_needed", []))

    status = "✅" if fail_count == 0 and review_count == 0 else "⚠️"
    print(f"\n{status} WIKI PAGES: {total} total")

    if fail_count:
        print(f"   🔴 Self-review FAIL ({fail_count}):")
        for p in issues["self_review_fail"]:
            print(f"      - {p['file']} (corrections={p['corrections']}, claims={p['claims_used']})")

    if review_count:
        print(f"   🟡 Needs human review ({review_count}):")
        for p in issues["human_review_needed"]:
            note = f" — {p['note'][:60]}" if p.get("note") else ""
            print(f"      - {p['file']}{note}")

    if not fail_count and not review_count:
        print("   All pages OK")

    # Claims
    total_claims = claims_result.get("total", 0)
    cats = claims_result.get("categories", {})
    missing_fields = claims_result.get("missing_fields", [])

    print(f"\n📋 CLAIMS: {total_claims} total across {len(cats)} categories")
    for cat, count in sorted(cats.items()):
        print(f"   - {cat}: {count}")

    if missing_fields:
        print(f"\n   ⚠️  Claims with missing required fields: {len(missing_fields)}")
        for m in missing_fields[:5]:
            print(f"      - {m['file']}: missing {m['missing']}")

    # Uncategorized
    draft_only = uncategorized.get("draft_only_categories", [])
    if draft_only:
        print(f"\n🗂️  DRAFT-ONLY CATEGORIES (not yet approved): {draft_only}")
    else:
        print(f"\n✅ All draft categories are approved")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Health Check")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    wiki_result = check_wiki_pages()
    claims_result = check_claims()
    build_result = check_build()
    uncategorized = check_uncategorized_claims()

    if args.json:
        print(json.dumps({
            "wiki": wiki_result,
            "claims": claims_result,
            "build": build_result,
            "uncategorized": uncategorized,
        }, indent=2, ensure_ascii=False))
    else:
        print_report(wiki_result, claims_result, build_result, uncategorized)


if __name__ == "__main__":
    main()
