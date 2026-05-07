from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.commands.autonomy_harness import run_classify_autonomy, run_select_harness
from lawfirm_os_orchestrator.commands.classify_exception import run as run_classify_exception
from lawfirm_os_orchestrator.commands.learning import run as run_learning
from lawfirm_os_orchestrator.commands.research_radar import run as run_research_radar


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lawfirm-os-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)
    autonomy = sub.add_parser("classify-autonomy")
    autonomy.add_argument("--action", required=True)
    autonomy.add_argument("--out", required=True)
    autonomy.add_argument("--stdout", choices=["json", "text"], default="text")
    harness = sub.add_parser("select-harness")
    harness.add_argument("--autonomy", required=True)
    harness.add_argument("--scorecard", required=True)
    harness.add_argument("--out", required=True)
    harness.add_argument("--stdout", choices=["json", "text"], default="text")
    classify = sub.add_parser("classify-exception")
    classify.add_argument("--input", required=True)
    classify.add_argument("--substrate", default="tests/fixtures/substrate")
    classify.add_argument("--ledger-dir", default=".lawfirm-os-orchestrator/ledger")
    classify.add_argument("--packet-out", default=".lawfirm-os-orchestrator/runs")
    classify.add_argument("--lake-mode", choices=["disabled", "dry-run", "runtime-safe"], default="disabled")
    classify.add_argument("--stdout", choices=["json", "text"], default="json")

    radar = sub.add_parser("research-radar")
    radar_sub = radar.add_subparsers(dest="research_command", required=True)
    import_local = radar_sub.add_parser("import-local")
    import_local.add_argument("--input", required=True)
    import_local.add_argument("--out", default=".lawfirm-os-orchestrator/research/signals.jsonl")
    import_local.add_argument("--stdout", choices=["json", "text"], default="text")
    list_signals = radar_sub.add_parser("list-signals")
    list_signals.add_argument("--signals", default=".lawfirm-os-orchestrator/research/signals.jsonl")
    list_signals.add_argument("--stdout", choices=["json", "text"], default="text")

    learning = sub.add_parser("learning")
    learning_sub = learning.add_subparsers(dest="learning_command", required=True)
    shadow = learning_sub.add_parser("run-shadow-eval")
    shadow.add_argument("--proposal", required=True)
    shadow.add_argument("--fixture", default="evals/fixtures/classify_exception_cases.jsonl")
    shadow.add_argument("--gold", default="evals/gold/classify_exception_gold.jsonl")
    shadow.add_argument("--substrate", default="tests/fixtures/substrate")
    shadow.add_argument("--artifacts", default=".lawfirm-os-orchestrator/shadow_eval/artifacts")
    shadow.add_argument("--out", default=".lawfirm-os-orchestrator/shadow_eval/latest_shadow_eval.json")
    shadow.add_argument("--stdout", choices=["json", "text"], default="text")
    proposal = learning_sub.add_parser("build-upgrade-proposal")
    proposal.add_argument("--input", required=True)
    proposal.add_argument("--out", default=".lawfirm-os-orchestrator/upgrade_proposals")
    proposal.add_argument("--stdout", choices=["json", "text"], default="text")
    task = learning_sub.add_parser("render-codex-task")
    task.add_argument("--input", required=True)
    task.add_argument("--out", default=".lawfirm-os-orchestrator/codex_task_drafts/example")
    task.add_argument("--stdout", choices=["json", "text"], default="text")
    insight = learning_sub.add_parser("score-insight")
    insight.add_argument("--input", required=True)
    insight.add_argument("--out")
    insight.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "classify-autonomy":
        code, summary = run_classify_autonomy(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "select-harness":
        code, summary = run_select_harness(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "classify-exception":
        code, summary = run_classify_exception(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "research-radar":
        code, summary = run_research_radar(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "learning":
        code, summary = run_learning(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    parser.error("unknown command")
    return 2
