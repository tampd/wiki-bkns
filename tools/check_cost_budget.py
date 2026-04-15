#!/usr/bin/env python3
"""
BKNS Agent Wiki — Cost budget checker (v0.4)

Đọc cost-guard.yaml + log files (logs/extract-claims-*.jsonl, logs/compile-wiki-*.jsonl)
để tính cumulative cost trong tháng hiện tại. Raise CostBudgetExceededError khi vượt ngưỡng.

Sử dụng:
    # CLI
    python3 tools/check_cost_budget.py
    python3 tools/check_cost_budget.py --simulate-pct 80

    # Trong pipeline (PART 04)
    from tools.check_cost_budget import assert_within_budget
    assert_within_budget(skill='extract-claims', max_per_build=15.00)
"""
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

import yaml

ROOT = Path(__file__).resolve().parent.parent
COST_GUARD_FILE = ROOT / "trienkhai" / "upgrade-v0.4" / "cost-guard.yaml"
LOGS_DIR = ROOT / "logs"


class CostBudgetExceededError(RuntimeError):
    pass


def load_config() -> dict:
    return yaml.safe_load(COST_GUARD_FILE.read_text(encoding="utf-8"))


def cumulative_cost_since(start_date: str, skill_prefix: str = None) -> float:
    """Sum cost_usd from log entries with ts >= start_date (YYYY-MM-DD)."""
    total = 0.0
    for log in LOGS_DIR.glob("*.jsonl"):
        if skill_prefix and not log.name.startswith(skill_prefix):
            continue
        try:
            for line in log.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                d = json.loads(line)
                ts = d.get("ts", "")
                if ts[:10] >= start_date:
                    total += d.get("cost_usd", 0) or 0
        except (OSError, json.JSONDecodeError):
            continue
    return round(total, 4)


def assert_within_budget(skill: str = None, max_per_build: float = None):
    cfg = load_config()
    vertex_cap = cfg["budgets"]["vertex_ai"]["monthly_hard_cap_usd"]
    openai_cap = cfg["budgets"]["openai"]["monthly_hard_cap_usd"]
    combined_cap = vertex_cap + openai_cap
    start = cfg.get("v04_start_date", datetime.now().strftime("%Y-%m-01"))

    spent = cumulative_cost_since(start)
    pct = spent / combined_cap * 100 if combined_cap else 0

    if spent >= combined_cap:
        raise CostBudgetExceededError(
            f"Monthly budget exceeded: {spent:.2f} USD / {combined_cap:.2f} USD cap"
        )

    # Per-build check (uses cost from current build_id, simplified: today's logs only)
    if max_per_build is not None:
        today = datetime.now().strftime("%Y-%m-%d")
        today_total = 0.0
        for log in LOGS_DIR.glob(f"*{today}.jsonl"):
            try:
                for line in log.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    today_total += json.loads(line).get("cost_usd", 0) or 0
            except (OSError, json.JSONDecodeError):
                continue
        if today_total >= max_per_build:
            raise CostBudgetExceededError(
                f"Per-build cap exceeded: today {today_total:.2f} USD ≥ {max_per_build:.2f} USD"
            )

    return {
        "spent_usd": spent,
        "cap_usd": combined_cap,
        "pct": round(pct, 1),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate-pct", type=float, help="Simulate spend at given pct of cap")
    args = parser.parse_args()

    cfg = load_config()
    vertex_cap = cfg["budgets"]["vertex_ai"]["monthly_hard_cap_usd"]
    openai_cap = cfg["budgets"]["openai"]["monthly_hard_cap_usd"]
    cap = vertex_cap + openai_cap

    if args.simulate_pct is not None:
        spent = cap * args.simulate_pct / 100
        print(f"[SIMULATE] spent={spent:.2f} cap={cap:.2f} pct={args.simulate_pct:.1f}%")
        return 0

    status = assert_within_budget()
    print(f"Spent: ${status['spent_usd']:.2f} / ${status['cap_usd']:.2f} cap ({status['pct']:.1f}%)")
    if status["pct"] >= 75:
        print("⚠️  WARNING: ≥75% of monthly budget consumed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
