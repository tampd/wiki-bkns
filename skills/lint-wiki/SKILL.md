---
name: lint-wiki
description: >
  Kiểm tra chất lượng wiki: Python syntax check + Gemini Pro semantic analysis.
  Layer 1: YAML frontmatter validation, broken links, orphan files.
  Layer 2: Semantic checks — outdated info, price conflicts, missing sources.
  Trigger: /lint hoặc auto trước mỗi build.
version: "1.0"
phase: "1"
model: gemini-2.5-pro
admin_only: true
triggers:
  - command: /lint
---

# lint-wiki

## Files
- scripts/lint.py: Two-layer lint engine
