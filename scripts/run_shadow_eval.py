from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.evals.shadow import run_shadow_eval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run proposal-only shadow evals for LawFirm OS Orchestrator.")
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--fixture", default="evals/fixtures/classify_exception_cases.jsonl")
    parser.add_argument("--gold", default="evals/gold/classify_exception_gold.jsonl")
    parser.add_argument("--substrate", default="tests/fixtures/substrate")
    parser.add_argument("--artifacts", default=".lawfirm-os-orchestrator/shadow_eval/artifacts")
    parser.add_argument("--out", default=".lawfirm-os-orchestrator/shadow_eval/latest_shadow_eval.json")
    parser.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_shadow_eval(
        proposal_path=Path(args.proposal),
        fixture_path=Path(args.fixture),
        gold_path=Path(args.gold),
        substrate_root=Path(args.substrate),
        artifact_root=Path(args.artifacts),
        out_path=Path(args.out),
    )
    if args.stdout == "json":
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        shadow = result["shadow_eval_result"]
        print(
            "shadow_eval "
            f"proposal={result['proposal_id']} "
            f"action={shadow['recommended_next_action']} "
            f"regressions={len(shadow['regression_warnings'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
