# 03 — Skills & Prompts: Chi Tiết Triển Khai

> **Mục đích:** Định nghĩa cụ thể từng skill cần build, prompt mẫu, và thứ tự ưu tiên.

---

## Thứ Tự Ưu Tiên Skills

| # | Skill | Phase | Độ ưu tiên | Lý do |
|---|-------|-------|-----------|-------|
| 1 | `query-wiki` | 0.5 | 🔴 Critical | Core function — bot trả lời câu hỏi |
| 2 | `ingest-raw` | 1 | 🔴 Critical | Bot nhận dữ liệu mới |
| 3 | `compile-wiki` | 1 | 🔴 Critical | Biến raw thành wiki |
| 4 | `syntax-check` | 1 | 🟡 Medium | QA tự động, không cần LLM |
| 5 | `ingest-image` | 2 | 🟠 High | Extract bảng giá từ ảnh |
| 6 | `lint-wiki` | 2 | 🟠 High | Phát hiện mâu thuẫn, outdated |
| 7 | `cross-link` | 2 | 🟡 Medium | Liên kết chéo tự động |
| 8 | `auto-file` | 3 | 🟡 Medium | Filing câu trả lời hay |
| 9 | `ground-truth-check` | 3 | 🟡 Medium | Cross-check giá thực tế |

---

## Skill 1: `query-wiki` (Phase 0.5)

### Mô tả
Nhận câu hỏi từ Telegram, gửi wiki + câu hỏi đến Gemini Flash, trả lời.

### Trigger
- Telegram: `/hoi [câu hỏi]` hoặc tin nhắn trực tiếp

### Input/Output
- **Input:** Câu hỏi tiếng Việt
- **Output:** Câu trả lời + nguồn trích dẫn

### System Prompt Chuẩn

```
Bạn là trợ lý tư vấn chính thức của BKNS - nhà cung cấp hosting, tên miền, VPS hàng đầu Việt Nam.

QUY TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên tài liệu wiki được cung cấp bên dưới
2. Luôn ghi rõ nguồn: "Theo [tên file/section]..."
3. Nếu không có thông tin → nói RÕ RÀNG:
   "Tôi không có thông tin về vấn đề này trong cơ sở dữ liệu.
    Vui lòng liên hệ hỗ trợ BKNS 24/7:
    • Hotline: [SỐ HOTLINE]
    • Live chat: https://bkns.vn"
4. TUYỆT ĐỐI KHÔNG bịa thông tin về giá, tính năng, chính sách
5. Nếu thông tin có thể đã lỗi thời → cảnh báo:
   "Thông tin này cập nhật ngày [ngày]. Vui lòng kiểm tra lại giá mới nhất tại bkns.vn"
6. Gợi ý sản phẩm phù hợp với nhu cầu khách
7. Trả lời bằng tiếng Việt, thân thiện, chuyên nghiệp
8. Trả lời ngắn gọn (dưới 300 từ) trừ khi khách yêu cầu chi tiết
```

### Code Mẫu (Python)

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
import os

vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

# Load wiki một lần, giữ trong memory
def load_wiki(wiki_dir: str) -> str:
    texts = []
    for root, dirs, files in os.walk(wiki_dir):
        dirs.sort()
        for fname in sorted(files):
            if fname.endswith(".md"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    rel_path = os.path.relpath(fpath, wiki_dir)
                    texts.append(f"\n\n---\n# FILE: {rel_path}\n\n{f.read()}")
    return "\n".join(texts)

WIKI_CONTENT = load_wiki("/home/openclaw/wiki/wiki/")

SYSTEM_PROMPT = """[System prompt từ trên]"""

model = GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT,
)

def query_wiki(question: str) -> str:
    response = model.generate_content(
        contents=[
            Content(role="user", parts=[
                Part.from_text(f"Tài liệu wiki BKNS:\n\n{WIKI_CONTENT}"),
            ]),
            Content(role="model", parts=[
                Part.from_text("Đã đọc tài liệu wiki. Sẵn sàng trả lời câu hỏi.")
            ]),
            Content(role="user", parts=[
                Part.from_text(question)
            ]),
        ]
    )
    
    # Log cache metrics
    usage = response.usage_metadata
    cached = getattr(usage, 'cached_content_token_count', 0)
    total = usage.prompt_token_count
    hit_rate = (cached / total * 100) if total > 0 else 0
    print(f"[Cache] {cached}/{total} tokens cached ({hit_rate:.1f}%)")
    print(f"[Cost] ~${(total - cached) * 0.30/1e6 + cached * 0.03/1e6 + usage.candidates_token_count * 2.50/1e6:.4f}")
    
    return response.text
```

### Lưu Ý Quan Trọng

- `WIKI_CONTENT` phải load **một lần duy nhất** và tái sử dụng → implicit cache hoạt động
- Khi wiki thay đổi → reload `WIKI_CONTENT` → cache tự invalidate (prefix khác)
- Token thứ tự: wiki trước, câu hỏi sau → đảm bảo prefix giống nhau

---

## Skill 2: `ingest-raw` (Phase 1)

### Mô tả
Nhận URL hoặc text từ Telegram, crawl/lưu vào raw/, gán metadata.

### Trigger
- Telegram: `/them [URL]`

### Hành vi

```
1. Nhận URL từ admin Telegram
2. Crawl webpage → extract text content
3. Lưu vào raw/website-crawl/[tên-page]-[YYYY-MM-DD].md
4. Tạo metadata header:
   ---
   source_url: [URL]
   crawled_at: [timestamp]
   content_type: webpage
   suggested_category: [auto-classify]
   status: pending_compile
   ---
5. Báo admin: "✅ Đã lưu. Gõ /compile để biên dịch vào wiki."
```

### Dependencies
- `requests` hoặc `playwright` cho web crawling
- `html2text` hoặc tương tự cho HTML → Markdown

---

## Skill 3: `compile-wiki` (Phase 1)

### Mô tả
Lấy file từ raw/ (pending_compile), dùng Gemini compile thành wiki draft.

### Trigger
- Telegram: `/compile`
- Auto trigger khi raw/ có file mới

### Compile Prompt

```
Bạn là thủ thư biên tập wiki BKNS. Nhiệm vụ: biên dịch tài liệu thô thành wiki Markdown chuẩn.

INPUT:
- Tài liệu thô: {raw_content}
- Loại: {doc_type}
- Ngày nhận: {date}
- Nguồn: {source_url}

QUY TẮC BIÊN DỊCH (COMPILE RULES):
1. ❌ KHÔNG tạo fact mới nếu fact đó KHÔNG CÓ trong tài liệu thô
2. ❌ KHÔNG bịa giá, thông số kỹ thuật, chính sách
3. ❌ KHÔNG biến marketing/sales language thành policy
4. ✅ Giữ nguyên mọi số liệu cụ thể: giá, RAM, CPU, SSD, bandwidth
5. ✅ Chuẩn hóa đơn vị: tiền → "đ/tháng" hoặc "đ/năm", dung lượng → GB/TB
6. ✅ Nếu thiếu thông tin → đánh dấu: > ⚠️ **Cần bổ sung:** [thông tin gì]
7. ✅ Nếu có suy luận → đánh dấu: > 💡 **Phân tích:** [nội dung]

OUTPUT FORMAT:
```yaml
---
title: [Tên chính xác]
category: [hosting|vps|ten-mien|email|ssl|company|support|sales]
updated: {date}
source: {source_url}
confidence: [high|medium|low]
---
```

## Mô tả
[Sản phẩm/dịch vụ là gì, dùng cho ai — 2-3 câu]

## Tính năng nổi bật
- ...

## Bảng giá
| Gói | Giá | Thông số |
|-----|-----|----------|

## Câu hỏi thường gặp
Q: ...
A: ...

## Xem thêm
- [[related-file]] — Mô tả ngắn
```

### Post-compile
- Lưu output vào `wiki/.drafts/[category]/[filename].md`
- Báo admin qua Telegram với preview ngắn
- Chờ `/duyet [filename]` để publish

---

## Skill 4: `syntax-check` (Phase 1)

### Mô tả
Script Python kiểm tra cú pháp wiki — KHÔNG cần LLM, chi phí = 0.

### Kiểm tra

```python
import os, yaml, re

def syntax_check(wiki_dir):
    issues = []
    
    for root, _, files in os.walk(wiki_dir):
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(root, f)
            content = open(path, 'r').read()
            
            # 1. Frontmatter check
            if not content.startswith('---'):
                issues.append(f"[{path}] Missing frontmatter")
            else:
                try:
                    fm = content.split('---')[1]
                    meta = yaml.safe_load(fm)
                    for field in ['title', 'category', 'updated', 'source']:
                        if field not in meta:
                            issues.append(f"[{path}] Missing '{field}' in frontmatter")
                except:
                    issues.append(f"[{path}] Invalid YAML frontmatter")
            
            # 2. Image reference check
            for match in re.finditer(r'!\[.*?\]\((.*?)\)', content):
                img_path = match.group(1)
                if img_path.startswith('http'):
                    continue
                abs_img = os.path.normpath(os.path.join(os.path.dirname(path), img_path))
                if not os.path.exists(abs_img):
                    issues.append(f"[{path}] Broken image: {img_path}")
            
            # 3. Empty file check
            body = content.split('---', 2)[-1].strip() if '---' in content else content.strip()
            if len(body) < 50:
                issues.append(f"[{path}] File too short ({len(body)} chars)")
    
    return issues
```

### Schedule
- Cron: 06:00 hàng ngày
- Chỉ báo khi có lỗi

---

## Skill 5: `ingest-image` (Phase 2)

### Mô tả
Nhận ảnh bảng giá từ Telegram → Vision extract → create claim draft.

### Vision Extract Prompt

```
Hãy extract toàn bộ bảng giá trong ảnh này thành định dạng Markdown table.

YÊU CẦU:
1. Giữ nguyên đơn vị tiền tệ (đ, VND, nghìn đồng → chuẩn hóa thành "đ")
2. Giữ nguyên tên gói, mã gói, thông số kỹ thuật
3. Nếu có nhiều bảng, tạo nhiều section riêng biệt với heading
4. Sau mỗi bảng, thêm dòng:
   "Nguồn: [tên ảnh], extract ngày [ngày hôm nay]"
5. Nếu có cột/ô không đọc được do ảnh mờ, ghi: **[KHÔNG RÕ]**
6. KHÔNG suy luận giá trị bị che/mờ — chỉ ghi những gì đọc được

OUTPUT: Chỉ nội dung Markdown, không giải thích thêm.
```

### Workflow

```
[Ảnh từ Telegram]
    → lưu assets/evidence/price-screens/[name]-original.[ext] (Git LFS)
    → Gemini Flash Vision extract → Markdown table
    → nén thumbnail → assets/images/[name].[ext]
    → tạo wiki/.drafts/products/[category]/bang-gia-update.md
    → bot hỏi: "Đây là bảng giá [?]. Ghi vào file nào?"
    → admin confirm → /duyet → merge vào wiki
```

---

## Skill 6: `lint-wiki` (Phase 2)

### Trigger
- Cron: 09:00 Thứ Hai hàng tuần
- Manual: `/lint`

### Lint Prompt

```
Bạn là kiểm toán viên chất lượng wiki BKNS. Đọc toàn bộ wiki và kiểm tra:

## 1. MÂU THUẪN GIÁ [🔴 Critical]
- Tìm TẤT CẢ giá tiền được đề cập trong wiki
- Kiểm tra: cùng gói/sản phẩm có giá khác nhau ở file khác nhau?
- Output: bảng [File A, Giá A] vs [File B, Giá B]

## 2. THÔNG TIN LỖI THỜI [🟡 Warning]
- File có `updated:` cũ hơn 30 ngày → cần verify
- Ngày tháng cụ thể đã qua hạn

## 3. THIẾU NGUỒN [🟠 Medium]
- Bảng giá không có `source:` URL
- Claim quan trọng không có citation

## 4. ORPHAN FILES [🔵 Info]
- File không được link từ index.md hoặc file nào khác

## 5. ĐỀ XUẤT CẢI THIỆN [💡 Top 5]

FORMAT OUTPUT:
# Báo Cáo Lint {ngày}
## 🔴 Mâu thuẫn giá (cần sửa ngay)
[liệt kê hoặc "✅ Không có vấn đề"]
## 🟡 Thông tin cần verify
## 🟠 Thiếu nguồn trích dẫn
## 🔵 Orphan files
## 💡 Đề xuất cải thiện (top 5)
```

---

## OpenClaw Skill Registration Format

Mỗi skill cần SKILL.md + script:

```
skills/
├── query-wiki/
│   ├── SKILL.md             ← Mô tả, trigger, inputs
│   └── scripts/
│       └── query.py          ← Logic chính
├── ingest-raw/
│   ├── SKILL.md
│   └── scripts/
│       └── ingest.py
├── compile-wiki/
│   ├── SKILL.md
│   └── scripts/
│       └── compile.py
└── ...
```

### SKILL.md mẫu cho query-wiki

```yaml
---
name: query-wiki
description: Trả lời câu hỏi về sản phẩm/dịch vụ BKNS dựa trên wiki knowledge base. Trigger khi người dùng hỏi về hosting, tên miền, VPS, email, SSL, giá cả, hỗ trợ BKNS.
triggers:
  - command: /hoi
  - pattern: ".*bkns.*|.*hosting.*|.*tên miền.*|.*vps.*|.*giá.*"
---

# query-wiki

## Mô tả
Query wiki BKNS để trả lời câu hỏi. Sử dụng Gemini 2.5 Flash với implicit caching.

## Bước thực hiện
1. Load wiki content (nếu chưa có trong memory)
2. Gửi wiki prefix + câu hỏi đến Gemini Flash
3. Format câu trả lời + ghi nguồn
4. Log token usage, cache hit rate
5. Trả lại câu trả lời qua Telegram
```

---

*Xem pricing chi tiết tại: [04-pricing-va-budget.md](./04-pricing-va-budget.md)*
