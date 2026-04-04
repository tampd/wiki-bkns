# Skill 2: extract-claims

> **Phase:** 0.5 | **Model:** Gemini 2.5 Pro | **Cost:** ~$0.01-0.05/file
> **Nguyên tắc:** "Raw data → structured facts. Claims là đơn vị tri thức gốc."

---

## SKILL.md

```yaml
---
name: extract-claims
description: >
  Đọc file raw/ (status=pending_extract), dùng Gemini Pro trích xuất facts
  thành claims YAML có cấu trúc. Mỗi fact = 1 claim file + 1 JSONL trace.
  Phát hiện conflict vs claims/approved/ hiện có.
  KHÔNG tự approve — mọi claims mới ở trạng thái drafted.
  Trigger: /extract hoặc tự động sau crawl-source thành công.
version: "1.0"
phase: "0.5"
model: gemini-2.5-pro
admin_only: true
user-invocable: true
triggers:
  - command: /extract
---
```

---

## Workflow

```
BƯỚC 1: Scan raw/ tìm file status=pending_extract
  └─ Nếu không có → báo "Không có dữ liệu mới cần extract"

BƯỚC 2: Đọc nội dung raw file (tối đa 50k chars)

BƯỚC 3: Gửi Gemini Pro với EXTRACTION PROMPT
  ├─ Input: raw content + source metadata
  └─ Output: JSON array claim objects

BƯỚC 4: Validate output
  ├─ Mỗi claim phải có: entity_id, attribute, value, source_ids
  ├─ Claim thiếu field bắt buộc → LOG WARNING, skip claim đó
  └─ value là giá tiền → risk_class = high (bắt buộc review)

BƯỚC 5: Ghi claims
  ├─ YAML: claims/.drafts/{entity_type}/{claim_id}.yaml
  └─ JSONL trace: claims/.drafts/{entity_type}/{claim_id}.jsonl

BƯỚC 6: Cập nhật entities/registry.yaml
  └─ Thêm entity mới (status: draft) nếu chưa có

BƯỚC 7: Cập nhật raw file status
  └─ pending_extract → extracted

BƯỚC 8: Conflict Detection
  ├─ So sánh claims mới vs claims/approved/ hiện có
  ├─ Cùng entity+attribute + khác value → TẠO CONFLICT
  └─ Notify admin ngay: "⚠️ Conflict: [entity].[attr] wiki={X} vs mới={Y}"

BƯỚC 9: Báo admin Telegram
  └─ "📋 extract-claims: Trích {N} claims từ {filename}
      • {M} high-risk (cần duyệt riêng)
      • {K} low-risk (auto-draft)
      • {C} conflicts phát hiện
      Gõ /claims để xem danh sách."
```

---

## Extraction Prompt

```
Bạn là chuyên gia trích xuất dữ liệu (data extraction specialist) cho BKNS.

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
  {
    "entity_id": "product.hosting.bkcp01",
    "entity_type": "product_plan",
    "entity_name": "BKCP01",
    "attribute": "monthly_price",
    "value": 26000,
    "unit": "VND",
    "qualifiers": {"billing_cycle": "month"},
    "confidence": "high",
    "risk_class": "high",
    "compiler_note": "Trích từ bảng giá: 'Gói BKCP01 - 26.000đ/tháng'"
  }
]

Ưu tiên extract: giá > specs > chính sách > mô tả.
Trả về JSON array DUY NHẤT, không giải thích thêm.
```

---

## Output: claims/.drafts/{category}/{claim_id}.yaml

```yaml
claim_id: CLM-HOST-BKCP01-PRICE-20260404
entity_id: product.hosting.bkcp01
attribute: monthly_price
value: 26000
unit: VND
qualifiers:
  billing_cycle: month
  tax_included: unknown
source_ids:
  - SRC-BKNS-WEB-HOSTING
observed_at: "2026-04-04T10:30:00+07:00"
valid_from: "2026-04-04"
confidence: high
review_state: drafted
risk_class: high
compiler_note: "Trích từ bảng giá: 'Gói BKCP01 - 26.000đ/tháng'"
```

## Output: JSONL Trace (song song)

```jsonl
{"ts":"2026-04-04T10:30:00+07:00","action":"extracted","claim_id":"CLM-HOST-BKCP01-PRICE-20260404","source":"SRC-BKNS-WEB-HOSTING","raw_file":"raw/website-crawl/hosting-2026-04-04.md","model":"gemini-2.5-pro"}
```

---

## Conflict Detection Logic

```python
def detect_conflicts(new_claims: list, approved_dir: Path) -> list:
    """So sánh claims mới vs approved, tìm mâu thuẫn."""
    conflicts = []
    for new in new_claims:
        for approved_file in approved_dir.rglob("*.yaml"):
            old = yaml.safe_load(approved_file.read_text())
            if (old["entity_id"] == new["entity_id"]
                    and old["attribute"] == new["attribute"]
                    and old.get("review_state") == "approved"):
                if str(old["value"]) != str(new["value"]):
                    conflicts.append({
                        "entity_id": new["entity_id"],
                        "attribute": new["attribute"],
                        "old_value": old["value"],
                        "new_value": new["value"],
                        "old_claim": old["claim_id"],
                        "new_claim": new["claim_id"],
                    })
    return conflicts
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Gemini API timeout | Retry 2 lần, interval 5s. Fail → báo admin |
| Output không phải JSON | Log raw output, báo admin "Extract failed" |
| Claim thiếu field bắt buộc | Skip claim đó, log warning, tiếp tục |
| Entity mới chưa có registry | Tự thêm vào entities/registry.yaml (status: draft) |
