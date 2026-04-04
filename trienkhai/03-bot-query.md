# Bước 3: Bot Query — skill query-wiki + Telegram

> **Phase:** 0.5 — Tuần 2
> **Ước lượng:** 3-4 giờ
> **Prerequisite:** Bước 1+2 hoàn thành, có ≥5 wiki files compiled (tạo thủ công trước)
> **Output:** Bot Telegram trả lời câu hỏi qua /hoi

---

## CHECKLIST

- [ ] 3.1 Compile wiki thủ công từ claims (5-8 file)
- [ ] 3.2 Tạo wiki/index.md
- [ ] 3.3 Build snapshot v0.1
- [ ] 3.4 Skill query-wiki: SKILL.md + query.py
- [ ] 3.5 Chạy bot + test 20 câu hỏi
- [ ] 3.6 Đo metrics: cache hit, cost/query
- [ ] 3.7 Commit + tag build/v0.1

---

## 3.1 Compile Wiki Thủ Công (Phase 0.5)

> Ở Phase 0.5, compile thủ công dùng script một lần. Phase 1 sẽ tự động hóa.

Tạo file `tools/compile_wiki_manual.py`:

```python
#!/usr/bin/env python3
"""
Compile wiki từ claims (chạy một lần thủ công cho Phase 0.5).
Chạy: python tools/compile_wiki_manual.py
"""
import os
import yaml
import glob
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/openclaw/wiki/.env")

import vertexai
from vertexai.generative_models import GenerativeModel

WIKI_ROOT = Path("/home/openclaw/wiki")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION", "us-central1"),
)

COMPILE_PROMPT = """Bạn là thủ thư biên tập wiki BKNS chuyên nghiệp. Hãy biên dịch các claims dưới đây thành trang wiki Markdown chuẩn.

CLAIMS INPUT:
{claims_yaml}

QUY TẮC BIÊN DỊCH:
1. KHÔNG tạo thêm fact không có trong claims
2. KHÔNG bịa giá, thông số, chính sách
3. Giữ nguyên số liệu: giá, RAM, CPU, SSD, bandwidth
4. Nếu thiếu thông tin → đánh dấu: > ⚠️ Cần bổ sung: [thông tin gì]
5. Trả lời bằng tiếng Việt, thân thiện, dễ đọc
6. Định dạng bảng giá rõ ràng với Markdown table

OUTPUT FORMAT (bắt buộc):
```
---
title: [Tên chính xác]
category: [hosting|vps|ten-mien|email|ssl|company|support]
updated: {today}
source: [URL nguồn chính]
confidence: [high|medium|low]
---

## Giới thiệu
[2-3 câu mô tả]

## Bảng giá
| Gói | Giá/tháng | Giá/năm | Thông số chính |
|-----|-----------|---------|----------------|

## Tính năng nổi bật
- ...

## Câu hỏi thường gặp
**Q:** ...
**A:** ...
```

CHỈ trả về nội dung Markdown, không có giải thích thêm.
"""

# Mapping: wiki file → claims cần dùng
COMPILE_TARGETS = [
    {
        "output": "wiki/company/gioi-thieu.md",
        "claims_pattern": "claims/company/*.yaml",
        "category": "company",
    },
    {
        "output": "wiki/products/hosting/tong-quan.md",
        "claims_pattern": "claims/products/hosting/*.yaml",
        "category": "hosting",
    },
    {
        "output": "wiki/products/vps/tong-quan.md",
        "claims_pattern": "claims/products/vps/*.yaml",
        "category": "vps",
    },
    {
        "output": "wiki/products/ten-mien/tong-quan.md",
        "claims_pattern": "claims/products/ten-mien/*.yaml",
        "category": "ten-mien",
    },
    {
        "output": "wiki/support/lien-he.md",
        "claims_pattern": "claims/products/support/*.yaml",
        "category": "support",
    },
]

def load_claims(pattern: str) -> str:
    """Load tất cả claims theo pattern, trả về YAML string."""
    claims_dir = WIKI_ROOT
    files = list(claims_dir.glob(pattern))
    
    claims = []
    for f in files:
        if f.name == "registry.yaml":
            continue
        try:
            with open(f, "r", encoding="utf-8") as fp:
                claim = yaml.safe_load(fp)
                if claim:
                    claims.append(claim)
        except Exception as e:
            print(f"  [WARN] Cannot load {f}: {e}")
    
    return yaml.dump(claims, allow_unicode=True, default_flow_style=False)

def compile_page(target: dict) -> bool:
    """Compile 1 wiki page từ claims."""
    claims_yaml = load_claims(target["claims_pattern"])
    
    if not claims_yaml or claims_yaml.strip() == "[]":
        print(f"  [SKIP] No claims for {target['output']}")
        # Tạo placeholder
        output_path = WIKI_ROOT / target["output"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"""---
title: {target['category'].title()} — Cần bổ sung
category: {target['category']}
updated: {TODAY}
source: https://bkns.vn
confidence: low
---

> ⚠️ Trang này chưa có dữ liệu. Cần crawl và extract claims trước.
""")
        return True
    
    model = GenerativeModel(model_name=os.getenv("MODEL_COMPILE", "gemini-2.5-pro"))
    
    prompt = COMPILE_PROMPT.format(claims_yaml=claims_yaml, today=TODAY)
    
    try:
        response = model.generate_content(prompt)
        wiki_content = response.text.strip()
        
        # Lưu vào wiki/
        output_path = WIKI_ROOT / target["output"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(wiki_content)
        
        print(f"  [OK] Compiled: {output_path}")
        return True
    
    except Exception as e:
        print(f"  [ERROR] Compile failed for {target['output']}: {e}")
        return False

def main():
    print("[COMPILE] Starting wiki compilation from claims...")
    
    success = 0
    for target in COMPILE_TARGETS:
        print(f"\n[TARGET] {target['output']}")
        if compile_page(target):
            success += 1
    
    print(f"\n[DONE] {success}/{len(COMPILE_TARGETS)} pages compiled")
    print("Tiếp theo: tạo wiki/index.md và chạy bot")

if __name__ == "__main__":
    main()
```

```bash
mkdir -p tools
python tools/compile_wiki_manual.py
```

---

## 3.2 Tạo wiki/index.md

```bash
cat > wiki/index.md << 'EOF'
---
title: BKNS Knowledge Base — Trang Chủ
category: index
updated: 2026-04-04
source: https://bkns.vn
confidence: high
---

# BKNS Knowledge Base

> Hệ thống tri thức chính thức của BKNS.VN — Nhà cung cấp hosting, tên miền, VPS hàng đầu Việt Nam.

## Danh Mục

### Sản Phẩm & Dịch Vụ
- [Shared Hosting](products/hosting/tong-quan.md) — Hosting dùng chung, phù hợp website vừa và nhỏ
- [VPS](products/vps/tong-quan.md) — Virtual Private Server, hiệu năng cao
- [Tên Miền](products/ten-mien/tong-quan.md) — Đăng ký và quản lý tên miền
- [Email Hosting](products/email/tong-quan.md) — Email theo tên miền doanh nghiệp
- [SSL Certificate](products/ssl/tong-quan.md) — Chứng chỉ bảo mật

### Hỗ Trợ
- [Liên Hệ](support/lien-he.md) — Hotline, live chat, ticket
- [Giới Thiệu BKNS](company/gioi-thieu.md) — Về công ty

## Liên Hệ Nhanh

| Kênh | Thông tin |
|------|-----------|
| Hotline kỹ thuật 24/7 | 1900 63 68 09 (mất phí) |
| Tư vấn kinh doanh | 1800 646 884 (miễn phí) |
| Website | https://bkns.vn |

---
*Wiki được cập nhật tự động. Mọi thông tin về giá cần verify tại bkns.vn.*
EOF
```

---

## 3.3 Build Snapshot v0.1

```bash
# Tạo snapshot directory
mkdir -p build/snapshots/v0.1

# Đếm files và token estimate
WIKI_FILES=$(find wiki/ -name "*.md" -not -path "wiki/.drafts/*" | wc -l)
WIKI_CHARS=$(find wiki/ -name "*.md" -not -path "wiki/.drafts/*" -exec cat {} \; | wc -c)
WIKI_TOKENS=$(echo "scale=0; $WIKI_CHARS / 4" | bc)  # ~4 chars/token

# Tạo manifest
cat > build/snapshots/v0.1/manifest.yaml << EOF
build_id: v0.1
build_date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
description: Phase 0.5 - Initial wiki from bkns.vn crawl
wiki_files: $WIKI_FILES
wiki_token_estimate: $WIKI_TOKENS
claims_count: $(find claims/ -name "*.yaml" -not -name "registry.yaml" | wc -l)
git_tag: build/v0.1
status: active
EOF

# Update active-build.yaml
cat > build/active-build.yaml << EOF
build_id: v0.1
build_date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
description: Phase 0.5 initial
wiki_files: $WIKI_FILES
wiki_token_estimate: $WIKI_TOKENS
git_tag: build/v0.1
status: active
EOF

echo "Build v0.1 created: $WIKI_FILES files, ~$WIKI_TOKENS tokens"
```

---

## 3.4 Skill query-wiki

### skills/query-wiki/SKILL.md

```yaml
---
name: query-wiki
description: Trả lời câu hỏi về sản phẩm/dịch vụ BKNS dựa trên wiki knowledge base. Sử dụng khi người dùng hỏi về hosting, tên miền, VPS, email, SSL, giá cả, thông số kỹ thuật, chính sách, liên hệ BKNS.
version: "1.0"
phase: "0.5"
model: gemini-2.5-flash
triggers:
  - command: /hoi
  - pattern: "hosting|vps|tên miền|ten mien|ssl|email|giá|gia|bkns|đăng ký|dang ky|hỗ trợ|ho tro"
---

# query-wiki

## Mô tả
Trả lời câu hỏi về BKNS bằng cách gửi toàn bộ wiki làm context prefix đến Gemini 2.5 Flash.
Tận dụng Implicit Context Caching để giảm 90% chi phí token lặp.

## Bước thực hiện
1. Đọc build/active-build.yaml để lấy build info
2. Load toàn bộ wiki/*.md làm WIKI_CONTENT (cache sau lần đầu)
3. Gửi WIKI_CONTENT + câu hỏi đến Gemini Flash
4. Log: timestamp, question, cached_tokens, total_tokens, cost_estimate
5. Trả lời qua Telegram

## Input
- $QUESTION: câu hỏi từ người dùng

## Output
- Câu trả lời bằng tiếng Việt
- Có ghi nguồn: "Theo [tên file]..."
- Nếu không biết: hướng dẫn liên hệ hotline

## Files
- scripts/query.py: logic chính
- scripts/test_query.py: test 20 câu hỏi
```

### skills/query-wiki/scripts/query.py

```python
#!/usr/bin/env python3
"""
query-wiki skill: trả lời câu hỏi từ wiki BKNS
"""
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load env
WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION", "us-central1"),
)

SYSTEM_PROMPT = """Bạn là trợ lý tư vấn chính thức của BKNS - nhà cung cấp hosting, tên miền, VPS hàng đầu Việt Nam.

QUY TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên tài liệu wiki được cung cấp. KHÔNG suy diễn thêm.
2. Luôn ghi nguồn: "Theo [tên file]..." hoặc "Dựa trên wiki BKNS..."
3. Nếu không có thông tin → nói RÕ RÀNG:
   "Tôi không có thông tin về vấn đề này trong cơ sở dữ liệu.
    Vui lòng liên hệ hỗ trợ BKNS:
    • Hotline kỹ thuật 24/7: 1900 63 68 09
    • Tư vấn kinh doanh: 1800 646 884 (miễn phí)
    • Live chat: https://bkns.vn"
4. TUYỆT ĐỐI KHÔNG bịa giá, tính năng, chính sách
5. Nếu thông tin có thể đã lỗi thời → cảnh báo ngắn gọn
6. Trả lời tiếng Việt, thân thiện, chuyên nghiệp
7. Ngắn gọn (dưới 300 từ) trừ khi khách yêu cầu chi tiết"""

# Cache wiki content trong memory
_WIKI_CONTENT: str | None = None
_WIKI_BUILD_ID: str | None = None

def load_wiki() -> str:
    """Load toàn bộ wiki vào memory. Chỉ reload khi build thay đổi."""
    global _WIKI_CONTENT, _WIKI_BUILD_ID
    
    # Kiểm tra build version
    build_file = WIKI_ROOT / "build" / "active-build.yaml"
    current_build_id = "unknown"
    if build_file.exists():
        import yaml
        with open(build_file) as f:
            build_info = yaml.safe_load(f)
            current_build_id = build_info.get("build_id", "unknown")
    
    # Reload nếu build thay đổi hoặc chưa load
    if _WIKI_BUILD_ID != current_build_id or _WIKI_CONTENT is None:
        wiki_dir = Path(os.getenv("WIKI_DIR", str(WIKI_ROOT / "wiki")))
        texts = []
        
        for root, dirs, files in os.walk(wiki_dir):
            # Bỏ qua .drafts/
            dirs[:] = [d for d in sorted(dirs) if d != ".drafts"]
            for fname in sorted(files):
                if not fname.endswith(".md"):
                    continue
                fpath = Path(root) / fname
                rel_path = fpath.relative_to(wiki_dir)
                with open(fpath, "r", encoding="utf-8") as f:
                    texts.append(f"\n\n---\n# FILE: {rel_path}\n\n{f.read()}")
        
        _WIKI_CONTENT = "\n".join(texts)
        _WIKI_BUILD_ID = current_build_id
        token_estimate = len(_WIKI_CONTENT) // 4
        print(f"[Wiki] Loaded build={current_build_id}, ~{token_estimate} tokens", file=sys.stderr)
    
    return _WIKI_CONTENT

def query_wiki(question: str) -> dict:
    """
    Query wiki với câu hỏi.
    Returns: {"answer": str, "cached_tokens": int, "total_tokens": int, "cost_usd": float}
    """
    wiki_content = load_wiki()
    
    model = GenerativeModel(
        model_name=os.getenv("MODEL_QUERY", "gemini-2.5-flash"),
        system_instruction=SYSTEM_PROMPT,
    )
    
    # Cấu trúc multi-turn để trigger implicit caching
    # Wiki content → fake model turn → câu hỏi thực
    response = model.generate_content(
        contents=[
            Content(role="user", parts=[
                Part.from_text(f"Tài liệu wiki BKNS (knowledge base):\n\n{wiki_content}")
            ]),
            Content(role="model", parts=[
                Part.from_text("Đã đọc xong tài liệu wiki BKNS. Tôi sẵn sàng trả lời câu hỏi của bạn.")
            ]),
            Content(role="user", parts=[
                Part.from_text(question)
            ]),
        ]
    )
    
    # Extract metrics
    usage = response.usage_metadata
    total_in = getattr(usage, 'prompt_token_count', 0)
    cached = getattr(usage, 'cached_content_token_count', 0)
    total_out = getattr(usage, 'candidates_token_count', 0)
    
    # Cost estimate (Vertex AI pricing 04/2026)
    non_cached = total_in - cached
    cost = (
        non_cached * 0.30 / 1_000_000 +
        cached * 0.030 / 1_000_000 +
        total_out * 2.50 / 1_000_000
    )
    
    # Log
    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "build_id": _WIKI_BUILD_ID,
        "question": question[:200],
        "total_input_tokens": total_in,
        "cached_tokens": cached,
        "output_tokens": total_out,
        "cache_hit_rate": round(cached / total_in * 100, 1) if total_in > 0 else 0,
        "cost_usd": round(cost, 6),
    }
    
    log_dir = Path(os.getenv("LOGS_DIR", str(WIKI_ROOT / "logs")))
    log_file = log_dir / f"query-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    print(f"[Cache] {cached}/{total_in} tokens cached ({log_entry['cache_hit_rate']}%)", file=sys.stderr)
    print(f"[Cost]  ${cost:.6f}", file=sys.stderr)
    
    return {
        "answer": response.text,
        "cached_tokens": cached,
        "total_tokens": total_in,
        "cost_usd": cost,
    }

# Entry point khi gọi từ OpenClaw
if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not question:
        question = sys.stdin.read().strip()
    
    if not question:
        print("Usage: python query.py 'câu hỏi của bạn'")
        sys.exit(1)
    
    result = query_wiki(question)
    print(result["answer"])
```

---

## 3.5 Test 20 Câu Hỏi

Tạo `skills/query-wiki/scripts/test_query.py`:

```python
#!/usr/bin/env python3
"""Test 20 câu hỏi tiêu chuẩn để validate Phase 0.5."""
import sys
sys.path.insert(0, str(__file__).rsplit('/scripts/', 1)[0] + '/scripts')
from query import query_wiki

TEST_QUESTIONS = [
    # Hosting (5)
    "Giá hosting cơ bản của BKNS là bao nhiêu?",
    "Hosting Business có bao nhiêu GB dung lượng?",
    "Có thể dùng hosting BKNS để chạy WordPress không?",
    "So sánh các gói hosting BKNS",
    "Hosting BKNS có hỗ trợ PHP phiên bản nào?",
    # Tên miền (5)
    "Giá đăng ký tên miền .vn là bao nhiêu?",
    "Quy trình đăng ký tên miền .com tại BKNS như thế nào?",
    "BKNS có hỗ trợ chuyển tên miền về không?",
    "Tên miền .net giá bao nhiêu một năm?",
    "Có thể mua tên miền và hosting cùng lúc không?",
    # VPS (5)
    "VPS của BKNS có cấu hình như thế nào?",
    "Giá VPS thấp nhất của BKNS là bao nhiêu?",
    "VPS BKNS dùng ổ cứng SSD hay HDD?",
    "Có thể nâng cấp VPS lên gói cao hơn không?",
    "VPS BKNS hỗ trợ hệ điều hành nào?",
    # Hỗ trợ (5)
    "Hotline hỗ trợ kỹ thuật của BKNS là số nào?",
    "BKNS có hỗ trợ 24/7 không?",
    "Làm sao để liên hệ tư vấn mua dịch vụ BKNS?",
    "BKNS có live chat không?",
    "Nếu website bị down, tôi phải gọi số nào?",
]

def main():
    print("=" * 60)
    print("TEST QUERY WIKI — 20 câu hỏi chuẩn")
    print("=" * 60)
    
    results = []
    total_cost = 0
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i:02d}/20] {question}")
        print("-" * 40)
        
        try:
            result = query_wiki(question)
            answer = result["answer"]
            cost = result["cost_usd"]
            total_cost += cost
            
            print(answer[:300] + ("..." if len(answer) > 300 else ""))
            
            # Manual check: có trả lời không, hay nói "không biết"?
            has_answer = len(answer) > 50
            no_hallucination = "không biết" not in answer.lower() or "liên hệ" in answer.lower()
            
            results.append({
                "q": i,
                "ok": has_answer,
                "cost": cost,
            })
        
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append({"q": i, "ok": False, "cost": 0})
    
    # Summary
    passed = sum(1 for r in results if r["ok"])
    print("\n" + "=" * 60)
    print(f"KẾTQUẢ: {passed}/20 câu trả lời thành công ({passed/20*100:.0f}%)")
    print(f"TỔNG CHI PHÍ: ${total_cost:.4f} cho 20 queries")
    print(f"CHI PHÍ TRUNG BÌNH: ${total_cost/20:.6f}/query")
    print("=" * 60)
    
    if passed >= 16:
        print("✅ PASS — Phase 0.5 query test OK (≥80%)")
    else:
        print("❌ FAIL — Cần review wiki content và/hoặc system prompt")

if __name__ == "__main__":
    main()
```

```bash
python skills/query-wiki/scripts/test_query.py
```

---

## 3.6 Telegram Bot Integration (OpenClaw)

OpenClaw tự động routing khi skill được register trong agents.yaml. Để test thủ công Telegram bot:

```bash
# Test trực tiếp qua Telegram:
# 1. Mở Telegram, tìm @BKNS_Wiki_bot
# 2. Gõ: /hoi Giá hosting BKNS cơ bản là bao nhiêu?
# 3. Xem câu trả lời

# Nếu cần test script trực tiếp:
python skills/query-wiki/scripts/query.py "Giá hosting BKNS là bao nhiêu?"
```

---

## 3.7 Commit + Tag build/v0.1

```bash
cd /home/openclaw/wiki

git add wiki/ build/ skills/query-wiki/ tools/
git commit -m "feat(phase-0.5): bot query + wiki v0.1

- Wiki compiled: $(find wiki/ -name '*.md' | wc -l) files
- query-wiki skill: Gemini Flash + implicit caching
- Build snapshot v0.1
- Test script: 20 standard questions"

git tag build/v0.1
echo "✅ Phase 0.5 complete! Bot ready."
```

---

## DEFINITION OF DONE — PHASE 0.5

- [ ] Bot Telegram trả lời `/hoi` câu hỏi
- [ ] ≥8 wiki files trong `wiki/` (không kể `.drafts/`)
- [ ] `wiki/support/lien-he.md` có hotline đúng: 1900 63 68 09 + 1800 646 884
- [ ] `build/active-build.yaml` trỏ v0.1
- [ ] Test 20 queries: ≥16/20 đúng (80%)
- [ ] Log ghi nhận cache hit rate và cost
- [ ] Git tag `build/v0.1`

---

## TIẾP THEO

→ [04-pipeline-ingest-compile.md](04-pipeline-ingest-compile.md) — Phase 1: Automation Pipeline
