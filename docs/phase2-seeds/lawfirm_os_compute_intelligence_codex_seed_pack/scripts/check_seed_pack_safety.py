#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Safety scanner for Compute Intelligence seed artifacts.

This scanner is intentionally conservative. It blocks common imports/patterns that
would turn seed-only docs/reference code into live automation.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

FORBIDDEN_PATTERNS = [
    ("network_requests", re.compile(r"\bimport\s+requests\b|\bfrom\s+requests\b")),
    ("network_httpx", re.compile(r"\bimport\s+httpx\b|\bfrom\s+httpx\b")),
    ("network_aiohttp", re.compile(r"\bimport\s+aiohttp\b|\bfrom\s+aiohttp\b")),
    ("network_urllib", re.compile(r"\bimport\s+urllib\b|\bfrom\s+urllib\b|urlopen\(")),
    ("subprocess_exec", re.compile(r"\bimport\s+subprocess\b|\bfrom\s+subprocess\b|subprocess\.")),
    ("git_exec", re.compile(r"\bgit\s+(push|pull|merge|checkout|reset|stash|branch|commit)\b")),
    ("scheduler", re.compile(r"\bapscheduler\b|\bschedule\.every\b|\bcron\b|\bcrontab\b", re.IGNORECASE)),
    ("model_sdk_openai", re.compile(r"\bimport\s+openai\b|\bfrom\s+openai\b|OpenAI\(")),
    ("model_sdk_anthropic", re.compile(r"\bimport\s+anthropic\b|\bfrom\s+anthropic\b|Anthropic\(")),
    ("external_write_language", re.compile(r"external_write\s*:\s*true|authorizes_external_writes\s*:\s*true", re.IGNORECASE)),
]

ALLOWLIST_FILENAMES = {
    "check_seed_pack_safety.py",  # scanner necessarily contains forbidden words as patterns
}

SCAN_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".mmd"}


def scan(root: Path) -> list[tuple[str, str, int, str]]:
    findings: list[tuple[str, str, int, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if path.name in ALLOWLIST_FILENAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            lower = stripped.lower()
            # Do not flag safety policy prose that explicitly forbids the pattern.
            if any(marker in lower for marker in ["do not", "must not", "no `", "no ", "forbidden", "blocked"]):
                continue
            for name, pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    findings.append((name, str(path.relative_to(root)), lineno, stripped))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    findings = scan(root)
    if findings:
        print("Seed-pack safety check failed:")
        for name, path, lineno, line in findings:
            print(f"- {name}: {path}:{lineno}: {line}")
        return 1
    print("Seed-pack safety check passed: no forbidden live-automation patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
