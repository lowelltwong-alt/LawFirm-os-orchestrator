# Architecture Contract for LawFirm-os-orchestrator

## Research baseline

The strongest public evidence today is uneven across the two existing
repositories. The public repository for LawFirm-os-semantic-substrate
exists on
GitHub[\[1\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability),
but it is currently empty. By contrast,
LawFirm-os-exceptions-lake-runtime is a concrete, library-first,
non-production runtime that already documents its boundaries, its
contract-loading behavior, and its current ingestion/validation flow.
That means the safest design for LawFirm-os-orchestrator is to treat the
semantic substrate as the intended long-term authority layer, but to
derive the actual initial contract shape from the public Exception Lake
runtime code and docs that already exist.
[\[2\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)

The runtime’s current posture is very explicit. It consumes pinned
contracts from an authoritative “Law Firm ontology” contract repository,
prefers a manifest-first export when available, falls back to specific
registries and schemas if the export manifest is absent, validates a
strict `contracts.lock.json`, rejects contract drift, validates route
authority against the canonical route registry, denies unsupported
ingestion modes, and forbids canon mutation. It also states that HTTP is
intentionally out of scope for the current implementation, so the
current surface is a Python library and CLI rather than a network
service. I therefore infer that the future semantic substrate must
occupy the “Law Firm ontology” role referenced throughout the runtime,
and that the orchestrator should initially integrate against that same
pinned-contract, fail-closed model instead of inventing a new authority
path.
[\[3\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)

## Recommended role split

The split below is the cleanest way to preserve source-of-truth
authority in the substrate, evidence authority in Exception Lake
runtime, and execution authority in the orchestrator. That
recommendation follows directly from the current public runtime
boundaries, validation rules, policy gateway, and contract loader
behavior.
[\[4\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)

| Repository                             | Should own                                                                                                                                                                                                        | Should never own                                                                                                                                                                 |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **LawFirm-os-semantic-substrate**      | Canonical semantic meaning; schemas; registries; route authority; governance boundaries; validation contracts; authoritative handoff surfaces; approval doctrine                                                  | Runtime observation handling; model execution policy; agent session state; ad hoc semantic rewrites driven by runtime convenience                                                |
| **LawFirm-os-exceptions-lake-runtime** | Pinned contract consumption; fail-closed validation; policy gate for allowed ingestion modes; append-only event records; append-only audit records; candidate pressure-vector derivation                          | Canonical semantics; ontology mutation; automatic adaptation proposals as canon; production data admission without later approved boundary changes                               |
| **LawFirm-os-orchestrator**            | Workflow execution; model/tool routing; bounded tool invocation; run state and checkpoints; approval pauses; evidence packet assembly; Exception Lake invocation; retry/time/cost budgets; evaluations and traces | Canonical schemas; canonical `route_id`; canonical `event_class`; lifecycle states; mutation authority; promotion authority; schema registry ownership; route registry ownership |

### What the orchestrator should own

The orchestrator should own **execution mechanics**, not **semantic
truth**. In practice, that means it should own run planning, specialist
selection, tool invocation, model selection, state/checkpointing, retry
and timeout budgets, evidence-packet assembly, and calls into Exception
Lake runtime. That is also the direction recommended by current
orchestration guidance from
OpenAI[\[5\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
and
Anthropic[\[6\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py):
keep orchestration in application code, start with one focused manager,
and add specialists only when capability isolation or policy isolation
materially improves the system.
[\[7\]](https://developers.openai.com/api/docs/guides/agents)

Concretely, the orchestrator should own these responsibilities:

- **Run governance at execution time**: task intake, model choice, tool
  choice, loop control, step limits, retry limits, and cost/latency
  budgets.
  [\[8\]](https://developers.openai.com/api/docs/guides/agents/running-agents)
- **Bounded tool execution** from a whitelist registry, with tools that
  are few, distinct, and namespaced so the agent is not overloaded by
  overlapping capabilities.
  [\[9\]](https://www.anthropic.com/engineering/writing-tools-for-agents)
- **Evidence-packet assembly** for each run, using hashes, tool
  references, trace IDs, route labels, contract SHA, and event-store
  references rather than raw privileged content. The Exception Lake
  runtime’s own audit-planning docs already point toward this shape.
  [\[10\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md)
- **Human approval pauses and resume flow**, because guardrails and
  approval are part of runtime orchestration, not semantic authority.
  Durable paused state is an execution concern.
  [\[11\]](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- **Exception Lake integration**, including envelope construction and
  submission through the current Python facade/CLI surfaces.
  [\[12\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- **Evaluation and observability**, including traces, trace grading, and
  policy-regression detection on orchestrator changes.
  [\[13\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)

### What the orchestrator must never own

The orchestrator must never become a shadow semantic authority. The
runtime boundary docs are already explicit that the contract repo
remains authoritative for schema meaning, lifecycle states, mutation
authority, promotion authority, registries, validators, and governed
boundary doctrine; the runtime may only consume and validate. The
orchestrator should inherit exactly that humility.
[\[14\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)

It must therefore never own these responsibilities:

- **Canonical semantic definitions**, including schemas, schema meaning,
  route registries, lifecycle states, and governance doctrine.
  [\[14\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
- **Canonical route or event vocabularies**, including invention or
  reinterpretation of `route_id` and `event_class` values. The runtime
  already rejects unknown values and mismatches against the route
  registry.
  [\[15\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/validation_gateway.py)
- **Direct canon mutation**, including adaptation proposal promotion,
  policy overwrite, taxonomy rewrite, schema mutation, or address-system
  mutation.
  [\[16\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/CANONICAL_ROUTE_MAPPING.md)
- **Production-data admission authority**. The current runtime only
  allows `synthetic_test_only` and metadata-only
  `non_synthetic_dry_run_preflight`, with all data flags false.
  [\[17\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/policy_gateway.py)
- **Raw transcript retention in Exception Lake surfaces**. Current
  runtime docs explicitly forbid storing production conversation text or
  sealed transcript contents there; only hashes, metadata, and pointers
  fit the present boundary.
  [\[18\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-transcript-retention-boundary.md)
- **Dynamic spawning of uncontrolled subagents**. Current multi-agent
  guidance is to keep one stable owner and add specialists only when the
  contract really changes.
  [\[19\]](https://developers.openai.com/api/docs/guides/agents/orchestration)

## Contracted dataflow

The orchestrator should sit **between** contract authority and evidence
persistence, never above either one.

**Text dataflow diagram**

Task or workflow request  
→ Orchestrator intake  
→ Load pinned semantic-substrate manifest, registries, schemas, and
boundary docs  
→ Apply risk/policy classification and stop conditions  
→ Manager agent executes with bounded tools and step budgets  
→ If action is high-risk or semantically ambiguous, pause for human
approval  
→ Build either a canonical exception-event envelope or a metadata-only
dry-run readiness envelope  
→ Call Exception Lake runtime  
→ Runtime applies deny-by-default mode policy and fail-closed
schema/route validation  
→ Runtime appends audit record and, when valid, appends exception event
record  
→ Runtime may derive a pressure-vector candidate  
→ Orchestrator emits evidence packet, trace pointer, and candidate
artifacts for review only.
[\[20\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)

### What the orchestrator should read from the semantic substrate

The **minimum existing public contract set** is whatever the current
runtime already expects from the authoritative contract repo:

- `registry/exceptions-lake-contract-export.json` when present, as the
  preferred manifest-first export.
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `registry/schema-registry.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `registry/exceptions-schema-registry.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `registry/governed-learning-schema-registry.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `registry/exception-route-registry.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `schemas/exception-event.schema.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `schemas/pressure-vector.schema.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `schemas/adaptation-proposal.schema.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `schemas/promotion-decision.schema.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `schemas/source-ingestion-manifest.schema.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `schemas/access-decision.schema.json`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `governance/EXCEPTIONS_LAKE_BOUNDARY.md`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- `governance/AI_CONTROL_PLANE_BOUNDARY.md`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- A strict pinned SHA through the orchestrator’s own
  `contracts.lock.json`, matching the runtime’s lock discipline.
  [\[22\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)

Those are the **high-confidence, already evidenced** contract surfaces.
Because the semantic substrate repo is currently empty in public, the
orchestrator should not assume any richer substrate contract until it is
actually published.
[\[23\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)

The **recommended future substrate additions** for orchestrator-specific
governance are:

- `registry/orchestrator-contract-export.json`
- `registry/model-policy-registry.json`
- `registry/tool-authority-registry.json`
- `registry/human-approval-registry.json`
- `schemas/evidence-packet.schema.json`
- `schemas/tool-call-trace.schema.json`
- `schemas/human-approval-record.schema.json`
- `schemas/orchestrator-run-record.schema.json`
- `governance/ORCHESTRATOR_BOUNDARY.md`

These should live in the semantic substrate, not in the orchestrator,
because policy and contract meaning should version and travel with the
authority layer rather than be reinvented in each caller. That direction
is consistent with governed-agent guidance that recommends
policies-as-code, centralized policy packaging, and organization-wide
guardrail distribution.
[\[24\]](https://developers.openai.com/cookbook/examples/partners/agentic_governance_guide/agentic_governance_cookbook)

### What the orchestrator should write to Exception Lake

For the **MVP**, the orchestrator should write **only through existing
Exception Lake runtime surfaces**, not around them. Today, those are the
Python facade functions and corresponding CLI commands for health,
synthetic ingest, non-synthetic dry-run preflight, event listing, and
pressure candidate generation.
[\[25\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)

That means the orchestrator should write these artifact types:

- **Validated exception-event envelopes**, submitted via
  `ingest_synthetic_event(envelope, config)`. The runtime then applies
  policy and validation before append-only persistence.
  [\[26\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- **Metadata-only non-synthetic readiness envelopes**, submitted via
  `run_non_synthetic_preflight(envelope, config)`, for audit-only dry
  runs with no event persistence.
  [\[27\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- **Audit metadata**, via the runtime’s append-only audit log, with
  action/result/actor/contract-version/details fields.
  [\[28\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py)

The runtime’s actual persisted event record today contains:
`record_type`, `event_id`, `received_at`, `contract_version`,
`schema_id`, `validation_result`, `policy_result`, and the canonical
`payload`. The actual audit record contains: `timestamp`, `action`,
`result`, `event_id`, `actor`, `contract_version`, and `details`. The
orchestrator should treat those as the **current write contract**.
[\[29\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py)

For richer evidence packets, the right rule is: **assemble now, persist
later when the substrate publishes a schema and the runtime accepts
it**. The runtime’s audit-policy docs already suggest what such an
envelope should carry—`audit_event_id`, runtime route, mode, contract
SHA, schema version, content hashes, policy decision, tool references,
event-store reference, retention class, legal-hold status, and
hash-linkage—but they also say canonical audit contracts belong in the
authority repo.
[\[30\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md)

### What the orchestrator should emit only as proposed evidence or candidates

Anything beyond a validated exception event should remain
**non-canonical** until the semantic substrate and governance path say
otherwise. That is exactly how the current runtime treats pressure
vectors: they are synthetic candidates with `review_status: draft`,
explicit mutation-boundary notes, and no canonical effect.
[\[31\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/pressure_builder.py)

The orchestrator should therefore emit these things **only as candidate
or evidence artifacts**:

- **Pressure-vector candidates** derived from accepted exception events.
  [\[31\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/pressure_builder.py)
- **Route recommendations** when the orchestrator can narrow a case but
  cannot bind a canonical route with confidence.
- **Event-class suggestions** when the observed issue appears real but
  does not fit published substrate vocabulary.
- **Schema-change requests**, **tool-authority change requests**, and
  **policy-change requests** when the workflow reveals gaps.
- **Learning-loop summaries**, retrieval diagnostics, and
  repeated-failure analyses.
- **Answer-quality or model-performance evidence**, especially from
  trace grading and evals.

The design principle is simple: the orchestrator may propose, explain,
and package evidence; it may not promote evidence into canon. That
boundary lines up with the runtime’s stated governed path:
`exception-event -> pressure-vector -> adaptation-proposal -> promotion-decision`.
[\[32\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/README.md)

### What contracts should exist between the orchestrator and the other two repos

The orchestrator should operate under a small set of explicit contracts:

| Contract                              | Between                               | Purpose                                                                                                                               |
|---------------------------------------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| **Contract pin contract**             | Orchestrator ↔ Semantic substrate     | Pin one reviewed substrate SHA via `contracts.lock.json`; fail closed on drift                                                        |
| **Manifest/export contract**          | Orchestrator ↔ Semantic substrate     | Load a manifest-first bundle of registries, schemas, and boundary docs                                                                |
| **Route authority contract**          | Orchestrator ↔ Semantic substrate     | Require `route_id`, `event_class`, `allowed_raw_actions`, source layers, and promotion-gate semantics to come from the route registry |
| **Boundary doctrine contract**        | Orchestrator ↔ Semantic substrate     | Load and obey Exceptions Lake and AI control plane boundary docs                                                                      |
| **Ingestion envelope contract**       | Orchestrator ↔ Exception Lake runtime | Submit only supported envelope shapes and modes                                                                                       |
| **Validation/result contract**        | Orchestrator ↔ Exception Lake runtime | Consume acceptance/validation/policy results and store them in evidence packets                                                       |
| **Audit/evidence reference contract** | Orchestrator ↔ Exception Lake runtime | Link traces, hashes, tool refs, approval refs, and event-store refs without storing forbidden raw content                             |
| **Candidate-only learning contract**  | Orchestrator ↔ Both repos             | Ensure derived pressure vectors and suggested changes never become canonical without governance                                       |

All of those are either already visible in current runtime behavior or
required to preserve the same authority split as the platform grows.
[\[33\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)

## Human approval and anti-sprawl controls

Current best-practice guidance is unusually consistent on human
oversight and bounded scope. National Institute of Standards and
Technology[\[34\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
says human roles and human-AI configurations should be clearly defined,
and its AI RMF playbook says processes for human oversight should be
documented.
OpenAI[\[5\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
recommends guardrails plus human review, with human intervention
especially for high-risk actions and when failure thresholds are
exceeded.
Anthropic[\[6\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
recommends the simplest workable architecture, then increasing
complexity only when needed. And
LangChain[\[35\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
documents interrupt-based pause/resume flows with persistent state for
human-in-the-loop approvals. Those sources strongly support an
orchestrator that is conservative by default, interruptible, and
review-centered in risky paths.
[\[36\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)

### What should require human approval

These actions should not run straight through the orchestrator without
explicit approval artifacts:

- **Any transition from synthetic work toward real-data handling**,
  including the move into `non_synthetic_dry_run_preflight` and
  certainly any future live-data admission. The current runtime already
  encodes `approval_status == approved_for_dry_run` as a readiness
  requirement.
  [\[37\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/non_synthetic_readiness.py)
- **Any write-capable tool call outside the local sandbox**, including
  future connectors, external records systems, or side-effecting
  updates.
- **Any semantically ambiguous case** where the orchestrator cannot bind
  a canonical `route_id` and `event_class` with confidence from the
  substrate registry.
- **Any contract SHA change**, tool-registry expansion, or model-policy
  change in production.
- **Any adaptation proposal or promotion decision activity**, because
  those sit beyond the runtime’s current evidence boundary.
  [\[38\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
- **Any high-risk action** involving regulated, financial, privileged,
  or privacy-sensitive content. Risk-proportionate controls guidance
  explicitly reserves enhanced logging, human-in-the-loop, and isolation
  for high-risk workloads.
  [\[39\]](https://developers.openai.com/cookbook/examples/partners/agentic_governance_guide/agentic_governance_cookbook)
- **Any run that exceeds failure thresholds**, retries, or budget
  limits. That is a standard trigger for human intervention in current
  agent guidance.
  [\[40\]](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

### Architecture boundaries that prevent agent sprawl

The most important anti-sprawl rule is: **one outer owner**. The
orchestrator should begin with one stable manager that owns the final
reply or final action plan, and it should use specialists as bounded
tools unless ownership truly needs to change. “Agents as tools” is the
better default when the main manager should stay responsible for the
answer; add handoffs only when the next branch truly needs different
tools, instructions, or policy.
[\[41\]](https://developers.openai.com/api/docs/guides/agents/orchestration)

In practical terms, these boundaries prevent sprawl:

- **No dynamic agent creation in production**. All agents and tools
  should be predeclared, versioned, and reviewable.
- **Specialists only when the contract changes**: add them for real
  isolation of policy, capability, or prompt surface, not just for
  convenience.
  [\[19\]](https://developers.openai.com/api/docs/guides/agents/orchestration)
- **Namespaced, non-overlapping tool registry** so the model is not
  forced to choose among vague or duplicate tools.
  [\[9\]](https://www.anthropic.com/engineering/writing-tools-for-agents)
- **Typed intermediate outputs** between nodes, so untrusted text does
  not directly steer downstream tool calls. Current safety guidance
  strongly recommends structured outputs to constrain data flow and
  reduce prompt-injection risk.
  [\[42\]](https://developers.openai.com/api/docs/guides/agent-builder-safety)
- **Hard operational budgets**: max steps, max retries, max fan-out, max
  tokens, max tool calls, max cost, max wall-clock.
- **Mandatory stop conditions**: missing contract SHA, ambiguous route,
  real data, raw transcript retention, unsupported mode, or any request
  that would redefine meaning. The runtime already documents stop
  conditions in exactly this style.
  [\[43\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-stop-conditions.md)
- **Trace-first observability and evals**: every run should be
  inspectable, and policy changes should be tested before deployment.
  [\[44\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)

## MVP boundary and future expansion

### MVP boundary

The minimum viable orchestrator should be **smaller than people
instinctively want**. Public agent guidance recommends starting with one
focused agent and evolving only when complexity is justified; the
current Exception Lake runtime is also intentionally minimal,
synthetic-only, and library-first. A safe MVP therefore looks like this:
one manager orchestrator, a tiny whitelist of internal tools, pinned
substrate loading, policy/risk classification, a human-approval
pause/resume surface, evidence-packet assembly using hashes and
references, and write-through to the existing Exception Lake runtime
functions for synthetic event ingest and metadata-only dry-run
preflight. It should not assume HTTP, live connectors, real data, swarms
of subagents, or automatic learning-loop promotion.
[\[45\]](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

The MVP should therefore include only:

- One **manager** orchestrator.
- At most a few **bounded helpers as tools**, not free-roaming
  specialists.
- Pinned contract loading from semantic substrate.
- Structured envelope building for `exception-event` and dry-run
  readiness requests.
- Submission only through current Exception Lake runtime surfaces.
- Evidence packets made of metadata, hashes, trace refs, tool refs, and
  event refs.
- Human approval interrupts for risky or ambiguous paths.
- No canon mutation, no schema ownership, no adaptation proposal
  creation, no promotion decisions, no raw transcript retention in
  Exception Lake, no live connectors, and no real-data ingestion path.
  [\[46\]](https://developers.openai.com/api/docs/guides/agents/orchestration)

### Future expansion boundary

Future growth should happen by adding **workflow sophistication**, not
by breaking authority boundaries. The best-supported next patterns are
routing, parallelization, orchestrator-workers, and evaluator-optimizer
loops, but they should remain internal execution patterns inside the
orchestrator rather than becoming new semantic authorities. That is
exactly the tradeoff described by Anthropic’s workflow taxonomy:
increase complexity only when the task genuinely requires it.
[\[47\]](https://www.anthropic.com/research/building-effective-agents)

The future boundary should allow:

- Specialist tools for retrieval, summarization, redaction,
  classification, and evidence ranking.
- Risk-tiered model selection and reasoning budgets.
- Durable checkpoint/resume for approvals and long workflows.
- Approved connector adapters, once a later boundary change authorizes
  them.
- Trace grading and formal evaluation datasets.
- External secure transcript storage with pointers only, if production
  capture is later approved.
  [\[48\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-transcript-retention-boundary.md)

But even in that future state, the orchestrator should still **not** own
semantics, canonical categories, route registries, or promotion
decisions. Those remain substrate concerns. Runtime observations and
orchestrator interpretations remain evidence until the governed path
promotes them.
[\[49\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)

## Repository shape and interface surfaces

The current runtime repo already shows a useful shape to mirror:
root-level boundary docs, `contracts.lock.json`, scripts for lock
maintenance, tests, examples, and a `docs/ai-workflow` folder with route
tables and stop conditions. The orchestrator repo should echo that
pattern so agent behavior is documented as explicitly as runtime
behavior.
[\[50\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/tree/main/docs)

### Files the new orchestrator repo should eventually contain

**Root**

- `README.md`
- `AI_WORK_START_HERE.md`
- `AGENTS.md`
- `ARCHITECTURE_ROLE.md`
- `MVP_BOUNDARY.md`
- `FUTURE_EXPANSION_BOUNDARY.md`
- `HUMAN_APPROVAL_MATRIX.md`
- `EXCEPTION_LAKE_INTEGRATION.md`
- `SEMANTIC_SUBSTRATE_CONSUMPTION.md`
- `FAILURE_MODES.md`
- `contracts.lock.json`
- `pyproject.toml`

**Source package**

- `src/lawfirm_os_orchestrator/__init__.py`
- `src/lawfirm_os_orchestrator/api.py`
- `src/lawfirm_os_orchestrator/config.py`
- `src/lawfirm_os_orchestrator/orchestrator.py`
- `src/lawfirm_os_orchestrator/substrate_loader.py`
- `src/lawfirm_os_orchestrator/contract_pin.py`
- `src/lawfirm_os_orchestrator/model_router.py`
- `src/lawfirm_os_orchestrator/tool_registry.py`
- `src/lawfirm_os_orchestrator/tool_executor.py`
- `src/lawfirm_os_orchestrator/policy_engine.py`
- `src/lawfirm_os_orchestrator/risk_classifier.py`
- `src/lawfirm_os_orchestrator/approval_gate.py`
- `src/lawfirm_os_orchestrator/route_binding.py`
- `src/lawfirm_os_orchestrator/envelope_builder.py`
- `src/lawfirm_os_orchestrator/evidence_packet_builder.py`
- `src/lawfirm_os_orchestrator/trace_context.py`
- `src/lawfirm_os_orchestrator/session_store.py`
- `src/lawfirm_os_orchestrator/exception_lake_client.py`
- `src/lawfirm_os_orchestrator/stop_conditions.py`
- `src/lawfirm_os_orchestrator/types.py`
- `src/lawfirm_os_orchestrator/ids.py`
- `src/lawfirm_os_orchestrator/eval_hooks.py`

**Workflow docs**

- `docs/ai-workflow/orchestrator-route-table.yaml`
- `docs/ai-workflow/orchestrator-stop-conditions.md`
- `docs/ai-workflow/tool-authority-table.yaml`
- `docs/ai-workflow/approval-routing.md`
- `docs/ai-workflow/transcript-retention-boundary.md`
- `docs/ai-workflow/evidence-packet-policy.md`

**Tests, scripts, and examples**

- `tests/test_contract_lock.py`
- `tests/test_route_binding.py`
- `tests/test_policy_engine.py`
- `tests/test_approval_gate.py`
- `tests/test_exception_lake_client.py`
- `tests/test_evidence_packet_builder.py`
- `scripts/update_contract_lock.py`
- `scripts/ci_check_contract_lock.py`
- `examples/synthetic_orchestrator_task.json`
- `examples/non_synthetic_preflight_request.json`
- `examples/validated_exception_event.json`

### Contract files it should consume from semantic substrate

**Consume now, because the public runtime already depends on them**

- `registry/exceptions-lake-contract-export.json`
- `registry/schema-registry.json`
- `registry/exceptions-schema-registry.json`
- `registry/governed-learning-schema-registry.json`
- `registry/exception-route-registry.json`
- `schemas/exception-event.schema.json`
- `schemas/pressure-vector.schema.json`
- `schemas/adaptation-proposal.schema.json`
- `schemas/promotion-decision.schema.json`
- `schemas/source-ingestion-manifest.schema.json`
- `schemas/access-decision.schema.json`
- `governance/EXCEPTIONS_LAKE_BOUNDARY.md`
- `governance/AI_CONTROL_PLANE_BOUNDARY.md`
  [\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)

**Request later, because they are the missing orchestrator-specific
authority surfaces**

- `registry/orchestrator-contract-export.json`
- `registry/model-policy-registry.json`
- `registry/tool-authority-registry.json`
- `registry/human-approval-registry.json`
- `schemas/evidence-packet.schema.json`
- `schemas/tool-call-trace.schema.json`
- `schemas/human-approval-record.schema.json`
- `schemas/orchestrator-run-record.schema.json`
- `governance/ORCHESTRATOR_BOUNDARY.md`

Those later files are recommendations, not public current-state
findings, because the semantic substrate repo is still empty.
[\[23\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)

### APIs and events it should send to Exception Lake

**Current public actual surfaces**

- `health(config=None)` for readiness checks.
  [\[51\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- `build_synthetic_envelope(payload, actor=...)` to wrap a canonical
  exception-event payload in the supported runtime envelope.
  [\[52\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- `ingest_synthetic_event(envelope, config=None)` to submit a synthetic
  exception event.
  [\[26\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- `build_non_synthetic_preflight_envelope(readiness_request, actor=...)`
  to wrap a metadata-only readiness request.
  [\[53\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- `run_non_synthetic_preflight(envelope, config=None)` to run audit-only
  dry-run readiness validation.
  [\[54\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
- `build_pressure_candidate(config=None)` to derive a pressure-vector
  candidate from accepted events. This is candidate generation, not
  canonical mutation.
  [\[55\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)

**Current public resulting persisted records**

- Event record with `record_type: synthetic_exception_event`,
  `event_id`, `received_at`, `contract_version`, `schema_id`,
  `validation_result`, `policy_result`, and `payload`.
  [\[29\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py)
- Audit record with `timestamp`, `action`, `result`, `event_id`,
  `actor`, `contract_version`, and `details`. Current `action` values
  are effectively `ingest_synthetic_event` and `dry_run_preflight`.
  [\[29\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py)

**Recommended future runtime surfaces, but only after substrate schemas
exist**

- `append_evidence_packet(...)`
- `append_tool_call_trace(...)`
- `append_human_approval_record(...)`
- `submit_pressure_vector_candidate(...)`

The orchestrator should not invent these as de facto canon inside its
own repo. They should appear only after the semantic substrate defines
their schemas and the Exception Lake runtime adopts them.
[\[56\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md)

## Top failure modes if the orchestrator acts too broadly

If the orchestrator is allowed to expand without hard architectural
boundaries, the most serious failure modes are predictable.

- **Semantic fork**: the orchestrator starts inventing or reinterpret­ing
  `event_class`, `route_id`, schema meanings, or lifecycle states, which
  breaks the authority split and causes contract drift. The runtime
  already fail-closes on exactly these mismatches.
  [\[57\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/validation_gateway.py)
- **Shadow canon mutation**: a tool or agent path effectively rewrites
  ontology, policy, taxonomy, or addresses without going through the
  governed promotion path. The current route mapping explicitly calls
  such actions prohibited direct actions.
  [\[58\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/CANONICAL_ROUTE_MAPPING.md)
- **Evidence/truth confusion**: runtime observations or model-generated
  interpretations get treated as canonical facts rather than evidence.
  The current runtime repeatedly says observations are candidates only,
  and its pressure vectors are explicitly non-canonical.
  [\[59\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/README.md)
- **Prompt injection and malicious tool use**: untrusted input
  influences downstream tool calls, causing data exfiltration or
  misaligned actions. Current safety guidance names prompt injection as
  a common and dangerous attack and recommends structured outputs,
  approvals, and cautious access.
  [\[42\]](https://developers.openai.com/api/docs/guides/agent-builder-safety)
- **Private-data leakage**: the agent sends more data to tools or
  connectors than intended, or stores forbidden transcript content where
  it should not live. OpenAI’s safety guidance and the runtime’s
  transcript-retention boundary both warn about exactly this.
  [\[60\]](https://developers.openai.com/api/docs/guides/agent-builder-safety)
- **Agent sprawl**: too many overlapping subagents and tools create more
  prompts, more traces, more approval surfaces, and less accountability
  without improving outcomes. Both OpenAI and Anthropic warn against
  splitting too early or creating unnecessary complexity.
  [\[61\]](https://developers.openai.com/api/docs/guides/agents/orchestration)
- **Approval bypass**: high-risk, irreversible, privileged, or real-data
  actions run automatically instead of pausing for human review. Current
  guidance is explicit that high-risk actions and failure thresholds
  should trigger human intervention.
  [\[62\]](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- **Observability gaps**: no durable trace, no event-store reference, no
  approval record, or no evidence packet means failures cannot be
  reconstructed or governed. Tracing and audit metadata are first-class
  in current agent guidance and runtime audit planning.
  [\[63\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)
- **Contract drift**: the orchestrator runs against an unpinned or stale
  substrate version, making route validation and policy judgments
  unreliable. The runtime loader already treats lock mismatch as a
  fail-closed error.
  [\[22\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
- **Silent degradation**: prompt or policy changes ship without evals,
  so the orchestrator drifts into worse routing, weaker guardrails, or
  lower-quality evidence capture. Trace grading and policy-eval patterns
  exist precisely to prevent this.
  [\[64\]](https://developers.openai.com/api/docs/guides/agent-evals)

## Open questions and limitations

The main limitation in the public evidence is that the semantic
substrate repo is currently empty, so this report could not inspect
actual substrate files, schemas, or boundary docs there. The design
below is therefore high confidence on **boundary direction** and
**runtime compatibility**, but only medium confidence on the final
substrate file names beyond those already referenced by the runtime. The
key unresolved question is not architectural philosophy; it is whether
the substrate team wants orchestrator-specific contracts to live as an
expanded export manifest, as separate registries, or as both.
[\[65\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)

The safest conclusion is this: **LawFirm-os-orchestrator should be an
execution-and-evidence control plane that is intentionally subordinate
to semantic substrate authority and intentionally downstream of
Exception Lake validation**. If it stays inside that boundary, it can
grow a long way without becoming a semantic fork or an agent sprawl
problem.
[\[66\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)

[\[1\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)
[\[13\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)
[\[44\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)
[\[63\]](https://developers.openai.com/api/docs/guides/agents/integrations-observability)
https://developers.openai.com/api/docs/guides/agents/integrations-observability

<https://developers.openai.com/api/docs/guides/agents/integrations-observability>

[\[2\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)
[\[23\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)
[\[65\]](https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate)
https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate

<https://github.com/lowelltwong-alt/LawFirm-os-semantic-substrate>

[\[3\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
[\[5\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
[\[6\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
[\[20\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
[\[21\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
[\[22\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
[\[33\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py)
https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py

<https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/contract_loader.py>

[\[4\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
[\[14\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
[\[34\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
[\[35\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
[\[38\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
[\[49\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
[\[66\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/RUNTIME_BOUNDARY.md>

[\[7\]](https://developers.openai.com/api/docs/guides/agents)
https://developers.openai.com/api/docs/guides/agents

<https://developers.openai.com/api/docs/guides/agents>

[\[8\]](https://developers.openai.com/api/docs/guides/agents/running-agents)
https://developers.openai.com/api/docs/guides/agents/running-agents

<https://developers.openai.com/api/docs/guides/agents/running-agents>

[\[9\]](https://www.anthropic.com/engineering/writing-tools-for-agents)
https://www.anthropic.com/engineering/writing-tools-for-agents

<https://www.anthropic.com/engineering/writing-tools-for-agents>

[\[10\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md)
[\[30\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md)
[\[56\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-audit-event-policy.md>

[\[11\]](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
https://developers.openai.com/api/docs/guides/agents/guardrails-approvals

<https://developers.openai.com/api/docs/guides/agents/guardrails-approvals>

[\[12\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[25\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[26\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[27\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[51\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[52\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[53\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[54\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
[\[55\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py)
https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py

<https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/api.py>

[\[15\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/validation_gateway.py)
[\[57\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/validation_gateway.py)
https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/validation_gateway.py

<https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/validation_gateway.py>

[\[16\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/CANONICAL_ROUTE_MAPPING.md)
[\[58\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/CANONICAL_ROUTE_MAPPING.md)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/CANONICAL_ROUTE_MAPPING.md

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/CANONICAL_ROUTE_MAPPING.md>

[\[17\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/policy_gateway.py)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/policy_gateway.py

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/policy_gateway.py>

[\[18\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-transcript-retention-boundary.md)
[\[48\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-transcript-retention-boundary.md)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-transcript-retention-boundary.md

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-transcript-retention-boundary.md>

[\[19\]](https://developers.openai.com/api/docs/guides/agents/orchestration)
[\[41\]](https://developers.openai.com/api/docs/guides/agents/orchestration)
[\[46\]](https://developers.openai.com/api/docs/guides/agents/orchestration)
[\[61\]](https://developers.openai.com/api/docs/guides/agents/orchestration)
https://developers.openai.com/api/docs/guides/agents/orchestration

<https://developers.openai.com/api/docs/guides/agents/orchestration>

[\[24\]](https://developers.openai.com/cookbook/examples/partners/agentic_governance_guide/agentic_governance_cookbook)
[\[39\]](https://developers.openai.com/cookbook/examples/partners/agentic_governance_guide/agentic_governance_cookbook)
https://developers.openai.com/cookbook/examples/partners/agentic_governance_guide/agentic_governance_cookbook

<https://developers.openai.com/cookbook/examples/partners/agentic_governance_guide/agentic_governance_cookbook>

[\[28\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py)
[\[29\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/src/exceptions_lake_runtime/event_ingestion.py>

[\[31\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/pressure_builder.py)
https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/pressure_builder.py

<https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/pressure_builder.py>

[\[32\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/README.md)
[\[59\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/README.md)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/README.md

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/README.md>

[\[36\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf

<https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf>

[\[37\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/non_synthetic_readiness.py)
https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/non_synthetic_readiness.py

<https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/blob/main/src/exceptions_lake_runtime/non_synthetic_readiness.py>

[\[40\]](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
[\[45\]](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
[\[62\]](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf

<https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf>

[\[42\]](https://developers.openai.com/api/docs/guides/agent-builder-safety)
[\[60\]](https://developers.openai.com/api/docs/guides/agent-builder-safety)
https://developers.openai.com/api/docs/guides/agent-builder-safety

<https://developers.openai.com/api/docs/guides/agent-builder-safety>

[\[43\]](https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-stop-conditions.md)
https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-stop-conditions.md

<https://raw.githubusercontent.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/refs/heads/main/docs/ai-workflow/runtime-stop-conditions.md>

[\[47\]](https://www.anthropic.com/research/building-effective-agents)
https://www.anthropic.com/research/building-effective-agents

<https://www.anthropic.com/research/building-effective-agents>

[\[50\]](https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/tree/main/docs)
https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/tree/main/docs

<https://github.com/lowelltwong-alt/LawFirm-os-exceptions-lake-runtime/tree/main/docs>

[\[64\]](https://developers.openai.com/api/docs/guides/agent-evals)
https://developers.openai.com/api/docs/guides/agent-evals

<https://developers.openai.com/api/docs/guides/agent-evals>
