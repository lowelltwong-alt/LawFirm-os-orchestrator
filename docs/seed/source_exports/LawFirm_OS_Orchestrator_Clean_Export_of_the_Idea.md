# Clean Export of the Idea Featured in This

**Project:** LawFirm OS Orchestrator  
**Date:** 2026-05-06  
**Purpose:** Preserve the core architecture idea in a form that can be pasted into a new ChatGPT/OpenAI chat, given to Codex, used in Cursor, or checked into the future `LawFirm-os-orchestrator` repo as seed material.

---

## 1. One-sentence idea

Build **LawFirm OS Orchestrator** as a **synthetic-only, local-first, contract-locked evidence-packet factory**: it coordinates one bounded exception-classification run, reads canonical truth from the Semantic Substrate, validates everything fail-closed, writes an append-only JSONL ledger, builds a reviewable evidence packet, and optionally hands off through the Exception Lake validation boundary.

---

## 2. Core architecture stance

LawFirm OS has three planes:

| Plane | Repository / system | Role | Must not do |
|---|---|---|---|
| **Semantic control plane** | Semantic Substrate | Owns canonical schemas, registries, governance boundaries, route authority, validation contracts, policy bundles, approval doctrine, and promotion decisions. | Must not become a runtime observation store. |
| **Execution plane** | Orchestrator | Coordinates model/tool/agent execution, policy gates, validation, approvals, ledger writes, packet assembly, and optional Lake handoff. | Must not define semantic truth or mutate canon. |
| **Evidence plane** | Exception Lake Runtime | Stores validated runtime observations, exception events, audit records, and learning candidates. | Must not define schemas, route IDs, event classes, or governance doctrine. |

The Orchestrator is **not** a general agent platform yet. It is a small governed execution kernel.

---

## 3. Executive synthesis

The strongest finding is that the first useful Orchestrator should not optimize for autonomy, agent count, or model-call volume. It should optimize for **reviewer trust and reviewer throughput**.

The first bottleneck is **trusted review capacity at the governance boundary**. Reviewers lose time when model output lacks route validity, event-class validity, source references, validation results, contract pins, and traceability. The Orchestrator should attack that bottleneck by producing small, complete, deterministic, reviewable evidence packets.

The principal runtime unit should be a **contract-locked evidence packet**, not a bare exception event.

A bare exception event is only an atomic operational proposal. A legal-grade review packet must also carry:

- `manifest_id` and `manifest_hash`
- route decision
- proposed exception event
- source claim references and hashes
- model call summary
- validation results
- trace/correlation IDs
- message history
- human-review state
- optional Exception Lake handoff receipt
- packet hash

The MVP should be deliberately small:

- local-first Python CLI
- synthetic-only input
- read-only Semantic Substrate fixture/manifest loader
- deterministic route and event-class validation
- fake model adapter first
- optional structured model adapter later
- append-only JSONL run ledger
- local evidence packet directory or JSON artifact
- Exception Lake disabled or validate-only by default
- no real client data
- no real matter data
- no autonomous operational writes
- no web app
- no queue
- no MCP server
- no LangGraph
- no Temporal
- no OpenTelemetry Collector
- no production connector

Design for future MCP, OpenTelemetry, durable execution, and Agents SDK, but do not implement them in the first pass.

---

## 4. Decision filters

Every implementation decision should pass these filters:

1. **Start small.** Build one command before building a platform.
2. **Bottleneck-first.** Improve review-ready packet quality before improving scale.
3. **No autonomous write actions at first.** Local artifact writes are allowed; client/matter/system writes are not.
4. **No real client or matter data.** Synthetic only until governance explicitly approves more.
5. **Semantic Substrate remains source of truth.** Orchestrator reads canon; it does not create canon.
6. **Exception Lake remains validation/evidence spine.** Orchestrator may hand off through supported boundaries only.
7. **Orchestrator coordinates but does not define truth.** Model output is proposal-only.
8. **JSONL is acceptable for MVP.** Include IDs and schema versions so it can evolve.
9. **Design now for MCP/OpenTelemetry/durable execution; implement later.** Stable interfaces first; concrete runtime later.

---

## 5. Conflict-resolution table

| Conflict | Recommendation | Applies now | Deferred |
|---|---|---:|---:|
| Evidence packet vs bare exception event | Evidence packet is the Orchestrator’s main output. Bare exception event is inside it as a proposal. | Yes | Lake-native packet append API |
| OpenAI Agents SDK now vs deterministic CLI now | Build deterministic CLI kernel first. Agents SDK can become an adapter later. | Yes | Agents SDK runner integration |
| MCP-compatible vs MCP-first | Define MCP-compatible `ToolSpec`/resource concepts, but do not run MCP servers in MVP. | Partial | MCP client/server transport |
| OpenTelemetry now vs JSONL now | Use JSONL with trace-compatible IDs and field names. | Yes | OTel Collector/export backend |
| Durable execution now vs local artifacts now | Make IDs, ledgers, and step records replay-safe now. | Yes design only | LangGraph/Temporal |
| Create registries in Orchestrator vs Substrate source of truth | Orchestrator may include test fixtures only. Canonical registries belong to Semantic Substrate. | Yes fixtures | Substrate-governed canon changes |
| Exception Lake ingest vs no autonomous writes | Lake mode defaults to disabled or validate-only. Any commit-like path must be dual-gated. | Yes | Production ingest |
| Approval UI vs small MVP | Model approval data objects now; use file/terminal/manual review only. | Yes | Rich approval workflow UI |
| Multi-agent orchestration vs one classifier | One bounded classifier flow first. Add specialists only when measured complexity requires it. | Yes | Multi-agent handoffs |
| Data platform/lakehouse vs exception packet flow | Do not build a broad data platform first. Prove the contract-locked path. | Yes | Warehouse/lakehouse/analytics |

---

## 6. Recommended MVP dataflow

```text
synthetic exception input
  -> strict input schema validation
  -> synthetic-only policy gate
  -> load pinned Semantic Substrate manifest
  -> load route registry and event-class registry
  -> deterministic route/event allowlist validation
  -> one structured model adapter call or deterministic fake stub
  -> strict model-output validation
  -> evidence completeness validation
  -> append-only JSONL run ledger
  -> build local contract-locked evidence packet
  -> optional Exception Lake disabled / validate-only / explicit local synthetic handoff
  -> reviewer label or defect tag
```

### MVP flow table

| Step | Input | Output | Authority | Failure behavior |
|---|---|---|---|---|
| 1. Intake | `synthetic_exception_input` | normalized input + hash | Orchestrator schema | Reject if non-synthetic or malformed. |
| 2. Contract pin | `contract_manifest` | `manifest_id`, `manifest_hash` | Semantic Substrate | Reject if missing, floating, stale, or hash mismatch. |
| 3. Route allowlist | route/event registries | candidate set | Semantic Substrate | Reject unsupported route/event class. |
| 4. Classification | normalized input + candidates | proposed classification | Model adapter | Reject malformed or off-canon output. |
| 5. Validation | proposed event | validation results | Orchestrator validators | Reject on required validation failure. |
| 6. Ledger append | run steps | JSONL records | Orchestrator | Fail run if ledger cannot append. |
| 7. Packet build | input + proposal + validations + refs | evidence packet | Orchestrator | Reject incomplete packet. |
| 8. Lake handoff | packet or supported envelope | receipt or reject reason | Exception Lake | Record result and stop. |
| 9. Review label | evidence packet | outcome + defects | Human reviewer | Learning only; no canon mutation. |

---

## 7. Recommended future-state dataflow

```text
governed source systems
  -> Orchestrator service
  -> pinned Semantic Substrate manifest API
  -> approved model/tool registry
  -> MCP-compatible tool/resource adapters
  -> durable run store and approval workflow
  -> event bus or API handoff
  -> Exception Lake validation and append-only evidence
  -> aggregate learning candidates
  -> governance inbox
  -> approved promotion decisions
  -> new Semantic Substrate manifest
```

Future-state expansion should change **transport, durability, approval UX, and observability**, not the semantic chain of custody.

---

## 8. Data-flow architecture principles

1. **Contract lock before inference.** Load and validate a pinned manifest before any model call.
2. **Evidence packet over event spam.** Emit one complete packet, not a flood of weak events.
3. **Proposal, validation, admission.** Model proposes; deterministic validators decide readiness; Lake validates/adduces evidence.
4. **Read-only Substrate consumption.** No Orchestrator code path writes to canon.
5. **Fail closed on ambiguity.** Unknown route, unknown event class, malformed output, missing manifest, or missing evidence stops the run.
6. **Data minimization by default.** Move claim refs and hashes, not raw privileged payloads.
7. **Append-only runtime memory.** Ledger, audit, validation, and evidence records are append-only.
8. **Reviewer attention is the drum.** Optimize for accepted review-ready packets per reviewer hour.
9. **Frameworks stay behind adapters.** Agents SDK, LangGraph, Temporal, MCP, and OTel are replaceable implementation choices.
10. **Learning is governed.** Runtime signals may become candidates; canon changes only through Substrate governance.

---

## 9. ADR set summary

| ADR | Title | Decision |
|---|---|---|
| ADR-001 | Preserve the three-plane authority split | Substrate = truth; Orchestrator = execution; Lake = evidence. |
| ADR-002 | Evidence packet is the runtime unit | Build contract-locked packets, not bare event spam. |
| ADR-003 | Start local-first and synthetic-only | CLI first; no real client/matter data. |
| ADR-004 | Substrate is read-only to Orchestrator | No canon mutation from runtime. |
| ADR-005 | Structured outputs plus deterministic validation | Model output is proposal-only and schema-bound. |
| ADR-006 | JSONL ledger for MVP | Append-only, inspectable, migratable logs. |
| ADR-007 | Lake disabled or validate-only by default | No autonomous operational writes. |
| ADR-008 | Hybrid deterministic CLI with future adapters | Do not let any framework become the domain model. |
| ADR-009 | Design for MCP/OTel/durable execution, defer implementation | Interfaces now; stacks later. |
| ADR-010 | Missing evidence is a defect | Packet readiness requires provenance. |

---

## 10. MVP data objects

### Read-only / canonical objects

| Object | Owner | Minimum fields |
|---|---|---|
| `contract_manifest` | Semantic Substrate | `manifest_id`, `manifest_version`, `manifest_hash`, `schema_refs`, `registry_refs`, `policy_bundle_id`, `created_at` |
| `route_registry_entry` | Semantic Substrate | `route_id`, `allowed_event_classes`, `risk_tier`, `required_validators`, `handoff_policy` |
| `event_class_registry_entry` | Semantic Substrate | `event_class`, `description`, `allowed_routes`, `severity_rules`, `evidence_requirements` |
| `validation_contract` | Semantic Substrate | `contract_id`, `schema_ref`, `validator_id`, `version`, `compatibility_rule` |
| `runtime_policy` | Semantic Substrate | `policy_bundle_id`, `synthetic_only`, `allowed_modes`, `forbidden_fields`, `approval_rules` |

### Runtime / Orchestrator-owned objects

| Object | Owner | Minimum fields |
|---|---|---|
| `synthetic_exception_input` | Orchestrator input | `input_id`, `synthetic`, `contains_real_client_data`, `contains_real_matter_data`, `source_type`, `route_hint`, `confidentiality_label`, `privilege_label`, `source_claim_refs`, `payload` |
| `run_envelope` | Orchestrator | `run_id`, `lineage_root_id`, `trace_id`, `correlation_id`, `command_name`, `environment`, `started_at`, `actor_type`, `actor_id` |
| `route_decision_record` | Orchestrator | `route_decision_id`, `selected_route_id`, `candidate_routes`, `allowed_event_classes`, `reason_code`, `manifest_id` |
| `model_call_record` | Orchestrator | `model_call_id`, `adapter`, `model_name`, `prompt_version`, `schema_version`, `request_hash`, `response_hash`, `tokens_in`, `tokens_out`, `latency_ms` |
| `proposed_exception_event` | Orchestrator proposal | `route_id`, `event_class`, `severity`, `reason_codes`, `supporting_claim_refs`, `confidence`, `notes` |
| `validation_result` | Orchestrator / Lake | `validation_result_id`, `validator`, `validator_version`, `status`, `violation_codes`, `containment_action`, `created_at` |
| `run_ledger_entry` | Orchestrator | `ledger_version`, `run_id`, `step_index`, `step_type`, `step_status`, `trace_id`, `span_id`, `manifest_id`, `correlation_id`, `timestamp`, `artifact_refs` |
| `evidence_packet` | Orchestrator → Lake | `evidence_id`, `run_id`, `manifest_id`, `manifest_hash`, `policy_bundle_id`, `route_decision`, `proposal`, `validation_results`, `source_claim_refs`, `message_history`, `human_review_required`, `packet_hash` |
| `approval_record` | Human governance / Orchestrator | `approval_id`, `run_id`, `required`, `approver_role`, `decision`, `decision_reason`, `decided_at` |
| `lake_handoff_receipt` | Exception Lake | `handoff_id`, `evidence_id`, `mode`, `attempted`, `status`, `reject_reasons`, `received_at` |

---

## 11. First 10 build tasks

| # | Task | Tests | Stop condition |
|---:|---|---|---|
| 1 | Scaffold package and CLI | CLI help; import; package metadata | Stop if CLI needs network/service. |
| 2 | Add strict synthetic input contract | Reject missing/false synthetic and real-data flags | Stop if real client/matter flags can pass. |
| 3 | Add pinned manifest loader | Missing/hash mismatch fail; valid fixture loads | Stop if loader writes to Substrate or accepts floating latest. |
| 4 | Add route/event-class fixture registries | Unknown route/event rejected; allowed pairing passes | Stop if Orchestrator invents IDs. |
| 5 | Add run identity and trace context | IDs present in every artifact | Stop if artifacts lack run/trace/correlation/manifest IDs. |
| 6 | Add model adapter and fake stub | Fake valid output passes; invalid enum fails | Stop if free-form text is parsed heuristically. |
| 7 | Add structured-output validation | Missing/extra/off-canon fields fail | Stop if malformed output reaches packet build. |
| 8 | Add append-only JSONL ledger | Appends not overwrites; failure path recorded | Stop if ledger failure is ignored. |
| 9 | Add evidence packet builder | Builds only after validation; hashes stable | Stop if packet lacks manifest hash, validations, or source refs. |
| 10 | Add Lake gateway disabled/validate-only | Disabled by default; validate-only does not commit | Stop if any operational write occurs by default or from model output. |

---

## 12. Runtime stop conditions

The CLI must stop immediately if:

1. Manifest is missing, unreadable, unsigned, or hash-mismatched.
2. Contract pin is absent or floating.
3. Synthetic-only gate fails.
4. Input contains real client or matter data flags.
5. Unsupported `route_id` is present.
6. Unsupported `event_class` is present.
7. Route/event-class pairing is not allowed by registry.
8. Model output is malformed, missing required keys, or contains extra fields.
9. Model invents semantic authority, schemas, route IDs, event classes, or governance rules.
10. Any required validator fails.
11. Evidence packet lacks manifest hash, validation results, source claim refs, trace IDs, or packet hash.
12. Ledger write fails.
13. Boundary payload contains forbidden data, secrets, unrestricted transcripts, hidden reasoning, or raw privileged content.
14. Any code path attempts to write to Semantic Substrate.
15. Any code path attempts a client-system, matter-system, connector, or operational write.
16. Exception Lake handoff is requested without an allowed explicit mode.
17. Retry/model/token/cost/time budget is exceeded.
18. Ambiguity cannot be resolved within pinned contracts.
19. Approval is required but no approval record exists.
20. The run cannot be reconstructed from ledger and packet artifacts.

---

## 13. Build-level stop conditions

Stop the MVP build and return to architecture review if:

- a task requires real client or matter data;
- a task requires Orchestrator to modify canonical Substrate meaning;
- a task requires web app, queue, background worker, or dashboard to prove the first flow;
- a task requires MCP, LangGraph, Temporal, or OpenTelemetry Collector before the CLI path passes;
- Exception Lake integration requires bypassing the Lake validation boundary;
- packet quality cannot be tested with fixtures;
- reviewers cannot reconstruct a run from JSONL ledger plus evidence packet;
- the fake model path cannot pass end-to-end deterministically;
- the team cannot state which manifest and hash governed a run.

---

## 14. Final clean decision

Build **LawFirm OS Orchestrator MVP** as a **bottleneck-first, synthetic-only, contract-locked evidence-packet factory**.

It should not be a general agent platform yet. It should not be a semantic authoring tool. It should not be a production connector layer. It should coordinate one safe run, under one pinned semantic manifest, produce one validated evidence packet, append its own audit trail, and optionally hand off through the existing Exception Lake validation boundary.

That is the smallest useful system that is already governed, testable, replayable, auditable, and ready to evolve.
