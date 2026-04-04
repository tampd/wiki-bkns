# Bước 7: Phase 3 — Onboarding + Auto-file + Observability

> **Phase:** 3 — Ongoing
> **Ước lượng:** 4-6 giờ (+ ongoing maintenance)
> **Prerequisite:** Phase 2 hoàn thành, wiki ≥30 files
> **Output:** Wiki phục vụ 3 đối tượng + tự động filing + dashboard metrics

---

## CHECKLIST

- [ ] 7.1 Onboarding wiki cho 3 đối tượng
- [ ] 7.2 Bot phân biệt đối tượng (routing)
- [ ] 7.3 Auto-file: câu trả lời hay → FAQ draft
- [ ] 7.4 Observability: metrics + monthly report
- [ ] 7.5 Answer Contract (build_id + confidence)
- [ ] 7.6 Pack builder (nếu wiki > 100k token)

---

## 7.1 Onboarding Wiki — 3 Đối Tượng

### wiki/onboarding/nhan-vien.md

```markdown
---
title: Onboarding Nhân Viên Mới — BKNS
category: onboarding
updated: 2026-04-04
source: internal
confidence: high
audience: new_employee
---

# Chào mừng đến với BKNS! 👋

## Tuần 1: Hiểu Về Sản Phẩm

### Sản phẩm chính BKNS cung cấp:
1. **Shared Hosting** — Hosting dùng chung, phù hợp website vừa và nhỏ
2. **VPS** — Virtual Private Server, cấu hình cao hơn, tự quản lý
3. **Tên miền** — Đăng ký và quản lý tên miền (.vn, .com, .net...)
4. **Email Hosting** — Email theo tên miền doanh nghiệp
5. **SSL Certificate** — Chứng chỉ bảo mật website

### Bảng giá cơ bản (xem chi tiết tại từng section):
- Hosting: từ ~36.000đ/tháng
- VPS: từ ~[xem wiki/products/vps/]
- Tên miền .vn: ~[xem wiki/products/ten-mien/]

## Tuần 2: Quy Trình Làm Việc

### Liên hệ hỗ trợ kỹ thuật
- **Hotline 24/7:** 1900 63 68 09 (mất phí)
- **Zalo/Chat:** [link nội bộ]
- **Ticket system:** [link nội bộ]

### Khi khách hàng gặp vấn đề:
1. Ghi nhận thông tin: tên miền, loại dịch vụ, mô tả vấn đề
2. Check status server tại [link monitoring nội bộ]
3. Nếu không tự xử lý được → escalate lên kỹ thuật

## Câu Hỏi Thường Gặp Của Nhân Viên Mới

**Q: Sự khác biệt giữa Hosting và VPS?**
A: Hosting dùng chung tài nguyên với nhiều website, phù hợp website nhỏ, quản lý đơn giản. VPS là server riêng ảo, tài nguyên được dành riêng, phù hợp ứng dụng cần hiệu năng cao.

**Q: Khách hỏi giá, tôi tra ở đâu?**
A: Wiki này (bot `/hoi`) hoặc trực tiếp tại bkns.vn. Luôn verify giá tại website vì có thể có khuyến mãi.

## Xem Thêm
- [Bảng giá Hosting](../products/hosting/tong-quan.md)
- [Bảng giá VPS](../products/vps/tong-quan.md)
- [Hỗ trợ & Liên hệ](../support/lien-he.md)
```

### wiki/onboarding/khach-hang.md

```markdown
---
title: Hướng Dẫn Khách Hàng — BKNS
category: onboarding
updated: 2026-04-04
source: internal
confidence: high
audience: customer
---

# BKNS — Dịch Vụ Hosting & Tên Miền Chuyên Nghiệp

## Chọn Dịch Vụ Phù Hợp

### Bạn cần gì?

| Nhu cầu | Dịch vụ khuyến nghị |
|---------|---------------------|
| Website blog/portfolio nhỏ | Shared Hosting Basic |
| Website doanh nghiệp | Shared Hosting Business |
| App/eCommerce tải cao | VPS |
| Email công ty | Email Hosting |
| Tên miền website | Đăng ký tên miền |
| Bảo mật HTTPS | SSL Certificate |

## Cách Đăng Ký

1. Truy cập **bkns.vn**
2. Chọn dịch vụ và gói phù hợp
3. Điền thông tin đăng ký
4. Thanh toán (hỗ trợ nhiều phương thức)
5. Nhận email xác nhận + thông tin kết nối

## Hỗ Trợ Kỹ Thuật

- **Hotline 24/7:** 1900 63 68 09
- **Tư vấn mua hàng:** 1800 646 884 (miễn phí)
- **Live chat:** bkns.vn

## Câu Hỏi Thường Gặp

**Q: Hosting BKNS có uptime bao nhiêu %?**
A: BKNS cam kết uptime 99.9% với SLA.

**Q: Tôi có thể nâng cấp gói sau không?**
A: Có, bạn có thể nâng cấp bất kỳ lúc nào.
```

### wiki/onboarding/team-ky-thuat.md

```markdown
---
title: Wiki Kỹ Thuật Nội Bộ — BKNS
category: onboarding
updated: 2026-04-04
source: internal
confidence: high
audience: technical_team
---

# Wiki Kỹ Thuật Nội Bộ

> ⚠️ Tài liệu này chứa thông tin nội bộ. Không chia sẻ ra ngoài.

## Kiến Trúc Hệ Thống Wiki Bot

### Stack
- **Bot platform:** OpenClaw + Telegram
- **AI:** Gemini 2.5 Flash (query) + 2.5 Pro (compile/lint)
- **Caching:** Vertex AI Implicit Context Caching (90% discount)
- **Storage:** Git repo + YAML claims + JSONL traces
- **Viewer:** MkDocs Material

### Thư mục quan trọng
- `/home/openclaw/wiki/` — Wiki root
- `wiki/` — Markdown files (MkDocs source)
- `claims/` — YAML source of truth
- `raw/` — Dữ liệu thô chưa compile
- `logs/` — Query traces, lint reports

### Lệnh thường dùng

```bash
# Xem bot logs
tail -f /home/openclaw/wiki/logs/query-$(date +%Y-%m-%d).jsonl

# Chạy syntax check thủ công
python /home/openclaw/wiki/tools/syntax_check.py

# Chạy lint thủ công
python /home/openclaw/wiki/skills/lint-wiki/scripts/lint.py

# Rebuild MkDocs
cd /home/openclaw/wiki && mkdocs build

# Xem chi phí hôm nay
python /home/openclaw/wiki/tools/cost_report.py --today
```

### Troubleshooting

**Bot không trả lời:**
1. Check OpenClaw service: `systemctl status openclaw`
2. Check Vertex AI quota: Google Cloud Console
3. Check logs: `tail -100 /home/openclaw/wiki/logs/query-*.jsonl`

**Cache hit rate thấp (<50%):**
- Wiki content thay đổi quá thường xuyên
- Traffic quá thấp (cache evict sau ~1h)
- Kiểm tra: cấu trúc prompt có giữ wiki prefix trước không?
```

---

## 7.2 Auto-file: Câu Trả Lời Hay → FAQ Draft

### tools/auto_file.py

```python
#!/usr/bin/env python3
"""
auto-file: phân tích query logs → tìm câu trả lời đáng đưa vào FAQ
Chạy weekly hoặc khi log đủ 50+ queries
"""
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import os

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION", "us-central1"),
)

AUTO_FILE_PROMPT = """Bạn là biên tập viên FAQ. Phân tích danh sách các câu hỏi đã được hỏi nhiều lần, xác định những câu nào nên đưa vào wiki FAQ.

DANH SÁCH CÂU HỎI (kèm số lần hỏi):
{question_list}

TIÊU CHÍ CHỌN vào FAQ:
1. Câu hỏi xuất hiện ≥3 lần
2. Câu trả lời không thay đổi theo thời gian (pricing FAQ cần cập nhật thường)
3. Câu hỏi mang giá trị cho người đọc wiki

OUTPUT FORMAT:
YAML array với format:
- question: "câu hỏi chuẩn hóa"
  short_answer: "câu trả lời ngắn gọn (1-2 câu)"
  category: "hosting|vps|ten-mien|support|general"
  priority: high|medium|low
  note: "lý do chọn"

Chỉ đề xuất tối đa 10 câu. Ưu tiên high priority trước.
"""

def load_recent_queries(days: int = 30) -> list[str]:
    """Load câu hỏi từ query logs."""
    logs_dir = WIKI_ROOT / "logs"
    questions = []
    
    for log_file in logs_dir.glob("query-*.jsonl"):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    q = entry.get("question", "")
                    if q:
                        questions.append(q)
                except:
                    pass
    
    return questions

def count_similar_questions(questions: list[str]) -> dict:
    """Đơn giản: đếm exact/near-exact duplicates."""
    from collections import Counter
    # Normalize: lowercase, strip
    normalized = [q.lower().strip() for q in questions]
    counter = Counter(normalized)
    # Chỉ lấy những câu hỏi ≥2 lần
    return {q: count for q, count in counter.items() if count >= 2}

def main():
    print("[AUTO-FILE] Analyzing query logs...")
    
    questions = load_recent_queries(days=30)
    
    if len(questions) < 20:
        print(f"[INFO] Chưa đủ queries ({len(questions)}/20 minimum). Skip.")
        return
    
    freq = count_similar_questions(questions)
    
    if not freq:
        print("[INFO] Không có câu hỏi lặp lại đủ điều kiện.")
        return
    
    # Format cho LLM
    q_list = "\n".join(f"- ({count} lần) {q}" for q, count in 
                        sorted(freq.items(), key=lambda x: -x[1])[:30])
    
    model = GenerativeModel(model_name=os.getenv("MODEL_INGEST", "gemini-2.5-flash"))
    response = model.generate_content(AUTO_FILE_PROMPT.format(question_list=q_list))
    
    try:
        suggestions = yaml.safe_load(response.text) or []
    except:
        suggestions = []
    
    if not suggestions:
        print("[INFO] Không có đề xuất FAQ mới.")
        return
    
    # Tạo draft FAQ
    faq_dir = WIKI_ROOT / "wiki" / ".drafts" / "faq"
    faq_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    draft_file = faq_dir / f"faq-suggestions-{today}.md"
    
    content = f"""---
title: FAQ Suggestions — {today}
category: faq
updated: {today}
source: auto-file
confidence: medium
---

> ⚠️ Auto-generated từ query logs. Cần review trước khi approve.

"""
    
    for s in suggestions:
        content += f"""## {s.get('question', 'Unknown')}

**{s.get('short_answer', '')}**

- Category: {s.get('category', 'general')}
- Priority: {s.get('priority', 'medium')}
- Note: {s.get('note', '')}

---

"""
    
    with open(draft_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"[AUTO-FILE] {len(suggestions)} FAQ suggestions → {draft_file}")
    print("Gõ /duyet để review và approve.")

if __name__ == "__main__":
    main()
```

---

## 7.3 Observability Dashboard

### tools/cost_report.py

```python
#!/usr/bin/env python3
"""
Monthly cost report + metrics từ query logs
Chạy: python tools/cost_report.py [--today|--week|--month]
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
import os, requests

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

def load_logs(days: int = 30) -> list[dict]:
    logs_dir = WIKI_ROOT / "logs"
    entries = []
    cutoff = datetime.now() - timedelta(days=days)
    
    for f in logs_dir.glob("query-*.jsonl"):
        with open(f, "r", encoding="utf-8") as fp:
            for line in fp:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00"))
                    if ts.replace(tzinfo=None) >= cutoff:
                        entries.append(entry)
                except:
                    pass
    
    return entries

def generate_report(days: int = 30) -> str:
    entries = load_logs(days)
    
    if not entries:
        return f"Không có dữ liệu cho {days} ngày qua."
    
    total_queries = len(entries)
    total_cost = sum(e.get("cost_usd", 0) for e in entries)
    total_cached = sum(e.get("cached_tokens", 0) for e in entries)
    total_tokens = sum(e.get("total_tokens", 0) for e in entries)
    cache_rate = (total_cached / total_tokens * 100) if total_tokens > 0 else 0
    avg_cost = total_cost / total_queries if total_queries > 0 else 0
    
    # Daily breakdown
    daily = defaultdict(lambda: {"queries": 0, "cost": 0})
    for e in entries:
        day = e["ts"][:10]
        daily[day]["queries"] += 1
        daily[day]["cost"] += e.get("cost_usd", 0)
    
    report = f"""# BKNS Wiki Cost Report — {days} ngày qua
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Tổng Quan
- Tổng queries: **{total_queries}**
- Tổng chi phí: **${total_cost:.4f}**
- Chi phí trung bình/query: **${avg_cost:.6f}**
- Cache hit rate: **{cache_rate:.1f}%**
- Ước tính/tháng (extrapolated): **${total_cost / days * 30:.2f}**

## Budget Tracker
- Budget ban đầu: $300.00
- Chi phí tích lũy (estimate): TBD
- Còn lại: TBD

## Hiệu Quả Cache
- Tổng tokens processed: {total_tokens:,}
- Cached tokens: {total_cached:,} ({cache_rate:.1f}%)
- Tiết kiệm ước tính: ${total_cached * (0.30 - 0.030) / 1_000_000:.4f}

## Top 5 Ngày Cao Điểm
"""
    
    for day, stats in sorted(daily.items(), key=lambda x: -x[1]["queries"])[:5]:
        report += f"- {day}: {stats['queries']} queries, ${stats['cost']:.4f}\n"
    
    return report

def send_monthly_report():
    report = generate_report(days=30)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    if not token or not admin_id:
        print(report)
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={
        "chat_id": admin_id,
        "text": f"📊 *Monthly Cost Report*\n\n```\n{report[:3000]}\n```",
        "parse_mode": "Markdown",
    }, timeout=10)
    
    print("[REPORT] Monthly report sent to Telegram")

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "--month"
    
    if arg == "--today":
        print(generate_report(days=1))
    elif arg == "--week":
        print(generate_report(days=7))
    else:  # --month
        print(generate_report(days=30))

if __name__ == "__main__":
    main()
```

### Cron monthly report (ngày 1 mỗi tháng 08:00)

```bash
# Thêm vào crontab:
0 8 1 * * cd /home/openclaw/wiki && /usr/bin/python3 tools/cost_report.py --month >> /home/openclaw/wiki/logs/monthly-report.log 2>&1
```

---

## 7.4 Answer Contract (addon.md §16)

Cập nhật `skills/query-wiki/scripts/query.py` để trả về metadata đầy đủ:

```python
# Thêm vào cuối phần format answer trong query_wiki()
def format_answer_with_contract(answer: str, build_id: str, cost: float, cached_rate: float) -> str:
    """Wrap câu trả lời với Answer Contract metadata."""
    contract_footer = f"\n\n---\n_📋 Build: {build_id} | Cache: {cached_rate:.0f}% | ${cost:.6f}_"
    
    # Chỉ hiện contract footer cho admin (production: ẩn với end user)
    return answer  # Trong phase 3: thêm logic phân biệt admin/user
```

---

## 7.5 Pack Builder (khi wiki > 100k token)

> **Chỉ implement khi** wiki token estimate vượt 80k. Kiểm tra:

```bash
find wiki/ -name "*.md" -not -path "wiki/.drafts/*" -exec cat {} \; | wc -c
# Chia cho 4 = token estimate
# Nếu > 320,000 chars (80k tokens) → implement packs
```

### Nếu cần packs (tools/pack_builder.py skeleton):

```python
#!/usr/bin/env python3
"""
pack_builder.py: tách wiki thành packs theo domain
Chỉ chạy khi wiki > 80k tokens
"""
PACKS = {
    "core":    ["wiki/index.md", "wiki/company/", "wiki/support/"],
    "hosting": ["wiki/products/hosting/", "wiki/onboarding/"],
    "vps":     ["wiki/products/vps/"],
    "domain":  ["wiki/products/ten-mien/"],
    "email_ssl": ["wiki/products/email/", "wiki/products/ssl/"],
}

INTENT_CLASSIFIER_PROMPT = """Phân loại câu hỏi sau vào 1 trong các pack:
- core: câu hỏi chung, liên hệ, onboarding
- hosting: shared hosting, wordpress hosting
- vps: VPS, server riêng
- domain: tên miền, dns
- email_ssl: email hosting, SSL certificate

Câu hỏi: {question}
Trả về 1 từ duy nhất: core|hosting|vps|domain|email_ssl
"""
```

---

## Crontab Tổng Hợp Cuối Cùng

```bash
# Xem crontab hiện tại
crontab -l

# Tổng hợp tất cả cron jobs:
# 06:00 daily - syntax check
0 6 * * * cd /home/openclaw/wiki && /usr/bin/python3 tools/syntax_check.py >> logs/syntax-check-cron.log 2>&1

# 09:00 Monday - lint wiki
0 9 * * 1 cd /home/openclaw/wiki && /usr/bin/python3 skills/lint-wiki/scripts/lint.py >> logs/lint-cron.log 2>&1

# 08:00 Sunday - ground truth
0 8 * * 0 cd /home/openclaw/wiki && /usr/bin/python3 tools/ground_truth.py >> logs/ground-truth-cron.log 2>&1

# 08:00 ngày 1 mỗi tháng - monthly report
0 8 1 * * cd /home/openclaw/wiki && /usr/bin/python3 tools/cost_report.py --month >> logs/monthly-report.log 2>&1
```

---

## DEFINITION OF DONE — PHASE 3

- [ ] 3 wiki onboarding files tồn tại và đầy đủ nội dung
- [ ] `/hoi` trả lời phù hợp với từng đối tượng (test với câu hỏi nhân viên mới, khách, kỹ thuật)
- [ ] `auto_file.py` chạy OK, tạo FAQ drafts từ query logs
- [ ] `cost_report.py` hiển thị metrics chính xác
- [ ] Monthly report cron đã set
- [ ] 4 cron jobs đang chạy: syntax, lint, ground-truth, monthly

---

## CHECKLIST TỔNG KẾT DỰ ÁN

```
Phase 0.5 ✅
  □ Git repo + cấu trúc đầy đủ
  □ 5+ entities, 10+ claims
  □ 8+ wiki files
  □ Bot query hoạt động (80% accuracy)
  □ Build v0.1

Phase 1 ✅
  □ /them + /compile + /duyet pipeline
  □ 20+ wiki files, 30+ claims
  □ MkDocs Material accessible
  □ Syntax check cron daily
  □ Build v0.2

Phase 2 ✅
  □ Vision extract từ ảnh
  □ Lint wiki weekly (Gemini Pro)
  □ Ground truth weekly
  □ Build v0.3+

Phase 3 ✅
  □ Onboarding 3 đối tượng
  □ Auto-file FAQ
  □ Observability + monthly report
  □ Crontab đầy đủ 4 jobs
```

---

*Kế hoạch triển khai hoàn chỉnh — BKNS Agent Wiki v1.0*
*Tài liệu: /home/openclaw/wiki/trienkhai/*
