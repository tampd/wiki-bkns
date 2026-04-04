# Skill 10: build-snapshot

> **Phase:** 1 | **Model:** Script Python ($0) | **Trigger:** Tự động sau /duyet

---

## SKILL.md

```yaml
---
name: build-snapshot
description: >
  Tạo build manifest sau khi wiki được publish (/duyet thành công).
  Hash toàn bộ claims/approved/ + wiki/ → build ID duy nhất.
  Cập nhật build/active-build.yaml. Git tag.
  Bot query-wiki sẽ reload wiki khi build_id thay đổi (cache invalidation).
  Trigger: tự động sau /duyet hoặc manual /build.
version: "1.0"
phase: "1"
model: null
admin_only: true
user-invocable: true
triggers:
  - event: after_duyet        # Tự động sau mỗi /duyet
  - command: /build
---
```

---

## Workflow

```
BƯỚC 1: Collect stats
  ├─ Count: claims/approved/**/*.yaml → claims_count
  ├─ Count: wiki/**/*.md (exclude .drafts) → wiki_pages_count
  └─ Count token estimate: tổng chars / 4

BƯỚC 2: Hash
  ├─ SHA256 of sorted(all claims/approved files) → claims_hash
  └─ SHA256 of sorted(all wiki files, exclude .drafts) → wiki_hash

BƯỚC 3: Tạo build manifest
  └─ build/manifests/build-{YYYY-MM-DD}-{seq:02d}.yaml

BƯỚC 4: Cập nhật build/active-build.yaml
  └─ Trỏ đến build mới (query-wiki sẽ detect + reload)

BƯỚC 5: Git tag
  └─ git tag build/v{major}.{minor}
     Major: tăng khi có breaking change
     Minor: tăng mỗi /duyet

BƯỚC 6: Log + notify
  └─ "🔨 Build v{version} created. {N} claims, {M} wiki pages, ~{T}k tokens."
```

---

## Build Manifest Schema

```yaml
# build/manifests/build-2026-04-04-01.yaml
build_id: build-2026-04-04-01
version: v0.1
created_at: "2026-04-04T16:00:00+07:00"
created_by: phamduytam              # admin who ran /duyet

# Stats
claims_count: 45
wiki_pages_count: 12
wiki_token_estimate: 48000          # ~48k tokens

# Hashes (for cache invalidation)
claims_hash: "sha256:abc..."
wiki_hash: "sha256:def..."

# Build quality
status: active                      # active | superseded | rollback
parent_build_id: null               # previous build
lint_summary:
  syntax_passed: true
  semantic_passed: true
  unresolved_conflicts: 0

# Git
git_tag: build/v0.1
git_commit: abc1234
```

---

## build/active-build.yaml (Pointer)

```yaml
# Bot đọc file này khi khởi động để biết build hiện tại
# Thay build_id để rollback về version cũ

build_id: build-2026-04-04-01
version: v0.1
build_date: "2026-04-04T16:00:00+07:00"
wiki_token_estimate: 48000
wiki_files: 12
claims_count: 45
git_tag: build/v0.1
status: active
```

---

## Rollback

```bash
# Rollback về build cũ:
# 1. Sửa build/active-build.yaml → trỏ build_id cũ
# 2. Bot query-wiki sẽ tự reload wiki từ git tag cũ
# 3. (Không cần restart bot)

# Xem lịch sử builds:
ls build/manifests/
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Git tag đã tồn tại | Thêm suffix -retry-{n} |
| Hash computation lỗi | Skip hash, vẫn tạo build với null hashes |
| Quá nhiều builds (>100) | Archive builds cũ vào build/archive/ |
