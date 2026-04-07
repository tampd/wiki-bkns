#!/usr/bin/env python3
"""
BKNS Wiki — Recategorize Claims
Di chuyển claims bị đặt sai category dựa vào entity_id prefix.

Usage:
    python3 tools/recategorize_claims.py --dry-run    # Preview changes
    python3 tools/recategorize_claims.py --execute    # Actually move files
    python3 tools/recategorize_claims.py --summary    # Show current distribution
"""
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── Routing Rules ─────────────────────────────────────────
# Order matters: more specific prefixes MUST come before generic ones.
# Each rule: (list_of_prefixes, target_category)
ROUTING_RULES = [
    # ── Hosting ──
    (["product.hosting", "ent-prod-hosting-wp"], "hosting"),
    # NOTE: ent-prod-hosting-dedicated → server (below)

    # ── VPS ──
    (["product.vps", "ent-prod-vps", "bkns.vps",
      "vps.gia_re", "vps.sieu_re"], "vps"),

    # ── Email ──
    ([
        "product.email", "ent-prod-email",
        "bkns.email", "bkns_cloud_email",
        "product.email_hosting",
    ], "email"),

    # ── SSL ──
    (["product.ssl", "ent-prod-ssl", "bkns.ssl"], "ssl"),

    # ── Tên Miền ──
    (["product.domain", "ent-prod-domain"], "ten-mien"),

    # ── Server (Dedicated, Colocation, Quản trị, Backup, VPN) ──
    ([
        "product.server", "product.colocation", "product.dedicated",
        "ent-prod-colocation", "ent-prod-backup",
        "ent-prod-vpn", "ent-prod-managed-server",
        "ent-prod-server", "ent-prod-hosting-dedicated",
        "bkns.server", "bkns:colocation", "bkns:promo_server",
        "product.server_management",
    ], "server"),

    # ── Software ──
    ([
        "product.software", "ent-prod-software",
        "dti_software", "prod.software", "doc.metadata.soft",
        "bkns.product.software", "vblt_", "vblt_5",
    ], "software"),

    # ── Server extras ──
    (["product.vpn"], "server"),

    # ── Hosting (generic — after specific prefixes) ──
    (["ent-prod-hosting"], "hosting"),
]

# Categories to DELETE entirely (user confirmed)
DELETE_CATEGORIES = ["other", "uncategorized"]

# entity_id prefixes that should be DELETED (not moved)
DELETE_PREFIXES = [
    "ent-prod-meeting", "ent-prod-emeeting",
    "ent-company",  # Company info — not a product
]


def determine_category(entity_id: str) -> str | None:
    """Route entity_id to correct category.

    Returns:
        Category string, or None if should be deleted.
    """
    eid = entity_id.strip().lower()

    # Check delete list first
    for prefix in DELETE_PREFIXES:
        if eid.startswith(prefix):
            return None  # Mark for deletion

    # Check routing rules
    for prefixes, category in ROUTING_RULES:
        for prefix in prefixes:
            if eid.startswith(prefix):
                return category

    return "__unknown__"  # Unrecognized — flag for review


def read_entity_id(yaml_path: Path) -> str:
    """Read entity_id from a YAML claim file without full YAML parsing."""
    try:
        text = yaml_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("entity_id:"):
                value = stripped[len("entity_id:"):].strip()
                # Remove quotes
                if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                    value = value[1:-1]
                return value
    except Exception:
        pass
    return ""


def scan_claims(base_dir: Path) -> list[dict]:
    """Scan all claims and determine correct category.

    Returns list of dicts with: path, current_cat, correct_cat, entity_id, action
    """
    results = []

    for cat_dir in sorted(base_dir.iterdir()):
        if not cat_dir.is_dir():
            continue
        current_cat = cat_dir.name

        for yaml_file in sorted(cat_dir.glob("*.yaml")):
            entity_id = read_entity_id(yaml_file)
            correct_cat = determine_category(entity_id)

            if correct_cat is None:
                action = "DELETE"
            elif correct_cat == "__unknown__":
                action = "REVIEW"
            elif current_cat in DELETE_CATEGORIES and correct_cat != "__unknown__":
                action = "MOVE"
            elif correct_cat != current_cat:
                action = "MOVE"
            else:
                action = "OK"

            results.append({
                "path": yaml_file,
                "current_cat": current_cat,
                "correct_cat": correct_cat,
                "entity_id": entity_id,
                "action": action,
            })

    return results


def print_summary(results: list[dict]):
    """Print current vs correct distribution."""
    from collections import Counter

    current = Counter(r["current_cat"] for r in results)
    correct = Counter(
        r["correct_cat"] for r in results
        if r["correct_cat"] and r["correct_cat"] != "__unknown__"
    )

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         CLAIM DISTRIBUTION: CURRENT vs CORRECT       ║")
    print("╠════════════════╦═══════════╦═══════════╦═════════════╣")
    print("║ Category       ║  Current  ║  Correct  ║    Delta    ║")
    print("╠════════════════╬═══════════╬═══════════╬═════════════╣")

    all_cats = sorted(set(list(current.keys()) + list(correct.keys())))
    for cat in all_cats:
        cur = current.get(cat, 0)
        cor = correct.get(cat, 0)
        delta = cor - cur
        delta_str = f"+{delta}" if delta > 0 else str(delta) if delta != 0 else "="
        print(f"║ {cat:<14} ║ {cur:>7}   ║ {cor:>7}   ║ {delta_str:>9}   ║")

    print("╠════════════════╬═══════════╬═══════════╬═════════════╣")

    to_delete = sum(1 for r in results if r["action"] == "DELETE")
    to_review = sum(1 for r in results if r["action"] == "REVIEW")
    print(f"║ TO DELETE      ║           ║ {to_delete:>7}   ║             ║")
    print(f"║ TO REVIEW      ║           ║ {to_review:>7}   ║             ║")
    print("╚════════════════╩═══════════╩═══════════╩═════════════╝")


def print_dry_run(results: list[dict]):
    """Print all planned moves/deletes."""
    moves = [r for r in results if r["action"] == "MOVE"]
    deletes = [r for r in results if r["action"] == "DELETE"]
    reviews = [r for r in results if r["action"] == "REVIEW"]
    ok = [r for r in results if r["action"] == "OK"]

    print(f"\n{'='*60}")
    print(f"DRY RUN RESULTS")
    print(f"{'='*60}")
    print(f"  ✅ OK (correct category):  {len(ok)}")
    print(f"  📦 MOVE (wrong category):  {len(moves)}")
    print(f"  🗑️  DELETE (invalid):       {len(deletes)}")
    print(f"  ❓ REVIEW (unknown):       {len(reviews)}")
    print(f"{'='*60}")

    if moves:
        print(f"\n📦 FILES TO MOVE ({len(moves)}):")
        print(f"{'─'*60}")
        # Group by current → correct
        from collections import defaultdict
        move_groups = defaultdict(list)
        for r in moves:
            key = f"{r['current_cat']} → {r['correct_cat']}"
            move_groups[key].append(r)

        for direction, items in sorted(move_groups.items()):
            print(f"\n  {direction} ({len(items)} files):")
            for r in items[:5]:  # Show first 5
                print(f"    • {r['path'].name}  (entity: {r['entity_id'][:50]})")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")

    if deletes:
        print(f"\n🗑️  FILES TO DELETE ({len(deletes)}):")
        print(f"{'─'*60}")
        for r in deletes:
            print(f"  • [{r['current_cat']}] {r['path'].name}  (entity: {r['entity_id'][:50]})")

    if reviews:
        print(f"\n❓ FILES NEEDING REVIEW ({len(reviews)}):")
        print(f"{'─'*60}")
        for r in reviews:
            print(f"  • [{r['current_cat']}] {r['path'].name}  (entity: {r['entity_id'][:60]})")


def execute_moves(results: list[dict], base_dir: Path, backup_dir: Path):
    """Execute the recategorization."""
    moves = [r for r in results if r["action"] == "MOVE"]
    deletes = [r for r in results if r["action"] == "DELETE"]

    # Create backup
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"recategorize_backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)

    moved_count = 0
    deleted_count = 0
    conflict_count = 0
    errors = []

    # Process MOVES
    for r in moves:
        yaml_path = r["path"]
        jsonl_path = yaml_path.with_suffix(".jsonl")
        target_dir = base_dir / r["correct_cat"]
        target_dir.mkdir(parents=True, exist_ok=True)

        target_yaml = target_dir / yaml_path.name
        target_jsonl = target_dir / jsonl_path.name

        try:
            # Handle conflict: if target exists
            if target_yaml.exists():
                # Compare observed_at → keep newer
                existing_date = _get_observed_at(target_yaml)
                new_date = _get_observed_at(yaml_path)

                if new_date >= existing_date:
                    # Backup existing, replace with newer
                    _backup_file(target_yaml, backup_path)
                    shutil.move(str(yaml_path), str(target_yaml))
                    if jsonl_path.exists():
                        # Append trace to existing
                        if target_jsonl.exists():
                            with open(target_jsonl, "a") as dst, open(jsonl_path) as src:
                                dst.write(src.read())
                            jsonl_path.unlink()
                        else:
                            shutil.move(str(jsonl_path), str(target_jsonl))
                    conflict_count += 1
                else:
                    # Existing is newer → backup and delete the source
                    _backup_file(yaml_path, backup_path)
                    yaml_path.unlink()
                    if jsonl_path.exists():
                        jsonl_path.unlink()
                    conflict_count += 1
                    continue
            else:
                # No conflict — simple move
                shutil.move(str(yaml_path), str(target_yaml))
                if jsonl_path.exists():
                    shutil.move(str(jsonl_path), str(target_jsonl))

            moved_count += 1

        except Exception as e:
            errors.append(f"MOVE {yaml_path.name}: {e}")

    # Process DELETES
    for r in deletes:
        yaml_path = r["path"]
        jsonl_path = yaml_path.with_suffix(".jsonl")

        try:
            _backup_file(yaml_path, backup_path)
            yaml_path.unlink()
            if jsonl_path.exists():
                jsonl_path.unlink()
            deleted_count += 1
        except Exception as e:
            errors.append(f"DELETE {yaml_path.name}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"EXECUTION COMPLETE")
    print(f"{'='*60}")
    print(f"  ✅ Moved:     {moved_count}")
    print(f"  🗑️  Deleted:   {deleted_count}")
    print(f"  ⚠️  Conflicts: {conflict_count} (resolved by date)")
    print(f"  ❌ Errors:    {len(errors)}")
    print(f"  💾 Backup:    {backup_path}")

    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  • {e}")

    return moved_count, deleted_count, len(errors)


def _get_observed_at(yaml_path: Path) -> str:
    """Extract observed_at date from yaml file."""
    try:
        text = yaml_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("observed_at:"):
                return line.strip().split(":", 1)[1].strip().strip("'\"")
    except Exception:
        pass
    return ""


def _backup_file(file_path: Path, backup_dir: Path):
    """Backup a file before moving/deleting."""
    backup_target = backup_dir / file_path.parent.name / file_path.name
    backup_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(file_path), str(backup_target))


def cleanup_empty_dirs(base_dir: Path, categories_to_remove: list[str]):
    """Remove empty category directories."""
    for cat in categories_to_remove:
        cat_dir = base_dir / cat
        if cat_dir.exists():
            remaining = list(cat_dir.glob("*"))
            if not remaining:
                cat_dir.rmdir()
                print(f"  Removed empty directory: {cat_dir}")
            else:
                print(f"  ⚠️  {cat_dir} still has {len(remaining)} files — skipping removal")


def main():
    parser = argparse.ArgumentParser(description="Recategorize BKNS Wiki Claims")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    parser.add_argument("--execute", action="store_true", help="Execute recategorization")
    parser.add_argument("--summary", action="store_true", help="Show current distribution")
    args = parser.parse_args()

    if not any([args.dry_run, args.execute, args.summary]):
        parser.print_help()
        sys.exit(1)

    workspace = Path("/home/openclaw/wiki")
    claims_base = workspace / "claims"
    backup_base = workspace / "tools" / ".backups"

    # Process BOTH drafts and approved
    for subdir_name in ["drafts", "approved"]:
        if subdir_name == "drafts":
            base = claims_base / ".drafts" / "products"
        else:
            base = claims_base / "approved" / "products"

        if not base.exists():
            print(f"Directory not found: {base}")
            continue

        print(f"\n{'═'*60}")
        print(f"  Processing: {subdir_name.upper()}")
        print(f"  Path: {base}")
        print(f"{'═'*60}")

        results = scan_claims(base)

        if args.summary or args.dry_run:
            print_summary(results)

        if args.dry_run:
            print_dry_run(results)

        if args.execute:
            print_summary(results)
            print_dry_run(results)

            # Confirmation
            moves = sum(1 for r in results if r["action"] == "MOVE")
            deletes = sum(1 for r in results if r["action"] == "DELETE")
            print(f"\n⚠️  About to MOVE {moves} files and DELETE {deletes} files in {subdir_name}.")
            confirm = input("Proceed? (yes/no): ").strip().lower()

            if confirm == "yes":
                execute_moves(results, base, backup_base / subdir_name)
                cleanup_empty_dirs(base, DELETE_CATEGORIES)
            else:
                print("Cancelled.")


if __name__ == "__main__":
    main()
