# Prompt Nghiên Cứu Phản Biện — Agent Wiki BKNS

> **Mục đích:** Copy toàn bộ prompt này gửi sang AI khác (ChatGPT, Claude, Gemini, DeepSeek...) để brainstorm tìm điểm nghẽn trước khi triển khai.
> **Cách dùng:** Copy từ dòng `---START PROMPT---` đến `---END PROMPT---`

---START PROMPT---

# YÊU CẦU: Phản biện kiến trúc dự án Agent Wiki trước khi triển khai

## Vai trò của bạn

Bạn là một **Senior AI Systems Architect** chuyên về LLM-powered knowledge systems. Tôi cần bạn đóng vai **Devil's Advocate** — tìm MỌI điểm yếu, rủi ro, contradiction, assumption sai, và bottleneck ẩn trong dự án dưới đây. Đừng khen — hãy phá.

## Mục tiêu tối thượng của dự án

Xây dựng một **hệ thống tri thức tự động (Knowledge Base)** cho công ty hosting BKNS.VN, sử dụng phương pháp **LLM-Compiled Wiki** (theo ý tưởng Andrej Karpathy 04/2026). Hệ thống này:

1. **Không dùng RAG/Vector DB** — thay vào đó gửi toàn bộ wiki làm context prefix, tận dụng Gemini Implicit Context Caching (giảm 90% chi phí token lặp)
2. **Bot Telegram** đóng vai "thủ thư tự động" — nhận dữ liệu thô, biên dịch thành wiki có cấu trúc, trả lời câu hỏi, tự kiểm tra chất lượng
3. **Claims-based architecture** — tách lớp sự thật gốc (claims YAML) khỏi lớp trình bày (Markdown wiki), mỗi fact có trạng thái, nguồn, review state
4. **Multi-agent** — Gemini 2.5 Pro (compile, lint) + Gemini 2.5 Flash (query, ingest, vision extract)
5. **Human-in-the-loop** — mọi thay đổi wiki quan trọng phải qua admin duyệt (`/duyet`)
6. **Phục vụ 3 đối tượng:** nhân viên mới, khách hàng, team kỹ thuật nội bộ
7. **MkDocs Material** làm wiki viewer cho nhân viên

## Các quyết định kiến trúc đã chốt

| Quyết định | Giá trị |
|-----------|---------|
| Platform | Vertex AI ($300 trial credit, 90 ngày) |
| Model query | gemini-2.5-flash ($0.30/$2.50 per 1M input/output) |
| Model compile/lint | gemini-2.5-pro ($1.25/$10 per 1M) |
| Caching | Implicit (90% discount, tự động, không storage fee) |
| Claims storage | Dual: YAML (human-readable, approved) + JSONL (append-only traces) |
| Build activation | active-build.yaml + Git tag |
| Ground truth | Verify toàn bộ (pricing + specs + contact) + báo cáo |
| Query traces | JSONL file log |
| Bot | OpenClaw + Telegram (@BKNS_Wiki_bot) |
| Wiki viewer | MkDocs Material |
| Schema scope | Full addon.md từ Phase 0.5 (10 đối tượng: Source, Entity, Claim, Page, Build, Pack...) |
| Dữ liệu nguồn | Crawl bkns.vn — không có dữ liệu nội bộ sẵn |
| Admin | 1 người duy nhất |

## Pipeline dữ liệu

```
[bkns.vn / ảnh / text]
  → raw/ (dữ liệu thô, metadata)
  → extraction (Gemini Flash/Pro)
  → claims/ (YAML facts + JSONL traces)
  → review gate (admin /duyet)
  → compile (Gemini Pro → Markdown wiki)
  → build/ (snapshot, active-build.yaml, Git tag)
  → query (Gemini Flash, wiki prefix + câu hỏi)
  → filing (câu trả lời hay → review → wiki)
  → lint (weekly, Gemini Pro: mâu thuẫn, outdated)
  → ground truth (crawl lại bkns.vn → compare)
```

## Lộ trình

| Phase | Thời gian | Mô tả |
|-------|-----------|-------|
| 0.5 | 2 tuần | Full schema + crawl bkns.vn + bot query cơ bản |
| 1 | 2-3 tuần | Ingest + compile pipeline + MkDocs + draft/review |
| 2 | 4-6 tuần | Vision extract + lint + ground truth + packs |
| 3 | Ongoing | Onboarding 3 đối tượng + auto-file + observability |

## Budget ước tính

- $300 trial credit (hết hạn 90 ngày)
- Chi phí dự kiến: ~$25-35/tháng (Flash query 80% + Pro compile/lint 20%)
- Đủ khoảng 8-12 tháng nếu dùng đúng model mix

## Constraints & Context

- **1 developer duy nhất** (tôi) — không có team
- **Không có dữ liệu nội bộ** — phải crawl từ website công khai
- BKNS là công ty hosting thực tế ở Việt Nam — dữ liệu bao gồm bảng giá, specs sản phẩm (hosting, VPS, tên miền, email, SSL), chính sách, hỗ trợ
- Bot chạy trên VPS Linux, đã có OpenClaw và Vertex AI service account
- Wiki dự kiến ~50-100 file Markdown, ~50k-100k token total

---

## CÂU HỎI CẦN BẠN TRẢ LỜI

### 1. ĐIỂM NGHẼN KỸ THUẬT (Technical Bottlenecks)

- Pipeline raw → claims → wiki → build có bước nào có thể thất bại âm thầm (silent failure) mà không ai biết?
- Implicit caching "90% discount" có điều kiện ẩn nào không? (TTL, minimum tokens, cache eviction khi low traffic?)
- Wiki 50-100k token gửi làm prefix mỗi query — khi nào kích thước này trở thành vấn đề? Giới hạn thực tế là bao nhiêu trước khi chất lượng câu trả lời giảm?
- Claims YAML + JSONL dual storage — có race condition hay sync issue nào khi bot và admin cùng thao tác?
- OpenClaw có giới hạn nào về skill complexity, concurrent requests, hay memory management?

### 2. ĐIỂM NGHẼN KIẾN TRÚC (Architecture Gaps)

- Claims-based architecture có thực sự cần thiết cho wiki 50-100 file? Hay nó là over-engineering cho scale này?
- Build manifest + pack system — khi nào cần? Có nên defer để Phase 3?
- Nếu Gemini API down 30 phút, bot xử lý thế nào? Có fallback strategy không?
- Ground truth check crawl bkns.vn — nếu BKNS đổi layout website, pipeline có tự phát hiện và báo lỗi không?
- 1 admin duy nhất — nếu admin nghỉ phép 2 tuần, bot stuck ở draft review, hệ thống có tê liệt không?

### 3. ĐIỂM NGHẼN BUDGET & TIMING (Financial Risks)

- $300 trong 90 ngày — trường hợp xấu nhất (worst case) tốn bao nhiêu? Có scenario nào burn hết $300 trong 30 ngày không?
- Sau khi hết $300 trial, chi phí thực tế production là bao nhiêu/tháng? Ai trả?
- 2 tuần cho Phase 0.5 với full schema — có thực tế cho 1 developer không? Các dự án tương tự cần bao lâu?

### 4. ĐIỂM NGHẼN VỀ GIÁ TRỊ (Value Proposition)

- BKNS website đã có thông tin sản phẩm rồi — bot wiki thêm giá trị gì mà website chưa có?
- So với một chatbot FAQ đơn giản (không claims, không lint, không build manifest) — toàn bộ kiến trúc phức tạp này tạo thêm bao nhiêu % giá trị so với giải pháp đơn giản?
- 3 đối tượng onboarding (nhân viên, khách, kỹ thuật) — content khác nhau thế nào? Có thực sự cần 3 onboarding hay 1 wiki đủ?

### 5. ALTERNATIVES (Giải pháp thay thế)

- Nếu bạn phải xây hệ thống tương tự từ đầu, bạn sẽ thiết kế khác chỗ nào?
- Có tool/platform nào đã giải quyết bài toán này tốt hơn custom build không? (Notion AI, Confluence + AI, GitBook AI, custom RAG...)
- Karpathy method hoạt động tốt cho personal wiki ~100 articles — nó có scale cho enterprise wiki với yêu cầu accuracy cao (giá cả, specs kỹ thuật) không?

### 6. FAILURE MODES (Kịch bản thất bại)

Hãy mô tả **3 kịch bản cụ thể** mà dự án có thể thất bại hoàn toàn, và cách phòng tránh.

---

## FORMAT TRẢ LỜI MONG MUỐN

Trả lời theo format:

```
## [Tên rủi ro/điểm nghẽn]
- **Mức độ:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- **Mô tả:** [Chi tiết vấn đề]
- **Ảnh hưởng:** [Hậu quả nếu không giải quyết]
- **Giải pháp đề xuất:** [Cách xử lý cụ thể]
```

Cuối cùng, cho tôi:
1. **Điểm số khả thi tổng thể: X/10** với lý giải
2. **Top 3 thay đổi bạn sẽ làm** nếu đây là dự án của bạn
3. **Kill criteria** — điều kiện nào thì nên dừng dự án, không triển khai

---END PROMPT---
