from __future__ import annotations

import argparse
import json
from pathlib import Path

from lawfirm_os_orchestrator.learning.codex_tasks import write_codex_task_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render inert local Codex task draft artifacts.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default=".lawfirm-os-orchestrator/codex_task_drafts/example")
    parser.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = write_codex_task_artifacts(request_path=Path(args.input), output_dir=Path(args.out))
    if args.stdout == "json":
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        print(f"codex_task_draft output_dir={result['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
