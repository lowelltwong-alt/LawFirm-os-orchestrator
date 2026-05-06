# 05 — Stop Conditions and Scope Gates

Codex must stop if a requested change would:

- accept real client data;
- accept real matter data;
- accept floating/unpinned contracts;
- let model output invent route IDs, event classes, schemas, or governance doctrine;
- write to the Semantic Substrate;
- write to a production/client/matter system;
- enable Exception Lake runtime ingest by default;
- parse free-form model text heuristically for downstream automation;
- ignore ledger write failure;
- build evidence packets without manifest hash, validation results, source refs, trace IDs, and packet hash;
- add autonomous code mutation;
- add a background agent daemon;
- add broad web crawling;
- add LangGraph/Temporal/MCP server mode before a task explicitly requires it;
- weaken tests to pass.

## Allowed in V1

- local JSONL ledgers;
- local evidence packets;
- local curated research signal import;
- offline evals;
- proposal generation;
- Codex task draft generation;
- disabled/dry-run Lake clients;
- runtime-safe shell that fails closed.

## Human approval required before implementation

- any real data path;
- any side-effect tool;
- any substrate schema/registry/governance change;
- any runtime persistence API;
- any automated research crawler;
- any self-patching loop.
