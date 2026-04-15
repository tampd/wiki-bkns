---
artifact: regression-review
part: 07
created: 2026-04-14
status: pending_human_review
---

# Regression Review — v0.3 vs v0.4 (Human Review)

> **Hướng dẫn**: Mở từng wiki page v0.4 và so sánh với v0.3 snapshot + trang BKNS.VN thực tế.
> - ✅ Pass: Thông tin đúng hoặc tốt hơn v0.3
> - ⚠️ Issue: Có thông tin mới chưa verify được
> - ❌ Regression: Thông tin đúng ở v0.3 bị mất hoặc sai ở v0.4
>
> Files để so sánh:
> - v0.3: `build/snapshots/v0.3-pre-upgrade-2026-04-13/wiki/products/<cat>/`
> - v0.4: `wiki-v0.4/products/<cat>/`
> - Diff HTML: `trienkhai/upgrade-v0.4/diff-report.html`

---

## 1. hosting

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | **CRITICAL** — check giá |
| thong-so.md | | ⬜ chưa review | check RAM/CPU/băng thông |
| tinh-nang.md | | ⬜ chưa review | |
| so-sanh.md | | ⬜ chưa review | |
| chinh-sach.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |
| huong-dan.md | | ⬜ chưa review | |

**Checklist hosting:**
- [ ] Bảng giá gói hosting khớp với bkns.vn/hosting
- [ ] Hotline / email hỗ trợ đúng
- [ ] Không mất thông tin về uptime guarantee
- [ ] Số lượng addon domain / email accounts đúng

---

## 2. vps

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | **CRITICAL** — check CPU/RAM/SSD/giá |
| thong-so.md | | ⬜ chưa review | |
| tinh-nang.md | | ⬜ chưa review | |
| so-sanh.md | | ⬜ chưa review | |
| chinh-sach.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |
| huong-dan.md | | ⬜ chưa review | |

**Checklist VPS:**
- [ ] Cấu hình VPS (vCPU, RAM, SSD) khớp với bkns.vn/vps
- [ ] Giá tháng/năm đúng (không lẫn đơn vị VND/USD)
- [ ] Datacenter location đúng (Hà Nội / TP.HCM)
- [ ] OS options đúng

---

## 3. ssl

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | **CRITICAL** — check giá/loại cert |
| thong-so.md | | ⬜ chưa review | |
| tinh-nang.md | | ⬜ chưa review | |
| so-sanh.md | | ⬜ chưa review | |
| chinh-sach.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |

**Checklist SSL:**
- [ ] Tên loại chứng chỉ đúng (DV/OV/EV/Wildcard)
- [ ] Giá năm khớp với thực tế
- [ ] Validation period đúng
- [ ] Brand (Sectigo/Comodo/RapidSSL) đúng

---

## 4. ten-mien

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | **CRITICAL** — check giá đăng ký/gia hạn |
| chinh-sach.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |

**Checklist Domain:**
- [ ] Giá .vn, .com, .net, .org đúng (đăng ký + gia hạn)
- [ ] Setup fee = 0 đúng không
- [ ] Transfer fee đúng
- [ ] Phân biệt giá có VAT / chưa VAT rõ ràng

---

## 5. email

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | **CRITICAL** — check giá/storage |
| thong-so.md | | ⬜ chưa review | |
| tinh-nang.md | | ⬜ chưa review | |
| chinh-sach.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |

**Checklist Email:**
- [ ] Storage quota đúng (GB)
- [ ] Số lượng email account/forwarder/alias đúng
- [ ] Anti-spam / SSL có không
- [ ] Daily send limit đúng

---

## 6. server

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | **CRITICAL** |
| chinh-sach.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |

---

## 7. software

| File | v0.3 → v0.4 | Verdict | Ghi chú |
|------|------------|---------|---------|
| tong-quan.md | | ⬜ chưa review | |
| bang-gia.md | | ⬜ chưa review | |
| cau-hoi-thuong-gap.md | | ⬜ chưa review | |

---

## Tổng Kết

| Category | Tổng files | ✅ Pass | ⚠️ Issue | ❌ Regression |
|----------|-----------|--------|---------|-------------|
| hosting | 8 | | | |
| vps | 8 | | | |
| ssl | 7 | | | |
| ten-mien | 4 | | | |
| email | 6 | | | |
| server | 4 | | | |
| software | 3 | | | |
| **TOTAL** | **40** | | | |

## Quyết Định Cuối

- [ ] **PROMOTE**: ≥ 90% Pass, 0 Regression critical → Tiến hành PART 08
- [ ] **FIX & RE-RUN**: Có regression critical → Quay lại PART tương ứng, re-run PART 07
- [ ] **ROLLBACK**: Regression nghiêm trọng, không fix được nhanh → Giữ v0.3

**Verdict (điền sau review):** _(GO / NO-GO / CONDITIONAL-GO)_

**Notes:**
