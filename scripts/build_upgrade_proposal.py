from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.learning.proposals import build_upgrade_proposal_packet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a local proposal-only upgrade packet.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default=".lawfirm-os-orchestrator/upgrade_proposals")
    parser.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_upgrade_proposal_packet(request_path=Path(args.input), output_root=Path(args.out))
    if args.stdout == "json":
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        print(f"upgrade_proposal proposal={result['proposal_id']} packet_dir={result['packet_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
