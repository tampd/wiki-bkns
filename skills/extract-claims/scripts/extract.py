#!/usr/bin/env python3
"""
BKNS Agent Wiki — extract-claims
Đọc raw/ files → Gemini Pro extract → claims YAML + JSONL trace.
Conflict detection vs claims/approved/.
SHA256 incremental cache: skip unchanged files (inspired by Graphify).

Usage:
    python3 scripts/extract.py              # Extract all pending (with cache)
    python3 scripts/extract.py [raw_file]   # Extract specific file
    python3 scripts/extract.py --force      # Bypass cache, re-extract all
    python3 scripts/extract.py --cache-stats # Show cache statistics
"""
import sys
import json
import re
import hashlib
import fcntl  # [C5] file locking for entity registry (Linux/Ubuntu)
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    RAW_CRAWL_DIR, RAW_MANUAL_DIR, CLAIMS_DRAFTS_DIR, CLAIMS_APPROVED_DIR,
    ENTITIES_REGISTRY, CLAIM_REQUIRED_FIELDS, CLAIM_HIGH_RISK_ATTRIBUTES,
    get_pro_model,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import notify_skill, notify_error, send_conflict_alert
from lib.utils import (
    parse_frontmatter, read_yaml, write_yaml, now_iso, today_str,
    generate_claim_id, ensure_dir, write_markdown_with_frontmatter,
)


# ── SHA256 Incremental Cache ───────────────────────────────
# Inspired by Graphify: cache file hashes to skip unchanged files.
# Saves ~$0.008/file × N files per re-extract run.
CACHE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "claims" / ".cache"
CACHE_FILE = CACHE_DIR / "extract_hashes.json"


def _load_cache() -> dict:
    """Load SHA256 hash cache from disk."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache: dict):
    """Persist SHA256 hash cache to disk."""
    ensure_dir(CACHE_DIR)
    CACHE_FILE.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _file_hash(path: Path) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_cached(path: Path, cache: dict) -> bool:
    """Check if file content matches cached hash (unchanged)."""
    key = str(path.resolve())
    cached_hash = cache.get(key, {}).get("sha256")
    if not cached_hash:
        return False
    return _file_hash(path) == cached_hash


def _update_cache(path: Path, cache: dict, claims_count: int, cost_usd: float):
    """Update cache entry after successful extraction."""
    key = str(path.resolve())
    cache[key] = {
        "sha256": _file_hash(path),
        "extracted_at": now_iso(),
        "claims_count": claims_count,
        "cost_usd": cost_usd,
        "filename": path.name,
    }


def show_cache_stats():
    """Display cache statistics."""
    cache = _load_cache()
    if not cache:
        print("📭 Cache trống — chưa có file nào được cache.")
        return

    total_files = len(cache)
    total_claims = sum(v.get("claims_count", 0) for v in cache.values())
    total_cost = sum(v.get("cost_usd", 0) for v in cache.values())
    still_valid = 0
    stale = 0

    for key, entry in cache.items():
        path = Path(key)
        if path.exists() and _file_hash(path) == entry.get("sha256"):
            still_valid += 1
        else:
            stale += 1

    print(f"📊 Extract Cache Statistics")
    print(f"{'='*45}")
    print(f"  Cached files:    {total_files}")
    print(f"  Still valid:     {still_valid} (sẽ skip khi re-extract)")
    print(f"  Stale/changed:   {stale} (cần re-extract)")
    print(f"  Total claims:    {total_claims}")
    print(f"  Total cost saved: ${total_cost:.4f} (nếu skip tất cả valid)")
    print(f"{'='*45}")
    print(f"  Cache file: {CACHE_FILE}")


# ── Category Routing (entity_id → category) ───────────────
# Order matters: specific prefixes before generic.
_ROUTING_RULES = [
    (["product.hosting", "ent-prod-hosting-wp"], "hosting"),
    (["product.vps", "ent-prod-vps", "bkns.vps",
      "vps.gia_re", "vps.sieu_re"], "vps"),
    (["product.email", "ent-prod-email", "bkns.email",
      "bkns_cloud_email", "product.email_hosting"], "email"),
    (["product.ssl", "ent-prod-ssl", "bkns.ssl"], "ssl"),
    (["product.domain", "ent-prod-domain"], "ten-mien"),
    (["product.server", "product.colocation", "product.dedicated",
      "ent-prod-colocation", "ent-prod-backup", "ent-prod-vpn",
      "ent-prod-managed-server", "ent-prod-server",
      "ent-prod-hosting-dedicated", "bkns.server",
      "bkns:colocation", "bkns:promo_server",
      "product.server_management", "product.vpn"], "server"),
    (["product.software", "ent-prod-software", "dti_software",
      "prod.software", "doc.metadata.soft", "bkns.product.software",
      "vblt_"], "software"),
    (["ent-prod-hosting"], "hosting"),
]


def determine_claim_category(entity_id: str, fallback: str) -> str:
    """Route claim to correct category based on entity_id prefix."""
    eid = entity_id.strip().lower()
    for prefixes, category in _ROUTING_RULES:
        for prefix in prefixes:
            if eid.startswith(prefix):
                return category
    return fallback  # Keep suggested_category as fallback


# ── Extraction Prompt ──────────────────────────────────────
EXTRACTION_PROMPT = """Bạn là chuyên gia trích xuất dữ liệu (data extraction specialist) cho BKNS.

INPUT:
- Nội dung trang web: {raw_content}
- Nguồn: {source_url}
- Ngày crawl: {crawled_at}

NHIỆM VỤ: Trích xuất MỌI facts có giá trị thành claims có cấu trúc.

QUY TẮC NGHIÊM NGẶT:
1. ❌ KHÔNG suy luận — chỉ trích xuất những gì THẤY RÕ RÀNG trong văn bản
2. ❌ KHÔNG bịa giá, thông số, chính sách
3. ❌ KHÔNG gộp nhiều facts vào 1 claim — mỗi fact = 1 claim riêng
4. ✅ Giá tiền → 1 claim riêng, risk_class = high
5. ✅ Thông số kỹ thuật (RAM, CPU, SSD) → 1 claim riêng mỗi attribute
6. ✅ Hotline, email, địa chỉ → 1 claim riêng, risk_class = high
7. ✅ Ghi rõ đoạn văn gốc vào compiler_note
8. ✅ Nếu không chắc chắn → confidence = low

Entities hợp lệ:
- ENT-COMPANY-001 (BKNS company info)
- ENT-PROD-HOSTING (shared hosting)
- ENT-PROD-VPS (VPS)
- ENT-PROD-DOMAIN (tên miền)
- ENT-PROD-EMAIL (email hosting)
- ENT-PROD-SSL (SSL)

OUTPUT FORMAT (JSON array):
[
  {{
    "entity_id": "product.hosting.bkcp01",
    "entity_type": "product_plan",
    "entity_name": "BKCP01",
    "attribute": "monthly_price",
    "value": 26000,
    "unit": "VND",
    "qualifiers": {{"billing_cycle": "month"}},
    "confidence": "high",
    "risk_class": "high",
    "compiler_note": "Trích từ bảng giá: 'Gói BKCP01 - 26.000đ/tháng'"
  }}
]

Ưu tiên extract: giá > specs > chính sách > mô tả.
Trả về JSON array DUY NHẤT, không giải thích thêm."""


def find_pending_files() -> list[Path]:
    """Find all raw files with status=pending_extract."""
    pending = []

    for raw_dir in [RAW_CRAWL_DIR, RAW_MANUAL_DIR]:
        if not raw_dir.exists():
            continue
        for f in raw_dir.rglob("*.md"):
            content = f.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            if fm.get("status") == "pending_extract":
                pending.append(f)

    return sorted(pending)


def write_claim_yaml(claim_data: dict, source_id: str, cat_short: str,
                     crawled_at: str) -> Path:
    """Write a single claim dict to YAML in claims/drafts/ and sync approved/.

    Extracted from the inline save logic in extract_claims_from_file() so that
    extract_dual.py can reuse it without code duplication.

    Returns the path where the claim was written.
    """
    attribute = claim_data.get("attribute", "")
    claim_id = generate_claim_id(claim_data["entity_id"], attribute)
    claim_category = determine_claim_category(claim_data["entity_id"], cat_short)

    claim_dir = CLAIMS_DRAFTS_DIR / "products" / claim_category
    ensure_dir(claim_dir)

    claim_filename = claim_id.lower().replace("-", "_") + ".yaml"
    claim_path = claim_dir / claim_filename

    existing = read_yaml(claim_path) if claim_path.exists() else None
    if isinstance(existing, dict) and existing.get("claim_id") == claim_id:
        old_sources = existing.get("source_ids", [])
        merged_sources = list(dict.fromkeys(old_sources + [source_id]))
        claim = {
            **existing,
            "value": claim_data["value"],
            "unit": claim_data.get("unit", existing.get("unit", "")),
            "qualifiers": claim_data.get("qualifiers", existing.get("qualifiers", {})),
            "source_ids": merged_sources,
            "observed_at": now_iso(),
            "confidence": claim_data.get("confidence", existing.get("confidence", "medium")),
            "risk_class": claim_data.get("risk_class", existing.get("risk_class", "low")),
            "compiler_note": claim_data.get("compiler_note", existing.get("compiler_note", "")),
            "entity_name": claim_data.get("entity_name", existing.get("entity_name", "")),
            "entity_type": claim_data.get("entity_type", existing.get("entity_type", "unknown")),
        }
        if str(existing.get("value")) != str(claim_data["value"]):
            claim["review_state"] = "drafted"
            claim["value_changed_from"] = existing.get("value")
            claim["value_changed_at"] = now_iso()
        # Carry through extra fields (e.g. dual_vote metadata)
        for k, v in claim_data.items():
            if k not in claim:
                claim[k] = v
    else:
        claim = {
            "claim_id": claim_id,
            "entity_id": claim_data["entity_id"],
            "entity_type": claim_data.get("entity_type", "unknown"),
            "entity_name": claim_data.get("entity_name", ""),
            "attribute": attribute,
            "value": claim_data["value"],
            "unit": claim_data.get("unit", ""),
            "qualifiers": claim_data.get("qualifiers", {}),
            "source_ids": [source_id],
            "observed_at": now_iso(),
            "valid_from": today_str(),
            "confidence": claim_data.get("confidence", "medium"),
            "review_state": "drafted",
            "risk_class": claim_data.get("risk_class", "low"),
            "compiler_note": claim_data.get("compiler_note", ""),
        }
        # Carry through extra fields (e.g. dual_vote metadata)
        for k, v in claim_data.items():
            if k not in claim:
                claim[k] = v

    write_yaml(claim, claim_path)

    # Sync approved claim if it exists — NEVER overwrite approved value
    approved_dir = CLAIMS_APPROVED_DIR / "products" / claim_category
    approved_path = approved_dir / claim_filename
    if approved_path.exists():
        approved_claim = read_yaml(approved_path)
        if isinstance(approved_claim, dict):
            old_sources = approved_claim.get("source_ids", [])
            merged_sources = list(dict.fromkeys(old_sources + [source_id]))
            approved_claim["source_ids"] = merged_sources
            approved_claim["observed_at"] = now_iso()
            if str(approved_claim.get("value")) != str(claim_data["value"]):
                approved_claim["review_state"] = "needs_review"
                approved_claim["pending_value"] = claim_data["value"]
                approved_claim["pending_observed_at"] = now_iso()
            write_yaml(approved_claim, approved_path)

    return claim_path


def extract_claims_from_file(raw_file: Path, force: bool = False) -> dict:
    """Extract claims from a single raw file.

    Args:
        raw_file: Path to the raw markdown file
        force: If True, bypass SHA256 cache and re-extract

    Returns:
        Result dict with status, claims count, conflicts count
    """
    # ── SHA256 Cache Check ──────────────────────────────────
    if not force:
        cache = _load_cache()
        if _is_cached(raw_file, cache):
            cached_info = cache.get(str(raw_file.resolve()), {})
            log_entry("extract-claims", "cache-hit",
                      f"Cache hit: {raw_file.name} (unchanged, "
                      f"{cached_info.get('claims_count', '?')} claims cached)")
            return {
                "status": "cache-hit",
                "detail": f"File unchanged since {cached_info.get('extracted_at', 'unknown')}",
                "claims_count": cached_info.get("claims_count", 0),
                "cost_usd": 0,
                "cached": True,
            }

    log_entry("extract-claims", "start", f"Extracting: {raw_file.name}")

    content = raw_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    if not body or len(body.strip()) < 50:
        log_entry("extract-claims", "skip", f"File too short: {raw_file.name}")
        return {"status": "skip", "detail": "Content too short"}

    source_url = fm.get("source_url", "unknown")
    crawled_at = fm.get("crawled_at", now_iso())
    category = fm.get("suggested_category", "uncategorized")

    # [W5] Truncate at word boundary to avoid cutting mid-sentence/mid-table
    MAX_CHARS = 50_000
    if len(body) > MAX_CHARS:
        body_truncated = body[:MAX_CHARS].rsplit("\n", 1)[0]
    else:
        body_truncated = body

    # Build prompt
    prompt = EXTRACTION_PROMPT.format(
        raw_content=body_truncated,
        source_url=source_url,
        crawled_at=crawled_at,
    )

    # Call Gemini Pro (model selected by USE_PRO_NEW feature flag)
    try:
        result = generate(
            prompt=prompt,
            model=get_pro_model(),
            skill="extract-claims",
            temperature=0.1,
            max_output_tokens=32768,  # 8192 quá nhỏ: Gemini 2.5-pro thinking tokens eat into budget
        )
    except Exception as e:
        error_msg = f"Gemini API error: {str(e)}"
        log_entry("extract-claims", "error", error_msg, severity="critical")
        notify_error("extract-claims", error_msg)
        return {"status": "error", "detail": error_msg}

    # Parse JSON response
    claims = parse_claims_json(result["text"])
    if claims is None:
        log_entry("extract-claims", "error",
                  f"Cannot parse JSON output for {raw_file.name}",
                  severity="high")
        notify_error("extract-claims",
                      f"Extract failed: output không phải JSON cho {raw_file.name}")
        return {"status": "error", "detail": "JSON parse error"}

    # Validate and save claims
    saved_claims = []
    high_risk_count = 0
    low_risk_count = 0
    skipped = 0

    source_id = fm.get("source_id", f"SRC-{raw_file.stem.upper().replace('-', '_')}")

    for claim_data in claims:
        # Validate required fields
        missing = [f for f in CLAIM_REQUIRED_FIELDS if f not in claim_data]
        if missing:
            log_entry("extract-claims", "skip",
                      f"Claim missing fields: {missing}",
                      severity="medium")
            skipped += 1
            continue

        # Auto-set risk_class for high-risk attributes
        attribute = claim_data.get("attribute", "")
        if attribute in CLAIM_HIGH_RISK_ATTRIBUTES:
            claim_data["risk_class"] = "high"
        elif "risk_class" not in claim_data:
            claim_data["risk_class"] = "low"

        # Generate deterministic claim ID (no date → same fact = same ID)
        claim_id = generate_claim_id(
            claim_data["entity_id"],
            attribute,
        )

        # Determine correct category from entity_id (not suggested_category)
        cat_fallback = category.split("/")[-1] if "/" in category else category
        claim_category = determine_claim_category(
            claim_data["entity_id"], cat_fallback
        )

        # Save claim YAML — merge with existing if present
        claim_dir = CLAIMS_DRAFTS_DIR / "products" / claim_category
        ensure_dir(claim_dir)

        claim_filename = claim_id.lower().replace("-", "_") + ".yaml"
        claim_path = claim_dir / claim_filename

        # Load existing claim to merge source_ids and preserve history
        existing = read_yaml(claim_path) if claim_path.exists() else None
        if isinstance(existing, dict) and existing.get("claim_id") == claim_id:
            # Merge: accumulate source_ids, keep newest value
            old_sources = existing.get("source_ids", [])
            merged_sources = list(dict.fromkeys(old_sources + [source_id]))
            claim = {
                **existing,
                "value": claim_data["value"],
                "unit": claim_data.get("unit", existing.get("unit", "")),
                "qualifiers": claim_data.get("qualifiers", existing.get("qualifiers", {})),
                "source_ids": merged_sources,
                "observed_at": now_iso(),
                "confidence": claim_data.get("confidence", existing.get("confidence", "medium")),
                "risk_class": claim_data.get("risk_class", existing.get("risk_class", "low")),
                "compiler_note": claim_data.get("compiler_note", existing.get("compiler_note", "")),
                "entity_name": claim_data.get("entity_name", existing.get("entity_name", "")),
                "entity_type": claim_data.get("entity_type", existing.get("entity_type", "unknown")),
            }
            # If value changed, mark for re-review
            if str(existing.get("value")) != str(claim_data["value"]):
                claim["review_state"] = "drafted"
                claim["value_changed_from"] = existing.get("value")
                claim["value_changed_at"] = now_iso()
        else:
            # Brand new claim
            claim = {
                "claim_id": claim_id,
                "entity_id": claim_data["entity_id"],
                "entity_type": claim_data.get("entity_type", "unknown"),
                "entity_name": claim_data.get("entity_name", ""),
                "attribute": attribute,
                "value": claim_data["value"],
                "unit": claim_data.get("unit", ""),
                "qualifiers": claim_data.get("qualifiers", {}),
                "source_ids": [source_id],
                "observed_at": now_iso(),
                "valid_from": today_str(),
                "confidence": claim_data.get("confidence", "medium"),
                "review_state": "drafted",
                "risk_class": claim_data.get("risk_class", "low"),
                "compiler_note": claim_data.get("compiler_note", ""),
            }

        write_yaml(claim, claim_path)

        # Sync source_ids into approved claim if it exists.
        # [DATA INTEGRITY] NEVER overwrite approved value — only flag for re-review.
        # A hallucinated extraction must NOT silently corrupt ground-truth data.
        approved_dir = CLAIMS_APPROVED_DIR / "products" / claim_category
        approved_path = approved_dir / claim_filename
        if approved_path.exists():
            approved_claim = read_yaml(approved_path)
            if isinstance(approved_claim, dict):
                old_sources = approved_claim.get("source_ids", [])
                merged_sources = list(dict.fromkeys(old_sources + [source_id]))
                approved_claim["source_ids"] = merged_sources
                approved_claim["observed_at"] = now_iso()
                if str(approved_claim.get("value")) != str(claim_data["value"]):
                    # Store the new candidate value without touching approved value.
                    # Human must compare pending_value vs value and decide.
                    approved_claim["review_state"] = "needs_review"
                    approved_claim["pending_value"] = claim_data["value"]
                    approved_claim["pending_observed_at"] = now_iso()
                    # value field intentionally untouched — keeps ground truth intact
                write_yaml(approved_claim, approved_path)

        # Save JSONL trace
        trace = {
            "ts": now_iso(),
            "action": "extracted",
            "claim_id": claim_id,
            "source": source_id,
            "raw_file": str(raw_file.relative_to(raw_file.parent.parent.parent)),
            "model": get_pro_model(),
            "cost_usd": result.get("cost_usd", 0),
        }
        trace_path = claim_dir / (claim_id.lower().replace("-", "_") + ".jsonl")
        with open(trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace, ensure_ascii=False) + "\n")

        saved_claims.append(claim)
        if claim["risk_class"] == "high":
            high_risk_count += 1
        else:
            low_risk_count += 1

    # Update entity registry
    update_entity_registry(claims)

    # Update raw file status
    update_raw_status(raw_file, "extracted")

    # [C1] Pre-load approved index once, pass into detect_conflicts
    approved_index = _load_approved_claims_index()

    # Conflict detection
    conflicts = detect_conflicts(saved_claims, approved_index)
    for conflict in conflicts:
        send_conflict_alert(
            conflict["entity_id"],
            conflict["attribute"],
            str(conflict["old_value"]),
            str(conflict["new_value"]),
        )

    # Notify admin
    notify_skill("extract-claims",
                  f"Trích {len(saved_claims)} claims từ {raw_file.name}\n"
                  f"• {high_risk_count} high-risk (cần duyệt riêng)\n"
                  f"• {low_risk_count} low-risk (auto-draft)\n"
                  f"• {len(conflicts)} conflicts phát hiện\n"
                  f"• {skipped} claims bỏ qua (thiếu fields)\n"
                  f"Cost: ${result.get('cost_usd', 0):.4f}",
                  severity="success")

    log_entry("extract-claims", "success",
              f"Extracted {len(saved_claims)} claims from {raw_file.name}",
              cost_usd=result.get("cost_usd", 0))

    # ── Update SHA256 Cache ─────────────────────────────────
    cache = _load_cache()
    _update_cache(raw_file, cache, len(saved_claims), result.get("cost_usd", 0))
    _save_cache(cache)

    return {
        "status": "success",
        "claims_count": len(saved_claims),
        "high_risk": high_risk_count,
        "low_risk": low_risk_count,
        "conflicts": len(conflicts),
        "skipped": skipped,
        "cost_usd": result.get("cost_usd", 0),
    }


def parse_claims_json(text: str) -> list | None:
    """Parse JSON array from LLM output with multiple fallback strategies.

    Gemini 2.5 Pro may wrap JSON in:
    - Markdown code fences (```json ... ```)
    - Thinking blocks
    - Extra explanation text before/after
    """
    text = text.strip()

    # Strategy 1: Remove ```json fences and try direct parse
    cleaned = re.sub(r"```json\s*", "", text)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Strategy 2: Find the outermost [...] using bracket matching
    first_bracket = text.find("[")
    if first_bracket != -1:
        depth = 0
        last_bracket = -1
        for i in range(first_bracket, len(text)):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
                if depth == 0:
                    last_bracket = i
                    break

        if last_bracket > first_bracket:
            candidate = text[first_bracket:last_bracket + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # Try fixing common JSON issues
                fixed = candidate
                # Fix trailing commas before ] or }
                fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
                # Fix single quotes → double quotes (careful with values)
                try:
                    parsed = json.loads(fixed)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass

    # Strategy 3: Find all {...} objects and wrap in array
    objects = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                candidate = text[start:i + 1]
                try:
                    obj = json.loads(candidate)
                    if isinstance(obj, dict) and "entity_id" in obj:
                        objects.append(obj)
                except json.JSONDecodeError:
                    # Try fixing trailing commas
                    fixed = re.sub(r",\s*([}\]])", r"\1", candidate)
                    try:
                        obj = json.loads(fixed)
                        if isinstance(obj, dict) and "entity_id" in obj:
                            objects.append(obj)
                    except json.JSONDecodeError:
                        pass

    if objects:
        return objects

    return None


def _load_approved_claims_index() -> dict:
    """[C1] Pre-load all approved claims into memory as (entity_id, attribute) → claim.

    Avoids O(N×M) file reads in detect_conflicts() by scanning approved dir once.
    """
    import yaml
    index = {}
    if not CLAIMS_APPROVED_DIR.exists():
        return index
    for approved_file in CLAIMS_APPROVED_DIR.rglob("*.yaml"):
        try:
            old = yaml.safe_load(approved_file.read_text(encoding="utf-8"))
            if not isinstance(old, dict):
                continue
            key = (old.get("entity_id"), old.get("attribute"))
            if key[0] and key[1]:
                index[key] = old
        except Exception:
            continue
    return index


def detect_conflicts(new_claims: list[dict],
                     approved_index: dict | None = None) -> list[dict]:
    """[C1] Compare new claims vs approved claims, find mismatches.

    Args:
        new_claims: Freshly extracted claims from this run.
        approved_index: Pre-loaded approved claims index from
            _load_approved_claims_index(). If None, loads on demand
            (slower — for backwards-compat single-call use).
    """
    if approved_index is None:
        approved_index = _load_approved_claims_index()

    conflicts = []
    for new in new_claims:
        key = (new.get("entity_id"), new.get("attribute"))
        old = approved_index.get(key)
        if old is None:
            continue
        if old.get("review_state") != "approved":
            continue
        if str(old.get("value")) != str(new.get("value")):
            conflicts.append({
                "entity_id": new["entity_id"],
                "attribute": new["attribute"],
                "old_value": old["value"],
                "new_value": new["value"],
                "old_claim": old.get("claim_id"),
                "new_claim": new.get("claim_id"),
            })
    return conflicts


def update_raw_status(raw_file: Path, new_status: str):
    """Update status field in raw file frontmatter."""
    content = raw_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    fm["status"] = new_status
    write_markdown_with_frontmatter(raw_file, fm, body)


def update_entity_registry(claims: list[dict]):
    """[C5] Add new entities to registry with exclusive file lock.

    Uses fcntl.flock to prevent concurrent writes corrupting registry.yaml
    when multiple extract processes run simultaneously (e.g., batch_pipeline).
    """
    if not claims:
        return

    ensure_dir(ENTITIES_REGISTRY.parent)
    lock_path = ENTITIES_REGISTRY.parent / "registry.lock"

    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            registry = read_yaml(ENTITIES_REGISTRY)
            if not isinstance(registry, dict):
                registry = {"entities": []}

            entities = registry.get("entities", [])
            existing_ids = {e.get("entity_id") for e in entities}

            for claim in claims:
                entity_id = claim.get("entity_id", "")
                entity_name = claim.get("entity_name", "")
                entity_type = claim.get("entity_type", "")

                if entity_id not in existing_ids and entity_name:
                    entities.append({
                        "entity_id": entity_id,
                        "name": entity_name,
                        "type": entity_type,
                        "status": "draft",
                        "description": "Auto-discovered from extraction",
                    })
                    existing_ids.add(entity_id)

            registry["entities"] = entities
            write_yaml(registry, ENTITIES_REGISTRY)
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def extract_all_pending(force: bool = False) -> list[dict]:
    """Extract claims from all pending raw files.

    Args:
        force: If True, bypass SHA256 cache and re-extract all files
    """
    pending = find_pending_files()

    if not pending:
        print("Không có dữ liệu mới cần extract.")
        notify_skill("extract-claims", "Không có dữ liệu mới cần extract.", severity="info")
        return []

    print(f"Found {len(pending)} pending file(s)")
    if not force:
        print(f"💾 SHA256 cache enabled — unchanged files sẽ được skip")
    else:
        print(f"⚠️  Force mode — bypass cache, re-extract tất cả")

    results = []
    cached_count = 0
    extracted_count = 0

    for i, raw_file in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}] {raw_file.name}", end="")
        result = extract_claims_from_file(raw_file, force=force)
        results.append({"file": raw_file.name, **result})

        if result.get("cached"):
            cached_count += 1
            print(f" → ⏭️  cache-hit (unchanged)")
        else:
            extracted_count += 1
            print(f" → {result['status']}: {result.get('claims_count', 0)} claims")

    # Summary
    total_claims = sum(r.get("claims_count", 0) for r in results)
    total_cost = sum(r.get("cost_usd", 0) for r in results)
    total_conflicts = sum(r.get("conflicts", 0) for r in results)
    saved_cost = sum(
        _load_cache().get(str(Path(r["file"]).resolve()), {}).get("cost_usd", 0)
        for r in results if r.get("cached")
    )

    print(f"\n{'='*50}")
    print(f"📊 Extract Summary")
    print(f"  Extracted:    {extracted_count} files (new/changed)")
    print(f"  Cache hits:   {cached_count} files (unchanged, skipped)")
    print(f"  Total claims: {total_claims}")
    print(f"  Conflicts:    {total_conflicts}")
    print(f"  Cost:         ${total_cost:.4f}")
    if cached_count > 0:
        print(f"  💰 Saved:     ~${saved_cost:.4f} (by skipping {cached_count} cached files)")
    print(f"{'='*50}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Extract Claims")
    parser.add_argument("files", nargs="*", help="Specific raw files to extract")
    parser.add_argument("--force", action="store_true",
                        help="Bypass SHA256 cache, re-extract all files")
    parser.add_argument("--cache-stats", action="store_true",
                        help="Show cache statistics and exit")
    args = parser.parse_args()

    if args.cache_stats:
        show_cache_stats()
        return

    if args.files:
        for f in args.files:
            path = Path(f)
            if path.exists():
                extract_claims_from_file(path, force=args.force)
            else:
                print(f"File not found: {f}")
    else:
        extract_all_pending(force=args.force)


if __name__ == "__main__":
    main()
