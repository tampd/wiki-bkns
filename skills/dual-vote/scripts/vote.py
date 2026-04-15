#!/usr/bin/env python3
"""
Dual-Vote CLI — thin wrapper around lib.dual_vote.run_dual.
Run directly: python3 skills/dual-vote/scripts/vote.py "your prompt"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.dual_vote import run_dual  # noqa: F401 — re-export for direct import


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dual-agent vote on a prompt")
    parser.add_argument("prompt", nargs="?", default="Dịch vụ hosting BKNS có giá bao nhiêu?")
    parser.add_argument("--system", default="Bạn là AI tư vấn dịch vụ BKNS.")
    parser.add_argument("--skill", default="dual-vote-cli")
    args = parser.parse_args()

    print(f"Running dual-vote on: {args.prompt[:80]}")
    result = run_dual(args.prompt, system=args.system, skill=args.skill)

    print(f"\nStatus    : {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Score     : {result['score']}")
    print(f"Flag      : {result['flag']}")
    print(f"Cost      : ${result['cost_usd_total']:.6f} (A=${result['cost_usd_a']:.6f} B=${result['cost_usd_b']:.6f})")
    print(f"Elapsed   : {result['elapsed_ms']} ms")

    if "consensus" in result:
        print(f"\n── Consensus ({result['model_a']}) ──")
        print(result["consensus"]["text"][:400])
    elif "agent_a" in result:
        print(f"\n── Agent A ({result['model_a']}) ──")
        print(result["agent_a"]["text"][:200])
        print(f"\n── Agent B ({result['model_b']}) ──")
        print(result["agent_b"]["text"][:200])
