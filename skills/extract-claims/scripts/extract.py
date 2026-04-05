#!/usr/bin/env python3
"""
BKNS Agent Wiki — extract-claims
Đọc raw/ files → Gemini Pro extract → claims YAML + JSONL trace.
Conflict detection vs claims/approved/.

Usage:
    python3 scripts/extract.py              # Extract all pending
    python3 scripts/extract.py [raw_file]   # Extract specific file
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    RAW_CRAWL_DIR, RAW_MANUAL_DIR, CLAIMS_DRAFTS_DIR, CLAIMS_APPROVED_DIR,
    ENTITIES_REGISTRY, CLAIM_REQUIRED_FIELDS, CLAIM_HIGH_RISK_ATTRIBUTES,
    MODEL_PRO,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import notify_skill, notify_error, send_conflict_alert
from lib.utils import (
    parse_frontmatter, read_yaml, write_yaml, now_iso, today_str,
    generate_claim_id, ensure_dir, write_markdown_with_frontmatter,
)


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


def extract_claims_from_file(raw_file: Path) -> dict:
    """Extract claims from a single raw file.

    Returns:
        Result dict with status, claims count, conflicts count
    """
    log_entry("extract-claims", "start", f"Extracting: {raw_file.name}")

    content = raw_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    if not body or len(body.strip()) < 50:
        log_entry("extract-claims", "skip", f"File too short: {raw_file.name}")
        return {"status": "skip", "detail": "Content too short"}

    source_url = fm.get("source_url", "unknown")
    crawled_at = fm.get("crawled_at", now_iso())
    category = fm.get("suggested_category", "uncategorized")

    # Truncate content to 50k chars
    body_truncated = body[:50000]

    # Build prompt
    prompt = EXTRACTION_PROMPT.format(
        raw_content=body_truncated,
        source_url=source_url,
        crawled_at=crawled_at,
    )

    # Call Gemini Pro
    try:
        result = generate(
            prompt=prompt,
            model=MODEL_PRO,
            skill="extract-claims",
            temperature=0.1,
            max_output_tokens=8192,
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

        # Generate claim ID
        claim_id = generate_claim_id(
            claim_data["entity_id"],
            attribute,
        )

        # Determine category path
        cat_parts = category.split("/")
        if len(cat_parts) >= 2:
            claim_category = cat_parts[1]
        else:
            claim_category = cat_parts[0]

        # Build claim YAML
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

        # Save claim YAML
        claim_dir = CLAIMS_DRAFTS_DIR / "products" / claim_category
        ensure_dir(claim_dir)

        claim_filename = claim_id.lower().replace("-", "_") + ".yaml"
        claim_path = claim_dir / claim_filename
        write_yaml(claim, claim_path)

        # Save JSONL trace
        trace = {
            "ts": now_iso(),
            "action": "extracted",
            "claim_id": claim_id,
            "source": source_id,
            "raw_file": str(raw_file.relative_to(raw_file.parent.parent.parent)),
            "model": MODEL_PRO,
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

    # Conflict detection
    conflicts = detect_conflicts(saved_claims)
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


def detect_conflicts(new_claims: list[dict]) -> list[dict]:
    """Compare new claims vs approved claims, find mismatches."""
    conflicts = []

    if not CLAIMS_APPROVED_DIR.exists():
        return conflicts

    for new in new_claims:
        for approved_file in CLAIMS_APPROVED_DIR.rglob("*.yaml"):
            try:
                import yaml
                old = yaml.safe_load(approved_file.read_text(encoding="utf-8"))
                if not isinstance(old, dict):
                    continue

                if (old.get("entity_id") == new["entity_id"]
                        and old.get("attribute") == new["attribute"]
                        and old.get("review_state") == "approved"):
                    if str(old.get("value")) != str(new.get("value")):
                        conflicts.append({
                            "entity_id": new["entity_id"],
                            "attribute": new["attribute"],
                            "old_value": old["value"],
                            "new_value": new["value"],
                            "old_claim": old.get("claim_id"),
                            "new_claim": new.get("claim_id"),
                        })
            except Exception:
                continue

    return conflicts


def update_raw_status(raw_file: Path, new_status: str):
    """Update status field in raw file frontmatter."""
    content = raw_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    fm["status"] = new_status
    write_markdown_with_frontmatter(raw_file, fm, body)


def update_entity_registry(claims: list[dict]):
    """Add new entities to registry if not exists."""
    if not claims:
        return

    registry = read_yaml(ENTITIES_REGISTRY)
    if not isinstance(registry, dict):
        registry = {"entities": []}

    entities = registry.get("entities", [])
    existing_ids = {e.get("entity_id") for e in entities}

    for claim in claims:
        entity_id = claim.get("entity_id", "")
        entity_name = claim.get("entity_name", "")
        entity_type = claim.get("entity_type", "")

        # Map to entity registry ID format
        if entity_id not in existing_ids and entity_name:
            entities.append({
                "entity_id": entity_id,
                "name": entity_name,
                "type": entity_type,
                "status": "draft",
                "description": f"Auto-discovered from extraction",
            })
            existing_ids.add(entity_id)

    registry["entities"] = entities
    write_yaml(registry, ENTITIES_REGISTRY)


def extract_all_pending() -> list[dict]:
    """Extract claims from all pending raw files."""
    pending = find_pending_files()

    if not pending:
        print("Không có dữ liệu mới cần extract.")
        notify_skill("extract-claims", "Không có dữ liệu mới cần extract.", severity="info")
        return []

    print(f"Found {len(pending)} pending file(s)")
    results = []

    for i, raw_file in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}] Extracting: {raw_file.name}")
        result = extract_claims_from_file(raw_file)
        results.append({"file": raw_file.name, **result})
        print(f"  → {result['status']}: {result.get('claims_count', 0)} claims")

    # Summary
    total_claims = sum(r.get("claims_count", 0) for r in results)
    total_cost = sum(r.get("cost_usd", 0) for r in results)
    total_conflicts = sum(r.get("conflicts", 0) for r in results)

    print(f"\n{'='*50}")
    print(f"Extract Summary: {total_claims} claims, {total_conflicts} conflicts, ${total_cost:.4f}")
    print(f"{'='*50}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Extract Claims")
    parser.add_argument("files", nargs="*", help="Specific raw files to extract")
    args = parser.parse_args()

    if args.files:
        for f in args.files:
            path = Path(f)
            if path.exists():
                extract_claims_from_file(path)
            else:
                print(f"File not found: {f}")
    else:
        extract_all_pending()


if __name__ == "__main__":
    main()
