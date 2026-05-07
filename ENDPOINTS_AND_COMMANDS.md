# Endpoints And Commands

This repo has no HTTP server, production endpoint, background daemon, MCP server mode, LangGraph runtime, Temporal runtime, or production connector surface.

All current surfaces are local CLI commands or local scripts. They are execution-plane helpers only and do not create canonical route IDs, event classes, schemas, governance doctrine, or promotion decisions.

## CLI

Run through the module entrypoint:

```powershell
python -m lawfirm_os_orchestrator <command>
```

Installed script entrypoint:

```powershell
lawfirm-os-orchestrator <command>
```

### classify-exception

```powershell
python -m lawfirm_os_orchestrator classify-exception --input examples/synthetic_exception_event.json --substrate tests/fixtures/substrate --lake-mode disabled --stdout json
```

Purpose: classify a synthetic exception event, validate against the pinned substrate fixture, write a local JSONL ledger, and build a local evidence packet.

Important controls:

- `--lake-mode disabled` is the default.
- Lake integration is not attempted when disabled.
- `dry-run` is receipt-only.
- `runtime-safe` remains guarded by explicit configuration and fail-closed tests.
- real client or matter data fails the synthetic gate.

### research-radar import-local

```powershell
python -m lawfirm_os_orchestrator research-radar import-local --input examples/research_signals/example_signal.json --out .lawfirm-os-orchestrator/research/signals.jsonl --stdout json
```

Purpose: import curated local JSON or Markdown research signals into a local JSONL store.

This is local-only. It does not crawl the web, call APIs, call models, schedule jobs, execute code, run Git, patch files, write to the Semantic Substrate, or write to the Exception Lake.

### research-radar list-signals

```powershell
python -m lawfirm_os_orchestrator research-radar list-signals --signals .lawfirm-os-orchestrator/research/signals.jsonl --stdout json
```

Purpose: list locally imported research signals.

### learning run-shadow-eval

```powershell
python -m lawfirm_os_orchestrator learning run-shadow-eval --proposal examples/shadow_eval/validator_threshold_proposal.json --stdout json
```

Purpose: compare proposal/candidate metrics against baseline eval metrics without changing runtime defaults.

### learning build-upgrade-proposal

```powershell
python -m lawfirm_os_orchestrator learning build-upgrade-proposal --input examples/upgrade_proposals/validator_threshold_packet_request.json --stdout json
```

Purpose: render a local human-reviewable upgrade proposal packet.

### learning render-codex-task

```powershell
python -m lawfirm_os_orchestrator learning render-codex-task --input examples/codex_task_drafts/validator_task_draft_request.json --stdout json
```

Purpose: render an inert local Codex task draft artifact. It never invokes Codex or Git.

### learning score-insight

```powershell
python -m lawfirm_os_orchestrator learning score-insight --input examples/research_signals/algorithm_insight_example.json --stdout json
```

Purpose: deterministically score a local algorithm/method insight as proposal evidence.

## Scripts

```powershell
python scripts/run_evals.py --fixture evals/fixtures/classify_exception_cases.jsonl --gold evals/gold/classify_exception_gold.jsonl --stdout json
python scripts/run_shadow_eval.py --proposal examples/shadow_eval/validator_threshold_proposal.json --stdout json
python scripts/build_upgrade_proposal.py --input examples/upgrade_proposals/validator_threshold_packet_request.json --stdout json
python scripts/render_codex_task.py --input examples/codex_task_drafts/validator_task_draft_request.json --stdout json
python scripts/check_safety.py
```

## Contract And Authority Notes

- Substrate loading is manifest-first via `manifests/contract_manifest.v1.json`.
- `policy_bundle_id` is required and must not be defaulted by the reader.
- Canonical `route_id` and `event_class` values come only from the substrate.
- Local operational labels are documented in `docs/CANONICAL_ROUTE_MAPPING.md` and are not canonical authority.
- `config/research_sources.yaml` is metadata-only and non-authoritative.
