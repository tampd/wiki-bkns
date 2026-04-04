# Skill 5: ingest-image

> **Phase:** 1 | **Model:** Gemini 2.5 Flash Vision | **Cost:** ~$0.01-0.03/ảnh

---

## SKILL.md

```yaml
---
name: ingest-image
description: >
  Nhận ảnh bảng giá/screenshot từ Telegram, lưu evidence vào Git LFS,
  dùng Gemini Flash Vision extract thành claims draft.
  Ảnh gốc → assets/evidence/ (Git LFS). Thumbnail → assets/images/.
  Claims → wiki/.drafts/ (chờ /duyet).
  Trigger: admin gửi ảnh kèm caption "bảng giá" / "giá" hoặc /anh.
version: "1.0"
phase: "1"
model: gemini-2.5-flash
admin_only: true
user-invocable: true
triggers:
  - type: image
    caption_pattern: ".*bang.gia.*|.*gia.*|.*price.*"
  - command: /anh
---
```

---

## Workflow

```
BƯỚC 1: Nhận ảnh từ Telegram
  ├─ Lưu gốc: assets/evidence/price-screens/{name}-{date}-original.{ext}
  │   → Git LFS tracked
  └─ Tạo thumbnail: assets/images/{name}-{date}-thumb.jpg
      → Resize max 800px, compress quality 70

BƯỚC 2: Gemini Flash Vision extract
  ├─ Gửi ảnh + Vision Extract Prompt (bên dưới)
  └─ Output: JSON array claims (cùng format extract-claims)

BƯỚC 3: Validate kết quả Vision
  ├─ Giá = 0 hoặc âm → cảnh báo
  ├─ Giá quá lớn (>100M VND/tháng) → cảnh báo
  └─ [KHÔNG RÕ] trong value → confidence = low

BƯỚC 4: Tạo Evidence record
  └─ evidence_id: EVD-IMG-{YYYYMMDD}-{seq}
     kind: image
     paths: {evidence + thumbnail}
     hash: sha256 của ảnh gốc
     human_verified: false

BƯỚC 5: Tạo claims draft
  ├─ claims/.drafts/{category}/{claim_id}.yaml
  ├─ evidence_refs: [evidence_id]
  └─ risk_class: high (ảnh luôn cần review vì không verify được tự động)

BƯỚC 6: Self-review
  ├─ Bot đọc lại extract, kiểm tra số có hợp lý
  └─ So sánh với claims/approved/ hiện có → detect conflicts

BƯỚC 7: Hỏi admin xác nhận
  └─ "📷 Tôi extract được {N} mục giá từ ảnh [category].
      Preview:
      | Gói | Giá |
      |-----|-----|
      | ... | ... |
      
      Gõ /duyet-anh để xác nhận và tạo wiki draft."
```

---

## Vision Extract Prompt

```
Extract TOÀN BỘ bảng giá trong ảnh thành JSON claims.

QUY TẮC:
1. Giữ nguyên số liệu: giá, RAM, CPU, SSD, bandwidth
2. Chuẩn hóa đơn vị: tiền → VND (không dùng "đ" hay "k"), dung lượng → GB/TB
3. Nếu ô mờ/không đọc được → value: "[KHÔNG RÕ]", confidence: "low"
4. KHÔNG suy luận giá trị bị che hoặc bị mờ
5. Mỗi dòng bảng giá = 1 claim object riêng
6. Gói sản phẩm cùng nhóm → cùng entity_id prefix

OUTPUT (JSON array — cùng format extract-claims):
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
    "compiler_note": "Dòng 1 bảng giá, cột 'Giá/tháng'"
  }
]

Trả về JSON array DUY NHẤT.
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Ảnh quá mờ (extract = rỗng) | "❌ Không extract được. Vui lòng gửi ảnh rõ hơn." |
| Ảnh không phải bảng giá | "⚠️ Không nhận diện được bảng giá trong ảnh." |
| File quá lớn (>20MB) | "❌ Ảnh quá lớn. Tối đa 20MB." |
| Git LFS not configured | Lưu assets/images/ thay thế, log warning |
