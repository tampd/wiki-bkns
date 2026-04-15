#!/usr/bin/env python3
"""
BKNS Agent Wiki — Approve and compile pipeline
Batch approve drafted claims → compile → build.

Usage:
    python3 tools/approve_and_compile.py                    # Approve all drafts + compile + build
    python3 tools/approve_and_compile.py --category hosting # Specific category only
    python3 tools/approve_and_compile.py --approve-only     # Only approve, no compile
"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import CLAIMS_DRAFTS_DIR, CLAIMS_APPROVED_DIR
from lib.utils import read_yaml, write_yaml, ensure_dir, now_iso
from lib.logger import log_entry


def approve_all_drafts(category: str = None) -> dict:
    """Batch approve all drafted claims.
    
    For MVP: approve all drafts automatically.
    In production: /duyet for manual review.
    """
    drafts_base = CLAIMS_DRAFTS_DIR / "products"
    if not drafts_base.exists():
        print("Không có claims drafts nào.")
        return {"approved": 0}
    
    approved = 0
    skipped = 0
    
    categories = [category] if category else [
        d.name for d in drafts_base.iterdir() if d.is_dir()
    ]
    
    for cat in categories:
        draft_dir = drafts_base / cat
        if not draft_dir.exists():
            continue
            
        approved_dir = CLAIMS_APPROVED_DIR / "products" / cat
        ensure_dir(approved_dir)
        
        for yaml_file in sorted(draft_dir.glob("*.yaml")):
            claim = read_yaml(yaml_file)
            if not isinstance(claim, dict):
                skipped += 1
                continue
            
            # Set approved status
            claim["review_state"] = "approved"
            claim["approved_at"] = now_iso()
            claim["approved_by"] = "admin-batch"
            
            # Move to approved directory
            dest = approved_dir / yaml_file.name
            write_yaml(claim, dest)
            approved += 1
        
        print(f"  {cat}: {approved} claims approved")
    
    log_entry("approve", "success", 
              f"Batch approved {approved} claims ({skipped} skipped)")
    
    return {"approved": approved, "skipped": skipped}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Approve & Compile")
    parser.add_argument("--category", "-c", help="Specific category")
    parser.add_argument("--approve-only", action="store_true")
    args = parser.parse_args()
    
    print("=" * 50)
    print("BKNS Wiki — Approve & Compile Pipeline")
    print("=" * 50)
    
    # Step 1: Approve
    print("\n📋 Step 1: Approving drafted claims...")
    result = approve_all_drafts(args.category)
    print(f"✅ Approved: {result['approved']} claims\n")
    
    if args.approve_only:
        return
    
    if result["approved"] == 0:
        print("Không có gì để compile.")
        return
    
    # Step 2: Compile each category (use importlib per LESSONS BUG-002)
    print("📝 Step 2: Compiling wiki pages...")
    import importlib.util

    def _load_module(module_name: str, file_path: Path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    repo_root = Path(__file__).resolve().parent.parent
    compile_mod = _load_module(
        "bkns_compile",
        repo_root / "skills" / "compile-wiki" / "scripts" / "compile.py",
    )
    do_compile = compile_mod.compile_category

    approved_base = CLAIMS_APPROVED_DIR / "products"
    categories = [args.category] if args.category else [
        d.name for d in approved_base.iterdir() if d.is_dir()
    ]

    for cat in categories:
        print(f"\n  Compiling: {cat}...")
        try:
            result = do_compile(cat)
            print(f"  → {result.get('status', 'unknown')}")
        except Exception as e:
            print(f"  → Error: {e}")

    # Step 3: Build snapshot
    print("\n🔨 Step 3: Building snapshot...")
    snapshot_mod = _load_module(
        "bkns_snapshot",
        repo_root / "skills" / "build-snapshot" / "scripts" / "snapshot.py",
    )
    build = snapshot_mod.create_snapshot()
    print(f"✅ Build: {build['build_id']} ({build['version']})")
    
    print(f"\n{'='*50}")
    print("✅ Pipeline complete! Run /hoi to query new content.")


if __name__ == "__main__":
    main()
