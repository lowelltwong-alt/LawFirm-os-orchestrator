# Task 004 — Research Radar local import

**Codex level:** High


## Required opening statement

Before editing, state:

```text
Route:
Mode:
Allowed paths:
Forbidden paths:
Contract surfaces touched:
Validation plan:
Stop conditions:
Expected artifacts:
Codex level:
```

## Global constraints

- No real client/matter data.
- No Semantic Substrate writes.
- No Lake runtime ingest by default.
- No autonomous self-patching.
- No production connectors.
- No framework expansion unless the task explicitly asks.

## Goal

Add local-only Research Radar commands.

## Commands

```bash
python -m lawfirm_os_orchestrator research-radar import-signal --input examples/research_signal.json --out .lawfirm-os-orchestrator/research/signals.jsonl
python -m lawfirm_os_orchestrator research-radar list-signals --signals .lawfirm-os-orchestrator/research/signals.jsonl --stdout json
```

## Constraints

- No web crawling.
- No network calls.
- No automatic upgrade application.
- Store signals as JSONL with hashes and source refs.

