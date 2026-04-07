"""
BKNS Agent Wiki — Shared Utilities
SHA256 hashing, slug generation, YAML helpers, frontmatter parsing.
"""
import hashlib
import re
import unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import yaml

# Vietnam timezone
VN_TZ = timezone(timedelta(hours=7))


# ── Hashing ────────────────────────────────────────────────
def sha256_content(content: str) -> str:
    """Generate SHA256 hash of content string."""
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def sha256_file(file_path: str | Path) -> str:
    """Generate SHA256 hash of file content."""
    with open(file_path, "rb") as f:
        return "sha256:" + hashlib.sha256(f.read()).hexdigest()


def sha256_directory(dir_path: str | Path, pattern: str = "*.yaml") -> str:
    """Generate SHA256 hash of all files in directory (sorted)."""
    h = hashlib.sha256()
    for f in sorted(Path(dir_path).rglob(pattern)):
        h.update(f.read_bytes())
    return "sha256:" + h.hexdigest()


# ── Slug Generation ────────────────────────────────────────
def slugify(text: str) -> str:
    """Convert text to URL-safe slug.

    Examples:
        'Hosting BKNS' -> 'hosting-bkns'
        'VPS Giá Rẻ' -> 'vps-gia-re'
    """
    # Normalize Unicode
    text = unicodedata.normalize("NFKD", text)
    # Remove non-ASCII (diacritics) but keep Vietnamese chars
    text = text.encode("ascii", "ignore").decode("ascii")
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Strip leading/trailing hyphens
    text = text.strip("-")
    return text


def url_to_slug(url: str) -> str:
    """Extract slug from URL.

    Examples:
        'https://bkns.vn/hosting' -> 'hosting'
        'https://bkns.vn/vps-gia-re' -> 'vps-gia-re'
        'https://bkns.vn/' -> 'index'
    """
    from urllib.parse import urlparse
    path = urlparse(url).path.strip("/")
    if not path:
        return "index"
    # Take last path segment
    slug = path.split("/")[-1]
    # Clean
    slug = re.sub(r"\.html?$", "", slug)
    return slugify(slug) or "page"


# ── Date/Time ──────────────────────────────────────────────
def now_iso() -> str:
    """Current time in ISO format with Vietnam timezone."""
    return datetime.now(VN_TZ).isoformat()


def today_str() -> str:
    """Today's date as YYYY-MM-DD string."""
    return datetime.now(VN_TZ).strftime("%Y-%m-%d")


def now_compact() -> str:
    """Current datetime as YYYYMMDD-HHMMSS."""
    return datetime.now(VN_TZ).strftime("%Y%m%d-%H%M%S")


# ── YAML Helpers ───────────────────────────────────────────
def read_yaml(file_path: str | Path) -> dict | list:
    """Read a YAML file and return parsed content."""
    path = Path(file_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(data: dict | list, file_path: str | Path):
    """Write data to a YAML file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def append_yaml_list(item: dict, file_path: str | Path):
    """Append an item to a YAML list file."""
    path = Path(file_path)
    data = read_yaml(path)
    if not isinstance(data, list):
        data = []
    data.append(item)
    write_yaml(data, path)


# ── Frontmatter Parsing ───────────────────────────────────
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from Markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        fm = {}

    body = parts[2].strip()
    return fm, body


def create_frontmatter(data: dict) -> str:
    """Create YAML frontmatter string."""
    fm = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{fm}---\n"


def write_markdown_with_frontmatter(
    file_path: str | Path,
    frontmatter: dict,
    body: str,
):
    """Write a Markdown file with YAML frontmatter."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    content = create_frontmatter(frontmatter) + "\n" + body
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ── File Utilities ─────────────────────────────────────────
def count_words(text: str) -> int:
    """Count words in text (approximate)."""
    return len(text.split())


def read_text_safe(file_path: str | Path) -> str:
    """Read text file safely, return empty string on error."""
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return ""


def ensure_dir(path: str | Path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


# ── Claim ID Generation ───────────────────────────────────
def generate_claim_id(
    entity_id: str,
    attribute: str,
    date_str: Optional[str] = None,
) -> str:
    """Generate a collision-proof deterministic claim ID via SHA256.

    Format: CLM-{SHA256[:12]}
    Example: CLM-3A7F2C1D9E4B

    Fully deterministic: same entity_id + attribute → same ID always.
    Collision-proof: SHA256 hash avoids the truncation collision risk
    of the old CLM-{ENTITY_SHORT}-{ATTR_SHORT} format.

    BREAKING CHANGE from v1 format (CLM-HOST-BKCP01-PRICE).
    Existing claim YAML files with old IDs will be treated as orphans
    on next extract — they will not be overwritten, just left in place.
    Run `python tools/recategorize_claims.py` to clean up if needed.

    date_str parameter is kept for backward compatibility but ignored.
    """
    key = f"{entity_id}:{attribute}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12].upper()
    return f"CLM-{digest}"
