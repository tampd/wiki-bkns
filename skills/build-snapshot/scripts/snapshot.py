#!/usr/bin/env python3
"""
BKNS Agent Wiki — build-snapshot
Đóng gói wiki → build manifest + update active-build.yaml.

Usage:
    python3 scripts/snapshot.py           # Create new build
    python3 scripts/snapshot.py --info    # Show current build info
"""
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    WIKI_DIR, BUILD_DIR, BUILD_MANIFESTS_DIR, ACTIVE_BUILD,
    CLAIMS_APPROVED_DIR, WORKSPACE,
)
from lib.logger import log_entry
from lib.telegram import notify_skill
from lib.utils import (
    sha256_directory, now_iso, today_str, now_compact,
    read_yaml, write_yaml, read_text_safe, ensure_dir,
)


def count_wiki_files() -> tuple[int, int, list[str]]:
    """Count wiki files and estimate tokens.

    Returns:
        (file_count, token_estimate, file_list)
    """
    total_chars = 0
    files = []

    for md in sorted(WIKI_DIR.rglob("*.md")):
        if ".drafts" in str(md):
            continue
        content = read_text_safe(str(md))
        total_chars += len(content)
        files.append(str(md.relative_to(WIKI_DIR)))

    # Estimate: ~4 chars per token
    token_estimate = total_chars // 4

    return len(files), token_estimate, files


def count_approved_claims() -> int:
    """Count total approved claims."""
    count = 0
    if CLAIMS_APPROVED_DIR.exists():
        count = len(list(CLAIMS_APPROVED_DIR.rglob("*.yaml")))
    return count


def git_tag(tag: str) -> bool:
    """Create Git tag if repo exists."""
    try:
        subprocess.run(
            ["git", "tag", tag],
            cwd=str(WORKSPACE),
            capture_output=True,
            timeout=10,
        )
        return True
    except Exception:
        return False


def create_snapshot() -> dict:
    """Create a new build snapshot.

    Returns:
        dict with build info
    """
    log_entry("build-snapshot", "start", "Creating new build")

    # 1. Count files and tokens
    file_count, token_estimate, file_list = count_wiki_files()
    claims_count = count_approved_claims()

    # 2. Generate build ID and version
    compact = now_compact()
    build_id = f"BLD-{compact}"

    # Auto-increment version
    current = read_yaml(ACTIVE_BUILD)
    current_version = current.get("version", "v0.0")
    try:
        parts = current_version.replace("v", "").split(".")
        major, minor = int(parts[0]), int(parts[1])
        new_version = f"v{major}.{minor + 1}"
    except (ValueError, IndexError):
        new_version = "v0.1"

    # 3. Wiki hash (fingerprint)
    wiki_hash = sha256_directory(WIKI_DIR, "*.md")

    # 4. Create manifest
    manifest = {
        "build_id": build_id,
        "version": new_version,
        "build_date": now_iso(),
        "wiki_hash": wiki_hash,
        "wiki_files": file_count,
        "wiki_token_estimate": token_estimate,
        "claims_count": claims_count,
        "file_list": file_list,
        "previous_build": current.get("build_id"),
        "previous_version": current_version,
    }

    ensure_dir(BUILD_MANIFESTS_DIR)
    manifest_path = BUILD_MANIFESTS_DIR / f"{build_id}.yaml"
    write_yaml(manifest, manifest_path)

    # 5. Update active-build.yaml
    active = {
        "build_id": build_id,
        "version": new_version,
        "build_date": now_iso(),
        "wiki_token_estimate": token_estimate,
        "wiki_files": file_count,
        "claims_count": claims_count,
        "wiki_hash": wiki_hash,
        "git_tag": new_version,
        "status": "active",
    }
    write_yaml(active, ACTIVE_BUILD)

    # 6. Git tag
    tagged = git_tag(new_version)

    # 7. Notify
    notify_skill("build-snapshot",
                  f"🔨 Build *{build_id}* ({new_version})\n"
                  f"• {file_count} wiki files\n"
                  f"• ~{token_estimate:,} tokens\n"
                  f"• {claims_count} approved claims\n"
                  f"• Git tag: {'✅' if tagged else '⚠️ no git'}",
                  severity="build")

    log_entry("build-snapshot", "success",
              f"Build {build_id} ({new_version}): {file_count} files, "
              f"~{token_estimate} tokens")

    return {
        "status": "success",
        "build_id": build_id,
        "version": new_version,
        "wiki_files": file_count,
        "token_estimate": token_estimate,
        "claims_count": claims_count,
    }


def show_build_info():
    """Display current build information."""
    info = read_yaml(ACTIVE_BUILD)
    if not info or not info.get("build_id"):
        print("No active build. Run build to create one.")
        return

    print(f"Build ID:     {info.get('build_id')}")
    print(f"Version:      {info.get('version')}")
    print(f"Build Date:   {info.get('build_date')}")
    print(f"Wiki Files:   {info.get('wiki_files')}")
    print(f"Token Est:    {info.get('wiki_token_estimate', 0):,}")
    print(f"Claims:       {info.get('claims_count')}")
    print(f"Status:       {info.get('status')}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Build Snapshot")
    parser.add_argument("--info", action="store_true", help="Show current build")
    args = parser.parse_args()

    if args.info:
        show_build_info()
    else:
        result = create_snapshot()
        print(f"\n{'='*40}")
        print(f"Build: {result['build_id']} ({result['version']})")
        print(f"Files: {result['wiki_files']}")
        print(f"Tokens: ~{result['token_estimate']:,}")
        print(f"{'='*40}")


if __name__ == "__main__":
    main()
