# Bot Vận Hành — Thiết Kế & Thực Hành Tốt Nhất
## BKNS Knowledge Wiki · OpenClaw + Gemini 2.5

> **Mục đích tài liệu này:** Ghi chép đầy đủ cách bot hoạt động, giao việc, tự kiểm tra, tương tác người, phân quyền file, vòng lặp tự động, kho skill, và những gì cần cải thiện để đúng với tinh thần gốc của **Andrej Karpathy**.
>
> **Phiên bản:** v1.0 · 2026-04-04

---

## Mục Lục

1. [Triết Lý Vận Hành Bot](#1-triết-lý-vận-hành-bot)
2. [Giao Việc Cho Bot — Mô Hình Thực Tế](#2-giao-việc-cho-bot--mô-hình-thực-tế)
3. [Bot Tự Kiểm Tra Tự Động](#3-bot-tự-kiểm-tra-tự-động)
4. [Phát Hiện Trùng Lặp & Nội Dung Không Hợp Lý](#4-phát-hiện-trùng-lặp--nội-dung-không-hợp-lý)
5. [Tương Tác Người — Human-in-the-Loop](#5-tương-tác-người--human-in-the-loop)
6. [Phân Quyền Ghi File & Sửa File](#6-phân-quyền-ghi-file--sửa-file)
7. [Vòng Lặp Tự Động — Tuần Hoàn](#7-vòng-lặp-tự-động--tuần-hoàn)
8. [Hệ Thống Skill — Tìm Ở Đâu](#8-hệ-thống-skill--tìm-ở-đâu)
9. [Skill Thủ Thư & Quản Lý Wiki](#9-skill-thủ-thư--quản-lý-wiki)
10. [Đánh Giá Kiến Trúc Hiện Tại & Cải Thiện](#10-đánh-giá-kiến-trúc-hiện-tại--cải-thiện)
11. [Sát Với Karpathy — Những Gì Còn Thiếu](#11-sát-với-karpathy--những-gì-còn-thiếu)
12. [Repo & Dự Án Tham Khảo Nên Nghiên Cứu](#12-repo--dự-án-tham-khảo-nên-nghiên-cứu)

---

## 1. Triết Lý Vận Hành Bot

### 1.1. Bot là "thủ thư tự động" — không phải chatbot thông thường

Bot BKNS không chỉ trả lời câu hỏi. Nó **quản lý một kho tri thức sống**, như một thủ thư thực thụ:

| Vai trò thủ thư truyền thống | Tương đương trong bot |
|------------------------------|----------------------|
| Nhận sách mới → phân loại → xếp đúng kệ | Nhận raw data → classify → đặt đúng wiki/ |
| Kiểm tra định kỳ sách lỗi thời | Lint định kỳ → phát hiện giá cũ, mâu thuẫn |
| Viết index, catalog liên kết | Cập nhật index.md, backlink chéo |
| Hỗ trợ tra cứu khách hàng | Query bot Telegram |
| Lưu bằng chứng gốc (tài liệu gốc) | Git LFS cho ảnh evidence/ |

### 1.2. Nguyên tắc thiết kế cốt lõi (từ Karpathy)

```
"LLM là trình biên dịch tri thức.
 Nó không thay thế con người — nó khuếch đại con người.
 Dữ liệu thô → LLM compile → Wiki sạch → LLM query.
 Mọi bước đều có thể audit."
```

Bot phải luôn:
- **Traceable**: Mọi thay đổi wiki có Git commit → có thể trace lại ai/cái gì thay đổi
- **Auditable**: Nguồn dẫn chứng rõ ràng trong từng fact
- **Recoverable**: Git history cho phép rollback bất kỳ phiên bản nào
- **Transparent**: Không "bịa" — nếu không có thông tin, nói thẳng

---

## 2. Giao Việc Cho Bot — Mô Hình Thực Tế

### 2.1. 3 kênh giao việc

```
┌──────────────────────────────────────────────────────────┐
│              CÁCH GIAO VIỆC CHO BOT                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. TELEGRAM (nhân viên gửi)                             │
│     • Gửi ảnh bảng giá → bot ingest + extract           │
│     • Gửi URL → bot crawl + lưu raw/                     │
│     • Câu lệnh: /compile, /lint, /query [câu hỏi]        │
│                                                          │
│  2. CRON JOB (tự động theo lịch)                         │
│     • Hàng ngày: health check nhỏ (missing backlinks)    │
│     • Hàng tuần: full lint pass                          │
│     • Hàng tháng: cross-check giá với bkns.vn            │
│                                                          │
│  3. GIT HOOK / WEBHOOK (trigger theo sự kiện)            │
│     • Khi có commit mới vào raw/ → tự động compile       │
│     • Khi có PR lint report → notify Telegram admin      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2.2. Ngôn ngữ lệnh Telegram (Command Language)

Thiết kế lệnh đơn giản, nhân viên không cần biết kỹ thuật:

```
Lệnh cơ bản:
  /hoi [câu hỏi]      → Query wiki (Flash + implicit cache)
  /them [URL]         → Ingest URL mới vào raw/
  /anh                → Đính kèm ảnh → ingest-image workflow
  /compile            → Trigger compile wiki từ raw/ mới
  /lint               → Chạy lint report ngay (Pro)
  /trangthai          → Xem trạng thái wiki: số file, token count, cache status

Lệnh admin:
  /duyet [file]       → Phê duyệt file wiki chờ review
  /rollback [commit]  → Rollback file wiki về commit cũ
  /report             → Xem báo cáo lint gần nhất
```

### 2.3. Luồng giao việc điển hình

**Kịch bản A: Nhân viên gửi bảng giá mới**
```
Nhân viên → gửi ảnh qua Telegram
Bot nhận → [ingest-image]
  → Lưu ảnh gốc: assets/evidence/price-screens/[name]-original.png
  → Flash Vision extract → bảng Markdown
  → Tạo thumbnail: assets/images/[name].png
  → Bot hỏi lại: "Đây có phải bảng giá Hosting không? Ghi vào file hosting/bang-gia.md?"
  → Admin reply "ok"
  → Bot ghi file + commit Git
  → Bot báo: "✅ Đã cập nhật. Xem tại wiki/products/hosting/bang-gia.md"
```

**Kịch bản B: Admin muốn cập nhật thông tin công ty**
```
Admin → /them https://bkns.vn/gioi-thieu
Bot → Crawl URL → lưu raw/website-crawl/gioi-thieu-2026-04.html
Bot → Hỏi: "Tôi thấy có thông tin mới về [X]. Compile vào wiki/company/gioi-thieu.md?"
Admin → "ok, nhưng bỏ phần quảng cáo"
Bot → Compile với chỉ dẫn bổ sung → tạo wiki draft
Bot → "Draft đã tạo, cần review trước khi publish. /duyet company/gioi-thieu"
Admin → /duyet company/gioi-thieu
Bot → Merge draft → commit → reload wiki_content
```

---

## 3. Bot Tự Kiểm Tra Tự Động

### 3.1. 4 lớp tự kiểm tra

```
LAYER 1: Syntax Check (mỗi commit)
  → Markdown valid?
  → Frontmatter YAML đúng format?
  → Relative path ảnh tồn tại?
  → Thực hiện bởi: script Python/bash nhẹ (không cần LLM)

LAYER 2: Semantic Check (hàng ngày, Flash)
  → Missing backlinks (có tham chiếu nhưng file không tồn tại)?
  → File orphan (không ai liên kết đến)?
  → Template compliance (có đủ frontmatter bắt buộc không)?
  → Thực hiện bởi: Gemini 2.5 Flash (~rẻ, nhanh)

LAYER 3: Content Lint (hàng tuần, Pro)
  → Giá có mâu thuẫn giữa các file?
  → Thông tin cũ hơn 30 ngày chưa được verify?
  → Nội dung không nhất quán (file A nói X, file B nói không-X)?
  → Thực hiện bởi: Gemini 2.5 Pro (cần reasoning sâu)

LAYER 4: Ground Truth Check (hàng tháng, Pro + web search)
  → Cross-check giá wiki vs giá thực tế trên bkns.vn
  → Sản phẩm trong wiki có còn tồn tại không?
  → Thực hiện bởi: Pro + tool web scraping bkns.vn
```

### 3.2. Cấu hình cron jobs

```yaml
# cron-config.yaml (trong OpenClaw)
jobs:
  - id: daily-syntax-check
    schedule: "0 6 * * *"        # 6h sáng mỗi ngày
    skill: syntax-check
    agent: bkns-flash-worker
    notify_on: failure            # chỉ báo khi có lỗi

  - id: daily-semantic-check
    schedule: "0 7 * * *"        # 7h sáng mỗi ngày
    skill: semantic-check
    agent: bkns-flash-worker
    notify_on: always

  - id: weekly-lint
    schedule: "0 9 * * 1"        # 9h sáng thứ Hai
    skill: lint-wiki
    agent: bkns-orchestrator
    output: logs/lint-reports/lint-{date}.md
    notify_on: always
    create_pr: true              # tạo Git branch + PR report

  - id: monthly-groundtruth
    schedule: "0 10 1 * *"       # 10h ngày 1 hàng tháng
    skill: ground-truth-check
    agent: bkns-orchestrator
    notify_on: always
    requires_human_review: true
```

### 3.3. Prompt chuẩn cho Lint Pass (Pro)

```python
LINT_PROMPT = """
Bạn là kiểm toán viên chất lượng wiki BKNS. Đọc toàn bộ wiki được cung cấp và thực hiện:

## NHIỆM VỤ LINT

### 1. Phát hiện mâu thuẫn giá
- Tìm tất cả giá tiền được đề cập
- Kiểm tra xem cùng một gói/sản phẩm có bị ghi giá khác nhau ở các file khác nhau không
- Output: Bảng mâu thuẫn với [file_A, giá_A] vs [file_B, giá_B]

### 2. Phát hiện thông tin lỗi thời
- Mọi fact có `updated:` trong frontmatter cũ hơn 30 ngày → đánh dấu "Cần verify"
- Tìm các ngày tháng cụ thể được đề cập có thể đã qua hạn

### 3. Phát hiện thiếu nguồn
- Mọi bảng giá không có `source:` URL → đánh dấu "Thiếu nguồn"
- Mọi claim quan trọng không có citation → liệt kê

### 4. Orphan detection
- Tìm file không được link từ index.md hoặc bất kỳ file nào khác

### 5. Đề xuất cải thiện
- Tối đa 5 đề xuất ưu tiên cao nhất

## FORMAT OUTPUT (Markdown)
---
# Báo Cáo Lint {ngày}
## 🔴 Mâu thuẫn giá (cần sửa ngay)
## 🟡 Thông tin cần verify
## 🟠 Thiếu nguồn trích dẫn
## 🔵 Orphan files
## 💡 Đề xuất cải thiện
---
Chỉ liệt kê vấn đề thực sự tìm thấy. Nếu không có vấn đề ở một category, ghi "✅ Không có vấn đề".
"""
```

---

## 4. Phát Hiện Trùng Lặp & Nội Dung Không Hợp Lý

### 4.1. Trùng lặp nội dung — 3 loại cần xử lý

**Loại 1: Trùng lặp exact (copy-paste)**
```python
# Phát hiện bằng hash, không cần LLM
import hashlib, os

def find_exact_duplicates(wiki_dir):
    hashes = {}
    duplicates = []
    for root, _, files in os.walk(wiki_dir):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                content = open(path).read()
                h = hashlib.md5(content.encode()).hexdigest()
                if h in hashes:
                    duplicates.append((path, hashes[h]))
                else:
                    hashes[h] = path
    return duplicates
```

**Loại 2: Trùng lặp semantic (cùng thông tin, diễn đạt khác)**
```
Prompt cho Flash:
"Đọc 2 đoạn văn sau. Chúng có mô tả cùng một thông tin không?
Nếu có: gợi ý nên giữ cái nào và cross-link cái kia.
[Đoạn A từ file X]
[Đoạn B từ file Y]"
```

**Loại 3: Thông tin conflicting (không phải trùng lặp — mâu thuẫn)**
```
Ví dụ: hosting/bang-gia.md nói "BKCP01: 26.000đ/tháng"
       hosting/gioi-thieu.md nói "Gói cơ bản từ 30.000đ/tháng"
→ Đây là CONFLICT, không phải duplicate
→ Cần verify với nguồn gốc (bkns.vn hoặc ảnh evidence/)
```

### 4.2. Phát hiện nội dung không hợp lý

```python
SANITY_CHECK_PROMPT = """
Kiểm tra các vấn đề logic trong wiki BKNS:

1. GIÁ BẤT HỢP LÝ:
   - Giá âm hoặc 0
   - Giá cao hơn 10× so với gói cùng loại không có giải thích
   - Đơn vị tiền tệ không nhất quán (đồng vs VNĐ vs k vs nghìn đồng)

2. THÔNG SỐ KỸ THUẬT BẤT HỢP LÝ:
   - RAM > storage (VPS 2GB RAM nhưng chỉ 1GB SSD)
   - Băng thông 0 hoặc "unlimited" mâu thuẫn với gói khác

3. NGÀY THÁNG BẤT HỢP LÝ:
   - updated: trong tương lai
   - Source URL ngày cũ hơn 6 tháng mà không có cờ "cần verify"

4. THÔNG TIN THIẾU BẮT BUỘC:
   - File trong products/ không có bảng giá
   - File không có `source:` trong frontmatter
   - Ảnh evidence được tham chiếu nhưng không tồn tại trong assets/

Output: Danh sách các vấn đề theo format [FILE][LOẠI][MÔ TẢ VẤN ĐỀ]
"""
```

### 4.3. Duplicate Detection Pipeline

```
Hàng tuần (sau lint pass):

[Scan toàn bộ wiki/]
      ↓
[Bước 1: Hash check → exact duplicates] (Python, 0 chi phí)
      ↓
[Bước 2: Cluster file theo category] (nhóm cùng products/, support/...)
      ↓
[Bước 3: Trong mỗi cluster, Flash so sánh semantic similarity]
  → Ngưỡng >80% giống nhau → flag là potential duplicate
      ↓
[Báo cáo: "Có thể hợp nhất: X và Y (82% tương đồng)"]
      ↓
[Admin quyết định: merge / keep-both / cross-link]
```

---

## 5. Tương Tác Người — Human-in-the-Loop

### 5.1. Ma trận quyết định: Bot tự làm vs. Hỏi người

```
┌─────────────────────────────┬──────────────┬─────────────────┐
│ Hành động                   │ Bot tự làm?  │ Cần người duyệt │
├─────────────────────────────┼──────────────┼─────────────────┤
│ Query câu hỏi → trả lời     │ ✅ Tự làm    │ Không           │
│ Ingest URL vào raw/         │ ✅ Tự làm    │ Không           │
│ Extract ảnh → Markdown draft│ ✅ Tự làm    │ Không           │
│ Tạo wiki draft từ raw/      │ ⚠️ Tạo draft │ Admin duyệt     │
│ Ghi đè file wiki hiện có    │ ❌ Không     │ Admin duyệt     │
│ Xóa file wiki               │ ❌ Không     │ Admin duyệt     │
│ Cập nhật bảng giá           │ ⚠️ Tạo draft │ Admin duyệt     │
│ Sửa system prompt           │ ❌ Không     │ Admin duyệt     │
│ Publish lint report         │ ✅ Tự làm    │ Không           │
│ Merge lint fixes vào main   │ ❌ Không     │ Admin duyệt     │
│ Rollback Git                │ ❌ Không     │ Admin duyệt     │
└─────────────────────────────┴──────────────┴─────────────────┘
```

### 5.2. Mẫu tương tác: Draft & Review Pattern

Thay vì bot ghi thẳng → bot tạo draft → người duyệt:

```
BOT → Tạo file wiki/products/hosting/bang-gia.md.DRAFT
BOT → Gửi Telegram: 
  "📝 Draft mới: bang-gia.md
   
   Thay đổi chính:
   • BKCP01: 26.000đ → 28.000đ (theo ảnh gửi lúc 14:30)
   • Thêm gói BKCP05: 120.000đ/tháng
   
   Xem draft: [link tới diff]
   
   Reply /duyet bang-gia để publish"

ADMIN → /duyet bang-gia
BOT → Rename .DRAFT → .md + commit + reload wiki_content
BOT → "✅ Published. Cache đã được invalidate."
```

### 5.3. Notification Levels

```yaml
# Cấu hình mức độ thông báo
notifications:
  critical:   # Luôn báo, cần hành động ngay
    - lint_conflict_found
    - file_write_failed
    - cache_invalidation_failed
    triggers: [telegram_admin, log_file]

  info:       # Báo nhưng không cần hành động
    - draft_created
    - compile_complete
    - cache_hit_stats_daily
    triggers: [telegram_admin]

  debug:      # Chỉ ghi log, không báo Telegram
    - query_processed
    - syntax_check_passed
    triggers: [log_file]
```

---

## 6. Phân Quyền Ghi File & Sửa File

### 6.1. Mô hình phân quyền 3 tầng

```
TẦNG 1: READ-ONLY (bot chỉ đọc)
  └── Không có — bot cần đọc mọi thứ để hoạt động

TẦNG 2: WRITE-WITH-DRAFT (bot ghi vào thư mục staging)
  ├── raw/           ← Bot ghi tự do (dữ liệu thô, ít rủi ro)
  ├── assets/        ← Bot ghi tự do (ảnh đã được extract)
  ├── logs/          ← Bot ghi tự do (logs, reports)
  └── wiki/.drafts/  ← Bot ghi draft (KHÔNG ghi thẳng vào wiki/)

TẦNG 3: WRITE-WITH-APPROVAL (cần admin approve)
  └── wiki/          ← Chỉ được ghi sau khi có /duyet từ admin
```

### 6.2. Cài đặt phân quyền trong OpenClaw

```yaml
# permissions.yaml
file_permissions:
  bkns-flash-worker:
    can_read: ["wiki/**", "raw/**", "assets/**", "logs/**"]
    can_write: ["raw/**", "assets/**", "logs/**", "wiki/.drafts/**"]
    can_delete: []  # Flash không được xóa gì
    requires_approval: ["wiki/**"]  # (ngoại trừ .drafts/)

  bkns-orchestrator:
    can_read: ["**"]
    can_write: ["raw/**", "assets/**", "logs/**", "wiki/.drafts/**"]
    can_delete: ["raw/**"]  # Pro được xóa raw/ sau khi compile
    requires_approval: ["wiki/**"]

  # Human admin (qua /duyet command)
  admin:
    can_approve: ["wiki/**"]  # Unlock ghi vào wiki/
    can_force_write: ["**"]   # Override mọi restriction
    can_rollback: ["**"]
```

### 6.3. Git Branch Strategy cho an toàn

```
main            ← Wiki production (chỉ admin merge)
├── draft/      ← Bot tạo draft ở đây
│   ├── draft/bang-gia-2026-04-04
│   └── draft/vps-cloud-update
└── lint/       ← Lint reports tự động
    └── lint/2026-04-01
```

```bash
# Bot workflow khi tạo draft
git checkout -b draft/bang-gia-$(date +%Y-%m-%d)
# ... tạo/sửa file ...
git commit -m "draft: cập nhật bảng giá hosting Q2/2026"
git push origin draft/bang-gia-$(date +%Y-%m-%d)
# → Tạo PR → Notify admin → Admin review → Merge main
```

---

## 7. Vòng Lặp Tự Động — Tuần Hoàn

### 7.1. Đồng hồ tổng thể

```
           VÒNG LẶP TỰ ĐỘNG BKNS WIKI
           
THỜI GIAN  HÀNH ĐỘNG                  AGENT
─────────  ─────────────────────────  ──────────
Mỗi query  Query bot (on-demand)      Flash
06:00      Syntax check               Flash
07:00      Semantic check             Flash
22:00      Compile raw/ mới (nếu có) Orchestrator

─────── Hàng tuần (Thứ Hai) ──────
09:00      Full lint pass             Pro
09:30      Duplicate detection        Flash → Pro
10:00      Notify admin lint report   Flash
10:15      Create lint PR branch      Git hook

─────── Hàng tháng (Ngày 1) ──────
10:00      Ground truth check         Pro + web
11:00      Price cross-check bkns.vn  Pro + scraper
12:00      Monthly summary report     Flash
12:30      Notify: "Cần review X file"Admin Telegram
```

### 7.2. Event-Driven (ngoài lịch cố định)

```python
# Các trigger theo sự kiện, không theo lịch
EVENT_TRIGGERS = {
    "new_image_received": ["ingest-image", "ask-confirm-location"],
    "new_url_received":   ["crawl-url", "save-raw", "ask-compile"],
    "raw_file_added":     ["classify-raw", "suggest-compile"],
    "wiki_compiled":      ["invalidate-cache", "reload-wiki-content"],
    "lint_conflict_found":["create-pr", "notify-admin-critical"],
    "price_mismatch_found":["flag-for-review", "notify-admin-critical"],
}
```

### 7.3. Cache Invalidation Flow

Điểm tế nhị quan trọng: khi wiki thay đổi, phải invalidate implicit cache:

```python
def update_wiki_and_invalidate(new_file_path, new_content):
    """Ghi wiki và cập nhật prefix cho implicit caching."""
    
    # 1. Ghi file
    with open(new_file_path, 'w') as f:
        f.write(new_content)
    
    # 2. Git commit
    subprocess.run(["git", "add", new_file_path])
    subprocess.run(["git", "commit", "-m", f"update: {new_file_path}"])
    
    # 3. QUAN TRỌNG: Reload wiki_content toàn bộ
    # Phải đọc lại TẤT CẢ file để build prefix mới
    global wiki_content
    wiki_content = load_wiki("/home/openclaw/wiki/wiki/")
    
    # 4. Implicit cache tự động invalidate vì wiki_content đã thay đổi
    # (prefix khác → Gemini không cache hit → tự build cache mới)
    log("Cache invalidated. Next query sẽ build cache mới.")
```

---

## 8. Hệ Thống Skill — Tìm Ở Đâu

### 8.1. Kho skill hiện có (trong project này)

```
/mnt/skills/
├── public/                    ← Skill dùng chung
│   ├── docx/SKILL.md          ← Tạo/đọc Word document
│   ├── pdf/SKILL.md           ← Tạo/đọc/merge PDF
│   ├── pdf-reading/SKILL.md   ← Đọc & extract PDF
│   ├── xlsx/SKILL.md          ← Spreadsheet
│   ├── pptx/SKILL.md          ← Presentation
│   ├── file-reading/SKILL.md  ← Router đọc file mọi loại
│   └── frontend-design/SKILL.md ← UI/UX components
│
└── examples/                  ← Skill mẫu nâng cao
    ├── doc-coauthoring/SKILL.md    ← ⭐ RẤT LIÊN QUAN
    ├── skill-creator/SKILL.md      ← Tạo skill mới
    ├── mcp-builder/SKILL.md        ← Build MCP server
    ├── internal-comms/SKILL.md     ← Thông báo nội bộ
    └── web-artifacts-builder/SKILL.md ← Build web tools
```

### 8.2. Skill nào quan trọng nhất với BKNS Wiki

| Skill | Liên quan | Dùng cho |
|-------|-----------|----------|
| `doc-coauthoring` | ⭐⭐⭐ Rất cao | Biên soạn wiki file, structured writing workflow |
| `file-reading` | ⭐⭐⭐ Rất cao | Đọc PDF bảng giá, DOCX nội bộ, ảnh |
| `pdf-reading` | ⭐⭐ Cao | Extract bảng giá từ PDF gốc BKNS |
| `skill-creator` | ⭐⭐ Cao | Tạo skill mới: ingest-image, compile-wiki, lint-wiki |
| `mcp-builder` | ⭐⭐ Cao | Build MCP cho OpenClaw tích hợp thêm |
| `internal-comms` | ⭐ Vừa | Notify Telegram admin theo template |

### 8.3. Skill cần tự xây cho dự án này

Các skill chưa có trong kho, cần viết mới:

```
SKILL MỚI CẦN BUILD:
├── ingest-raw          → Nhận URL/file → lưu raw/ + metadata
├── ingest-image        → Ảnh → Vision extract → thumbnail + evidence
├── compile-wiki        → raw/ → wiki/ Markdown chuẩn hóa
├── query-wiki          → Câu hỏi → Flash + implicit cache → trả lời
├── lint-wiki           → Wiki → Pro health check → diff report
├── cross-link          → ⭐ Xem mục 9 bên dưới
├── syntax-check        → Markdown/YAML validation (không cần LLM)
├── semantic-check      → Flash kiểm tra orphan, missing backlinks
└── ground-truth-check  → Pro + web scraper verify giá thực tế
```

---

## 9. Skill Thủ Thư & Quản Lý Wiki

### 9.1. Skill quan trọng nhất còn thiếu: `cross-link`

Đây là skill **khác biệt nhất** so với ý tưởng gốc Karpathy — quản lý liên kết chéo tự động:

```python
# cross-link skill prompt
CROSS_LINK_PROMPT = """
Bạn là thủ thư wiki BKNS. Đọc toàn bộ wiki và thực hiện:

## NHIỆM VỤ CROSS-LINK

### 1. Phát hiện liên kết tiềm năng
Trong mỗi file wiki, tìm các khái niệm/sản phẩm được đề cập nhưng CHƯA có link:
- Tên sản phẩm: "hosting", "VPS MMO", "tên miền .vn", "SSL Wildcard"...
- Chủ đề liên quan: "JetBackup", "cPanel", "VNNIC"...
- File tham chiếu: mỗi khái niệm có file wiki tương ứng không?

### 2. Tạo liên kết chéo
Nếu "VPS MMO" được đề cập trong hosting/bang-gia.md nhưng chưa có link:
→ Thêm: [[../vps-cloud/vps-mmo]] vào cuối đoạn tham chiếu

### 3. Cập nhật index.md
Đảm bảo index.md có đầy đủ link đến mọi file trong wiki/

### 4. Tạo "Xem thêm" section
Cuối mỗi file nên có:
```markdown
## Xem thêm
- [[../related-file-1]] — Mô tả ngắn tại sao liên quan
- [[../related-file-2]] — Mô tả ngắn
```

OUTPUT: Danh sách thay đổi cần thực hiện (bot sẽ apply sau khi admin duyệt)
FORMAT: [FILE] [DÒNG] [NỘI DUNG THÊM/SỬA]
"""
```

### 9.2. Skill `compile-wiki` — phiên bản thủ thư đầy đủ

Karpathy định nghĩa compile là bước quan trọng nhất. Dưới đây là prompt compile hoàn chỉnh:

```python
COMPILE_PROMPT = """
Bạn là thủ thư biên tập wiki BKNS. Nhận tài liệu thô và compile thành wiki chuẩn.

## INPUT
Tài liệu thô: {raw_content}
Loại tài liệu: {doc_type}  # website, image-extracted, internal-doc, pdf
Ngày nhận: {date}
Nguồn: {source_url}

## NHIỆM VỤ

### 1. Phân tích và phân loại
- Đây là thông tin về sản phẩm nào? Đặt vào thư mục nào trong wiki/?
- Có thông tin giá không? → Cần extract riêng vào bảng
- Có thông tin kỹ thuật không? → Cần bảng specs

### 2. Biên tập nội dung
- Loại bỏ: quảng cáo, nội dung trùng lặp, thông tin không liên quan
- Giữ nguyên: số liệu cụ thể, tên gói, giá, thông số kỹ thuật
- Chuẩn hóa: đơn vị tiền tệ (→ đồng/tháng), đơn vị dung lượng (GB/TB)

### 3. Tạo file Markdown theo template chuẩn
```yaml
---
title: [Tên chính xác của sản phẩm/chủ đề]
category: [hosting|vps|ten-mien|email|ssl|company|support|sales]
updated: {date}
source: {source_url}
confidence: [high|medium|low]  # Độ tin cậy của thông tin
evidence: [đường dẫn ảnh nếu có]
---
```

### 4. Backlink gợi ý
Cuối file, đề xuất: "File này nên link đến: [danh sách file liên quan]"

### 5. Cờ cần review
Nếu có thông tin không chắc chắn → đánh dấu:
> ⚠️ **Cần verify:** [thông tin cụ thể] — Nguồn không rõ ràng

## OUTPUT
Trả về file Markdown hoàn chỉnh + JSON metadata:
{"suggested_path": "wiki/products/hosting/...", "requires_review": true/false, "flags": [...]}
"""
```

### 9.3. Cấu trúc phân bổ thư mục — đánh giá lại

Cấu trúc hiện tại trong `ytuongbandau.md` **tốt nhưng thiếu một số thư mục quan trọng**:

```
wiki/                     ← Cấu trúc hiện tại (giữ nguyên)
├── index.md              ← QUAN TRỌNG: Phải là "bản đồ" toàn bộ wiki
├── company/
├── products/
│   ├── ten-mien/
│   ├── hosting/
│   ├── vps-cloud/
│   ├── may-chu/
│   ├── email/
│   └── ssl/
├── support/
├── sales/
├── technical/
└── faq/

THÊM MỚI (đề xuất):
├── policies/             ← ⭐ THIẾU: Chính sách hoàn tiền, bảo hành, SLA
├── comparisons/          ← ⭐ THIẾU: So sánh gói (hosting vs VPS, các đối thủ)
├── onboarding/           ← Tài liệu nhân viên mới
└── .drafts/              ← Thư mục draft (bot ghi, chưa publish)
```

---

## 10. Đánh Giá Kiến Trúc Hiện Tại & Cải Thiện

### 10.1. Những gì đã tốt trong `ytuongbandau.md`

| Điểm mạnh | Chi tiết |
|-----------|----------|
| ✅ Implicit caching đúng | Đã chuyển từ explicit → implicit, tiết kiệm đáng kể |
| ✅ Git LFS cho evidence | Path đúng (assets/evidence/), pattern đúng |
| ✅ Multi-agent architecture | Pro (orchestrator) + Flash (worker) hợp lý |
| ✅ 6-stage pipeline | Sát với Karpathy: Raw→Ingest→Compile→View→Query→Filing→Linting |
| ✅ Template file chuẩn | Frontmatter YAML + bảng giá + details block |
| ✅ Budget realistic | ~$19/tháng là trung thực, không phải $9 |

### 10.2. Những gì cần cải thiện

| Vấn đề | Mức độ | Giải pháp |
|--------|--------|-----------|
| ❌ Thiếu Draft/Review pattern | Nghiêm trọng | Thêm wiki/.drafts/, /duyet command |
| ❌ Thiếu cross-link skill | Cao | Build skill cross-link (xem mục 9.1) |
| ❌ Thiếu policies/ folder | Cao | Thêm vào cấu trúc thư mục |
| ❌ Thiếu duplicate detection | Cao | Thêm vào lint pipeline |
| ❌ Cron config không có trong tài liệu | Vừa | Thêm cron-config.yaml |
| ❌ Không có rollback workflow | Vừa | Git branch strategy + /rollback command |
| ❌ Hotline BKNS vẫn trống | Vừa | Cần điền trước Phase 1 |
| ⚠️ index.md chưa được define rõ | Thấp | Cần template cho index.md |

### 10.3. Template cho `wiki/index.md` (còn thiếu trong tài liệu)

```markdown
---
title: BKNS Wiki Index
updated: {auto-updated-date}
total_files: {auto-count}
total_tokens: {auto-estimate}
---

# BKNS Knowledge Wiki — Bản Đồ

> Cập nhật tự động bởi bot. Lần cập nhật cuối: {date}

## Công Ty
- [[company/gioi-thieu]] — Hồ sơ, lịch sử, địa chỉ
- [[company/gia-tri-cot-loi]] — Giá trị cốt lõi, cam kết
- [[company/doi-tac]] — Đối tác, chứng nhận

## Sản Phẩm
### Tên Miền
- [[products/ten-mien/tong-quan]] — Giới thiệu dịch vụ
- [[products/ten-mien/bang-gia]] — Bảng giá đầy đủ
- [[products/ten-mien/huong-dan]] — Hướng dẫn đăng ký

### Hosting
- [[products/hosting/tong-quan]]
- [[products/hosting/bang-gia]]
[... tương tự cho VPS, Email, SSL ...]

## Hỗ Trợ
- [[support/lien-he]] — Hotline, live chat, địa chỉ
- [[support/chinh-sach]] — Chính sách hoàn tiền, SLA

## FAQ
- [[faq/ten-mien]] — Câu hỏi về tên miền
- [[faq/hosting]] — Câu hỏi về hosting
[...]

---
*Auto-generated index. Do not edit manually.*
```

---

## 11. Sát Với Karpathy — Những Gì Còn Thiếu

### 11.1. So sánh với pipeline gốc Karpathy

Karpathy đề xuất pipeline đơn giản:
```
Raw Data → LLM → Markdown → Context Window → Q&A
```

Dự án BKNS đã mở rộng tốt, nhưng **3 điểm Karpathy nhấn mạnh chưa được implement đầy đủ:**

#### Điểm 1: "Filing" — Câu trả lời hay → vào wiki tự động

Karpathy đề xuất: câu trả lời hay từ Q&A session tự động được file vào knowledge base.

**Hiện tại:** Chưa có skill `auto-file`
**Cần thêm:**
```python
AUTO_FILE_PROMPT = """
Câu hỏi: {question}
Câu trả lời bot: {answer}
Đánh giá:
1. Câu trả lời này có thể tái sử dụng không? (y/n)
2. Nếu y: đặt vào faq/[category].md với format Q&A chuẩn
3. Nếu câu hỏi chưa có trong wiki nhưng câu trả lời đúng → compile thêm fact mới

Ngưỡng tự động file: admin rate câu trả lời ⭐⭐⭐⭐+ hoặc câu hỏi xuất hiện ≥3 lần
"""
```

#### Điểm 2: "View" — Con người phải đọc được wiki dễ dàng

Karpathy nhấn mạnh wiki phải **readable by humans**, không chỉ readable by LLM.

**Hiện tại:** Chỉ có Markdown files trong Git repo
**Cần thêm:** Web viewer đơn giản hoặc Obsidian vault để nhân viên đọc wiki dễ dàng không cần Git

```bash
# Option đơn giản: dùng mkdocs
pip install mkdocs mkdocs-material
mkdocs serve  # → http://localhost:8000 — wiki dạng web đẹp
```

#### Điểm 3: LLM là "compiler" — không phải "editor"

Karpathy cẩn thận: LLM compile từ dữ liệu thô, không tự phịa dữ liệu mới.

**Hiện tại:** Prompt compile-wiki có thể cho phép LLM "sáng tạo" quá nhiều
**Cần thêm:** Ràng buộc chặt hơn trong compile prompt:
```
COMPILE RULE: Mọi fact trong output phải có trong input raw data.
Nếu LLM muốn thêm thông tin bổ sung → đánh dấu [SUYLUẬN] và yêu cầu verify.
LLM không được tạo ra bảng giá, thông số kỹ thuật mà không có trong raw data.
```

### 11.2. Roadmap bổ sung để sát Karpathy hơn

```
PHASE 1.5 (ngay sau Phase 1):
  □ Build skill auto-file (Q&A hay → faq/)
  □ Setup mkdocs viewer cho nhân viên
  □ Thêm COMPILE RULE vào prompt

PHASE 2.5 (sau Phase 2):
  □ Build skill cross-link đầy đủ
  □ Build duplicate detection
  □ Thêm policies/ folder
  □ Draft/Review pattern hoàn chỉnh
```

---

## 12. Repo & Dự Án Tham Khảo Nên Nghiên Cứu

### 12.1. Repo trực tiếp liên quan đến ý tưởng Karpathy

| Repo | Link | Học gì |
|------|------|--------|
| **karpathy/llm.c** | github.com/karpathy/llm.c | Tư duy compile từ dữ liệu thô |
| **Obsidian** | obsidian.md | Graph view, backlinks, wiki pattern |
| **MkDocs Material** | squidfunk.github.io/mkdocs-material | Wiki viewer đẹp, free |
| **Quartz** | quartz.jzhao.cc | Obsidian → web, rất phù hợp cho wiki nội bộ |

### 12.2. Repo về LLM-powered knowledge management

| Repo | Link | Học gì |
|------|------|--------|
| **MemGPT** | github.com/cpacker/MemGPT | Memory management cho LLM agent |
| **LlamaIndex** | llamaindex.ai | Dù dùng RAG, nhưng có nhiều pattern tốt về ingestion |
| **Haystack** | haystack.deepset.ai | Pipeline pattern cho document processing |
| **Docling** | github.com/DS4SD/docling | Extract PDF/DOCX/ảnh → Markdown rất tốt |

### 12.3. Repo liên quan đến OpenClaw & Gemini

| Repo | Link | Học gì |
|------|------|--------|
| **OpenClaw docs** | docs.openclaw.ai | Skill format, agent config, channel bindings |
| **Vertex AI samples** | github.com/GoogleCloudPlatform/vertex-ai-samples | Gemini API patterns, implicit caching examples |
| **Gemini cookbook** | github.com/google-gemini/cookbook | Context caching, vision, long context patterns |

### 12.4. Skill `doc-coauthoring` — Áp dụng vào compile-wiki

Skill `doc-coauthoring` trong `/mnt/skills/examples/doc-coauthoring/SKILL.md` rất liên quan. Nó định nghĩa workflow 3 bước:

1. **Context Gathering** → Tương đương: bot hỏi "Đây là thông tin về gì? Đặt vào thư mục nào?"
2. **Refinement & Structure** → Tương đương: compile-wiki tạo draft → admin review → refine
3. **Reader Testing** → Tương đương: test query bot với draft wiki để xem bot trả lời đúng không trước khi publish

**→ Nên adapt workflow này vào compile-wiki skill của BKNS.**

---

## Tóm Tắt: Checklist Triển Khai Bot Hoàn Chỉnh

```
TRƯỚC KHI BẮT ĐẦU:
  □ Xác nhận $300 là billing hay trial credit
  □ Điền hotline BKNS chính thức
  □ Xác nhận model string trong OpenClaw

PHASE 1 (bắt buộc):
  □ Git repo + cấu trúc thư mục đầy đủ (kể cả wiki/.drafts/, policies/)
  □ Git LFS setup đúng cách
  □ 5 skill cơ bản: ingest-raw, compile-wiki, query-wiki, lint-wiki, ingest-image
  □ Draft/Review pattern + /duyet command
  □ Cron jobs: daily syntax-check, weekly lint
  □ wiki/index.md template

PHASE 1.5 (nên làm sớm):
  □ Skill auto-file (câu trả lời hay → faq/)
  □ MkDocs viewer cho nhân viên
  □ Skill cross-link cơ bản
  □ Compile Rule ràng buộc chặt hơn

PHASE 2+:
  □ Duplicate detection pipeline
  □ Flash Worker multi-agent (khi >20 queries/giờ)
  □ Ground truth check hàng tháng
  □ Skill ground-truth-check + web scraper bkns.vn
```

---

*bot.md v1.0 · BKNS Knowledge Wiki · 2026-04-04*
*Tổng hợp từ thảo luận: vận hành bot, phân quyền, tự kiểm tra, Karpathy alignment, skill ecosystem*

