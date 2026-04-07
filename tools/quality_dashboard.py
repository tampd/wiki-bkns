#!/usr/bin/env python3
"""
BKNS Wiki — Quality Dashboard

Calculates and displays quality metrics for the entire wiki.
Sends summary via Telegram.

Usage:
    python3 tools/quality_dashboard.py          # Full dashboard
    python3 tools/quality_dashboard.py --brief   # Quick summary
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import (
    CLAIMS_APPROVED_DIR, CLAIMS_DRAFTS_DIR, WIKI_DIR, LOGS_DIR,
)
from lib.utils import (
    ensure_dir, now_iso, today_str, read_text_safe, parse_frontmatter,
)
from lib.telegram import send_report

VN_TZ = timezone(timedelta(hours=7))
CATEGORIES = ["hosting", "vps", "email", "ssl", "ten-mien", "server", "software"]


def count_claims() -> dict:
    """Count claims by category and confidence."""
    stats = defaultdict(lambda: defaultdict(int))
    total = 0
    
    for yaml_file in CLAIMS_APPROVED_DIR.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                claim = yaml.safe_load(f)
            if claim and isinstance(claim, dict):
                # Extract category from path
                rel = yaml_file.relative_to(CLAIMS_APPROVED_DIR)
                parts = rel.parts
                cat = parts[1] if len(parts) > 1 else "other"
                
                confidence = claim.get("confidence", "unknown")
                stats[cat][confidence] += 1
                stats[cat]["total"] += 1
                total += 1
        except Exception:
            continue
    
    stats["_total"] = {"total": total}
    return dict(stats)


def count_wiki_pages() -> dict:
    """Count wiki pages and check for skeleton/empty pages."""
    stats = defaultdict(lambda: {"total": 0, "content": 0, "skeleton": 0, "empty": 0})
    
    for md_file in WIKI_DIR.rglob("*.md"):
        if ".drafts" in str(md_file):
            continue
        
        rel = md_file.relative_to(WIKI_DIR)
        parts = rel.parts
        cat = parts[1] if len(parts) > 1 else "other"
        
        content = read_text_safe(str(md_file))
        fm, body = parse_frontmatter(content)
        
        stats[cat]["total"] += 1
        
        if "Đang cập nhật" in body and len(body.strip()) < 200:
            stats[cat]["skeleton"] += 1
        elif len(body.strip()) < 50:
            stats[cat]["empty"] += 1
        else:
            stats[cat]["content"] += 1
    
    return dict(stats)


def get_verification_stats() -> dict:
    """Get latest verification report stats."""
    verify_dir = LOGS_DIR / "verify"
    if not verify_dir.exists():
        return {}
    
    reports = sorted(verify_dir.glob("verify-*.json"), reverse=True)
    if not reports:
        return {}
    
    with open(reports[0], "r", encoding="utf-8") as f:
        return json.load(f)


def get_audit_stats() -> dict:
    """Get latest audit report stats."""
    audit_dir = LOGS_DIR / "audit"
    if not audit_dir.exists():
        return {}
    
    reports = sorted(audit_dir.glob("audit-*.json"), reverse=True)
    if not reports:
        return {}
    
    with open(reports[0], "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_scores(claim_stats: dict, page_stats: dict, 
                     verify_stats: dict, audit_stats: dict) -> dict:
    """Calculate overall quality scores."""
    total_claims = sum(v.get("total", 0) for k, v in claim_stats.items() if k != "_total")
    gt_claims = sum(v.get("ground_truth", 0) for k, v in claim_stats.items() if k != "_total")
    
    total_pages = sum(v.get("total", 0) for v in page_stats.values())
    content_pages = sum(v.get("content", 0) for v in page_stats.values())
    skeleton_pages = sum(v.get("skeleton", 0) for v in page_stats.values())
    
    # Accuracy = ground truth claims / total
    accuracy = (gt_claims / total_claims * 100) if total_claims else 0
    
    # Coverage = content pages / total pages
    coverage = (content_pages / total_pages * 100) if total_pages else 0
    
    # Verification score from latest report
    verify_score = 0
    if verify_stats:
        total_checks = verify_stats.get("total_checks", 0)
        critical = verify_stats.get("critical_issues", 0)
        verify_score = ((total_checks - critical) / total_checks * 100) if total_checks else 100
    
    # Audit score from latest report
    audit_score = audit_stats.get("avg_score", 0) if audit_stats else 0
    
    return {
        "accuracy": round(accuracy, 1),
        "coverage": round(coverage, 1),
        "verification": round(verify_score, 1),
        "audit": round(audit_score, 1),
        "overall": round((accuracy * 0.3 + coverage * 0.2 + verify_score * 0.3 + audit_score * 0.2), 1),
        "total_claims": total_claims,
        "gt_claims": gt_claims,
        "total_pages": total_pages,
        "content_pages": content_pages,
        "skeleton_pages": skeleton_pages,
    }


def format_dashboard(scores: dict, claim_stats: dict, page_stats: dict, brief: bool = False) -> str:
    """Format dashboard as text."""
    out = []
    out.append("📊 BKNS Wiki Quality Dashboard")
    out.append(f"   {datetime.now(VN_TZ).strftime('%Y-%m-%d %H:%M %Z')}")
    out.append("═" * 40)
    
    # Overall score with emoji
    overall = scores["overall"]
    if overall >= 90:
        grade = "🟢 Excellent"
    elif overall >= 75:
        grade = "🟡 Good"
    elif overall >= 60:
        grade = "🟠 Fair"
    else:
        grade = "🔴 Needs Work"
    
    out.append(f"\n🎯 Overall: {overall}/100 — {grade}")
    out.append(f"   📐 Accuracy (GT claims):    {scores['accuracy']}%")
    out.append(f"   📄 Coverage (content pages): {scores['coverage']}%")
    out.append(f"   ✅ Verification:             {scores['verification']}%")
    out.append(f"   🔍 Audit:                    {scores['audit']}%")
    
    out.append(f"\n📋 Claims: {scores['total_claims']} total ({scores['gt_claims']} ground truth)")
    out.append(f"📄 Pages:  {scores['total_pages']} total ({scores['content_pages']} content, {scores['skeleton_pages']} skeleton)")
    
    if not brief:
        out.append(f"\n{'─' * 40}")
        out.append("Claims by Category:")
        for cat in CATEGORIES:
            stats = claim_stats.get(cat, {})
            if stats:
                gt = stats.get("ground_truth", 0)
                high = stats.get("high", 0)
                total = stats.get("total", 0)
                out.append(f"  {cat:12s}: {total:4d} claims ({gt} GT, {high} high)")
        
        out.append(f"\n{'─' * 40}")
        out.append("Pages by Category:")
        for cat in CATEGORIES:
            stats = page_stats.get(cat, {})
            if stats:
                content = stats.get("content", 0)
                skeleton = stats.get("skeleton", 0)
                total = stats.get("total", 0)
                pct = (content / total * 100) if total else 0
                out.append(f"  {cat:12s}: {total:3d} pages ({content} content, {skeleton} skeleton) [{pct:.0f}%]")
    
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="BKNS Wiki Quality Dashboard")
    parser.add_argument("--brief", "-b", action="store_true", help="Brief summary")
    parser.add_argument("--telegram", "-t", action="store_true", help="Send to Telegram")
    args = parser.parse_args()
    
    print("📊 Calculating quality metrics...\n")
    
    claim_stats = count_claims()
    page_stats = count_wiki_pages()
    verify_stats = get_verification_stats()
    audit_stats = get_audit_stats()
    
    scores = calculate_scores(claim_stats, page_stats, verify_stats, audit_stats)
    dashboard = format_dashboard(scores, claim_stats, page_stats, brief=args.brief)
    
    print(dashboard)
    
    # Save report
    ensure_dir(LOGS_DIR / "quality")
    report = {
        "ts": now_iso(),
        "scores": scores,
        "claims": dict(claim_stats),
        "pages": dict(page_stats),
    }
    report_path = LOGS_DIR / "quality" / f"quality-{today_str()}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    if args.telegram:
        send_report("Wiki Quality Dashboard", dashboard)
        print(f"\n📱 Sent to Telegram")
    
    print(f"\n📁 Report saved: {report_path}")


if __name__ == "__main__":
    main()
