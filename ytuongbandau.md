# Đề Tài Nghiên Cứu: BKNS Knowledge Wiki
## LLM-Compiled · Full-Context · Implicit-Context-Cached · Không RAG

> **Tác giả ý tưởng gốc:** Người dùng (cộng tác với OpenClaw)
> **Ngày khởi tạo:** 2026-04-04
> **Cập nhật lần 2:** 2026-04-04 — Bổ sung: quản lý ảnh, context caching, kiến trúc multi-agent
> **Cập nhật lần 3:** 2026-04-04 — **Sửa lỗi nghiêm trọng:** model strings, pricing Gemini 2.5, caching strategy, gitattributes, budget
> **Trạng thái:** Nghiên cứu hoàn chỉnh — Sẵn sàng phê duyệt để triển khai Phase 1
> **Vị trí repo:** `/home/openclaw/wiki/`

---

## ⚠️ Nhật Ký Sửa Lỗi (v3 — 2026-04-04)

| # | Lỗi | Tình trạng |
|---|-----|-----------|
| 1 | Mâu thuẫn model: toàn bộ code và bảng dùng `gemini-1.5-*`, quyết định dùng 2.5 | ✅ Đã sửa toàn bộ |
| 2 | Context window sai: ghi 2M token cho Gemini 2.5 Pro (thực tế 1M) | ✅ Đã sửa |
| 3 | Dùng **explicit caching** (tốn storage cost, phức tạp) trong khi **implicit caching** đơn giản hơn và miễn phí storage | ✅ Đã chuyển sang implicit caching làm chiến lược chính |
| 4 | Lệnh `git lfs track` sai — `.gitattributes` không có tác dụng | ✅ Đã sửa |
| 5 | Bảng giá token dùng số của Gemini 1.5, tính toán budget sai lệch | ✅ Đã tính lại với giá Gemini 2.5 |
| 6 | Budget "$9/tháng → 2.7 năm" bỏ sót output token cost khi compile | ✅ Đã tính lại trung thực |
| 7 | Dùng song song "Wave" và "Phase" gây nhầm lẫn | ✅ Đã thống nhất dùng "Phase" |
| 8 | Section 4.2 label `wiki/assets/` nhưng thực tế `assets/` ở root | ✅ Đã sửa path |

---

## Mục Lục

1. [Tổng Quan Ý Tưởng](#1-tổng-quan-ý-tưởng)
2. [Nền Tảng Lý Thuyết: LLM Knowledge Base](#2-nền-tảng-lý-thuyết-llm-knowledge-base-karpathy)
3. [Hệ Sinh Thái Sản Phẩm BKNS](#3-hệ-sinh-thái-sản-phẩm-bkns-nghiên-cứu-thực-địa)
4. [Quản Lý Ảnh — Bằng Chứng & Tài Liệu Trực Quan](#4-quản-lý-ảnh--bằng-chứng--tài-liệu-trực-quan)
5. [Context Caching — Tiết Kiệm Token Tối Đa](#5-context-caching--tiết-kiệm-token-tối-đa)
6. [Kiến Trúc Multi-Agent: Gemini Pro + Flash](#6-kiến-trúc-multi-agent-gemini-pro--flash)
7. [Cấu Trúc Wiki & Phạm Vi Kiến Thức](#7-cấu-trúc-wiki--phạm-vi-kiến-thức)
8. [Thiết Kế Kỹ Thuật Tổng Thể](#8-thiết-kế-kỹ-thuật-tổng-thể)
9. [Đảm Bảo Chất Lượng Kiến Thức](#9-đảm-bảo-chất-lượng-kiến-thức)
10. [Lộ Trình Triển Khai](#10-lộ-trình-triển-khai)
11. [Phân Tích Khả Thi & Ngân Sách](#11-phân-tích-khả-thi--ngân-sách)
12. [Câu Hỏi Đã Trả Lời](#12-câu-hỏi-đã-trả-lời)

---

## 1. Tổng Quan Ý Tưởng

### 1.1. Vấn đề cần giải quyết

BKNS (Công ty Cổ phần Giải pháp Mạng Bạch Kim) là nhà cung cấp dịch vụ hạ tầng mạng tại Việt Nam, thành lập 2010. Với hệ sinh thái sản phẩm rộng, nhân viên và bot CSKH đang gặp:

- Kiến thức sản phẩm phân tán, không có "single source of truth"
- Nhân viên mới mất nhiều thời gian học từ nhiều nguồn rời rạc
- Bot CSKH thiếu tài liệu cấu trúc → câu trả lời kém chính xác, dễ hallucinate
- **Bằng chứng bảng giá** (screenshot) bị lưu rải rác, không có hệ thống tra cứu

### 1.2. Mục tiêu

| # | Mục tiêu | Đối tượng |
|---|----------|-----------|
| 1 | Nguồn kiến thức nền tảng đầy đủ về BKNS | Nhân viên mới, nhân viên tư vấn |
| 2 | Tài liệu train bot — load vào context LLM khi cần | Bot CSKH trên Telegram, bot hỗ trợ nội bộ |
| 3 | Knowledge base sống — tự cập nhật, có liên kết | OpenClaw quản trị |
| 4 | Quản lý ảnh chuẩn — bảng giá, note quan trọng có bằng chứng ảnh gốc | Mọi người dùng |

### 1.3. Triết lý cốt lõi

> Dựa trên ý tưởng **Andrej Karpathy**: LLM là "trình biên dịch tri thức" — nhận dữ liệu thô → compile thành wiki Markdown → nhét toàn bộ vào context LLM khi trả lời. **Không RAG, không vector DB.** Đơn giản, minh bạch, dễ audit.

**Điểm khác biệt so với ý tưởng gốc Karpathy:**
- Thêm **quản lý ảnh** (bảng giá screenshot → extract → Markdown + lưu ảnh gốc làm evidence)
- Thêm **Gemini Implicit Context Caching** — wiki được gửi như prefix cố định mỗi query, Gemini tự động cache và giảm 75% chi phí token
- Thêm **kiến trúc multi-agent** (Gemini Pro orchestrator + Gemini Flash worker) cho các tác vụ thủ thư tự động

---

## 2. Nền Tảng Lý Thuyết: LLM Knowledge Base (Karpathy)

### 2.1. Pipeline 6 giai đoạn

```
Raw Data → Ingest → Compile (LLM) → View → Query (Q&A) → Filing → Linting
```

| Giai đoạn | Mô tả áp dụng cho BKNS |
|-----------|------------------------|
| **Raw** | Trang web BKNS, bảng giá PDF, screenshot, note nội bộ, kịch bản tư vấn |
| **Ingest** | OpenClaw nhận file/URL, lưu vào `raw/`, gán metadata |
| **Compile** | Gemini Pro biên dịch sang `wiki/`: tóm tắt, tạo bảng, backlink |
| **View** | Xem qua Obsidian, VS Code, hoặc cổng nội bộ |
| **Query** | Bot Telegram nhận câu hỏi → gửi wiki + câu hỏi → Gemini Flash trả lời (implicit cache) |
| **Filing** | Câu trả lời hay được file vào `faq/` tự động |
| **Linting** | Job tuần/tháng phát hiện giá lỗi thời, mâu thuẫn, chỗ thiếu |

### 2.2. Tại sao không cần RAG

- BKNS wiki ước tính: **50–150 file Markdown ≈ 200k–500k token** sau biên dịch
- **Gemini 2.5 Pro: 1M token context | Gemini 2.5 Flash: 1M token context** — đủ để full-context
- Full-context tốt hơn RAG: nhìn thấy toàn cảnh, không mất thông tin do chunking, suy luận đa bước tốt hơn
- **Khi nào nên thêm RAG:** wiki vượt 1M token hoặc cần phục vụ >50 concurrent users

---

## 3. Hệ Sinh Thái Sản Phẩm BKNS (Nghiên Cứu Thực Địa)

### 3.1. Hồ sơ công ty

| Thông tin | Chi tiết |
|-----------|---------|
| **Tên đầy đủ** | Công ty Cổ phần Giải pháp Mạng Bạch Kim |
| **Tên thương mại** | BKNS / BKNS.vn |
| **Thành lập** | 2010 |
| **Trụ sở** | Tầng 5, 169 Nguyễn Ngọc Vũ, Yên Hòa, Cầu Giấy, Hà Nội |
| **Chi nhánh HCM** | 319 Lý Thường Kiệt, Quận 11 |
| **Nhà đăng ký .vn** | Chính thức — được VNNIC chứng nhận |
| **Hạ tầng mạng** | AS135967 — sở hữu AS riêng, IPv4 đặt tại Việt Nam |
| **Chứng nhận** | An toàn hệ thống thông tin cấp độ 3 |
| **Hotline** | 📋 *Cần bổ sung số hotline chính thức vào đây* |
| **Live chat** | https://bkns.vn |

### 3.2. Danh mục sản phẩm & dịch vụ

#### A. Tên miền
- Là **nhà đăng ký .vn chính thức** — lợi thế cạnh tranh lớn
- Bảng giá: `.com` ~540k/năm | `.vn` ~450k/năm | `.com.vn` ~350k/năm
- Công cụ WHOIS: https://whois.bkns.vn/

#### B. Hosting
| Loại | Giá khởi điểm | Đặc điểm |
|------|--------------|----------|
| Giá rẻ | ~26k–45k/tháng | SSD, cá nhân/startup |
| Shared cPanel | ~47k–104k/tháng | LSCache, SSL miễn phí, JetBackup hàng ngày |
| WordPress | ~570k–1.254k/năm | Tối ưu WP (WPCP01–03) |
| Reseller | ~1.7M/tháng | Bao gồm rack/power/bandwidth |
| Windows | — | ASP.NET, MS SQL |

#### C. VPS & Cloud
| Dòng | Giá | Specs |
|------|-----|-------|
| VPS MMO | 70k–450k/tháng | 1–8 vCPU, 1–8GB RAM, 20–80GB SSD |
| VPS SEO | 425k–700k/tháng | 3–5GB RAM, cam kết ≥3 tháng |
| Cloud VPS AMD | — | AMD EPYC Gen2, hiệu năng cao |
| VMware/KVM | — | Doanh nghiệp, linh hoạt |

#### D. Máy chủ vật lý & Colocation
- Dedicated server và colocation tại data center đạt chuẩn Tier 3
- Cài OS miễn phí, bảo hành phần cứng, hỗ trợ 24/7

#### E. Email Doanh Nghiệp
- Gói MINI EMAIL 01–04 và ES 01–04: 100GB → 2.000GB
- Chống virus/spam, webmail, >2.000 khách đang dùng

#### F. SSL & Chứng chỉ
- RapidSSL, PositiveSSL, GeoTrust, Comodo Wildcard DV, EV SSL
- RapidSSL ~160k/năm; Comodo Wildcard DV ~5.574k/năm
- https://ssl.bkns.vn/

#### G. Cloud & Hạ tầng nâng cao
- Public Cloud resell: FPT Cloud, AWS, GCP, Alibaba Cloud
- Private/Hybrid Cloud cho doanh nghiệp

#### H. Dịch vụ bổ trợ
- Backup tự động JetBackup (hàng ngày, lưu 30 ngày)
- Migration WordPress (giảm 20%)
- Anti-DDoS, Monitoring, Managed server

---

## 4. Quản Lý Ảnh — Bằng Chứng & Tài Liệu Trực Quan

> **Đây là tính năng hoàn toàn mới** so với ý tưởng Karpathy gốc, được bổ sung vì bối cảnh BKNS có nhiều bảng giá, chính sách thay đổi thường xuyên cần lưu bằng chứng gốc.

### 4.1. Bài toán cần giải quyết

- Bảng giá BKNS thay đổi thường xuyên → cần **ảnh gốc làm bằng chứng** tại thời điểm
- Một số note/thông báo quan trọng chỉ tồn tại dưới dạng screenshot (Zalo, Facebook, ảnh chụp màn hình)
- Ảnh cần vừa được **trích xuất thành Markdown** (để nhét vào context LLM) vừa **lưu nguyên bản** (để kiểm tra lại khi cần)

### 4.2. Cấu trúc thư mục ảnh

> ⚠️ **Lưu ý path:** `assets/` nằm ở **root repo** (cùng cấp với `wiki/`), KHÔNG phải trong `wiki/`.

```
/home/openclaw/wiki/          ← root repo
├── wiki/                     ← wiki Markdown (không chứa ảnh)
└── assets/                   ← ảnh & media (ở root, không phải trong wiki/)
    ├── images/               ← Thumbnail đã nén (≤100KB, commit Git thường)
    │   ├── bang-gia-hosting-2026q1.png
    │   └── thong-bao-khuyen-mai.jpg
    └── evidence/             ← Ảnh gốc full-resolution (Git LFS)
        ├── price-screens/
        │   └── bang-gia-hosting-2026q1-original.png
        └── notes/
            └── thong-bao-chinh-sach-2026-04.png
```

**Quy tắc đặt tên:**
- Lowercase, dùng dấu gạch ngang: `bang-gia-hosting-2026q1.png`
- Thêm năm-quý vào tên để dễ tra cứu theo thời gian
- Ảnh gốc thêm hậu tố `-original`: `bang-gia-hosting-2026q1-original.png`

### 4.3. Cách tham chiếu ảnh trong wiki Markdown

**Pattern chuẩn — từ file trong `wiki/products/hosting/` tham chiếu lên `assets/`:**
```markdown
## Bảng giá Hosting (Cập nhật Q1/2026)

| Gói | Giá/tháng | Disk | Băng thông |
|-----|-----------|------|-----------|
| BKCP01 | 26.000đ | 1GB | Không giới hạn |
| BKCP02 | 45.000đ | 2GB | Không giới hạn |

*Nguồn: Bảng giá chính thức BKNS, chụp ngày 2026-04-01*

<details>
<summary>📸 Xem ảnh bảng giá gốc (bằng chứng)</summary>

![Bảng giá hosting BKNS Q1/2026](../../assets/images/bang-gia-hosting-2026q1.png)

*Ảnh gốc full-resolution: `assets/evidence/price-screens/bang-gia-hosting-2026q1-original.png`*
</details>
```

> **Lưu ý relative path:** Từ `wiki/products/hosting/*.md` → lên root cần `../../assets/...` (2 cấp).

### 4.4. Workflow xử lý ảnh tự động (Gemini Vision)

**Khi người dùng gửi ảnh bảng giá qua Telegram:**

```
[User gửi ảnh screenshot bảng giá]
         ↓
[OpenClaw nhận → skill: ingest-image]
         ↓
[Lưu ảnh gốc vào assets/evidence/ với Git LFS]
         ↓
[Gemini 2.5 Flash Vision extract → bảng dữ liệu]
         ↓
[Tạo markdown table + nén thumbnail → assets/images/]
         ↓
[Ghép vào file wiki tương ứng + backlink]
         ↓
[Commit Git: "Update: bảng giá hosting Q1/2026"]
```

**Prompt chuẩn cho Gemini Vision khi extract bảng giá:**
```
Hãy extract toàn bộ bảng giá trong ảnh này thành định dạng Markdown table.
Yêu cầu:
1. Giữ nguyên đơn vị tiền tệ (đ, VND)
2. Giữ nguyên tên gói, thông số kỹ thuật
3. Nếu có nhiều bảng, tạo nhiều section riêng biệt
4. Sau bảng, thêm dòng: "Nguồn: [tên ảnh], ngày [ngày extract]"
5. Nếu có thông tin không rõ do ảnh mờ, đánh dấu: [KHÔNG RÕ]
Trả về chỉ nội dung Markdown, không giải thích thêm.
```

### 4.5. So sánh: OCR thuần vs. Gemini Vision (cho bảng giá)

| Tiêu chí | Google Vision OCR | Gemini 2.5 Flash Vision | Chọn |
|----------|------------------|------------------------|------|
| Độ chính xác bảng phức tạp | <70% | ~93–100% | **Gemini** |
| Latency | ~2s/ảnh | ~8–12s/ảnh | OCR nếu cần nhanh |
| Chi phí | $1.50/1000 ảnh | ~$0.04/1000 ảnh | **Gemini** |
| Hiểu merged cells | Kém | Tốt | **Gemini** |
| Kết luận | Dùng cho scan nhanh | **Dùng cho bảng giá** | ✅ Gemini 2.5 Flash |

**→ Kết luận: Dùng Gemini 2.5 Flash Vision cho extract ảnh bảng giá. Chi phí cực thấp, chất lượng cao với bảng phức tạp.**

### 4.6. Thiết lập Git LFS đúng cách

```bash
# ✅ ĐÚNG: Chạy từ root repo (/home/openclaw/wiki/)
git lfs install
git lfs track "assets/evidence/**"
git add .gitattributes
git commit -m "chore: setup Git LFS for evidence images"

# Kiểm tra .gitattributes đã được tạo đúng:
cat .gitattributes
# Nên thấy:
# assets/evidence/** filter=lfs diff=lfs merge=lfs -text
```

> ❌ **Lỗi cũ (đã xóa):** Lệnh `echo "wiki/assets/evidence/** ..."` sai vì:
> 1. Prefix `wiki/` không tồn tại (assets ở root, không trong wiki/)
> 2. Không gọi `git lfs install` trước
> 3. Pattern glob có thể không hoạt động nếu thiếu dấu ngoặc kép

---

## 5. Context Caching — Tiết Kiệm Token Tối Đa

> **Chiến lược đã cập nhật:** Dùng **Implicit Caching** (tự động, miễn phí storage) thay vì **Explicit Caching** (cần quản lý, tốn $1/1M token/giờ lưu trữ).

### 5.1. Implicit Caching là gì?

Gemini 2.5 tự động nhận diện và cache **prefix lặp lại** giữa các request. Nếu mỗi query đều bắt đầu bằng toàn bộ wiki (prefix cố định), Gemini sẽ:
- Tự động cache prefix đó trên server
- Giảm giá **75%** cho các token được cache
- **Không tốn phí lưu trữ** — khác hoàn toàn với Explicit Caching

**Điều kiện để implicit caching có hiệu quả:**
- Prefix phải giống hệt nhau (xuống từng byte) giữa các request
- Prefix đủ dài (thường ≥1024 token)
- Nhiều request trong khoảng thời gian ngắn → cache hit cao hơn

### 5.2. So sánh: Implicit vs Explicit Caching

| Tiêu chí | Implicit Caching | Explicit Caching |
|----------|-----------------|-----------------|
| Quản lý | Tự động — không cần code | Phải gọi API tạo/xóa cache |
| Storage cost | **Miễn phí** | $1.00/1M token/giờ |
| Discount | **75% off** cached tokens | 75% off cached tokens |
| TTL | Tự động (~1 giờ) | Tự chọn (có thể rất dài) |
| Phù hợp | Wiki nhỏ–vừa (<500k token) | Wiki lớn, TTL >6h cần đảm bảo |
| **Lựa chọn** | ✅ **Phase 1–2** | ⚠️ Chỉ dùng nếu wiki rất lớn |

**→ Kết luận: Dùng Implicit Caching ngay từ Phase 1 — đơn giản hơn, không tốn storage cost.**

### 5.3. Giá token Gemini 2.5 (cập nhật 2026-04)

> ⚠️ Luôn kiểm tra giá mới nhất tại: https://cloud.google.com/vertex-ai/generative-ai/pricing

| Model | Input (thường) | Input (cached, -75%) | Output |
|-------|---------------|---------------------|--------|
| **Gemini 2.5 Pro** | $1.25/1M (≤200K) | $0.31/1M | $10.00/1M |
| **Gemini 2.5 Flash** | $0.15/1M | $0.0375/1M | $0.60/1M |

*Lưu ý: Giá Pro tăng lên $2.50/1M với request >200K token context.*

### 5.4. Tính toán tiết kiệm thực tế

**Kịch bản: Wiki 50k token, 100 câu hỏi/ngày (3.000/tháng)**

Giả định cache hit rate 80% (cache hoạt động ~1 giờ, queries trải đều trong ngày):

| Loại token | Lượng/tháng | Đơn giá | Thành tiền |
|------------|------------|---------|-----------|
| Input wiki (non-cached, 20%) | 3.000 × 20% × 50k = 30M | $0.15/1M | $4.50 |
| Input wiki (cached, 80%) | 3.000 × 80% × 50k = 120M | $0.0375/1M | $4.50 |
| Dynamic input (câu hỏi) | 3.000 × 200 = 600k | $0.15/1M | $0.09 |
| Output (câu trả lời ~500 token) | 3.000 × 500 = 1.5M | $0.60/1M | $0.90 |
| **Tổng query/tháng** | | | **~$9.99** |

*So sánh: Nếu không dùng caching → 3.000 × 50k = 150M × $0.15/1M = $22.50 chỉ riêng input wiki.*

### 5.5. Code mẫu: Query với Implicit Caching (Python)

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part

vertexai.init(project="BKNS_PROJECT_ID", location="us-central1")

# Load toàn bộ wiki (concat tất cả .md files)
def load_wiki(wiki_dir: str) -> str:
    import os
    texts = []
    for root, dirs, files in os.walk(wiki_dir):
        for fname in sorted(files):
            if fname.endswith(".md"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    rel_path = os.path.relpath(fpath, wiki_dir)
                    texts.append(f"\n\n---\n# FILE: {rel_path}\n\n{f.read()}")
    return "\n".join(texts)

wiki_content = load_wiki("/home/openclaw/wiki/wiki/")

SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn của BKNS - nhà cung cấp hosting, tên miền, VPS hàng đầu Việt Nam.

Quy tắc bắt buộc:
1. CHỈ trả lời dựa trên tài liệu wiki được cung cấp
2. Luôn ghi rõ nguồn: "Theo [tên file/section]..."
3. Nếu không có thông tin → nói rõ: "Tôi không có thông tin về vấn đề này.
   Vui lòng liên hệ hỗ trợ BKNS 24/7 qua hotline [SỐ HOTLINE] hoặc
   live chat tại bkns.vn"
4. KHÔNG bịa thông tin về giá, tính năng, chính sách
5. Gợi ý sản phẩm phù hợp với nhu cầu khách
6. Trả lời bằng tiếng Việt, thân thiện, chuyên nghiệp
"""

# ✅ IMPLICIT CACHING: Wiki được đặt đầu tiên trong contents → Gemini tự cache
# Prefix (wiki_content) phải giống hệt nhau qua mọi request để cache có hiệu lực
model = GenerativeModel(
    model_name="gemini-2.5-flash",  # Dùng model name mới nhất từ Vertex AI docs
    system_instruction=SYSTEM_PROMPT,
)

def query_wiki(user_question: str) -> str:
    """Query wiki với implicit caching."""
    response = model.generate_content(
        contents=[
            # Wiki content đặt trước → implicit cache prefix
            Content(role="user", parts=[
                Part.from_text(f"Tài liệu wiki BKNS:\n\n{wiki_content}"),
            ]),
            Content(role="model", parts=[
                Part.from_text("Đã đọc tài liệu wiki. Sẵn sàng trả lời câu hỏi.")
            ]),
            # Câu hỏi thực tế của user
            Content(role="user", parts=[
                Part.from_text(user_question)
            ]),
        ]
    )
    # Log token usage để theo dõi cache hit
    usage = response.usage_metadata
    cached_tokens = getattr(usage, 'cached_content_token_count', 0)
    print(f"[Cache] Cached: {cached_tokens} / Total input: {usage.prompt_token_count}")
    return response.text

# Sử dụng
answer = query_wiki("Gói VPS MMO01 giá bao nhiêu và phù hợp cho ai?")
print(answer)
```

> **Lưu ý quan trọng:** Để implicit caching hoạt động, `wiki_content` phải được load **một lần** và tái sử dụng qua mọi request trong cùng một process. Không load lại wiki mỗi lần query.

### 5.6. Khi nào nên chuyển sang Explicit Caching?

| Tình huống | Giải pháp |
|-----------|-----------|
| Wiki < 500k token, queries thường xuyên | ✅ **Implicit caching** — dùng ngay |
| Wiki > 500k token, cần TTL >6 giờ đảm bảo | → Explicit Caching đáng đầu tư |
| Queries thưa thớt (<10/ngày) | Không cần caching — chi phí không đáng kể |
| Lint / health check wiki | Không dùng cache — cần đọc file thực tế |
| Compile wiki mới | Không dùng cache — Gemini Pro đọc `raw/` |

---

## 6. Kiến Trúc Multi-Agent: Gemini Pro + Flash

### 6.1. Quyết định đã được xác nhận

> **Kênh:** Telegram (OpenClaw hỗ trợ tốt)
> **Ngân sách:** $300 Vertex AI budget
> **Kiến trúc:** Bắt đầu với **Gemini 2.5 Pro đơn thuần** — thêm Flash Worker khi cần tối ưu

### 6.2. Phân công vai trò

| Vai trò | Model | Nhiệm vụ | Chi phí tương đối |
|---------|-------|----------|------------------|
| **Orchestrator** | Gemini 2.5 Pro | Compile wiki, linting, review phức tạp, phán quyết khó | Cao |
| **Flash Worker** | Gemini 2.5 Flash | Trả lời Telegram (query), ingest tài liệu mới, extract ảnh | Thấp (~13× rẻ hơn Pro) |

**Flash nhanh hơn Pro ~3×, rẻ hơn ~13×** → dùng Flash cho 90% volume queries.

### 6.3. Sơ đồ kiến trúc tổng thể

```
[Telegram User]
      ↓
[OpenClaw Gateway]
      ↓
[Orchestrator Agent — Gemini 2.5 Pro]
      │
      ├── Câu hỏi đơn giản ──→ [Flash Worker + Implicit Cache] ──→ Trả lời
      │
      ├── Câu hỏi phức tạp ──→ [Flash Worker] (research)
      │                               ↓ tóm tắt kết quả
      │                        [Pro] (synthesis) ──→ Trả lời
      │
      ├── Ingest ảnh mới ──→ [Flash Vision Worker] ──→ Extract → Commit wiki
      │
      ├── Ingest tài liệu ──→ [Flash Worker] ──→ classify → raw/
      │                               ↓ trigger
      │                        [Pro] (compile wiki) ──→ wiki/
      │
      └── Linting (cron) ──→ [Pro] health check ──→ Diff report → Git PR
```

### 6.4. Cấu hình OpenClaw cho multi-agent

```yaml
# agents.yaml
agents:
  list:
    - id: bkns-orchestrator
      default: true
      model: "google/gemini-2.5-pro"  # ✅ model string đúng — verify với OpenClaw docs
      workspace: "~/.openclaw/bkns-orchestrator"
      subagents:
        allowAgents: ["bkns-flash-worker", "bkns-vision-worker"]
      skills:
        - compile-wiki
        - lint-wiki
        - route-query

    - id: bkns-flash-worker
      model: "google/gemini-2.5-flash"  # ✅ model string đúng
      workspace: "~/.openclaw/bkns-flash"
      skills:
        - query-wiki-cached
        - ingest-raw

    - id: bkns-vision-worker
      model: "google/gemini-2.5-flash"  # Vision included trong Flash 2.5
      workspace: "~/.openclaw/bkns-vision"
      skills:
        - ingest-image
        - extract-price-table

# channels.yaml
channels:
  telegram:
    enabled: true
    dmPolicy: "allowlist"
    accounts:
      bkns-main:
        botToken: "<BKNS_BOT_TOKEN>"
        allowFrom: ["<ADMIN_TELEGRAM_ID>"]

bindings:
  - agentId: bkns-orchestrator
    match: { channel: "telegram", accountId: "bkns-main" }
```

> ⚠️ **Lưu ý:** Model string chính xác cho OpenClaw cần verify với tài liệu OpenClaw. Ví dụ trên dùng format ước lượng.

### 6.5. Routing logic

```
┌─────────────────────────────────────────────────────────┐
│              ROUTING DECISION TREE                       │
├─────────────────────────────────────────────────────────┤
│ INPUT: Câu hỏi từ Telegram                              │
│                                                         │
│ Phân loại (Flash - 1 round trip rẻ):                    │
│   "simple" → Flash + Implicit Cache → Trả lời ngay     │
│   "complex" → Flash research → Pro synthesis            │
│   "image"  → Vision Worker → Extract → commit wiki      │
│   "compile"→ Pro compile từ raw/ mới                    │
│   "lint"   → Pro health check (cron only)               │
│                                                         │
│ Nếu Flash trả lời có confidence thấp:                   │
│   → Fallback sang Pro để kiểm tra lại                   │
└─────────────────────────────────────────────────────────┘
```

### 6.6. Khuyến nghị theo phase

- **Phase 1–2:** Dùng **Gemini 2.5 Pro đơn thuần** — đơn giản, dễ debug, không cần overhead multi-agent
- **Phase 3+:** Nếu traffic >20 queries/giờ → thêm Flash Worker cho query thông thường
- **Implicit Caching** nên dùng ngay từ Phase 1 — không cần multi-agent, tiết kiệm đáng kể

---

## 7. Cấu Trúc Wiki & Phạm Vi Kiến Thức

### 7.1. Cấu trúc thư mục hoàn chỉnh

```
/home/openclaw/wiki/              ← root repo
├── README.md                    ← Tổng quan dự án
├── ytuongbandau.md              ← Tài liệu nghiên cứu này
│
├── wiki/                        ← Wiki chính (Markdown, do LLM quản lý)
│   ├── index.md
│   ├── company/
│   │   ├── gioi-thieu.md
│   │   ├── gia-tri-cot-loi.md
│   │   └── doi-tac.md
│   ├── products/
│   │   ├── ten-mien/
│   │   ├── hosting/
│   │   ├── vps-cloud/
│   │   ├── may-chu/
│   │   ├── email/
│   │   └── ssl/
│   ├── support/
│   ├── sales/
│   ├── technical/
│   └── faq/
│
├── raw/                         ← Dữ liệu thô chưa biên dịch
│   ├── website-crawl/
│   ├── price-lists/
│   └── internal-docs/
│
├── assets/                      ← Ảnh & media (ở ROOT, không phải trong wiki/)
│   ├── images/                  ← Thumbnail nén ≤100KB (Git thường)
│   └── evidence/                ← Ảnh gốc full-res (Git LFS)
│       ├── price-screens/
│       └── notes/
│
└── logs/                        ← Log agent, diff, cron job
    ├── compile-log.md
    └── lint-reports/
```

### 7.2. Lịch trình xây dựng theo Phase

| Phase | Nội dung wiki | Mục tiêu | Thời gian |
|-------|--------------|----------|----------|
| **1** | company/ + products/ten-mien/ + products/hosting/ | Bot trả lời câu hỏi cơ bản | Tuần 1–2 |
| **2** | products/vps-cloud/ + email/ + ssl/ + ingest ảnh | Bao phủ toàn bộ sản phẩm + Vision | Tuần 3–4 |
| **3** | support/ + sales/ + technical/ | Hỗ trợ nhân viên tư vấn | Tuần 5–6 |
| **4** | faq/ + linting + cross-link | Hoàn thiện, chuẩn hóa | Ongoing |

---

## 8. Thiết Kế Kỹ Thuật Tổng Thể

### 8.1. Luồng dữ liệu hoàn chỉnh

```
[Nguồn dữ liệu thô]
  Web crawl bkns.vn
  Ảnh bảng giá (Telegram)
  Tài liệu nội bộ
         ↓
      [raw/]
         ↓  [Gemini 2.5 Pro: compile-wiki]
      [wiki/]
         ↓
  [Concat wiki → wiki_content string]
  (load 1 lần, giữ trong memory)
         ↓  ←────── [Câu hỏi từ Telegram]
  [Flash Worker: gửi wiki_content + câu hỏi]
  (Implicit cache tự động cache prefix wiki)
         ↓
  [Câu trả lời + nguồn file]
         ↓
  [Filing: hay → faq.md]

  ──────── Cron jobs song song ────────
  [Lint tuần/tháng]
  → Pro đọc wiki/ → health check → PR report
```

### 8.2. Các Skill cần xây cho OpenClaw

#### Skill 1: `ingest-raw`
- **Input:** URL hoặc file (qua Telegram) hoặc text paste
- **Hành vi:** Download/lưu vào `raw/`, gán metadata (nguồn, ngày, chủ đề sơ bộ)
- **Output:** Xác nhận lưu, trigger `compile-wiki` nếu cần

#### Skill 2: `ingest-image`
- **Input:** Ảnh từ Telegram
- **Hành vi:**
  1. Lưu ảnh gốc vào `assets/evidence/` với tên chuẩn + Git LFS
  2. Gọi Gemini 2.5 Flash Vision → extract bảng/nội dung
  3. Tạo thumbnail nén vào `assets/images/`
  4. Ghép nội dung extracted vào file wiki tương ứng
  5. Commit Git với message chuẩn
- **Output:** Preview nội dung extracted + link file wiki được update

#### Skill 3: `compile-wiki`
- **Input:** Trigger thủ công hoặc cron
- **Hành vi:**
  1. Liệt kê file mới/thay đổi trong `raw/`
  2. Gửi cho Gemini 2.5 Pro: tóm tắt + phân loại + đề xuất vị trí wiki
  3. Tạo/cập nhật file `.md` trong `wiki/` theo template chuẩn
  4. Thêm backlink, cập nhật `index.md`
  5. Reload `wiki_content` string trong memory (invalidate implicit cache prefix)
- **Output:** Danh sách file created/updated

#### Skill 4: `query-wiki`
- **Input:** Câu hỏi từ Telegram
- **Hành vi:**
  1. Gọi Gemini 2.5 Flash với wiki_content (prefix) + câu hỏi
  2. Implicit caching tự động hoạt động nếu wiki_content giữ nguyên
  3. Format câu trả lời, thêm nguồn file
  4. Nếu hay → file vào `faq/`
- **Output:** Câu trả lời + "Nguồn: [file/section]"

#### Skill 5: `lint-wiki`
- **Input:** Cron tuần/tháng
- **Hành vi:**
  1. Đọc toàn bộ `wiki/` theo batch
  2. Gemini 2.5 Pro health check: mâu thuẫn, giá lỗi thời, link hỏng
  3. Cross-check giá với web search (bkns.vn)
  4. Sinh diff report → commit vào nhánh `lint/YYYY-MM-DD`
- **Output:** PR report để admin review

### 8.3. Template file wiki chuẩn

```markdown
---
title: [Tên sản phẩm/chủ đề]
category: [Hosting/VPS/Tên miền/...]
updated: YYYY-MM-DD
source: [URL nguồn chính]
evidence: [assets/evidence/... nếu có ảnh bằng chứng]
---

## Mô tả
[Giải thích ngắn: sản phẩm là gì, dùng cho ai]

## Tính năng nổi bật
- ...

## Bảng giá
| Gói | Giá | Thông số | Phù hợp |
|-----|-----|----------|---------|

<details>
<summary>📸 Bằng chứng bảng giá (ảnh gốc)</summary>
![Bảng giá](../../assets/images/...)
</details>

## So sánh & tư vấn chọn gói
[Khi nào chọn gói nào]

## Câu hỏi thường gặp
**Q:** ...
**A:** ...

## Liên quan
- [[products/[related-product]]]
- [[support/chinh-sach]]
```

---

## 9. Đảm Bảo Chất Lượng Kiến Thức

### 9.1. Nguyên tắc

1. **Nguồn trích dẫn bắt buộc:** Mỗi fact có giá, chính sách, thông số → ghi rõ nguồn URL + ngày
2. **Tách fact và suy luận:** Fact sát nguồn; suy luận đánh dấu `> [Phân tích]`
3. **Versioning Git:** Toàn bộ wiki được Git track, dễ rollback
4. **Ảnh làm bằng chứng:** Bảng giá quan trọng phải có ảnh gốc kèm theo
5. **Linting định kỳ:** Phát hiện mâu thuẫn, giá lỗi thời, link hỏng
6. **Human review:** File về chính sách, giá, quy trình → admin review trước khi dùng

### 9.2. System prompt chuẩn cho bot BKNS Telegram

```
Bạn là trợ lý tư vấn của BKNS - nhà cung cấp hosting, tên miền,
VPS hàng đầu Việt Nam. Quy tắc bắt buộc:

1. CHỈ trả lời dựa trên tài liệu wiki được cung cấp
2. Luôn ghi rõ nguồn: "Theo [tên file/section]..."
3. Nếu không có thông tin → nói rõ:
   "Tôi không có thông tin về vấn đề này. Vui lòng liên hệ
   hỗ trợ BKNS 24/7 qua hotline [SỐ HOTLINE — cần bổ sung]
   hoặc live chat tại bkns.vn"
4. KHÔNG bịa thông tin về giá, tính năng, chính sách
5. Gợi ý sản phẩm phù hợp với nhu cầu khách
6. Trả lời bằng tiếng Việt, thân thiện, chuyên nghiệp
```

> 📋 **TODO:** Bổ sung số hotline BKNS chính thức vào system prompt và vào `wiki/support/lien-he.md`

---

## 10. Lộ Trình Triển Khai

### Phase 1: Bootstrap — Nền tảng (Tuần 1–2)
- [ ] Thiết lập Git repo tại `/home/openclaw/wiki/`
- [ ] Tạo cấu trúc thư mục theo section 7.1
- [ ] Thiết lập Git LFS đúng cách (theo section 4.6)
- [ ] Crawl bkns.vn → lưu vào `raw/`
- [ ] Viết skill `compile-wiki` và `ingest-raw`
- [ ] Compile Phase 1: company/ + products/ten-mien/ + products/hosting/
- [ ] Viết skill `query-wiki` với implicit caching (section 5.5)
- [ ] Kết nối bot Telegram đơn giản (Gemini 2.5 Pro đơn thuần)
- [ ] **Bổ sung hotline BKNS vào wiki/support/lien-he.md và system prompt**
- [ ] Test trả lời câu hỏi cơ bản về hosting và tên miền

### Phase 2: Mở rộng sản phẩm (Tuần 3–4)
- [ ] Compile Phase 2: VPS/Cloud + Email + SSL
- [ ] Viết skill `ingest-image` và `extract-price-table` (Gemini 2.5 Flash Vision)
- [ ] Nhập bảng giá hiện tại dưới dạng ảnh → extract → wiki
- [ ] Test bot trả lời đa dạng câu hỏi, đo cache hit rate
- [ ] Nếu wiki > 500k token: xem xét chuyển sang Explicit Caching (section 5.6)

### Phase 3: Hỗ trợ bán hàng (Tuần 5–6)
- [ ] Compile Phase 3: support/ + sales/ + technical/
- [ ] Xây dựng kịch bản tư vấn, xử lý phản đối
- [ ] FAQ tổng hợp từ câu hỏi thực tế trong team
- [ ] Thêm Flash Worker nếu traffic >20 queries/giờ (multi-agent)

### Phase 4: Hoàn thiện & Vận hành (Ongoing)
- [ ] Full linting pass đầu tiên
- [ ] Thiết lập cron job linting mỗi tuần
- [ ] Cross-link toàn bộ wiki
- [ ] Onboarding tài liệu hướng dẫn cho nhân viên mới
- [ ] Đo lường: % câu hỏi bot trả lời đúng (mục tiêu: >85%)

---

## 11. Phân Tích Khả Thi & Ngân Sách

### 11.1. Ước tính chi phí với $300 Vertex AI (đã cập nhật giá Gemini 2.5)

> ⚠️ Budget $300: Cần xác nhận đây là **billing credit** (dùng được vô thời hạn) hay **trial credit** (hết hạn sau 90 ngày theo chính sách Google Cloud standard). Nếu là trial credit → $300 cần được dùng hết trong 90 ngày.

**Kịch bản: 100 câu hỏi/ngày (3.000/tháng), wiki 50k token**

| Hoạt động | Model | Token/tháng | Chi phí/tháng |
|-----------|-------|------------|--------------|
| **Compile wiki** (2×/tuần, Flash 70% + Pro 30%) | Flash + Pro | ~5M input, ~1.2M output | ~$6.50 |
| **Ingest ảnh** (~50 ảnh, Flash Vision) | Flash | ~150k input | ~$0.02 |
| **Query bot** (3.000 q, implicit cache 80%) | Flash | ~153M input mixed | ~$9.99 |
| **Linting** (2×/tháng, Pro) | Pro | ~600k input, ~200k output | ~$2.75 |
| **Tổng ước tính** | | | **~$19/tháng** |

**→ $300 budget đủ dùng ~15 tháng (~1.3 năm)**

*Lưu ý: Khác với ước tính gốc ("2.7 năm") vì đã tính đúng:*
- *Giá output token Pro ($10/1M, không phải $0)*
- *Giá Gemini 2.5 (cao hơn 1.5)*
- *Output token cost khi compile (150k output × 8 lần/tháng)*

**Tối ưu để kéo dài ngân sách:**
- Dùng Flash thay Pro cho compile khi nội dung đơn giản → giảm ~50% compile cost
- Giảm tần suất compile: 1×/tuần thay vì 2× → giảm thêm 50%
- Với tối ưu tốt: có thể xuống ~$12/tháng → ~25 tháng (~2 năm)

### 11.2. Đánh giá khả thi tổng thể

| Tiêu chí | Đánh giá | Ghi chú |
|----------|----------|---------|
| Kỹ thuật | ✅ **Khả thi cao** | Gemini 2.5 + OpenClaw, API mature |
| Chi phí | ✅ **Tiết kiệm** | Implicit caching giảm ~60% query cost |
| Thời gian | ✅ **Nhanh** | Phase 1 hoàn thành trong 1–2 tuần |
| Độ chính xác | ✅ **Cao** | Full-context tốt hơn RAG ở quy mô này |
| Quản lý ảnh | ✅ **Khả thi** | Gemini Vision hiệu quả, Git LFS đơn giản |
| Bảo trì | ✅ **Nhẹ** | Linting tự động, Git versioning |
| Rủi ro chính | ⚠️ **Giá BKNS** | Thay đổi thường → linting tuần là bắt buộc |

### 11.3. Rủi ro và giải pháp

| Rủi ro | Giải pháp |
|--------|-----------|
| Giá BKNS thay đổi → wiki lỗi thời | Linting tuần + nguồn trích dẫn có ngày |
| Bot hallucinate | System prompt chặt + yêu cầu cite nguồn |
| Wiki quá lớn (>1M token) | Lexical search lọc trước + Explicit Cache theo nhóm |
| Ảnh mờ → extract sai | Human review cho bảng giá trước khi publish |
| $300 là trial credit (hết hạn 90 ngày) | Dùng tập trung, ưu tiên Phase 1–2 trong 90 ngày đầu |
| Implicit cache miss cao | Đảm bảo wiki_content load 1 lần, không reload mỗi query |

---

## 12. Câu Hỏi Đã Trả Lời

> Cập nhật dựa trên feedback và nghiên cứu (2026-04-04)

| Câu hỏi | Quyết định |
|---------|-----------|
| **Kênh bot** | ✅ **Telegram** — OpenClaw hỗ trợ tốt |
| **LLM chính** | ✅ **Gemini 2.5 Pro** (Vertex AI) |
| **LLM phụ** | ✅ **Gemini 2.5 Flash** cho queries thông thường + extract ảnh |
| **Multi-agent** | ⚠️ **Tùy chọn** — Bắt đầu với Pro đơn thuần; thêm Flash Worker khi traffic >20 q/giờ |
| **Caching strategy** | ✅ **Implicit Caching** làm chính — miễn phí storage, đơn giản |
| **Nguồn dữ liệu nội bộ** | 📋 **Chưa xác định** — cần bổ sung khi có: kịch bản tư vấn, quy trình nội bộ |
| **Hotline BKNS** | 📋 **Chưa có** — cần bổ sung vào system prompt và wiki/support/lien-he.md |
| **Cập nhật bảng giá** | ✅ **Tự động** — Bot nhận ảnh → Vision extract → commit; linting tuần kiểm tra |
| **Ngưỡng chuyển RAG** | ✅ **>1M token hoặc >50 concurrent users** — hiện tại chưa cần |
| **Quản lý ảnh** | ✅ **Git LFS cho assets/evidence/** + **thumbnail trong assets/images/** + Gemini Vision |
| **$300 budget** | ⚠️ **Cần xác nhận** — trial credit (90 ngày) hay billing credit (vô hạn)? |
| **Budget thực tế** | ✅ **~$15–19/tháng** → ~15–20 tháng (không phải 2.7 năm như ước tính cũ) |

---

*Tài liệu v3 — Sửa lỗi toàn diện bởi OpenClaw + Claude (2026-04-04).*
*Trạng thái: **Sẵn sàng triển khai Phase 1** — chờ xác nhận loại $300 budget và số hotline BKNS.*

