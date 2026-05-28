# ADR-002 — AI Strategy, Decision Bottleneck, and Decision Models

**Status:** Accepted / proposed for repo adoption
**Date:** 2026-05-28
**Applies to:** LawFirm OS Orchestrator

---

## Context

The project already rejects a one-framework or one-vendor architecture. The Orchestrator is designed as a local-first deterministic kernel with adapters for models, tools, runtime frameworks, traces, transport, context, and Exception Lake handoff.

The missing explicit doctrine is why this is the AI strategy:

> LawFirm OS should build what retains value no matter which AI vendor, memory pattern, runtime framework, or deployment model wins.

There is also a second-order bottleneck:

> As AI makes outputs cheaper and faster, decisions become the bottleneck.

---

## Decision

The Orchestrator will treat AI strategy and decision models as control-plane inputs from the Semantic Substrate.

The Orchestrator will:

1. remain provider-agnostic at the domain layer;
2. treat vendors as capability/token suppliers;
3. preserve local/cloud/hybrid optionality;
4. record model/provider/runtime choices as execution details, not semantic authority;
5. require decision models for high-stakes or authority-changing workflows;
6. include decision-model references in evidence packets and ledgers;
7. use gates to prevent decisionless automation.

---

## Rationale

### Vendor uncertainty

The AI market is not settled. Tying canon, decision logic, memory, audit, or workflow truth to one provider would create strategic lock-in.

### Jevons and scale

Cheaper inference will likely increase total AI use. Token efficiency must coexist with demand governance.

### Physical bottlenecks

Compute, memory bandwidth, energy, and data-center capacity may constrain AI deployment. LawFirm OS needs routing, fallback, and local/cloud optionality.

### Decision bottleneck

AI can generate many recommendations. It cannot own institutional risk appetite, legal accountability, client context, or final authority. The Orchestrator should produce fewer, better, decision-ready packets.

### Legal decomposition

Legal work must be decomposed before automation. A matter becomes tasks; tasks become primitives; primitives reveal decision points; decision points need explicit criteria, evidence, and authority.

---

## Consequences

Positive:

- reduced vendor lock-in;
- clearer decision accountability;
- better evidence packets;
- safer automation;
- stronger audit;
- reusable decision models;
- cleaner integration with AIRCA / decision architecture.

Negative / cost:

- more control-plane artifacts to maintain;
- more up-front modeling before automation;
- slower path to broad autonomy;
- need for governance ownership of decision models.

The cost is accepted because decision models, audit, and ontology are durable assets rather than temporary glue.

---

## Implementation notes

Add:

- `DecisionModelGate`;
- `decision_model_id` in run ledger;
- decision section in evidence packet;
- `decision-model-registry` consumption from substrate;
- decision defect tags in Exception Lake handoff;
- tests proving no high-risk decision path runs without a decision model.

---

## Revisit triggers

Revisit if:

- model providers converge into one stable, trusted utility layer;
- local models become dominant for all legal workflows;
- approval queues become the primary constraint;
- decision models become too heavy and need simplification;
- AIRCA or another decision-architecture repo publishes a stronger machine-readable standard.
