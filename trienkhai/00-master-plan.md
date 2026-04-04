# BKNS Agent Wiki — Kế Hoạch Triển Khai Hoàn Thiện

> **Phiên bản:** 1.0 — Finalized 2026-04-04
> **Trạng thái:** ✅ SẴN SÀNG TRIỂN KHAI
> **Tác giả:** phamduytam (@phamduytam, Telegram ID: 882968821)

---

## PHẦN 1: BỨC TRANH TỔNG THỂ

### Mục tiêu dự án

Xây dựng **hệ thống tri thức tự động (Knowledge Base)** cho BKNS.VN, hoạt động như một "thủ thư AI":
- Tự thu thập dữ liệu từ bkns.vn
- Biên dịch thành wiki có cấu trúc
- Trả lời câu hỏi qua Telegram bot
- Tự kiểm tra chất lượng + cập nhật định kỳ

### Triết lý cốt lõi (Karpathy LLM-Compiled Wiki)

```
KHÔNG dùng RAG / Vector DB
→ Gửi TOÀN BỘ wiki làm context prefix mỗi query
→ Tận dụng Gemini Implicit Context Caching (giảm 90% chi phí token lặp)
→ Wiki ~50-100 file ≈ 50k-100k token — vừa đủ cho 1M context window
```

---

## PHẦN 2: QUYẾT ĐỊNH ĐÃ CHỐT (KHÔNG THAY ĐỔI)

### 2.1 Infrastructure

| Hạng mục | Giá trị | Ghi chú |
|----------|---------|---------|
| **Cloud** | Vertex AI | $300 trial credit, 90 ngày |
| **Model query** | `gemini-2.5-flash` | $0.30/$2.50 per 1M in/out |
| **Model compile/lint** | `gemini-2.5-pro` | $1.25/$10 per 1M in/out |
| **Caching** | Implicit (tự động) | 90% discount, không cần quản lý |
| **Bot platform** | OpenClaw + Telegram | Custom skills only — KHÔNG dùng ClawHub |
| **Wiki viewer** | MkDocs Material | Deploy web cho nhân viên |

### 2.2 Bot & Admin

| Hạng mục | Giá trị |
|----------|---------|
| **Bot name** | `BKNS_Wiki_bot` |
| **Bot token** | Lấy từ `.env` (KHÔNG commit) |
| **Admin** | @phamduytam (ID: `882968821`) |
| **Workspace** | `/home/openclaw/wiki/` |
| **Service account** | `/home/openclaw/api/duytam29284.json` |

### 2.3 Data & Schema

| Hạng mục | Giá trị |
|----------|---------|
| **Nguồn dữ liệu** | Crawl `bkns.vn` (không có dữ liệu nội bộ) |
| **Claims format** | Dual: YAML (approved) + JSONL (audit trail) |
| **Build activation** | `active-build.yaml` + Git tag |
| **Query log** | JSONL file (`logs/`) |
| **Ground truth** | Pricing + specs + contact info |

### 2.4 BKNS Contact (Verified)

| Kênh | Số | Mục đích |
|------|-----|---------|
| Tổng đài 24/7 | `1900 63 68 09` | Kỹ thuật, báo lỗi (mất phí) |
| Tư vấn KD | `1800 646 884` | Mua hàng, hóa đơn (miễn phí) |

---

## PHẦN 3: KIẾN TRÚC HỆ THỐNG

### Pipeline tổng thể

```
[bkns.vn / ảnh / text]
        │
        ▼
   raw/           ← Dữ liệu thô (metadata + content)
        │
        ▼ (Gemini Flash/Pro extract)
   claims/        ← YAML (facts) + JSONL (traces)
        │
        ▼ (Admin /duyet)
   wiki/          ← Markdown compiled, human-readable
        │
        ▼ (Gemini Flash query)
   [Trả lời Telegram] ← wiki prefix + câu hỏi → answer
        │
        ▼ (Loop)
   filing/lint/ground-truth ← Cải thiện liên tục
```

### Cấu trúc thư mục (CUỐI CÙNG)

```
/home/openclaw/wiki/
├── .env                          ← Secrets (KHÔNG commit)
├── .gitignore
├── .gitattributes                ← Git LFS: assets/evidence/**
├── agents.yaml                   ← OpenClaw config
│
├── raw/                          ← Dữ liệu thô
│   ├── website-crawl/            ← Từ bkns.vn
│   └── manual/                   ← Text paste thủ công
│
├── claims/                       ← Source of Truth
│   ├── registry.yaml             ← Master index
│   └── products/
│       ├── hosting/
│       ├── vps/
│       ├── ten-mien/
│       ├── email/
│       └── ssl/
│
├── entities/                     ← Entity registry
│   └── registry.yaml
│
├── sources/                      ← Source registry
│   └── registry.yaml
│
├── wiki/                         ← Wiki compiled
│   ├── index.md
│   ├── company/
│   │   └── gioi-thieu.md
│   ├── products/
│   │   ├── hosting/
│   │   ├── vps/
│   │   ├── ten-mien/
│   │   ├── email/
│   │   └── ssl/
│   ├── support/
│   │   └── lien-he.md
│   ├── onboarding/               ← Phase 3
│   │   ├── nhan-vien.md
│   │   ├── khach-hang.md
│   │   └── team-ky-thuat.md
│   └── .drafts/                  ← Pending admin review
│
├── build/                        ← Build snapshots
│   ├── active-build.yaml         ← Trỏ đến build hiện tại
│   └── snapshots/
│       └── v0.1/
│
├── assets/
│   ├── evidence/                 ← Full-res (Git LFS)
│   └── images/                   ← Compressed thumbnails
│
├── logs/
│   ├── query-YYYY-MM-DD.jsonl    ← Query traces
│   ├── lint/
│   └── ground-truth/
│
├── skills/                       ← OpenClaw custom skills
│   ├── query-wiki/
│   ├── ingest-raw/
│   ├── compile-wiki/
│   ├── ingest-image/             ← Phase 2
│   ├── lint-wiki/                ← Phase 2
│   └── ground-truth-check/       ← Phase 2
│
├── mkdocs.yml
├── README.md
├── addon.md
├── bot.md
└── trienkhai/                    ← Tài liệu triển khai này
```

---

## PHẦN 4: PHÂN TÍCH KHẢ THI

### Điểm mạnh (đã được validate)
- ✅ Karpathy LLM-Wiki pattern đã được validate rộng rãi (04/2026)
- ✅ Gemini 2.5 implicit caching 90% — cost-effective cho wiki prefix lặp
- ✅ 1M context window — wiki 100k token vẫn trong giới hạn tốt
- ✅ Claims-based architecture — tách sự thật khỏi trình bày (vững từ ngày 1)
- ✅ Budget $300 đủ ~8-13 tháng với model mix đúng

### Rủi ro đã được xử lý

| Rủi ro | Giải pháp đã chốt |
|--------|-------------------|
| Pricing sai trong docs cũ | File này dùng giá đã verify (04/2026) |
| OpenClaw security | Chỉ custom skills, KHÔNG ClawHub |
| Budget burn nhanh | Flash cho query (80% volume), Pro chỉ compile/lint |
| Single admin bottleneck | Bot có thể query mà không cần admin; chỉ stuck ở ingest mới |
| Gemini API down | Graceful error: "Hệ thống đang bảo trì, liên hệ hotline" |

### Điểm cần chú ý khi triển khai

1. **Verify model string** trên Vertex AI: `gemini-2.5-flash` hay `gemini-2.5-flash-001`
2. **Implicit cache TTL ~1 giờ** — nếu traffic thấp, cache miss nhiều hơn ước tính
3. **Full schema từ ngày 1** — Phase 0.5 nặng hơn (~2 tuần thay vì 1 tuần)
4. **Flash output đắt** ($2.50/1M) — giữ câu trả lời ngắn gọn (<300 từ)

---

## PHẦN 5: LỘTRÌNH & BUDGET

### Timeline tổng hợp

| Phase | Tên | Thời gian | Budget tích lũy | Kết quả |
|-------|-----|-----------|-----------------|---------|
| **0.5** | Full Schema MVP | 2 tuần | ~$5-15 | Bot query hoạt động, cấu trúc đầy đủ |
| **1** | Automation Pipeline | 2-3 tuần | ~$20-40 | Ingest/compile tự động, MkDocs |
| **2** | Intelligence | 4-6 tuần | ~$60-100 | Vision, lint, ground truth |
| **3** | Enterprise | Ongoing | ~$25-35/tháng | Onboarding 3 đối tượng, observability |

### Budget breakdown (Scenario B — Standard)

```
Wiki: 50k token | 100 queries/ngày | Flash query + Pro compile/lint

Query cached (80%):     $3.60/tháng
Query non-cached (20%): $9.00/tháng
Query output:           $3.75/tháng
Query dynamic input:    $0.18/tháng
Compile 8×/tháng:       $3.20/tháng
Lint 4×/tháng (Pro):    $2.75/tháng
────────────────────────────────────
TỔNG:                  ~$22.50/tháng → $300 đủ ~13 tháng
```

> ⚠️ **Worst case:** Nếu dùng Pro cho query → ~$80-120/tháng → $300 chỉ đủ ~3 tháng. PHẢI dùng Flash cho query.

---

## PHẦN 6: SKILLS PRIORITY MAP

| # | Skill | Phase | Priority | Mô tả |
|---|-------|-------|----------|-------|
| 1 | `query-wiki` | 0.5 | 🔴 Critical | Bot trả lời câu hỏi — core function |
| 2 | `ingest-raw` | 1 | 🔴 Critical | Bot nhận URL/text mới |
| 3 | `compile-wiki` | 1 | 🔴 Critical | Raw → claims → wiki draft |
| 4 | `syntax-check` | 1 | 🟡 Medium | QA tự động (Python, cost=0) |
| 5 | `ingest-image` | 2 | 🟠 High | Extract bảng giá từ ảnh |
| 6 | `lint-wiki` | 2 | 🟠 High | Phát hiện mâu thuẫn, outdated |
| 7 | `ground-truth-check` | 2 | 🟡 Medium | Cross-check giá vs bkns.vn |
| 8 | `auto-file` | 3 | 🟡 Medium | Filing câu trả lời hay |

---

## PHẦN 7: FILE TRIỂN KHAI (CÁC BƯỚC NHỎ)

Mỗi file dưới đây = 1 session vibe coding / 1 context window. Thực hiện THEO THỨ TỰ:

| File | Nội dung | Ước lượng |
|------|----------|-----------|
| [01-setup-infra.md](01-setup-infra.md) | Git, .env, folder structure, registries | 1-2 giờ |
| [02-crawl-claims.md](02-crawl-claims.md) | Crawl bkns.vn + extract claims YAML/JSONL | 3-4 giờ |
| [03-bot-query.md](03-bot-query.md) | query-wiki skill + Telegram bot + test 20 queries | 3-4 giờ |
| [04-pipeline-ingest-compile.md](04-pipeline-ingest-compile.md) | ingest-raw + compile-wiki + /duyet | 4-6 giờ |
| [05-mkdocs-syntax-check.md](05-mkdocs-syntax-check.md) | MkDocs Material + syntax-check cron | 2-3 giờ |
| [06-phase2-intelligence.md](06-phase2-intelligence.md) | ingest-image + lint-wiki + ground-truth-check | 6-8 giờ |
| [07-phase3-enterprise.md](07-phase3-enterprise.md) | Onboarding wiki + auto-file + observability | 4-6 giờ |

---

## PHẦN 8: KILL CRITERIA

Dừng dự án nếu:
- Budget $300 hết trước khi Phase 1 hoàn thành (burn rate > $50/tháng)
- Gemini Implicit Caching không hoạt động cho use case này (cache hit < 50% sau 2 tuần)
- Bot trả lời sai > 30% câu hỏi cơ bản sau khi có đủ wiki (Phase 0.5 done test)
- Vertex AI không support implicit caching cho account trial

---

*Bắt đầu từ: [01-setup-infra.md](01-setup-infra.md)*
