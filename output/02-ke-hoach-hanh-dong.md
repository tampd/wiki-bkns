# 02 — Kế Hoạch Hành Động: Full Schema MVP → Production

> **Cập nhật:** 2026-04-04 — Phản ánh quyết định Option C (full addon.md schema từ ngày 1)
> **Triết lý:** Xây nền vững từ đầu, không refactor sau. Ship nhanh nhưng đúng kiến trúc.

---

## Tổng Quan Phân Pha

```
Phase 0.5: Full Schema MVP (2 tuần)
    → Cấu trúc đầy đủ + crawl bkns.vn + 5 entities + claims + wiki + bot query
    → Chứng minh pipeline end-to-end hoạt động

Phase 1: Automation Pipeline (2-3 tuần)
    → Ingest workflow tự động + compile pipeline + draft/review
    → MkDocs Material cho nhân viên

Phase 2: Intelligence (4-6 tuần)
    → Vision extract + linting tự động + ground truth
    → Build manifest + packs + multi-agent

Phase 3: Enterprise (ongoing)
    → Onboarding 3 đối tượng + auto-file + observability
    → Full lifecycle management
```

---

## Phase 0.5: Full Schema MVP — "Nền Vững, Bot Chạy"

**Thời gian:** ~2 tuần
**Budget:** ~$5-15
**Mục tiêu:** Bot Telegram trả lời câu hỏi BKNS, toàn bộ cấu trúc addon.md đã sẵn sàng.

### Tuần 1: Cấu Trúc + Dữ Liệu

```
□ 1.1 Git repo setup
    → git init /home/openclaw/wiki/
    → .gitignore: .env, logs/, *.pyc, __pycache__/
    → .gitattributes: assets/evidence/** filter=lfs
    → git lfs install && git lfs track "assets/evidence/**"
    → Initial commit

□ 1.2 Tạo cấu trúc thư mục đầy đủ (theo addon.md)
    → raw/, claims/, entities/, sources/, wiki/, build/,
       assets/evidence/, assets/images/, logs/, skills/
    → Tạo registry files: sources/registry.yaml, entities/registry.yaml
    → Tạo build/active-build.yaml (v0.1, initial)

□ 1.3 Tạo .env
    → VERTEX_PROJECT_ID=...
    → VERTEX_LOCATION=us-central1
    → VERTEX_SERVICE_ACCOUNT=/home/openclaw/api/duytam29284.json
    → TELEGRAM_BOT_TOKEN=8790440541:AAF...
    → ADMIN_TELEGRAM_ID=882968821
    → WIKI_DIR=/home/openclaw/wiki/wiki/

□ 1.4 Crawl bkns.vn → raw/
    → Sử dụng Tavily hoặc script Python crawl 5 trang chính:
      • Trang chủ → giới thiệu công ty
      • Hosting → sản phẩm + bảng giá
      • Tên miền → sản phẩm + bảng giá
      • Hỗ trợ → thông tin liên hệ
      • VPS → sản phẩm + bảng giá
    → Lưu raw/website-crawl/[page]-20260404.md
    → Mỗi file có metadata header (source_url, crawled_at)

□ 1.5 Tạo Source registry
    sources/registry.yaml:
    - source_id: SRC-BKNS-WEB-001
      type: official_website
      url: https://bkns.vn
      authority: primary
      trust_level: high
      last_crawled: 2026-04-04

□ 1.6 Extract claims từ raw (dùng Gemini Pro/Flash)
    → Mỗi sản phẩm → pricing claims YAML + JSONL trace
    → Mỗi entity → entities/registry.yaml entry
    → claims/products/hosting/shared-hosting-pricing.yaml
    → claims/products/ten-mien/ten-mien-pricing.yaml
    → ...

□ 1.7 Compile wiki từ claims
    → Dùng compile prompt (output/03-skills-va-prompts.md)
    → wiki/company/gioi-thieu.md
    → wiki/products/hosting/tong-quan.md
    → wiki/products/hosting/bang-gia.md
    → wiki/products/ten-mien/tong-quan.md
    → wiki/products/ten-mien/bang-gia.md
    → wiki/support/lien-he.md (hotline + chat links)
    → wiki/index.md (master index)
```

### Tuần 2: Bot + Query + Git

```
□ 2.1 Setup OpenClaw agent
    → agents.yaml: model gemini-2.5-flash (query), gemini-2.5-pro (compile)
    → Channel: Telegram (BKNS_Wiki_bot)
    → Workspace: /home/openclaw/wiki/

□ 2.2 Build skill: query-wiki
    → skills/query-wiki/SKILL.md
    → skills/query-wiki/scripts/query.py
    → System prompt từ 03-skills-va-prompts.md
    → Gửi wiki prefix + câu hỏi → Gemini Flash → trả lời
    → Log: logs/query-YYYY-MM-DD.jsonl

□ 2.3 Test thủ công: 20 câu hỏi
    → 5 câu hosting (giá, tính năng, so sánh gói)
    → 5 câu tên miền (giá, quy trình đăng ký)
    → 5 câu VPS (giá, specs)
    → 5 câu hỗ trợ (hotline, chính sách, liên hệ)
    → Verify: câu trả lời có đúng, có ghi nguồn, có nói "không biết" khi cần

□ 2.4 Đo metrics thực tế
    → Token usage per query (input cached, non-cached, output)
    → Cache hit rate
    → Chi phí thực tế sau 20 queries
    → Response time

□ 2.5 Build snapshot v0.1
    → build/snapshots/v0.1/manifest.yaml
    → Git tag: build/v0.1
    → build/active-build.yaml → trỏ v0.1

□ 2.6 Git commit
    → Commit tất cả: structure + raw + claims + wiki + skills + build
    → Tag: phase-0.5-complete
```

### Definition of Done — Phase 0.5

- [ ] Bot Telegram hoạt động, trả lời câu hỏi qua `/hoi`
- [ ] Cấu trúc thư mục theo addon.md (raw/, claims/, entities/, sources/, wiki/, build/)
- [ ] ≥5 entities trong registry (hosting, VPS, tên miền, email/SSL, BKNS company)
- [ ] ≥10 claims YAML + JSONL traces
- [ ] ≥8 wiki files compiled
- [ ] wiki/support/lien-he.md có hotline chính xác
- [ ] Build snapshot v0.1 + active-build.yaml
- [ ] 20/20 test queries: ≥16 câu trả lời đúng (80%)
- [ ] Đo được: cache hit rate, cost/query, response time
- [ ] Git repo clean, tagged

---

## Phase 1: Automation Pipeline — "Bot Tự Nhận Dữ Liệu"

**Thời gian:** 2-3 tuần sau Phase 0.5
**Budget:** ~$20-40 tích lũy

### Checklist

```
□ 1.1 Skill: ingest-raw
    → /them [URL] → crawl → raw/ → metadata
    → /them [text] → paste text → raw/manual/

□ 1.2 Skill: compile-wiki
    → /compile → raw/ pending → Gemini Pro → claims/ → wiki/.drafts/
    → Tự động detect category
    → Báo admin preview qua Telegram

□ 1.3 Command: /duyet
    → Admin review draft
    → /duyet [filename] → move .drafts/ → wiki/ → update claims status
    → Git commit auto: "feat(wiki): approve [filename]"

□ 1.4 Skill: syntax-check
    → Cron 06:00 daily → check frontmatter, broken links, empty files
    → Script Python (không LLM, cost=0)
    → Báo lỗi qua Telegram nếu có

□ 1.5 MkDocs Material setup
    → pip install mkdocs-material
    → mkdocs.yml config (theme vi, search, navigation)
    → mkdocs serve / mkdocs build
    → Deploy: localhost hoặc subdomain nội bộ

□ 1.6 Mở rộng wiki
    → Crawl thêm: VPS, Email, SSL, chính sách
    → Target: ≥20 wiki files, ≥30 claims
    → Mỗi category: tong-quan + bang-gia

□ 1.7 Build v0.2
    → Snapshot mới sau mỗi batch approve
    → Git tag: build/v0.2
```

### Definition of Done — Phase 1

- [ ] Ingest URL → compile → draft → review → publish hoạt động end-to-end
- [ ] ≥20 wiki files, ≥30 claims
- [ ] Syntax check chạy tự động 06:00 daily
- [ ] MkDocs Material accessible trên web
- [ ] Bot trả lời đúng >85% câu hỏi về sản phẩm BKNS
- [ ] ≥3 build snapshots (v0.1, v0.2, v0.3)

---

## Phase 2: Intelligence — "Bot Nhìn, Kiểm Tra, Tự Sửa"

**Thời gian:** 4-6 tuần
**Budget:** ~$60-100 tích lũy

### Checklist

```
□ 2.1 Skill: ingest-image
    → Ảnh Telegram → assets/evidence/ (Git LFS) → Vision extract
    → Thumbnail → assets/images/
    → Claim draft YAML → /duyet

□ 2.2 Skill: lint-wiki
    → Cron weekly → Gemini Pro → lint report
    → Tìm: mâu thuẫn giá, thông tin cũ, orphan files, thiếu nguồn
    → Output: logs/lint/report-YYYY-MM-DD.md

□ 2.3 Ground truth checker
    → Cron weekly/bi-weekly → crawl bkns.vn
    → Compare claims vs live data
    → Report: logs/ground-truth/report-YYYY-MM-DD.md
    → Telegram alert nếu phát hiện outdated

□ 2.4 Pack builder (nếu wiki > 100k token)
    → Tách wiki thành packs: core, hosting, domain, vps, support
    → Intent classifier (Flash) → chọn pack phù hợp
    → Giảm prefix size → giảm cost

□ 2.5 Multi-agent (nếu traffic ≥ 50 queries/ngày)
    → Flash: query + ingest + ground truth
    → Pro: compile + lint
    → Routing logic trong agents.yaml

□ 2.6 Cross-linker
    → Auto detect related articles → thêm "Xem thêm" links
    → Update index.md
```

---

## Phase 3: Enterprise — "Hệ Thống Tri Thức Sống"

**Thời gian:** Ongoing
**Budget:** ~$25-35/tháng (Flash query + Pro compile/lint)

### Checklist

```
□ 3.1 Onboarding wiki
    → wiki/onboarding/nhan-vien.md
    → wiki/onboarding/khach-hang.md
    → wiki/onboarding/team-ky-thuat.md

□ 3.2 Auto-file policy (addon.md §15)
    → FAQ candidates → wiki/faq/ (reviewed)
    → Sales candidates → claims/ (reviewed)
    → Factual corrections → lint report

□ 3.3 Full lifecycle management
    → Claims: received → extracted → drafted → approved → superseded
    → Conflict detection (addon.md §8)
    → Source Authority Ladder enforcement

□ 3.4 Observability
    → Dashboard: queries/day, cache hit%, cost/day, lint issues
    → Monthly report cho management

□ 3.5 Answer Contract (addon.md §16)
    → Mỗi câu trả lời có: build_id, sources[], confidence
    → "Tôi không biết" contract khi confidence < threshold
```

---

## Timeline Tổng Hợp

| Phase | Thời gian | Budget | Model chính | Output |
|-------|-----------|--------|-------------|--------|
| **0.5** | 2 tuần | ~$5-15 | Flash (query) + Pro (compile) | Bot chạy, cấu trúc đầy đủ |
| **1** | 2-3 tuần | ~$20-40 | Flash + Pro | Pipeline tự động, MkDocs |
| **2** | 4-6 tuần | ~$60-100 | Flash + Pro | Vision, lint, ground truth |
| **3** | Ongoing | ~$25-35/tháng | Flash (80%) + Pro (20%) | Full system |
| **Tổng 0.5→2** | ~8-11 tuần | ~$85-155 | | Hệ thống functional |

**$300 budget:** Đủ hoàn thành Phase 0.5→2 + ~4-6 tháng Phase 3.

---

## Nguyên Tắc Triển Khai (Cập Nhật)

1. **Full schema from day 1:** Cấu trúc addon.md đầy đủ, không cut corners
2. **Pro cho compile/lint, Flash cho query:** Tiết kiệm 70%+ budget
3. **Crawl bkns.vn là nguồn chính:** Không chờ dữ liệu nội bộ
4. **Dual storage claims:** YAML (human) + JSONL (machine/audit)
5. **MkDocs sớm:** Deploy viewer Phase 1, không đợi Phase 3
6. **Ground truth toàn bộ:** Pricing + specs + contact, có báo cáo
7. **Git tag mỗi build:** audit trail cho mọi bản snapshot

---

*Xem skills chi tiết: [03-skills-va-prompts.md](./03-skills-va-prompts.md)*
*Xem quyết định: [08-quyet-dinh-cuoi-cung.md](./08-quyet-dinh-cuoi-cung.md)*
