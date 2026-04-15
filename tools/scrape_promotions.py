#!/usr/bin/env python3
"""
BKNS Wiki — Weekly Promotion Scraper
Scrapes https://www.bkns.vn/khuyen-mai.html and updates wiki/khuyen-mai/index.md

Usage:
    python3 tools/scrape_promotions.py           # Scrape and update wiki
    python3 tools/scrape_promotions.py --dry-run  # Preview without writing

Schedule: Weekly (via cron_tasks.py `promo-scrape`)
"""
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("⚠️  Missing deps. Run: pip install requests beautifulsoup4")
    sys.exit(1)

from lib.telegram import notify_skill

WIKI_ROOT = Path(__file__).resolve().parent.parent
PROMO_PAGE = WIKI_ROOT / "wiki" / "khuyen-mai" / "index.md"
PROMO_URL = "https://www.bkns.vn/khuyen-mai.html"
VN_DOMAIN_URL = "https://www.bkns.vn/ten-mien/ten-mien-vn.html"
LOGS_DIR = WIKI_ROOT / "logs"
LOG_FILE = LOGS_DIR / "promo-scrape.jsonl"


def scrape_promotions() -> list[dict]:
    """Scrape promotion page and extract promos."""
    headers = {
        "User-Agent": "BKNS-Wiki-Bot/1.0 (internal; weekly-scrape)"
    }
    resp = requests.get(PROMO_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    promos = []

    # Find promotion cards/articles — BKNS uses .sale-item or article cards
    # Fallback: search for links containing /sale/
    sale_links = soup.find_all("a", href=re.compile(r"/sale/"))
    seen_urls = set()

    for link in sale_links:
        href = link.get("href", "")
        if href in seen_urls or not href.startswith("https://"):
            if href.startswith("/"):
                href = "https://www.bkns.vn" + href
            elif not href.startswith("http"):
                continue

        if href in seen_urls:
            continue
        seen_urls.add(href)

        # Extract title from the link text
        title_text = link.get_text(strip=True)
        if not title_text or len(title_text) < 10:
            continue

        # Clean title — remove trailing numbers and dates
        title_clean = re.sub(r"\d{2}/\d{2}/\d{4}\s*\d*\s*$", "", title_text).strip()
        if not title_clean:
            continue

        # Try to find date from surrounding text
        parent = link.parent
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", parent.get_text() if parent else "")
        date_str = date_match.group(1) if date_match else ""

        # Try to find view count
        view_match = re.search(r"(\d+)\s*$", title_text)
        views = int(view_match.group(1)) if view_match else 0

        promo = {
            "title": title_clean[:100],
            "url": href,
            "date": date_str,
            "views": views,
        }
        promos.append(promo)

    # Deduplicate by URL
    final = {}
    for p in promos:
        url = p["url"]
        if url not in final or len(p["title"]) > len(final[url]["title"]):
            final[url] = p

    return list(final.values())


def classify_product(title: str) -> str:
    """Classify promotion by product type."""
    title_lower = title.lower()
    if "ssl" in title_lower or "sectigo" in title_lower or "geotrust" in title_lower:
        return "SSL"
    if "vps" in title_lower or "cloud" in title_lower or "openclaw" in title_lower:
        return "VPS"
    if "hosting" in title_lower:
        return "Hosting"
    if "tên miền" in title_lower or "domain" in title_lower or ".com" in title_lower or ".net" in title_lower:
        return "Tên miền"
    if "website" in title_lower:
        return "Website"
    if "email" in title_lower:
        return "Email"
    return "Đa dịch vụ"


def classify_status(date_str: str) -> str:
    """Classify status based on how old the promo is."""
    if not date_str:
        return "🟡 Cần verify"
    try:
        promo_date = datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        return "🟡 Cần verify"

    now = datetime.now()
    days_old = (now - promo_date).days

    if days_old < 60:
        return "🟢 Đang chạy"
    elif days_old < 120:
        return "🟡 Cần verify"
    else:
        return "🔴 Có thể hết hạn"


def generate_markdown(promos: list[dict]) -> str:
    """Generate the wiki markdown from scraped promotions."""
    now = datetime.now(tz=timezone.utc)
    next_check = now + timedelta(days=7)

    lines = [
        "---",
        "page_id: wiki.khuyen-mai.index",
        'title: "Khuyến mãi BKNS"',
        "category: marketing",
        f"updated: '{now.strftime('%Y-%m-%d')}'",
        "review_state: verified",
        f"claims_used: {len(promos)}",
        "source_urls:",
        "  - https://www.bkns.vn/khuyen-mai.html",
        f"last_scraped: '{now.isoformat()}'",
        "auto_update: weekly",
        f"next_check: '{next_check.strftime('%Y-%m-%d')}'",
        "---",
        "",
        "",
        "# Khuyến mãi BKNS",
        "",
        "> Tổng hợp các chương trình khuyến mãi tên miền .VN, Hosting, Cloud VPS, SSL tại BKNS. Cập nhật liên tục mỗi tuần.",
        ">",
        f"> **Nguồn:** [bkns.vn/khuyen-mai.html]({PROMO_URL})",
        ">",
        f"> **Cập nhật lần cuối:** {now.strftime('%Y-%m-%d')} • **Lần kiểm tra tiếp theo:** {next_check.strftime('%Y-%m-%d')}",
        "",
        "## Chương trình khuyến mãi đang diễn ra",
        "",
        "| # | Tên chương trình | Ngày đăng | Áp dụng cho | Lượt xem | Link nguồn | Trạng thái |",
        "|---|---|---|---|---|---|---|",
    ]

    # Categorize promos
    by_product = {}
    for i, p in enumerate(promos, 1):
        product = classify_product(p["title"])
        status = classify_status(p["date"])
        views_str = f"{p['views']:,}" if p["views"] > 0 else "—"
        date_str = p["date"] if p["date"] else "—"

        lines.append(
            f"| {i} | {p['title']} | {date_str} | {product} | {views_str} | "
            f"[Chi tiết]({p['url']}) | {status} |"
        )

        by_product.setdefault(product, []).append(p)

    lines.extend([
        "",
        "> **Ghi chú trạng thái:**",
        "> - 🟢 **Mới / Đang chạy** — Chương trình mới đăng (trong 60 ngày gần đây)",
        "> - 🟡 **Cần verify** — Đăng 60–120 ngày trước, cần kiểm tra còn hiệu lực",
        "> - 🔴 **Có thể hết hạn** — Đăng >120 ngày trước, khả năng cao đã hết hạn",
        "",
        "## Khuyến mãi nổi bật theo sản phẩm",
        "",
    ])

    for product, items in by_product.items():
        lines.append(f"### {product}")
        for p in items[:3]:  # Top 3 per product
            lines.append(f"- **{p['title']}** → [Chi tiết]({p['url']})")
        lines.append("")

    lines.extend([
        "## Quy tắc cập nhật",
        "",
        "- Trang này được **tự động kiểm tra mỗi tuần** qua cron task `promo-scrape`",
        "- Khi phát hiện khuyến mãi mới, sẽ gửi thông báo qua Telegram",
        "- Mỗi chương trình phải có ngày đăng và link nguồn",
        "- Trạng thái tự động đánh giá dựa trên thời gian: <60 ngày = 🟢, 60-120 ngày = 🟡, >120 ngày = 🔴",
        "",
        "## Sản phẩm liên quan",
        "",
        "- [Trang chủ wiki](../index.md)",
        "- [Bảng giá Tên miền](../products/ten-mien/bang-gia.md)",
        "- [So sánh tổng hợp](../so-sanh-tong-hop.md)",
        "- [Liên hệ BKNS](../support/lien-he.md)",
        "",
        "---",
        f"*Auto-scraped by BKNS Wiki Bot • {now.strftime('%Y-%m-%d')} • Source: bkns.vn/khuyen-mai.html*",
    ])

    return "\n".join(lines) + "\n"


def load_existing_urls() -> set:
    """Load URLs from current wiki page."""
    if not PROMO_PAGE.exists():
        return set()
    content = PROMO_PAGE.read_text(encoding="utf-8")
    return set(re.findall(r"https://www\.bkns\.vn/sale/[^\s\)]+", content))


def log_scrape(status: str, detail: str, new_count: int = 0):
    """Log scrape results."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "task": "promo-scrape",
        "status": status,
        "new_promos": new_count,
        "detail": detail[:200],
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="BKNS Promotion Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    print(f"🔍 Scraping promotions from {PROMO_URL}...")

    try:
        promos = scrape_promotions()
    except Exception as e:
        msg = f"❌ Scrape failed: {e}"
        print(msg)
        log_scrape("error", str(e))
        return 1

    if not promos:
        print("⚠️  No promotions found")
        log_scrape("empty", "No promos extracted")
        return 1

    print(f"✅ Found {len(promos)} promotions")

    # Check for new promos
    existing_urls = load_existing_urls()
    new_urls = {p["url"] for p in promos} - existing_urls
    new_promos = [p for p in promos if p["url"] in new_urls]

    if new_promos:
        print(f"🆕 {len(new_promos)} NEW promotions detected!")
        for p in new_promos:
            print(f"   → {p['title']}")
    else:
        print("ℹ️  No new promotions since last check")

    # Generate updated markdown
    md = generate_markdown(promos)

    if args.dry_run:
        print("\n--- DRY RUN (preview) ---")
        print(md[:500])
        print("...")
        return 0

    # Write to wiki
    PROMO_PAGE.parent.mkdir(parents=True, exist_ok=True)
    PROMO_PAGE.write_text(md, encoding="utf-8")
    print(f"📝 Updated {PROMO_PAGE.relative_to(WIKI_ROOT)}")

    # Notify if new promos found
    if new_promos:
        titles = "\n".join(f"• {p['title']}" for p in new_promos[:5])
        notify_skill(
            "promo-scrape",
            f"🆕 {len(new_promos)} khuyến mãi mới:\n{titles}",
            severity="medium",
        )

    log_scrape("success", f"total={len(promos)} new={len(new_promos)}", len(new_promos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
