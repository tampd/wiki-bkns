# Skill 2: extract-claims — Trích Xuất Facts Từ Raw

> **Phase:** 0.5 | **Model:** Gemini 2.5 Pro | **Cost:** ~$0.01-0.05/file
> **Triết lý Karpathy:** Raw data → structured facts. Claims là đơn vị tri thức gốc (addon.md §4.5)

---

## SKILL.md

```yaml
---
name: extract-claims
description: >
  Đọc file raw/ (pending_extraction), dùng Gemini Pro trích xuất facts có cấu trúc 
  thành claims YAML. Mỗi fact = 1 claim file. Tạo JSONL trace song song.
  KHÔNG tự approve — tất cả claims mới ở trạng thái draft.
  Trigger: /extract hoặc tự động sau crawl-source thành công.
user-invocable: true
---
```

## Workflow: raw/ → claims/

```
BƯỚC 1: Scan raw/ tìm file status=pending_extraction
  ├─ Đọc frontmatter → filter status
  └─ Nếu không có file pending → báo "Không có dữ liệu mới"

BƯỚC 2: Đọc nội dung raw file

BƯỚC 3: Gửi Gemini Pro với EXTRACTION PROMPT (bên dưới)
  ├─ Input: raw content + source metadata
  ├─ Output: JSON array of claim objects
  └─ Nếu API error → BÁO LỖI, giữ file ở pending

BƯỚC 4: Validate output
  ├─ Mỗi claim phải có: entity_id, attribute, value, source_ids
  ├─ Nếu thiếu field bắt buộc → LOG WARNING, skip claim đó
  └─ Nếu value là giá tiền → risk_class = high (bắt buộc review)

BƯỚC 5: Ghi claims
  ├─ YAML: claims/.drafts/{entity_type}/{claim_id}.yaml
  ├─ JSONL trace: claims/.drafts/{entity_type}/{claim_id}.jsonl
  └─ Cập nhật entities/registry.yaml nếu entity mới

BƯỚC 6: Cập nhật raw file status
  └─ status: pending_extraction → extracted

BƯỚC 7: Detect conflicts (gọi nội bộ)
  ├─ So sánh claims mới vs claims/approved/ hiện có
  ├─ Nếu cùng entity+attribute khác value → TẠO CONFLICT
  └─ Conflict → notify admin ngay lập tức

BƯỚC 8: Báo admin Telegram
  └─ "📋 extract-claims: Trích {N} claims từ {filename}
      • {M} high-risk (cần duyệt)
      • {K} low-risk (auto-draft)
      • {C} conflicts phát hiện
      Gõ /claims để xem danh sách."
```

## Extraction Prompt (Gemini Pro)

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
3. ❌ KHÔNG gộp nhiều facts vào 1 claim — mỗi fact riêng 1 claim
4. ✅ Giá tiền → 1 claim riêng, risk_class = high
5. ✅ Thông số kỹ thuật (RAM, CPU, SSD) → 1 claim riêng mỗi attribute
6. ✅ Hotline, email, địa chỉ → 1 claim riêng, risk_class = high
7. ✅ Ghi rõ đoạn văn gốc vào compiler_note
8. ✅ Nếu không chắc chắn → confidence = low

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
  },
  {
    "entity_id": "product.hosting.bkcp01",
    "entity_type": "product_plan",
    "entity_name": "BKCP01",
    "attribute": "disk_space",
    "value": 2,
    "unit": "GB",
    "qualifiers": {"type": "SSD"},
    "confidence": "high",
    "risk_class": "medium",
    "compiler_note": "Trích từ specs: 'Dung lượng: 2GB SSD'"
  }
]

Trích MỌI facts tìm thấy. Ưu tiên: giá > specs > chính sách > mô tả.
Trả về JSON array DUY NHẤT, không giải thích thêm.
```

## Claim YAML Output (claims/.drafts/)

```yaml
# claims/.drafts/products/hosting/CLM-HOST-BKCP01-PRICE-20260404.yaml
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

## JSONL Trace (song song)

```jsonl
{"ts":"2026-04-04T10:30:00+07:00","action":"extracted","claim_id":"CLM-HOST-BKCP01-PRICE-20260404","source":"SRC-BKNS-WEB-HOSTING","raw_file":"raw/website-crawl/hosting-2026-04-04.md","model":"gemini-2.5-pro"}
```

## Conflict Detection (Bước 7)

```python
def detect_conflicts(new_claims: list, approved_dir: Path) -> list:
    """So sánh claims mới vs approved, tìm mâu thuẫn."""
    conflicts = []
    for new in new_claims:
        # Tìm claims approved cùng entity+attribute
        for approved_file in approved_dir.rglob("*.yaml"):
            old = yaml.safe_load(approved_file.read_text())
            if (old["entity_id"] == new["entity_id"] and
                old["attribute"] == new["attribute"] and
                old["review_state"] == "approved"):
                # So sánh value
                if str(old["value"]) != str(new["value"]):
                    conflicts.append({
                        "entity_id": new["entity_id"],
                        "attribute": new["attribute"],
                        "old_value": old["value"],
                        "new_value": new["value"],
                        "old_claim": old["claim_id"],
                        "new_claim": new["claim_id"],
                        "suspected_cause": "source_mismatch" 
                            if old.get("source_ids") != new.get("source_ids")
                            else "time_window_difference",
                    })
    return conflicts
```

## Xử Lý Lỗi

| Lỗi | Hành động |
|-----|----------|
| Gemini API timeout | Retry 2 lần, interval 5s. Nếu fail → báo admin |
| Output không phải JSON | Log raw output, báo admin "Extract failed, cần review thủ công" |
| Claim thiếu field bắt buộc | Skip claim đó, log warning, tiếp tục claims khác |
| Entity mới chưa có trong registry | Tự thêm vào entities/registry.yaml (status: draft) |

---

*Skill tiếp: [10c-compile-wiki.md](./10c-compile-wiki.md) — Biên dịch claims → wiki Markdown*
