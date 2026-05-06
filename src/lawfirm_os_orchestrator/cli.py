from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.commands.classify_exception import run as run_classify_exception


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
    parser.error("unknown command")
    return 2
