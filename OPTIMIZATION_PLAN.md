# BKNS Wiki — Optimization Plan v1.0
**Ngày lập:** 2026-04-14  
**Mục tiêu:** Tối ưu hóa toàn bộ dự án — xóa code thừa, bổ sung code thiếu, chuẩn bị bàn giao sản phẩm hoàn chỉnh.  
**Phương pháp:** Chia 5 phase độc lập, mỗi phase ≤ 300K token, chạy tuần tự.

---

## TỔNG QUAN: VẤN ĐỀ PHÁT HIỆN

### 🔴 Loại bỏ (Dead / Redundant Code)
| Vấn đề | File | Dòng | Mức độ |
|--------|------|------|--------|
| Explicit Context Caching — 270 dòng không dùng (implicit caching đã thay thế) | `lib/gemini.py` | 419–688 | Cao |
| `_now_iso()`, `_today_str()`, `_ensure_dir()` duplicate từ `utils.py` | `lib/logger.py` | 15–27 | Trung |
| `sys.path.insert` hack trong mọi bot handler (dùng importlib thay) | `bot/wiki_bot.py` | 84,129,152,… | Trung |
| `/them` command — hiện thi trong /help nhưng **không có handler** | `bot/wiki_bot.py` | 262 | Cao |
| Unused `hashlib`, `json` import trong `gemini.py` sau xóa cache section | `lib/gemini.py` | 8–9 | Thấp |
| `CRAWL_RULES` — định nghĩa nhưng không ai enforce | `lib/config.py` | 114–122 | Thấp |

### 🟢 Bổ sung (Missing Features)
| Thiếu | Impact |
|-------|--------|
| `wiki/requirements.txt` — không có file quản lý dependency | CI/CD, onboarding |
| Handler `/them [URL]` trong Telegram bot | Tính năng ghi trong /help nhưng lỗi |
| Monthly cost report log (`logs/cost-YYYY-MM.jsonl`) | Tracking chi phí |
| Budget guard per-request (hiện chỉ có monthly) | Phòng chi phí vượt |
| Input sanitization cho bot commands | Security |
| `wiki/web/package.json` lockfile audit + `npm audit` | Security |
| Type hints cho toàn bộ `lib/` | Maintainability |

### 🟡 Cải thiện (Improvements)
| Vấn đề | File |
|--------|------|
| Bot error messages không có context (chỉ `str(e)`) | `bot/wiki_bot.py` |
| Retry trong bot khi Telegram API timeout | `bot/wiki_bot.py` |
| `PRICING` dict hardcode model name string thay vì dùng constant | `lib/gemini.py:61-62` |
| `generate_with_cache` không log model name trong detail | `lib/gemini.py:272` |
| Web server log chỉ dùng `console.error` — không có structured log | `web/server.js:172` |
| CSP `unsafe-inline` cho styles — cần nonce hoặc hash | `web/server.js:53` |

---

## PHASE 1 — FOUNDATION: Dead Code & Dependencies
**Token estimate:** ~150K  
**Files cần đọc:** `lib/gemini.py`, `lib/logger.py`, `lib/utils.py`, `lib/config.py`  
**Mục tiêu:** Xóa code thừa, tạo requirements.txt, fix duplicate utilities

### 1.1 Xóa Explicit Context Caching section khỏi `gemini.py`
**Lý do:** 270 dòng (line 419–688) implement explicit named cache nhưng không có caller nào trong toàn bộ codebase. Implicit caching (generate_with_cache) đã đủ tốt hơn và đang được dùng. Code dead này gây nhầm lẫn cho maintainer.

**Action:**
- Xóa dòng 419–688: `_CACHE_META_PATH`, `_CACHE_TTL_SECONDS`, `_CACHE_REFRESH_BUFFER`, `_load_cache_meta()`, `_save_cache_meta()`, `_wiki_hash()`, `create_wiki_cache()`, `get_or_create_wiki_cache()`, `generate_with_explicit_cache()`
- Xóa import `hashlib`, `json` (chỉ dùng bởi cache section đã xóa)
- Giữ nguyên: `generate()`, `generate_with_cache()`, `generate_with_image()`, `get_client()`, `calculate_cost()`
- Cập nhật module docstring: xóa dòng "Supports explicit context caching..."

**Verification:** `grep -r "create_wiki_cache\|get_or_create_wiki_cache\|generate_with_explicit_cache" wiki/` → không có kết quả

---

### 1.2 Fix duplicate functions trong `logger.py`
**Lý do:** `logger.py` có `_now_iso()`, `_today_str()`, `_ensure_dir()` là bản copy y hệt từ `utils.py` (minus the `ensure_dir` public version). Duplicate code là nguồn gốc bug khi fix một chỗ mà quên chỗ kia.

**Action:**
- Xóa `_now_iso()`, `_today_str()`, `_ensure_dir()` khỏi `logger.py`
- Import từ `utils.py`:
  ```python
  from lib.utils import now_iso as _now_iso, today_str as _today_str, ensure_dir as _ensure_dir
  ```
- Đổi tên alias để không thay đổi call sites trong file

**Verification:** `python3 -c "from lib.logger import log_entry; print('OK')"` từ `wiki/`

---

### 1.3 Tạo `wiki/requirements.txt`
**Lý do:** Không có file quản lý Python dependencies. Khi deploy fresh hoặc CI/CD sẽ không biết install gì.

**Action:** Tạo `wiki/requirements.txt` với pinned versions:
```
# Core AI
google-genai>=1.0.0
openai>=1.30.0

# Telegram
requests>=2.31.0

# Data
pyyaml>=6.0.1
python-dotenv>=1.0.0

# File conversion
markitdown>=0.4.0

# Utilities
openpyxl>=3.1.2
yt-dlp>=2024.1.0

# Dev
pytest>=8.0.0
```

**Verification:** `pip install -r requirements.txt --dry-run` thành công

---

### 1.4 Làm rõ `CRAWL_RULES` trong `config.py`
**Lý do:** `CRAWL_RULES` dict định nghĩa rules nhưng không có code nào enforce (dùng `crawl_bkns.py` tham chiếu trực tiếp các giá trị, không import dict này). Dict này chỉ là documentation, dễ drift.

**Action:** Thêm comment rõ ràng:
```python
# NOTE: CRAWL_RULES là reference config — các giá trị được đọc trực tiếp
# bởi tools/crawl_bkns.py và skills/crawl-source/scripts/crawl.py
# Không xóa — dùng cho documentation và future validation layer
```

Đây là minimal action — không xóa vì có giá trị documentation, không cần refactor lớn trong phase này.

---

**Deliverables Phase 1:**
- [ ] `lib/gemini.py`: giảm từ 688 → ~420 dòng (xóa 270 dòng dead code)
- [ ] `lib/logger.py`: xóa 15 dòng duplicate, import từ utils
- [ ] `wiki/requirements.txt`: tạo mới
- [ ] `lib/config.py`: thêm comment rõ CRAWL_RULES

**Log file:** `OPTIMIZATION_LOG.md` → Phase 1 section

---

## PHASE 2 — BOT QUALITY: Fixes & Missing Features
**Token estimate:** ~200K  
**Files cần đọc:** `bot/wiki_bot.py`, `lib/config.py`, `lib/telegram.py`  
**Mục tiêu:** Fix `/them` command missing, cải thiện error handling, input sanitization

### 2.1 Implement handler `/them [URL]` (CRITICAL FIX)
**Lý do:** `/help` liệt kê `/them [URL]` nhưng `process_message()` không có branch xử lý. User gõ sẽ nhận "Lệnh không nhận diện". Đây là broken feature.

**Action:** Thêm `handle_them()` function và route trong `process_message()`:
```python
def handle_them(chat_id: int, url: str):
    """Handle /them [URL] — crawl URL mới vào raw/."""
    if str(chat_id) != str(ADMIN_TELEGRAM_ID):
        send_message(chat_id, "⛔ Chỉ admin mới được sử dụng lệnh này.")
        return
    if not url:
        send_message(chat_id, "❓ Cú pháp: `/them [URL]`\nVí dụ: `/them https://bkns.vn/hosting`")
        return
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        send_message(chat_id, "❌ URL không hợp lệ. Phải bắt đầu bằng http:// hoặc https://")
        return
    send_typing(chat_id)
    send_message(chat_id, f"⏳ Đang crawl: `{url}`")
    try:
        # Call crawl-source skill
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, str(WORKSPACE / "skills/crawl-source/scripts/crawl.py"), url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            send_message(chat_id, f"✅ Crawl thành công!\n\nChạy `/extract` để xử lý file mới.")
        else:
            send_message(chat_id, f"⚠️ Crawl gặp vấn đề:\n`{result.stderr[:500]}`")
    except subprocess.TimeoutExpired:
        send_message(chat_id, "⏰ Crawl timeout (60s). Vui lòng thử lại sau.")
    except Exception as e:
        send_message(chat_id, f"❌ Lỗi crawl: {str(e)[:200]}")
        log_entry("wiki-bot", "error", f"Crawl error for {url}: {e}", severity="high")
```

Thêm vào `process_message()`:
```python
elif text.startswith("/them"):
    url = text[5:].strip()
    handle_them(chat_id, url)
```

---

### 2.2 Replace `sys.path.insert` hacks bằng subprocess
**Lý do:** Bot hiện tại dùng `sys.path.insert(0, ...)` rồi `from compile import ...` — fragile vì:
1. Side effects: modify sys.path globally trong process
2. Module name collision nếu 2 skills có file cùng tên
3. Không isolate lỗi import

**Action:** Thay tất cả `sys.path.insert` + dynamic import trong bot bằng `subprocess.run()` calls. Bot đã có pattern này trong `handle_them()` trên — áp dụng cho `handle_extract`, `handle_compile`, `handle_build`, `handle_lint`.

Pattern chuẩn:
```python
result = subprocess.run(
    [sys.executable, str(WORKSPACE / "skills/{skill}/scripts/{script}.py"), *args],
    capture_output=True, text=True, timeout=300, 
    env={**os.environ, "PYTHONPATH": str(WORKSPACE)}
)
```

Parse stdout JSON hoặc exit code.

---

### 2.3 Add input sanitization
**Lý do:** Bot nhận text từ Telegram users — cần sanitize trước khi pass vào shell commands hoặc file paths.

**Action:**
- `question` trong `handle_hoi()`: strip, limit 500 chars, không sanitize content (AI handle)
- `url` trong `handle_them()`: validate scheme, max 2000 chars
- `category` trong `handle_compile()`: validate against allowlist `CATEGORY_MAP.keys()`
- Thêm validation function `_validate_category(cat)` trả về `bool`

---

### 2.4 Cải thiện error messages trong bot
**Lý do:** `f"❌ Lỗi: {str(e)}"` expose raw Python exception ra Telegram — không user-friendly và có thể leak internal paths.

**Action:**
- Wrap với `_safe_error(e)` helper: truncate ở 200 chars, mask file paths
- Log full error vào logger với severity="high"
- Bot message chỉ show tóm tắt friendly

---

### 2.5 Thêm Telegram retry cho network errors
**Lý do:** `send_message()` có try/except nhưng không retry. Network flicker → tin nhắn mất.

**Action:** Thêm retry với backoff vào `send_message()`:
```python
for attempt in range(3):
    try:
        r = requests.post(..., timeout=10)
        if r.status_code == 200:
            break
    except requests.RequestException:
        if attempt < 2:
            time.sleep(1 * (attempt + 1))
```

---

**Deliverables Phase 2:**
- [ ] `bot/wiki_bot.py`: implement `/them` handler
- [ ] `bot/wiki_bot.py`: replace sys.path hacks với subprocess
- [ ] `bot/wiki_bot.py`: input sanitization
- [ ] `bot/wiki_bot.py`: improved error messages
- [ ] `bot/wiki_bot.py`: send_message retry

---

## PHASE 3A — WEB BACKEND: Routes Audit & Security
**Token estimate:** ~250K  
**Files cần đọc:** `web/server.js` (189L), `web/routes/wiki.js` (771L), `web/routes/review.js` (630L), `web/routes/files.js` (222L), `web/routes/upload.js` (145L), `web/routes/trigger.js` (39L), `web/routes/status.js` (91L), `web/routes/activity.js` (158L), `web/routes/builds.js` (134L), `web/middleware/auth.js`  
**Mục tiêu:** Audit toàn bộ API routes, fix security issues, thêm structured logging

### 3A.1 Audit all route files
Đọc từng file trong `web/routes/` (tổng 2379 dòng backend):
- `wiki.js` (771L) — CRUD cho wiki pages
- `review.js` (630L) — Review queue
- `files.js` (222L) — File management
- `upload.js` (145L) — Upload handler
- `activity.js` (158L) — Activity logs
- `builds.js` (134L) — Build snapshots
- `status.js` (91L) — System status
- `trigger.js` (39L) — Pipeline trigger

Cho mỗi route: kiểm tra (a) auth check, (b) input validation, (c) error handling, (d) dead routes không dùng.

### 3A.2 Fix CSP `unsafe-inline` cho styles
**Lý do:** `styleSrc: ["'self'", "'unsafe-inline'", ...]` trong `server.js:53` cho phép inline styles — weakens CSP.

**Action:** Evaluate: nếu TOAST UI Editor yêu cầu inline styles → giữ nhưng add comment giải thích. Nếu không cần → xóa.

### 3A.3 Thêm structured error logging cho web server
**Lý do:** `console.error('[SERVER] Unhandled error:', err)` không structured, không audit trail.

**Action:** Trong error handler `web/server.js:171-174`:
```javascript
const logDir = path.resolve(__dirname, '../logs');
app.use((err, req, res, _next) => {
  const today = new Date().toISOString().slice(0, 10);
  const entry = JSON.stringify({
    ts: new Date().toISOString(),
    method: req.method,
    url: req.url,
    error: err.message,
    stack: err.stack?.split('\n')[0],
  });
  try { require('fs').appendFileSync(`${logDir}/web-errors-${today}.jsonl`, entry + '\n'); }
  catch (_) {}
  res.status(500).json({ error: 'Internal server error' });
});
```

### 3A.4 Kiểm tra npm dependencies
```bash
cd wiki/web && npm audit --audit-level=high
```
Fix các vulnerability level high/critical.

---

**Deliverables Phase 3A:**
- [ ] Route audit report: mỗi route có status + issues list
- [ ] `web/server.js`: structured error logging (JSONL)
- [ ] `web/server.js`: CSP evaluation/fix với comment
- [ ] npm audit sạch (0 high/critical)
- [ ] Xóa dead routes không có caller

---

## PHASE 3B — WEB FRONTEND: UI Audit & Cleanup
**Token estimate:** ~200K  
**Files cần đọc:** `web/public/index.html` (786L), `web/public/app.js` (1778L), `web/public/style.css` (1166L)  
**Mục tiêu:** Tìm và xóa nút thừa/chức năng không cần, fix hard-coded values, validate UX

### 3B.1 Audit `app.js` — JavaScript logic
Đọc toàn bộ 1778 dòng `app.js`, tìm:
- Functions không được gọi (dead code)
- Event listeners trên nút bấm không có trong HTML
- Hard-coded URLs, API endpoints, config values
- Console.log statements nên xóa trong production
- Chức năng UI không còn dùng

### 3B.2 Audit `index.html` — UI structure
Đọc 786 dòng, tìm:
- Nút bấm không có handler trong app.js
- Form fields không được submit
- Hidden sections không bao giờ show
- Duplicate UI components

### 3B.3 Kiểm tra responsive và accessibility
- Verify mobile breakpoints trong `style.css`
- Kiểm tra contrast ratios theo WCAG AA (4.5:1 minimum)
- Focus indicators cho keyboard navigation
- ARIA labels trên interactive elements

### 3B.4 Xóa dead UI elements
Sau audit, xóa:
- Nút bấm thừa (không có handler)
- CSS classes không dùng
- Dead JavaScript functions

---

**Deliverables Phase 3B:**
- [ ] `web/public/app.js`: xóa dead functions, console.logs
- [ ] `web/public/index.html`: xóa nút/sections thừa
- [ ] `web/public/style.css`: xóa unused CSS classes
- [ ] Accessibility checklist: contrast, ARIA, keyboard nav

---

## PHASE 4 — TESTING & COST MONITORING
**Token estimate:** ~200K  
**Files cần đọc:** `tests/`, `tools/check_cost_budget.py`, `lib/gemini.py`, `lib/logger.py`  
**Mục tiêu:** Test coverage, monthly cost log, per-request budget guard

### 4.1 Thêm monthly cost summary log
**Lý do:** OpenAI calls được log vào `logs/openai-calls-YYYY-MM.jsonl`. Gemini calls chỉ log vào `logs/{skill}-{date}.jsonl` nhưng không có file tổng hợp theo tháng. Không thể track chi phí Gemini month-over-month.

**Action:** Trong `lib/logger.py`, thêm `log_gemini_call()` ghi vào `logs/gemini-calls-YYYY-MM.jsonl`:
```python
def log_gemini_call(
    skill: str,
    model: str,
    input_tokens: int,
    cached_tokens: int,
    output_tokens: int,
    cost_usd: float,
    elapsed_ms: int,
    action: str = "llm_call",
) -> None:
    """Log Gemini API call to monthly JSONL file."""
    entry = {
        "ts": _now_iso(),
        "skill": skill,
        "action": action,
        "model": model,
        "input_tokens": input_tokens,
        "cached_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
        "elapsed_ms": elapsed_ms,
    }
    month_str = datetime.now(VN_TZ).strftime("%Y-%m")
    log_file = LOGS_DIR / f"gemini-calls-{month_str}.jsonl"
    ...
```

Call `log_gemini_call()` từ `gemini.py` trong mỗi successful generate (bổ sung vào `log_entry()` hiện tại, không thay thế).

---

### 4.2 Per-request budget guard
**Lý do:** `MAX_QUERY_COST_USD = 0.01` định nghĩa trong config nhưng `gemini.py:generate()` không kiểm tra sau khi tính cost. Một query expensive không bị alert ngay lập tức.

**Action:** Trong `gemini.py:generate()`, sau khi tính cost:
```python
if cost > MAX_QUERY_COST_USD:
    log_entry(
        skill=skill,
        action="cost_alert",
        detail=f"High-cost query: ${cost:.5f} > threshold ${MAX_QUERY_COST_USD}",
        cost_usd=cost,
        severity="high",
    )
```

Không reject query — chỉ alert. User cần visibility, không cần hard block.

---

### 4.3 Tạo integration test cho pipeline cơ bản
**Lý do:** 4 test files hiện tại chỉ test utils. Không có test nào verify pipeline end-to-end: `extract → approve → compile → query`.

**Action:** Tạo `wiki/tests/test_pipeline_smoke.py`:
```python
"""Smoke test: full pipeline extract → compile → query (mock LLM calls)."""
import pytest
from unittest.mock import patch, MagicMock

def test_extract_claims_returns_list():
    """extract_all_pending trả list, không crash."""
    ...

def test_compile_category_returns_success():
    """compile_category('hosting') với mock data."""
    ...

def test_query_returns_answer():
    """query() với mock LLM trả dict có key 'answer'."""
    ...
```

Dùng `unittest.mock.patch` để mock LLM calls — không gọi API thật trong test.

---

### 4.4 Test `/them` handler mới
**Action:** Thêm test case trong `tests/test_bot.py` (tạo mới nếu chưa có):
```python
def test_handle_them_invalid_url():
    """URL không hợp lệ bị reject."""
    ...

def test_handle_them_valid_url():
    """URL hợp lệ được chấp nhận (mock subprocess)."""
    ...
```

---

### 4.5 Kiểm tra và fix 2 skills chưa được test
Skills cần smoke test:
- `skills/ingest-image/scripts/ingest.py` — Vision extraction
- `skills/auto-file/scripts/auto_file.py` — FAQ detection

**Action:** Đọc từng file, chạy với `--dry-run` nếu có, hoặc viết unit test mock.

---

**Deliverables Phase 4:**
- [ ] `lib/logger.py`: `log_gemini_call()` function
- [ ] `lib/gemini.py`: call `log_gemini_call()` sau mỗi successful generate
- [ ] `lib/gemini.py`: per-request cost alert
- [ ] `tests/test_pipeline_smoke.py`: 3+ smoke tests
- [ ] `tests/test_bot.py`: `/them` handler tests
- [ ] Smoke test cho `ingest-image` và `auto-file`

---

## PHASE 5 — FINAL POLISH: Type Hints, Docs & Handover
**Token estimate:** ~150K  
**Files cần đọc:** tất cả `lib/*.py` cho type hints, `README.md`, `PROJECT_SUMMARY.md`  
**Mục tiêu:** Type hints, cập nhật docs, tạo HANDOVER.md

### 5.1 Thêm type hints cho `lib/` files
**Lý do:** Code hiện tại thiếu return type annotations và parameter types ở một số functions. Type hints giúp IDE catch bugs sớm và cải thiện code readability.

Files cần thêm type hints:
- `lib/gemini.py`: `generate()`, `generate_with_cache()`, `generate_with_image()`, `calculate_cost()`, `get_client()`
- `lib/logger.py`: `log_entry()`, `log_query()`, `log_intake()`, `log_approval()`
- `lib/config.py`: `get_pro_model()` (đã có, verify)
- `lib/utils.py`: đã có type hints ở nhiều chỗ — verify coverage

**Action:** Thêm type hints theo Python 3.10+ style (union types với `|`).

---

### 5.2 Fix PRICING dict dùng string literals thay vì constants
**Lý do:** `gemini.py:61-62` hardcode `"gemini-2.5-pro"`, `"gemini-3.1-pro-preview"` thay vì dùng `MODEL_PRO`, `MODEL_PRO_NEW` constants. Nếu rename model trong `.env`, PRICING dict sẽ không match.

**Action:**
```python
PRICING = {
    MODEL_FLASH: {"input": 0.30, "input_cached": 0.030, "output": 2.50},
    MODEL_PRO: {"input": 1.25, "input_cached": 0.125, "output": 10.00},
    MODEL_PRO_NEW: {"input": 2.00, "input_cached": 0.20, "output": 12.00},
}
```

Note: Đây là thay đổi behavior — `calculate_cost()` sẽ dùng model constant từ config thay vì hardcoded string. Safer khi model name thay đổi.

---

### 5.3 Cập nhật `README.md` và `PROJECT_SUMMARY.md`
**Action:**
- Cập nhật feature list (thêm `/them` command, cost monitoring)
- Cập nhật skill matrix (mark untested skills đúng trạng thái)
- Thêm Quick Start section với requirements.txt

---

### 5.4 Tạo `HANDOVER.md` — Tài liệu bàn giao
**Action:** Tạo file `wiki/HANDOVER.md` với:
- System Architecture overview
- Environment setup (step-by-step)
- Deployment guide (PM2 commands)
- Daily operations playbook
- Troubleshooting guide
- Known limitations
- Backlog / Future improvements

---

### 5.5 Tạo `CHANGELOG.md` update
Ghi lại tất cả thay đổi từ 5 phases thành CHANGELOG entry:
```
## v1.1.0 - Optimization Release (2026-04-14)
### Removed
- gemini.py: Explicit Context Caching (270 lines dead code)
- logger.py: Duplicate utility functions

### Added
- Bot: /them [URL] command implementation
- Cost monitoring: per-request budget alert
- Gemini monthly cost log (logs/gemini-calls-YYYY-MM.jsonl)
- requirements.txt for dependency management

### Fixed
- Bot: sys.path hack replaced with subprocess
- Bot: input sanitization for URL/category
- gemini.py: PRICING uses config constants

### Improved
- Bot: retry for Telegram network errors
- Bot: better error messages
- Web: structured error logging
- lib/: type hints coverage
```

---

**Deliverables Phase 5:**
- [ ] `lib/gemini.py`: type hints + PRICING fix
- [ ] `lib/logger.py`: type hints
- [ ] `README.md`: updated
- [ ] `PROJECT_SUMMARY.md`: updated
- [ ] `HANDOVER.md`: created
- [ ] `CHANGELOG.md`: v1.1.0 entry

---

## LIÊN KẾT GIỮA CÁC PHASE

```
PHASE 1 (Foundation)
    ├─ Xóa dead code trong gemini.py
    ├─ Fix duplicate utils trong logger.py   ←─ Phase 4 dùng log_gemini_call()
    └─ Tạo requirements.txt                  ←─ Phase 4 cần khi run tests

PHASE 2 (Bot Quality)
    ├─ Implement /them handler               ←─ Phase 4 viết test cho này
    ├─ Fix sys.path → subprocess             ←─ Phase 4 verify với smoke tests
    └─ Input sanitization

PHASE 3A (Web Backend)
    ├─ Route audit                           ←─ Độc lập, không phụ thuộc Phase khác
    ├─ Security fixes
    └─ Structured error logging

PHASE 3B (Web Frontend)
    ├─ UI audit                              ←─ Cần Phase 3A xong để biết route nào còn dùng
    ├─ Dead code cleanup
    └─ Accessibility fixes

PHASE 4 (Testing & Monitoring)
    ├─ log_gemini_call()                     ←─ Cần Phase 1 (logger.py fix) xong trước
    ├─ Per-request cost alert                ←─ Cần Phase 1 (gemini.py clean) xong trước
    └─ Integration tests                     ←─ Cần Phase 2 (bot fixes) xong trước

PHASE 5 (Final Polish)
    └─ Type hints, HANDOVER, CHANGELOG       ←─ Chạy sau khi tất cả phase khác done
```

**Thứ tự bắt buộc:**
1. Phase 1 → Phase 4 (logger.py phải sạch trước khi thêm log_gemini_call)
2. Phase 2 → Phase 4 (bot phải có /them trước khi viết test cho nó)
3. Phase 3A → Phase 3B (biết route nào dùng trước rồi mới audit frontend)
4. Phase 3A/3B có thể chạy song song với Phase 1/2
5. Phase 5 chỉ chạy sau khi 1, 2, 3A, 3B, 4 xong

---

## TOKEN BUDGET PER PHASE

| Phase | Files đọc | Files sửa | Estimate Token |
|-------|-----------|-----------|----------------|
| Phase 1 | 4 lib files (~1,200L) | 3 files + 1 tạo mới | ~150K |
| Phase 2 | 3 files (~700L) | 1 file lớn (380L) | ~200K |
| Phase 3A | 9 route files (~2,379L) | 2-3 files | ~250K |
| Phase 3B | 3 frontend files (~3,730L) | 3 files | ~200K |
| Phase 4 | 3 lib files + 2 skill files | 3 files + 2 tạo mới | ~200K |
| Phase 5 | lib/ + 3 doc files | lib/ + 2 docs + 2 tạo mới | ~150K |
| **Total** | | | **~1.15M token** |

> **Note:** Phase 3B (frontend 3730L) là phase nặng nhất về reading. Nếu cần giảm token, có thể split tiếp thành 3B-1 (app.js) và 3B-2 (index.html + style.css).

---

## VERIFICATION CHECKLIST — Final Version

Sau khi hoàn thành tất cả phases, verify:

```bash
# Python syntax check
python3 -m py_compile wiki/lib/*.py

# Import test
cd wiki && python3 -c "from lib.gemini import generate; from lib.logger import log_entry; print('OK')"

# Unit tests
cd wiki && python3 -m pytest tests/ -v

# Bot syntax
python3 -c "import ast; ast.parse(open('wiki/bot/wiki_bot.py').read()); print('OK')"

# Web server
cd wiki/web && node -c server.js && npm audit --audit-level=high

# Dependency install
pip install -r wiki/requirements.txt --dry-run
```

---

## FILE LOG — Mọi thay đổi

Ghi vào `OPTIMIZATION_LOG.md` sau khi hoàn thành mỗi phase:

```markdown
## Phase N — YYYY-MM-DD
### Changed
- file.py: mô tả thay đổi (dòng X-Y)
### Removed
- file.py: mô tả xóa
### Added
- file.py: mô tả thêm
### Verified
- [x] Test pass
- [x] Import OK
```

---

*BKNS Wiki Optimization Plan v1.0 — Lập bởi Claude Code (APEX v12.0) — 2026-04-14*
