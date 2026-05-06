# World-Class AI Orchestration for LawFirm OS in 2026

## Executive judgment

World-class AI orchestration in 2026 is **not** “many agents talking to
each other until something useful happens.” The strongest production
pattern is a **hybrid system**: deterministic workflow code for
authority, policy, state transitions, retries, approvals, and side
effects; bounded LLM calls for classification, extraction, drafting,
routing within approved options, and evidence synthesis. The leading
vendor and framework docs all point in that direction:
OpenAI[\[1\]](https://www.nist.gov/itl/ai-risk-management-framework)
recommends starting with a single agent and adding complexity only when
needed;
LangChain[\[2\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)’s
production guidance centers on durable execution, persistence, and
interrupts; and
Temporal[\[3\]](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
positions durable execution as the answer once long-running,
failure-prone, approval-heavy processes matter.
[\[4\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)

For **LawFirm OS Orchestrator**, the right design is a **control
plane**, not just an agent loop. Your orchestrator should sit on top of
the Semantic Substrate and Exception Lake Runtime, never replace them.
The Semantic Substrate should remain the source of truth for tool
contracts, schema versions, policies, approval rules, prompt versions,
and model classes. The Exception Lake should remain the evidence and
audit layer for traces, tool calls, approvals, outputs, and artifacts.
The orchestrator’s job is to coordinate runs against those authorities
and emit a complete execution record. That architecture follows the
strongest current patterns around typed tools, structured outputs,
traceability, resumability, and model-router separation.
[\[5\]](https://developers.openai.com/api/docs/guides/structured-outputs)

The best near-term answer is therefore: **start with the OpenAI Agents
SDK inside a lightweight homegrown orchestration shell, while designing
your tools, prompts, and resources to be MCP-compatible from day one**.
Do **not** start MCP-first as if MCP were the orchestrator; it is a
protocol, not a runtime. Do **not** start Temporal-first unless your
first release already requires multi-day resumability, external
approvals, cross-service compensation, and hard operational durability.
Do **not** start with a big multi-agent swarm. Start with a bounded
runner, typed contracts, persisted run state, approvals, tracing, and a
narrow tool surface; then add LangGraph-style persistence or
Temporal-style durable workflows once actual runtime pressure justifies
it. [\[6\]](https://developers.openai.com/api/docs)

## What world-class orchestration looks like in 2026

A world-class orchestrator in 2026 has six defining traits. First,
**every important boundary is typed**: model outputs are
schema-constrained, tools have explicit schemas, and agent-to-agent or
agent-to-workflow handoffs carry structured state rather than free-form
prose. OpenAI’s Structured Outputs guarantee schema adherence; MCP
tools, prompts, and resources are all defined with explicit metadata and
schemas; and both LangGraph and Temporal assume named state and message
structures rather than “just let the model remember.”
[\[7\]](https://developers.openai.com/api/docs/guides/structured-outputs)

Second, **runs are resumable**. In the OpenAI Agents SDK, human approval
pauses execution and `RunState` can be serialized and resumed later. In
LangGraph, interrupts persist graph state and resume from the saved
checkpoint. In Temporal, workflow state is durably persisted in event
history and replayed after failure, with Signals, Queries, and Updates
used to re-enter the process. That is a bright line between reliable
systems and demo-grade loops that lose state on process restart.
[\[8\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)

Third, **the system is observable end-to-end**. OpenAI’s Agents SDK
traces LLM generations, tool calls, handoffs, guardrails, and custom
events by default. LangSmith,
Braintrust[\[9\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp),
and
Langfuse[\[10\]](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
all emphasize linking traces to prompt versions, metrics, and
evaluations. OpenTelemetry is now defining semantic conventions both for
generative AI generally and for MCP specifically, which is exactly the
direction an enterprise orchestrator should follow if it wants long-term
portability.
[\[11\]](https://openai.github.io/openai-agents-python/tracing/)

Fourth, **human oversight is modeled as workflow state, not as an
afterthought**. OpenAI approvals surface as run interruptions; LangGraph
interrupts are explicit pause points; MCP tool invocation guidance says
there should always be a human in the loop with the ability to deny tool
invocations; and Temporal’s Signals/Updates make approval and escalation
first-class parts of the workflow. For a law firm, this matters more
than in almost any other domain because “draft,” “recommend,” and “send”
are different authority levels that should map to different approval
states.
[\[12\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)

Fifth, **tool access is governed, not merely available**. OpenAI’s
MCP/connector guidance explicitly recommends `require_approval`,
`allowed_tools`, trusted servers, and logging of data shared with
third-party MCP servers; MCP’s own guidance treats tools as
model-controlled but recommends clear UI, confirmation prompts, and
human denial. This is the foundation of a real tool registry: not just
“what functions exist,” but “who may invoke them, on what data class,
under what risk policy, with what audit event.”
[\[13\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)

Sixth, **evaluation is continuous, not a launch checklist**. OpenAI’s
own model-selection guidance says to establish an eval baseline with the
strongest model and optimize cost and latency only after quality is
measured. LangSmith exposes both offline and online evaluation.
Braintrust and Langfuse both tie traces back into prompt quality and
iteration. A system that cannot connect a production failure to the
exact prompt, model, tool surface, and policy version that produced it
is not yet world-class.
[\[14\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)

## Pattern assessment

The dominant patterns today are visible in vendor guidance and
production telemetry. OpenAI recommends maximizing a single agent’s
capabilities first, then moving to multi-agent patterns only when logic
or tool overload truly requires it. LangChain’s 2025 survey found that
more than half of respondents had agents in production, observability
was nearly table stakes, and model diversity was normal; it also showed
strong daily use of coding agents, research agents, and custom agents
built on LangChain/LangGraph, while broader “agentic everything”
remained early. That combination points to a market where **bounded
workflows are real, but uncontrolled swarms are still not the center of
gravity**.
[\[15\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)

### Production-grade versus experimental patterns

| Pattern                                                    | Assessment in 2026                                                               | Why                                                                                                                                                                                                                                                                                         |
|------------------------------------------------------------|----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Single-agent with tools                                    | **Production-grade and still the default starting point**                        | OpenAI explicitly recommends starting here, says a single agent can handle many tasks, and only splitting after prompts or tool choice become unreliable. [\[16\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)                               |
| Workflow-first deterministic graph                         | **Production-grade for bounded, stateful business flows**                        | LangGraph’s durable execution, persistence, interrupts, and deterministic/idempotent guidance are aimed directly at production use. [\[17\]](https://docs.langchain.com/oss/python/langgraph/overview)                                                                                      |
| Multi-agent handoff system                                 | **Selective use in production; overused in demos**                               | OpenAI documents both manager and decentralized handoff patterns, but also says to maximize a single agent first because extra agents add complexity and overhead. [\[18\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)                      |
| Router/planner/executor                                    | **Production-grade if the planner is bounded and the executor is deterministic** | Manager-style orchestration is workable when one agent remains in control, while side effects stay in code. Temporal and LangGraph both reinforce deterministic side-effect boundaries. [\[19\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) |
| Event-driven orchestration                                 | **Production-grade when backed by durable workflow semantics**                   | Temporal’s event history, replay, message passing, and continue-as-new make event-driven control reliable; event-driven designs without durable workflow semantics are much more brittle. [\[20\]](https://docs.temporal.io/workflow-execution)                                             |
| MCP-first tool/resource architecture                       | **Production-aligned as an interoperability layer, not a complete orchestrator** | MCP standardizes tools, resources, prompts, auth, progress, cancellation, and logging, but the spec is modular and implementations may support only subsets. [\[21\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)                                                       |
| Hybrid deterministic workflow plus agentic decision points | **The strongest enterprise pattern today**                                       | It matches LangGraph and Temporal durability constraints, OpenAI’s bounded agent guidance, and the operational reality that quality, security, and audit still live outside the model. [\[22\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)                          |

### What should be deterministic code versus LLM calls

For LawFirm OS, the deterministic side should own **identity,
authorization, data classification, workflow transitions, retry policy,
timeout policy, side effects, approval routing, compensation steps,
persistence, and audit/event emission**. LangGraph explicitly says
durable execution works best when workflows are deterministic and
idempotent, with side effects wrapped inside tasks. Temporal requires
deterministic workflow code and pushes side effects into Activities.
Those are the right boundaries for legal operations.
[\[23\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)

The LLM side should own **bounded reasoning under contract**: document
triage, extraction to schema, evidence summarization, issue spotting,
routing among approved branches, query rewriting, comparative synthesis,
and draft generation. Use structured outputs whenever the next system
step depends on the result. Use free-form prose only when the product
actually needs prose.
[\[24\]](https://developers.openai.com/api/docs/guides/structured-outputs)

## Technology comparison

| Technology                  | What it is strongest at now                                                                                                                                                                                                                                                                                                                                                      | Production fit now                                                                         | Main gap                                                                                                                                                                                                                                                                                            | Best role in LawFirm OS                                                         |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| OpenAI Agents SDK           | Code-first agent loops with tools, handoffs, guardrails, human approvals, tracing, sessions, and container-backed execution around the Responses API. OpenAI’s docs now position the Responses API and Agents SDK as the main build path, while the Assistants API is deprecated and scheduled to shut down on August 26, 2026. [\[25\]](https://developers.openai.com/api/docs) | **High** for local and controlled runtime orchestration                                    | Durable multi-day workflow semantics, external approval routing, and cross-service compensation still need an external state machine or workflow runtime. [\[26\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)                                                                | Best first runner for MVP and controlled runtime                                |
| MCP                         | Open interoperability for tools, resources, prompts, authorization, progress, cancellation, and logging. It also keeps model access under client control in the sampling flow. [\[27\]](https://modelcontextprotocol.io/specification/2025-06-18)                                                                                                                                | **High** as a protocol layer                                                               | It is not itself an orchestrator, scheduler, persistence layer, or approval engine. Also, newer features such as task lifecycle and structured logging should be treated as capability targets, not universal assumptions. [\[28\]](https://modelcontextprotocol.io/specification/2025-06-18/basic) | Mandatory compatibility target from day one                                     |
| LangGraph                   | Durable graph execution, checkpoints, persistence, interrupts, time travel, and human-in-the-loop for stateful workflows. [\[17\]](https://docs.langchain.com/oss/python/langgraph/overview)                                                                                                                                                                                     | **High** for workflow-centric orchestration                                                | More framework and state-graph complexity than you need for a local MVP if your workflow is still narrow. [\[29\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)                                                                                                               | Best second-stage runtime if you want deterministic flow plus agentic nodes     |
| Temporal                    | Durable execution for long-running workflows, persisted event history, replay, Signals/Queries/Updates, and Continue-As-New for workflows that may run for days or years. [\[30\]](https://docs.temporal.io/evaluate/understanding-temporal)                                                                                                                                     | **Very high** once approvals, retries, outages, and long waits become first-order concerns | Higher engineering and operational investment; not the lightest way to validate an orchestration model. [\[31\]](https://docs.temporal.io/ai-cookbook)                                                                                                                                              | Best enterprise-grade durable orchestration/control plane                       |
| Lightweight homegrown shell | Fastest path to encode your domain boundaries: your own run record, your own policy checks, your own audit/event schema, your own CLI/service ergonomics                                                                                                                                                                                                                         | **Good only if narrowly scoped**                                                           | Easy to devolve into bespoke glue unless you borrow proven patterns for state, approvals, tracing, and typed tools from the frameworks above. [\[32\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)                                                   | Best wrapper around the first-stage runner, not the long-term runtime by itself |

## Recommended architecture for LawFirm OS Orchestrator

The best architecture is a **three-plane design**.

The **authority plane** should live in the Semantic Substrate. It should
store tool registry entries, prompt versions, workflow definitions,
model classes, approval policies, data classification, and schema
contracts. The orchestrator reads from this plane but does not author
truth inside it. MCP’s separation among tools, prompts, and resources is
useful here because it gives you natural object types for that registry,
while OpenAI prompt versioning, LangSmith/Braintrust/Langfuse prompt
versioning, and structured outputs show how modern systems connect
prompt identities to runtime behavior.
[\[33\]](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)

The **execution plane** should be the Orchestrator runtime. For the MVP,
that means a lightweight service or CLI that wraps the OpenAI Agents
SDK, persists run state, enforces policy before tool calls, and emits
trace and audit events. It should support: run IDs; session IDs;
structured outputs; tool search for large registries; approval
interrupts; model routing within an allowed class; and a sandbox
boundary for code, shell, and file operations. OpenAI’s current platform
supports all of those pieces directly or with light wrapping.
[\[34\]](https://developers.openai.com/api/docs)

The **evidence plane** should be the Exception Lake Runtime. It should
record every important execution artifact: prompt ID and version; model
and reasoning level; retrieved evidence IDs; tool inputs and outputs;
approvals and approvers; guardrail trips; final outputs; and trace/span
IDs. Temporal’s event-history model, OpenAI trace records, and modern
observability platforms all point to the same principle: **your best
debugging surface is the run history, not the source code alone**.
[\[35\]](https://openai.github.io/openai-agents-python/tracing/)

### How tools should be registered, typed, versioned, permissioned, and audited

Each tool entry should have: a stable tool ID; semantic version; JSON
Schema for inputs and output contract; risk class; data domains touched;
action type (`read`, `draft`, `write`, `send`, `publish`, `execute`);
human-approval rule; idempotency class; timeout/retry policy; provenance
mapping; and audit serialization rules. MCP already assumes typed tool
metadata; OpenAI’s tooling surface now supports deferred loading,
allowed-tool filtering, require-approval, and MCP server descriptions;
and legal operations need those capabilities expressed as policy, not
buried inside the prompt.
[\[36\]](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)

A useful practical split is this:

| Class                    | Examples                                                        | Default policy                                                   |
|--------------------------|-----------------------------------------------------------------|------------------------------------------------------------------|
| Read-only evidence tools | search corpus, fetch matter metadata, load governing clause set | auto-allow if scoped to permitted matter and user role           |
| Transform tools          | extract clauses, normalize parties, generate issue list         | auto-allow but require structured output and trace logging       |
| Draft tools              | create memo outline, draft email, propose redlines              | allow with schema contract and provenance bundle                 |
| Side-effect tools        | send email, write DMS, file intake update, open ticket          | human approval required by default                               |
| Execution tools          | shell, code, browser/computer use, file mutation                | sandboxed; allowlist only; approval required; high audit density |

That policy split is exactly aligned with OpenAI’s approval model and
sandbox guidance, MCP’s advice to preserve human denial, and OWASP/NIST
risk framing for agentic systems.
[\[37\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)

### How prompts and model selection should be governed

Prompts should be treated like code artifacts. Version them, pin them,
promote them across environments, and link them to traces and eval
results. OpenAI supports prompt versions and explicit version selection;
LangSmith supports prompt versioning plus commit tags/environments;
Braintrust versions prompts automatically and supports environment-based
promotion; Langfuse links prompt versions to traces and metrics. Do not
rely on “the current prompt in code” as the only source of truth.
[\[38\]](https://developers.openai.com/api/docs/guides/prompting)

Model selection should be **separate from governance authority**. The
policy engine should say things like “this step may use only models from
approved class `legal_drafting_high`, with structured output required,
no autonomous side effects, and no external connectors.” The runtime
router may then choose among models inside that approved class based on
latency, cost, and current performance. MCP’s sampling model is
instructive here because it lets the client retain control over model
access, selection, and permissions, while OpenAI’s own guidance says to
baseline on the strongest model and optimize downward only after evals
prove you can.
[\[39\]](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling)

### What should be OpenAI-specific versus provider-agnostic

Make the following **OpenAI-specific** in the early phases: the runner
implementation, OpenAI tracing integration, guardrail/handoff APIs,
built-in hosted tools where they reduce engineering burden, and
structured-output enforcement if you are already on the Responses API.
These are real accelerators today.
[\[40\]](https://developers.openai.com/api/docs)

Make the following **provider-agnostic** from day one: tool IDs;
schemas; policy classes; approval logic; event/audit schema; prompt
registry identity; run ledger; evaluation datasets; trace correlation
IDs; and MCP server contracts. OpenAI itself now describes the Agents
SDK as provider-agnostic with documented paths to non-OpenAI models,
which is helpful precisely because it lets you separate your
architecture from a single vendor’s inference endpoint.
[\[41\]](https://developers.openai.com/blog/openai-for-developers-2025)

## Current checklist and future-proof principles

### Current world-class orchestration checklist

- Define every agent output that drives downstream automation with a
  schema, and use structured outputs instead of prompt-only format
  instructions.
  [\[42\]](https://developers.openai.com/api/docs/guides/structured-outputs)
- Persist run state, pending approvals, and correlation IDs outside
  process memory. Pause/resume must survive restarts.
  [\[43\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- Keep side effects in deterministic code paths with idempotency and
  retry policy, not in unconstrained model prose.
  [\[23\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- Model approvals as explicit workflow states with timeout, escalation,
  and re-entry, not as UI-only modals.
  [\[44\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- Instrument end-to-end traces and include prompt version, model, tool
  surface, latency, token usage, and outcome metadata.
  [\[45\]](https://openai.github.io/openai-agents-python/tracing/)
- Run both offline evaluations on curated datasets and online
  evaluations on live traffic.
  [\[46\]](https://docs.langchain.com/langsmith/evaluation)
- Put tool permissions, data scopes, and approval policy in a registry,
  not only in tool descriptions or prompts.
  [\[47\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
- Use sandboxed execution for shell, code, computer-use, and file
  mutation, with allowlists/denylists and auditing.
  [\[48\]](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
- Expose internal capabilities through MCP-compatible contracts for
  tools, resources, and prompts.
  [\[49\]](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
- Route models by risk tier and measured quality, not by a hardcoded
  “always use the largest model” rule.
  [\[50\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
- Keep large artifacts and evidence outside workflow history; store
  references in the workflow state and payloads in the Exception Lake.
  Temporal’s event-history limits make this a practical necessity in
  durable systems.
  [\[51\]](https://docs.temporal.io/workflow-execution/event)
- Tie your controls to risk frameworks such as
  NIST[\[52\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)’s
  AI RMF and
  OWASP[\[53\]](https://developers.openai.com/blog/openai-for-developers-2025)’s
  agentic application guidance.
  [\[54\]](https://www.nist.gov/itl/ai-risk-management-framework)

### Future-proof principles

Over the next three to five years, the center of gravity is likely to
move toward **standardized capability surfaces, durable task primitives,
and portable observability**, not away from them. MCP is already
standardizing tools/resources/prompts plus
auth/progress/cancellation/logging, and OpenTelemetry is adding GenAI
and MCP semantic conventions. The runtime winners will be the systems
that can plug into that ecosystem while keeping governance, audit, and
state outside the model vendor boundary.
[\[55\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)

That means LawFirm OS should follow these principles: **protocols over
hidden integrations; policies outside prompts; state outside context
windows; approvals as workflow messages; evidence links over raw
transcript dependence; model classes over vendor names; traces as the
debugging source of truth; and durable runtime only when the workflow
truly becomes long-running or outage-sensitive**. Those principles are
the cleanest synthesis of the current OpenAI, LangGraph, Temporal, MCP,
and enterprise-risk guidance.
[\[56\]](https://developers.openai.com/blog/openai-for-developers-2025)

## Risk register, roadmap, and explicit recommendation

### Risk register

| Risk                                                        | What goes wrong                                                                                        | Control                                                                                                                                                                                                    |
|-------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Prompt injection through tools, connectors, and MCP servers | User or tool-returned content changes model behavior and can trigger unexpected data access or actions | Trust only vetted servers, default to approvals for sensitive actions, allowlist tools, and log shared data. [\[57\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)                  |
| Unauthorized side effects                                   | Agent sends, writes, publishes, or executes before a human intended it to                              | Separate read/draft/send permissions; require approval for high-impact tools; use run-state interrupts and escalation rules. [\[58\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)    |
| Lost state or orphaned approvals                            | Process dies while waiting for review or during a multi-step run                                       | Persist run state/checkpoints now; adopt LangGraph or Temporal when waits become long or frequent. [\[43\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)                              |
| Non-deterministic workflow bugs                             | Retries duplicate actions, side effects occur twice, or replay diverges                                | Keep side effects in tasks/activities; use idempotency keys and deterministic workflow boundaries. [\[23\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)                             |
| Audit gaps                                                  | You cannot reconstruct which prompt, model, evidence, or tool produced a result                        | Emit trace-linked audit events with version IDs for prompts, models, tools, approvals, and outputs. [\[59\]](https://openai.github.io/openai-agents-python/tracing/)                                       |
| Prompt or model regressions                                 | A small change silently degrades quality, safety, or tone                                              | Pin versions, run offline regression suites, and add online evals on live traffic. [\[60\]](https://developers.openai.com/api/docs/guides/prompting)                                                       |
| Data residency and third-party retention problems           | Sensitive legal data reaches external MCP hosts or connectors with different retention policies        | Prefer first-party or officially hosted servers, review third-party terms, and keep policy metadata about external retention. [\[61\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp) |
| Workflow history bloat                                      | Long-running matters accumulate too much history and become slow or unmanageable                       | Use claim-check patterns, external artifact stores, and Continue-As-New for durable workflows. [\[62\]](https://docs.temporal.io/workflow-execution/continue-as-new)                                       |

### Three-stage roadmap

| Stage                          | Goal                                                                                                          | Recommended stack                                                                                                                                                                                                                                                                                                         | What to postpone                                                                                     |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Local MVP                      | Prove the orchestration contract on one or two legal workflows, such as intake triage and memo drafting       | OpenAI Agents SDK + lightweight homegrown CLI/service wrapper; schema-first tool registry in the Semantic Substrate; structured outputs; persisted run ledger; local approvals; trace correlation into the Exception Lake; sandbox for any code/file actions. [\[63\]](https://developers.openai.com/api/docs)            | Multi-agent swarms, cross-service durable runtime, broad connector surface, open-ended tool catalogs |
| Controlled runtime             | Add stateful workflowing, bounded delegation, richer approvals, and environment-based prompt/model governance | Keep the OpenAI runner, add LangGraph-style checkpointed graphs or equivalent persistence where flow complexity justifies it; introduce MCP wrappers for internal tools/resources/prompts; formalize offline and online evals; tighten policy classes. [\[64\]](https://docs.langchain.com/oss/python/langgraph/overview) | Full Temporal adoption unless you now have multi-day or outage-sensitive processes                   |
| Enterprise-grade orchestration | Make the orchestrator durable across days, human queues, outages, and many systems of record                  | Durable workflow runtime such as Temporal for long-lived matters, escalations, reminders, compensations, and event-driven integration; Continue-As-New; Signals/Queries/Updates; enterprise observability/evals stack and stronger policy automation. [\[65\]](https://docs.temporal.io/evaluate/understanding-temporal)  | Very little — this is the maturity stage                                                             |

### Explicit recommendation

**Start with the OpenAI Agents SDK wrapped in a lightweight homegrown
CLI/service shell, and design your tool/resource/prompt contracts to be
MCP-compatible from day one.** Use the Agents SDK for the first runnable
system because it already gives you the right modern primitives —
structured outputs, handoffs, guardrails, tracing, approvals, sessions,
and sandbox-backed execution — without forcing you to commit too early
to a large graph runtime. Make the shell yours because the orchestration
contract, policy checks, run ledger, audit schema, and registry lookups
are LawFirm OS differentiators, not framework features. Make MCP
compatibility non-negotiable because it is the cleanest current hedge
against vendor lock-in. Add LangGraph when you need persistent graph
semantics. Add Temporal when workflows become long-running,
approval-heavy, and operationally critical.
[\[66\]](https://developers.openai.com/api/docs)

Put differently:

- **Do start** with OpenAI Agents SDK as the first agent runner.
  [\[67\]](https://developers.openai.com/api/docs)
- **Do start** with a lightweight homegrown orchestration shell as the
  first LawFirm OS control plane.
  [\[68\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
- **Do start** with MCP-compatible contracts from day one.
  [\[69\]](https://modelcontextprotocol.io/specification/2025-06-18)
- **Do not start** with MCP alone as if it were the runtime.
  [\[70\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)
- **Do not start** with LangGraph unless you already need graph
  persistence and interrupt-heavy flows in the first release.
  [\[71\]](https://docs.langchain.com/oss/python/langgraph/overview)
- **Do not start** with Temporal unless your MVP already includes long
  waits, external approvals, or outage-resilient, multi-system
  workflows.
  [\[72\]](https://docs.temporal.io/evaluate/understanding-temporal)

### Open questions and limitations

The broad architectural conclusions above are high confidence, but two
areas are still moving quickly. First, MCP’s newer task/logging
utilities are valuable signals of where orchestration is heading, yet
support is still modular and uneven across hosts and servers; LawFirm OS
should target compatibility, not assume universal implementation on day
one. Second, the observability market is converging around traces plus
evals, but there is not yet a single dominant neutral standard for every
agent-specific metric, so you should normalize your own event schema
even if you adopt vendor tools.
[\[73\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)

[\[1\]](https://www.nist.gov/itl/ai-risk-management-framework)
[\[54\]](https://www.nist.gov/itl/ai-risk-management-framework)
https://www.nist.gov/itl/ai-risk-management-framework

<https://www.nist.gov/itl/ai-risk-management-framework>

[\[2\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[8\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[12\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[26\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[37\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[43\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[44\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[52\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[58\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
https://openai.github.io/openai-agents-python/human_in_the_loop/

<https://openai.github.io/openai-agents-python/human_in_the_loop/>

[\[3\]](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
[\[48\]](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
https://developers.openai.com/api/docs/guides/tools-code-interpreter

<https://developers.openai.com/api/docs/guides/tools-code-interpreter>

[\[4\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[14\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[15\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[16\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[18\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[19\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[32\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[50\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
[\[68\]](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

<https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/>

[\[5\]](https://developers.openai.com/api/docs/guides/structured-outputs)
[\[7\]](https://developers.openai.com/api/docs/guides/structured-outputs)
[\[24\]](https://developers.openai.com/api/docs/guides/structured-outputs)
[\[42\]](https://developers.openai.com/api/docs/guides/structured-outputs)
https://developers.openai.com/api/docs/guides/structured-outputs

<https://developers.openai.com/api/docs/guides/structured-outputs>

[\[6\]](https://developers.openai.com/api/docs)
[\[25\]](https://developers.openai.com/api/docs)
[\[34\]](https://developers.openai.com/api/docs)
[\[40\]](https://developers.openai.com/api/docs)
[\[63\]](https://developers.openai.com/api/docs)
[\[66\]](https://developers.openai.com/api/docs)
[\[67\]](https://developers.openai.com/api/docs)
https://developers.openai.com/api/docs

<https://developers.openai.com/api/docs>

[\[9\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
[\[13\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
[\[47\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
[\[57\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
[\[61\]](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
https://developers.openai.com/api/docs/guides/tools-connectors-mcp

<https://developers.openai.com/api/docs/guides/tools-connectors-mcp>

[\[10\]](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
[\[33\]](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
[\[49\]](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
https://modelcontextprotocol.io/specification/2025-06-18/server/resources

<https://modelcontextprotocol.io/specification/2025-06-18/server/resources>

[\[11\]](https://openai.github.io/openai-agents-python/tracing/)
[\[35\]](https://openai.github.io/openai-agents-python/tracing/)
[\[45\]](https://openai.github.io/openai-agents-python/tracing/)
[\[59\]](https://openai.github.io/openai-agents-python/tracing/)
https://openai.github.io/openai-agents-python/tracing/

<https://openai.github.io/openai-agents-python/tracing/>

[\[17\]](https://docs.langchain.com/oss/python/langgraph/overview)
[\[64\]](https://docs.langchain.com/oss/python/langgraph/overview)
[\[71\]](https://docs.langchain.com/oss/python/langgraph/overview)
https://docs.langchain.com/oss/python/langgraph/overview

<https://docs.langchain.com/oss/python/langgraph/overview>

[\[20\]](https://docs.temporal.io/workflow-execution)
https://docs.temporal.io/workflow-execution

<https://docs.temporal.io/workflow-execution>

[\[21\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)
[\[28\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)
[\[55\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)
[\[70\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)
[\[73\]](https://modelcontextprotocol.io/specification/2025-06-18/basic)
https://modelcontextprotocol.io/specification/2025-06-18/basic

<https://modelcontextprotocol.io/specification/2025-06-18/basic>

[\[22\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)
[\[23\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)
[\[29\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)
https://docs.langchain.com/oss/python/langgraph/durable-execution

<https://docs.langchain.com/oss/python/langgraph/durable-execution>

[\[27\]](https://modelcontextprotocol.io/specification/2025-06-18)
[\[69\]](https://modelcontextprotocol.io/specification/2025-06-18)
https://modelcontextprotocol.io/specification/2025-06-18

<https://modelcontextprotocol.io/specification/2025-06-18>

[\[30\]](https://docs.temporal.io/evaluate/understanding-temporal)
[\[65\]](https://docs.temporal.io/evaluate/understanding-temporal)
[\[72\]](https://docs.temporal.io/evaluate/understanding-temporal)
https://docs.temporal.io/evaluate/understanding-temporal

<https://docs.temporal.io/evaluate/understanding-temporal>

[\[31\]](https://docs.temporal.io/ai-cookbook)
https://docs.temporal.io/ai-cookbook

<https://docs.temporal.io/ai-cookbook>

[\[36\]](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

<https://modelcontextprotocol.io/specification/2025-06-18/server/tools>

[\[38\]](https://developers.openai.com/api/docs/guides/prompting)
[\[60\]](https://developers.openai.com/api/docs/guides/prompting)
https://developers.openai.com/api/docs/guides/prompting

<https://developers.openai.com/api/docs/guides/prompting>

[\[39\]](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling)
https://modelcontextprotocol.io/specification/2025-06-18/client/sampling

<https://modelcontextprotocol.io/specification/2025-06-18/client/sampling>

[\[41\]](https://developers.openai.com/blog/openai-for-developers-2025)
[\[53\]](https://developers.openai.com/blog/openai-for-developers-2025)
[\[56\]](https://developers.openai.com/blog/openai-for-developers-2025)
https://developers.openai.com/blog/openai-for-developers-2025

<https://developers.openai.com/blog/openai-for-developers-2025>

[\[46\]](https://docs.langchain.com/langsmith/evaluation)
https://docs.langchain.com/langsmith/evaluation

<https://docs.langchain.com/langsmith/evaluation>

[\[51\]](https://docs.temporal.io/workflow-execution/event)
https://docs.temporal.io/workflow-execution/event

<https://docs.temporal.io/workflow-execution/event>

[\[62\]](https://docs.temporal.io/workflow-execution/continue-as-new)
https://docs.temporal.io/workflow-execution/continue-as-new

<https://docs.temporal.io/workflow-execution/continue-as-new>
