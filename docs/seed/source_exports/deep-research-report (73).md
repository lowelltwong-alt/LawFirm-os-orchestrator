# Architecture Contract for LawFirm-os-orchestrator

## Research baseline

The strongest public evidence today is uneven across the two existing repositories. The public repository for LawFirm-os-semantic-substrate exists on entity["company","GitHub","developer platform"], but it is currently empty. By contrast, LawFirm-os-exceptions-lake-runtime is a concrete, library-first, non-production runtime that already documents its boundaries, its contract-loading behavior, and its current ingestion/validation flow. That means the safest design for LawFirm-os-orchestrator is to treat the semantic substrate as the intended long-term authority layer, but to derive the actual initial contract shape from the public Exception Lake runtime code and docs that already exist. citeturn43view0turn10view0turn15view1

The runtime’s current posture is very explicit. It consumes pinned contracts from an authoritative “Law Firm ontology” contract repository, prefers a manifest-first export when available, falls back to specific registries and schemas if the export manifest is absent, validates a strict `contracts.lock.json`, rejects contract drift, validates route authority against the canonical route registry, denies unsupported ingestion modes, and forbids canon mutation. It also states that HTTP is intentionally out of scope for the current implementation, so the current surface is a Python library and CLI rather than a network service. I therefore infer that the future semantic substrate must occupy the “Law Firm ontology” role referenced throughout the runtime, and that the orchestrator should initially integrate against that same pinned-contract, fail-closed model instead of inventing a new authority path. citeturn11view4turn15view4turn13view0turn10view2turn10view0turn15view2

## Recommended role split

The split below is the cleanest way to preserve source-of-truth authority in the substrate, evidence authority in Exception Lake runtime, and execution authority in the orchestrator. That recommendation follows directly from the current public runtime boundaries, validation rules, policy gateway, and contract loader behavior. citeturn15view1turn13view0turn10view2turn11view4

| Repository | Should own | Should never own |
|---|---|---|
| **LawFirm-os-semantic-substrate** | Canonical semantic meaning; schemas; registries; route authority; governance boundaries; validation contracts; authoritative handoff surfaces; approval doctrine | Runtime observation handling; model execution policy; agent session state; ad hoc semantic rewrites driven by runtime convenience |
| **LawFirm-os-exceptions-lake-runtime** | Pinned contract consumption; fail-closed validation; policy gate for allowed ingestion modes; append-only event records; append-only audit records; candidate pressure-vector derivation | Canonical semantics; ontology mutation; automatic adaptation proposals as canon; production data admission without later approved boundary changes |
| **LawFirm-os-orchestrator** | Workflow execution; model/tool routing; bounded tool invocation; run state and checkpoints; approval pauses; evidence packet assembly; Exception Lake invocation; retry/time/cost budgets; evaluations and traces | Canonical schemas; canonical `route_id`; canonical `event_class`; lifecycle states; mutation authority; promotion authority; schema registry ownership; route registry ownership |

### What the orchestrator should own

The orchestrator should own **execution mechanics**, not **semantic truth**. In practice, that means it should own run planning, specialist selection, tool invocation, model selection, state/checkpointing, retry and timeout budgets, evidence-packet assembly, and calls into Exception Lake runtime. That is also the direction recommended by current orchestration guidance from entity["company","OpenAI","ai company"] and entity["company","Anthropic","ai company"]: keep orchestration in application code, start with one focused manager, and add specialists only when capability isolation or policy isolation materially improves the system. citeturn37search1turn29view2turn37search0turn36view0turn32view1turn31view0

Concretely, the orchestrator should own these responsibilities:

- **Run governance at execution time**: task intake, model choice, tool choice, loop control, step limits, retry limits, and cost/latency budgets. citeturn29view2turn38search0turn38search3
- **Bounded tool execution** from a whitelist registry, with tools that are few, distinct, and namespaced so the agent is not overloaded by overlapping capabilities. citeturn30view1
- **Evidence-packet assembly** for each run, using hashes, tool references, trace IDs, route labels, contract SHA, and event-store references rather than raw privileged content. The Exception Lake runtime’s own audit-planning docs already point toward this shape. citeturn25view1turn25view3
- **Human approval pauses and resume flow**, because guardrails and approval are part of runtime orchestration, not semantic authority. Durable paused state is an execution concern. citeturn29view1turn29view2turn30view0
- **Exception Lake integration**, including envelope construction and submission through the current Python facade/CLI surfaces. citeturn42view0turn42view1turn42view2turn42view4
- **Evaluation and observability**, including traces, trace grading, and policy-regression detection on orchestrator changes. citeturn37search0turn37search3turn37search5turn40view5

### What the orchestrator must never own

The orchestrator must never become a shadow semantic authority. The runtime boundary docs are already explicit that the contract repo remains authoritative for schema meaning, lifecycle states, mutation authority, promotion authority, registries, validators, and governed boundary doctrine; the runtime may only consume and validate. The orchestrator should inherit exactly that humility. citeturn15view1turn10view0

It must therefore never own these responsibilities:

- **Canonical semantic definitions**, including schemas, schema meaning, route registries, lifecycle states, and governance doctrine. citeturn15view1turn10view0
- **Canonical route or event vocabularies**, including invention or reinterpretation of `route_id` and `event_class` values. The runtime already rejects unknown values and mismatches against the route registry. citeturn13view0
- **Direct canon mutation**, including adaptation proposal promotion, policy overwrite, taxonomy rewrite, schema mutation, or address-system mutation. citeturn15view0turn15view1
- **Production-data admission authority**. The current runtime only allows `synthetic_test_only` and metadata-only `non_synthetic_dry_run_preflight`, with all data flags false. citeturn10view2turn15view3turn23view0
- **Raw transcript retention in Exception Lake surfaces**. Current runtime docs explicitly forbid storing production conversation text or sealed transcript contents there; only hashes, metadata, and pointers fit the present boundary. citeturn25view3turn25view1
- **Dynamic spawning of uncontrolled subagents**. Current multi-agent guidance is to keep one stable owner and add specialists only when the contract really changes. citeturn36view0turn32view1

## Contracted dataflow

The orchestrator should sit **between** contract authority and evidence persistence, never above either one.

**Text dataflow diagram**

Task or workflow request  
→ Orchestrator intake  
→ Load pinned semantic-substrate manifest, registries, schemas, and boundary docs  
→ Apply risk/policy classification and stop conditions  
→ Manager agent executes with bounded tools and step budgets  
→ If action is high-risk or semantically ambiguous, pause for human approval  
→ Build either a canonical exception-event envelope or a metadata-only dry-run readiness envelope  
→ Call Exception Lake runtime  
→ Runtime applies deny-by-default mode policy and fail-closed schema/route validation  
→ Runtime appends audit record and, when valid, appends exception event record  
→ Runtime may derive a pressure-vector candidate  
→ Orchestrator emits evidence packet, trace pointer, and candidate artifacts for review only. citeturn11view4turn10view2turn13view0turn10view1turn13view1turn25view1

### What the orchestrator should read from the semantic substrate

The **minimum existing public contract set** is whatever the current runtime already expects from the authoritative contract repo:

- `registry/exceptions-lake-contract-export.json` when present, as the preferred manifest-first export. citeturn11view4turn10view0
- `registry/schema-registry.json` citeturn11view4turn10view0
- `registry/exceptions-schema-registry.json` citeturn11view4turn10view0
- `registry/governed-learning-schema-registry.json` citeturn11view4turn10view0
- `registry/exception-route-registry.json` citeturn11view4turn10view0
- `schemas/exception-event.schema.json` citeturn11view4turn10view0
- `schemas/pressure-vector.schema.json` citeturn11view4turn10view0
- `schemas/adaptation-proposal.schema.json` citeturn11view4turn10view0
- `schemas/promotion-decision.schema.json` citeturn11view4turn10view0
- `schemas/source-ingestion-manifest.schema.json` citeturn11view4turn10view0
- `schemas/access-decision.schema.json` citeturn11view4turn10view0
- `governance/EXCEPTIONS_LAKE_BOUNDARY.md` citeturn11view4turn10view0
- `governance/AI_CONTROL_PLANE_BOUNDARY.md` citeturn11view4turn10view0
- A strict pinned SHA through the orchestrator’s own `contracts.lock.json`, matching the runtime’s lock discipline. citeturn11view4turn15view4

Those are the **high-confidence, already evidenced** contract surfaces. Because the semantic substrate repo is currently empty in public, the orchestrator should not assume any richer substrate contract until it is actually published. citeturn43view0

The **recommended future substrate additions** for orchestrator-specific governance are:

- `registry/orchestrator-contract-export.json`
- `registry/model-policy-registry.json`
- `registry/tool-authority-registry.json`
- `registry/human-approval-registry.json`
- `schemas/evidence-packet.schema.json`
- `schemas/tool-call-trace.schema.json`
- `schemas/human-approval-record.schema.json`
- `schemas/orchestrator-run-record.schema.json`
- `governance/ORCHESTRATOR_BOUNDARY.md`

These should live in the semantic substrate, not in the orchestrator, because policy and contract meaning should version and travel with the authority layer rather than be reinvented in each caller. That direction is consistent with governed-agent guidance that recommends policies-as-code, centralized policy packaging, and organization-wide guardrail distribution. citeturn40view1turn40view5turn40view0

### What the orchestrator should write to Exception Lake

For the **MVP**, the orchestrator should write **only through existing Exception Lake runtime surfaces**, not around them. Today, those are the Python facade functions and corresponding CLI commands for health, synthetic ingest, non-synthetic dry-run preflight, event listing, and pressure candidate generation. citeturn42view0turn42view1turn42view2turn42view3turn42view4turn15view2

That means the orchestrator should write these artifact types:

- **Validated exception-event envelopes**, submitted via `ingest_synthetic_event(envelope, config)`. The runtime then applies policy and validation before append-only persistence. citeturn42view0turn10view1
- **Metadata-only non-synthetic readiness envelopes**, submitted via `run_non_synthetic_preflight(envelope, config)`, for audit-only dry runs with no event persistence. citeturn42view2turn10view1turn15view3
- **Audit metadata**, via the runtime’s append-only audit log, with action/result/actor/contract-version/details fields. citeturn10view1turn21view0

The runtime’s actual persisted event record today contains: `record_type`, `event_id`, `received_at`, `contract_version`, `schema_id`, `validation_result`, `policy_result`, and the canonical `payload`. The actual audit record contains: `timestamp`, `action`, `result`, `event_id`, `actor`, `contract_version`, and `details`. The orchestrator should treat those as the **current write contract**. citeturn10view1

For richer evidence packets, the right rule is: **assemble now, persist later when the substrate publishes a schema and the runtime accepts it**. The runtime’s audit-policy docs already suggest what such an envelope should carry—`audit_event_id`, runtime route, mode, contract SHA, schema version, content hashes, policy decision, tool references, event-store reference, retention class, legal-hold status, and hash-linkage—but they also say canonical audit contracts belong in the authority repo. citeturn25view1

### What the orchestrator should emit only as proposed evidence or candidates

Anything beyond a validated exception event should remain **non-canonical** until the semantic substrate and governance path say otherwise. That is exactly how the current runtime treats pressure vectors: they are synthetic candidates with `review_status: draft`, explicit mutation-boundary notes, and no canonical effect. citeturn13view1

The orchestrator should therefore emit these things **only as candidate or evidence artifacts**:

- **Pressure-vector candidates** derived from accepted exception events. citeturn13view1
- **Route recommendations** when the orchestrator can narrow a case but cannot bind a canonical route with confidence.
- **Event-class suggestions** when the observed issue appears real but does not fit published substrate vocabulary.
- **Schema-change requests**, **tool-authority change requests**, and **policy-change requests** when the workflow reveals gaps.
- **Learning-loop summaries**, retrieval diagnostics, and repeated-failure analyses.
- **Answer-quality or model-performance evidence**, especially from trace grading and evals.

The design principle is simple: the orchestrator may propose, explain, and package evidence; it may not promote evidence into canon. That boundary lines up with the runtime’s stated governed path: `exception-event -> pressure-vector -> adaptation-proposal -> promotion-decision`. citeturn10view0turn15view1

### What contracts should exist between the orchestrator and the other two repos

The orchestrator should operate under a small set of explicit contracts:

| Contract | Between | Purpose |
|---|---|---|
| **Contract pin contract** | Orchestrator ↔ Semantic substrate | Pin one reviewed substrate SHA via `contracts.lock.json`; fail closed on drift |
| **Manifest/export contract** | Orchestrator ↔ Semantic substrate | Load a manifest-first bundle of registries, schemas, and boundary docs |
| **Route authority contract** | Orchestrator ↔ Semantic substrate | Require `route_id`, `event_class`, `allowed_raw_actions`, source layers, and promotion-gate semantics to come from the route registry |
| **Boundary doctrine contract** | Orchestrator ↔ Semantic substrate | Load and obey Exceptions Lake and AI control plane boundary docs |
| **Ingestion envelope contract** | Orchestrator ↔ Exception Lake runtime | Submit only supported envelope shapes and modes |
| **Validation/result contract** | Orchestrator ↔ Exception Lake runtime | Consume acceptance/validation/policy results and store them in evidence packets |
| **Audit/evidence reference contract** | Orchestrator ↔ Exception Lake runtime | Link traces, hashes, tool refs, approval refs, and event-store refs without storing forbidden raw content |
| **Candidate-only learning contract** | Orchestrator ↔ Both repos | Ensure derived pressure vectors and suggested changes never become canonical without governance |

All of those are either already visible in current runtime behavior or required to preserve the same authority split as the platform grows. citeturn11view4turn13view0turn10view2turn10view1turn25view1

## Human approval and anti-sprawl controls

Current best-practice guidance is unusually consistent on human oversight and bounded scope. entity["organization","National Institute of Standards and Technology","us standards agency"] says human roles and human-AI configurations should be clearly defined, and its AI RMF playbook says processes for human oversight should be documented. entity["company","OpenAI","ai company"] recommends guardrails plus human review, with human intervention especially for high-risk actions and when failure thresholds are exceeded. entity["company","Anthropic","ai company"] recommends the simplest workable architecture, then increasing complexity only when needed. And entity["company","LangChain","ai framework company"] documents interrupt-based pause/resume flows with persistent state for human-in-the-loop approvals. Those sources strongly support an orchestrator that is conservative by default, interruptible, and review-centered in risky paths. citeturn29view5turn29view6turn29view7turn29view1turn31view0turn32view1turn30view0

### What should require human approval

These actions should not run straight through the orchestrator without explicit approval artifacts:

- **Any transition from synthetic work toward real-data handling**, including the move into `non_synthetic_dry_run_preflight` and certainly any future live-data admission. The current runtime already encodes `approval_status == approved_for_dry_run` as a readiness requirement. citeturn23view0turn15view3
- **Any write-capable tool call outside the local sandbox**, including future connectors, external records systems, or side-effecting updates.
- **Any semantically ambiguous case** where the orchestrator cannot bind a canonical `route_id` and `event_class` with confidence from the substrate registry.
- **Any contract SHA change**, tool-registry expansion, or model-policy change in production.
- **Any adaptation proposal or promotion decision activity**, because those sit beyond the runtime’s current evidence boundary. citeturn15view1turn25view2
- **Any high-risk action** involving regulated, financial, privileged, or privacy-sensitive content. Risk-proportionate controls guidance explicitly reserves enhanced logging, human-in-the-loop, and isolation for high-risk workloads. citeturn40view2turn31view0
- **Any run that exceeds failure thresholds**, retries, or budget limits. That is a standard trigger for human intervention in current agent guidance. citeturn31view0

### Architecture boundaries that prevent agent sprawl

The most important anti-sprawl rule is: **one outer owner**. The orchestrator should begin with one stable manager that owns the final reply or final action plan, and it should use specialists as bounded tools unless ownership truly needs to change. “Agents as tools” is the better default when the main manager should stay responsible for the answer; add handoffs only when the next branch truly needs different tools, instructions, or policy. citeturn36view0

In practical terms, these boundaries prevent sprawl:

- **No dynamic agent creation in production**. All agents and tools should be predeclared, versioned, and reviewable.
- **Specialists only when the contract changes**: add them for real isolation of policy, capability, or prompt surface, not just for convenience. citeturn36view0turn32view1
- **Namespaced, non-overlapping tool registry** so the model is not forced to choose among vague or duplicate tools. citeturn30view1
- **Typed intermediate outputs** between nodes, so untrusted text does not directly steer downstream tool calls. Current safety guidance strongly recommends structured outputs to constrain data flow and reduce prompt-injection risk. citeturn41view0
- **Hard operational budgets**: max steps, max retries, max fan-out, max tokens, max tool calls, max cost, max wall-clock.
- **Mandatory stop conditions**: missing contract SHA, ambiguous route, real data, raw transcript retention, unsupported mode, or any request that would redefine meaning. The runtime already documents stop conditions in exactly this style. citeturn25view2
- **Trace-first observability and evals**: every run should be inspectable, and policy changes should be tested before deployment. citeturn37search0turn37search3turn40view4

## MVP boundary and future expansion

### MVP boundary

The minimum viable orchestrator should be **smaller than people instinctively want**. Public agent guidance recommends starting with one focused agent and evolving only when complexity is justified; the current Exception Lake runtime is also intentionally minimal, synthetic-only, and library-first. A safe MVP therefore looks like this: one manager orchestrator, a tiny whitelist of internal tools, pinned substrate loading, policy/risk classification, a human-approval pause/resume surface, evidence-packet assembly using hashes and references, and write-through to the existing Exception Lake runtime functions for synthetic event ingest and metadata-only dry-run preflight. It should not assume HTTP, live connectors, real data, swarms of subagents, or automatic learning-loop promotion. citeturn31view0turn32view1turn10view0turn10view2turn15view2turn15view3

The MVP should therefore include only:

- One **manager** orchestrator.
- At most a few **bounded helpers as tools**, not free-roaming specialists.
- Pinned contract loading from semantic substrate.
- Structured envelope building for `exception-event` and dry-run readiness requests.
- Submission only through current Exception Lake runtime surfaces.
- Evidence packets made of metadata, hashes, trace refs, tool refs, and event refs.
- Human approval interrupts for risky or ambiguous paths.
- No canon mutation, no schema ownership, no adaptation proposal creation, no promotion decisions, no raw transcript retention in Exception Lake, no live connectors, and no real-data ingestion path. citeturn36view0turn41view0turn25view3turn25view2

### Future expansion boundary

Future growth should happen by adding **workflow sophistication**, not by breaking authority boundaries. The best-supported next patterns are routing, parallelization, orchestrator-workers, and evaluator-optimizer loops, but they should remain internal execution patterns inside the orchestrator rather than becoming new semantic authorities. That is exactly the tradeoff described by Anthropic’s workflow taxonomy: increase complexity only when the task genuinely requires it. citeturn32view3turn32view1

The future boundary should allow:

- Specialist tools for retrieval, summarization, redaction, classification, and evidence ranking.
- Risk-tiered model selection and reasoning budgets.
- Durable checkpoint/resume for approvals and long workflows.
- Approved connector adapters, once a later boundary change authorizes them.
- Trace grading and formal evaluation datasets.
- External secure transcript storage with pointers only, if production capture is later approved. citeturn25view3turn37search3

But even in that future state, the orchestrator should still **not** own semantics, canonical categories, route registries, or promotion decisions. Those remain substrate concerns. Runtime observations and orchestrator interpretations remain evidence until the governed path promotes them. citeturn15view1turn13view1

## Repository shape and interface surfaces

The current runtime repo already shows a useful shape to mirror: root-level boundary docs, `contracts.lock.json`, scripts for lock maintenance, tests, examples, and a `docs/ai-workflow` folder with route tables and stop conditions. The orchestrator repo should echo that pattern so agent behavior is documented as explicitly as runtime behavior. citeturn14view0turn24view0turn15view2

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
- `governance/AI_CONTROL_PLANE_BOUNDARY.md` citeturn11view4turn10view0

**Request later, because they are the missing orchestrator-specific authority surfaces**

- `registry/orchestrator-contract-export.json`
- `registry/model-policy-registry.json`
- `registry/tool-authority-registry.json`
- `registry/human-approval-registry.json`
- `schemas/evidence-packet.schema.json`
- `schemas/tool-call-trace.schema.json`
- `schemas/human-approval-record.schema.json`
- `schemas/orchestrator-run-record.schema.json`
- `governance/ORCHESTRATOR_BOUNDARY.md`

Those later files are recommendations, not public current-state findings, because the semantic substrate repo is still empty. citeturn43view0

### APIs and events it should send to Exception Lake

**Current public actual surfaces**

- `health(config=None)` for readiness checks. citeturn42view3
- `build_synthetic_envelope(payload, actor=...)` to wrap a canonical exception-event payload in the supported runtime envelope. citeturn42view1
- `ingest_synthetic_event(envelope, config=None)` to submit a synthetic exception event. citeturn42view0turn10view1
- `build_non_synthetic_preflight_envelope(readiness_request, actor=...)` to wrap a metadata-only readiness request. citeturn42view1turn42view2
- `run_non_synthetic_preflight(envelope, config=None)` to run audit-only dry-run readiness validation. citeturn42view2turn10view1
- `build_pressure_candidate(config=None)` to derive a pressure-vector candidate from accepted events. This is candidate generation, not canonical mutation. citeturn42view4turn13view1

**Current public resulting persisted records**

- Event record with `record_type: synthetic_exception_event`, `event_id`, `received_at`, `contract_version`, `schema_id`, `validation_result`, `policy_result`, and `payload`. citeturn10view1
- Audit record with `timestamp`, `action`, `result`, `event_id`, `actor`, `contract_version`, and `details`. Current `action` values are effectively `ingest_synthetic_event` and `dry_run_preflight`. citeturn10view1

**Recommended future runtime surfaces, but only after substrate schemas exist**

- `append_evidence_packet(...)`
- `append_tool_call_trace(...)`
- `append_human_approval_record(...)`
- `submit_pressure_vector_candidate(...)`

The orchestrator should not invent these as de facto canon inside its own repo. They should appear only after the semantic substrate defines their schemas and the Exception Lake runtime adopts them. citeturn25view1turn43view0

## Top failure modes if the orchestrator acts too broadly

If the orchestrator is allowed to expand without hard architectural boundaries, the most serious failure modes are predictable.

- **Semantic fork**: the orchestrator starts inventing or reinterpret­ing `event_class`, `route_id`, schema meanings, or lifecycle states, which breaks the authority split and causes contract drift. The runtime already fail-closes on exactly these mismatches. citeturn13view0turn15view1
- **Shadow canon mutation**: a tool or agent path effectively rewrites ontology, policy, taxonomy, or addresses without going through the governed promotion path. The current route mapping explicitly calls such actions prohibited direct actions. citeturn15view0
- **Evidence/truth confusion**: runtime observations or model-generated interpretations get treated as canonical facts rather than evidence. The current runtime repeatedly says observations are candidates only, and its pressure vectors are explicitly non-canonical. citeturn10view0turn13view1
- **Prompt injection and malicious tool use**: untrusted input influences downstream tool calls, causing data exfiltration or misaligned actions. Current safety guidance names prompt injection as a common and dangerous attack and recommends structured outputs, approvals, and cautious access. citeturn41view0
- **Private-data leakage**: the agent sends more data to tools or connectors than intended, or stores forbidden transcript content where it should not live. OpenAI’s safety guidance and the runtime’s transcript-retention boundary both warn about exactly this. citeturn41view0turn25view3
- **Agent sprawl**: too many overlapping subagents and tools create more prompts, more traces, more approval surfaces, and less accountability without improving outcomes. Both OpenAI and Anthropic warn against splitting too early or creating unnecessary complexity. citeturn36view0turn32view1turn30view1
- **Approval bypass**: high-risk, irreversible, privileged, or real-data actions run automatically instead of pausing for human review. Current guidance is explicit that high-risk actions and failure thresholds should trigger human intervention. citeturn31view0turn29view1
- **Observability gaps**: no durable trace, no event-store reference, no approval record, or no evidence packet means failures cannot be reconstructed or governed. Tracing and audit metadata are first-class in current agent guidance and runtime audit planning. citeturn37search0turn25view1turn40view3
- **Contract drift**: the orchestrator runs against an unpinned or stale substrate version, making route validation and policy judgments unreliable. The runtime loader already treats lock mismatch as a fail-closed error. citeturn11view4turn15view4
- **Silent degradation**: prompt or policy changes ship without evals, so the orchestrator drifts into worse routing, weaker guardrails, or lower-quality evidence capture. Trace grading and policy-eval patterns exist precisely to prevent this. citeturn37search3turn37search5turn40view4

## Open questions and limitations

The main limitation in the public evidence is that the semantic substrate repo is currently empty, so this report could not inspect actual substrate files, schemas, or boundary docs there. The design below is therefore high confidence on **boundary direction** and **runtime compatibility**, but only medium confidence on the final substrate file names beyond those already referenced by the runtime. The key unresolved question is not architectural philosophy; it is whether the substrate team wants orchestrator-specific contracts to live as an expanded export manifest, as separate registries, or as both. citeturn43view0turn11view4

The safest conclusion is this: **LawFirm-os-orchestrator should be an execution-and-evidence control plane that is intentionally subordinate to semantic substrate authority and intentionally downstream of Exception Lake validation**. If it stays inside that boundary, it can grow a long way without becoming a semantic fork or an agent sprawl problem. citeturn15view1turn36view0turn32view1