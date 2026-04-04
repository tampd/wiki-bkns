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

# extract-claims

## Mô tả
Đọc raw files, dùng Gemini Pro trích xuất mọi facts thành claims YAML.
Mỗi fact = 1 claim riêng. Conflict detection vs claims đã approved.

## Input
- `raw/website-crawl/*.md` với `status: pending_extract`
- `/extract` command

## Output
- `claims/.drafts/{category}/{claim_id}.yaml` — Claim files
- `claims/.drafts/{category}/{claim_id}.jsonl` — Audit traces
- `entities/registry.yaml` — Updated entities
- Telegram notification với summary

## Model
Gemini 2.5 Pro — cần precision cao cho extraction.

## Files
- scripts/extract.py: Logic extract chính
