# Legal Knowledge Runtime Integration

The Orchestrator should call the Legal Knowledge Runtime through a narrow adapter.

## Role split

- Semantic Substrate owns legal knowledge schemas, registries, bundle definitions, access labels, and boundaries.
- Legal Knowledge Runtime owns ingestion preflight, parsing, indexing, retrieval planning, context-bundle assembly, and retrieval traces.
- Orchestrator owns execution sequencing, approvals, tool budgets, and evidence packet assembly.
- Exception Lake Runtime records retrieval traces, defects, quality events, and evidence pointers.

## Orchestrator may call

- `legal_knowledge.ingest_preflight`
- `legal_knowledge.assemble_context_bundle`
- `legal_knowledge.explain_retrieval_trace`

## Orchestrator must not do

- ingest broad corpora directly;
- decide legal document type canon;
- bypass access policy;
- store full raw legal documents in run ledgers;
- promote legal retrieval output into canon.

## Default MVP mode

`disabled` or local dry run only. Production connectors require a later governance change.
