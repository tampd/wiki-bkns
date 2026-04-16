#!/usr/bin/env python3
"""
Migration: Remove date suffix from claim IDs and consolidate duplicates.

Old format: CLM-HOST-BKCP01-PRICE-20260404 (date causes duplicates)
New format: CLM-HOST-BKCP01-PRICE (deterministic, dedup-safe)

For duplicates (same entity+attribute, different dates):
- Keep the most recent one (latest observed_at)
- Merge source_ids from all versions

Usage:
    python3 tools/migrate_claim_ids.py --dry-run    # Preview changes
    python3 tools/migrate_claim_ids.py              # Execute migration
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.utils import read_yaml, write_yaml


def migrate_claims(base_dir: Path, dry_run: bool = True) -> dict:
    """Migrate claim files: remove date from ID, consolidate duplicates."""
    stats = {"renamed": 0, "merged": 0, "removed": 0, "errors": 0}

    for cat_dir in sorted(base_dir.iterdir()):
        if not cat_dir.is_dir():
            continue

        # Group files by base name (without date)
        groups = {}
        for f in sorted(cat_dir.glob("*.yaml")):
            stem = f.stem
            # Remove trailing _YYYYMMDD
            base = re.sub(r"_\d{8}$", "", stem)
            groups.setdefault(base, []).append(f)

        for base, files in groups.items():
            new_filename = base + ".yaml"
            new_path = cat_dir / new_filename

            if len(files) == 1 and files[0].name == new_filename:
                # Already migrated
                continue

            if len(files) == 1:
                # Single file, just rename
                old_file = files[0]
                claim = read_yaml(old_file)
                if not isinstance(claim, dict):
                    stats["errors"] += 1
                    continue

                # Update claim_id: remove date suffix
                old_id = claim.get("claim_id", "")
                new_id = re.sub(r"-\d{8}$", "", old_id)
                claim["claim_id"] = new_id

                if dry_run:
                    print(f"  RENAME: {old_file.name} → {new_filename}")
                else:
                    write_yaml(claim, new_path)
                    if old_file != new_path:
                        old_file.unlink()
                    # Also remove old jsonl trace
                    old_jsonl = old_file.with_suffix(".jsonl")
                    new_jsonl = new_path.with_suffix(".jsonl")
                    if old_jsonl.exists() and old_jsonl != new_jsonl:
                        # Append old trace to new trace file
                        content = old_jsonl.read_text(encoding="utf-8")
                        with open(new_jsonl, "a", encoding="utf-8") as f:
                            f.write(content)
                        old_jsonl.unlink()

                stats["renamed"] += 1

            else:
                # Multiple files = duplicates → merge
                # Sort by observed_at descending to keep newest
                claims = []
                for f in files:
                    claim = read_yaml(f)
                    if isinstance(claim, dict):
                        claims.append((f, claim))

                if not claims:
                    stats["errors"] += 1
                    continue

                # Sort: newest first
                claims.sort(
                    key=lambda x: x[1].get("observed_at", ""),
                    reverse=True,
                )

                # Start with newest claim
                merged = claims[0][1].copy()

                # Merge source_ids from all versions
                all_sources = []
                for _, c in claims:
                    all_sources.extend(c.get("source_ids", []))
                merged["source_ids"] = list(dict.fromkeys(all_sources))

                # Update claim_id
                old_id = merged.get("claim_id", "")
                merged["claim_id"] = re.sub(r"-\d{8}$", "", old_id)

                if dry_run:
                    print(f"  MERGE: {[f.name for f in files]} → {new_filename}")
                    print(f"         Keep value: {merged.get('value')} "
                          f"(from {claims[0][0].name})")
                else:
                    write_yaml(merged, new_path)
                    # Remove old files
                    for f, _ in claims:
                        if f != new_path:
                            f.unlink()
                        # Clean jsonl too
                        old_jsonl = f.with_suffix(".jsonl")
                        new_jsonl = new_path.with_suffix(".jsonl")
                        if old_jsonl.exists() and old_jsonl != new_jsonl:
                            content = old_jsonl.read_text(encoding="utf-8")
                            with open(new_jsonl, "a", encoding="utf-8") as fh:
                                fh.write(content)
                            old_jsonl.unlink()

                stats["merged"] += 1
                stats["removed"] += len(files) - 1

    return stats


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print(f"Claim ID Migration {'(DRY RUN)' if dry_run else '(EXECUTE)'}")
    print("=" * 60)

    for label, base_dir in [
        ("Approved", Path("/wiki/claims/approved/products")),
        ("Drafts", Path("/wiki/claims/.drafts/products")),
    ]:
        if not base_dir.exists():
            continue
        print(f"\n--- {label} ---")
        stats = migrate_claims(base_dir, dry_run=dry_run)
        print(f"  Renamed: {stats['renamed']}")
        print(f"  Merged: {stats['merged']}")
        print(f"  Removed: {stats['removed']}")
        print(f"  Errors: {stats['errors']}")

    if dry_run:
        print("\n(Dry run — no changes made. Run without --dry-run to execute.)")


if __name__ == "__main__":
    main()
