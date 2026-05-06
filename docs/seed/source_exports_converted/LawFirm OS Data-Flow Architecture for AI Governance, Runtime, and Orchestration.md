# LawFirm OS Data-Flow Architecture for AI Governance, Runtime, and Orchestration

## Executive summary

No retrievable uploaded project file was available in this conversation,
so the architectural constraints below are extracted from your prompt
and treated as binding design decisions.

The strongest starting point for LawFirm OS is **not** a warehouse, a
lakehouse program, or a generalized agent platform. It is a
**contract-locked exception-classification flow** in which the Semantic
Substrate publishes immutable manifests, the Orchestrator pins one
manifest per run, every model and tool result is forced into structured
output, and only a provenance-rich evidence packet is allowed to cross
into the Exception Lake Runtime. That approach lines up with current
practice around explicit data contracts, common schema and API
descriptions, interoperable event envelopes, lineage over
runs/jobs/datasets, and observability built from traces, logs, and
metrics. [\[1\]](https://www.nist.gov/itl/ai-risk-management-framework)

The **main runtime unit of flow** should be a **contract-locked evidence
packet**, not a bare exception event. A bare event is too weak for legal
operations because it does not carry enough provenance, validation,
routing, and review context. The packet should carry: the proposed
exception event, the pinned contract manifest ID and hash, validation
outcomes, trace and correlation IDs, source claim-check references,
model/tool call summaries, and approval state. Canonical meaning must
stay in the Semantic Substrate; runtime facts and proposals live in the
Exception Lake; model output is always proposal-only. That separation is
the safest way to operationalize AI risk management and the legal
profession’s duty to verify AI outputs and protect client information.
[\[2\]](https://docs.getdbt.com/docs/use-dbt-semantic-layer/sl-architecture)

The **true bottleneck** to attack first is not model latency. It is
**trusted review capacity at the governance boundary**: the amount of
human attention required to decide whether a machine-produced suggestion
is safe, well-supported, and semantically valid. In law-firm operations,
that bottleneck is load-bearing because lawyers remain accountable for
work product, confidentiality, and downstream action. The first
world-class dataflow should therefore minimize reviewer rework by
turning unstructured model completions into small, reviewable,
contract-locked packets that make validation and provenance explicit.
[\[3\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)

The design recommendation is straightforward. Build a **small
control-plane/evidence-plane split** now, keep transport simple, and
scale later without changing the unit of flow. In the MVP, use CLI plus
immutable files plus optional local ingestion. In the enterprise state,
keep the same contracts but move evidence transport onto APIs and
queues, add durable run storage, add OpenTelemetry-compatible export,
and expose tools/resources through MCP-compatible adapters behind the
Orchestrator. The architecture becomes future-proof because the
contracts stay stable while the transport matures.
[\[4\]](https://swagger.io/specification/)

The first world-class dataflow to build is therefore:

**synthetic input → pinned substrate manifest → deterministic route
allowlist check → structured model/tool execution → schema/policy
validation → append-only run ledger → contract-locked evidence packet →
optional Exception Lake ingestion**

That is the smallest flow that is already “world-class” because it is
governed, replayable, observable, lineaged, fail-closed, and legally
defensible.

## Architecture decisions and data object taxonomy

Your existing architecture already implies a strong set of constraints.
They should be treated as hard boundaries, not preferences.

**Binding architecture decisions**

1.  **The Semantic Substrate is the control plane.** It owns meaning,
    schemas, route authority, governance boundaries, and validation
    contracts.
2.  **The Exception Lake Runtime is the evidence plane.** It stores
    append-only runtime observations, exception events, audit records,
    and learning candidates, but it cannot define meaning.
3.  **The Orchestrator is the execution plane.** It coordinates models,
    tools, agents, approvals, policy gates, and run ledgers, but it
    cannot redefine semantic truth.
4.  **Model outputs are proposals.** They are never canonical truth,
    never semantic authority, and never direct substrate mutations.
5.  **Runtime evidence cannot mutate the Substrate.** Runtime can only
    emit candidate learning signals or proposals for human review.
6.  **Human approval is a first-class system boundary.** Promotion into
    the Substrate is a governance act, not a side effect of runtime
    success.
7.  **Data minimization is mandatory.** The system should move the
    minimum needed data across each boundary and prefer references over
    payload fanout.
8.  **Fail-closed is the default.** Route mismatches, invalid event
    classes, malformed model output, missing manifests, or forbidden
    data should stop the flow.
9.  **Not all data should move everywhere.** Transport should be
    selective and bounded by authority, confidentiality, and purpose.
10. **Append-only should be the norm for runtime records.** Corrections
    happen through superseding records, not mutable overwrites.

**The main unit of flow**

The best answer to “what is the main unit of flow?” is:

**The principal cross-boundary runtime unit should be a contract-locked
evidence packet.**

Why this and not a plain exception event?

- An exception event is the **atomic operational proposal**.
- A validation result is the **atomic gate artifact**.
- A route decision is the **atomic policy-application artifact**.
- A model/tool call record is the **atomic execution artifact**.
- A run ledger entry is the **atomic audit/trace artifact**.
- But the **evidence packet** is the smallest unit that can safely cross
  from execution into runtime evidence because it bundles proposal,
  provenance, validation, contract lock, and lineage together.

**Data object taxonomy**

| Object                       | Owner                                   | Status                     | Canonical semantic authority | Cross-boundary role                    |
|------------------------------|-----------------------------------------|----------------------------|------------------------------|----------------------------------------|
| `route_registry_entry`       | Semantic Substrate                      | Canonical                  | Yes                          | Read-only outbound                     |
| `event_class_registry_entry` | Semantic Substrate                      | Canonical                  | Yes                          | Read-only outbound                     |
| `validation_contract`        | Semantic Substrate                      | Canonical                  | Yes                          | Read-only outbound                     |
| `governance_boundary`        | Semantic Substrate                      | Canonical                  | Yes                          | Read-only outbound                     |
| `contract_manifest`          | Semantic Substrate                      | Canonical control artifact | Yes                          | Pinned by every run                    |
| `promotion_decision`         | Human governance → Substrate            | Canonical after approval   | Yes                          | Inbound to Substrate only              |
| `proposed_exception_event`   | Orchestrator                            | Proposal                   | No                           | Inside evidence packet                 |
| `validation_result`          | Orchestrator / Exception Lake validator | Runtime fact               | No                           | Gate artifact                          |
| `route_decision_record`      | Orchestrator                            | Runtime fact               | No                           | Audit/evidence                         |
| `model_call_record`          | Orchestrator                            | Runtime fact               | No                           | Ledger + evidence support              |
| `tool_call_record`           | Orchestrator                            | Runtime fact               | No                           | Ledger + evidence support              |
| `run_ledger_entry`           | Orchestrator                            | Audit/runtime fact         | No                           | Append-only primary ledger             |
| `evidence_packet`            | Orchestrator → Exception Lake           | Runtime evidence envelope  | No                           | Main runtime transport unit            |
| `exception_event_record`     | Exception Lake                          | Runtime evidence fact      | No                           | Append-only operational history        |
| `learning_candidate`         | Exception Lake                          | Proposal                   | No                           | Outbound to governance only            |
| `pressure_vector`            | Exception Lake analytics                | Aggregate analytic signal  | No                           | Should not be a primary transport unit |
| `trace/log/metric`           | Observability plane                     | Audit/observability only   | No                           | Cross-cutting telemetry                |

**Which things are canonical, runtime, proposal-only, or audit-only**

- **Canonical:** schemas, registries, route IDs, event class vocabulary,
  promotion decisions after approval.
- **Runtime evidence:** evidence packets, exception events, validation
  outcomes, run ledger entries, audit records.
- **Model-generated proposals:** proposed exception events, draft
  normalizations, draft reason codes, route suggestions.
- **Audit-only:** traces, logs, metrics, retry records, dead-letter
  records, message histories.

**Units that should never cross certain boundaries**

The following should **not** cross from one leg of the system to another
except by tightly controlled claim-check reference:

- full real client documents,
- full matter files,
- unrestricted prompt transcripts,
- raw tool payloads that contain privileged or confidential content,
- chain-of-thought or hidden reasoning artifacts,
- substrate authoring drafts,
- secrets, credentials, and provider tokens.

For LawFirm OS, “pressure vectors” belong in Exception Lake analytics,
not on the main runtime bus. “Promotion decisions” become canonical only
after human approval. “Route decisions” are evidence of policy
application, not semantic authority.

## World-class principles for LawFirm OS

At a reference-architecture level, LawFirm OS should combine governance
from National Institute of Standards and
Technology[\[5\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)’s
AI RMF, explicit schema/API/event contracts, bounded canonical models
instead of a giant enterprise meta-model, lineage at run/job/dataset
level, OpenTelemetry-compatible traces/logs/metrics with standardized
propagation, and strict legal confidentiality/accountability rules for
AI-assisted work. Those principles are directly supported by the AI RMF
and Playbook, semantic-layer thinking, multiple bounded canonical
models, OpenLineage, Trace Context, OpenTelemetry, CloudEvents, JSON
Schema, OpenAPI, medallion-style layered refinement, unified
stream/batch execution models, and MCP’s
client-host-server/tool-resource separation.
[\[6\]](https://www.nist.gov/itl/ai-risk-management-framework)

**Principle matrix**

| Principle                  | Mature interpretation                                   | Direct application to LawFirm OS                                                                                                                         |
|----------------------------|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Data contracts             | Versioned schemas plus compatibility and quality rules  | Every route, event class, evidence packet, audit record, and approval object is schema-bound and versioned                                               |
| Canonical data model       | Use a common language only where integration needs it   | Substrate canonicalizes only cross-boundary terms such as `route_id`, `event_class`, `confidentiality_label`, `approval_state`, not every internal field |
| Bounded context            | Large systems need multiple contextual models           | Keep separate bounded models for exceptions, evidence, approvals, substrate authoring, and external-tool adapters                                        |
| Semantic layer             | Centralize shared definitions and queryable meaning     | Substrate is the semantic layer for routes, contracts, vocabulary, and governance boundaries                                                             |
| Event-driven architecture  | Events must be portable, correlated, and safe to fail   | Use contract-locked envelopes; reject invalid events; keep dead letters and idempotency explicit                                                         |
| Data lineage               | Track inputs, outputs, runs, and parent-child execution | Treat each orchestration run as a lineage root; carry evidence, tool, and approval links forward                                                         |
| Data observability         | Use traces, metrics, and logs together                  | Make run health, queue pressure, validation failures, and lineage gaps visible from day one                                                              |
| Stream vs batch            | Unify contracts even if transports differ               | Runtime exception handling is event-like; retrospectives and learning candidates are batch or replay jobs over the same contracts                        |
| Data mesh                  | Domain ownership plus federated governance              | Adopt federated governance principles, but do **not** build a full mesh platform first                                                                   |
| Medallion-style refinement | Progressively improve data quality through layers       | Inside Exception Lake: raw/ingest references → validated evidence packets → curated governance analytics; never treat those layers as semantic authority |
| Audit and evidence         | Keep append-only documentary history                    | Ledger, exception events, approvals, and dead letters are append-only; corrections are new records                                                       |
| Tool/resource protocols    | Separate context, tools, prompts, and session control   | Use MCP-compatible adapters for tools/resources behind the Orchestrator, not as the control protocol between core repos                                  |
| AI governance              | Governance must precede action                          | Human approval remains the only path to semantic promotion or high-risk operational release                                                              |

That matrix leads to a crucial architectural stance: **LawFirm OS should
use a bounded canonical model, not a giant enterprise-wide canonical
universe**. The bounded-context literature is very clear that large
organizations struggle when they force every domain into one unified
model; the right approach is multiple canonical models with explicit
translation where overlap exists. In LawFirm OS, the Semantic Substrate
should therefore canonicalize only what crosses governance boundaries,
not every possible law-firm object.
[\[7\]](https://martinfowler.com/bliki/MultipleCanonicalModels.html)

**Data contract model**

LawFirm OS should use four layers of contracts.

- **Semantic contracts** in the Substrate define route IDs, event
  classes, field meanings, policy bundles, confidentiality labels, and
  promotion rules.
- **Object contracts** define JSON payloads using a stable schema
  language with validation and meta-schema support.
- **Interface contracts** define synchronous APIs and asynchronous event
  channels.
- **Execution contracts** define model-output schemas, tool I/O schemas,
  approval requirements, and fail-closed runtime rules.

For canonical contracts, use a compatibility policy equivalent to **full
transitive compatibility** whenever possible. If a change truly breaks
compatibility, create a new contract subject, namespace, or route rather
than mutating meaning in place. That is the cleanest way to preserve
replayability and legal defensibility.
[\[8\]](https://json-schema.org/specification)

**Observability model**

Use OpenTelemetry-style signals from the start, even if the MVP stores
them in JSONL. Traces show the causal path of a run, logs record
timestamped events with metadata, and metrics quantify runtime pressure.
Context propagation is what ties them together, and the default
propagation model is the industry-standard Trace Context header format.
Semantic conventions matter because they keep field names stable across
libraries, services, and export backends.
[\[9\]](https://opentelemetry.io/docs/concepts/context-propagation/)

**Legal and privacy principle**

For a law-firm system, the confidentiality boundary must reflect
guidance from the American Bar
Association[\[10\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html):
lawyers remain accountable for AI-assisted work product, must understand
tool limitations, must protect client information, and should not treat
AI output as self-verifying truth. That means LawFirm OS should encode
“proposal, not truth” directly into its data model and should minimize
the movement of sensitive data by default.
[\[11\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)

## Flow model, boundaries, bottlenecks, and defects

The flow model below translates your three-repo architecture into a
control/evidence/execution pattern informed by schema-bound contracts,
lineage metadata, message history, correlation identifiers, idempotent
receivers, dead-letter handling, and claim-check minimization.
[\[12\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)

**Flow matrix**

| Flow                                                              | Contract and schema                                                            | Authority                            | Allowed data                                                                                                   | Forbidden data                                                                      | Validation gate and failure mode                                                                | Audit and tracing                                                                 | Bottleneck risk                                    |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|----------------------------------------------------|
| Semantic Substrate → Orchestrator                                 | `contract_manifest`, `route_registry`, `event_class_registry`, `policy_bundle` | Substrate only                       | IDs, schemas, hashes, compatibility rules, tool allowlists, prompt template IDs                                | Runtime evidence, ad hoc overrides, mutable semantic drafts                         | Signature/hash check, schema validation, compatibility check; on failure the run does not start | Record `manifest_id`, `manifest_hash`, `policy_bundle_id` in root ledger entry    | Stale manifest cache, release lag                  |
| Semantic Substrate → Exception Lake Runtime                       | `runtime_validation_bundle`, retention classes, ingest schema refs             | Substrate only                       | Validation contracts, allowed versions, retention classes, privilege label vocabulary                          | Runtime proposals, analytics, semantic edits                                        | Boot-time contract lock; disable ingest on mismatch                                             | Lake stores active validator bundle hash                                          | Validator drift between lake and orchestrator      |
| Orchestrator → Exception Lake Runtime                             | `evidence_packet`, `proposed_exception_event`, `audit_event`                   | Orchestrator emits; Lake stores      | Structured proposals, validation results, source claim refs, model/tool summaries, route decision, trace IDs   | Canonical schema changes, raw secrets, unrestricted payloads, unbounded transcripts | Schema + policy + redaction + idempotency check; invalid packets go to dead-letter quarantine   | Must include `run_id`, `trace_id`, `correlation_id`, `evidence_id`, `manifest_id` | Overproduction of low-value evidence, packet bloat |
| Exception Lake Runtime → Semantic Substrate as learning candidate | `learning_candidate`, `promotion_proposal_input`                               | Runtime may propose only             | Aggregated evidence stats, repeated correction patterns, support counts, linked evidence IDs, pressure vectors | Direct substrate mutations, single-run model suggestions, raw privileged content    | Aggregate-threshold and anonymization checks; rejection leaves candidate queued                 | Must preserve supporting evidence lineage                                         | Human-review queue saturation                      |
| Human approval/governance → Semantic Substrate                    | `promotion_decision`, signed patch, approval metadata                          | Human approvers                      | Approved schema diffs, registry changes, policy changes, effective dates                                       | Unreviewed model output, direct evidence-as-truth, silent semantic mutation         | Two-person rule for semantic changes; CI compatibility + policy tests; failure blocks merge     | Signed approval log with reasons and linked evidence                              | Governance latency                                 |
| Tool/model calls → Orchestrator run ledger                        | `model_call_record`, `tool_call_record`, `run_step_record`                     | Adapters emit; Orchestrator persists | Parameters, redacted inputs, output claim refs, latency, tokens, status, provider details                      | Secrets, full privileged docs, hidden reasoning, uncontrolled payload dumps         | Structured output parsing and adapter schema validation; malformed output fails step            | Trace span per call; append-only ledger line per step                             | Log I/O overhead, adapter drift                    |
| Run ledger → audit/evidence events                                | `audit_record`, `message_history`, final `evidence_packet` assembly            | Orchestrator exporter                | Step history, action types, actor, object refs, result codes, hashes                                           | Mutable overwrites, missing causality links                                         | Sequence monotonicity, digest chaining, completeness checks; alert on exporter failure          | Trace/log correlation and message history required                                | Fan-out to too many sinks                          |

**Boundary matrix**

| Boundary                         | What may cross                                            | What must not cross                                                                        | Control                                                     |
|----------------------------------|-----------------------------------------------------------|--------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| Semantic authority boundary      | Approved contracts out; approved promotion decisions in   | Runtime evidence as truth; automatic schema mutation                                       | Manifest pinning, signed approvals, CI compatibility gates  |
| Orchestrator execution boundary  | Redacted context in; proposals and ledger records out     | Raw privileged corpora, secrets, uncontrolled provider transcripts                         | Claim-check refs, field allowlists, adapter validators      |
| Exception Lake evidence boundary | Validated evidence in; aggregate candidates out           | Semantic edits, runtime-written registries, raw high-risk payload re-broadcast             | Ingest validator, dead-letter quarantine, retention classes |
| Human governance boundary        | Diffs, evidence bundles, approval decisions               | Opaque black-box outputs without provenance                                                | Review UI, evidence links, approval logs                    |
| External model/tool boundary     | Minimal slices, schema-constrained requests and responses | Full client files by default, substrate internals, unrestricted shell/process access       | Adapter layer, tool allowlist, MCP resource/tool separation |
| Environment boundary             | Promoted manifests, synthetic fixtures, approved config   | Production client data into dev/test, lower-environment telemetry with live matter content | Environment-scoped configs, synthetic-only gate in MVP      |

**Bottleneck map**

The first constraint is **review trust**, not compute. In practice, the
slowest and most expensive step in a governed legal AI flow is the human
effort needed to determine whether a machine-produced result is safe and
supported. That constraint is exactly where LawFirm OS must concentrate
its first design energy.
[\[13\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)

| TOC element | LawFirm OS choice                                                                                                                                      |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Drum**    | Human review capacity for high-risk proposals and semantic promotions; secondarily, Exception Lake validation throughput                               |
| **Buffer**  | Candidate queue, manifest cache, claim-check artifact store, dead-letter quarantine, approval inbox                                                    |
| **Rope**    | Orchestrator rate limiters, per-route quotas, policy gates that block proposal creation before validation, and “no emit without evidence packet” rules |

**Which bottleneck should the Orchestrator attack first**

The Orchestrator should attack **review rework** first. Every run should
arrive at the reviewer already normalized into a valid route, bounded
event class, explicit source references, explicit validation outcomes,
and explicit missing-data flags. The reviewer should be deciding whether
the packet is sufficient, not reconstructing what happened from scratch.

**Which bottlenecks should remain manual**

Some constraints should stay manual because automation would create
larger governance risk than throughput gain:

- semantic schema changes,
- event class additions,
- route authority changes,
- approval-policy changes,
- first-time real-data connector approval,
- deletion/retention exception approvals,
- promotion from runtime signal into substrate meaning.

**How to prevent overproduction**

Low-value event overproduction is a classic failure mode in message
systems. LawFirm OS should prevent it by making proposal creation
conditional on route eligibility, schema validity, provenance
completeness, and size controls. Use claim checks for bulky or sensitive
payloads, idempotent ingestion to neutralize retries, dead-letter
quarantine for irreparable failures, and per-route quotas for noisy
routes.
[\[14\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)

**Metrics that reveal bottlenecks**

- `manifest_load_latency_ms`
- `contract_lock_fail_total`
- `input_validation_fail_total`
- `output_validation_fail_total`
- `dead_letter_total`
- `evidence_packet_bytes_p95`
- `proposals_created_total`
- `proposals_rejected_total`
- `manual_correction_rate`
- `approval_queue_depth`
- `approval_cycle_time_p95`
- `promotion_rejection_rate`
- `duplicate_packet_total`
- `lineage_gap_total`
- `trace_coverage_pct`

Those metrics map cleanly onto runtime measurements, logs, and
correlated traces.
[\[15\]](https://opentelemetry.io/docs/concepts/signals/metrics/)

**Lean waste table**

| Waste                    | How it appears in LawFirm OS                                              | Control                                                   |
|--------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------|
| Duplicate data movement  | Same payload copied into prompts, ledgers, lake, dashboards               | Claim checks; ledger stores refs and digests              |
| Unnecessary model calls  | Routing done by model when deterministic rules suffice                    | Deterministic pre-routing before model use                |
| Stale context            | Old manifest or policy bundle applied to new runtime                      | Contract lock per run; manifest age alarms                |
| Invalid events           | Free-text outputs that cannot be parsed or governed                       | Structured output + schema validation                     |
| Unverified evidence      | Event emitted without source linkage                                      | Evidence packet requires source claims and hashes         |
| Unclear authority        | Runtime begins redefining semantic meaning                                | Hard owner matrix; no back-mutation path                  |
| Too many dashboards      | Separate dashboards for run status, lake status, approval status, quality | One ledger-centered operational view, one governance view |
| Unbounded logs           | Verbose provider dumps and raw tool payloads                              | Redaction, retention classes, field caps                  |
| Repeated manual checks   | Reviewers keep checking the same contract facts                           | Precompute validation outcomes in packet                  |
| Schema drift             | Prompt or output changes without versioning                               | Versioned prompt templates and contract tests             |
| Tool output drift        | External tools change shape silently                                      | Adapter schemas and canary tests                          |
| Hidden rework            | Reviewer corrects output but system learns nothing                        | Correction captured as labeled runtime evidence           |
| Retry storms             | Malformed packets retried indefinitely                                    | Dead-letter after bounded retries                         |
| Low-value event creation | Overeager candidate generation from weak signals                          | Support thresholds and significance tests                 |

**Data-flow defect taxonomy**

| Defect class       | Definition                                                       | Primary gate                       |
|--------------------|------------------------------------------------------------------|------------------------------------|
| Semantic defect    | Wrong `route_id`, wrong `event_class`, wrong field meaning       | Substrate contract validation      |
| Structural defect  | Payload violates schema or missing required fields               | JSON Schema validator              |
| Provenance defect  | Missing source refs, hashes, or generation path                  | Evidence packet completeness check |
| Lineage defect     | Missing or broken `run_id`, `trace_id`, parent/child links       | Ledger and lineage validator       |
| Governance defect  | Missing approval or wrong approver for a promotion               | Approval workflow validator        |
| Privacy defect     | Overexposed or unauthorized data crosses a boundary              | Redaction and claim-check gate     |
| Temporal defect    | Stale manifest, expired policy, or replay against wrong contract | Contract-lock gate                 |
| Duplication defect | Same packet or event ingested multiple times                     | Idempotent receiver                |
| Retry defect       | Excessive retries without new information                        | Retry policy + dead-letter         |
| Tool defect        | Tool output does not satisfy adapter contract                    | Tool adapter validator             |
| Model defect       | Structured output malformed or unsupported                       | Model-output parser + schema check |
| Audit defect       | Missing ledger line, missing message history, mutable overwrite  | Append-only audit validator        |

**Identifier model**

Use **UUIDv7** for sortable domain IDs where possible, because modern
lineage tooling explicitly recommends it for run IDs. Complement that
with Trace Context identifiers for distributed tracing.
[\[16\]](https://openlineage.io/docs/spec/facets/run-facets/)

| Identifier              | Purpose                                                          |
|-------------------------|------------------------------------------------------------------|
| `manifest_id`           | Pinned contract bundle for the run                               |
| `run_id`                | Root execution instance                                          |
| `trace_id`              | Distributed trace identity                                       |
| `span_id`               | Individual execution span                                        |
| `correlation_id`        | Business/request correlation across systems and queues           |
| `lineage_root_id`       | Long-lived workflow root, especially when approvals happen later |
| `route_decision_id`     | One route application record                                     |
| `model_call_id`         | One model invocation                                             |
| `tool_call_id`          | One tool invocation                                              |
| `validation_result_id`  | One validation output                                            |
| `evidence_id`           | One evidence packet                                              |
| `exception_event_id`    | One stored exception event                                       |
| `approval_id`           | One human review action                                          |
| `promotion_decision_id` | One canonical promotion result                                   |

**Minimum run ledger fields**

`run_id`, `lineage_root_id`, `trace_id`, `span_id`, `correlation_id`,
`manifest_id`, `policy_bundle_id`, `environment`, `command_name`,
`input_id`, `synthetic_flag`, `confidentiality_label`,
`privilege_label`, `route_candidate_set`, `selected_route_id`,
`route_decision_id`, `step_type`, `step_status`, `model_call_id`,
`tool_call_id`, `validation_result_id`, `evidence_id`,
`event_class_proposed`, `human_review_required`, `started_at`,
`ended_at`, `duration_ms`, `retry_count`, `error_code`,
`error_message_redacted`, `source_claim_refs`, `output_claim_refs`,
`message_history`.

**Minimum audit fields**

`audit_record_id`, `timestamp`, `actor_type`, `actor_id`, `action_type`,
`object_type`, `object_id`, `trace_id`, `correlation_id`, `manifest_id`,
`reason_code`, `before_hash`, `after_hash`, `approval_id`,
`signature_or_attestation`, `retention_class`, `environment`.

## Diagram set

**Current-state diagram set**

**C4-style context diagram**

    flowchart LR
        U[Operations user or caller]
        G[Governance reviewer]
        M[Model providers]
        T[Tool and resource providers]
        subgraph LFO[LawFirm OS]
            SS[Semantic Substrate\ncontrol plane]
            OR[Orchestrator\nexecution plane]
            EL[Exception Lake Runtime\nevidence plane]
        end

        U --> OR
        SS --> OR
        SS --> EL
        OR --> EL
        EL --> G
        G --> SS
        OR --> M
        OR --> T

Boundary note: the Substrate is the control plane, the Orchestrator is
the execution plane, and the Exception Lake is the evidence plane.
External models and tools are behind the Orchestrator boundary, not
peers of the Substrate. That separation fits AI RMF governance,
semantic-layer centralization, lineage-aware execution, and MCP’s clear
separation among host, client, server, resources, and tools.
[\[17\]](https://www.nist.gov/itl/ai-risk-management-framework)

**Three-repo dataflow diagram**

    flowchart LR
        SS[Semantic Substrate] -- contract manifests / registries --> OR[Orchestrator]
        SS -- validation bundles / policy bundles --> EL[Exception Lake Runtime]
        OR -- validated evidence packets / proposed exception events --> EL
        EL -- learning candidates only --> GI[Governance inbox]
        GI -- approved promotions only --> SS

        OR -. no semantic mutation .-> SS
        EL -. no direct substrate mutation .-> SS

Boundary note: only one upstream semantic authority exists, and the
feedback loop is proposal-only until human governance approves a
promotion. That matches bounded canonical modeling, explicit event
contracts, and legal-accountability requirements around AI review.
[\[18\]](https://martinfowler.com/bliki/MultipleCanonicalModels.html)

**Orchestrator run lifecycle diagram**

    sequenceDiagram
        participant C as CLI / caller
        participant O as Orchestrator
        participant S as Semantic Substrate manifest
        participant MT as Model / Tool adapters
        participant L as Run ledger
        participant E as Exception Lake

        C->>O: classify-exception(input)
        O->>S: load pinned manifest
        S-->>O: manifest_id + registries + schemas
        O->>O: validate input and allowed route/event_class
        O->>L: append run_started
        O->>MT: deterministic tool/model steps
        MT-->>O: structured proposal
        O->>O: parse + validate + redact
        O->>L: append step records
        O->>O: build evidence packet
        O->>L: append run_completed or run_failed
        O->>E: optionally ingest evidence packet

Boundary note: the run starts with contract lock rather than with
inference, because governance must constrain execution before any model
output exists. The ledger is append-only and the ingest happens only
after validation succeeds.
[\[19\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)

**Exception event lifecycle diagram**

    flowchart TD
        I[Intake record] --> V1[Input validation]
        V1 --> R[Route eligibility and policy gate]
        R --> P[Proposed exception event]
        P --> V2[Output validation]
        V2 --> EP[Evidence packet assembly]
        EP --> IG[Exception Lake ingest]
        IG --> ER[Stored exception event record]
        ER --> GA[Governance and ops analytics]
        ER --> LC[Learning candidate extractor]

        V1 --> DL[Dead-letter quarantine]
        V2 --> DL

Boundary note: the lifecycle makes a clear distinction between a
proposal and a stored runtime record. The stored runtime record is
authoritative for audit and operations, but it does not define semantic
meaning. Dead letters are not retries-without-end; they are governed
failure sinks.
[\[20\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)

**Evidence packet flow diagram**

    flowchart LR
        SI[Source intake refs]
        CM[Contract manifest]
        RD[Route decision]
        MC[Model call summary]
        TC[Tool call summaries]
        VR[Validation results]
        MH[Message history]
        ID[Trace and correlation IDs]

        SI --> EP[Evidence packet]
        CM --> EP
        RD --> EP
        MC --> EP
        TC --> EP
        VR --> EP
        MH --> EP
        ID --> EP

        EP --> EL[Exception Lake Runtime]

Boundary note: source material should usually enter the packet by
**claim-check reference and digest**, not by full payload copy. Message
history belongs in the system/control section of the packet, while
application meaning stays in the event body.
[\[21\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)

**Contract-lock flow diagram**

    sequenceDiagram
        participant SS as Semantic Substrate
        participant O as Orchestrator
        participant EL as Exception Lake
        participant RV as Replay / analytics

        SS->>O: publish contract_manifest.vN
        SS->>EL: publish validator_bundle.vN
        O->>O: pin manifest_id and hash at run start
        O->>EL: evidence_packet(manifest_id, hash, payload)
        EL->>EL: verify payload against pinned validator bundle
        EL-->>O: accept or reject
        RV->>EL: read packet + manifest_id
        RV->>SS: fetch exact historical contract bundle for replay

Boundary note: contract lock is the critical mechanism that makes
replay, audit, and legal explanation possible. Without it, the same
payload could mean different things after schema drift.
[\[22\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)

**Human approval and promotion decision flow diagram**

    flowchart TD
        LC[Learning candidate or authored change] --> GI[Governance inbox]
        GI --> EV[Evidence bundle review]
        EV --> DF[Semantic diff review]
        DF --> AP[Approval gate]
        AP -->|approved| PR[Promotion decision record]
        PR --> SS[Semantic Substrate update]
        AP -->|rejected| RJ[Rejected candidate archive]
        SS --> MF[New manifest version]
        MF --> OR[Orchestrator]
        MF --> EL[Exception Lake validator]

Boundary note: promotion is not model training, not automatic drift
response, and not runtime mutation. It is a governed semantic change
supported by evidence and approvals. That is exactly where manual
control should remain.
[\[23\]](https://www.nist.gov/itl/ai-risk-management-framework)

**Observability and tracing flow diagram**

    flowchart LR
        C[Caller]
        O[Orchestrator]
        M[Model adapter]
        T[Tool adapter]
        E[Exception Lake]
        JL[JSONL traces/logs/metrics in MVP]
        OC[OpenTelemetry Collector in future]
        B[Observability backend]

        C --> O
        O --> M
        O --> T
        O --> E

        O --> JL
        M --> JL
        T --> JL
        E --> JL

        JL --> OC
        OC --> B

Boundary note: the MVP can store telemetry as structured JSONL while
preserving `trace_id`, `span_id`, and domain IDs. Later, the same signal
model can export through an OpenTelemetry Collector. Context propagation
is what correlates traces, logs, and metrics across the boundary.
[\[24\]](https://opentelemetry.io/docs/concepts/context-propagation/)

**Feedback loop from runtime evidence to substrate proposal**

    flowchart LR
        EL[Exception Lake Runtime] --> AG[Aggregate reviewed evidence]
        AG --> CE[Candidate extractor]
        CE --> PP[Promotion proposal package]
        PP --> HR[Human review]
        HR -->|approve| SS[Semantic Substrate]
        HR -->|reject| RA[Rejected archive]
        SS --> CM[New contract manifest]
        CM --> OR[Future runs use new meaning]

Boundary note: the loop is **evidence → aggregation → proposal → human
approval → semantic change**. The disallowed loop is **runtime evidence
→ direct semantic mutation**. That is the core non-negotiable governance
boundary.
[\[25\]](https://www.nist.gov/itl/ai-risk-management-framework)

**Future-state diagram set**

**Future-state enterprise dataflow diagram**

    flowchart LR
        subgraph Sources[Governed source systems]
            CS[Case / matter systems]
            DS[Document systems]
            BS[Billing / ops systems]
        end

        subgraph Control[Semantic control plane]
            SS[Semantic Substrate service]
            AW[Approval workflow]
            CI[Contract CI/CD]
        end

        subgraph Execution[Runtime execution plane]
            ORS[Orchestrator service]
            MR[Model router]
            MCP[MCP-compatible tool/resource layer]
            RS[Durable run store]
        end

        subgraph Evidence[Evidence plane]
            BUS[Event bus / queue]
            EL[Exception Lake Runtime]
            CG[Candidate generator]
        end

        subgraph Obs[Observability plane]
            OTL[OTel collector]
            OB[Tracing / logs / metrics backend]
        end

        CS --> ORS
        DS --> ORS
        BS --> ORS
        SS --> ORS
        SS --> EL
        ORS --> MR
        ORS --> MCP
        ORS --> RS
        ORS --> BUS
        BUS --> EL
        EL --> CG
        CG --> AW
        AW --> SS
        CI --> SS
        ORS --> OTL
        MR --> OTL
        MCP --> OTL
        EL --> OTL
        OTL --> OB

Boundary note: the long-term system scales by changing transport and
durability, not by changing the semantic chain of custody. The same
contract-manifest and evidence-packet ideas survive the move to
services, queues, durable stores, and distributed observability.
[\[26\]](https://swagger.io/specification/)

## MVP design and orchestrator repo plan

The smallest useful MVP is a **single-run, synthetic-only, fail-closed,
contract-locked classification flow** invoked from the CLI. It should
use immutable manifests, structured model output, append-only JSONL
ledgers, and optional local Exception Lake ingestion. JSON Lines is a
strong fit for the MVP ledger because it supports one-record-at-a-time
processing and works well for logs and cooperating processes, while JSON
Schema provides immediate object validation and future reuse.
[\[27\]](https://jsonlines.org/)

**MVP dataflow diagram**

    flowchart LR
        IN[examples/synthetic_exception_event.json]
        CM[contract_manifest.v1.json]
        RR[route_registry.json]
        CLI[python -m lawfirm_os_orchestrator classify-exception]
        MA[model adapter or fake stub]
        OV[output validator]
        JL[var/run_ledger.jsonl]
        EP[var/evidence_packets/<run_id>.json]
        EL[optional local Exception Lake ingest]

        IN --> CLI
        CM --> CLI
        RR --> CLI
        CLI --> MA
        MA --> OV
        OV --> JL
        OV --> EP
        EP --> EL

Boundary note: this flow is intentionally small. It proves contract
lock, fail-closed validation, evidence packaging, and observability
before any real-data connector or enterprise transport exists.

**MVP file artifacts**

    lawfirm_os_semantic_substrate/
      manifests/
        contract_manifest.v1.json
      registries/
        route_registry.v1.json
        event_class_registry.v1.json
      schemas/
        synthetic_exception_input.schema.json
        proposed_exception_event.schema.json
        validation_result.schema.json
        evidence_packet.schema.json
        run_ledger_entry.schema.json
      policies/
        runtime_policy.v1.json

    lawfirm_os_orchestrator/
      lawfirm_os_orchestrator/
        cli.py
        commands/classify_exception.py
        contracts/loader.py
        routing/resolver.py
        validation/input_validator.py
        validation/output_validator.py
        evidence/packet_builder.py
        ledger/jsonl_writer.py
        adapters/model/base.py
        adapters/model/fake_model.py
        adapters/lake/base.py
        adapters/lake/local_ingest.py
        tracing/ids.py
        tracing/jsonl_telemetry.py
      examples/
        synthetic_exception_event.json
      var/
        run_ledger.jsonl
        evidence_packets/
      tests/
        test_contract_lock.py
        test_route_validation.py
        test_model_output_validation.py
        test_evidence_packet.py
        test_synthetic_only.py

    lawfirm_os_exception_lake_runtime/
      ingest/
        local_ingest_interface.py
      storage/
        evidence/
        exception_events/
        audit/
        dead_letters/

**MVP data contracts**

| Contract                                | Purpose                                    | MVP rule                                                             |
|-----------------------------------------|--------------------------------------------|----------------------------------------------------------------------|
| `synthetic_exception_input.schema.json` | Allowed CLI input shape                    | Must require `synthetic=true`                                        |
| `route_registry.v1.json`                | Allowed route IDs and event-class bindings | Input may only resolve to registered route IDs                       |
| `proposed_exception_event.schema.json`  | Structured model output                    | No free-form route invention                                         |
| `validation_result.schema.json`         | Gate artifact                              | Every validator emits machine-readable pass/fail details             |
| `evidence_packet.schema.json`           | Main runtime transport object              | Must include manifest lock, provenance refs, IDs, validation results |
| `run_ledger_entry.schema.json`          | Append-only ledger line                    | Every step writes a structured line                                  |
| `runtime_policy.v1.json`                | MVP guardrails                             | Synthetic-only, fail-closed, no substrate writes                     |

**MVP JSON examples**

Synthetic input:

    {
      "input_id": "syn-2026-0001",
      "synthetic": true,
      "source_type": "synthetic_fixture",
      "route_hint": "exception.classify.v1",
      "confidentiality_label": "synthetic",
      "privilege_label": "none",
      "source_claim_refs": [
        {
          "claim_ref": "synthetic://document/email-001",
          "sha256": "9d8f5d2a4f2f7e3b8b8d4d70f7d0f28b4f1b8a2410c8221bf1e5b8fbe0d9d101"
        }
      ],
      "payload": {
        "summary": "Synthetic billing exception example",
        "observed_facts": [
          "time entry missing matter code",
          "supervisor approval not present"
        ]
      }
    }

Structured model output:

    {
      "proposed_exception_event": {
        "route_id": "exception.classify.v1",
        "event_class": "billing_approval_exception",
        "severity": "medium",
        "reason_codes": [
          "missing_supervisor_approval",
          "missing_matter_code"
        ],
        "supporting_claim_refs": [
          "synthetic://document/email-001"
        ]
      },
      "confidence": 0.86,
      "notes": "Synthetic example only"
    }

Evidence packet:

    {
      "evidence_id": "01969d38-0b9e-7c5f-b5fb-5e6a4a223001",
      "run_id": "01969d38-0b9e-7b8f-bb12-8b4b2a553000",
      "lineage_root_id": "01969d38-0b9e-7b8f-bb12-8b4b2a553000",
      "trace_id": "0af7651916cd43dd8448eb211c80319c",
      "correlation_id": "syn-2026-0001",
      "manifest_id": "manifest-v1",
      "manifest_hash": "sha256:0d8ad5...",
      "policy_bundle_id": "runtime-policy-v1",
      "synthetic": true,
      "route_decision": {
        "route_decision_id": "01969d38-0b9e-7d0d-8b39-d9fce1191000",
        "selected_route_id": "exception.classify.v1",
        "allowed_event_classes": [
          "billing_approval_exception",
          "billing_validation_exception"
        ]
      },
      "proposal": {
        "event_class": "billing_approval_exception",
        "severity": "medium",
        "reason_codes": [
          "missing_supervisor_approval",
          "missing_matter_code"
        ]
      },
      "validation_results": [
        {
          "validator": "route_registry_check",
          "status": "pass"
        },
        {
          "validator": "proposed_exception_event_schema",
          "status": "pass"
        }
      ],
      "source_claim_refs": [
        "synthetic://document/email-001"
      ],
      "message_history": [
        "cli_input",
        "manifest_load",
        "route_validate",
        "model_call",
        "output_validate",
        "evidence_packet_build"
      ],
      "human_review_required": true,
      "created_at": "2026-05-05T14:12:31Z"
    }

Run ledger line:

    {
      "run_id": "01969d38-0b9e-7b8f-bb12-8b4b2a553000",
      "step_index": 4,
      "step_type": "output_validate",
      "step_status": "success",
      "trace_id": "0af7651916cd43dd8448eb211c80319c",
      "span_id": "b7ad6b7169203331",
      "manifest_id": "manifest-v1",
      "correlation_id": "syn-2026-0001",
      "validation_result_id": "01969d38-0b9e-7d69-9a06-e7e7cbaf1001",
      "synthetic": true,
      "timestamp": "2026-05-05T14:12:31Z"
    }

**MVP metrics**

- `runs_started_total`
- `runs_completed_total`
- `runs_failed_total`
- `contract_lock_fail_total`
- `input_validation_fail_total`
- `output_validation_fail_total`
- `model_call_total`
- `model_output_malformed_total`
- `evidence_packet_built_total`
- `exception_lake_ingest_attempt_total`
- `exception_lake_ingest_fail_total`
- `synthetic_gate_fail_total`
- `run_duration_ms_p50/p95`

**MVP tests**

1.  Reject input if `synthetic` is missing or false.
2.  Reject input if `route_hint` does not resolve to an allowed
    `route_id`.
3.  Reject output if model invents an `event_class` outside the
    manifest.
4.  Reject output if required structured keys are missing.
5.  Record `manifest_id` and `manifest_hash` on every run.
6.  Write append-only JSONL ledger line for every step.
7.  Build evidence packet only after all validators pass.
8.  Never write to the Semantic Substrate from the Orchestrator.
9.  Ingest to Exception Lake only with valid packet and idempotency key.
10. Preserve `run_id`, `trace_id`, `correlation_id`, and `evidence_id`
    in all artifacts.

**Runtime stop conditions**

The CLI should stop the run immediately if any of the following occurs:

- manifest missing, unreadable, or hash mismatch,
- synthetic-only gate violation,
- unsupported route or event class,
- malformed structured model output,
- any required validator failure,
- any attempt to write canonical semantic data,
- any forbidden field detected in a boundary-crossing payload,
- evidence packet cannot be assembled completely.

**Recommended repo/module design for the Orchestrator**

The Orchestrator repo should be organized around **execution, not
semantics**. Its modules should make coordination and evidence explicit.

- `commands/` for CLI or service entrypoints
- `contracts/` for manifest loading, caching, and contract lock
- `routing/` for deterministic route selection and allowlist checks
- `validation/` for input, output, and policy validators
- `adapters/model/` for provider-agnostic model invocation
- `adapters/tools/` for provider-agnostic tool invocation and later MCP
- `approvals/` for human-review requests and status handling
- `ledger/` for append-only step recording
- `evidence/` for packet assembly and digesting
- `tracing/` for IDs, trace propagation, and telemetry emission
- `lake/` for Exception Lake client or event emitter

That keeps the Orchestrator from absorbing substrate authority or lake
semantics.

**Integration contracts**

Semantic Substrate integration:

| Interface          | MVP                                                   | Enterprise                                                |
|--------------------|-------------------------------------------------------|-----------------------------------------------------------|
| Contract retrieval | local file read of pinned `contract_manifest.v1.json` | read-only API, cached locally                             |
| Compatibility      | CI test + startup validation                          | CI plus runtime compatibility service                     |
| Change intake      | none from runtime                                     | governance workflow sends approved promotion to substrate |

Exception Lake integration:

| Interface        | MVP                                   | Enterprise                                                |
|------------------|---------------------------------------|-----------------------------------------------------------|
| Evidence ingest  | optional local interface or file drop | API or event bus with CloudEvents-style envelope          |
| Validation       | local schema validation before write  | orchestrator and lake both validate against pinned bundle |
| Failure handling | local dead-letter folder              | dead-letter topic / quarantine store                      |
| Idempotency      | `evidence_id` uniqueness check        | idempotent receiver with receipt record                   |

**First ten Cursor tasks**

1.  Scaffold the `lawfirm_os_orchestrator` package and
    `classify-exception` CLI entrypoint.
2.  Create `contract_manifest.v1.json` and a loader that pins
    `manifest_id` and `manifest_hash`.
3.  Create `route_registry.v1.json` and `event_class_registry.v1.json`
    in the Semantic Substrate repo.
4.  Write JSON Schemas for synthetic input, proposed exception event,
    validation result, evidence packet, and run ledger entry.
5.  Implement deterministic input validation that rejects unsupported
    `route_id` and `event_class`.
6.  Implement a provider-agnostic model adapter interface and a fake
    model stub returning structured JSON.
7.  Implement strict structured-output parsing plus fail-closed output
    validation.
8.  Implement append-only JSONL ledger writing with `run_id`,
    `trace_id`, `correlation_id`, and `manifest_id`.
9.  Implement evidence-packet assembly with source claim refs,
    validation results, and message history.
10. Add tests for contract lock, synthetic-only gating, invalid model
    output, and optional Exception Lake ingest.

## Enterprise roadmap and build order

The enterprise roadmap should change **transport, durability, and
governance tooling**, while preserving the same semantic custody chain.
The architecture becomes future-proof when manifests, IDs, evidence
packets, and approval semantics remain stable even as you move from CLI
to services, from files to queues, and from JSONL to collectors and
durable stores. [\[28\]](https://swagger.io/specification/)

| Evolution step                                        | Trigger condition                                 | Required tests                                         | Risk introduced                             | Governance control                                         | Rollback path                                   |
|-------------------------------------------------------|---------------------------------------------------|--------------------------------------------------------|---------------------------------------------|------------------------------------------------------------|-------------------------------------------------|
| CLI → local service                                   | repeated manual invocations, need for API callers | parity tests between CLI and service                   | new deployment/runtime complexity           | same contract lock in both modes                           | keep CLI as reference path                      |
| JSONL ledger → durable run store                      | investigations need indexed querying              | replay parity, append-only guarantees                  | accidental mutability, schema drift         | append-only write model, retention policy                  | continue dual-writing JSONL                     |
| File handoff → API/event queue                        | concurrency or backpressure becomes real          | exactly-once/idempotency tests, DLQ tests              | duplicate delivery, queue misconfig         | idempotent receiver, dead-letter, quotas                   | temporary synchronous API fallback              |
| Fake model → model router                             | more than one provider/model needed               | structured-output conformance tests                    | provider drift, nondeterminism              | provider allowlist, adapter contracts                      | pin back to stub or single provider             |
| Ad hoc tracing → OpenTelemetry-compatible export      | multiple processes or services                    | trace-context propagation tests                        | telemetry overhead, accidental PII in logs  | collector processors, field allowlists                     | local JSONL-only mode                           |
| Static tools → MCP-compatible layer                   | tool count grows, portability matters             | tool schema conformance and sandbox tests              | wider attack surface                        | tool allowlist, approval gates, adapter sandboxing         | keep static adapters for critical tools         |
| Manual approvals in files → approval workflow service | approval volume and SLAs increase                 | approval state-machine tests                           | workflow sprawl and auth complexity         | signed approvals, role separation                          | fall back to PR-like approval flow              |
| Single runtime → multiple runtime domains             | separate practice areas or operational domains    | cross-domain contract tests                            | semantic bleed between domains              | bounded contexts and federated governance                  | retain one shared validator bundle until stable |
| Local validation → CI + runtime validation gates      | team size and release cadence increase            | compatibility regression suite                         | false confidence from weak CI               | mandatory contract tests in merge pipeline                 | keep startup hard-stop validation               |
| Synthetic only → controlled real-data connectors      | MVP stable and governance approved                | connector redaction, claim-check, access-control tests | privilege leakage, confidentiality breaches | explicit connector approval and data minimization controls | disable connector and return to synthetic gate  |

**Do not build yet**

- A giant warehouse or lakehouse program detached from the
  control/evidence/execution split.
- A full enterprise data mesh platform.
- Fully autonomous multi-agent swarms.
- Automatic promotion from runtime evidence into substrate meaning.
- Default ingestion of full client documents into prompts.
- A universal law-firm canonical mega-model.
- A custom observability platform before you have stable fields and IDs.
- Production real-data connectors before synthetic-only MVP gates are
  passing.
- Queue-first complexity before validation and review bottlenecks
  justify it.
- Fine-grained real-time analytics dashboards for everything.

**What the first world-class dataflow should be**

The first world-class dataflow to build is the **contract-locked
exception-classification path**:

**synthetic input → pinned semantic manifest → deterministic route
allowlist check → structured model/tool execution → output validation →
append-only run ledger → evidence packet → optional Exception Lake
ingestion**

It attacks the **main bottleneck**, which is trusted human review
capacity, by ensuring that every machine-produced proposal arrives
already bounded by allowed route IDs, allowed event classes, explicit
provenance, explicit validation results, and explicit contract versions.
Reviewers no longer have to reconstruct context or guess what policy
version applied; they only have to decide whether the packet is
sufficient and whether the proposal should advance. That is the
highest-leverage throughput gain in a governed legal AI system.
[\[29\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)

It avoids creating new bottlenecks because it is deliberately **small
and selective**. It starts file-first and local, so you do not create a
queue-ops bottleneck before you need a queue. It uses claim checks, so
you do not create a payload-bloat bottleneck. It keeps the Substrate
read-only from runtime, so you do not create a semantic-mutation
bottleneck. It keeps human approval only where the risk is highest, so
you do not automate the wrong boundary. And it makes validation
mandatory before emission, so you do not create a downstream cleanup
bottleneck from low-quality event overproduction.
[\[30\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)

**Bibliography**

- AI RMF overview and implementation materials.
  [\[31\]](https://www.nist.gov/itl/ai-risk-management-framework)
- Generative AI profile for AI RMF.
  [\[32\]](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
- Privacy and data minimization guidance.
  [\[33\]](https://www.nist.gov/privacy-framework)
- Legal ethics and confidentiality guidance for lawyers using AI.
  [\[34\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)
- JSON Schema specification.
  [\[35\]](https://json-schema.org/specification)
- OpenAPI specification and initiative materials.
  [\[36\]](https://swagger.io/specification/)
- Data-contract and schema-evolution guidance.
  [\[37\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
- CloudEvents and AsyncAPI event standards.
  [\[38\]](https://cloudevents.io/)
- Semantic layer and medallion-style layered refinement references.
  [\[39\]](https://docs.getdbt.com/docs/use-dbt-semantic-layer/sl-architecture)
- Unified stream/batch execution reference.
  [\[40\]](https://beam.apache.org/get-started/beam-overview/)
- Data mesh, bounded context, and multiple canonical models.
  [\[41\]](https://martinfowler.com/articles/data-mesh-principles.html)
- OpenLineage project and facet model. [\[42\]](https://openlineage.io/)
- OpenTelemetry traces, logs, metrics, semantic conventions, and context
  propagation. [\[43\]](https://opentelemetry.io/)
- Trace Context standard. [\[44\]](https://www.w3.org/TR/trace-context/)
- Log-management and audit-log guidance.
  [\[45\]](https://csrc.nist.gov/pubs/sp/800/92/final)
- MCP architecture, overview, resources, and tools.
  [\[46\]](https://modelcontextprotocol.io/specification/2025-03-26/architecture)
- Enterprise integration patterns used in the design: canonical data
  model, claim check, message history, correlation identifier,
  idempotent receiver, dead-letter channel, pipes-and-filters.
  [\[47\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html)
- Event-sourcing references used to scope append-only runtime evidence
  without event-sourcing the whole system.
  [\[48\]](https://martinfowler.com/eaaDev/EventSourcing.html)

[\[1\]](https://www.nist.gov/itl/ai-risk-management-framework)
[\[6\]](https://www.nist.gov/itl/ai-risk-management-framework)
[\[17\]](https://www.nist.gov/itl/ai-risk-management-framework)
[\[23\]](https://www.nist.gov/itl/ai-risk-management-framework)
[\[25\]](https://www.nist.gov/itl/ai-risk-management-framework)
[\[31\]](https://www.nist.gov/itl/ai-risk-management-framework)
https://www.nist.gov/itl/ai-risk-management-framework

<https://www.nist.gov/itl/ai-risk-management-framework>

[\[2\]](https://docs.getdbt.com/docs/use-dbt-semantic-layer/sl-architecture)
[\[39\]](https://docs.getdbt.com/docs/use-dbt-semantic-layer/sl-architecture)
https://docs.getdbt.com/docs/use-dbt-semantic-layer/sl-architecture

<https://docs.getdbt.com/docs/use-dbt-semantic-layer/sl-architecture>

[\[3\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)
[\[11\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)
[\[13\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)
[\[29\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)
[\[34\]](https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/)
https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/

<https://www.americanbar.org/news/abanews/aba-news-archives/2024/07/aba-issues-first-ethics-guidance-ai-tools/>

[\[4\]](https://swagger.io/specification/)
[\[26\]](https://swagger.io/specification/)
[\[28\]](https://swagger.io/specification/)
[\[36\]](https://swagger.io/specification/)
https://swagger.io/specification/

<https://swagger.io/specification/>

[\[5\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
[\[10\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
[\[12\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
[\[19\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
[\[22\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
[\[37\]](https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html)
https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html

<https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html>

[\[7\]](https://martinfowler.com/bliki/MultipleCanonicalModels.html)
[\[18\]](https://martinfowler.com/bliki/MultipleCanonicalModels.html)
https://martinfowler.com/bliki/MultipleCanonicalModels.html

<https://martinfowler.com/bliki/MultipleCanonicalModels.html>

[\[8\]](https://json-schema.org/specification)
[\[35\]](https://json-schema.org/specification)
https://json-schema.org/specification

<https://json-schema.org/specification>

[\[9\]](https://opentelemetry.io/docs/concepts/context-propagation/)
[\[24\]](https://opentelemetry.io/docs/concepts/context-propagation/)
https://opentelemetry.io/docs/concepts/context-propagation/

<https://opentelemetry.io/docs/concepts/context-propagation/>

[\[14\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)
[\[21\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)
[\[30\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)
https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html

<https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html>

[\[15\]](https://opentelemetry.io/docs/concepts/signals/metrics/)
https://opentelemetry.io/docs/concepts/signals/metrics/

<https://opentelemetry.io/docs/concepts/signals/metrics/>

[\[16\]](https://openlineage.io/docs/spec/facets/run-facets/)
https://openlineage.io/docs/spec/facets/run-facets/

<https://openlineage.io/docs/spec/facets/run-facets/>

[\[20\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)
https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html

<https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html>

[\[27\]](https://jsonlines.org/) https://jsonlines.org/

<https://jsonlines.org/>

[\[32\]](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

<https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence>

[\[33\]](https://www.nist.gov/privacy-framework)
https://www.nist.gov/privacy-framework

<https://www.nist.gov/privacy-framework>

[\[38\]](https://cloudevents.io/) https://cloudevents.io/

<https://cloudevents.io/>

[\[40\]](https://beam.apache.org/get-started/beam-overview/)
https://beam.apache.org/get-started/beam-overview/

<https://beam.apache.org/get-started/beam-overview/>

[\[41\]](https://martinfowler.com/articles/data-mesh-principles.html)
https://martinfowler.com/articles/data-mesh-principles.html

<https://martinfowler.com/articles/data-mesh-principles.html>

[\[42\]](https://openlineage.io/) https://openlineage.io/

<https://openlineage.io/>

[\[43\]](https://opentelemetry.io/) https://opentelemetry.io/

<https://opentelemetry.io/>

[\[44\]](https://www.w3.org/TR/trace-context/)
https://www.w3.org/TR/trace-context/

<https://www.w3.org/TR/trace-context/>

[\[45\]](https://csrc.nist.gov/pubs/sp/800/92/final)
https://csrc.nist.gov/pubs/sp/800/92/final

<https://csrc.nist.gov/pubs/sp/800/92/final>

[\[46\]](https://modelcontextprotocol.io/specification/2025-03-26/architecture)
https://modelcontextprotocol.io/specification/2025-03-26/architecture

<https://modelcontextprotocol.io/specification/2025-03-26/architecture>

[\[47\]](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html)
https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html

<https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html>

[\[48\]](https://martinfowler.com/eaaDev/EventSourcing.html)
https://martinfowler.com/eaaDev/EventSourcing.html

<https://martinfowler.com/eaaDev/EventSourcing.html>
