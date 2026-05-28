# Decision Model Gates for the Orchestrator

**Status:** proposed workflow doc
**Scope:** LawFirm OS Orchestrator
**Authority:** consumes Semantic Substrate decision-model registry

---

## Purpose

The Orchestrator must not merely route model outputs. It must route **decision requests**.

A decision request is only admissible when the system can identify:

- the decision model;
- the evidence packet;
- the decision alternatives;
- the decision owner;
- the risk tier;
- the autonomy level;
- the approval rule;
- the defect modes;
- the metrics.

---

## New gate: DecisionModelGate

Add `DecisionModelGate` after `RouteAuthorityGate` and before `EvidenceCompletenessGate`.

```text
SyntheticOnlyGate
-> ContractPinGate
-> AgentIdentityGate
-> RevocationGate
-> RouteAuthorityGate
-> DecisionModelGate
-> ToolAuthorityGate
-> PromptIntegrityGate
-> EvidenceCompletenessGate
```

### Blocks if

- no `decision_model_id` exists for the task class;
- decision model is not in the substrate registry;
- the model's `risk_tier` conflicts with route/task risk;
- evidence minimums cannot be satisfied;
- autonomy requested exceeds `autonomy_allowed`;
- approval requirement is missing for high-risk or irreversible decisions;
- decision model appears to be runtime-generated rather than substrate-published.

### Emits

```yaml
DecisionModelGateResult:
  decision_model_id: string
  result: pass | deny | needs_review
  reason_code: string
  evidence_minimums_met: boolean
  autonomy_allowed: none | recommend | draft | act_with_approval | act_autonomously
  approval_required: boolean
  approver_role: string | null
  evaluated_at: timestamp
```

---

## Evidence packet changes

Add:

```yaml
decision:
  decision_model_id: string
  decision_name: string
  decision_type: string
  decision_owner_role: string
  alternatives: [string]
  criteria: [string]
  evidence_minimums: [string]
  risk_tier: low | medium | high | protected
  reversibility: reversible | partially_reversible | irreversible
  autonomy_allowed: none | recommend | draft | act_with_approval | act_autonomously
  approval_required: boolean
  approver_role: string | null
  decision_gate_result: pass | deny | needs_review
```

---

## Ledger changes

Every run ledger entry that asks a human, agent, or tool to choose among alternatives should include:

```yaml
decision_model_id: string
decision_type: string
decision_owner_role: string
evidence_packet_id: string
risk_tier: string
reversibility: string
autonomy_allowed: string
approval_required: boolean
decision_defect_tags: [string]
```

---

## Metrics

Track:

- `decision_ready_packet_total`
- `decision_model_missing_total`
- `decision_gate_deny_total`
- `decision_needs_review_total`
- `decision_cycle_time_p50/p95`
- `decision_owner_override_total`
- `decision_defect_total`
- `approval_bypass_total`
- `evidence_minimum_missing_total`
- `autonomy_overreach_total`
- `cost_per_accepted_decision`

---

## TOC interpretation

The Orchestrator should optimize for decision throughput, not output production.

```text
Drum   = accountable decision capacity
Buffer = prevalidated evidence packets
Rope   = DecisionModelGate + EvidenceCompletenessGate
```

If reviewers are overloaded, do not add more agents. Tighten the rope: reduce low-evidence packets, require stronger evidence minimums, and use decision-model triage.
