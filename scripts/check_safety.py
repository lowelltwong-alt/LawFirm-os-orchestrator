from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from lawfirm_os_orchestrator.cli import build_parser
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "src" / "lawfirm_os_orchestrator"
FORBIDDEN_SUBSTRATE_PREFIXES = ("write", "update", "delete", "mutate", "create", "save", "append")
FORBIDDEN_RUNTIME_IMPORT_ROOTS = {"requests", "httpx", "urllib", "socket", "subprocess"}
CHECKED_LOCAL_ONLY_DIRS = (
    APP_ROOT / "autonomy",
    APP_ROOT / "commands",
    APP_ROOT / "discovery",
    APP_ROOT / "evals",
    APP_ROOT / "harness",
    APP_ROOT / "learning",
)


def substrate_write_methods() -> list[str]:
    client = PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate")
    return [name for name in dir(client) if name.startswith(FORBIDDEN_SUBSTRATE_PREFIXES)]


def default_lake_mode() -> str:
    parser = build_parser()
    args = parser.parse_args(
        [
            "classify-exception",
            "--input",
            "examples/synthetic_exception_event.json",
        ]
    )
    return str(args.lake_mode)


def forbidden_imports() -> dict[str, list[str]]:
    violations: dict[str, list[str]] = {}
    for directory in CHECKED_LOCAL_ONLY_DIRS:
        for path in directory.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module.split(".", 1)[0])
            matches = sorted(set(imports) & FORBIDDEN_RUNTIME_IMPORT_ROOTS)
            if matches:
                violations[str(path.relative_to(ROOT))] = matches
    return violations


def run_checks() -> dict[str, object]:
    write_methods = substrate_write_methods()
    lake_mode = default_lake_mode()
    import_violations = forbidden_imports()
    checks = {
        "substrate_client_has_no_write_methods": not write_methods,
        "lake_mode_defaults_disabled": lake_mode == "disabled",
        "local_learning_imports_have_no_network_or_process_modules": not import_violations,
    }
    return {
        "status": "ok" if all(checks.values()) else "failed",
        "checks": checks,
        "details": {
            "substrate_write_methods": write_methods,
            "default_lake_mode": lake_mode,
            "forbidden_imports": import_violations,
        },
    }


def build_parser_for_script() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local LawFirm OS Orchestrator safety checks.")
    parser.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser_for_script().parse_args(argv)
    result = run_checks()
    if args.stdout == "json":
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        print(result["status"])
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
