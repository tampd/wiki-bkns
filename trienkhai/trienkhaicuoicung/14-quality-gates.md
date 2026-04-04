# Quality Gates — Tất Cả Điểm Kiểm Soát Chất Lượng

---

## Tổng Quan Quality Gates

```
GATE 1: Validation đầu vào (crawl-source)
  → URL hợp lệ? Domain bkns.vn? Hash trùng?

GATE 2: Claim validation (extract-claims)
  → Có đủ required fields? Giá tiền đúng? Conflict detection?

GATE 3: Self-review (compile-wiki)
  → Số liệu draft = claims gốc? Hallucination detection?

GATE 4: Admin approval (/duyet)
  → Human review trước khi publish

GATE 5: Syntax lint (lint-wiki Layer A)
  → Frontmatter, freshness, broken links, orphans?

GATE 6: Semantic lint (lint-wiki Layer B)
  → Price conflicts cross-file? Outdated info?

GATE 7: Ground truth (ground-truth)
  → Wiki claims = website live?
```

---

## GATE 1: Input Validation

```python
CRAWL_RULES = {
    "url_scheme": ["http", "https"],        # Reject ftp, file, etc.
    "warn_if_not_bkns": True,               # Cảnh báo URL ngoài bkns.vn
    "duplicate_window_hours": 24,           # Skip nếu crawl trong 24h
    "content_hash_check": True,             # Skip nếu content không đổi
    "min_word_count": 100,                  # Skip nếu trang quá trống
    "timeout_seconds": 30,
    "max_retries": 1,
}
```

---

## GATE 2: Claim Validation

```python
CLAIM_REQUIRED_FIELDS = [
    "entity_id",     # ENT-PROD-* hoặc ENT-COMPANY-*
    "attribute",     # pricing | specs | policy | contact | description
    "value",         # giá trị thực tế
    "confidence",    # high | medium | low
]

CLAIM_HIGH_RISK_ATTRIBUTES = [
    "monthly_price", "yearly_price", "one_time_price",
    "hotline", "email", "address", "website",
    "sla_uptime", "refund_policy",
]
# → risk_class = "high" tự động cho tất cả các attributes trên

CLAIM_VALIDATION_RULES = {
    "price_must_be_positive": True,
    "price_max_vnd": 100_000_000,           # >100M/tháng → cảnh báo
    "confidence_if_unclear": "low",
    "skip_claim_if_missing_required": True, # Log warning + continue
}
```

---

## GATE 3: Self-Review (compile-wiki)

```python
SELF_REVIEW_RULES = {
    "check_every_number": True,       # Mọi số trong draft phải có trong claims
    "check_hallucination": True,      # Fact trong draft phải có claim source
    "auto_correct": True,             # Tự sửa nếu sai nhỏ
    "max_auto_corrections": 3,        # >3 corrections → báo admin
    "block_if_hallucination": True,   # KHÔNG publish nếu còn hallucination
}
```

### Self-Review Severity Matrix

| Issue | Severity | Hành động |
|-------|---------|----------|
| Số liệu giá sai | CRITICAL | Auto-correct, log, nếu >1 → alert admin |
| Thông số kỹ thuật sai | HIGH | Auto-correct + log |
| Hallucinated fact | CRITICAL | Xóa fact + log "[HALLUCINATION] removed" |
| Claim bị bỏ sót | MEDIUM | Thêm vào draft + log |
| Link sai | LOW | Fix link + log |

---

## GATE 4: Admin Approval (/duyet)

```
Quy trình /duyet:
1. Admin nhận preview qua Telegram
2. Admin đọc và kiểm tra các điểm:
   □ Giá chính xác với bkns.vn hiện tại?
   □ Thông số kỹ thuật đúng?
   □ Không có thông tin gây hiểu nhầm?
   □ Ngôn ngữ phù hợp (trung lập, chuyên nghiệp)?
3. Admin gõ: /duyet {filename}
4. Bot move + publish + build-snapshot

KHÔNG /duyet nếu:
  - Có ký hiệu ⚠️ chưa resolve
  - Có [CONFLICT] trong file
  - Giá chưa verify với bkns.vn
```

---

## GATE 5 + 6: Lint Rules

```python
LINT_RULES = {
    # Layer A (Python, $0)
    "require_frontmatter": True,
    "required_fields": ["title", "category", "updated"],
    "stale_threshold_days": 30,
    "min_body_length": 50,          # chars
    "check_broken_images": True,
    "check_orphan_files": True,

    # Layer B (Gemini Pro)
    "check_price_conflicts": True,  # Cross-file price consistency
    "check_outdated_info": True,
    "check_missing_sources": True,
    "suggest_improvements": 5,      # Top 5 suggestions
}
```

---

## GATE 7: Ground Truth Rules

```python
GROUND_TRUTH_RULES = {
    "schedule": "weekly_sunday_22:00",
    "sources_to_verify": "all in sources/registry.yaml",
    "alert_on_mismatch": True,
    "mismatch_severity": {
        "price": "high",            # Giá thay đổi → alert ngay
        "specs": "medium",
        "contact": "high",          # Hotline thay đổi → alert ngay
        "policy": "low",
    },
    "auto_queue_recrawl": True,     # Tự tạo task recrawl khi mismatch
}
```

---

## Error Handling Central Spec

```python
# Mọi skill tuân theo pattern này khi gặp lỗi:

ERROR_HANDLING = {
    "log_format": {
        "ts": "ISO timestamp",
        "skill": "skill-name",
        "action": "error",
        "severity": "critical|high|medium|low",
        "detail": "mô tả lỗi",
        "context": {"url": "...", "file": "..."},
    },
    "log_path": "logs/errors/YYYY-MM-DD.jsonl",
    "telegram_notify": {
        "critical": True,   # Alert ngay
        "high": True,
        "medium": False,    # Batch trong daily digest
        "low": False,
    },
    "telegram_format": "{emoji} {skill}: {detail_1_line}",
    "emoji_map": {
        "critical": "❌",
        "high": "⚠️",
        "medium": "🟡",
        "low": "ℹ️",
    },
    "retry_policy": {
        "gemini_timeout": {"max_retries": 2, "interval_seconds": 5},
        "http_error": {"max_retries": 1, "interval_seconds": 2},
    },
    "stop_on_critical": True,  # KHÔNG tiếp tục processing khi critical error
}
```

---

## Telegram Message Standards

```
# Format chuẩn cho mọi notification:

SUCCESS: ✅ {skill}: {tóm tắt ngắn}
ERROR:   ❌ {skill}: {mô tả lỗi} [Xem log: {path}]
WARNING: ⚠️ {skill}: {cảnh báo} [Action: {gợi ý}]
INFO:    📋 {skill}: {thông tin}
REPORT:  📊 {skill} Report — {date}\n{nội dung}

# Độ dài: tối đa 300 chars cho alert ngắn
# Báo cáo chi tiết: link đến log file
```
