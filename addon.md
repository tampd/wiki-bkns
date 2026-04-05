# addon.md — Design Spec đầy đủ cho Agent thủ thư OpenClaw và chuỗi Wiki dữ liệu BKNS

> **Vai trò của tài liệu này**  
> Đây không phải là tài liệu giới thiệu dự án, cũng không phải tài liệu vận hành bot theo ngày.  
> Đây là **design spec kiến trúc dữ liệu và luật quyết định** để toàn bộ hệ thống đi đúng mục tiêu dài hạn: **OpenClaw là công cụ điều phối; chuỗi Wiki dữ liệu BKNS mới là tài sản cốt lõi.**

**Trạng thái:** Draft để chuẩn hóa vào bộ tài liệu chính  
**Phạm vi:** Kiến trúc tri thức, schema, lifecycle, review gates, build system, query contract, observability  
**Đọc cùng với:** `README.md`, `bot.md`, `ytuongbandau.md`

---

## 0. Tóm tắt điều hành

BKNS đang đi đúng hướng khi chọn mô hình **LLM-Compiled Wiki + OpenClaw + Gemini** để xây dựng một knowledge base sống thay vì chỉ dựng một chatbot trả lời câu hỏi. Tuy nhiên, ở trạng thái hiện tại, hệ thống vẫn còn một khoảng trống kiến trúc quan trọng:

- Markdown đang bị dùng vừa như **nguồn sự thật**, vừa như **bản hiển thị**, vừa như **prefix context**.
- Nguồn dữ liệu đã đa dạng (web, ảnh, file, note, hợp đồng, câu trả lời bot), nhưng luật quyết định **nguồn nào thắng nguồn nào** chưa được đóng thành schema và state machine.
- `draft/review`, `lint`, `cross-link`, `auto-file`, `cron` và `human-in-the-loop` đã được mô tả, nhưng chưa có một tài liệu khóa chặt khái niệm **đơn vị tri thức gốc**.

Tài liệu này giải quyết khoảng trống đó bằng một kiến trúc trung gian:

```text
raw -> extraction -> claims -> resolve/review -> compile wiki -> build packs -> query -> filing -> lint/ground truth
```

Điểm cốt lõi của spec này là:

1. **Claims mới là lớp sự thật gốc; Markdown là lớp trình bày đã biên dịch.**
2. **OpenClaw không được giữ logic dữ liệu cốt lõi bên trong workflow riêng; logic dữ liệu phải nằm ở schema và policy độc lập.**
3. **Mọi fact nhạy cảm phải có trạng thái, nguồn, thời điểm hiệu lực và review state.**
4. **Bot trả lời theo build snapshot và context pack xác định, không theo một biến `wiki_content` mơ hồ.**
5. **Filing ngược về wiki phải đi qua rule engine, không phải cứ “trả lời hay” là nhập thẳng vào knowledge base.**

---

## 1. Vai trò của addon.md trong bộ tài liệu

### 1.1. Phân vai giữa các tài liệu

- `README.md`: mô tả dự án là gì, mục tiêu, công nghệ chính, cấu trúc repo mức cao.
- `bot.md`: mô tả bot hoạt động ra sao, command, workflow, cron, phân quyền, review pattern.
- `ytuongbandau.md`: mô tả lý do chọn kiến trúc, research, roadmap, chi phí, mô hình multi-agent, các phase triển khai.
- `addon.md`: khóa các **luật kiến trúc**, **schema**, **cơ chế biên dịch tri thức**, **state machine**, **policy quyết định**.

### 1.2. Những gì addon.md phải trả lời

1. Đâu là **đơn vị tri thức gốc** của toàn hệ thống?
2. Dữ liệu đi từ `raw/` đến `wiki/` qua những lớp nào?
3. Nguồn nào có quyền overwrite tự động, nguồn nào bắt buộc review?
4. Khi hai nguồn mâu thuẫn nhau thì quyết định theo luật nào?
5. Một câu trả lời của bot có thể được file ngược vào hệ thống hay không, dưới điều kiện nào?
6. Query đang trả lời dựa trên build nào, pack nào, claim nào?
7. Làm thế nào để thay OpenClaw trong tương lai mà vẫn giữ nguyên tài sản tri thức?

### 1.3. Những gì addon.md không nên lặp lại

- Toàn bộ Telegram command cụ thể.
- Giải thích dài về vì sao không dùng RAG.
- Toàn bộ lịch cron chi tiết từng giờ.
- Toàn bộ hướng dẫn cài Git, Git LFS, mkdocs.

Tài liệu này là **hiến pháp dữ liệu** của dự án, không phải handbook vận hành hằng ngày.

---

## 2. Tuyên ngôn kiến trúc

```markdown
OpenClaw không phải đích đến.
OpenClaw là lớp điều phối để thu nhận, biên dịch, kiểm tra và phục vụ tri thức.
Tài sản cốt lõi của dự án là chuỗi Wiki dữ liệu BKNS có nguồn gốc rõ ràng,
được cập nhật được, audit được, rollback được, và tái sử dụng được qua nhiều kênh.
```

### 2.1. Nguyên tắc cốt lõi

1. **Data-first, bot-second**  
   Bot có thể thay; dữ liệu chuẩn hóa không nên phụ thuộc vào một bot cụ thể.

2. **Claims trước prose**  
   Fact phải được ghi nhận ở dạng có cấu trúc trước khi được biên dịch thành văn bản Markdown.

3. **Provenance-first**  
   Mỗi fact quan trọng phải truy về được nguồn, thời gian quan sát, trạng thái review và bằng chứng.

4. **Deterministic build**  
   Query phải biết mình đang trả lời trên build snapshot nào, thay vì đọc một state mơ hồ trong RAM.

5. **Risk-based automation**  
   Tự động hóa mạnh cho việc ít rủi ro; bắt buộc human review cho dữ liệu nhạy cảm.

6. **Orchestrator-agnostic**  
   Schema tri thức không được khóa cứng vào riêng OpenClaw. OpenClaw chỉ là công cụ thực thi workflow.

7. **Human-readable + machine-auditable**  
   Wiki phải dễ đọc cho con người, còn claims/logs/manifest phải đủ cấu trúc cho máy kiểm tra.

---

## 3. Bức tranh kiến trúc mục tiêu

```text
Nguồn dữ liệu
  ├─ website BKNS
  ├─ ảnh bảng giá / screenshot
  ├─ file nội bộ / hợp đồng / PDF
  ├─ note admin
  └─ câu hỏi và câu trả lời thực tế

        ↓ intake

raw/
  ├─ stored assets
  ├─ metadata
  └─ intake logs

        ↓ extraction / normalization

claims/
  ├─ claim drafts
  ├─ approved claims
  ├─ superseded claims
  └─ conflict records

        ↓ compile

wiki/
  ├─ human-readable markdown
  ├─ index / backlinks / faq / sales / policies
  └─ compiled views, not source-of-truth

        ↓ build

build/
  ├─ manifests
  ├─ pack definitions
  ├─ active build pointer
  └─ answer traces

        ↓ query

OpenClaw / bot / viewer / internal tools

        ↓ filing / feedback / lint

feedback -> claims/.drafts -> review -> next build
```

### 3.1. Hệ quả của kiến trúc này

- `wiki/` không còn là nơi duy nhất chứa sự thật gốc.
- `claims/` trở thành lớp trung gian để lint, conflict detection, freshness tracking và rollback hoạt động đúng.
- `build/` tách runtime query ra khỏi quy trình compile.
- `bot.md` mô tả bot làm gì; `addon.md` mô tả dữ liệu nào được bot quyền đụng tới và theo luật nào.

---

## 4. Mô hình dữ liệu chuẩn (Canonical Data Model)

## 4.1. Đối tượng cốt lõi

Hệ thống chuẩn hóa quanh 10 đối tượng:

1. `Source`
2. `Entity`
3. `Evidence`
4. `Claim`
5. `Conflict`
6. `ReviewDecision`
7. `WikiPage`
8. `BuildManifest`
9. `PackManifest`
10. `AnswerTrace`

---

## 4.2. Source

### 4.2.1. Mục đích

`Source` đại diện cho nguồn gốc mà từ đó dữ liệu được lấy ra. Một source có thể là:

- trang chính sách trên BKNS.vn
- trang bảng giá sản phẩm
- hợp đồng / phụ lục / file pháp lý
- ảnh chụp bảng giá
- note nội bộ
- transcript cuộc trao đổi nội bộ

### 4.2.2. Schema tối thiểu

```yaml
source_id: web.bkns.hosting.pricing
kind: official_product_page
canonical_title: Bang gia hosting BKNS
owner: BKNS
url: https://www.bkns.vn/...
authority_level: 3
freshness_sla_days: 7
default_review_gate: high_risk
capture_method: crawl
captured_at: 2026-04-04T12:10:00+07:00
hash_sha256: <content hash>
notes:
status: active
```

### 4.2.3. Luật

- Mọi claim phải trỏ về ít nhất một `source_id`.
- `kind`, `authority_level`, `freshness_sla_days` là bắt buộc.
- Nếu source là ảnh/screenshot, phải kèm `Evidence` tương ứng.

---

## 4.3. Entity

### 4.3.1. Mục đích

`Entity` chuẩn hóa các đối tượng mà BKNS wiki nói đến. Ví dụ:

- công ty BKNS
- hotline chính thức
- gói hosting BKCP01
- dòng VPS MMO
- chính sách hoàn tiền
- SLA uptime
- dịch vụ email doanh nghiệp

### 4.3.2. Schema tối thiểu

```yaml
entity_id: product.hosting.bkcp01
entity_type: product_plan
canonical_name: BKCP01
aliases:
  - hosting BKCP01
  - goi BKCP01
belongs_to:
  - category.hosting
status: active
labels:
  - pricing_sensitive
  - customer_facing
```

### 4.3.3. Luật

- Mọi claim quan trọng phải gắn `entity_id`.
- `canonical_name` là tên được dùng khi compile wiki và khi bot trích nguồn.
- `aliases` chỉ phục vụ linking và query normalization, không được xem là source-of-truth.

---

## 4.4. Evidence

### 4.4.1. Mục đích

`Evidence` là bản ghi về bằng chứng trực quan hoặc tệp gốc phục vụ audit lại fact.

### 4.4.2. Schema tối thiểu

```yaml
evidence_id: evi.price.hosting.q2_2026.sha256_xxx
kind: image
original_path: assets/evidence/price-screens/bang-gia-hosting-2026q2-original.png
thumbnail_path: assets/images/bang-gia-hosting-2026q2.png
source_id: image.telegram.hosting.q2_2026
captured_at: 2026-04-04T14:32:00+07:00
extracted_by: bkns-vision-worker
hash_sha256: <file hash>
ocr_or_vision_status: extracted
human_verified: false
```

### 4.4.3. Luật

- Evidence không tự động là claim.
- Evidence chỉ trở thành claim sau bước extraction.
- Claim nhạy cảm đi từ ảnh phải có `human_verified` hoặc review bắt buộc.

---

## 4.5. Claim

### 4.5.1. Định nghĩa

`Claim` là đơn vị tri thức gốc có cấu trúc, có nguồn, có thời gian, có trạng thái.

### 4.5.2. Schema tối thiểu

```yaml
claim_id: product.hosting.bkcp01.monthly_price.2026-04-04T14-35-00+07-00
entity_id: product.hosting.bkcp01
attribute: monthly_price
value: 26000
unit: VND
qualifiers:
  billing_cycle: month
  tax_included: unknown
source_ids:
  - web.bkns.hosting.pricing
  - image.telegram.hosting.q2_2026
evidence_refs:
  - evi.price.hosting.q2_2026.sha256_xxx
observed_at: 2026-04-04T14:35:00+07:00
valid_from: 2026-04-04
valid_to:
confidence: high
review_state: approved
freshness_state: fresh
supersedes:
superseded_by:
compiler_note: extracted from pricing row BKCP01
risk_class: high
```

### 4.5.3. Trường bắt buộc

- `claim_id`
- `entity_id`
- `attribute`
- `value`
- `source_ids`
- `observed_at`
- `review_state`
- `risk_class`

### 4.5.4. Trường khuyến nghị

- `valid_from`, `valid_to`
- `qualifiers`
- `evidence_refs`
- `confidence`
- `freshness_state`
- `supersedes`, `superseded_by`

### 4.5.5. Thuộc tính nên chuẩn hóa thành claim riêng

- giá bán
- chu kỳ thanh toán
- thông số RAM / CPU / SSD / bandwidth
- hotline / email hỗ trợ / địa chỉ liên hệ
- chính sách hoàn tiền / SLA / thời gian hỗ trợ
- domain pricing / renewal fee / transfer fee
- trạng thái sản phẩm active/deprecated

### 4.5.6. Những gì không nên là claim đơn lẻ

- đoạn mô tả marketing dài
- câu văn bán hàng
- outline FAQ hoàn chỉnh
- cảm nhận / diễn giải của model

Những phần đó nên nằm ở `wiki/`, `sales/`, `faq/` hoặc `playbooks/` sau khi compile.

---

## 4.6. Conflict

### 4.6.1. Định nghĩa

`Conflict` tồn tại khi hai hoặc nhiều claim cùng nói về một `entity_id + attribute` nhưng khác `value` hoặc khác `qualifier` một cách không hòa giải được.

### 4.6.2. Schema tối thiểu

```yaml
conflict_id: conflict.product.hosting.bkcp01.monthly_price.2026-04-04
entity_id: product.hosting.bkcp01
attribute: monthly_price
claim_ids:
  - claim_a
  - claim_b
status: needs_review
suspected_cause: source_mismatch
opened_at: 2026-04-04T15:00:00+07:00
resolved_by:
resolved_at:
resolution_note:
```

### 4.6.3. Luật

- Conflict không được resolve bằng việc LLM tự chọn bừa một claim.
- Khi conflict chưa resolve, compile vẫn có thể chạy nhưng page hoặc answer phải gắn cờ phù hợp.
- Nếu conflict chạm dữ liệu high-risk, pack query tương ứng phải giảm mức khẳng định và ưu tiên fallback.

---

## 4.7. ReviewDecision

```yaml
review_id: review.2026-04-04.price.hosting.001
target_type: claim
target_id: product.hosting.bkcp01.monthly_price.2026-04-04T14-35-00+07-00
reviewer: admin.telegram.12345
decision: approved
reason: matched official website and evidence image
reviewed_at: 2026-04-04T15:10:00+07:00
```


---

## 4.8. WikiPage

`WikiPage` là kết quả compile từ claims + prose bổ trợ.

### 4.8.1. Frontmatter tối thiểu

```yaml
---
page_id: wiki.products.hosting.bang-gia
title: Bang gia Hosting BKNS
category: products/hosting
build_source: build-2026-04-04-01
compiled_from_claims:
  - claim_a
  - claim_b
  - claim_c
updated: 2026-04-04
review_state: compiled
sensitivity: high
---
```

### 4.8.2. Luật

- `compiled_from_claims` phải truy ngược được.
- Page không phải source-of-truth.
- Nếu page có prose suy luận hoặc tư vấn, phần đó phải được đánh dấu loại nội dung riêng.

---

## 4.9. BuildManifest

### 4.9.1. Mục đích

`BuildManifest` định nghĩa snapshot tri thức được kích hoạt cho query.

### 4.9.2. Schema tối thiểu

```yaml
build_id: build-2026-04-04-01
created_at: 2026-04-04T16:00:00+07:00
created_by: bkns-orchestrator
claims_hash: sha256:...
wiki_hash: sha256:...
source_snapshot_hash: sha256:...
pack_ids:
  - core-pack
  - hosting-pack
  - support-pack
status: active
parent_build_id: build-2026-04-03-03
lint_summary:
  syntax_passed: true
  semantic_passed: true
  unresolved_high_risk_conflicts: 0
activation_note: weekly publish
```

### 4.9.3. Luật

- Chỉ một build có `status: active`.
- Query log phải lưu `build_id`.
- Rollback chỉ đổi active build, không xóa build cũ.

---

## 4.10. PackManifest

### 4.10.1. Mục đích

`PackManifest` định nghĩa một gói context biên dịch sẵn cho query.

### 4.10.2. Schema tối thiểu

```yaml
pack_id: hosting-pack
build_id: build-2026-04-04-01
includes:
  - wiki/company/*.md
  - wiki/products/hosting/*.md
  - wiki/support/lien-he.md
  - wiki/faq/hosting.md
excludes:
  - wiki/products/email/**
max_tokens_target: 120000
selection_rules:
  intents:
    - hosting_pricing
    - hosting_plan_selection
sensitivity: mixed
status: active
```

### 4.10.3. Luật

- Pack chỉ tham chiếu content thuộc một build cụ thể.
- Pack phục vụ deterministic context assembly, không phải vector retrieval.

---

## 4.11. AnswerTrace

### 4.11.1. Mục đích

`AnswerTrace` là bản ghi giúp audit một câu trả lời của bot.

### 4.11.2. Schema tối thiểu

```yaml
answer_id: ans-2026-04-04-0001
asked_at: 2026-04-04T16:15:00+07:00
channel: telegram
user_class: admin_or_customer
question_text: Gói BKCP01 giá bao nhiêu?
build_id: build-2026-04-04-01
pack_id: hosting-pack
claim_refs:
  - product.hosting.bkcp01.monthly_price.2026-04-04T14-35-00+07-00
response_sensitivity: high
had_conflict_warning: false
had_fallback: false
model_runtime: google/gemini-2.5-flash
cached_prefix: true
cost_estimate_usd: 0.0021
autofile_candidate: false
```

---

## 5. Cấu trúc thư mục mục tiêu

```text
/home/openclaw/wiki/
├── README.md
├── bot.md
├── ytuongbandau.md
├── addon.md                         # tài liệu này sau khi chính thức hóa
│
├── wiki/                            # compiled human-readable knowledge
│   ├── index.md
│   ├── company/
│   ├── products/
│   ├── support/
│   ├── sales/
│   ├── technical/
│   ├── faq/
│   ├── policies/
│   ├── onboarding/
│   └── .drafts/
│
├── raw/                             # intake layer
│   ├── website-crawl/
│   ├── uploads/
│   ├── screenshots/
│   ├── contracts/
│   ├── internal-notes/
│   └── manifests/
│
├── claims/                          # source-of-truth structured facts
│   ├── .drafts/
│   ├── approved/
│   ├── superseded/
│   ├── rejected/
│   └── conflicts/
│
├── entities/
│   └── registry.yaml
│
├── sources/
│   └── registry.yaml
│
├── build/
│   ├── manifests/
│   ├── packs/
│   ├── active-build.yaml
│   └── traces/
│
├── assets/
│   ├── images/
│   └── evidence/
│
└── logs/
    ├── intake/
    ├── compile/
    ├── lint/
    ├── query/
    └── metrics/
```

### 5.1. Quy tắc phân vai thư mục

- `raw/`: lưu dữ liệu nhận vào, chưa là tri thức chính thức.
- `claims/`: lưu fact có cấu trúc; đây là lớp sự thật gốc.
- `wiki/`: lưu tri thức đã biên dịch cho người đọc và cho pack builder.
- `build/`: lưu snapshot runtime cho query.
- `assets/`: lưu evidence/media.
- `logs/`: lưu hành vi hệ thống, không chứa source-of-truth.

---

## 6. Lifecycle và State Machine

## 6.1. Claim lifecycle

```text
received -> extracted -> drafted -> needs_review -> approved
                                └-> rejected
approved -> superseded
approved -> stale_candidate
approved -> conflict_opened
```

### 6.1.1. Ý nghĩa trạng thái

- `received`: raw đã được tiếp nhận.
- `extracted`: hệ thống đã trích ra claim candidate.
- `drafted`: claim đã có cấu trúc nhưng chưa vào review.
- `needs_review`: chờ duyệt.
- `approved`: được xem là dùng được để compile.
- `rejected`: claim sai, không dùng.
- `superseded`: claim cũ nhưng vẫn giữ để audit lịch sử.
- `stale_candidate`: claim chưa chắc sai nhưng quá hạn verify.
- `conflict_opened`: claim chạm conflict với claim khác.

### 6.1.2. Luật chuyển trạng thái

- Claim high-risk không được từ `drafted` sang `approved` nếu không có `ReviewDecision`.
- Claim low-risk có thể auto-approve nếu vượt qua rule engine và không có conflict.
- Claim approved khi bị thay thế bởi claim mới không bị xóa; chỉ chuyển `superseded`.

---

## 6.2. Build lifecycle

```text
assembling -> syntax_check -> semantic_check -> candidate -> active
candidate -> rejected
active -> archived
active -> rolled_back_to_previous
```

### 6.2.1. Luật

- Build chỉ thành `candidate` khi compile hoàn tất.
- Build chỉ thành `active` khi pass tối thiểu: syntax, semantic, zero unresolved critical conflict.
- Rollback là thay `active-build.yaml`, không biên dịch lại lịch sử.

---

## 6.3. Answer lifecycle

```text
question_received -> pack_selected -> answered -> traced
traced -> autofile_candidate
traced -> no_action
autofile_candidate -> reviewed -> filed_or_rejected
```

---

## 7. Source Authority Ladder

### 7.1. Thang quyền lực nguồn đề xuất

```yaml
source_authority:
  - level: 1
    kind: signed_contract_or_legal_doc
    overwrite_policy: manual_only
  - level: 2
    kind: official_policy_page
    overwrite_policy: manual_only
  - level: 3
    kind: official_product_page
    overwrite_policy: draft_then_review
  - level: 4
    kind: official_support_contact_page
    overwrite_policy: draft_then_review
  - level: 5
    kind: official_evidence_image
    overwrite_policy: draft_then_review
  - level: 6
    kind: internal_note
    overwrite_policy: never_direct
  - level: 7
    kind: inferred_by_model
    overwrite_policy: prohibited
```

### 7.2. Luật bắt buộc

1. Model inference không bao giờ là nguồn gốc.
2. Ảnh là evidence; chỉ trở thành fact sau extraction và review tương ứng.
3. Giá, hotline, SLA, điều khoản, hoàn tiền, chính sách dữ liệu là **high-risk**.
4. Nguồn mới hơn không tự động thắng nguồn authority cao hơn.
5. Source level chỉ là một chiều đánh giá; quyết định cuối cùng còn phụ thuộc `valid_from`, `valid_to`, `freshness_state`.

---

## 8. Risk classes và Review Gates

## 8.1. Risk classes

```yaml
risk_classes:
  low:
    examples: [typo, backlink, index update, metadata formatting]
  medium:
    examples: [faq wording, product description rewrite, cross-link suggestion]
  high:
    examples: [pricing, hotline, sla, support flow, legal policy, specs]
  critical:
    examples: [delete page, change authority rules, change answer contract, change review gates]
```

## 8.2. Review gates

```yaml
review_gates:
  low:
    action: auto_merge_allowed
  medium:
    action: draft_then_review
  high:
    action: manual_approval_required
  critical:
    action: admin_only
```

### 8.2.1. Luật

- `low`: bot được phép tự áp dụng và commit.
- `medium`: bot tạo draft, người duyệt trước khi publish.
- `high`: bot chỉ được tạo claim/page draft, không được publish thẳng.
- `critical`: chỉ admin sửa.

---

## 9. Freshness Policy

### 9.1. Mục tiêu

Freshness policy ngăn hệ thống trả lời chắc chắn bằng fact có khả năng đã lỗi thời.

### 9.2. Chính sách mẫu

```yaml
freshness_policy:
  pricing:
    verify_every_days: 7
    answer_behavior_if_stale: warn
  hotline:
    verify_every_days: 30
    answer_behavior_if_stale: warn
  legal_policy:
    verify_every_days: 30
    answer_behavior_if_stale: warn
  technical_specs:
    verify_every_days: 30
    answer_behavior_if_stale: cautious
  company_profile:
    verify_every_days: 180
    answer_behavior_if_stale: neutral
  sales_playbook:
    verify_every_days: 30
    answer_behavior_if_stale: neutral
```

### 9.3. Luật

- Stale không có nghĩa là sai; chỉ có nghĩa là cần verify.
- Claim stale vẫn có thể compile, nhưng answer contract phải điều chỉnh theo `answer_behavior_if_stale`.
- Lint phải sinh danh sách `stale_candidate` ưu tiên theo risk class.

---

## 10. Conflict Resolution Policy

### 10.1. Khi nào mở conflict

Mở conflict khi có ít nhất một trong các điều kiện:

- cùng `entity_id + attribute`, khác `value`
- cùng `entity_id + attribute`, cùng `value` nhưng khác qualifier quan trọng
- alias ambiguity khiến hai claim có thể đang nói về hai thực thể khác nhau
- OCR/vision extract nghi ngờ sai và làm lệch fact high-risk

### 10.2. Nguyên nhân sơ bộ

```yaml
suspected_causes:
  - source_mismatch
  - time_window_difference
  - entity_alias_ambiguity
  - extraction_error
  - outdated_source
  - incomplete_qualifier
```

### 10.3. Luật resolve

1. Không resolve bằng “cái nào nghe hợp lý hơn”.
2. Cố gắng quy chiếu về:
   - authority level
   - thời điểm hiệu lực
   - qualifier đầy đủ
   - entity mapping đúng
3. Nếu vẫn không resolve được:
   - giữ conflict mở
   - compile page với note phù hợp
   - answer phải cảnh báo hoặc fallback

### 10.4. Hành vi query khi gặp conflict

- Nếu conflict low-risk: trả lời có note “cần kiểm tra thêm”.
- Nếu conflict high-risk: không khẳng định một giá trị duy nhất nếu chưa có approved resolution.
- Nếu conflict critical: ưu tiên hướng dẫn liên hệ kênh chính thức.

---

## 11. Compile Policy: từ claims sang wiki

### 11.1. Nguyên tắc compile

1. Chỉ claim `approved` mới được compile vào page chính thức.
2. Claim `stale_candidate` có thể compile, nhưng page phải mang note hoặc metadata cảnh báo.
3. Claim `needs_review` không được compile vào page chính thức; chỉ vào draft.
4. Một page phải truy ngược được đến claim set dùng để compile.

### 11.2. Phân loại nội dung khi compile

Mỗi đoạn trong wiki nên được xem là một trong các loại:

- `fact_table`
- `summary_from_claims`
- `interpretation`
- `sales_guidance`
- `faq_entry`
- `related_links`

### 11.3. Rule cứng cho LLM compiler

```text
- Không tạo fact mới nếu fact đó không tồn tại trong claims hoặc source được cung cấp.
- Không hợp nhất hai claim mâu thuẫn thành một câu văn trơn tru.
- Không biến sales phrasing thành policy.
- Không điền chỗ trống bằng suy luận khi thiếu số liệu.
- Nếu cần diễn giải, phải đánh dấu loại nội dung là interpretation hoặc guidance.
```

---

## 12. Build Manifest và snapshot activation

### 12.1. Vì sao không chỉ dùng `wiki_content reload`

`wiki_content reload` phù hợp để khởi đầu, nhưng không đủ cho vận hành lâu dài vì:

- không truy vết được query đang dùng snapshot nào
- khó rollback an toàn
- khó đo cache hit theo phiên bản tri thức
- dễ xảy ra trạng thái nửa build cũ nửa build mới

### 12.2. Cơ chế đề xuất

1. Compile claims thành wiki.
2. Tạo `BuildManifest`.
3. Sinh các `PackManifest`.
4. Pass tối thiểu syntax/semantic checks.
5. Activate build bằng cách cập nhật `build/active-build.yaml`.
6. Query service chỉ đọc từ active build.

### 12.3. Mẫu `active-build.yaml`

```yaml
active_build_id: build-2026-04-04-01
activated_at: 2026-04-04T16:20:00+07:00
previous_build_id: build-2026-04-03-03
reason: weekly publish approved by admin
```

---

## 13. Pack Builder và deterministic context assembly

### 13.1. Quan điểm

Dự án có thể tiếp tục giữ tinh thần “không vector DB mặc định”, nhưng không nên buộc mọi query phải dùng đúng một prefix khổng lồ duy nhất.

### 13.2. Mục tiêu của pack

- giảm kích thước prefix không cần thiết
- tăng cache hit theo nhóm intent
- giữ full-context theo miền thay vì chunk search
- cho phép scale dần mà chưa phải nhảy sang RAG

### 13.3. Các pack gợi ý ban đầu

- `core-pack`: company + support + nguyên tắc chung
- `hosting-pack`: hosting + faq hosting + contact liên quan
- `domain-pack`: tên miền + VNNIC context + faq domain
- `vps-pack`: vps/cloud + specs + support liên quan
- `email-pack`: email doanh nghiệp + FAQ
- `ssl-pack`: ssl + FAQ + advisory
- `legal-pack`: sla + terms + refund + privacy
- `sales-pack`: playbooks + objection handling + product comparison

### 13.4. Luật chọn pack

```yaml
pack_selection:
  by_intent:
    hosting_pricing: hosting-pack
    domain_pricing: domain-pack
    support_contact: core-pack
    policy_question: legal-pack
    sales_objection: sales-pack
  fallback_order:
    - core-pack
    - domain-specific-pack
```

### 13.5. Rule runtime

- Một answer phải log `pack_id`.
- Nếu intent classifier không chắc, có thể ghép `core-pack + domain-pack`.
- Không được trộn content từ build khác nhau vào cùng một response.

---

## 14. Answer Contract

### 14.1. Mục tiêu

Cố định hình dạng tối thiểu của câu trả lời để model thay đổi vẫn không làm thay đổi tiêu chuẩn chất lượng.

### 14.2. Contract

```yaml
answer_contract:
  must_include:
    - direct_answer
    - source_reference
  must_include_when_sensitive:
    - verification_state
    - caution_if_applicable
  must_include_when_missing_data:
    - explicit_unknown
    - safe_fallback
  forbidden:
    - fabricated_price
    - unsupported_policy_claim
    - pretending_certainty_with_open_conflict
```

### 14.3. Mẫu hành vi

**Trường hợp đủ dữ liệu, không conflict**

```markdown
Theo `products/hosting/bang-gia.md` trong build `build-2026-04-04-01`, gói BKCP01 đang được ghi là 26.000đ/tháng.
Thông tin này thuộc nhóm giá nên nên kiểm tra lại nếu bạn cần chốt đơn ngay hôm nay.
```

**Trường hợp stale**

```markdown
Theo `support/lien-he.md`, hotline đang được ghi là ... Tuy nhiên thông tin này đang ở trạng thái cần xác minh lại.
Nếu bạn cần liên hệ ngay, nên kiểm tra trang liên hệ chính thức của BKNS.
```

**Trường hợp conflict**

```markdown
Tôi đang thấy hai nguồn nội bộ chưa khớp về mức giá của BKCP01, nên chưa thể khẳng định chắc một con số duy nhất.
Bạn nên kiểm tra trang giá hiện hành hoặc hotline chính thức để chốt thông tin mới nhất.
```

---

## 15. Auto-file Policy

### 15.1. Quan điểm

Tinh thần Karpathy về filing là đúng, nhưng filing phải đi vào **đúng lớp dữ liệu**.

Không phải mọi câu trả lời hay đều được nhập thẳng vào wiki.

### 15.2. Phân loại autofile

1. `faq_candidate`
2. `sales_candidate`
3. `factual_candidate`
4. `no_action`

### 15.3. Rule engine đề xuất

```yaml
autofile_rules:
  faq_candidate:
    conditions:
      min_repeat_count: 3
      min_admin_rating: 4
    destination: wiki/.drafts/faq/
  sales_candidate:
    conditions:
      min_admin_rating: 4
      no_policy_language: true
    destination: wiki/.drafts/sales/
  factual_candidate:
    conditions:
      requires_evidence: true
      requires_claim_extraction: true
    destination: claims/.drafts/
  no_action:
    conditions:
      default: true
```

### 15.4. Luật

- FAQ tái sử dụng đi vào `wiki/.drafts/faq/`.
- Sales phrasing đi vào `wiki/.drafts/sales/`.
- Fact mới phát hiện đi vào `claims/.drafts/`, không vào wiki thẳng.
- Không biến lời trấn an khách hàng thành policy.

---

## 16. Query Runtime Policy

### 16.1. Runtime inputs bắt buộc

Một request query phải xác định được:

- `build_id`
- `pack_id` hoặc tổ hợp pack
- `model_runtime`
- `answer_contract_version`

### 16.2. Runtime outputs bắt buộc

- text response
- source refs
- claim refs (nếu log nội bộ)
- trace log
- cache usage (nếu thu được)

### 16.3. Không được phép

- dùng file draft cho khách hàng cuối nếu chưa có rule đặc biệt
- dùng active build A nhưng pack của build B
- trả lời chắc chắn về high-risk fact khi `review_state` chưa approved

---

## 17. Provider Binding Matrix

### 17.1. Vì sao cần

Dự án đang gắn ngân sách và logic chi phí với một runtime/billing path cụ thể. Phần này phải được khai báo chính thức, không được “ngầm hiểu”.

### 17.2. Schema mẫu

```yaml
provider_bindings:
  bkns-orchestrator:
    runtime_provider: google
    runtime_model: google/gemini-2.5-pro
    billing_path: unverified
    quota_bucket: compile_and_lint
    verified: false
  bkns-flash-worker:
    runtime_provider: google
    runtime_model: google/gemini-2.5-flash
    billing_path: unverified
    quota_bucket: query_and_extract
    verified: false
  bkns-vision-worker:
    runtime_provider: google
    runtime_model: google/gemini-2.5-flash
    billing_path: unverified
    quota_bucket: vision_extract
    verified: false
```

### 17.3. Luật

- Không chốt dự toán chính thức khi `billing_path` chưa verified.
- Mỗi agent phải có `runtime_provider`, `runtime_model`, `billing_path`, `quota_bucket`.
- Thay đổi provider phải là change thuộc gate `critical`.

---

## 18. SDK / Dependency Policy

### 18.1. Mục tiêu

Tránh để bộ tài liệu chính thức lỗi thời quá nhanh vì SDK hoặc import path thay đổi.

### 18.2. Rule

```markdown
- Mọi ví dụ code chính thức phải ghi rõ ngày xác minh và SDK version.
- Mã mới không nên phụ thuộc vào package hoặc module đã bị deprecate nếu đã có hướng thay thế rõ ràng.
- Tài liệu nghiên cứu và tài liệu vận hành phải cùng một chuẩn SDK/runtime naming.
- Việc đổi SDK chính là thay đổi cấp medium hoặc high tùy phạm vi tác động.
```

### 18.3. Volatile assumptions

Các thứ sau đây không được hardcode như chân lý bền vững trong kiến trúc:

- model IDs
- provider paths
- pricing
- cached discount
- TTL cache
- import path / SDK package
- rate limits / quotas

Nên giữ các thông tin này trong một khối `volatile_assumptions` hoặc `runtime_assumptions.md` để dễ kiểm tra định kỳ.

---

## 19. Observability và Metrics

### 19.1. Mục tiêu

Dự án không chỉ cần bot trả lời được; nó cần đo chất lượng tri thức và sức khỏe chuỗi wiki.

### 19.2. Chỉ số đề xuất

```yaml
metrics:
  grounding_rate:
    description: percent answers with valid source refs
  stale_fact_rate:
    description: percent sensitive answers using stale claims
  conflict_exposure_rate:
    description: percent answers touching unresolved conflicts
  claim_approval_latency:
    description: avg time from extraction to approval
  build_success_rate:
    description: percent builds activated successfully
  cache_hit_rate:
    description: percent queries with cached prefix hit
  autofile_acceptance_rate:
    description: percent autofile candidates later approved
  cost_per_resolved_question:
    description: monthly cost divided by accepted answers
  source_coverage_rate:
    description: percent critical entities with at least one approved source-backed claim
```

### 19.3. Dashboard tối thiểu

Mỗi tuần nên xem được:

- số claim mới
- số claim approved / rejected / stale
- số conflict mở
- số build candidate / active / rollback
- top stale high-risk facts
- grounding rate
- cache hit rate
- top câu hỏi chưa được hệ thống trả lời chắc chắn

---

## 20. Workflow chi tiết

## 20.1. Workflow: ingest URL / web page

```text
Admin gửi URL
  -> OpenClaw ingest
  -> raw/website-crawl/
  -> tạo Source record
  -> extraction thành claim drafts
  -> classify entity mapping
  -> nếu medium/high risk -> review queue
  -> approved claims -> compile -> build candidate
```

### Luật

- URL crawl không được ghi thẳng vào wiki chính thức.
- Phải tạo `Source` trước khi tạo `Claim`.
- Nếu crawl page là official policy/pricing, risk class mặc định phải là high.

---

## 20.2. Workflow: ingest image / screenshot

```text
Nhận ảnh Telegram
  -> lưu original vào assets/evidence/
  -> tạo Evidence record
  -> vision extract
  -> claim drafts
  -> human review if pricing/policy/support
  -> approved claims
  -> compile page draft / page update
```

### Luật

- Không publish giá từ ảnh nếu chưa qua review.
- Nếu extract có ô mờ / merged cell / ambiguity, phải đánh dấu `confidence: low`.
- Image ingestion chủ yếu sinh `claim drafts`, không sửa wiki trực tiếp.

---

## 20.3. Workflow: compile wiki

```text
Select approved claims
  -> group by entity/category
  -> compile summary/table/page
  -> add backlinks/index updates
  -> generate page draft
  -> run syntax + semantic checks
  -> build candidate
```

### Luật

- Compile chỉ dùng approved claims của cùng snapshot.
- Cross-link suggestions là low/medium risk, có thể auto-apply tùy rule.
- Page produced phải mang `compiled_from_claims`.

---

## 20.4. Workflow: query

```text
Question
  -> classify intent
  -> choose build + pack
  -> answer using active build only
  -> log AnswerTrace
  -> optionally mark autofile candidate
```

### Luật

- Không query trực tiếp `raw/` trừ chế độ admin/debug.
- Không dùng claim draft cho user-facing answers.
- Câu trả lời phải theo answer contract.

---

## 20.5. Workflow: lint / ground truth

```text
Schedule or manual trigger
  -> syntax check
  -> semantic check
  -> stale scan
  -> conflict scan
  -> source freshness scan
  -> ground truth compare for critical entities
  -> report + issue queue + optional build block
```

### Luật

- Lint không được tự thay fact high-risk nếu chưa review.
- Ground truth mismatch với pricing/support/legal phải tạo conflict hoặc stale alert.

---

## 20.6. Workflow: rollback

```text
Admin selects previous build
  -> switch active-build.yaml
  -> record rollback reason
  -> new queries serve previous build
```

### Luật

- Rollback build không được xóa artifacts của build mới.
- Nếu rollback do data corruption, phải mở incident note.

---

## 21. Quality gates trước khi publish build

## 21.1. Bắt buộc

- syntax check pass
- semantic check pass
- không có unresolved critical conflict
- không có page lỗi frontmatter
- active build pointer hợp lệ

## 21.2. Nên có

- stale high-risk facts dưới ngưỡng cho phép
- source coverage cho core entities đạt ngưỡng
- grounding test set đạt ngưỡng mục tiêu

### 21.3. Mẫu ngưỡng khởi đầu

```yaml
release_thresholds:
  max_unresolved_critical_conflicts: 0
  max_unresolved_high_risk_conflicts: 3
  min_grounding_rate: 0.90
  min_source_coverage_rate_core_entities: 0.85
```

---

## 22. Mapping sang các tài liệu chính

## 22.1. README.md cần phản chiếu gì

- đổi ngôn ngữ từ `wiki_content reload` sang `build snapshot + pack activation`
- nhấn mạnh wiki chain là tài sản, bot là interface
- bổ sung thư mục `claims/`, `sources/`, `entities/`, `build/`

## 22.2. bot.md cần phản chiếu gì

- workflow ingest-image phải sinh `claim drafts`
- `/duyet` phải duyệt claim/page/build tương ứng
- query log phải lưu `build_id`, `pack_id`, `answer_id`
- auto-file phải phân biệt FAQ / sales / factual candidate

## 22.3. ytuongbandau.md cần phản chiếu gì

- pipeline 6 giai đoạn nên được mở rộng theo lớp claim/build
- mọi cost estimate gắn với `billing_path verified`
- compile prompt phải có rule “no new facts outside claims/sources”

---

## 23. Definition of Done theo phase

## 23.1. Phase 1 Done khi

- có `Source Registry`
- có `Entity Registry` tối thiểu cho company, hosting, domain, support contact
- có `Claim` schema và claim drafts hoạt động
- high-risk claims bắt buộc review trước khi vào wiki
- query log ghi `build_id`
- có ít nhất `core-pack`, `hosting-pack`, `domain-pack`

## 23.2. Phase 1.5 Done khi

- auto-file phân nhánh được vào FAQ / sales / factual candidate
- build manifest và active build chạy thật
- có dashboard tuần tối thiểu

## 23.3. Phase 2 Done khi

- ingest-image sinh claim drafts ổn định
- conflict detection hoạt động cho pricing/specs/contact
- policy/support/legal có pack riêng
- rollback build được thử nghiệm

## 23.4. Phase 3 Done khi

- sales playbooks và onboarding đi qua cùng schema governance
- viewer cho con người đọc wiki thuận tiện
- metrics đủ để quyết định health của chuỗi wiki hằng tuần

---

## 24. Những quyết định nên khóa ngay

### Quyết định 1

**Markdown không phải lớp sự thật gốc; claims mới là lớp sự thật gốc.**

### Quyết định 2

**OpenClaw không được phép trở thành nơi giam logic dữ liệu.**

Workflow có thể chạy bằng OpenClaw, nhưng schema, policy, authority ladder, build manifest phải tồn tại độc lập trong repo dữ liệu.

### Quyết định 3

**Mọi fact nhạy cảm phải có trạng thái, không chỉ có nội dung.**

Ví dụ giá không chỉ là “26.000đ”, mà còn phải có:

- observed_at
- source_ids
- review_state
- freshness_state
- risk_class
- valid_from / valid_to nếu biết

---

## 25. Danh sách quyết định còn mở

```yaml
open_decisions:
  - entity_id naming convention co can them namespace version hay khong
  - claims luu dang yaml tung file hay jsonl append-only
  - viewer nen dung mkdocs hay obsidian-first
  - build activation la git tag, symlink hay active-build.yaml
  - query runtime cach luu trace o file hay database nhe
  - ground truth compare muc nao can web verify tu dong
```

---

## 26. Phụ lục A — Ví dụ tối thiểu cho một cụm tri thức giá hosting

```text
Source:
  web.bkns.hosting.pricing
  image.telegram.hosting.q2_2026

Evidence:
  evi.price.hosting.q2_2026.sha256_xxx

Entity:
  product.hosting.bkcp01

Claim drafts:
  product.hosting.bkcp01.monthly_price.2026-04-04
  product.hosting.bkcp01.disk_gb.2026-04-04

Review:
  admin approves monthly_price and disk_gb

Compile:
  wiki/products/hosting/bang-gia.md updated

Build:
  build-2026-04-04-01 becomes active

Query:
  answer uses hosting-pack on build-2026-04-04-01
```

---

## 27. Phụ lục B — Mẫu pseudo-rules cho compiler

```text
INPUT:
- approved claims only
- entity registry
- page templates

RULES:
- Group claims by entity/category
- Prefer tables for numeric claims
- Prefer short summary paragraphs for descriptive claims
- Add source note for sensitive sections
- Refuse to synthesize unsupported numbers
- Preserve unresolved conflicts as warnings, not silent merges
```

---

## 28. Web Data Portal — Intake Interface qua Web (Bổ sung 2026-04-05)

> **Trạng thái**: 📋 Design — chờ phê duyệt

### 28.1. Bối cảnh

Hệ thống hiện tại intake dữ liệu qua 3 kênh:
1. `crawl-source` → `raw/website-crawl/` (bị Cloudflare block)
2. CLI copy → `raw/manual/` (cần SSH access)
3. Telegram → `ingest-image` (chỉ ảnh)

**Thiếu**: Kênh upload web cho file đa định dạng (PDF, DOCX, XLSX, MD, TXT).

### 28.2. Vị trí trong kiến trúc

```text
Nguồn dữ liệu (mới)
  └─ Web Portal upload (PDF/DOCX/XLSX/MD/TXT)

        ↓ intake (POST /api/upload)

raw/web/{date}/
  ├─ {uuid}-{filename}
  └─ metadata.jsonl    ← upload audit log

        ↓ extraction / normalization (trigger thủ công hoặc auto)

claims/ → wiki/ → build/ → query
```

### 28.3. Luật intake qua web

1. File upload qua web chỉ được ghi vào `raw/web/`, **KHÔNG** vào `claims/` hay `wiki/` trực tiếp.
2. Mỗi upload PHẢI có metadata record: `source_channel: "web"`, `uploader`, `timestamp`, `file_hash`.
3. Pipeline trigger sau upload là **optional** — admin quyết định khi nào chạy.
4. File types cho phép: `.pdf`, `.docx`, `.xlsx`, `.md`, `.txt` (whitelist, không blacklist).
5. Max file size: 50MB per file.
6. Auth: Bearer token (env ADMIN_TOKEN). Không cho phép anonymous upload.
7. Upload metadata tuân thủ Source schema (section 4.2) với `kind: web_upload`.

### 28.4. Source registration tự động

Mỗi file upload tạo một Source record:

```yaml
source_id: web.upload.{date}.{uuid}
kind: web_upload
canonical_title: "{original_filename}"
owner: admin
url: null
authority_level: 6  # internal_note equivalent
freshness_sla_days: 30
default_review_gate: medium
capture_method: web_upload
captured_at: "{ISO timestamp}"
hash_sha256: "{file hash}"
status: active
```

---

## 29. Phụ lục C — Mẫu câu chốt để đặt cuối tài liệu

```markdown
Tài liệu này tồn tại để ngăn dự án đi lệch thành một chatbot biết nhiều.
Đích đến không phải là một bot trả lời được nhiều câu hỏi hơn.
Đích đến là một chuỗi Wiki dữ liệu BKNS ngày càng đầy đủ, có quản trị,
để nhiều bot, nhiều kênh và nhiều con người có thể cùng dùng chung một nền tri thức đáng tin cậy.
```


