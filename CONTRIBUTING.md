# Contributing — BKNS Wiki

Cảm ơn bạn quan tâm đến dự án. Tài liệu này mô tả quy trình đóng góp.

## Quy trình cơ bản

1. **Fork + clone** repository.
2. Tạo nhánh từ `master`: `git checkout -b feat/ten-tinh-nang` hoặc `fix/ten-loi`.
3. Đọc [CLAUDE.md](./CLAUDE.md) và [docs/SPEC-wiki-system.md](./docs/SPEC-wiki-system.md) để nắm kiến trúc.
4. Commit theo Conventional Commits (xem bên dưới).
5. Push và mở Pull Request tới `master`.

## Commit message format

```
type(scope): tóm tắt ngắn dưới 70 ký tự

[optional body — giải thích "why", không phải "what"]
```

**Types hợp lệ:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`, `ci`.

**Ví dụ:**
- `feat(bot): add /them command for admin URL ingestion`
- `fix(review): guard against null review_state in filter`
- `docs(runbook): add dual-vote troubleshooting section`

## Trước khi mở PR — checklist

- [ ] Tests liên quan pass cục bộ: `pytest tests/ -q`
- [ ] Lint không regress: `python3 skills/lint-wiki/scripts/lint.py` (nếu sửa wiki content)
- [ ] Không hardcode secrets, API keys, personal data
- [ ] File `.env` không nằm trong diff
- [ ] Đã đọc [LESSONS.md](./LESSONS.md) để tránh lặp lại lỗi đã biết
- [ ] Cập nhật [CHANGELOG.md](./CHANGELOG.md) nếu là breaking change, feature, hoặc fix quan trọng

## Cấu trúc commit

Ưu tiên **atomic commits** — một commit = một thay đổi logic. Tránh commit gộp nhiều tính năng.

## Branch naming

- `feat/*` — tính năng mới
- `fix/*` — sửa lỗi
- `docs/*` — chỉ sửa tài liệu
- `refactor/*` — refactor không đổi hành vi
- `upgrade-v*-part*` — nhánh nâng cấp version lớn, chia nhiều phần

## Testing

```bash
# Unit tests + smoke tests
pytest tests/ -q

# Dual-vote integration (cần .env có OPENAI_API_KEY)
python3 tools/ab_test_models.py verify

# Regression (v0.3 vs v0.4)
python3 tools/regression_test.py --dry-run
```

## Bảo mật

Tuyệt đối **không** commit: `.env`, `api/`, `password.md`, service account JSON, Telegram bot tokens, cookies.

Báo cáo lỗ hổng: gửi email cho `duytam@bkns.vn` thay vì mở issue công khai.

## Liên hệ

- Maintainer: Tampd (BKNS) — `duytam@bkns.vn`
- Issues: https://github.com/tampd/Wiki/issues
