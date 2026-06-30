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

### classify-autonomy

```powershell
python -m lawfirm_os_orchestrator classify-autonomy --action path/to/action.json --out .lawfirm-os-orchestrator/autonomy/latest.json --stdout json
```

Purpose: classify a local action descriptor into a red/yellow/green autonomy decision and deterministic hardness score.

Important controls:

- risk color controls authority;
- hard red triggers override hardness and leverage;
- green is conditional on synthetic or metadata-only, local-only, reversible, preapproved-lane work;
- yellow can prepare bounded local drafts or green-candidate recommendations, but cannot restore green;
- red may only produce proposal-only risk memos or human decision packets.

### select-harness

```powershell
python -m lawfirm_os_orchestrator select-harness --autonomy .lawfirm-os-orchestrator/autonomy/latest.json --scorecard path/to/scorecard.json --out .lawfirm-os-orchestrator/harness/latest.json --stdout json
```

Purpose: combine an autonomy decision, hardness score, and local scorecard into a harness plan.

Important controls:

- hardness controls harness depth only;
- leverage controls priority only;
- harness depth never upgrades risk authority;
- outputs are local orchestrator artifacts only.

### watch-green-lanes

```powershell
python -m lawfirm_os_orchestrator watch-green-lanes --signals path/to/signals.json --lanes path/to/green_lanes.json --out .lawfirm-os-orchestrator/autonomy/watch.json --stdout json
```

Purpose: evaluate local signals against green-lane assumptions and recommend unchanged, yellow, or red lane status.

Important controls:

- signals may downgrade green to yellow or red;
- agents may recommend green-candidate but may not restore green;
- human restoration is required for any green restoration;
- Research Radar remains local-file scaffold only;
- no live crawling, model calls, scheduled jobs, external APIs, external writes, Git operations, Substrate writes, or Lake writes.

### generate-codex-task

```powershell
python -m lawfirm_os_orchestrator generate-codex-task --opportunity path/to/opportunity.json --scorecard path/to/scorecard.json --autonomy path/to/autonomy.json --harness path/to/harness.json --out .lawfirm-os-orchestrator/harness/codex_task_packet.json --stdout json
```

Purpose: generate an inert local Codex task packet from opportunity, scorecard, autonomy, and harness inputs.

Important controls:

- packet is build instructions only;
- packet does not execute Codex, Git, patches, tests, tools, models, network, external APIs, Substrate writes, or Lake writes;
- red packets require human approval and can only recommend risk memo or decision packet output;
- yellow packets may recommend draft evidence and review only;
- green packets remain limited to local reversible work inside a preapproved lane.

### research-radar import-local

```powershell
python -m lawfirm_os_orchestrator research-radar import-local --input examples/research_signals/example_signal.json --out .lawfirm-os-orchestrator/research/signals.jsonl --stdout json
```

Purpose: import curated local JSON or Markdown research signals into a local JSONL store.

This is local-only. It does not crawl the web, call APIs, call models, schedule jobs, execute code, run Git, patch files, write to the Semantic Substrate, or write to the Exception Lake.

### intake prepare-owner-packet

```powershell
python -m lawfirm_os_orchestrator intake prepare-owner-packet --input examples/intake_owner_review_request.synthetic.json --stdout json
```

Purpose: prepare a local, candidate-only owner-review packet for the intake-to-budget workflow.

Important controls:

- synthetic-only request data;
- raw client, matter, privileged, or production transcript fields fail closed;
- human pauses and missing budget preconditions block readiness;
- every carrier rejection notice is classified into a known candidate bucket or `unknown_or_new_rejection_pattern`;
- appeals/fixes require human authorization before any future submission;
- budget actuals variance is calculated by phase/task against proposed, carrier-compliant, approved-if-known, and actual amounts;
- Exception Lake handoff is preview-only and has no write authority.

### intake build-lake-admission-review-packet

```powershell
python -m lawfirm_os_orchestrator intake build-lake-admission-review-packet --owner-packet .lawfirm-os-orchestrator/intake_owner_review/<packet_id>/intake_owner_review_packet.json --stdout json
```

Purpose: prepare a local, candidate-only Exception Lake owner-review packet from an intake owner-review packet.

Important controls:

- owner packet hash is recomputed before packaging;
- input must remain synthetic, non-authoritative, and not authorized for client submission;
- raw client, matter, privileged, or production transcript fields fail closed;
- Lake handoff must still be `handoff_allowed=false`;
- Lake writes, SQLite writes, raw-payload storage, real-data admission, budget submission, and appeal submission remain unauthorized;
- canonical route and event-class assignments remain `none`;
- output record-family summaries are candidate-only and require Exception Lake owner review before any admission path.

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
python scripts/run_full_pytest.py
python scripts/run_full_pytest.py tests/test_workflow_atlas.py -q
python scripts/run_full_pytest.py tests/test_intake_owner_review_packet.py -q
python scripts/run_full_pytest.py tests/test_intake_lake_admission_review_packet.py -q
python scripts/validate_intake_orchestrator_adoption_review.py
python scripts/run_evals.py --fixture evals/fixtures/classify_exception_cases.jsonl --gold evals/gold/classify_exception_gold.jsonl --stdout json
python scripts/run_shadow_eval.py --proposal examples/shadow_eval/validator_threshold_proposal.json --stdout json
python scripts/build_upgrade_proposal.py --input examples/upgrade_proposals/validator_threshold_packet_request.json --stdout json
python scripts/render_codex_task.py --input examples/codex_task_drafts/validator_task_draft_request.json --stdout json
python scripts/check_safety.py
```

`config/validation-runtime-policy.yaml` requires all pytest runs to use `python scripts/run_full_pytest.py`; direct pytest invocation fails closed so short default ceilings do not create false failures.

## Contract And Authority Notes

- Substrate loading is manifest-first via `manifests/contract_manifest.v1.json`.
- `policy_bundle_id` is required and must not be defaulted by the reader.
- Canonical `route_id` and `event_class` values come only from the substrate.
- Local operational labels are documented in `docs/CANONICAL_ROUTE_MAPPING.md` and are not canonical authority.
- `config/research_sources.yaml` is metadata-only and non-authoritative.
- PR02 autonomy and harness records are execution-plane local artifacts only.
- PR03 green-lane watcher records are execution-plane local artifacts only.
- PR04 Codex task packets are inert execution-plane local artifacts only.
