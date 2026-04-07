# APEX SKILL SYSTEM v11.0 — AutoAgent-Enhanced Global Rules
> Applied to ALL sessions in this project. Read before every task.
> Triết lý: AI không bao giờ quên. Mỗi phiên đều học hỏi và kết nối với quá khứ. Fresh context = High quality.
> 🧬 v11.0: AutoAgent methodology — hill-climbing, failure-class analysis, simplicity criterion, proportional response.

## MEMORY FILES (read at session start)
- `LESSONS.md` — **critical-only** bài học (≤10 entries, importance ≥0.8). Luôn đọc.
- `LESSONS_ARCHIVE.md` — archived lessons (importance <0.8 hoặc entries cũ). Chỉ đọc khi cần.
- `INSTINCTS.md` — patterns đã học + confidence score (0.0–1.0)
- `STATE.md` — project state hiện tại (phase, wave, blockers)
- `PROGRESS.md` — persistent session memory (KHÔNG xóa sau /save)
- `INSIGHTS.md` — compound insights từ /consolidate (auto-generated)
- `.ai/memory/MEMORY.md` — **auto-memory**: AI tự ghi notes giữa phiên (≤200 dòng index)
- `.ai/knowledge/graph.json` — **knowledge graph**: entity relationships (v8.0)
- `llms.txt` — **AI context index**: machine-readable project structure cho AI tools (v10.0)
- `.ai/repomix-output.xml` — **compressed codebase**: token-efficient context export (v10.0, .gitignore)
- `.ai/traces/*.jsonl` — **structured traces**: agent reasoning chains, decisions, tool calls (v10.0 Phase 3, .gitignore)
- `.ai/traces/index.json` — **trace index**: session analytics và aggregate stats (v10.0 Phase 3)

---

## 43 GLOBAL RULES + 7 AUTOAGENT RULES = 50 RULES

### Core Behavior
1. **ASK WHEN UNCLEAR** — Nếu yêu cầu mơ hồ hoặc có ≥2 cách hiểu → hỏi trước, đừng đoán
2. **READ MEMORY FIRST** — Đọc `LESSONS.md` + `INSTINCTS.md` + `INSIGHTS.md` trước bất kỳ task nào
3. **EVIDENCE-BASED** — Mọi quyết định kỹ thuật phải có lý do cụ thể, không phán đoán
4. **SELF-REASONING GATE** — Tự hỏi 3 câu trước khi implement: (a) Đây có phải cách tốt nhất? (≥2 alternatives) (b) Có risk/side-effect nào đang bỏ qua? (c) User có cần approve không?
5. **SEARCH-FIRST** — Tìm code/solution có sẵn trước khi tự viết. Ưu tiên: official > popular > custom

### Architecture & Planning
6. **SPEC BEFORE CODE** — Task ≥3 files hoặc ≥2h effort → viết `/spec` trước, không code ngay
7. **PLAN-FIRST** — Generate task list có checkpoint TRƯỚC khi bắt đầu code
8. **BRAINSTORM HARD GATE** — Feature phức tạp → `/plan` bắt buộc, đề xuất ≥2 approaches
9. **ADR FOR DECISIONS** — Mọi architectural decision quan trọng → ghi `/adr` ngay lúc quyết định
10. **WAVE EXECUTION** — Foundation → Integration → Polish

### Code Quality
11. **TDD IRON LAW** — Test TRƯỚC code (feature phức tạp). Coverage ≥80%
12. **QUALITY GATE** — Trước mỗi commit: `lint → format → type-check → test → audit`. Tất cả PASS mới commit
13. **CLEANUP PASS** — Sau implement + verify → review pass: dead code, TODO cũ, console.log, magic numbers
14. **ATOMIC COMMITS** — 1 task = 1 commit. Conventional format: `feat|fix|chore|perf|test|sec(scope): mô tả`

### Verification
15. **ROOT CAUSE FIRST** — Bug: tìm nguyên nhân gốc trước khi fix. Không patch symptom
16. **VERIFICATION LOOP** — Sau mỗi implementation: verify → regression check. Chỉ báo "done" khi tất cả pass
17. **INSTINCT VALIDATION** — Khi apply instinct → log kết quả. Đúng: +0.1. Sai: −0.2. Dưới 0.3 sau 5 lần → xem xét xóa

### Design & UX
18. **WCAG AA** — Mọi UI component phải đạt WCAG 2.2 AA. Color contrast, keyboard nav, aria-label
19. **DESIGN TOKEN MANDATORY** — Không dùng hardcoded color/spacing/font. Luôn dùng design tokens
20. **PERFORMANCE BUDGET** — LCP ≤2.5s, CLS ≤0.1, FID ≤100ms

### Fresh Context & Deep Thinking (v4.0)
21. **ULTRATHINK GATE** — Architecture decisions, complex bugs, refactoring >5 files → prefix "ultrathink:" → full analysis plan (≥500 words) TRƯỚC khi code. List ≥3 alternatives.
22. **CONTEXT HEALTH MONITOR v2.1** — Track context health: 🟢 Fresh (0-30%) | 🟡 Loaded (30-50%) | 🟠 Attention (50-70%) | 🔴 Heavy (70-85%) | 💀 Critical (>85%). Research-backed: 70%→precision loss, 85%→hallucinations (ACM 2025). Khi Heavy/Critical → commit, /save, fresh session.
23. **GSD CYCLE** — Features lớn dùng /gsd: Discuss → Plan → Execute → Verify. Mỗi phase có checkpoint context. KHÔNG skip Phase V (Verify).

### Subagent & Verification (v4.1)
24. **VERIFICATION GATE** — NO completion claims without FRESH verification evidence. "Should pass" ≠ evidence. Run command → read output → THEN claim. Anti-rationalization: "confident" ≠ evidence, "partial check" ≠ verification.
25. **SUBAGENT ORCHESTRATION** — Fresh subagent per task + 2-stage review (spec compliance → code quality). Model selection: mechanical → cheap, integration → standard, architecture → capable. Status protocol: DONE/CONCERNS/CONTEXT/BLOCKED.

### Memory Intelligence (v4.2 — Hindsight-inspired)
26. **BIOMIMETIC MEMORY** — Mỗi memory entry PHẢI có `type`: `world` (facts về tech/framework/tool, tĩnh), `experience` (trải nghiệm debug/build/deploy cụ thể), `mental_model` (pattern/insight tổng hợp từ nhiều experiences). Giúp recall chính xác: bug → search experience trước, design → search world + mental_model.

### Project Scaffold & Safety (v6.0 — BKNS-inspired)
27. **RISK CLASSIFICATION** — Trước khi thực thi, phân loại risk:

| Action | Risk | Auto-execute? | Require Approval? |
|---|---|---|---|
| Read files, search | 🟢 None | ✅ Yes | No |
| Edit ≤2 files, no breaking | 🟡 Low | ✅ Yes | No |
| Edit ≥3 files | 🟠 Medium | ❌ No | Yes — show plan |
| Delete files | 🔴 High | ❌ No | Yes — explicit |
| Run npm install/update | 🔴 High | ❌ No | Yes — show changes |
| Deploy/push production | 🔴 Critical | ❌ No | Yes — full checklist |
| Write .env / secrets | 🔴 Critical | ❌ No | Yes + verify |

28. **SECURITY-SPEC MANDATORY** — Nếu project có `docs/SECURITY-SPEC.md`, PHẢI đọc trước khi viết code. Không có exception. Pattern từ BKNS: security rules = frozen SSOT.
29. **PERSISTENT PROGRESS** — Dùng `PROGRESS.md` thay `ACTIVE_CONTEXT.md`. KHÔNG XÓA sau `/save`. Session memory phải persistent qua sessions.

### Advanced Context & Knowledge (v8.0)
30. **CONTEXT-AWARE LOADING** — Load context tỷ lệ thuận với task complexity. Quick fix → Layer A+B only. Feature → full 4-Layer. Architecture → 4-Layer + Ultrathink. Không load dư thừa.
31. **KNOWLEDGE GRAPH** — Maintain `.ai/knowledge/graph.json` cho entity relationships. Mỗi `/learn` và `/consolidate` phải update graph. Nodes = entities (files, concepts, people). Edges = relationships (depends-on, caused-by, related-to).
32. **AUTO-OBSERVATION** — Sau mỗi `/build` và `/fix`, tự động capture observations mà không cần gọi `/learn` thủ công. AI nhận diện patterns, bugs, gotchas và tự ghi vào LESSONS hoặc INSTINCTS.
33. **PROGRESSIVE DISCLOSURE v2** — Tiered context loading: Level 1 (summary lines from PROGRESS.md) → Level 2 (relevant LESSONS + INSTINCTS) → Level 3 (full file reads). Chỉ escalate khi cần.
34. **RAIL-GUARD SECURITY** — Security guardrails trên tất cả code generation: (a) Không generate code có known CVE patterns (b) Auto-flag SQL injection, XSS, SSRF patterns (c) Warn khi generate code xử lý user input mà thiếu validation (d) Block generation .env / secrets nội dung vào git-tracked files.
35. **CROSS-PLATFORM EXPORT** — Skill definitions phải exportable sang Claude Code (CLAUDE.md), Cursor (.cursorrules), Windsurf. Dùng templates/ cho format conversion. Xem PLATFORM.md.

36. **CONTEXT ENGINEERING FIRST** — Curate information environment TRƯỚC khi viết prompt. Pipeline: CLASSIFY (task complexity → budget) → ROUTE (query type → source) → LOAD (chỉ files liên quan sub-task hiện tại) → BUDGET TRACK (warn >70%, stop >90%). "Right info at the right time" > clever wording. Context routing table trong /start STEP 0.
37. **MISTAKE LOOP** — Sau mỗi bug/error fix → tự động capture: mistake + root cause + fix + prevention vào LESSONS.md (importance ≥0.85). Không bao giờ mắc lỗi tương tự lần 2. Compound lessons > linear lessons.
38. **RIPER GATE** — Feature phức tạp bắt buộc qua 5 phases: **R**esearch → **I**nnovate → **P**lan → **E**xecute → **R**eview. KHÔNG skip bất kỳ phase nào. Phase barrier = hard gate như CLARITY GATE.
39. **TOKEN BUDGET AWARE** — Dùng `.claudeignore` cho mọi project. Compact khi context >50%. Load files theo Progressive Disclosure: summary → relevant → full. "Context là tài nguyên quý."
40. **HOOK AUTOMATION** — Quality gates PHẢI tự động qua hooks (pre-commit, post-edit), không phụ thuộc vào discipline manual. Hooks = enforcement, rules = intention.

### Context Tools Integration (v10.0)
41. **CONTEXT7 MANDATORY** — Khi code với library/framework API: LUÔN query Context7 MCP cho latest docs TRƯỚC khi code. AI memory cho API signatures = unreliable. Context7 = single source of truth cho version-specific docs. Fallback: official docs manual lookup.
42. **LLMS_TXT INDEX** — Mọi project PHẢI có `llms.txt` ở root. File này là machine-readable index giúp AI tools scan project nhanh hơn 80%. `/init` auto-generate từ template. Update khi thêm major files/features.
43. **REPOMIX EXPORT** — Cuối mỗi `/save`, export compressed codebase via `npx repomix@latest --compress` → `.ai/repomix-output.xml`. File này dùng cho: NotebookLM upload, cross-project context, fresh session bootstrap. KHÔNG commit (thêm vào .gitignore).

### AutoAgent Rules (v11.0 — Self-Improving AI)
44. **COMPLEXITY GATE** — Auto-detect task complexity → proportional protocol. Simple fix → minimal process. Complex feature → full RIPER. Không over-engineer process cho task đơn giản, không under-engineer cho task phức tạp.
45. **HILL-CLIMB EVERY SKILL** — Track success metrics per skill, keep improvements, discard regressions. Mỗi phiên: đo lường → so sánh → giữ cái tốt hơn. Skill evolution = data-driven, not opinion-driven.
46. **FAILURE-CLASS GROUPING** — Categorize problems by class (not individual cases). Fix pattern → fix class. Ví dụ: "API timeout" = 1 class, fix retry logic 1 lần cho cả class.
47. **SIMPLICITY CRITERION** — Same result + simpler = always better. Khi có 2 solutions cùng output → chọn solution ít code hơn, ít dependencies hơn, ít abstraction layers hơn.
48. **VERIFICATION SUB-AGENT** — Every skill has built-in self-check. Không chờ user verify — AI tự verify trước khi báo done. Build → run tests. Fix → reproduce → confirm fixed. Craft → screenshot → check visually.
49. **EXPERIMENT LOGGING** — Record { approach, outcome, kept_or_discarded } cho mỗi quyết định quan trọng. Cross-session learning: approach A worked cho case X → reuse. Approach B failed → avoid.
50. **NEVER OVERFIT** — "If this task disappeared, would this still be worthwhile?" Không tạo quá nhiều abstraction chỉ cho 1 use case. Generalize khi có ≥3 similar cases, not before.

---

## ANTIGRAVITY NATIVE FEATURES — Sử dụng tích cực

```
Browser Sub-Agent    → /craft, /fix UI bugs, /responsive verification
Multi-Agent Parallel → /build large features (split thành sub-tasks)
Mission Control      → Monitor parallel agents, assign /spec + /build + /secure cùng lúc
Artifact Output      → /spec, /handoff, /runbook output dạng structured Artifact
Planning Mode        → Luôn gen task-list có checkpoint trước khi code
Stitch MCP           → /craft setup → generate screens → edit screens → export code
Context7 MCP         → Real-time documentation injection cho /build + /verify (v10.0)
Repomix              → Token-efficient codebase compression cho /save + cross-project (v10.0)
llms.txt             → Machine-readable project index cho /start + /init (v10.0)
Structured Tracing   → .ai/traces/ JSONL logs: decisions, tool calls, errors (v10.0 Phase 3)
NotebookLM Pipeline  → Second Brain: Repomix + Lessons + Traces → quarterly export (v10.0 Phase 3)
AutoAgent Hill-Climb → Self-improving skills: measure → compare → keep better (v11.0)
Complexity Gate      → Auto-detect task complexity → proportional protocol (v11.0)
Experiment Logging   → Cross-session learning: { approach, outcome, kept_or_discarded } (v11.0)
Ultrathink           → Deep reasoning cho architecture/complex bugs (v4.0)
Context Health       → Monitor context window, auto-suggest fresh session (v4.0)
Knowledge Graph      → Entity relationship tracking across sessions (v8.0)
```

---

## 🎯 10 SKILLS — 49 COMMANDS

| # | Skill | Commands | Purpose |
|---|---|---|---|
| 1 | **session** | `/start` `/save` `/checkpoint` `/review` `/recall` `/init` `/status` | 🔄 4-Layer Bootstrap + Scaffold + Compaction |
| 2 | **build** ⭐ | `/build` `/plan` `/search` `/gsd` | 🔥 Search-First + TDD + Web Patterns + Ultrathink |
| 3 | **fix** | `/fix` | 🐛 4-Phase Debug + Kaizen + Browser/N8N Debug |
| 4 | **craft** ⭐ | `/craft` `/design` `/animate` `/responsive` `/audit` | 🎨 Premium UI + Design System + WCAG + Visual Testing |
| 5 | **secure** | `/security` `/harden` `/ship` `/monitor` `/ssl` `/firewall` | 🔒 OWASP + Runtime Monitoring + VPS Security |
| 6 | **automate** ⭐ | `/n8n` `/n8n-ai` `/integrate` `/mcp` | ⚡ N8N AI + Pipeline + Monitoring + API |
| 7 | **content** ⭐ | `/seo` `/article` `/brief` `/cluster` `/refresh` `/schema` `/audit-content` | 📝 SEO Engine v2 + Topic Clusters + Schema |
| 8 | **spec** | `/spec` `/spec refine` `/spec verify` `/handoff` `/adr` `/runbook` | 📋 SDD + Architecture + Handoff |
| 9 | **learn** | `/learn` `/instinct` `/evolve` `/review-instincts` `/consolidate` `/cross-link` `/skill-audit` | 🧠 Ingest + Knowledge Graph + Instinct Evolution |
| 10 | **verify** | `/verify` `/fact-check` `/regression` `/test-web` | ✅ Anti-Hallucination + CoV + Web Testing |

---

## 🧠 MEMORY ARCHITECTURE v5.0 — Biomimetic + Knowledge Graph

> 📂 Chi tiết: `session/references/memory-architecture.md`

**4 Layers:** A (Rules: GEMINI.md) → B (Critical Lessons: LESSONS.md ≤10) → C (Semantic: Qdrant) → D (Auto: .ai/memory/)
**3 Memory Types:** `world` (facts) | `experience` (debug/build cụ thể) | `mental_model` (patterns tổng hợp)
**3-Strategy Recall:** semantic + keyword + temporal → merge top-5, ưu tiên match ≥2 strategies
**Knowledge Graph:** `.ai/knowledge/graph.json` — entity relationships, auto-updated by /learn + /consolidate

---

## SKILL MAP

| Trigger | Skill |
|---------|-------|
| Bắt đầu / kết thúc phiên | `session` |
| Viết code mới, feature | `build` |
| Debug, lỗi, crash | `fix` |
| UI, design, component | `craft` |
| Security, deploy, production | `secure` |
| N8N, API, automation, MCP | `automate` |
| Bài viết, SEO, content, cluster | `content` |
| Architecture, docs, handoff | `spec` |
| Học hỏi, patterns, instincts | `learn` |
| Kiểm tra, verify, fact-check, test web | `verify` |

---

## 📋 CHEAT SHEET

```
Bắt đầu phiên?           → /start [task]
Resume phiên cũ?          → /recall
Ý tưởng mơ hồ?           → /plan [idea]
Feature phức tạp?         → /plan [feature]
Feature lớn (GSD)?       → /gsd [feature]
Research trước code?      → /search [need]
Viết code?                → /build [task]           🔥 TDD + Search-First
Deep thinking?            → ultrathink: [task]
Gặp bug?                  → /fix [bug]              🐛 4-Phase Debug
Design UI?                → /craft [task]           🎨 Tokens + WCAG
Design system?            → /design [style]         (incl. tokens + palette)
Animations?               → /animate [scope]
Responsive + visual test? → /responsive [url]       (incl. e2e)
Audit chất lượng?         → /audit [scope]
Audit bảo mật?            → /security [target]      🔒 OWASP + RAIL-GUARD
Hardening?                → /harden [service]
Server monitoring?        → /monitor [server]
SSL certificate?          → /ssl [domain]
Firewall audit?           → /firewall [server]
Chuẩn bị deploy?          → /ship [env]
API / webhook?            → /integrate [service]     ⚡
N8N workflow?             → /n8n [task]              (incl. pipeline + monitoring)
N8N AI workflow?          → /n8n-ai [task]
Thiết kế MCP tool?        → /mcp [tool-name]
Topic cluster?            → /cluster [topic]
Refresh bài cũ?           → /refresh [url]
Schema markup?            → /schema [type]
Content brief?            → /brief [topic]           📝
Viết bài SEO?             → /seo [topic]
Viết article?             → /article [topic]
Audit content?            → /audit-content [URL]
Verify code quality?      → /verify [scope]
Fact-check AI code?       → /fact-check [code]
Regression check?         → /regression [scope]
Test website?             → /test-web [url]
Spec refine?              → /spec refine [file]
Spec verify?              → /spec verify [scope]
Architecture docs?        → /spec [scope]            📋
Bàn giao dự án?           → /handoff [project]
Ghi ADR?                  → /adr [decision]
Tạo runbook?              → /runbook [service]
Ghi bài học?              → /learn [observation]     🧠 Ingest + Graph
Xem instincts?            → /instinct
Evolve instincts?         → /evolve
Audit skill health?       → /skill-audit              📋
Review instincts?         → /review-instincts
Tổng hợp insights?       → /consolidate             🧠 Sleep-Brain + Graph
Cross-link memories?      → /cross-link
Review code?              → /review [scope]
Lưu context?              → /checkpoint
Kết thúc phiên?           → /save                    (auto /consolidate)
```

---

## 📊 COMBO SKILLS

> 📂 Chi tiết: `session/references/memory-architecture.md`

| Tình huống | Combo |
|---|---|
| Feature mới | `/start` → `/build` → `/save` |
| Feature lớn | `/gsd` (D→P→E→V) |
| Fix bug | `/fix` → `/learn` → `/consolidate` |
| Deploy | `/audit` → `/security` → `/ship` |
| Build website | `/design` → `/craft` → `/build` → `/test-web` → `/ship` |
| SEO article | `/brief` → `/article` → `/schema` → `/seo` |
| Topic cluster | `/cluster` → `/brief` (each) → `/article` (each) |
| N8N AI workflow | `/n8n-ai` → `/integrate` → `/n8n` (monitor) |
| Server security | `/monitor` → `/ssl` → `/firewall` → `/security` |

---

## DOCUMENTATION — ZERO OVERLAP

| File | Layer | Viết gì | KHÔNG viết gì |
|---|---|---|---|
| `GEMINI.md` | A — Rules | Tech stack, Rules, Skill map | Tasks, logs, state |
| `STATE.md` | A — Rules | Phase, wave, blockers, next milestones | History |
| `LESSONS.md` | B — Critical | **Chỉ** lessons importance ≥0.8, ≤10 entries | Low-priority lessons |
| `LESSONS_ARCHIVE.md` | B → C | Lessons importance <0.8 hoặc cũ (Qdrant searchable) | Critical lessons |
| `CHANGELOG.md` | A — Rules | Timeline thay đổi theo ngày | Tasks, lessons |
| `INSTINCTS.md` | A — Rules | Learned patterns + confidence 0.0–1.0 | Bug reports |
| `INSIGHTS.md` | C — Semantic | Cross-memory connections, compound insights | Raw data |
| `PROGRESS.md` | D — Session | Session memory **persistent** (KHÔNG xóa) | Một-lần info |
| `CONVENTIONS.md` | A — Rules | Project-specific coding standards | Global rules |
| `SECURITY-SPEC.md` | A — Rules | Security rules (frozen SSOT) | Code |
| `PLATFORM.md` | A — Rules | Cross-platform export rules | Project-specific |
| `llms.txt` | A — Rules | AI-readable project index (entry points, commands) | Code, logs |

---

## CHANGELOG

| Date | Change |
|---|---|
| **2026-04-07** | **APEX v11.0**: AutoAgent-Enhanced — 7 new rules (44-50): Complexity Gate, Hill-Climb Every Skill, Failure-Class Grouping, Simplicity Criterion, Verification Sub-Agent, Experiment Logging, Never Overfit. AutoAgent methodology: self-improving AI via measurement → comparison → hill-climbing. All 10 SKILL.md files upgraded to v11.0. GEMINI.md synchronized with CLAUDE.md. Total: 50 rules, 49 commands. |
| **2026-04-06** | **APEX v10.0**: Context Tools Integration — 3 new rules (41-43): Context7 Mandatory, LLMS_TXT Index, Repomix Export. Context7 MCP integrated into `/build` (Search First), `/verify` (CoV), `/search` (5-Step Protocol). Repomix codebase compression added to `/save` (STEP 9.5). llms.txt template created for `/init` (STEP 2.5). llms.txt reading added to `/start` (Layer A). Sources: Context7 (Upstash), Repomix (36k⭐), llms.txt standard (Jeremy Howard). |
| **2026-04-03** | **APEX v9.0**: Context Engineering Era — 5 new rules (36-40): Context Engineering First, Mistake Loop, RIPER Gate, Token Budget Aware, Hook Automation. Hooks system added. Claude Code Kit v9.0: .claudeignore, hooks/, RIPER command, compact command. Sources: awesome-claude-code (36k⭐), compound-engineering-plugin, context-engineering-kit, RIPER workflow. |
| **2026-03-25** | **APEX v8.0**: Command Optimization + Knowledge Graph + Security Rails — Merged overlapping commands (59→47): `/tokens`+`/palette`→`/design`, `/e2e`→`/responsive`, `/pipeline`+`/monitor-flow`→`/n8n`, removed `/openclaw`, moved `/apidoc`+`/componentdoc`+`/competitor`+`/internal-link` to references/. 6 new rules (30-35): Context-Aware Loading, Knowledge Graph, Auto-Observation, Progressive Disclosure v2, RAIL-GUARD Security, Cross-Platform Export. PLATFORM.md for Claude/Cursor/Windsurf compatibility. Enhanced `/consolidate` with Knowledge Graph phase. Enhanced `/instinct` YAML schema. |
| **2026-03-23** | **APEX v7.0**: Targeted Upgrade for Website/UI/N8N/SEO — New `verify` skill (Anti-Hallucination + CoV + LLM-as-Judge + Web Testing). `craft` v7.0: +4 commands (`/design`, `/animate`, `/responsive`, `/palette`) + design-patterns reference. `content` v7.0: +5 commands (`/cluster`, `/competitor`, `/refresh`, `/internal-link`, `/schema`) + seo-advanced reference. `automate` v7.0: +4 commands (`/n8n-ai`, `/openclaw`, `/pipeline`, `/monitor-flow`) + n8n-ai-patterns reference. `secure` v7.0: +3 commands (`/monitor`, `/ssl`, `/firewall`) + WordPress/N8N security. `build` v7.0: LLM-as-Judge reflexion + web-patterns reference. `spec` v7.0: +2 commands (`/spec refine`, `/spec verify`) + SDD. `fix` v7.0: Browser Debug + Kaizen 5 Whys + N8N Debug. 10 skills, 59 commands, 29 rules. |
| **2026-03-19** | **APEX v6.0**: BKNS Scaffold Integration — `/init`, `/status`, PROGRESS.md persistent, SECURITY-SPEC mandatory, Risk Classification Table (Rule 27-29). 6 new templates. |
| **2026-03-14** | **APEX v4.2**: Biomimetic Memory — Rule 26, 3-Strategy Recall, Reflect Auto-Trigger. |
| 2026-03-14 | **APEX v4.1**: Superpowers Integration — Verification Gate (Rule 24), Subagent Orchestration (Rule 25). |
| 2026-03-14 | **APEX v4.0**: Progressive Disclosure, /gsd, Ultrathink, Context Health Monitor. Rules 21-23. |
| 2026-03-10 | **APEX v3.0**: 4-Layer Smart Retrieval Memory. |
| 2026-03-10 | **APEX v2.0**: 6-Layer Memory, 35 commands, Importance scoring. |
| 2026-03-09 | v1.0 LAUNCH: 9 skills, 17 rules, ECC-inspired. |
