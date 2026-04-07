#!/usr/bin/env python3
"""
BKNS Agent Wiki — compile-wiki (Multi-Page Architecture v2.0)
Đọc claims → Gemini Pro compile → multiple wiki sub-pages per category.

Architecture:
  Each category produces multiple focused sub-pages:
  - index.md        → Overview + Table of Contents
  - bang-gia.md     → Pricing tables
  - thong-so.md     → Technical specifications
  - chinh-sach.md   → Policies (SLA, support, billing)
  - tinh-nang.md    → Features (hosting-specific)
  - [product-line].md → Per-product-line pages (VPS, Email, Server)

Usage:
    python3 scripts/compile.py hosting           # Compile 1 category
    python3 scripts/compile.py --all             # Compile all
    python3 scripts/compile.py --approve hosting  # Publish draft
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    CLAIMS_APPROVED_DIR, CLAIMS_DRAFTS_DIR, WIKI_DRAFTS_DIR, WIKI_DIR,
    SELF_REVIEW_RULES, MODEL_PRO,
)
from lib.gemini import generate
from lib.logger import log_entry, log_approval  # [W7] top-level import
from lib.telegram import notify_skill, notify_error
from lib.utils import (
    read_yaml, write_yaml, now_iso, today_str, ensure_dir,
    write_markdown_with_frontmatter, read_text_safe,
)


# ═══════════════════════════════════════════════════════════
#  SUB-PAGE DEFINITIONS PER CATEGORY
# ═══════════════════════════════════════════════════════════
# Each sub-page defines:
#   filename: output file
#   title: page title
#   desc: short description for index TOC
#   filter: function(claim) → bool — which claims to include
#   prompt_hint: extra instructions for this page type

def _attr_in(claim, keywords):
    """Check if claim's attribute contains any keyword."""
    attr = (claim.get("attribute") or "").lower()
    return any(kw in attr for kw in keywords)

def _entity_has(claim, keywords):
    """Check if entity_id contains any keyword."""
    eid = (claim.get("entity_id") or "").lower()
    return any(kw in eid for kw in keywords)


# ── Filter Functions ──────────────────────────────────────

def _is_pricing(c):
    return _attr_in(c, ["price", "giá", "cost", "fee", "billing",
                        "monthly_price", "yearly_price", "registration_fee",
                        "renewal_fee", "transfer_in_fee", "setup_fee",
                        "minimum_billing"])

def _is_specs(c):
    return _attr_in(c, ["cpu", "ram", "storage", "bandwidth", "vcpu",
                        "disk", "ssd", "core", "memory", "data_transfer",
                        "iops", "connection", "port", "ip_address",
                        "ipv4", "ipv6", "daily_email_limit",
                        "inbox_delivery_rate", "email_account",
                        "validation_type", "wildcard", "san_support",
                        "warranty", "issuance_time", "encryption",
                        "browser_compatibility", "server_license",
                        "domain_limit", "user_accounts_limit"])

def _is_policy(c):
    return _attr_in(c, ["policy", "sla", "support", "trial", "refund",
                        "uptime", "guarantee", "payment", "hoàn tiền",
                        "backup_frequency", "backup_policy",
                        "registration_process", "required_documents",
                        "purchase_url", "contact", "hotline"])

def _is_feature(c):
    return _attr_in(c, ["feature", "benefit", "tính năng", "capability",
                        "technology", "platform", "infrastructure",
                        "architecture", "has_", "support", "compatible"])

def _is_general(c):
    return _attr_in(c, ["desc", "name", "category", "target_audience",
                        "target_customer", "use_case", "alternative",
                        "provider", "source_url", "url", "canonical",
                        "product_name"])

def _is_faq(c):
    """FAQ-related claims: questions, answers, common concerns."""
    return _attr_in(c, ["faq", "question", "câu_hỏi", "answer",
                        "trả_lời", "common_question", "concern"])

def _is_comparison(c):
    """Comparison/alternative-related claims."""
    return _attr_in(c, ["compare", "so_sánh", "alternative", "vs",
                        "competitor", "khác_biệt", "difference",
                        "advantage", "disadvantage"])

def _is_guide(c):
    """Guide/tutorial-related claims."""
    return _attr_in(c, ["guide", "hướng_dẫn", "tutorial", "how_to",
                        "step", "bước", "quy_trình", "process",
                        "instruction", "setup", "cài_đặt"])

def _is_overview(c):
    """Overview: broad descriptive claims combining general + feature."""
    return _is_general(c) or _is_feature(c)

# ── Standard Sub-Page Definitions (9 per category) ────────
# Every category gets these 9 standard sub-pages.
# Categories may also get custom product-line pages.

def _build_standard_subpages(category: str, vn_name: str) -> list[dict]:
    """Generate the 9 standard sub-pages for any category."""
    return [
        {
            "filename": "index.md",
            "title": f"{vn_name} — Trang Tổng Quan",
            "desc": f"Hub điều hướng cho {vn_name}: mục lục, sản phẩm con, liên kết nhanh",
            "filter": _is_general,
            "prompt_hint": (
                f"Viết trang HUB ĐIỀU HƯỚNG cho {vn_name}. "
                "Bao gồm: mô tả ngắn category, danh sách sản phẩm con (nếu có từ claims), "
                "MỤC LỤC link đến: tong-quan.md, bang-gia.md, thong-so.md, tinh-nang.md, "
                "chinh-sach.md, cau-hoi-thuong-gap.md, so-sanh.md, huong-dan.md. "
                "Nếu category có các sản phẩm con riêng biệt, liệt kê link san-pham/<slug>.md."
            ),
        },
        {
            "filename": "tong-quan.md",
            "title": f"{vn_name} — Tổng Quan Chi Tiết",
            "desc": f"Giới thiệu sâu về {vn_name}: USP, đối tượng, vị trí trong hệ sinh thái BKNS",
            "filter": _is_overview,
            "prompt_hint": (
                f"Viết TỔNG QUAN chi tiết cho {vn_name}: "
                "1) Dịch vụ/sản phẩm này là gì, giải quyết bài toán gì; "
                "2) BKNS cung cấp những gì trong category này (liệt kê theo claims); "
                "3) Đối tượng phù hợp (cá nhân, doanh nghiệp, developer...); "
                "4) Điểm mạnh / USP so với thị trường; "
                "5) Khi nào nên chọn dịch vụ này vs dịch vụ BKNS khác."
            ),
        },
        {
            "filename": "bang-gia.md",
            "title": f"{vn_name} — Bảng Giá",
            "desc": f"Bảng giá chi tiết tất cả gói {vn_name}",
            "filter": _is_pricing,
            "prompt_hint": (
                f"Tạo BẢNG GIÁ chi tiết dạng Markdown table cho {vn_name}. "
                "Mỗi gói/sản phẩm 1 dòng. Cột: Tên gói, Giá tháng (hoặc năm), "
                "Setup fee (nếu có), VAT, Ghi chú. "
                "Nhóm theo dòng sản phẩm nếu có nhiều line. "
                "GIỮ NGUYÊN số liệu từ claims, KHÔNG làm tròn hay đổi đơn vị."
            ),
        },
        {
            "filename": "thong-so.md",
            "title": f"{vn_name} — Thông Số Kỹ Thuật",
            "desc": f"So sánh specs từng gói {vn_name}",
            "filter": _is_specs,
            "prompt_hint": (
                f"Tạo BẢNG SO SÁNH kỹ thuật cho {vn_name}. "
                "Mỗi gói 1 dòng. Cột tùy thuộc vào loại sản phẩm: "
                "Server/VPS/Hosting → CPU, RAM, SSD, Bandwidth, OS. "
                "Email → Dung lượng, Accounts, Email/ngày. "
                "SSL → Loại, Warranty, Thời gian cấp, Domains. "
                "Sắp xếp từ gói nhỏ → lớn."
            ),
        },
        {
            "filename": "tinh-nang.md",
            "title": f"{vn_name} — Tính Năng",
            "desc": f"Features nổi bật của {vn_name}",
            "filter": _is_feature,
            "prompt_hint": (
                f"Liệt kê tất cả TÍNH NĂNG chung của {vn_name}. "
                "Nhóm theo: Quản trị, Bảo mật, Hiệu suất, Hỗ trợ kỹ thuật. "
                "Mỗi tính năng có mô tả ngắn 1-2 câu. "
                "CHỈ liệt kê tính năng có trong claims."
            ),
        },
        {
            "filename": "chinh-sach.md",
            "title": f"{vn_name} — Chính Sách",
            "desc": f"SLA, hoàn tiền, trial, hỗ trợ cho {vn_name}",
            "filter": _is_policy,
            "prompt_hint": (
                f"Tổng hợp CHÍNH SÁCH cho {vn_name}: "
                "SLA uptime (%), thời gian dùng thử, chính sách hoàn tiền, "
                "kênh hỗ trợ (hotline, email, ticket), thời gian phản hồi, "
                "điều khoản sử dụng, chính sách backup. "
                "Format rõ ràng, dễ tra cứu."
            ),
        },
        {
            "filename": "cau-hoi-thuong-gap.md",
            "title": f"{vn_name} — Câu Hỏi Thường Gặp",
            "desc": f"FAQ cho {vn_name}",
            "filter": _is_faq,
            "prompt_hint": (
                f"Tạo trang FAQ cho {vn_name}. "
                "Format: ### Câu hỏi → trả lời. "
                "Nhóm theo: Trước khi mua, Trong quá trình sử dụng, Hỗ trợ & khắc phục sự cố. "
                "CHỈ sử dụng claims FAQ thực tế. "
                "Nếu claims FAQ ít → ghi 'Đang cập nhật' cho từng nhóm thiếu, KHÔNG tự suy luận câu hỏi."
                # [W8] Removed 'phỏng đoán hợp lý' — violates core anti-hallucination rule.
            ),
        },
        {
            "filename": "so-sanh.md",
            "title": f"{vn_name} — So Sánh",
            "desc": f"So sánh nội bộ các sản phẩm trong {vn_name}",
            "filter": _is_comparison,
            "prompt_hint": (
                f"Tạo trang SO SÁNH cho {vn_name}. "
                "So sánh NỘI BỘ giữa các sản phẩm/gói trong cùng category. "
                "KHÔNG so sánh với đối thủ bên ngoài. "
                "Format: Markdown table so sánh. "
                "Nếu claims so sánh ít → dùng claims giá + specs để xây bảng so sánh tính năng."
            ),
        },
        {
            "filename": "huong-dan.md",
            "title": f"{vn_name} — Hướng Dẫn",
            "desc": f"Hướng dẫn đăng ký, kích hoạt, quản lý {vn_name}",
            "filter": _is_guide,
            "prompt_hint": (
                f"Tạo trang HƯỚNG DẪN cho {vn_name}. "
                "Bao gồm: 1) Cách đăng ký/mua, 2) Cách kích hoạt/triển khai, "
                "3) Cách quản lý/sử dụng cơ bản, 4) Troubleshooting cơ bản. "
                "Format step-by-step. "
                "Nếu claims hướng dẫn ít → ghi 'Đang cập nhật' cho từng section thiếu."
            ),
        },
    ]


# ── Category-Specific Sub-Page Overrides ──────────────────
# Additional product-line pages beyond the 9 standard ones.

CATEGORY_PRODUCT_PAGES = {
    "hosting": [],  # Product detail pages handled by auto-generator

    "vps": [
        {
            "filename": "san-pham/cloud-vps-vm.md",
            "title": "Cloud VPS SSD — VM Series",
            "desc": "Dòng Cloud VPS SSD: VM01, VM02, VM03...",
            "filter": lambda c: _entity_has(c, ["cloud", "vm0", "vm-0", "cloud_vps_ssd"]) and not _entity_has(c, ["amd", "epyc", "seo", "misa", "n8n", "storage", "sieu_re", "gia_re"]),
            "prompt_hint": "Chi tiết dòng Cloud VPS SSD (VM series): bảng so sánh các gói VM01-VM03+, cấu hình, giá, features đặc trưng.",
        },
        {
            "filename": "san-pham/cloud-vps-amd.md",
            "title": "Cloud VPS AMD EPYC — Hiệu Năng Cao",
            "desc": "Dòng AMD EPYC: EPYC 1-5",
            "filter": lambda c: _entity_has(c, ["amd", "epyc"]),
            "prompt_hint": "Chi tiết dòng Cloud VPS AMD EPYC: bảng so sánh EPYC 1-5, cấu hình, giá, ưu điểm AMD vs Intel.",
        },
        {
            "filename": "san-pham/vps-seo.md",
            "title": "VPS SEO BKNS",
            "desc": "VPS tối ưu cho SEO",
            "filter": lambda c: _entity_has(c, ["seo"]),
            "prompt_hint": "Chi tiết VPS SEO: cấu hình, giá, tính năng tối ưu cho SEO tools, multi-IP.",
        },
        {
            "filename": "san-pham/vps-bk-misa.md",
            "title": "VPS MISA BKNS",
            "desc": "VPS chạy phần mềm kế toán MISA",
            "filter": lambda c: _entity_has(c, ["misa"]),
            "prompt_hint": "Chi tiết VPS MISA: cấu hình, giá, tính năng tối ưu cho phần mềm kế toán MISA.",
        },
        {
            "filename": "san-pham/vps-n8n.md",
            "title": "VPS N8N-AI BKNS",
            "desc": "VPS chạy N8N và AI workflows",
            "filter": lambda c: _entity_has(c, ["n8n", "ai"]) and not _entity_has(c, ["misa", "seo"]),
            "prompt_hint": "Chi tiết VPS N8N-AI: cấu hình, giá, tính năng tối ưu cho automation/AI workflows.",
        },
        {
            "filename": "san-pham/storage-vps.md",
            "title": "VPS Storage BKNS",
            "desc": "VPS lưu trữ dung lượng lớn",
            "filter": lambda c: _entity_has(c, ["storage"]) and _entity_has(c, ["vps"]),
            "prompt_hint": "Chi tiết VPS Storage: cấu hình, giá, dung lượng lưu trữ lớn.",
        },
        {
            "filename": "san-pham/vps-gia-re.md",
            "title": "VPS Giá Rẻ BKNS",
            "desc": "Dòng VPS giá rẻ cho cá nhân/startup",
            "filter": lambda c: _entity_has(c, ["gia_re", "gia-re", "mm0"]),
            "prompt_hint": "Chi tiết VPS Giá Rẻ: bảng so sánh MM01-MM05, cấu hình, giá, phù hợp cá nhân/startup.",
        },
        {
            "filename": "san-pham/vps-mmo.md",
            "title": "VPS MMO BKNS",
            "desc": "Dòng VPS dành cho MMO",
            "filter": lambda c: _entity_has(c, ["mmo"]),
            "prompt_hint": "Chi tiết VPS MMO: cấu hình, giá, tính năng phù hợp cho MMO.",
        },
    ],

    "email": [
        {
            "filename": "san-pham/email-hosting.md",
            "title": "Email Hosting BKNS",
            "desc": "Email Hosting gói 1-4: giá, dung lượng, accounts",
            "filter": lambda c: _entity_has(c, ["email_hosting", "email-hosting", "email.email", "email1", "email2", "email3", "email4"]) and not _entity_has(c, ["server", "relay"]),
            "prompt_hint": "Chi tiết Email Hosting: bảng so sánh gói 1-4, dung lượng, accounts, domains, giá.",
        },
        {
            "filename": "san-pham/cloud-email-server.md",
            "title": "Cloud Email Server BKNS",
            "desc": "Cloud Email Server: ES 01-04, Mini Email",
            "filter": lambda c: _entity_has(c, ["cloud_email", "email_server", "es_0", "es-0", "mini_email"]) or (_entity_has(c, ["email"]) and _entity_has(c, ["server"])),
            "prompt_hint": "Chi tiết Cloud Email Server: ES 01-04, Mini Email 01-04. Bảng so sánh cấu hình, dung lượng, giá.",
        },
        {
            "filename": "san-pham/email-relay.md",
            "title": "Email Relay BKNS",
            "desc": "Email Relay gửi hàng loạt: BK-RELAY 01-04",
            "filter": lambda c: _entity_has(c, ["relay", "bk-relay", "bk_relay"]),
            "prompt_hint": "Chi tiết Email Relay (BK-RELAY): bảng so sánh gói 01-04, số email/ngày, giá.",
        },
    ],

    "ssl": [
        # SSL has many individual certs — auto-detect from entity_id
    ],

    "ten-mien": [
        {
            "filename": "san-pham/dang-ky-ten-mien.md",
            "title": "Đăng Ký Tên Miền BKNS",
            "desc": "Quy trình đăng ký tên miền, đuôi hỗ trợ",
            "filter": lambda c: _entity_has(c, ["dang_ky", "register"]) or _attr_in(c, ["registration"]),
            "prompt_hint": "Chi tiết đăng ký tên miền: đuôi hỗ trợ, quy trình, hồ sơ cần thiết.",
        },
        {
            "filename": "san-pham/chuyen-ten-mien.md",
            "title": "Chuyển Tên Miền (Transfer)",
            "desc": "Quy trình transfer domain, phí, điều kiện",
            "filter": lambda c: _attr_in(c, ["transfer", "chuyển"]),
            "prompt_hint": "Hướng dẫn TRANSFER domain: phí, quy trình, điều kiện, thời gian.",
        },
    ],

    "server": [
        {
            "filename": "san-pham/thue-may-chu.md",
            "title": "Thuê Máy Chủ Riêng (Dedicated)",
            "desc": "Thuê máy chủ riêng: MCCB01, MCCB02...",
            "filter": lambda c: _entity_has(c, ["dedicated", "mccb", "thue_may_chu"]) and not _entity_has(c, ["colocation", "colo", "management", "backup", "vpn"]),
            "prompt_hint": "Chi tiết Dedicated Server: bảng so sánh gói (MCCB01, MCCB02...), CPU, RAM, Storage, giá.",
        },
        {
            "filename": "san-pham/thue-cho-dat-may-chu.md",
            "title": "Colocation BKNS",
            "desc": "Cho thuê chỗ đặt máy chủ",
            "filter": lambda c: _entity_has(c, ["colocation", "colo", "co_location", "cho_dat"]),
            "prompt_hint": "Chi tiết Colocation: rack size, bandwidth, power, SLA, giá.",
        },
        {
            "filename": "san-pham/quan-tri-may-chu-tron-goi.md",
            "title": "Quản Trị Server Trọn Gói",
            "desc": "Managed server, Backup, VPN",
            "filter": lambda c: _entity_has(c, ["management", "quan_tri", "managed"]) or _entity_has(c, ["backup"]) or _entity_has(c, ["vpn"]),
            "prompt_hint": "Chi tiết Quản trị server, Cloud Backup, VPN: gói, tính năng, giá.",
        },
    ],

    "software": [
        # Software products auto-detected from entity_id
    ],

    "other": [],
    "uncategorized": [],
}

# ── Build Full SUBPAGE_DEFS ───────────────────────────────

# Category name → Vietnamese title mapping
CATEGORY_TITLES = {
    "hosting": "Web Hosting BKNS",
    "vps": "Cloud VPS BKNS",
    "email": "Email Doanh Nghiệp BKNS",
    "ssl": "Chứng Chỉ SSL BKNS",
    "ten-mien": "Tên Miền BKNS",
    "server": "Máy Chủ BKNS",
    "software": "Phần Mềm & Bản Quyền BKNS",
    "other": "Dịch Vụ Khác BKNS",
    "uncategorized": "Chưa Phân Loại",
}

# Build SUBPAGE_DEFS: standard 9 + category-specific product pages
SUBPAGE_DEFS = {}
for _cat, _vn_name in CATEGORY_TITLES.items():
    SUBPAGE_DEFS[_cat] = _build_standard_subpages(_cat, _vn_name)
    # Append category-specific product pages
    SUBPAGE_DEFS[_cat].extend(CATEGORY_PRODUCT_PAGES.get(_cat, []))

# Cross-link mapping
CROSS_LINKS = {
    "hosting": ["ssl", "ten-mien", "email", "software"],
    "vps": ["ssl", "software", "server"],
    "email": ["ten-mien", "hosting", "ssl"],
    "ssl": ["hosting", "vps", "ten-mien"],
    "ten-mien": ["hosting", "email", "ssl"],
    "server": ["vps", "software"],
    "software": ["hosting", "vps", "server"],
    "other": ["hosting", "vps", "ssl"],
    "uncategorized": ["hosting", "vps"],
}


# ═══════════════════════════════════════════════════════════
#  COMPILE PROMPT (per sub-page)
# ═══════════════════════════════════════════════════════════

SUBPAGE_COMPILE_PROMPT = """Bạn là biên tập viên chuyên nghiệp cho Wiki tri thức BKNS.

INPUT — Danh sách claims đã duyệt, thuộc category "{category}":
{claims_content}

NHIỆM VỤ: Tổng hợp claims thành trang wiki "{title}".

MÔ TẢ TRANG: {page_desc}

HƯỚNG DẪN ĐẶC BIỆT:
{prompt_hint}

QUY TẮC BẮT BUỘC:
1. ✅ CHỈ sử dụng dữ liệu từ claims — KHÔNG thêm thông tin ngoài
2. ✅ Bảng giá → dùng Markdown table, giữ NGUYÊN số liệu chính xác
3. ✅ Viết tiếng Việt tự nhiên, chuyên nghiệp
4. ❌ KHÔNG bịa thêm features, giá, chính sách không có trong claims
5. ❌ KHÔNG dùng "có lẽ", "có thể", "khoảng" cho số liệu cụ thể
6. ✅ Nếu thiếu dữ liệu → ghi rõ "Đang cập nhật" chứ không bịa
7. ✅ Cuối trang: "Compiled by BKNS Wiki Bot • {date}"
8. ✅ Nếu claims quá ít cho trang này → ghi nội dung cô đọng, không kéo dài

SẢN PHẨM LIÊN QUAN (cross-link):
{cross_links}

OUTPUT: Markdown thuần (không frontmatter, không code fence)."""


# ═══════════════════════════════════════════════════════════
#  SELF-REVIEW PROMPT
# ═══════════════════════════════════════════════════════════

SELF_REVIEW_PROMPT = """Bạn là auditor kiểm tra chất lượng wiki BKNS.

WIKI DRAFT:
{draft_content}

CLAIMS GỐC (nguồn đáng tin cậy):
{claims_content}

NHIỆM VỤ: So sánh draft vs claims, tìm hallucination.

KIỂM TRA:
1. Mỗi con số (giá, specs) trong draft CÓ KHỚP claims không?
2. Có feature/tính năng nào bịa ra?
3. Có thiếu thông tin quan trọng?
4. URLs/emails/hotlines chính xác?

OUTPUT (JSON thuần, không code fence):
{{
  "verdict": "pass" | "fail",
  "issues": [
    {{
      "type": "hallucination" | "missing" | "mismatch",
      "detail": "mô tả",
      "severity": "critical" | "high" | "medium" | "low",
      "location": "đoạn text",
      "suggested_fix": "gợi ý"
    }}
  ],
  "corrected_text": "bản sửa (nếu fail)" | null,
  "confidence": 0.0-1.0
}}"""


# ═══════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def collect_claims(category: str) -> tuple[list[dict], str]:
    """Collect all claims for a category (approved + new drafts)."""
    claims_by_id = {}

    # Approved first (priority)
    approved_dir = CLAIMS_APPROVED_DIR / "products" / category
    if approved_dir.exists():
        for f in sorted(approved_dir.glob("*.yaml")):
            claim = read_yaml(f)
            if isinstance(claim, dict):
                cid = claim.get("claim_id", f.stem)
                claims_by_id[cid] = claim

    # Drafts — only add NEW ones
    drafts_dir = CLAIMS_DRAFTS_DIR / "products" / category
    if drafts_dir.exists():
        for f in sorted(drafts_dir.glob("*.yaml")):
            claim = read_yaml(f)
            if isinstance(claim, dict):
                cid = claim.get("claim_id", f.stem)
                if cid not in claims_by_id:
                    claims_by_id[cid] = claim

    claims = list(claims_by_id.values())
    return claims, _format_claims_text(claims)


def _format_claims_text(claims: list[dict]) -> str:
    """Format claims into text for LLM prompt.
    
    Ground truth claims are marked with [GT] for the compiler to prioritize.
    """
    # Sort: ground_truth first, then high, then medium
    confidence_order = {"ground_truth": 0, "high": 1, "medium": 2, "low": 3}
    sorted_claims = sorted(claims, key=lambda c: confidence_order.get(c.get("confidence", "low"), 3))
    
    formatted = []
    for c in sorted_claims:
        gt_tag = "[GT] " if c.get("confidence") == "ground_truth" else ""
        quals = c.get("qualifiers", {})
        qual_str = ""
        if quals:
            qual_parts = [f"{k}={v}" for k, v in quals.items()]
            qual_str = f"  qualifiers: {', '.join(qual_parts)}\n"
        
        formatted.append(
            f"- {gt_tag}claim_id: {c.get('claim_id', 'N/A')}\n"
            f"  entity: {c.get('entity_id', '')} ({c.get('entity_name', '')})\n"
            f"  attribute: {c.get('attribute', '')}\n"
            f"  value: {c.get('value', '')}\n"
            f"  unit: {c.get('unit', '')}\n"
            f"  confidence: {c.get('confidence', '')}\n"
            f"{qual_str}"
            f"  note: {c.get('compiler_note', '')}"
        )
    return "\n".join(formatted)


def _deduplicate_claims(claims: list[dict]) -> list[dict]:
    """Remove duplicate claims (same entity_id + attribute).
    
    Priority: ground_truth > high > medium > low.
    Within same confidence, keep latest observed_at.
    """
    confidence_rank = {"ground_truth": 4, "high": 3, "medium": 2, "low": 1}
    seen = {}
    for c in claims:
        key = (c.get("entity_id", ""), c.get("attribute", ""))
        if key not in seen:
            seen[key] = c
        else:
            existing = seen[key]
            existing_rank = confidence_rank.get(existing.get("confidence", "low"), 0)
            new_rank = confidence_rank.get(c.get("confidence", "low"), 0)
            
            # Ground truth always wins
            if new_rank > existing_rank:
                seen[key] = c
            elif new_rank == existing_rank:
                # Same confidence → keep latest
                if c.get("observed_at", "") > existing.get("observed_at", ""):
                    seen[key] = c
    return list(seen.values())


def _filter_claims(claims: list[dict], filter_fn) -> list[dict]:
    """Filter claims by a filter function."""
    return [c for c in claims if filter_fn(c)]


def _generate_cross_links(category: str) -> str:
    """Generate cross-link text for a category."""
    related = CROSS_LINKS.get(category, [])
    if not related:
        return "Không có."
    lines = []
    for r in related:
        title = CATEGORY_TITLES.get(r, r)
        lines.append(f"- [{title}](../{r}/index.md)")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
#  COMPILE CATEGORY (multi-page)
# ═══════════════════════════════════════════════════════════

def compile_category(category: str, force: bool = False) -> dict:
    """Compile all sub-pages for a category.

    Returns dict with status, pages compiled, cost, etc.
    """
    log_entry("compile-wiki", "start", f"Compiling multi-page: {category}")

    # 1. Collect and deduplicate
    claims, _ = collect_claims(category)
    claims = _deduplicate_claims(claims)

    if not claims:
        msg = f"Không có claims cho category: {category}"
        log_entry("compile-wiki", "skip", msg)
        return {"status": "skip", "detail": msg}

    # 2. Get sub-page definitions
    subpages = SUBPAGE_DEFS.get(category)
    if not subpages:
        msg = f"No sub-page definitions for: {category}"
        log_entry("compile-wiki", "error", msg)
        return {"status": "error", "detail": msg}

    total_cost = 0
    pages_compiled = 0
    pages_skipped = 0
    results = []
    cross_links_text = _generate_cross_links(category)

    # 3. Compile each sub-page
    for sp in subpages:
        filename = sp["filename"]
        title = sp["title"]
        filter_fn = sp["filter"]

        # Filter claims for this sub-page
        page_claims = _filter_claims(claims, filter_fn)

        if not page_claims:
            # Generate skeleton page instead of skipping
            log_entry("compile-wiki", "skeleton",
                      f"  No claims for {category}/{filename} — generating skeleton")
            page_content = (
                f"# {title}\n\n"
                f"> {sp['desc']}\n\n"
                "## Nội dung\n\n"
                "⏳ Đang cập nhật — Chưa có claims đủ cho trang này.\n\n"
                f"## Sản phẩm liên quan\n\n{cross_links_text}\n\n"
                "## Liên hệ / đăng ký\n\n"
                "- [Liên hệ BKNS](../../support/lien-he.md)\n"
                "- [Hướng dẫn chung](../../support/huong-dan-chung.md)\n"
            )
            page_cost = 0
            review_verdict = "skeleton"
            corrections = 0
            pages_skipped += 1  # [W1] was never incremented
        else:
            claims_text = _format_claims_text(page_claims)

            log_entry("compile-wiki", "compiling",
                      f"  {category}/{filename}: {len(page_claims)} claims")

            # Build prompt
            prompt = SUBPAGE_COMPILE_PROMPT.format(
                category=category,
                claims_content=claims_text,
                title=title,
                page_desc=sp["desc"],
                prompt_hint=sp["prompt_hint"],
                date=today_str(),
                cross_links=cross_links_text,
            )

            try:
                result = generate(
                    prompt=prompt,
                    model=MODEL_PRO,
                    skill="compile-wiki",
                    temperature=0.2,
                    max_output_tokens=65536,
                )
            except Exception as e:
                error_msg = f"Compile error {category}/{filename}: {str(e)}"
                log_entry("compile-wiki", "error", error_msg, severity="critical")
                results.append({
                    "filename": filename,
                    "status": "error",
                    "detail": str(e),
                })
                continue

            page_content = result["text"]
            page_cost = result.get("cost_usd", 0)
            total_cost += page_cost

            # [W4] Self-review threshold:
            # - Pricing/spec pages (high-risk): review even with 1+ claims
            # - Other pages: review when >= 5 claims
            review_verdict = "skipped"
            corrections = 0

            is_high_risk_page = filename in ("bang-gia.md", "thong-so.md", "chinh-sach.md")
            review_threshold = 1 if is_high_risk_page else 5

            if len(page_claims) >= review_threshold:
                review_result = self_review(page_content, claims_text, category)
                total_cost += review_result.get("cost_usd", 0)
                review_verdict = review_result.get("verdict", "unknown")

                if review_result.get("verdict") == "fail":
                    corrected = review_result.get("corrected_text")
                    if corrected and SELF_REVIEW_RULES.get("auto_correct"):
                        page_content = corrected
                        corrections = len(review_result.get("issues", []))

        # Save draft — handle san-pham/ subdirectory
        draft_dir = WIKI_DRAFTS_DIR / "products" / category
        if "/" in filename:
            # e.g., "san-pham/cloud-vps-amd.md" → create san-pham/ subdir
            sub_dir = draft_dir / Path(filename).parent
            ensure_dir(sub_dir)
        else:
            ensure_dir(draft_dir)
        draft_path = draft_dir / filename

        # Generate page_id from filename (handle nested paths)
        page_id_suffix = filename.replace(".md", "").replace("/", ".")
        frontmatter = {
            "page_id": f"wiki.products.{category}.{page_id_suffix}",
            "title": title,
            "category": f"products/{category}",
            "updated": today_str(),
            "review_state": "drafted",
            "claims_used": len(page_claims),
            "compile_cost_usd": round(page_cost, 4),
            "self_review": review_verdict,
            "corrections": corrections,
        }

        write_markdown_with_frontmatter(draft_path, frontmatter, page_content)

        pages_compiled += 1
        results.append({
            "filename": filename,
            "status": "success",
            "claims": len(page_claims),
            "review": review_verdict,
            "corrections": corrections,
        })

        log_entry("compile-wiki", "page_done",
                  f"  ✅ {category}/{filename}: {len(page_claims)} claims, "
                  f"review={review_verdict}")

    # 4. Summary
    msg = (
        f"Compiled *{category}*:\n"
        f"• {pages_compiled} pages compiled\n"
        f"• {pages_skipped} pages skipped (no data)\n"
        f"• {len(claims)} total claims\n"
        f"• Cost: ${total_cost:.4f}"
    )
    notify_skill("compile-wiki", msg, severity="success")

    log_entry("compile-wiki", "complete", msg, cost_usd=total_cost)

    return {
        "status": "success",
        "category": category,
        "pages_compiled": pages_compiled,
        "pages_skipped": pages_skipped,
        "total_claims": len(claims),
        "cost_usd": total_cost,
        "pages": results,
    }


def self_review(draft: str, claims_text: str, category: str) -> dict:
    """Run self-review: verify draft against claims."""
    log_entry("compile-wiki", "self_review_start", f"Reviewing {category}")

    prompt = SELF_REVIEW_PROMPT.format(
        draft_content=draft,
        claims_content=claims_text,
    )

    try:
        result = generate(
            prompt=prompt,
            model=MODEL_PRO,
            skill="compile-wiki",
            system_instruction="Bạn là QA auditor. Trả lời bằng JSON DUY NHẤT.",
            temperature=0.1,
            max_output_tokens=8192,
        )
    except Exception as e:
        log_entry("compile-wiki", "error",
                  f"Self-review API error: {str(e)}", severity="high")
        return {"verdict": "error", "issues": [], "cost_usd": 0}

    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        review = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                review = json.loads(match.group(0))
            except json.JSONDecodeError:
                review = {"verdict": "error", "issues": []}
        else:
            review = {"verdict": "error", "issues": []}

    review["cost_usd"] = result.get("cost_usd", 0)
    return review


def approve_draft(category: str) -> dict:
    """Publish all drafted sub-pages for a category."""
    draft_dir = WIKI_DRAFTS_DIR / "products" / category
    if not draft_dir.exists():
        return {"status": "error", "detail": f"No drafts for {category}"}

    published = []
    for draft_path in sorted(draft_dir.rglob("*.md")):
        content = draft_path.read_text(encoding="utf-8")
        from lib.utils import parse_frontmatter
        fm, body = parse_frontmatter(content)

        fm["review_state"] = "approved"
        fm["approved_at"] = now_iso()

        # Preserve relative path structure (e.g., san-pham/cloud-vps-amd.md)
        rel_path = draft_path.relative_to(draft_dir)
        target_dir = WIKI_DIR / "products" / category / rel_path.parent
        ensure_dir(target_dir)
        target_path = target_dir / draft_path.name
        write_markdown_with_frontmatter(target_path, fm, body)
        published.append(str(target_path))

    if published:
        log_approval(str(draft_dir), "admin")  # [W7] using top-level import

        notify_skill("compile-wiki",
                      f"✅ Wiki *{category}* published! ({len(published)} pages)\n"
                      + "\n".join(f"• {Path(p).name}" for p in published),
                      severity="success")

    return {"status": "approved", "published": published}


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Compile Wiki (Multi-Page)")
    parser.add_argument("category", nargs="?", help="Category to compile")
    parser.add_argument("--all", action="store_true", help="Compile all categories")
    parser.add_argument("--approve", help="Approve drafts: category name")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show claim distribution per sub-page without compiling")
    args = parser.parse_args()

    if args.dry_run:
        cats = [args.category] if args.category else list(SUBPAGE_DEFS.keys())
        for cat in cats:
            claims, _ = collect_claims(cat)
            claims = _deduplicate_claims(claims)
            subpages = SUBPAGE_DEFS.get(cat, [])
            print(f"\n{'═'*50}")
            print(f"  {cat.upper()} — {len(claims)} claims (deduped)")
            print(f"{'═'*50}")
            for sp in subpages:
                page_claims = _filter_claims(claims, sp["filter"])
                print(f"  {sp['filename']:25} → {len(page_claims):>4} claims")
        return

    if args.approve:
        result = approve_draft(args.approve)
        print(f"Approve result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    elif args.all:
        all_results = {}
        for cat in SUBPAGE_DEFS.keys():
            print(f"\n{'='*50}")
            print(f"Compiling: {cat}")
            result = compile_category(cat)
            all_results[cat] = result
            print(f"  → {result['status']}: {result.get('pages_compiled', 0)} pages")
        print(f"\n{'='*50}")
        print("ALL DONE")
        total_cost = sum(r.get("cost_usd", 0) for r in all_results.values())
        print(f"Total cost: ${total_cost:.4f}")
    elif args.category:
        result = compile_category(args.category)
        print(f"\nResult: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
