# Clean Export of the Idea Featured in This Chat

## LawFirm OS Orchestrator: third leg, execution architect, governed self-learning system

This export is designed to be pasted into a new chat, used as a Codex/Cursor seed, or copied into a new `LawFirm-os-orchestrator` repository. It preserves the core idea from the conversation: build a world-class orchestration layer for LawFirm OS that interacts safely with the Semantic Substrate and Exceptions Lake, learns continuously from runtime evidence, and also monitors high-signal external research such as frontier math, algorithmic discoveries, AI systems research, evaluation methods, and governance breakthroughs.

---

## 1. Core thesis

The LawFirm OS Orchestrator should be the **third leg** of the LawFirm OS architecture:

```text
Semantic Substrate  = authority / control plane
Orchestrator        = execution / coordination plane
Exceptions Lake     = evidence / audit / learning plane
```

The Orchestrator should act as the **master architect for execution**, not as the owner of semantic truth. It coordinates model calls, tools, policy gates, approvals, run state, ledgers, evidence packets, evals, learning loops, and engineering guidance. It must not invent canonical route IDs, event classes, schemas, governance doctrine, or promotion decisions.

The world-class version is not a giant agent swarm. It is a **contract-locked execution kernel and evidence-packet factory** that can later grow into a durable orchestration service.

The first durable unit is:

```text
contract-locked evidence packet + append-only run ledger
```

The first executable command is:

```bash
python -m lawfirm_os_orchestrator classify-exception \
  --input examples/synthetic_exception_event.json \
  --contract-pin ../LawFirm-os-semantic-substrate/manifests/contract_manifest.v1.json \
  --ledger-dir .lawfirm-os-orchestrator/ledger \
  --packet-out .lawfirm-os-orchestrator/runs \
  --exception-lake-mode disabled
```

The first throughput metric is:

```text
accepted, contract-locked proposed exception packets per reviewer hour
```

---

## 2. Repository role split

| Repository | Owns | Must not own |
|---|---|---|
| **LawFirm-os-semantic-substrate** | Canonical meaning, schemas, registries, route IDs, event classes, policy bundles, validation contracts, approval doctrine, promotion authority | Runtime execution state, model session state, ad hoc semantic rewrites |
| **LawFirm-os-orchestrator** | Run execution, model/tool routing, policy gates, approval pauses, budgets, evidence packet assembly, JSONL ledgers, evals, learning-loop proposals, engineering guidance | Canonical schemas, route/event-class invention, lifecycle-state authority, substrate mutation, promotion authority |
| **LawFirm-os-exceptions-lake-runtime** | Append-only exception events, audit records, validation outcomes, evidence records, pressure vectors, learning candidates | Canonical semantics, ontology mutation, automatic promotion |

The Orchestrator can propose. The Exceptions Lake can accumulate evidence. The Semantic Substrate can promote only after governance approval.

---

## 3. What the Orchestrator should be

Build the Orchestrator as a **local-first, deterministic Python orchestration kernel** with provider and runtime adapters.

MVP shape:

```text
synthetic input
→ pinned Semantic Substrate manifest
→ deterministic route/event-class allowlist check
→ one bounded structured classifier call or mock classifier
→ schema + policy validation
→ append-only JSONL run ledger
→ contract-locked evidence packet
→ optional Exceptions Lake dry-run / runtime-safe handoff
```

The kernel should be framework-independent at the domain layer. It may later use OpenAI Agents SDK, LangGraph, MCP, or Temporal behind adapters, but those frameworks must not become the business state, legal audit record, or semantic authority.

Recommended posture:

```text
Start: deterministic Python CLI + strict Pydantic contracts + JSONL ledger + evidence packet directory.
Then: optional OpenAI structured-output / Agents SDK adapter.
Later: LangGraph for checkpointed graphs if branching/interrupt pressure appears.
Later: Temporal if long-running, outage-resilient workflows become required.
Always: MCP-compatible tool/resource contracts, but MCP is a protocol, not the orchestrator.
```

---

## 4. How it interacts with the Exceptions Lake

The Orchestrator should interact with the Exceptions Lake only through approved, typed, fail-closed clients.

### 4.1 Lake client modes

```text
DisabledLakeClient       = default; no Lake writes.
DryRunLakeClient         = writes local request/receipt artifacts only.
RuntimeSafeLakeClient    = calls one approved runtime-safe ingestion function.
```

MVP default:

```bash
--exception-lake-mode disabled
```

Later safe modes:

```bash
--exception-lake-mode dry-run
--exception-lake-mode runtime-safe
```

Commit-like ingestion requires both:

```text
1. config allow switch
2. explicit CLI flag
```

No hidden writes. No autonomous writes. No direct filesystem/database bypass into the Lake.

### 4.2 What gets sent to the Lake

The Orchestrator should send only validated, minimal, schema-bound objects:

```text
proposed exception event
contract pin and manifest hash
route decision
candidate event class
validation results
policy gate results
approval state
trace_id / span_id / correlation_id
source claim refs and artifact hashes
idempotency key
packet hash
ledger refs
```

The Lake should independently validate and either accept, reject, or dry-run the handoff. The Orchestrator must store the Lake receipt or rejection reason inside the evidence packet and ledger.

### 4.3 Current practical write contract

For the MVP, use only surfaces that the runtime already supports or that are explicitly approved by the runtime team. The intended shape is:

```text
health/readiness check
build_synthetic_envelope(payload, actor)
ingest_synthetic_event(envelope, config)
build_non_synthetic_preflight_envelope(readiness_request, actor)
run_non_synthetic_preflight(envelope, config)
build_pressure_candidate(config)
```

If richer surfaces such as these do not yet exist, do **not** invent them as canon inside the Orchestrator:

```text
append_evidence_packet(...)
append_tool_call_trace(...)
append_human_approval_record(...)
submit_pressure_vector_candidate(...)
```

Instead:

```text
assemble now locally → persist later only after substrate schema + runtime adoption
```

### 4.4 What the Lake returns

The Lake returns evidence and learning signals, not semantic truth:

```text
validation_result
policy_result
machine-readable rejection reason
accepted event ref
audit record ref
pressure-vector candidate
learning candidate
aggregate defect signal
```

The Orchestrator consumes those signals to improve prompts, validators, routing rules, approval thresholds, and evals — but not to directly mutate the Semantic Substrate.

---

## 5. Self-learning architecture

The Orchestrator should be self-learning, but in a governed way.

Do **not** implement:

```text
runtime evidence → automatic code rewrite → production deployment
```

Implement:

```text
runtime evidence
→ defect classification
→ pressure vector
→ upgrade hypothesis
→ shadow eval / replay
→ proposal
→ human or promotion approval
→ versioned implementation
→ measured result
```

This means the system becomes increasingly intelligent without becoming chaotic or unsafe.

### 5.1 Five learning loops

#### Loop 1 — Run-level learning

Every run writes:

```text
input
contract pin
route candidates
model response
validation result
policy gate result
evidence completeness
human review status
reviewer corrections
Lake receipt/rejection
```

Reviewer corrections and Lake rejection reasons become labeled training/eval data.

#### Loop 2 — Pressure-vector learning

The Exceptions Lake aggregates repeated defects:

```text
wrong route_id
wrong event_class
missing evidence
stale contract pin
false confidence
approval bypass attempt
schema failure
Lake rejection reason
```

Then it emits pressure vectors:

```text
affected surface
cohort
recurrence
impact
detectability
candidate causes
smallest plausible intervention
supporting evidence refs
```

The Orchestrator converts pressure vectors into proposed changes, not direct changes.

#### Loop 3 — Eval learning

The Orchestrator maintains fixture and gold-label evals:

```text
evals/fixtures.jsonl
evals/gold_labels.jsonl
evals/graders.py
scripts/run_evals.py
```

Metrics:

```text
route_exact_match_rate
event_class_exact_match_rate
first_pass_validation_rate
evidence_completeness_score
stale_pin_count
unknown_enum_count
model_calls_per_run
cost_per_accepted_packet
high_confidence_error_rate
reviewer_edits_per_packet
```

A proposed change must improve the relevant metric without causing CTQ regressions.

#### Loop 4 — Governance/promotion learning

Some findings are Orchestrator issues:

```text
prompt patch
validator patch
router threshold
approval threshold
evidence template
model adapter behavior
eval suite expansion
```

Other findings are Semantic Substrate issues:

```text
missing route ID
ambiguous event class
schema gap
policy ambiguity
governance boundary gap
```

For substrate issues, the Orchestrator opens a governed semantic-change request. It does not mutate canon.

#### Loop 5 — External Discovery Learning / Research Radar

This is a key feature.

The Orchestrator should continuously monitor high-signal external discoveries:

```text
frontier math results
new algorithmic techniques
AI reasoning/search/proof methods
eval methods
model-routing methods
agent safety methods
retrieval/grounding improvements
formal verification methods
optimization techniques
legal-tech governance patterns
security/privacy standards
```

The loop is:

```text
new discovery
→ DiscoverySignal
→ credibility assessment
→ relevance assessment
→ evidence packet
→ UpgradeHypothesis
→ ExperimentPlan
→ ShadowEvalResult
→ UpgradeProposal
→ approval
→ versioned implementation
→ measured effect
```

The Orchestrator should treat frontier research as **method evidence**, not authority.

It can learn better ways to:

```text
search
verify
route
calibrate confidence
structure evals
optimize prompts
build validators
rank evidence
reduce reviewer burden
prevent prompt injection
sandbox tools
plan decompositions
```

It must not directly rewrite itself from a paper, blog, benchmark, or model suggestion.

---

## 6. Research Radar feature

### 6.1 Command shape

Future commands:

```bash
python -m lawfirm_os_orchestrator research-radar scan \
  --sources config/research_sources.yaml \
  --since 2026-05-01 \
  --out .lawfirm-os-orchestrator/research/signals.jsonl \
  --lake-mode dry-run
```

```bash
python -m lawfirm_os_orchestrator research-radar propose-upgrades \
  --signals .lawfirm-os-orchestrator/research/signals.jsonl \
  --current-bottleneck review_rework \
  --eval-suite evals/classify_exception_gold.jsonl \
  --out .lawfirm-os-orchestrator/research/upgrade_proposals
```

```bash
python -m lawfirm_os_orchestrator research-radar run-shadow-evals \
  --proposal .lawfirm-os-orchestrator/research/upgrade_proposals/<id>.json \
  --eval-suite evals/classify_exception_gold.jsonl
```

### 6.2 Source tiers

```yaml
sources:
  - id: arxiv_math
    kind: arxiv
    authority_tier: 1
    categories: ["math", "cs.AI", "cs.LG", "cs.DS", "cs.CR"]
    allowed: true

  - id: benchmark_frontier_math
    kind: benchmark
    authority_tier: 1
    allowed: true

  - id: official_lab_blogs
    kind: lab_blog
    authority_tier: 1
    allowed: true

  - id: standards_bodies
    kind: standards
    authority_tier: 1
    allowed: true

  - id: github_repos
    kind: repository
    authority_tier: 3
    allowed: true

  - id: social_posts
    kind: social
    authority_tier: 4
    allowed: false
```

### 6.3 Discovery signal schema

```json
{
  "schema_version": "1.0",
  "signal_type": "external_research_discovery",
  "source_kind": "paper",
  "source_uri": "https://example.org/paper",
  "title": "Example discovery",
  "published_at": "2026-05-01",
  "claims": [
    {
      "claim": "Automated evaluators can guide search over candidate algorithms.",
      "claim_type": "algorithmic_pattern",
      "evidence_strength": "medium_high"
    }
  ],
  "relevance": {
    "orchestrator_surfaces": ["evals", "model_router", "experiment_planner"],
    "possible_upgrade": "Add evaluator-optimizer shadow loop for prompt and validator improvements.",
    "risk": "Do not allow autonomous code mutation."
  },
  "recommended_action": "create_shadow_experiment"
}
```

### 6.4 Upgrade priority scoring

Use a reviewable formula:

```text
upgrade_priority =
  credibility
  × relevance
  × expected_lift
  × verifiability
  ÷ risk
  ÷ implementation_cost
```

Every score must be backed by evidence and must identify the target metric.

### 6.5 Approved upgrade surfaces

External discovery may propose upgrades to:

```text
prompt templates
structured output schemas
eval fixtures
graders
validation rules
model routing
confidence calibration
approval thresholds
evidence packet templates
retrieval/ranking strategy
tool sandboxing
observability fields
```

External discovery must not automatically modify:

```text
canonical route IDs
event classes
schemas in the Semantic Substrate
approval doctrine
production connectors
real client data handling
write permissions
protected workflow transitions
```

---

## 7. Evidence packet design

Evidence packets are the main cross-boundary runtime unit.

Directory shape:

```text
.lawfirm-os-orchestrator/runs/<run_id>/evidence/
├── manifest.json
├── input_event.json
├── policy_gate.json
├── substrate_snapshot.json
├── model_request.json
├── model_response.json
├── classification_result.json
├── validation_results.json
├── ledger_refs.json
├── stdout_summary.json
├── ingest_request.json      # optional
└── ingest_receipt.json      # optional
```

For research radar runs:

```text
.lawfirm-os-orchestrator/research/<discovery_id>/evidence/
├── manifest.json
├── source_record.json
├── credibility_assessment.json
├── relevance_assessment.json
├── extracted_claims.json
├── upgrade_hypothesis.json
├── experiment_plan.json
├── shadow_eval_result.json  # optional until tested
└── promotion_decision_ref.json # optional after approval
```

`manifest.json` must hash every file.

---

## 8. Minimum run ledger fields

Every run should write append-only JSONL records.

Minimum fields:

```text
run_id
lineage_root_id
trace_id
span_id
correlation_id
manifest_id
manifest_hash
policy_bundle_id
environment
command_name
step_type
step_status
selected_route_id
event_class_proposed
validation_result_id
evidence_id
synthetic
started_at
ended_at
duration_ms
retry_count
error_code
error_message_redacted
source_claim_refs
output_claim_refs
message_history
```

Lake handoff fields:

```text
lake_mode
handoff_attempted
idempotency_key
lake_receipt_id
lake_acceptance_status
lake_rejection_reasons
lake_audit_ref
lake_event_ref
```

Learning-loop fields:

```text
reviewer_edits
final_label_route_id
final_label_event_class
defect_tags
pressure_vector_ref
upgrade_proposal_ref
shadow_eval_result_ref
promotion_decision_ref
```

---

## 9. MVP repository structure

```text
LawFirm-os-orchestrator/
├── README.md
├── AGENTS.md
├── AI_WORK_START_HERE.md
├── ARCHITECTURE_ROLE.md
├── MVP_BOUNDARY.md
├── FUTURE_EXPANSION_BOUNDARY.md
├── HUMAN_APPROVAL_MATRIX.md
├── EXCEPTION_LAKE_INTEGRATION.md
├── SEMANTIC_SUBSTRATE_CONSUMPTION.md
├── SELF_LEARNING_AND_RESEARCH_RADAR.md
├── FAILURE_MODES.md
├── contracts.lock.json
├── pyproject.toml
├── .cursor/
│   └── rules/
│       ├── 000-core-boundaries.mdc
│       ├── 010-cursor-workflow.mdc
│       ├── 020-python-package.mdc
│       ├── 030-contracts-and-validation.mdc
│       ├── 040-substrate-boundary.mdc
│       ├── 050-exception-lake-boundary.mdc
│       ├── 060-testing-and-evals.mdc
│       ├── 070-do-not-build-yet.mdc
│       └── 080-self-learning-and-research-radar.mdc
├── config/
│   └── research_sources.yaml
├── docs/
│   ├── architecture.md
│   ├── contracts.md
│   ├── decisions/
│   │   ├── 0001-local-first-kernel.md
│   │   ├── 0002-read-only-substrate.md
│   │   ├── 0003-exception-lake-validate-only.md
│   │   ├── 0004-jsonl-ledger-first.md
│   │   ├── 0005-frameworks-as-adapters.md
│   │   └── 0006-external-discovery-loop.md
│   └── ai-workflow/
│       ├── orchestrator-route-table.yaml
│       ├── orchestrator-stop-conditions.md
│       ├── tool-authority-table.yaml
│       ├── approval-routing.md
│       └── evidence-packet-policy.md
├── src/
│   └── lawfirm_os_orchestrator/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── commands/
│       │   ├── classify_exception.py
│       │   └── research_radar.py
│       ├── domain/
│       ├── contracts/
│       ├── substrate/
│       ├── policy/
│       ├── routing/
│       ├── validation/
│       ├── model_router/
│       ├── ledger/
│       ├── evidence/
│       ├── lake/
│       ├── approvals/
│       ├── discovery/
│       ├── evals/
│       ├── tracing/
│       └── util/
├── schemas/
├── examples/
├── evals/
├── tests/
├── scripts/
└── prompts/
```

---

## 10. Cursor/Codex execution model

Cursor/Codex should implement one PR-sized task at a time.

GPT-5.5 Pro, or the lead architect, should own:

```text
architecture decisions
ADR drafting
boundary interpretation
PR task decomposition
acceptance criteria
stop-condition design
schema review
test-plan design
risk review
prompt/rule tightening
roadmap sequencing
```

Cursor/Codex should own:

```text
file edits
local implementation
tests
fixtures
CLI smoke tests
small refactors inside allowed paths
```

Cursor/Codex must not own:

```text
semantic authority decisions
route/event-class invention
scope expansion
framework adoption decisions
production connector decisions
real-data policy decisions
schema promotion decisions
```

Every task must begin with:

```text
Route:
Mode:
Allowed paths:
Forbidden paths:
Contract surfaces touched:
Validation plan:
Stop conditions:
Expected artifacts:
```

---

## 11. First ten PRs

| PR | Name | Deliverable | Main tests |
|---:|---|---|---|
| 0 | Preseed governance | `AGENTS.md`, `AI_WORK_START_HERE.md`, `.cursor/rules`, route table | docs and route table exist |
| 1 | Package scaffold | Python package, CLI stub, help output | CLI smoke tests |
| 2 | Domain contracts | Strict Pydantic models | extra-field and missing-field failures |
| 3 | Substrate fixtures | local manifest, routes, event classes | contract-lock and read-only tests |
| 4 | Policy gate | synthetic-only and pre/post gates | real-data and unknown-ID rejection |
| 5 | Mock classifier | deterministic adapter and schema factory | output validation tests |
| 6 | Ledger | JSONL append-only run events | ledger completeness tests |
| 7 | Evidence packet | packet directory and manifest hashes | packet completeness/hash tests |
| 8 | Lake clients | disabled, dry-run, runtime-safe shell | dual opt-in and no-write tests |
| 9 | End-to-end classify | full CLI run from input to packet | integration test |
| 10 | Eval harness | fixtures, gold labels, graders | eval command and metric output |
| 11 | Learning loop | defect tags, pressure-vector intake, proposal objects | learning object tests |
| 12 | Research Radar | discovery contracts, source registry, scan/propose commands | discovery schema and shadow-eval tests |

---

## 12. Phase plan

### Days 1–30 — prove the kernel

Build:

```text
preseed docs and Cursor rules
CLI package
strict contracts
read-only substrate adapter
mock classifier
policy gate
JSONL ledger
evidence packet builder
disabled/dry-run Lake clients
integration tests
```

Exit criterion:

```bash
python -m lawfirm_os_orchestrator classify-exception --input examples/synthetic_exception_event.json
```

produces:

```text
stdout summary
append-only ledger records
evidence packet directory
manifest hashes
validation results
no substrate writes
no Lake commit by default
```

### Days 31–60 — improve reviewer utility

Build:

```text
richer evidence templates
confidence thresholds
reviewer-note field
abstain path
duplicate/idempotency checks
eval fixtures and gold labels
optional OpenAI structured-output adapter
trace/eval report
```

Exit criterion:

```text
route/event exact-match measured
first-pass validation rate measured
evidence completeness measured
high-confidence error rate measured
```

### Days 61–90 — harden migration seams and learning loops

Build:

```text
OpenTelemetry-compatible JSONL field names
approval request / approval decision schema
optional resume-state abstraction
pressure-vector intake
upgrade proposal objects
external discovery contracts
research radar dry-run mode
shadow eval runner
optional Agents SDK adapter spike
optional LangGraph mapping spike
runtime-safe Lake adapter if safe callable is stable
```

Exit criterion:

```text
same domain contracts survive CLI, mock model, provider model, Lake dry-run, and research-radar dry-run
no framework owns business state
no vendor trace is legal system of record
no research signal can auto-promote a change
```

---

## 13. Do not build yet

Do not build:

```text
web dashboard
background worker
event bus
production connectors
real client data ingestion
broad RAG/vector DB
multi-agent planner/executor swarm
autonomous write tools
substrate mutation tools
workflow engine
analytics warehouse
rich human approval UI
automatic research-to-code mutation
automatic promotion from Lake evidence into canon
```

These are future bottleneck-elevation items only.

---

## 14. Final design statement

Build `LawFirm-os-orchestrator` as:

> A local-first, contract-locked, evidence-packet factory and execution kernel that coordinates LawFirm OS workflows, learns from Exceptions Lake evidence, monitors external frontier research, proposes safe upgrades, and remains subordinate to the Semantic Substrate and downstream of Exceptions Lake validation.

Its highest leverage is not “more agency.” Its highest leverage is:

```text
less reviewer rework
more complete evidence
zero semantic drift
safe self-improvement proposals
faster governed decisions
```

The self-learning principle is:

```text
self-observe → self-diagnose → self-propose → shadow-test → seek approval → versioned improvement
```

Not:

```text
self-rewrite → self-promote → hope it worked
```
