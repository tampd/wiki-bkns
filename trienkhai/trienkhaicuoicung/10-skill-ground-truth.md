# Skill 7: ground-truth

> **Phase:** 1 | **Model:** Flash + crawl script | **Cost:** ~$0.02-0.05/lần
> **Schedule:** Cron Sunday 22:00 + manual `/verify`

---

## SKILL.md

```yaml
---
name: ground-truth
description: >
  Crawl lại bkns.vn, so sánh dữ liệu live vs wiki claims hiện tại.
  Phát hiện: giá thay đổi, sản phẩm mới, sản phẩm bị xóa, specs thay đổi.
  Output: báo cáo diff + Telegram alert nếu có mismatch.
  Trigger: /verify hoặc cron weekly Sunday 22:00.
version: "1.0"
phase: "1"
model: gemini-2.5-flash
admin_only: true
user-invocable: true
triggers:
  - command: /verify
  - cron: "0 22 * * 0"
---
```

---

## Workflow

```
BƯỚC 1: Re-crawl bkns.vn (reuse crawl-source logic)
  ├─ Crawl các URL trong sources/registry.yaml
  ├─ KHÔNG lưu vào raw/ (chỉ đọc tạm trong memory)
  └─ Timeout 30s mỗi URL

BƯỚC 2: Extract facts từ crawl mới (reuse extract-claims logic)
  ├─ Dùng Gemini Flash (không cần Pro cho verify)
  ├─ KHÔNG tạo claim files
  └─ Chỉ lấy structured data để so sánh

BƯỚC 3: So sánh live data vs claims/approved/
  ├─ MATCH → ✅ ghi nhận OK
  ├─ MISMATCH → ⚠️ "Giá BKCP01: wiki=26.000đ, live=28.000đ"
  ├─ NEW → 📌 "Sản phẩm mới phát hiện: [tên]"
  └─ MISSING → ❓ "Sản phẩm trong wiki không còn trên web"

BƯỚC 4: Tạo report
  └─ logs/ground-truth/report-{date}.md

BƯỚC 5: Telegram alert
  ├─ Nếu MISMATCH hoặc MISSING → ngay lập tức alert admin
  └─ Nếu tất cả MATCH → summary nhẹ: "✅ Verify OK, wiki up to date"
```

---

## Ground Truth Comparison Prompt

```
So sánh dữ liệu wiki (hiện tại) vs dữ liệu website bkns.vn (vừa crawl):

WIKI CLAIMS (approved): {wiki_claims_json}
LIVE DATA (extracted từ bkns.vn): {live_extracted_json}

Tìm và liệt kê:
1. GIÁ THAY ĐỔI: entity wiki={X} VND → live={Y} VND
2. SPECS THAY ĐỔI: RAM/CPU/SSD/bandwidth khác
3. SẢN PHẨM MỚI: có trên live nhưng không có trong wiki
4. SẢN PHẨM BỊ XÓA: có trong wiki nhưng không còn trên live
5. THÔNG TIN LIÊN HỆ THAY ĐỔI: hotline, email, địa chỉ

OUTPUT (JSON):
{
  "checked_at": "ISO timestamp",
  "sources_checked": N,
  "matches": N,
  "mismatches": [
    {
      "entity": "product.hosting.bkcp01",
      "attribute": "monthly_price",
      "wiki_value": 26000,
      "live_value": 28000,
      "severity": "high"
    }
  ],
  "new_products": [...],
  "missing_products": [...],
  "contact_changes": [...]
}
```

---

## Report + Alert

```
⚠️ Ground Truth Alert — 2026-04-07
━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Kiểm tra: 5 nguồn, 45 claims
❌ Mismatch phát hiện: 2

• Hosting BKCP01: wiki=26.000đ → live=28.000đ
• VPS Basic RAM: wiki=2GB → live=4GB

📌 Sản phẩm mới: 1
• VPS Ultra: Chưa có trong wiki

Chi tiết: logs/ground-truth/report-2026-04-07.md
/them https://bkns.vn/vps để ingest trang mới
```

---

## Sau khi phát hiện Mismatch

Bot tự động:
1. Tạo file `raw/website-crawl/re-verify-{slug}-{date}.md` từ crawl mới
2. Gửi admin hướng dẫn: "Gõ `/extract` rồi `/compile` rồi `/duyet` để update wiki"
3. KHÔNG tự update wiki — luôn cần admin approve

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| bkns.vn không truy cập được | Retry 1 lần. Fail → "⚠️ ground-truth: Không crawl được bkns.vn" |
| Gemini Flash API error | Skip semantic compare, dùng script diff đơn giản |
| Tất cả MATCH | Gửi silent confirm: "✅ Wiki up to date (verified {N} claims)" |
