# LawFirm OS Orchestrator

Canonical machine name: `LawFirm-os-orchestrator`. Human label: Law Firm OS Orchestrator. Plane: execution. Consumes the substrate `LawFirm-os-semantic-substrate` read-only via the canonical orchestrator manifest at `manifests/contract_manifest.v1.json`. For sibling-repo names and authority order across repos, see the substrate's `governance/CROSS_REPO_MAP.md` and this repo's `docs/CANONICAL_ROUTE_MAPPING.md`.

Contract-governed orchestration for law-firm AI systems — not an agent swarm demo.

The MVP is a synthetic-only, local-first, contract-locked evidence-packet factory.

```text
synthetic input
-> pinned Semantic Substrate manifest
-> deterministic route/event-class allowlist validation
-> deterministic mock classifier
-> strict structured-output validation
-> append-only JSONL ledger
-> local evidence packet directory
-> Exception Lake disabled or dry-run by default
```

## Quickstart

```bash
python -m pip install -e ".[dev]"
python -m lawfirm_os_orchestrator classify-exception \
  --input examples/synthetic_exception_event.json \
  --substrate tests/fixtures/substrate \
  --lake-mode disabled \
  --stdout json
```

## Safety boundaries

- no real client data;
- no real matter data;
- no production connectors;
- no Semantic Substrate writes;
- no route/event-class invention;
- no Exception Lake writes by default;
- no free-form model text parsing fallback;
- no live model calls in the MVP;
- no scheduled jobs;
- no live Research Radar collection, external APIs, or autonomous research execution;
- contract-lock validation is fail-closed on SHA drift or missing required manifest fields, including `policy_bundle_id`.

## Substrate consumption

The orchestrator loads contracts from a pinned substrate checkout in this order:

1. `manifests/contract_manifest.v1.json` — canonical orchestrator-facing manifest. Required keys: `manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, `registry_refs`, `governance_refs`. Loading fail-closes if absent or missing required fields.
2. `registry/exception-route-registry.json` — canonical `route_id`/`event_class` authority.

`policy_bundle_id` is required from the manifest and must not be silently defaulted. See the substrate's `governance/ORCHESTRATOR_BOUNDARY.md` for the full contract.

The substrate is pinned in `contracts.lock.json`. Lock fields:

- `contract_repo: LawFirm-os-semantic-substrate`
- `contract_ref_type: git_sha`
- `contract_sha: <substrate commit>`
- `generated_at: <ISO8601>`
- `generated_by: LawFirm-os-orchestrator`

## First throughput metric

Accepted, contract-locked proposed exception packets per reviewer hour.
