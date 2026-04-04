# Bước 1: Setup Infrastructure — Git, Env, Folder Structure

> **Phase:** 0.5 — Tuần 1
> **Ước lượng:** 1-2 giờ
> **Prerequisite:** VPS đã có OpenClaw, Python 3.10+, git
> **Output:** Repo sạch + cấu trúc đầy đủ + .env + registries

---

## CHECKLIST

- [ ] 1.1 Git init + .gitignore + .gitattributes
- [ ] 1.2 Tạo toàn bộ cấu trúc thư mục
- [ ] 1.3 Tạo .env với đủ biến
- [ ] 1.4 Tạo registry files (sources, entities)
- [ ] 1.5 Tạo active-build.yaml (v0.0 initial)
- [ ] 1.6 Tạo agents.yaml cho OpenClaw
- [ ] 1.7 Commit initial structure

---

## 1.1 Git Init

```bash
cd /home/openclaw/wiki
git init
git lfs install
```

### .gitignore

```
# Secrets
.env
*.json.bak

# Logs (tùy chọn — có thể commit)
logs/

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# MkDocs build output
site/

# OS
.DS_Store
Thumbs.db
```

### .gitattributes (Git LFS cho ảnh gốc)

```
assets/evidence/** filter=lfs diff=lfs merge=lfs -text
```

```bash
git lfs track "assets/evidence/**"
```

---

## 1.2 Tạo Cấu Trúc Thư Mục

```bash
mkdir -p raw/website-crawl raw/manual
mkdir -p claims/products/hosting claims/products/vps
mkdir -p claims/products/ten-mien claims/products/email claims/products/ssl
mkdir -p entities sources
mkdir -p wiki/company wiki/products/hosting wiki/products/vps
mkdir -p wiki/products/ten-mien wiki/products/email wiki/products/ssl
mkdir -p wiki/support wiki/onboarding wiki/.drafts
mkdir -p build/snapshots
mkdir -p assets/evidence/price-screens assets/images
mkdir -p logs/lint logs/ground-truth
mkdir -p skills/query-wiki/scripts
mkdir -p skills/ingest-raw/scripts
mkdir -p skills/compile-wiki/scripts
```

---

## 1.3 File .env

> ⚠️ File này KHÔNG được commit. Chỉ tạo thủ công trên server.

```bash
cat > /home/openclaw/wiki/.env << 'EOF'
# Vertex AI
VERTEX_PROJECT_ID=YOUR_PROJECT_ID
VERTEX_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/home/openclaw/api/duytam29284.json

# Telegram
TELEGRAM_BOT_TOKEN=8790440541:AAFZLkj2l9VO_RjsB6FCmai4Ri-VK4KoIHQ
ADMIN_TELEGRAM_ID=882968821

# Wiki
WIKI_DIR=/home/openclaw/wiki/wiki/
CLAIMS_DIR=/home/openclaw/wiki/claims/
RAW_DIR=/home/openclaw/wiki/raw/
BUILD_DIR=/home/openclaw/wiki/build/
LOGS_DIR=/home/openclaw/wiki/logs/

# Models
MODEL_QUERY=gemini-2.5-flash
MODEL_COMPILE=gemini-2.5-pro
MODEL_LINT=gemini-2.5-pro
MODEL_INGEST=gemini-2.5-flash
EOF
```

> 📝 Thay `YOUR_PROJECT_ID` bằng project ID thực tế từ Google Cloud Console.

---

## 1.4 Registry Files

### sources/registry.yaml

```yaml
# Source Registry — Danh sách nguồn dữ liệu đã được xác nhận
# Thêm mỗi nguồn mới vào đây trước khi crawl

sources:
  - source_id: SRC-BKNS-WEB-001
    type: official_website
    url: https://bkns.vn
    authority: primary
    trust_level: high
    description: Website chính thức BKNS.VN
    last_crawled: null
    note: Nguồn duy nhất được phép cho pricing claims

  - source_id: SRC-BKNS-WEB-HOSTING
    type: official_website_section
    url: https://bkns.vn/hosting
    authority: primary
    trust_level: high
    parent: SRC-BKNS-WEB-001
    last_crawled: null

  - source_id: SRC-BKNS-WEB-VPS
    type: official_website_section
    url: https://bkns.vn/vps
    authority: primary
    trust_level: high
    parent: SRC-BKNS-WEB-001
    last_crawled: null

  - source_id: SRC-BKNS-WEB-DOMAIN
    type: official_website_section
    url: https://bkns.vn/ten-mien
    authority: primary
    trust_level: high
    parent: SRC-BKNS-WEB-001
    last_crawled: null

  - source_id: SRC-BKNS-WEB-SUPPORT
    type: official_website_section
    url: https://bkns.vn/ho-tro
    authority: primary
    trust_level: high
    parent: SRC-BKNS-WEB-001
    last_crawled: null
```

### entities/registry.yaml

```yaml
# Entity Registry — Danh sách các thực thể được track trong wiki

entities:
  - entity_id: ENT-COMPANY-001
    name: BKNS
    full_name: Công ty CP Công nghệ BKNS
    type: company
    description: Nhà cung cấp hosting, tên miền, VPS hàng đầu Việt Nam
    website: https://bkns.vn
    contact:
      hotline_support: "1900 63 68 09"
      hotline_sales: "1800 646 884"
    status: active

  - entity_id: ENT-PROD-HOSTING
    name: Shared Hosting
    type: product_category
    parent: ENT-COMPANY-001
    description: Dịch vụ hosting dùng chung
    wiki_path: wiki/products/hosting/
    status: active

  - entity_id: ENT-PROD-VPS
    name: VPS
    type: product_category
    parent: ENT-COMPANY-001
    description: Virtual Private Server
    wiki_path: wiki/products/vps/
    status: active

  - entity_id: ENT-PROD-DOMAIN
    name: Tên miền
    type: product_category
    parent: ENT-COMPANY-001
    description: Đăng ký và quản lý tên miền
    wiki_path: wiki/products/ten-mien/
    status: active

  - entity_id: ENT-PROD-EMAIL
    name: Email Hosting
    type: product_category
    parent: ENT-COMPANY-001
    description: Dịch vụ email theo tên miền
    wiki_path: wiki/products/email/
    status: active

  - entity_id: ENT-PROD-SSL
    name: SSL Certificate
    type: product_category
    parent: ENT-COMPANY-001
    description: Chứng chỉ bảo mật SSL/TLS
    wiki_path: wiki/products/ssl/
    status: active
```

### claims/registry.yaml

```yaml
# Claims Registry — Index tất cả claims đã tạo
# Mỗi claim mới phải được thêm vào đây

claims: []
# Format mỗi entry:
# - claim_id: CLM-HOST-001
#   entity_id: ENT-PROD-HOSTING
#   attribute: pricing
#   file: claims/products/hosting/shared-hosting-pricing.yaml
#   status: approved  # pending|approved|superseded|rejected
#   created_at: 2026-04-04
#   approved_at: null
#   approved_by: null
```

---

## 1.5 Build Files

### build/active-build.yaml

```yaml
# Active Build Pointer — Bot đọc file này khi khởi động
# Đổi build_id để rollback về version cũ

build_id: v0.0
build_date: 2026-04-04
description: Initial structure — no wiki content yet
wiki_token_estimate: 0
wiki_files: 0
claims_count: 0
git_tag: null
status: empty
```

### build/snapshots/ (tạo thư mục trống)

```bash
touch build/snapshots/.gitkeep
```

---

## 1.6 agents.yaml (OpenClaw Config)

```yaml
# OpenClaw Agent Configuration — BKNS Wiki Bot
name: bkns-wiki-agent
description: Agent wiki tri thức BKNS — thủ thư tự động

telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  admin_ids:
    - ${ADMIN_TELEGRAM_ID}

workspace: /home/openclaw/wiki/

models:
  default: gemini-2.5-flash
  compile: gemini-2.5-pro
  lint: gemini-2.5-pro

vertex_ai:
  project: ${VERTEX_PROJECT_ID}
  location: ${VERTEX_LOCATION}
  credentials: ${GOOGLE_APPLICATION_CREDENTIALS}

skills:
  - skills/query-wiki/SKILL.md
  # Phase 1:
  # - skills/ingest-raw/SKILL.md
  # - skills/compile-wiki/SKILL.md
  # Phase 2:
  # - skills/ingest-image/SKILL.md
  # - skills/lint-wiki/SKILL.md

memory:
  type: file
  path: /home/openclaw/wiki/build/active-build.yaml

logging:
  level: INFO
  path: /home/openclaw/wiki/logs/
```

---

## 1.7 Commit Initial Structure

```bash
cd /home/openclaw/wiki

# Stage tất cả (trừ .env đã trong .gitignore)
git add .gitignore .gitattributes agents.yaml
git add sources/ entities/ claims/registry.yaml
git add build/ skills/
git add wiki/.gitkeep 2>/dev/null || true

# Commit
git commit -m "feat(infra): initial project structure

- Full directory layout theo addon.md schema
- Source registry: 5 BKNS sources
- Entity registry: 6 entities (company + 5 products)
- Claims registry: empty (ready for Phase 0.5)
- active-build.yaml: v0.0 initial
- OpenClaw agents.yaml skeleton"

# Tag
git tag infra/v0.0
```

---

## DEFINITION OF DONE

- [ ] `git status` sạch (không có untracked files quan trọng)
- [ ] `.env` tồn tại, KHÔNG xuất hiện trong `git status`
- [ ] `sources/registry.yaml` có 5 sources
- [ ] `entities/registry.yaml` có 6 entities
- [ ] `build/active-build.yaml` tồn tại
- [ ] `agents.yaml` tồn tại với model đúng
- [ ] Git tag `infra/v0.0` đã tạo

---

## TIẾP THEO

→ [02-crawl-claims.md](02-crawl-claims.md) — Crawl bkns.vn + tạo claims
