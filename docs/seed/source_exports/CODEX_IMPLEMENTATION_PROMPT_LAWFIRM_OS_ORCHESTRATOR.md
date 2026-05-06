# Clean Export of the Idea Featured in This — Codex Implementation Prompt

Use this prompt with Codex or a coding agent.

---

You are Codex working on LawFirm OS. Implement the following architecture carefully and conservatively.

## Goal

Create a research-integrated v2 implementation path for LawFirm OS Orchestrator and its supporting contract surfaces.

This work involves three repos:

1. `lowelltwong-alt/LawFirm-os-semantic-substrate`
2. `lowelltwong-alt/LawFirm-os-exceptions-lake-runtime`
3. new repo: `LawFirm-os-orchestrator`

## Architecture rule

Do not invert authority.

```text
Semantic Substrate publishes meaning.
Orchestrator executes bounded workflows and builds evidence packets.
Exception Lake Runtime validates and records runtime evidence.
Humans approve semantic promotion.
Only approved promotion changes canon.
```

The Orchestrator is not a semantic authority.

## Current live baseline

Observed Semantic Substrate commit:

```text
a9df5e75319ecdd4e100321be35b51e88bb75ba8
```

Observed Exceptions Runtime release commit:

```text
6f2d7c17da71221a6600d039b3be934f8452c346
```

Before merging runtime lock changes, regenerate the lock from the actual live Semantic Substrate checkout.

## Tasks

### Task A — Patch Semantic Substrate

Add draft, metadata-only orchestrator contract surfaces.

Create or update:

```text
registry/orchestrator-contract-export.json
registry/model-policy-registry.json
registry/tool-authority-registry.json
registry/human-approval-registry.json
schemas/evidence-packet.schema.json
schemas/orchestrator-run-record.schema.json
schemas/tool-call-trace.schema.json
schemas/human-approval-record.schema.json
governance/ORCHESTRATOR_BOUNDARY.md
docs/ORCHESTRATION_LAYER_DATA_FLOW.md
```

Constraints:

- Mark these as `draft_metadata_only` unless tests/examples make them stable.
- Do not claim production runtime readiness.
- Do not duplicate canonical definitions already present elsewhere.
- Do not let Orchestrator-specific contracts mutate existing canonical meaning without explicit promotion.
- Add references to existing `registry/exceptions-lake-contract-export.json` rather than replacing it.

### Task B — Patch Exceptions Lake Runtime

Fix repo identity and contract lock hygiene.

Update:

```text
contracts.lock.json
.github/workflows/ci.yml
scripts/update_contract_lock.py
README.md
docs/LOCAL_DEV.md
docs/architecture/DATA_FLOW.md
```

Constraints:

- Use `lowelltwong-alt/LawFirm-os-semantic-substrate` as the contract repo identity.
- Regenerate `contracts.lock.json` from the live checked-out Semantic Substrate SHA.
- Preserve fail-closed behavior on lock mismatch.
- Do not write into the contract repo path.
- Do not add production claims.
- Do not add `append_evidence_packet` or richer runtime APIs until the Semantic Substrate publishes stable schemas and runtime validators adopt them.

Runtime docs should clearly state:

```text
Current accepted runtime inputs:
- synthetic exception envelopes
- metadata-only non-synthetic dry-run preflight envelopes

Future possible inputs:
- evidence packets
- tool-call traces
- human-approval records
- orchestrator run records

Future inputs require Semantic Substrate schemas and Runtime validation before persistence.
```

### Task C — Create LawFirm OS Orchestrator MVP repo

Scaffold an installable Python package:

```text
LawFirm-os-orchestrator/
  README.md
  pyproject.toml
  contracts.lock.json
  examples/synthetic_exception_event.json
  docs/architecture.md
  docs/contracts.md
  docs/decisions/local_first.md
  docs/decisions/read_only_substrate.md
  docs/decisions/synthetic_only_policy.md
  src/lawfirm_os_orchestrator/
    __init__.py
    __main__.py
    cli.py
    app.py
    commands/classify_exception.py
    config/
    domain/
    policy/
    substrate/
    model_router/
    evidence/
    ledger/
    lake/
    util/
  tests/
```

Package name must be:

```text
lawfirm_os_orchestrator
```

First command:

```bash
python -m lawfirm_os_orchestrator classify-exception --input examples/synthetic_exception_event.json
```

## MVP behavior

The command must:

1. Parse strict synthetic input.
2. Reject real client/matter data flags.
3. Load pinned Semantic Substrate contracts read-only.
4. Resolve allowed canonical route IDs and event classes.
5. Build a per-run output schema whose route/event fields are enum-bounded to canonical IDs.
6. Call exactly one classifier/model adapter.
7. Default to deterministic `mock` adapter in CI.
8. Optionally support `openai_structured` adapter behind an optional dependency.
9. Locally validate returned JSON again.
10. Reject unknown fields, unknown route IDs, unknown event classes, malformed output, refusals, or missing fields.
11. Write append-only JSONL ledger lines.
12. Build an evidence packet directory containing manifest, input, substrate snapshot, policy gate, model request/response, classification result, and optional ingest receipt.
13. Default Exception Lake integration to disabled or validate-only.
14. Require dual opt-in for any runtime ingest: config allow-switch plus CLI flag.
15. Never write to Semantic Substrate.

## First command exit codes

```text
0 success
2 input/config/policy validation failed
3 substrate load or canonical lookup failed
4 model classification failed
5 artifact writing failed
6 Exception Lake handoff failed after successful classification
```

## Strict no-build list

Do not build yet:

```text
web app
dashboards
background daemon
live firm connectors
real client or matter data ingestion
autonomous write actions
substrate mutation tools
route/event-class authoring workflow
multi-agent planner/executor swarm
broad RAG/vector database
durable workflow engine
MCP server mode
Temporal-first runtime
LangGraph-first runtime
```

## Acceptance criteria

- `python -m lawfirm_os_orchestrator classify-exception --input examples/synthetic_exception_event.json` succeeds with the mock adapter.
- Every successful run writes a ledger line and evidence packet.
- Every successful run records contract pin, manifest hash, input hash, route/event decision, validation results, trace/correlation IDs, and ingest mode.
- Unknown route/event values fail closed.
- Missing contract pin fails closed.
- Synthetic gate violations fail closed.
- Orchestrator has no write methods in its substrate client.
- Runtime ingest cannot occur without dual opt-in.
- Tests prove no Semantic Substrate mutation is possible from the Orchestrator code path.
