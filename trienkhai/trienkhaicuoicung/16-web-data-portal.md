# Spec Web: Web Data Portal — Giao Diện Upload Dữ Liệu

> **Phiên bản:** 2.0 — 2026-04-05
> **Trạng thái:** ✅ Deployed — Production
> **Domain:** https://upload.trieuphu.biz
> **Port:** 3000 (Node.js) → Nginx 443 (SSL)
> **Liên quan:** addon.md Section 28, ytuongbandau.md Section 13

---

## Mục Đích

Cung cấp giao diện web cho phép admin upload tài liệu đa định dạng (PDF, DOCX, XLSX, MD, TXT, PNG, JPG) vào `raw/web/` layer, thay thế quy trình copy thủ công hiện tại. Hỗ trợ trigger pipeline tự động hoặc thủ công.

---

## 1. Tổng Quan

### 1.1. Vấn đề (Đã giải quyết)

| Phương thức cũ | Hạn chế | Giải pháp mới |
|--------|---------|--------------|
| SSH copy → `raw/manual/` | Cần SSH access, không trực quan | Web upload drag & drop |
| Telegram → `ingest-image` | Chỉ ảnh, không PDF/DOCX | Web hỗ trợ 7 định dạng |
| `crawl-source` | Bị Cloudflare block | Upload trực tiếp |

### 1.2. Stack (Deployed)

| Component | Technology | Status |
|-----------|-----------|--------|
| Backend | Node.js 18+ / Express 4.21 | ✅ Running |
| Frontend | Vanilla HTML/CSS/JS (Glassmorphism) | ✅ Deployed |
| Upload | Multer 1.4.5 | ✅ Active |
| Auth | Bearer token + bcrypt | ✅ Active |
| Security | Helmet 7.1, express-rate-limit 7.4 | ✅ Active |
| Process Manager | PM2 | ✅ Online |
| SSL | Let's Encrypt (certbot, auto-renewal) | ✅ Active |
| Reverse Proxy | Nginx (TLS 1.2+, HSTS) | ✅ Active |

---

## 2. API Endpoints (Verified)

### 2.1. Login

```
POST /api/login
Headers: Content-Type: application/json
Body: { "password": "admin_password" }

Response 200: { "token": "bearer_token_here" }
Response 401: { "error": "Sai mật khẩu" }
Response 429: { "error": "Quá nhiều lần đăng nhập thất bại. Thử lại sau 15 phút." }

Rate limit: 5 requests/15 minutes (Nginx) + 10 requests/15 minutes (Express)
```

### 2.2. Upload

```
POST /api/upload
Headers: Authorization: Bearer {ADMIN_TOKEN}
Body: multipart/form-data
  - files: File[] (max 10 files, max 50MB each)
  - trigger: "true" | "false" (auto-trigger pipeline)

Response 200:
{
  "uploaded": [
    {
      "id": "c82c0b45",
      "filename": "original.pdf",
      "size": 1234567,
      "uploaded_at": "2026-04-05T08:07:18.135Z",
      "pipeline_status": "pending" | "queued"
    }
  ],
  "trigger": false
}

Rate limit: 2 requests/second (Nginx)
```

### 2.3. List Files

```
GET /api/files?source=web|manual|all&page=1&limit=15
Headers: Authorization: Bearer {ADMIN_TOKEN}

Response 200:
{
  "files": [
    {
      "id": "uuid",
      "filename": "document.pdf",
      "stored_name": "uuid-document.pdf",
      "path": "raw/web/2026-04-05/uuid-document.pdf",
      "size": 1234567,
      "mtime": "2026-04-05T08:07:18Z",
      "source": "web" | "manual",
      "uploaded_at": "2026-04-05T08:07:18Z"
    }
  ],
  "total": 147,
  "page": 1,
  "limit": 15
}
```

### 2.4. Delete File

```
DELETE /api/files/:id
Headers: Authorization: Bearer {ADMIN_TOKEN}

Response 200: { "deleted": true, "filename": "uuid-original.pdf" }
Response 404: { "error": "File not found" }

Note: Chỉ xóa được file trong raw/web/ (path traversal guard)
```

### 2.5. Trigger Pipeline

```
POST /api/trigger
Headers: Authorization: Bearer {ADMIN_TOKEN}
Body: { "action": "extract" | "compile" | "full" }

Response 200: { "job_id": "uuid", "status": "started", "action": "full" }
Response 409: { "error": "Pipeline đang chạy. Vui lòng đợi hoàn tất." }
```

### 2.6. Status

```
GET /api/status
Headers: Authorization: Bearer {ADMIN_TOKEN}

Response 200:
{
  "pipeline": "idle" | "running" | "success" | "failed",
  "last_run": "2026-04-05T08:34:30.345Z",
  "last_result": "success",
  "build_version": "snapshots",
  "wiki_stats": {
    "total_files": 147,
    "web_files": 0,
    "manual_files": 147,
    "wiki_pages": 20,
    "total_claims": 1619,
    "build_version": "snapshots"
  }
}
```

---

## 3. File Structure (Deployed)

```
/home/openclaw/wiki/
├── web/                              ✅ DEPLOYED
│   ├── server.js                     ← Express server (helmet, CORS, rate limit)
│   ├── package.json                  ← 8 dependencies
│   ├── ecosystem.web.config.js       ← PM2 config (256MB limit)
│   ├── deploy-nginx.sh              ← One-click SSL deploy script
│   ├── nginx-upload.trieuphu.biz.conf ← Nginx SSL config
│   ├── middleware/
│   │   └── auth.js                   ← Bearer token + bcrypt auth
│   ├── routes/
│   │   ├── upload.js                 ← Multer upload (UUID names, JSONL audit)
│   │   ├── files.js                  ← Recursive file scan + delete
│   │   ├── trigger.js                ← Pipeline trigger with lock
│   │   └── status.js                 ← System stats
│   ├── lib/
│   │   └── pipeline-runner.js        ← Python script runner (10-min timeout)
│   └── public/
│       ├── index.html                ← SPA (login + dashboard)
│       ├── style.css                 ← Design system (glassmorphism, 800+ lines)
│       └── app.js                    ← Client app (drag-drop, pipeline, files)
├── raw/
│   ├── web/                          ✅ ACTIVE
│   │   └── {date}/
│   │       └── {uuid}-{sanitized_name}.{ext}
│   └── manual/                       ← Existing manual uploads
└── logs/
    ├── web-uploads.jsonl             ← Upload/delete audit log
    ├── pipeline-runs.jsonl           ← Pipeline execution log
    ├── web-portal-out.log            ← PM2 stdout
    └── web-portal-error.log          ← PM2 stderr
```

---

## 4. Metadata & Audit

### 4.1. Upload Log (`logs/web-uploads.jsonl`)

```jsonl
{"id":"c82c0b45","filename":"test.txt","stored_name":"c82c0b45-...-test.txt","path":"/home/openclaw/wiki/raw/web/2026-04-05/...","size":34,"mime":"text/plain","uploaded_at":"2026-04-05T08:07:18.135Z","source":"web","pipeline_status":"pending","action":"upload","uploader":"admin"}
{"action":"delete","id":"c82c0b45","filename":"c82c0b45-...-test.txt","deleted_at":"2026-04-05T08:10:00Z","deleter":"admin"}
```

### 4.2. Pipeline Log (`logs/pipeline-runs.jsonl`)

```jsonl
{"job_id":"uuid","action":"extract","status":"started","started_at":"2026-04-05T08:34:30Z","timestamp":"..."}
{"job_id":"uuid","action":"extract","status":"success","completed_at":"...","timestamp":"..."}
```

### 4.3. Source Registration

Tuân thủ addon.md Section 4.2 Source schema:

```yaml
source_id: web.upload.2026-04-05.{uuid}
kind: web_upload
canonical_title: "policy.pdf"
owner: admin
authority_level: 6
capture_method: web_upload
captured_at: "2026-04-05T07:38:16Z"
status: active
```

---

## 5. Security (Implemented)

| Layer | Concern | Mitigation | Status |
|-------|---------|-----------|--------|
| **Nginx** | DDoS/Brute force | 3 rate limit zones: API (10r/s), Login (5r/min), Upload (2r/s) | ✅ |
| **Nginx** | Traffic encryption | TLS 1.2+ / TLS 1.3 with AES-256-GCM | ✅ |
| **Nginx** | Clickjacking | X-Frame-Options: DENY | ✅ |
| **Nginx** | HTTPS enforcement | HSTS max-age=31536000, includeSubDomains, preload | ✅ |
| **Nginx** | Privacy | Permissions-Policy: camera=(), microphone=(), geolocation=() | ✅ |
| **Express** | CSP | Helmet Content-Security-Policy (self + fonts.googleapis + unpkg) | ✅ |
| **Express** | Auth | Bearer token required on all /api/ routes except /api/login | ✅ |
| **Express** | Password | bcrypt hash support (plain-text fallback for MVP) | ✅ |
| **Express** | Login brute force | Rate limit 10 attempts/15 minutes | ✅ |
| **Multer** | File type exploit | Whitelist extensions: .pdf .docx .xlsx .md .txt .png .jpg .jpeg | ✅ |
| **Multer** | File size DoS | 50MB per file, 10 files per request | ✅ |
| **Routes** | Path traversal | UUID rename + path validation within raw/web/ | ✅ |
| **Routes** | XSS filenames | Sanitize: only [a-zA-Z0-9_-] kept in stored names | ✅ |
| **Audit** | Accountability | JSONL log for all uploads and deletions | ✅ |
| **PM2** | Memory leak | 256MB memory limit, auto-restart | ✅ |
| **SSL** | Cert renewal | Certbot auto-renewal via systemd timer | ✅ |

---

## 6. UI Design (Implemented)

### 6.1. Theme
- **Style:** Glassmorphism dark theme
- **Background:** Deep navy (#030712 → #0a1628) with animated radial gradient overlays
- **Accent:** Teal (#22d3ee) + Emerald (#10b981) gradient
- **Fonts:** Space Grotesk (headings), DM Sans (body), JetBrains Mono (code)
- **Glass:** backdrop-filter: blur(16px), rgba borders

### 6.2. Components Implemented
1. **Login Page**: Centered card, gradient logo, password input, error animation
2. **Stats Bar**: 4 metric cards (Total files, Wiki pages, Claims, Build version)
3. **Upload Zone**: Drag & drop area, format tags, file queue with progress bars
4. **Upload Actions**: Dual buttons — "Upload & Trigger Pipeline" vs "Upload & Chờ xử lý"
5. **Pipeline Control**: Status badge (animated pulse), 3 action buttons with confirmation modal
6. **File Browser**: Tab navigation (All/Web/Manual), sortable table, pagination
7. **Toast Notifications**: Slide-in from right, auto-dismiss, 4 types (success/error/warning/info)
8. **Modal System**: Promise-based confirmation dialogs

### 6.3. Responsive
- **Desktop (≥1024px)**: 2-column grid (upload + pipeline/files)
- **Mobile (<640px)**: Single column, simplified stats, hidden columns

### 6.4. Accessibility (WCAG AA)
- Skip-to-content link
- All interactive elements have aria-labels
- Keyboard navigation (Tab, Enter/Space)
- `prefers-reduced-motion` support
- Screen reader announcements via `role="status"` + `aria-live`
- Minimum 44px touch targets

---

## 7. Deployment (Production)

### 7.1. Architecture

```
Browser → upload.trieuphu.biz:443 → Nginx (SSL + Rate Limit) → localhost:3000 → Express
```

### 7.2. Configuration

```env
# /home/openclaw/wiki/.env
WEB_PORT=3000
ADMIN_TOKEN=<random-64-char-hex>
ADMIN_PASSWORD=bkns2026portal
```

### 7.3. Commands

```bash
# Start/restart
cd /home/openclaw/wiki/web
pm2 restart wiki-portal

# View logs
pm2 logs wiki-portal --lines 50

# Nginx reload
sudo nginx -t && sudo systemctl reload nginx

# SSL renewal (auto via certbot timer)
sudo certbot renew --dry-run
```

---

## 8. Kết Nối Với Pipeline Hiện Tại

Web portal KHÔNG thay đổi pipeline hiện tại. Nó thêm 1 kênh intake mới:

```
Kênh intake:
  SSH copy    → raw/manual/     (giữ nguyên)
  Web upload  → raw/web/        (MỚI — portal này)
  Telegram    → ingest-image    (giữ nguyên)
       ↓
  Cùng pipeline:
  convert → extract → compile → build
```

Pipeline scripts (`convert_manual.py`, `extract.py`, `compile.py`) không cần sửa.

---

## 9. Checklist Triển Khai ✅

- [x] Tạo `web/` directory structure
- [x] Init Node.js project + install dependencies (8 packages)
- [x] Implement Express server + routes (6 endpoints)
- [x] Implement auth middleware (Bearer + bcrypt)
- [x] Implement file upload (multer, UUID naming, JSONL audit)
- [x] Implement file listing API (recursive scan, pagination)
- [x] Implement pipeline trigger wrapper (Python scripts, 10-min timeout)
- [x] Build frontend UI (HTML/CSS/JS, glassmorphism design)
- [x] Test upload via HTTPS ✅ (file saved to raw/web/2026-04-05/)
- [x] Test pipeline trigger ✅ (job started, extract action)
- [x] Setup PM2 production config ✅ (wiki-portal, online)
- [x] Nginx reverse proxy ✅ (SSL, rate limiting, security headers)
- [x] SSL certificate ✅ (Let's Encrypt, expires 2026-07-04, auto-renewal)
- [x] Verify audit log ✅ (web-uploads.jsonl + pipeline-runs.jsonl)
- [x] Verify security headers ✅ (HSTS, X-Frame, CSP, Permissions-Policy)
- [x] Verify TLS 1.3 ✅ (TLS_AES_256_GCM_SHA384)
- [x] Verify rate limiting ✅ (login rate limit triggered after wrong attempts)
- [x] Verify auth guard ✅ (401 without token)
- [x] Cập nhật PROJECT_SUMMARY.md
