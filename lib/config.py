"""
BKNS Agent Wiki — Central Configuration
Loads .env, defines paths, constants, model selection.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ── Workspace Root ─────────────────────────────────────────
WORKSPACE = Path(os.getenv("WIKI_WORKSPACE", "/home/openclaw/wiki"))

# ── Directory Paths ────────────────────────────────────────
RAW_DIR = WORKSPACE / "raw"
RAW_CRAWL_DIR = RAW_DIR / "website-crawl"
RAW_MANUAL_DIR = RAW_DIR / "manual"

CLAIMS_DIR = WORKSPACE / "claims"
CLAIMS_DRAFTS_DIR = CLAIMS_DIR / ".drafts"
CLAIMS_APPROVED_DIR = CLAIMS_DIR / "approved"

ENTITIES_DIR = WORKSPACE / "entities"
SOURCES_DIR = WORKSPACE / "sources"

WIKI_DIR = WORKSPACE / "wiki"
WIKI_DRAFTS_DIR = WIKI_DIR / ".drafts"

BUILD_DIR = WORKSPACE / "build"
BUILD_MANIFESTS_DIR = BUILD_DIR / "manifests"

ASSETS_DIR = WORKSPACE / "assets"
EVIDENCE_DIR = ASSETS_DIR / "evidence" / "price-screens"
IMAGES_DIR = ASSETS_DIR / "images"

LOGS_DIR = WORKSPACE / "logs"
LOGS_INTAKE_DIR = LOGS_DIR / "intake"
LOGS_ERRORS_DIR = LOGS_DIR / "errors"
LOGS_LINT_DIR = LOGS_DIR / "lint"
LOGS_GROUND_TRUTH_DIR = LOGS_DIR / "ground-truth"

SKILLS_DIR = WORKSPACE / "skills"
TOOLS_DIR = WORKSPACE / "tools"

# ── Registry Files ─────────────────────────────────────────
ENTITIES_REGISTRY = ENTITIES_DIR / "registry.yaml"
SOURCES_REGISTRY = SOURCES_DIR / "registry.yaml"
CLAIMS_REGISTRY = CLAIMS_DIR / "registry.yaml"
ACTIVE_BUILD = BUILD_DIR / "active-build.yaml"

# ── Vertex AI ──────────────────────────────────────────────
GOOGLE_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(WORKSPACE / "api" / "vertex-key.json")
)
GOOGLE_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "ai-test-491016")
GOOGLE_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# ── Models ─────────────────────────────────────────────────
# gemini-2.5-flash: GA, fast, cost-effective
MODEL_FLASH = os.getenv("MODEL_FLASH", "gemini-2.5-flash")
# gemini-2.5-pro: GA stable — default PRO model
# [C6] Default to gemini-2.5-pro (GA). Override via MODEL_PRO env var if needed.
MODEL_PRO = os.getenv("MODEL_PRO", "gemini-2.5-pro")
# gemini-3.1-pro-preview: PART 04 upgrade target — stronger reasoning, 1M context
MODEL_PRO_NEW = os.getenv("MODEL_PRO_NEW", "gemini-3.1-pro-preview")
# Feature flag: set USE_PRO_NEW=true in .env after A/B test passes
USE_PRO_NEW = os.getenv("USE_PRO_NEW", "false").lower() == "true"
# gemini-3.1-pro-preview chỉ available qua 'global' routing endpoint (không phải us-central1)
MODEL_PRO_NEW_LOCATION = os.getenv("MODEL_PRO_NEW_LOCATION", "global")


def get_pro_model() -> str:
    """Return the active Pro model based on the USE_PRO_NEW feature flag.

    USE_PRO_NEW=false (default) → MODEL_PRO  (gemini-2.5-pro, stable GA)
    USE_PRO_NEW=true            → MODEL_PRO_NEW (gemini-3.1-pro-preview, upgrade)

    Rollback: set USE_PRO_NEW=false in .env + pm2 restart all
    """
    return MODEL_PRO_NEW if USE_PRO_NEW else MODEL_PRO


# Model assignment per skill (theo spec 00-MASTER.md)
# NOTE: skills that call generate(model=MODEL_PRO) should use get_pro_model()
# instead, so the feature flag is respected at call time.
SKILL_MODELS = {
    "query-wiki": MODEL_FLASH,       # $0.30/$2.50 per 1M — queries
    "crawl-source": None,             # No LLM — pure script
    "extract-claims": MODEL_PRO,      # $1.25/$10 per 1M — extraction
    "compile-wiki": MODEL_PRO,        # $1.25/$10 per 1M — compilation
    "ingest-image": MODEL_FLASH,      # Vision task
    "lint-wiki": MODEL_PRO,           # Semantic lint
    "ground-truth": MODEL_FLASH,      # Verification
    "auto-file": MODEL_FLASH,         # FAQ filing
    "cross-link": MODEL_FLASH,        # Cross-linking
    "build-snapshot": None,            # No LLM — pure script
    "librarian-chat": MODEL_PRO,       # $1.25/$10 per 1M — conversational assistant
    "librarian-classify": MODEL_PRO,   # $1.25/$10 per 1M — strict-JSON classification
}

# ── Telegram ───────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# [C3] No hardcoded default — must be set via .env to prevent privilege escalation.
# If unset, admin commands in the bot will be blocked for all users (safe default).
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "")

# ── BKNS Contact (Ground Truth — KHÔNG thay đổi) ──────────
BKNS_HOTLINE_KY_THUAT = "1900 63 68 09"  # Có phí
BKNS_HOTLINE_KINH_DOANH = "1800 646 884"  # Miễn phí
BKNS_WEBSITE = "https://bkns.vn"

# ── Quality Gates ──────────────────────────────────────────
# NOTE: CRAWL_RULES là reference config — các giá trị được đọc trực tiếp
# bởi tools/crawl_bkns.py và skills/crawl-source/scripts/crawl.py
# Không xóa — dùng cho documentation và future validation layer
CRAWL_RULES = {
    "url_scheme": ["http", "https"],
    "warn_if_not_bkns": True,
    "duplicate_window_hours": 24,
    "content_hash_check": True,
    "min_word_count": 100,
    "timeout_seconds": 30,
    "max_retries": 1,
}

CLAIM_REQUIRED_FIELDS = [
    "entity_id", "attribute", "value", "confidence"
]

CLAIM_HIGH_RISK_ATTRIBUTES = [
    "monthly_price", "yearly_price", "one_time_price",
    "hotline", "email", "address", "website",
    "sla_uptime", "refund_policy",
]

SELF_REVIEW_RULES = {
    "check_every_number": True,
    "check_hallucination": True,
    "auto_correct": True,
    "max_auto_corrections": 3,
    "block_if_hallucination": True,
}

LINT_RULES = {
    "require_frontmatter": True,
    "required_fields": ["title", "category", "updated"],
    "stale_threshold_days": 30,
    "min_body_length": 50,
    "check_broken_images": True,
    "check_orphan_files": True,
    "check_price_conflicts": True,
    "check_outdated_info": True,
    "check_missing_sources": True,
    "suggest_improvements": 5,
}

# ── Category Mapping ──────────────────────────────────────
CATEGORY_MAP = {
    "hosting": "products/hosting",
    "vps": "products/vps",
    "ten-mien": "products/ten-mien",
    "domain": "products/ten-mien",
    "email": "products/email",
    "ssl": "products/ssl",
    "server": "products/server",
    "software": "products/software",
    "gioi-thieu": "company",
    "lien-he": "support",
    "ho-tro": "support",
    "chinh-sach": "policies",
}

# ── OpenAI — PART 05 (dual-vote with GPT-5.4) ──────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
OPENAI_MODEL_MINI = os.getenv("OPENAI_MODEL_MINI", "gpt-5.4-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "120"))

# ── Dual-Vote (PART 06) ────────────────────────────────────
# Feature flag: set true AFTER smoke test + unit tests pass
DUAL_VOTE_ENABLED = os.getenv("DUAL_VOTE_ENABLED", "false").lower() == "true"
# Agreement thresholds (mirrors vote.py — keep in sync)
DUAL_VOTE_THRESHOLD_AGREE = float(os.getenv("DUAL_VOTE_THRESHOLD_AGREE", "0.9"))
DUAL_VOTE_THRESHOLD_PARTIAL = float(os.getenv("DUAL_VOTE_THRESHOLD_PARTIAL", "0.6"))
# High-stakes categories: always use dual-vote regardless of flag
DUAL_VOTE_HIGH_STAKES = {"hosting", "vps", "ssl", "ten-mien", "email", "server"}
# Review queue: flagged sections land here for human review
REVIEW_QUEUE_DIR = WORKSPACE / ".review-queue"

# ── Budget ─────────────────────────────────────────────────
MONTHLY_BUDGET_USD = 50.0  # Kill criteria: >$50/tháng → dừng
MAX_QUERY_COST_USD = 0.01  # Alert nếu 1 query > $0.01
