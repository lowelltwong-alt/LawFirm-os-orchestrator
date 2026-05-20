# Core Artifact: Agent-Hostile MVP

The Orchestrator MVP is a contract-locked, agent-scoped, revocable, audited synthetic classification run.

The Orchestrator remains an execution plane. Canonical agent-hostile control contracts live in Semantic Substrate. The Orchestrator reads those registries read-only, applies local execution gates, assembles evidence packets, and hands them to the Exception Lake adapter. It does not define canonical route IDs, event classes, schemas, prompt policy, model policy, endpoint authority, revocation policy meaning, or tool policy authority.

Local files under `config/agent_hostile/` are synthetic fixture fallback only. They are not governance canon and must be selected explicitly with local fixture mode.

Implemented controls:

- agent identity proof for actor, delegation, tenant, route, tool, and data scope;
- revocation gate for revoked agents, paused routes, and denied tools;
- prompt integrity gate for registered, approved, hash-checked prompts;
- tool authority manifest validation with auth, identity, audit, risk, and approval metadata;
- evidence packet enrichment for actor proof, authz decisions, prompt proof, revocation snapshot, and blast radius.
- evidence packet provenance for the control registry source, registry path, registry hash, and pinned contract SHA.

Fail-closed behavior:

- missing canonical Semantic Substrate prompt/tool/endpoint/control registries blocks non-fixture runs;
- revoked agent, paused route, or denied tool blocks before model execution;
- unknown tool or default-open tool config blocks before model execution;
- missing, unapproved, or hash-mismatched prompt blocks before model execution.
