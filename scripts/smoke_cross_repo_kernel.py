from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from lawfirm_os_orchestrator.commands.classify_exception import run  # noqa: E402
from lawfirm_os_orchestrator.util.json_io import read_json  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local sibling-repo kernel smoke.")
    parent = REPO_ROOT.parent
    parser.add_argument("--substrate", default=str(parent / "LawFirm-os-semantic-substrate"))
    parser.add_argument("--ledger-dir", default=str(REPO_ROOT / ".lawfirm-os-orchestrator" / "smoke-ledger"))
    parser.add_argument("--packet-out", default=str(REPO_ROOT / ".lawfirm-os-orchestrator" / "smoke-runs"))
    parser.add_argument("--lake-mode", choices=["disabled", "dry-run", "runtime-safe"], default="dry-run")
    parser.add_argument("--stdout", choices=["json", "text"], default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command_args = SimpleNamespace(
        input=str(REPO_ROOT / "examples" / "synthetic_exception_event.json"),
        substrate=args.substrate,
        ledger_dir=args.ledger_dir,
        packet_out=args.packet_out,
        lake_mode=args.lake_mode,
        stdout=args.stdout,
    )
    if args.lake_mode == "runtime-safe":
        os.environ.setdefault("LAWFIRM_OS_ORCHESTRATOR_ALLOW_RUNTIME_SAFE", "true")
        os.environ.setdefault("EXCEPTIONS_LAKE_CONTRACT_REPO_PATH", args.substrate)
    code, summary = run(command_args)
    if code == 0:
        manifest_path = Path(summary["evidence_packet_path"]) / "manifest.json"
        manifest = read_json(manifest_path)
        packet_path = Path(summary["evidence_packet_path"]) / "packet.json"
        if "packet.json" not in manifest.get("files", {}):
            return _emit({"status": "failed", "error": "manifest missing packet.json", "summary": summary}, 1, args.stdout)
        if not packet_path.exists():
            return _emit({"status": "failed", "error": "packet.json missing", "summary": summary}, 1, args.stdout)
    return _emit(summary, code, args.stdout)


def _emit(summary: dict, code: int, stdout_mode: str) -> int:
    if stdout_mode == "json":
        print(json.dumps(summary, indent=2, sort_keys=False))
    else:
        print(summary.get("status", "unknown"))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
