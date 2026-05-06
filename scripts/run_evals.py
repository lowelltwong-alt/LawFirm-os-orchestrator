from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.evals.runner import run_eval_suite
from lawfirm_os_orchestrator.util.json_io import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run offline LawFirm OS Orchestrator evals.")
    parser.add_argument("--fixture", default="evals/fixtures/classify_exception_cases.jsonl")
    parser.add_argument("--gold", default="evals/gold/classify_exception_gold.jsonl")
    parser.add_argument("--substrate", default="tests/fixtures/substrate")
    parser.add_argument("--artifacts", default=".lawfirm-os-orchestrator/evals/artifacts")
    parser.add_argument("--out", default=".lawfirm-os-orchestrator/evals/latest_metrics.json")
    parser.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_eval_suite(
        fixture_path=Path(args.fixture),
        gold_path=Path(args.gold),
        substrate_root=Path(args.substrate),
        artifact_root=Path(args.artifacts),
    )
    write_json(Path(args.out), result)
    if args.stdout == "json":
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        metrics = result["metrics"]
        print(
            "classify_exception "
            f"cases={metrics['total_cases']} "
            f"route_exact={metrics['route_exact_match_rate']:.3f} "
            f"event_class_exact={metrics['event_class_exact_match_rate']:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
