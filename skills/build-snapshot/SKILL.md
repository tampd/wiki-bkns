---
name: build-snapshot
description: >
  Đóng gói wiki hiện tại thành build (snapshot).
  Tính token count, tạo manifest, tag Git.
  Bot query-wiki load build_id từ active-build.yaml.
  Trigger: Tự động sau /duyet thành công.
version: "1.0"
phase: "0.5"
model: null
admin_only: true
user-invocable: true
triggers:
  - command: /build
---

# build-snapshot

## Quy trình
1. Đọc tất cả wiki/*.md (không .drafts/)
2. Tính tổng token estimate (~4 chars/token)
3. Hash toàn bộ wiki → build fingerprint
4. Tạo manifest YAML → build/manifests/
5. Cập nhật active-build.yaml
6. Git tag (nếu có Git)

## Model
Không dùng LLM ($0/lần).

## Files
- scripts/snapshot.py: Build logic
