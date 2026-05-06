from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.commands.classify_exception import run as run_classify_exception
from lawfirm_os_orchestrator.commands.research_radar import run as run_research_radar


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lawfirm-os-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
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
    parser.error("unknown command")
    return 2
