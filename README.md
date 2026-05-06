# LawFirm OS Orchestrator

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
- no free-form model text parsing fallback.

## First throughput metric

Accepted, contract-locked proposed exception packets per reviewer hour.
