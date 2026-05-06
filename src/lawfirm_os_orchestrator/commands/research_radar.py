from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.discovery.local_import import import_signal, list_signals

EXIT_IMPORT = 2


def run(args) -> tuple[int, dict[str, Any]]:
    try:
        if args.research_command == "import-local":
            signal = import_signal(Path(args.input), Path(args.out))
            return 0, {
                "status": "ok",
                "signal_id": signal.signal_id,
                "title": signal.title,
                "source_hash": signal.source_hash,
                "out": str(Path(args.out)),
                "proposal_only": signal.semantics == "proposal_only",
            }
        if args.research_command == "list-signals":
            signals = list_signals(Path(args.signals))
            return 0, {"status": "ok", "count": len(signals), "signals": signals}
    except Exception as exc:
        return EXIT_IMPORT, {"status": "failed_validation", "error": str(exc)}
    return EXIT_IMPORT, {"status": "failed_validation", "error": f"unknown research command: {args.research_command}"}
