# Data Flow Map

## Summary

Canonical machine name: `LawFirm-os-orchestrator`. Plane: execution.

This repo consumes the Semantic Substrate read-only, validates model/tool outputs, writes local ledgers, builds local evidence packets, and may optionally prepare dry-run or guarded handoff artifacts for the Exception Lake. It does not define canon, mutate the substrate, promote governance changes, or authorize production automation.

## Contract Flow

```text
Semantic Substrate manifest
-> orchestrator read-only substrate client
-> canonical route/event allowlist
-> synthetic classify-exception workflow
-> structured validation
-> local JSONL ledger
-> local evidence packet
-> Exception Lake disabled/not_attempted by default
```

The substrate manifest is loaded first from `manifests/contract_manifest.v1.json`. Required fields include `policy_bundle_id`; loading fails closed when required fields are missing.

## Mermaid Flowchart

```mermaid
flowchart LR
    SS["Semantic Substrate / control plane\nLawFirm-os-semantic-substrate\nmanifest + registries + policies"]
    OR["Orchestrator / execution plane\nLawFirm-os-orchestrator\nbounded local workflows"]
    LED["Local JSONL ledger\n.lawfirm-os-orchestrator/ledger"]
    PKT["Local evidence packet\n.lawfirm-os-orchestrator/runs"]
    EL["Exception Lake / evidence plane\nexceptions-lake-runtime-main"]
    HUM["Human Governance\nreview + promotion outside runtime"]
    RR["Research Radar local import\nmetadata-only, non-authoritative"]
    LEARN["Learning artifacts\nshadow evals + proposals + task drafts"]

    SS -->|"read-only manifest-first contracts"| OR
    OR -->|"validated synthetic run records"| LED
    OR -->|"contract-locked evidence packet"| PKT
    PKT -->|"disabled by default / dry-run only when explicit"| EL
    RR -->|"local JSON/Markdown signals only"| LEARN
    LEARN -->|"proposal-only artifacts"| HUM
    HUM -->|"approved promotion only"| SS

    OR -. "no substrate writes" .-> SS
    OR -. "no local canonical route_id/event_class authority" .-> SS
    RR -. "no live crawl, API, model call, schedule, or external write" .-> RR
```

## Mermaid Sequence

```mermaid
sequenceDiagram
    participant CLI as CLI Caller
    participant OR as Orchestrator
    participant SS as Semantic Substrate
    participant LED as Local Ledger
    participant PKT as Evidence Packet
    participant EL as Exception Lake

    CLI->>OR: classify-exception synthetic input
    OR->>SS: read manifest and route registry
    SS-->>OR: policy_bundle_id, schema keys, route_id/event_class allowlist
    OR->>OR: deterministic validation and mock classification
    OR->>LED: append local run record
    OR->>PKT: write local evidence packet
    alt lake-mode disabled
        OR-->>EL: not attempted
    else explicit dry-run/runtime-safe
        OR->>EL: guarded handoff or receipt only
    end
```

## Current Commands

- `classify-exception`
- `research-radar import-local`
- `research-radar list-signals`
- `learning run-shadow-eval`
- `learning build-upgrade-proposal`
- `learning render-codex-task`
- `learning score-insight`

See `ENDPOINTS_AND_COMMANDS.md` for command details.

## Phase 2 Status

Implemented locally:

- offline eval and metrics spine
- governed learning object models
- local-only Research Radar import
- algorithm/method insight scoring
- shadow eval runner
- upgrade proposal packet builder
- action recommendations and inert Codex task drafts
- learning-loop CLI surfaces
- safety regression suite

Still non-authoritative and local-only:

- Research Radar source metadata in `config/research_sources.yaml`
- learning proposals, recommendations, and task drafts
- all Phase 2 upgrade and decision-support artifacts

## Hard Prohibitions

- no Semantic Substrate writes
- no route/event-class invention
- no real client or matter data
- no live Research Radar automation
- no live web crawling
- no scheduled jobs
- no live model calls
- no external APIs
- no external writes
- no production connectors
- no automatic code mutation or Git operations from inside the app
