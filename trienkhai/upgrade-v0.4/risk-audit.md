---
part: 01
artifact: risk-audit
status: complete
created: 2026-04-13
---

# 🛡️ Risk Audit — Upgrade v0.4

> Đánh giá rủi ro trước khi chuyển từ Gemini 2.5 Pro (đơn) → Gemini 3.1 Pro + GPT-5.4 (vote) + markitdown ingestion.

---

## 1. Code surface phải chạm

| File | LoC | Vai trò | Risk | Mức độ | PART chạm |
|---|---|---|---|---|---|
| [lib/gemini.py](../../lib/gemini.py) | 676 | Wrapper Vertex AI cho Gemini, có generate / generate_with_cache / generate_with_image / explicit cache | API surface đã PRICING ghi sẵn `gemini-3.1-pro-preview` ($2/$0.20/$12) — chỉ cần đổi `MODEL_PRO` env. **Risk thấp.** | 🟢 | 04 |
| [skills/extract-claims/scripts/extract.py](../../skills/extract-claims/scripts/extract.py) | 751 | Extract claims từ markdown, gọi `MODEL_PRO` qua `lib.gemini.generate()` ở line 274 | Prompt template hiện tune cho 2.5 Pro. Risk: 3.1 Pro có thể thay đổi format JSON output (verbose hơn / strict hơn). **Cần A/B test 5 raw files trước rollout.** | 🟡 | 04 |
| [skills/compile-wiki/scripts/compile.py](../../skills/compile-wiki/scripts/compile.py) | 910 | Compile claims → wiki page + self-review (line 681 generate, 794 self-review) | Self-review prompt phụ thuộc khả năng "chỉ trích chính mình" của model. 3.1 Pro reasoning mạnh hơn → có thể quá nghiêm khắc → false-positive blocks. **Theo dõi block rate.** | 🟡 | 04 |
| [tools/convert_manual.py](../../tools/convert_manual.py) | ~400 | Chuyển DOCX (mammoth) + PDF (pdfminer) → MD | Sẽ thay engine bằng markitdown. Risk: format frontmatter có thể đổi → break extract pipeline downstream. **Bắt buộc dual-write giai đoạn pilot.** | 🟠 | 02, 03 |
| [.env](../../.env) | 11 keys | Chứa `MODEL_PRO=gemini-2.5-pro` | Cần thêm `OPENAI_API_KEY`, `OPENAI_MODEL`, có thể cần `MODEL_PRO_FALLBACK` để rollback nhanh | 🟢 | 04, 05 |
| [lib/config.py](../../lib/config.py) | — | Định nghĩa `SKILL_MODELS` mapping skill → model | Nếu thêm dual-vote, có thể cần `SKILL_MODELS_VOTE` với 2 model | 🟡 | 06 |

---

## 2. Tương thích SDK

- ✅ `google.genai.types.Part.from_text(text=...)` — signature đã verify, dùng keyword-only `text=` đúng cú pháp SDK mới (genai >= 1.0).
- ✅ `client.models.generate_content(model=..., contents=..., config=...)` — pattern mới của SDK, không phải `GenerativeModel(...).generate_content(...)` cũ → đã chuyển đổi rồi.
- ✅ `client.caches.create(model=..., config=CreateCachedContentConfig(...))` — explicit caching đã hoạt động → 3.1 Pro hỗ trợ caching cùng pattern.
- ⚠️ `gemini-3.1-pro-preview` là **preview** model — có thể bị Vertex deprecate / đổi tên. Phải sẵn sàng pin version cụ thể nếu Google công bố GA.

---

## 3. Pipeline state risks

| Trạng thái hiện tại | Rủi ro khi nâng cấp | Mitigation |
|---|---|---|
| 2,252 claims approved (immutable) | Không bị ảnh hưởng — chỉ build mới chạm | Snapshot v0.3 đã lock read-only |
| 1,495 drafts pending | Re-extract bằng 3.1 có thể tạo claim_id khác → mất link với draft cũ | PART 03 phải giữ deterministic claim_id (hash trên content, không trên model) |
| 213 wiki pages | Compile lại bằng 3.1 → output sẽ khác hoàn toàn | Dual-write `wiki/` + `wiki-v04/` trong giai đoạn pilot, diff trước khi swap |
| Bot live tại upload.trieuphu.biz | Bot đọc `wiki/` trực tiếp → swap = downtime | PART 08 dùng atomic symlink swap (`wiki -> wiki-v04`) |
| Cumulative cost $35.77 (5 ngày) | Build v0.4 sẽ tốn nhiều hơn (2 model) | Cost guard $20 hard-cap (Bước 5) |

---

## 4. Failure modes mới được giới thiệu

### 4.1 Dual-vote conflict resolution
- **Risk**: Nếu Gemini 3.1 và GPT-5.4 bất đồng > 30% claims → human review backlog tăng đột biến
- **Mitigation**: PART 06 phải có ngưỡng auto-flag rõ ràng; nếu disagree-rate > 25%, trigger circuit breaker → fallback về single-model

### 4.2 markitdown format drift
- **Risk**: markitdown có thể sinh markdown khác cấu trúc heading so với mammoth → category-detection fail
- **Mitigation**: PART 02 pilot trên 3 file representative (1 docx, 1 pdf, 1 xlsx), so sánh AST với output cũ

### 4.3 OpenAI rate-limit / 429
- **Risk**: Free/Tier-1 OpenAI có rate-limit thấp → batch của 213 pages compile có thể block
- **Mitigation**: PART 05 implement exponential-backoff + concurrent limit ≤ 4

### 4.4 API key leakage
- **Risk**: OPENAI_API_KEY trong `.env` có thể bị commit nhầm
- **Mitigation**: `.env` đã trong `.gitignore` — verify ở PART 05; thêm pre-commit hook detect `sk-*` pattern

### 4.5 Self-review over-triggering
- **Risk**: 3.1 Pro reasoning mạnh hơn → block rate có thể tăng từ baseline (1/7 categories trong v0.3 — xem L002)
- **Mitigation**: PART 07 đo block-rate, nếu > 30% → tune temperature hoặc nới SELF_REVIEW_RULES

---

## 5. Rollback readiness

| Tình huống | Cách rollback | Thời gian |
|---|---|---|
| 3.1 Pro fail | `MODEL_PRO=gemini-2.5-pro` trong `.env`, restart pipeline | < 1 phút |
| markitdown break extract | Revert `tools/convert_manual.py` (git revert PART 03 commit) | < 5 phút |
| Dual-vote conflict bùng nổ | Set env `DUAL_VOTE_ENABLED=false`, single-model resume | < 1 phút |
| Wiki output lỗi | Restore từ `build/snapshots/v0.3-pre-upgrade-2026-04-13/` (xem MANIFEST.yaml) | < 10 phút |
| Bot đọc nhầm wiki rỗng | Atomic symlink swap về `wiki-v03-backup/` | < 30 giây |

---

## 6. Go/No-go criteria cho từng PART

- **PART 02 → 03**: pilot 3 file phải có diff < 5% so với output mammoth (cấu trúc heading)
- **PART 04 → 06**: 3.1 Pro extract test-set phải accuracy ≥ 95% so với baseline
- **PART 06 → 07**: dual-vote disagree-rate ≤ 15% trên test-set
- **PART 07 → 08**: regression suite (5 page + 20 claim trong test-set) phải pass 100%
- **PART 08 production**: cost build thực ≤ $12 (target), hard-cap $15; bot smoke-test trả đúng 5/5 câu hỏi

---

## 7. Kết luận audit

🟢 **GO** — Có thể triển khai PART 02-08 theo thứ tự với điều kiện:
1. Mỗi PART chạy trong branch riêng `upgrade-v0.4-partXX`
2. Dual-write toàn bộ output trong PART 03-06
3. Cost guard $15 alert / $20 hard-cap (Bước 5 đang setup thủ công ngoài Cloud Console)
4. Mỗi PART end-to-end test trên test-set.yaml trước khi merge

Risk tổng thể: **Trung bình thấp**. Code architecture (lib/gemini, SKILL_MODELS) đã sẵn sàng cho việc swap model. Phần lo nhất là markitdown format drift và dual-vote conflict — cần PART 02 + PART 06 thiết kế cẩn thận.
