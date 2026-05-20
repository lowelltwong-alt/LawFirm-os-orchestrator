# ADR: Agent-Hostile MVP

Accepted. The synthetic `classify-exception` run must carry enough local proof to answer who acted, on whose behalf, under which tenant, route, tool, prompt, revocation, and data scope.

The control layer is intentionally additive. Existing contract lock, read-only substrate loading, execution authority, synthetic policy, evidence packet, ledger, and Exception Lake adapter behavior stay in place. The new local gates are execution safeguards; they do not promote the Orchestrator into Semantic Substrate authority.

Semantic Substrate is the canonical source for agent-hostile schemas, prompt registry, tool authority, endpoint authority, revocation policy shape, and the control bundle/export surfaces. Orchestrator enforcement consumes those contracts read-only and records their provenance in evidence packets.

`config/agent_hostile/` remains available only as a synthetic local fixture fallback. Fixture mode is explicitly non-canonical and is meant for tests or bootstrapping, not governance authority.
