# APEX v11.0 — AutoAgent-Enhanced Context Engineering for Claude Code

> AI tự cải tiến: đo lường → so sánh → hill-climb mỗi phiên.

## Core Philosophy (AutoAgent Methodology)
- **Hill-climbing**: Track metrics, keep improvements, discard regressions
- **Failure-class analysis**: Group problems by class, fix patterns not symptoms
- **Simplicity criterion**: Same result + simpler = better
- **Proportional response**: Match process complexity to task complexity
- **Verification always**: Verify actual output, not intended output
- **Experiment logging**: Record what worked/didn't for cross-session learning

---

## 43 Global Rules + 7 AutoAgent Rules = 50 Rules

### Foundation (1-7)
1. **CLARITY GATE** — Hỏi nếu thiếu ≥3/5 yếu tố: [what] [where] [stack] [behavior] [constraints]
2. **CONTEXT LOADING** — 4-Layer: Rules → Lessons → Semantic → Auto-Memory
3. **LESSONS MANAGEMENT** — ≤10 entries, importance scoring, archive rotation
4. **SELF-REASONING GATE** — 3 questions trước mọi quyết định: best approach? hidden risks? user approval needed?
5. **CLEAN CODE** — Service layer, type-safe, no hardcode
6. **GIT CONVENTIONAL** — `feat(scope):` / `fix(scope):`
7. **VERIFICATION LOOP** — lint → format → type-check → test → audit

### TDD & Debug (8-13)
8. **TDD CYCLE** — Test first → code → refactor
9. **4-PHASE DEBUG** — Reproduce → Diagnose → Fix → Verify
10. **AUTO-INGEST** — LESSONS.md entry bắt buộc sau mỗi fix
11. **ANTI-PATTERN GUARD** — Rationalization Prevention Table
12. **PRODUCTION DEPLOY GATE** — Build → HTTP 200 → Response body check
13. **ULTRATHINK GATE** — Deep analysis cho complex tasks (≥500 words)

### UI/UX (14-20)
14. **ATOMIC DESIGN** — Atoms → Molecules → Organisms → Templates
15. **WCAG AA** — Contrast ≥4.5:1, focus visible, ARIA, touch ≥44px
16. **RESPONSIVE** — Mobile-first, test ≥3 breakpoints (375/768/1440)
17. **DARK MODE** — CSS custom properties, prefers-color-scheme
18. **ANIMATION** — GPU-only, prefers-reduced-motion, token-based
19. **DESIGN TOKENS** — var(--color-*), var(--space-*), var(--text-*). NO hardcode.
20. **PERFORMANCE BUDGET** — LCP ≤2.5s, CLS ≤0.1, FID ≤100ms

### Context & Memory (21-26)
21. **ULTRATHINK** — Complex → ≥500 words analysis before action
22. **CONTEXT HEALTH** — 🟢/🟡/🟠/🔴/💀 five levels
23. **GSD CYCLE** — Discuss → Plan → Execute → Verify
24. **VERIFICATION GATE** — Evidence before claims
25. **SUBAGENT ORCHESTRATION** — Use Agent tool for parallel research
26. **BIOMIMETIC MEMORY** — world | experience | mental_model

### Safety & Advanced (27-35)
27. **RISK CLASSIFICATION** — 🟢None → 🔴Critical
28. **SECURITY-SPEC** — Read before code if exists
29. **PERSISTENT PROGRESS** — Track state across sessions
30. **CONTEXT-AWARE LOADING** — Load ∝ task complexity
31. **KNOWLEDGE GRAPH** — Track entities and relationships
32. **AUTO-OBSERVATION** — Auto-capture patterns after /build and /fix
33. **PROGRESSIVE DISCLOSURE** — summary → relevant → full
34. **RAIL-GUARD** — Block CVE patterns, secret detection
35. **CROSS-PLATFORM** — Works in Antigravity, Claude Code, Cursor

### Context Engineering (36-43)
36. **CONTEXT ENGINEERING FIRST** — Curate info environment > clever prompts
37. **MISTAKE LOOP** — Auto-capture every bug fix into lessons
38. **RIPER GATE** — Research → Innovate → Plan → Execute → Review
39. **TOKEN BUDGET AWARE** — Progressive disclosure, ignore unnecessary files
40. **HOOK AUTOMATION** — Quality gates via hooks, not discipline
41. **CONTEXT7 EQUIVALENT** — Always verify API docs before coding (use WebSearch/WebFetch)
42. **PROJECT INDEX** — Maintain clear project structure understanding
43. **EXPORT COMPRESSED** — Summarize learnings for session continuity

### AutoAgent Rules (44-50) [v11.0 NEW]
44. **COMPLEXITY GATE** — Auto-detect task complexity → proportional protocol
45. **HILL-CLIMB EVERY SKILL** — Track success metrics, keep improvements, discard regressions
46. **FAILURE-CLASS GROUPING** — Categorize problems by class, not individual cases
47. **SIMPLICITY CRITERION** — Same result + simpler = always better
48. **VERIFICATION SUB-AGENT** — Every skill has built-in self-check
49. **EXPERIMENT LOGGING** — Record { approach, outcome, kept_or_discarded } for learning
50. **NEVER OVERFIT** — "If this task disappeared, would this still be worthwhile?"

---

## Memory Architecture (Claude Code Native)

```
┌─────────────────────────────────────────────────┐
│ A — RULES        CLAUDE.md (this file)          │
├─────────────────────────────────────────────────┤
│ B — LESSONS      .claude/memory/ (persistent)   │
├─────────────────────────────────────────────────┤
│ C — COMMANDS     .claude/commands/*.md           │
├─────────────────────────────────────────────────┤
│ D — AUTO-MEMORY  Claude Code native memory       │
└─────────────────────────────────────────────────┘

Memory Types: user | feedback | project | reference
Mapped from Antigravity: world→project, experience→feedback, mental_model→user
```

---

## Skill Commands (see .claude/commands/ for details)

| Command | Purpose |
|---|---|
| `/build` | Feature implementation — TDD, complexity gate, hill-climb |
| `/fix` | Debugging — severity triage, hypothesis loop, failure-class |
| `/security` | OWASP audit — active probing, risk scoring, fix-verify |
| `/learn` | Pattern capture — auto-consolidation, A/B instinct testing |
| `/spec` | Architecture docs — living spec, quality scoring |
| `/automate` | Workflow automation — circuit breaker, benchmarking |
| `/plan` | Brainstorm + plan before coding |
| `/verify` | Verification loop — lint + typecheck + test + security |

---

## Tool Mapping (Antigravity → Claude Code)

| Antigravity Tool | Claude Code Equivalent |
|---|---|
| Browser Sub-Agent | WebFetch / WebSearch |
| Qdrant Memory | Claude Code native memory (.claude/projects/) |
| Context7 MCP | WebSearch + WebFetch for API docs |
| Repomix | Grep + Glob for codebase understanding |
| Structured Traces | TodoWrite for progress tracking |
| Mission Control | Agent tool for parallel sub-tasks |
| Knowledge Graph | Memory files + cross-references |
