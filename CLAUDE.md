# APEX v13 — Doc-First Vibe Coding

> Mọi thay đổi code phải đi kèm cập nhật docs. Không ngoại lệ.

---

## DOC-FIRST GATE (Bắt buộc trước MỌI code change)

TRƯỚC khi viết/sửa bất kỳ dòng code nào:
1. **Ghi INTENT** — Mục đích thay đổi là gì? Viết 1-2 câu vào CHANGELOG draft
2. **Cập nhật SPEC** — Nếu thay đổi behavior/API/config → cập nhật docs/ trước
3. **Ghi expected outcome** — Success criteria cụ thể, verify bằng cách nào?

SAU khi code xong:
4. **Finalize CHANGELOG** — Chuyển draft thành entry chính thức
5. **Cập nhật HANDOVER** — Nếu thay đổi deployment, ops, hoặc setup
6. **Commit atomic** — `type(scope): message` — reference docs đã update

> Vi phạm Doc-First Gate = commit bị reject. Code không có docs = code không tồn tại.

---

## KARPATHY GATE (Chạy trước mọi task)

```
K1 Think:    Assumptions đã surface? Ambiguity đã hỏi user?
K2 Simple:   Minimum code? Không thêm feature/config không ai yêu cầu?
K3 Surgical: Chỉ đụng file liên quan? Không drive-by refactor?
K4 Goal:     Success criteria cụ thể? Verify bằng gì?
```

Bất kỳ ô nào fail → DỪNG, hỏi user. Không đoán.

---

## CORE RULES

1. **Doc-First** — Intent → Docs → Code → Verify → CHANGELOG → Commit
2. **Ask when unclear** — Mơ hồ → hỏi ngay. Liệt kê 2-3 cách hiểu nếu ambiguous
3. **Memory check** — Đọc LESSONS.md + memory/ trước task mới
4. **Search before build** — Codebase → Context7 → packages → mới viết mới
5. **Minimal change** — Mỗi dòng diff trace về request. Không refactor/reformat ngoài scope
6. **Root cause only** — Fix gốc, không patch triệu chứng
7. **Verify before claiming** — Chạy xong, xác nhận output, rồi mới nói "done"
8. **Max 3 retries** — 3 lần fail cùng approach → dừng, escalate cho user

---

## WORKFLOW COMMANDS

| Lệnh | Khi nào |
|-------|---------|
| `/start [task]` | Bắt đầu session mới |
| `/spec [feature]` | Feature phức tạp, cần spec trước |
| `/plan` | Brainstorm + task breakdown |
| `/build [task]` | Implement (tự động chạy Doc-First Gate) |
| `/fix [error]` | Debug: reproduce → isolate → root cause → fix |
| `/review` | Review code quality + security |
| `/ship` | Commit + verify + push (kiểm tra docs đã update) |
| `/save` | Kết thúc session, update LESSONS |
| `/checkpoint` | Snapshot giữa session |
| `/search [query]` | Context7 + codebase research |
| `/vibe [idea]` | Rapid UI prototyping |
| `/security` | OWASP audit |

---

## CONTEXT MANAGEMENT

- `/clear` giữa các task không liên quan — tiết kiệm token quan trọng nhất
- `/compact` sau mỗi milestone, không đợi warning
- Subagent cho research nặng — giữ main context sạch
- Skills load on-demand — chi tiết nằm trong skills/, không cần nhớ hết

---

## PROJECT-SPECIFIC

Mỗi project có CLAUDE.md riêng với: stack, commands, known issues.
Global file này chỉ chứa workflow rules chung cho MỌI project.

---

*APEX v13 — Doc-First Vibe Coding | Karpathy Mental Model*
