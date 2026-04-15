---
title: Hướng Dẫn Reviewer — BKNS Wiki Admin Portal
updated: 2026-04-15
audience: BKNS reviewer, editor, admin
---

# Hướng Dẫn Reviewer — BKNS Wiki

Tài liệu này dành cho người trực tiếp thao tác phê duyệt claims và xử lý xung đột dữ liệu tại https://upload.trieuphu.biz.

Mục tiêu: biến quy trình review từ "biết code là hiểu" thành "ai đọc cũng thao tác được".

---

## 1. Tổng quan 30 giây

Wiki BKNS được "đúc" từ **claims** — mỗi claim là một fact đơn lẻ (giá hosting X = 50K/tháng). Claims qua 3 trạng thái:

```
drafted (nháp, LLM vừa extract)
    ↓ reviewer phê duyệt
approved (đã duyệt, ăn vào wiki)
    ↓ ổn định + được confirm nhiều nguồn
ground_truth (chân lý — không bao giờ bị LLM ghi đè)
```

Reviewer có 3 nhiệm vụ chính:
1. **Duyệt claim** (approve / reject / flag) trong tab **Review**
2. **Giải xung đột** (conflict resolution) khi 2 nguồn khai giá khác nhau
3. **Xử lý dual-vote queue** khi Gemini và GPT không đồng ý

---

## 2. Thao tác cơ bản trong tab Review

### 2.1 Mở và filter

1. Đăng nhập https://upload.trieuphu.biz
2. Chọn tab **Review**
3. Dropdown filter:
   - `all` — Tất cả đang chờ (không bao gồm đã approve/reject)
   - `flagged` — Đã flag cần xem lại
   - `conflicts` — Các entity có ≥2 giá trị khác nhau
   - `unverified` — Confidence thấp (medium/low)
   - `image-based` — Claims trích từ ảnh (OCR, dễ sai)
   - `approved` / `rejected` — Xem lịch sử

### 2.2 Duyệt 1 claim

Mỗi card hiển thị:
- **Entity**: sản phẩm liên quan (ví dụ `prod.bkns.hosting.platinum`)
- **Attribute**: thuộc tính (ví dụ `monthly_price`)
- **Value**: giá trị LLM trích (ví dụ `55000 VND`)
- **Source**: nguồn gốc (URL hoặc tên file Excel)
- **Confidence**: ground_truth / high / medium / low

**Quyết định:**
- ✅ **Approve** — Đúng với nguồn, không mâu thuẫn. Bấm nút Approve.
- ❌ **Reject** — Sai rõ ràng hoặc đã cũ. Ghi **lý do bắt buộc** vào ô reason.
- 🟡 **Flag** — Nghi ngờ nhưng chưa chắc → để người khác review sau. Ghi ngắn gọn lý do.

**Nguyên tắc vàng**: Nếu phân vân > 10 giây → FLAG, không approve mù.

### 2.3 Bulk action (duyệt hàng loạt)

Khi có nhiều claims tương tự (ví dụ: cùng một đợt extract) bạn có thể chọn nhiều rồi dùng Bulk:

1. Tick checkbox các hàng cần xử lý (≤ 300 mỗi lần)
2. Chọn action: Approve / Reject / Flag
3. Ghi `reason` chung (bắt buộc với reject)
4. **Atomic mode** (tick nếu cần): nếu 1 claim fail → rollback toàn bộ. Dùng khi các claims phụ thuộc nhau (ví dụ: bảng giá trọn gói).
5. Submit

Kết quả trả về: `success_count` và `failed_ids` → xem lại các id fail để xử lý thủ công.

---

## 3. Xử lý Conflict (xung đột giá trị)

### 3.1 Khi nào có conflict?

Conflict = cùng một `entity_id + attribute` có ≥ 2 giá trị khác nhau. Ví dụ:

```
prod.bkns.hosting.platinum / monthly_price
  ├─ claim A: 55000 VND  (từ bang-gia-2026.xlsx, confidence: ground_truth)
  └─ claim B: 58000 VND  (từ crawl web 2026-04-13, confidence: high)
```

### 3.2 Quyết định theo thứ tự ưu tiên

1. **Ưu tiên confidence**: `ground_truth` > `high` > `medium` > `low`
2. **Ưu tiên thời gian**: claim mới hơn (nếu cùng confidence)
3. **Ưu tiên nguồn chính thức**: Excel BKNS > web bkns.vn > crawl 3rd party
4. **Ưu tiên claim có đủ metadata**: có `source_ids`, `observed_at`, `compiler_note`

### 3.3 Thao tác trong UI

1. Tab **Review** → filter `conflicts`
2. Mỗi conflict group hiển thị tất cả giá trị đang tranh chấp
3. Chọn **Resolve**:
   - **Pick winner**: chọn 1 claim làm giá đúng → các claim còn lại tự động reject với lý do `conflict_loser`
   - **Merge**: nếu cả hai đều đúng nhưng khác ngữ cảnh (ví dụ: giá trước/sau khuyến mãi) → manual edit để tách attribute
   - **All wrong**: nếu cả hai đều sai → reject hết + flag entity để xử lý thủ công

4. **Phải ghi lý do** vào ô note (sẽ vào audit log)

### 3.4 Khi không chắc

Nếu không có nguồn chính thức để đối chiếu:
- **FLAG toàn bộ group** với reason `need_excel_source`
- Hỏi trực tiếp team BKNS để có bảng giá chuẩn
- Tuyệt đối KHÔNG approve bừa — ưu tiên chính xác hơn coverage

---

## 4. Dual-Vote Queue

### 4.1 Dual-vote là gì?

Các category quan trọng (hosting, vps, ssl, email, server, ten-mien) luôn được 2 model LLM trích độc lập (Gemini Pro + GPT-5.4). Kết quả so sánh:
- **AGREE** (similarity ≥ 0.9) → tự approve
- **PARTIAL** (0.6–0.89) → vào queue, cần review
- **DISAGREE** (< 0.6) → vào queue, cần review

### 4.2 Thao tác

1. Tab **Review** → section **Dual-Vote Queue** (hoặc URL `/app?tab=review&view=dual`)
2. Mỗi item hiển thị:
   - `text_a` — Output Gemini Pro
   - `text_b` — Output GPT-5.4
   - `prompt_preview` — Đoạn đầu của prompt gốc để bạn hiểu ngữ cảnh
3. Quyết định:
   - **pick_a** — Output Gemini đúng hơn
   - **pick_b** — Output GPT đúng hơn
   - **reject_both** — Cả hai đều sai → claim bị xoá, cần re-extract thủ công

### 4.3 Quy tắc chọn

| Tình huống | Chọn gì |
|---|---|
| Gemini trích đầy đủ số liệu, GPT bỏ sót | pick_a |
| GPT format JSON sạch hơn, dữ liệu tương tự | pick_b |
| Cả hai đều bịa thêm features không có trong nguồn | reject_both |
| Một cái đưa VND, một cái đưa USD (cùng giá) | pick_a (giữ VND vì BKNS bán VN) |
| Một cái lỗi markdown fence | pick cái còn lại + log bug |

---

## 5. Promotion lên Ground Truth

Sau khi claims `high` + `approved` đã ổn định (≥ 2 tuần không conflict), có thể promote lên `ground_truth`:

1. Tab **Review** → button **Promote to Ground Truth**
2. **Luôn dry-run trước** (checkbox `--dry-run`): xem preview sẽ promote bao nhiêu + entity nào
3. Đọc kỹ preview — nếu có entity lạ thì dừng lại
4. Uncheck dry-run → confirm

⚠️ **Ground truth không bị LLM ghi đè nữa** → sai một claim = sai vĩnh viễn cho đến khi có người sửa thủ công. Cẩn thận.

---

## 6. Audit Trail (lịch sử review)

Mọi thao tác được ghi vào `logs/approve-YYYY-MM-DD.jsonl` (per-claim, bất kể single hay bulk).

Xem lịch sử 1 claim qua API:
```
GET /api/review/audit?claim_id=CLM-XXX&days=30
```

Response:
```json
{
  "claim_id": "CLM-HOST-PLATINUM-MONTHLY",
  "count": 3,
  "history": [
    {"reviewed_at": "2026-04-10T...", "review_state": "flagged", "review_note": "giá cao bất thường", "reviewed_by": "admin"},
    {"reviewed_at": "2026-04-12T...", "review_state": "rejected", "review_note": "sai, xem Excel 2026-Q2", "reviewed_by": "admin"},
    {"reviewed_at": "2026-04-15T...", "review_state": "approved", "review_note": "đã fix từ nguồn chính thức", "reviewed_by": "admin"}
  ]
}
```

---

## 7. Checklist "Đã duyệt xong 1 phiên"

Trước khi đóng tab, đảm bảo:

- [ ] `conflicts` filter trả về 0 group, HOẶC mọi group đã resolve/flag
- [ ] Dual-Vote queue không còn item `PARTIAL`/`DISAGREE` cũ hơn 7 ngày
- [ ] Các claim reject đều có reason ≥ 1 câu (không phải rỗng)
- [ ] Bulk actions không có `failed_ids` chưa xử lý
- [ ] Không còn flag `image-based` nào chưa xem qua (OCR dễ sai)

---

## 8. Khi nào ESCALATE cho admin

- Gặp ≥ 3 claim cùng entity có giá khác xa (≥ 50%) → có vấn đề với nguồn
- Dual-vote DISAGREE với score < 0.3 nhiều hơn 5 lần/ngày → LLM có bug
- Bulk atomic rollback liên tục → có file YAML corrupt
- Audit trail trả về entry thiếu trường `reviewed_by` → log format đổi, cần điều tra

Escalate qua: đăng nhập bot Telegram BKNS Wiki → `/status` → gửi message hoặc liên hệ trực tiếp admin server.

---

## 9. Tham khảo nhanh

| Việc cần làm | Vị trí trong UI | API tương ứng |
|---|---|---|
| Duyệt 1 claim | Review → card → Approve | POST `/api/review/approve` |
| Duyệt hàng loạt | Review → checkbox + Bulk | POST `/api/review/bulk` (atomic optional) |
| Xem conflicts | Review → filter `conflicts` | GET `/api/review/conflicts` |
| Resolve conflict | Conflict group → Resolve button | POST `/api/review/resolve-conflict` |
| Dual-vote decide | Review → Dual-Vote section | POST `/api/review/dual/:id/decide` |
| Promote ground truth | Review → Promote button | POST `/api/review/promote-groundtruth` |
| Xem lịch sử 1 claim | (chưa có UI) | GET `/api/review/audit?claim_id=X` |

---

*Câu hỏi / bug → báo lại trong file `logs/reviewer-issues.md` hoặc nhắn admin qua Telegram.*
