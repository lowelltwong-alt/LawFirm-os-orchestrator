# Technology Decision Record for LawFirm OS Orchestrator

## Decision framing

The architectural tradeoff is real because the candidate options solve
different layers of the problem. The Agents SDK from
OpenAI[\[1\]](https://openai.github.io/openai-agents-js/guides/tracing)
emphasizes a small Python-first runtime with tools, handoffs,
guardrails, sessions, human-in-the-loop, usage tracking, structured
outputs, and built-in tracing. LangGraph from
LangChain[\[2\]](https://openai.github.io/openai-agents-js/guides/tracing)
emphasizes low-level orchestration for long-running stateful agents with
persistence, interrupts, durable execution, replay-oriented state
management, and explicit testing guidance.
[\[3\]](https://openai.github.io/openai-agents-python/)

MCP and Temporal solve adjacent but different problems. MCP standardizes
how tools, resources, and prompts are exposed over JSON-RPC transports
such as stdio and Streamable HTTP, with typed tool schemas and explicit
security guidance around sensitive tool invocation. Temporal from
Temporal
Technologies[\[4\]](https://modelcontextprotocol.io/registry/authentication)
is a durable workflow engine whose core value is surviving crashes and
infrastructure failures, preserving execution history, and supporting
replay and time-skipping tests for long-running processes.
[\[5\]](https://modelcontextprotocol.io/docs/learn/architecture)

Because no internal documentation for Semantic Substrate or Exception
Lake was available in accessible sources, this report evaluates those
two compatibility criteria using minimal functional assumptions. I
assume Semantic Substrate is the typed context, grounding, and retrieval
plane that the orchestrator should consume but not own. I assume
Exception Lake is the normalized operational sink for failures, retries,
policy rejections, approvals, and other run events.

Under those assumptions, the key architectural insight is this: LawFirm
OS should not let any one framework become the domain model too early.
The orchestrator should own its own run state, contracts, audit events,
approval policy, and integration surfaces, while treating Agents SDK,
LangGraph, MCP, and later Temporal as pluggable execution or transport
backends. That is why the strongest starting choice is the Hybrid
option.

## Decision matrix

The matrix below scores each option from 1 to 5 for this specific
objective: start as a small local CLI, keep the MVP fast and
understandable, and still preserve a clean path to an auditable,
durable, multi-tool, multi-agent orchestration layer. The weighted fit
slightly favors MVP speed and future durability over any single vendor
convenience. The scores synthesize official feature surfaces in Agents
SDK, LangGraph, MCP, and Temporal documentation.
[\[6\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)

Scale: **5 = strongest fit**, **1 = weakest fit** for the stated
objective.

| Option                                        | MVP | Maint | Lock | Tools | Trace | HITL | Durable | Test | Cost | Sec | Schema | Substrate | ExLake | Cloud | MCP | Fit     |
|-----------------------------------------------|-----|-------|------|-------|-------|------|---------|------|------|-----|--------|-----------|--------|-------|-----|---------|
| Lightweight custom Python CLI                 | 5   | 3     | 5    | 3     | 2     | 3    | 1       | 4    | 5    | 4   | 4      | 4         | 4      | 3     | 3   | **3.4** |
| OpenAI Agents SDK-first                       | 4   | 4     | 3    | 4     | 5     | 5    | 3       | 3    | 4    | 3   | 5      | 4         | 4      | 4     | 5   | **3.9** |
| LangGraph-first                               | 3   | 4     | 4    | 4     | 4     | 5    | 5       | 5    | 4    | 4   | 4      | 4         | 4      | 5     | 5   | **4.3** |
| MCP-first                                     | 2   | 4     | 5    | 5     | 2     | 3    | 1       | 3    | 4    | 5   | 5      | 5         | 4      | 4     | 5   | **3.5** |
| Hybrid deterministic CLI with future adapters | 5   | 5     | 5    | 4     | 4     | 4    | 3       | 5    | 5    | 5   | 5      | 5         | 5      | 5     | 5   | **4.6** |
| Temporal-style architecture later             | 1   | 4     | 4    | 3     | 4     | 5    | 5       | 5    | 3    | 5   | 4      | 4         | 5      | 5     | 4   | **4.0** |

Legend: **Lock** = vendor lock-in, **Tools** = tool interoperability,
**Sec** = security boundaries, **Schema** = schema and contract
integration, **Substrate** = Semantic Substrate compatibility,
**ExLake** = Exception Lake compatibility, **Fit** = weighted fit for
this particular decision.

The Hybrid option wins because it preserves the speed, lock-in
resistance, and cost control of a small local kernel while leaving
explicit adapter seams for the things the frameworks are already best
at: Agents SDK for approvals, tracing, and MCP access; LangGraph for
checkpointed graphs; MCP for protocol-level interoperability; and
Temporal for fully durable workflows.
[\[7\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)

If LawFirm OS insisted on choosing a single framework as the primary
control plane immediately, LangGraph would be the strongest
single-framework choice. Its persistence layer, interrupts, thread and
checkpoint model, and dedicated testing guidance line up closely with
the user’s end-state of auditable, resumable, multi-step orchestration.
[\[8\]](https://docs.langchain.com/oss/python/langgraph/overview)

Agents SDK is the best accelerator for selected workflows, but not the
best sole foundation for the entire orchestrator. It has strong
ergonomics, approvals, run-state resumption, MCP support,
Pydantic-backed schemas, and token-usage tracking, and it can work with
non-OpenAI providers. But its most opinionated advantages are still
centered on the OpenAI ecosystem, and durable execution remains
lighter-weight unless you add an external durability layer such as the
documented DBOS integration.
[\[9\]](https://openai.github.io/openai-agents-python/)

MCP-first is the best protocol posture, not the best runtime posture.
MCP gives the cleanest future story for tool and resource
interoperability because it standardizes transports and contracts, but
it does not provide orchestration durability, replay semantics, or
tracing as a complete control-plane framework.
[\[10\]](https://modelcontextprotocol.io/docs/learn/architecture)

Vendor lock-in is not binary here. Agents SDK, LangGraph, the official
MCP SDKs, and Temporal’s open-source components are all MIT-licensed,
and both Agents SDK and LangGraph support non-OpenAI or model-agnostic
patterns. The practical lock-in risk comes less from source licensing
and more from depending on vendor-specific services such as OpenAI
tracing or hosted MCP execution, or on framework-specific runtime
semantics too early.
[\[11\]](https://github.com/openai/openai-agents-python/blob/main/LICENSE)

## Recommended starting architecture

The recommended starting architecture is **Option 5: Hybrid
deterministic CLI + adapters now, with Agents SDK, LangGraph, MCP, and
Temporal adopted later behind stable seams**.

The most important design choice is not the CLI itself. It is the
creation of a **small orchestration kernel** that owns run state,
execution events, policy decisions, approval gates, retries, idempotency
keys, and contract validation. Models and agent runtimes should help
generate candidate actions, but they should not own the application’s
authoritative state machine. That approach is what lets LawFirm OS begin
as a local CLI without becoming trapped in a one-off script
architecture.

A good mental model is:

    CLI / API entrypoints
        -> Orchestrator Kernel
            -> Run State Store
            -> Audit Ledger / Trace Sink
            -> Tool Registry / Tool Executor
            -> Approval Gate
            -> Model Adapter
            -> Agent Runtime Adapter
            -> Context Provider (Semantic Substrate)
            -> Exception Sink (Exception Lake)
            -> Transport Adapter (local subprocess, MCP stdio, MCP HTTP)

Two recommendations are especially important for a law-firm environment.

First, keep an **append-only audit ledger** outside any vendor
dashboard. OpenAI’s tracing captures generation and function inputs and
outputs by default unless sensitive data capture is disabled, and OpenAI
notes that tracing is unavailable for organizations operating under Zero
Data Retention. That means vendor traces are useful observability
overlays, but they should not be treated as the legal system of record.
The system of record should be your own event model, stored locally
first and exportable later.
[\[12\]](https://openai.github.io/openai-agents-js/guides/tracing)

Second, make every non-read-only tool invocation a **replay-safe
command** with an idempotency key and explicit side-effect boundary.
That makes future migration dramatically easier because LangGraph
durability depends on deterministic replay with side effects isolated
into tasks, while Temporal reconstructs workflow state from execution
history and replay rather than by restoring an arbitrary Python process
frame.
[\[13\]](https://docs.langchain.com/oss/javascript/langgraph/durable-execution)

Tool execution should be split into three classes from day one. Pure
in-process tools are appropriate for safe deterministic transforms such
as schema normalization, citation formatting, or semantic ranking.
Subprocess tools are appropriate for privileged local operations that
should not share memory with the orchestrator. An MCP client adapter is
appropriate for external or separately sandboxed tools that may later
move to Streamable HTTP in cloud deployment. The MCP SDK already models
stdio and Streamable HTTP cleanly, and its own docs recommend Streamable
HTTP for production deployments. Hosted MCP inside Agents SDK should be
treated as optional and off by default for confidential workflows,
because it moves the tool round trip into OpenAI’s infrastructure.
[\[14\]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)

Contracts should be first-class. Tool inputs and outputs, state
snapshots, approval requests, context packets, and exception envelopes
should all be typed with Pydantic models that also emit JSON Schema.
That aligns with Agents SDK function-tool validation and structured
outputs, LangGraph state schemas, and MCP’s tool contract model.
[\[15\]](https://openai.github.io/openai-agents-python/agents/)

For Semantic Substrate specifically, framework-native memory should not
become the source of truth. Agents SDK sessions and LangGraph memory are
useful runtime conveniences, but Semantic Substrate should remain the
authoritative context plane and be injected explicitly into each run as
typed context packets. That preserves auditability and portability
across runtimes.
[\[16\]](https://openai.github.io/openai-agents-python/sessions/)

For Exception Lake, normalize failures at the kernel boundary rather
than storing raw framework-native exceptions as your domain model.
Agents SDK, MCP, and Temporal expose different error and execution
surfaces; a normalized failure envelope preserves comparability across
runtimes and migration stages.
[\[17\]](https://openai.github.io/openai-agents-python/running_agents/)

## Deferred decisions and migration seams

The right discipline is to defer the parts whose value arrives only
after the core contracts are stable. The official docs make the trigger
points fairly clear: LangGraph earns its complexity when you need
persisted branches, interrupts, and replayable threads; Agents SDK earns
its integration when you want high-quality approvals, tracing, and MCP
access in a selected flow; MCP server mode earns its cost when outside
clients need LawFirm OS tools or resources; Temporal earns its
operational weight when runs must survive process loss for hours or
days.
[\[18\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)

### What to defer

| Defer                                 | Until this becomes true                                                                                                        | Why defer now                                                               |
|---------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| LangGraph as the primary runtime      | You need checkpointed branching, graph interrupts, replayable threads, or visual graph debugging                               | It adds runtime shape before the domain model has stabilized                |
| Agents SDK as the primary runtime     | You want native handoffs, run-state approvals, tracing, or MCP in a specific workflow                                          | It is excellent as an accelerator, but too early as the whole control plane |
| MCP server mode for LawFirm OS        | External clients need to consume your tools/resources, or your tool surface is stable enough to publish                        | Publishing a protocol surface before the contracts settle creates churn     |
| Temporal-style durability             | Approvals, retries, or workflows must survive restarts for hours or days, or run in the background with operational guarantees | Durable workflow infrastructure is heavier than a local CLI MVP             |
| Vendor dashboards as the audit system | Never                                                                                                                          | Use them as mirrors, not the source of record                               |
| Rich multi-user cloud UI              | After the event model, approval model, and contracts are stable                                                                | Otherwise the UI will fossilize unstable runtime details                    |

### What abstractions to create now so migration stays easy

The migration seams to build now should line up with the stable concepts
shared across the frameworks: state, tool schema, context, pause and
resume, transport, and history. That mapping is visible in Agents SDK’s
run state, context, and tool model; LangGraph’s state and checkpoint
model; MCP’s tool, resource, and transport model; and Temporal’s
workflow and event-history model.
[\[19\]](https://openai.github.io/openai-agents-python/ref/run_state/)

| Abstraction           | Create now                                                                               | Why it matters later                                                         |
|-----------------------|------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| `RunEnvelope`         | Stable run ID, actor, tenant, prompt version, policy version, timestamps                 | Prevents framework-native metadata from becoming your persistent schema      |
| `RunEvent`            | Append-only event type with correlation IDs and redaction metadata                       | Becomes the audit ledger and feeds Exception Lake                            |
| `StateStore`          | Interface for load, save, checkpoint, resume                                             | Swaps SQLite now for Postgres or a durable backend later                     |
| `ToolSpec`            | Name, description, risk level, input schema, output schema, idempotency, approval policy | Maps naturally to local tools, Agents SDK tools, and MCP tool definitions    |
| `ToolExecutor`        | Pure call contract returning `ToolResult` or `FailureEnvelope`                           | Keeps execution portable across in-process, subprocess, and MCP transports   |
| `ApprovalGate`        | Typed approval request and typed resolution                                              | Maps to Agents SDK interruptions, LangGraph interrupts, and Temporal signals |
| `ModelAdapter`        | Provider-neutral completion or response contract                                         | Preserves model portability and cost control                                 |
| `AgentRuntimeAdapter` | Optional runtime for manager-agent or handoff-style execution                            | Lets selected flows use Agents SDK or LangGraph without rewriting the kernel |
| `ContextProvider`     | Pull typed context packets from Semantic Substrate                                       | Preserves grounding portability and audit clarity                            |
| `ExceptionSink`       | Send normalized failures and decision events to Exception Lake                           | Separates operational analytics from runtime implementation details          |
| `TraceSink`           | Local JSONL and OpenTelemetry-friendly export interface                                  | Lets you mirror into vendor tracing later without coupling to it             |
| `TransportAdapter`    | Local subprocess, MCP stdio, MCP HTTP                                                    | Enables gradual movement from local tools to remote protocol tools           |
| `PromptRegistry`      | Versioned prompt and policy references                                                   | Makes runs reproducible and auditable                                        |
| `IdempotencyPolicy`   | Side-effect keying and replay behavior                                                   | Eases migration to replay-based runtimes such as LangGraph or Temporal       |

## Architecture decision record

**Title.** Build LawFirm OS Orchestrator as a deterministic local-first
Python kernel with typed adapters and an append-only audit ledger.

**Status.** Accepted.

**Date.** 2026-05-05.

**Context.** LawFirm OS needs an orchestrator that can begin as a small
local CLI but grow into a durable, auditable, multi-tool, multi-agent
layer. Official documentation shows that Agents SDK is strongest on
ergonomic agent execution, approvals, tracing, usage tracking, sessions,
and MCP integration; LangGraph is strongest on long-running stateful
orchestration with persistence and interrupts; MCP is strongest on
protocol-level interoperability and typed tool and resource contracts;
Temporal is strongest on durable execution, event history, and testable
recovery semantics. No single option is best across every phase of the
adoption curve. [\[20\]](https://openai.github.io/openai-agents-python/)

**Decision.** Start with a deterministic Python orchestration kernel
that runs locally through a CLI and persists its own run events, state
snapshots, approvals, tool results, and normalized failures. Expose
models, tools, agent runtimes, traces, context access, and failure sinks
through stable internal interfaces. Add Agents SDK, LangGraph, MCP
server mode, and Temporal later only as adapters or backend runtimes,
not as the primary domain schema.

**Rationale.** This decision gives the MVP the speed and simplicity of a
small local CLI while preserving explicit migration seams to the
capabilities that the external frameworks already provide well. It also
protects auditability by keeping the system-of-record event model inside
LawFirm OS rather than in a vendor trace backend. That is especially
important because vendor tracing may include sensitive I/O, and some
managed tracing features are unavailable under Zero Data Retention.
Replay-safe side-effect boundaries are also easier to establish early
than to retrofit later, and both LangGraph and Temporal benefit directly
from that discipline.
[\[21\]](https://openai.github.io/openai-agents-js/guides/tracing)

**Consequences.** The positive consequence is that LawFirm OS avoids
premature framework lock-in and can move selectively into Agents SDK,
LangGraph, MCP, or Temporal when concrete triggers appear. The negative
consequence is that the team must design and maintain a small amount of
core infrastructure itself: an event model, state store, approval model,
trace sink, and adapter layer. That cost is acceptable because those
pieces are the long-lived business architecture, not incidental glue.

**Alternatives not chosen.** A custom CLI alone was rejected because it
leaves too much future capability to be retrofitted. Agents SDK-first
was rejected as the primary control plane because durability and
legal-grade audit boundaries still need an external system of record.
LangGraph-first was not chosen because it adds more runtime shape than
the MVP currently needs, even though it is the best single-framework
choice. MCP-first was not chosen because protocol interoperability is
not a substitute for orchestration. Temporal-first was not chosen
because durable workflow infrastructure is heavier than the present MVP
requires.

**Revisit triggers.** Revisit this ADR if any of the following become
true: approvals must survive restarts for more than one hour; multiple
branchy workflows need replay and visible checkpoints; outside clients
need LawFirm OS tools over a protocol boundary; or the orchestrator
moves from local CLI usage into sustained background execution.

## Risks and mitigations

The most important risks are legal-data leakage through traces,
migration pain caused by hidden side effects and nondeterminism, and
premature dependence on still-evolving protocol or hosted-runtime
surfaces. Those risks are manageable, but only if the system keeps an
internal ledger and narrow interfaces from the start.
[\[22\]](https://openai.github.io/openai-agents-js/guides/tracing)

| Risk                                                               | Why it matters                                                                                                                                                                                                                | Mitigation                                                                                                                                              |
|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| Sensitive client data ends up in vendor traces                     | Agents SDK tracing can capture model and tool I/O unless sensitive data capture is disabled, and tracing is unavailable under ZDR policies. [\[12\]](https://openai.github.io/openai-agents-js/guides/tracing)                | Make the LawFirm OS audit ledger the system of record, redact by default, hash large payloads, and treat vendor traces as optional mirrors              |
| Future durability migration becomes painful                        | Replay-oriented runtimes require deterministic steps and isolated side effects. LangGraph and Temporal both depend on that discipline. [\[13\]](https://docs.langchain.com/oss/javascript/langgraph/durable-execution)        | Introduce idempotency keys now, separate reads from writes, and represent side effects as typed commands                                                |
| Hidden vendor dependence grows faster than expected                | Hosted MCP in Agents SDK pushes tool execution into OpenAI infrastructure, and practical lock-in rises when tracing or hosted runtimes become core dependencies. [\[23\]](https://openai.github.io/openai-agents-python/mcp/) | Keep a provider-neutral `ModelAdapter`, prefer local or self-controlled transports for confidential workflows, and gate hosted features behind policy   |
| MCP ecosystem churn causes integration breakage                    | The registry is still in preview and SDK maturity is tiered across languages. [\[24\]](https://modelcontextprotocol.io/registry/authentication)                                                                               | Adopt a conservative internal subset of MCP, pin SDK versions, and keep an internal `ToolSpec` as the canonical contract                                |
| Security boundaries collapse because too many tools run in-process | Sensitive tools are harder to reason about when they share memory and permissions with the orchestrator                                                                                                                       | Classify tools by risk and move privileged operations to subprocess or MCP boundaries; require explicit approvals for high-risk actions                 |
| Human-in-the-loop becomes an afterthought                          | MCP, Agents SDK, and durable workflows all assume approval or pause/resume patterns for sensitive operations. [\[25\]](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)                                 | Make approval requests a first-class kernel concept instead of a UI-only behavior                                                                       |
| Tests remain too shallow for nondeterministic systems              | LangChain documents fake-model unit tests, LangGraph documents graph tests, and Temporal documents time-skipping tests. [\[26\]](https://docs.langchain.com/oss/python/langchain/test/unit-testing)                           | Build three layers of tests: contract tests, deterministic fake-model tests, and replay or resume tests using recorded event fixtures                   |
| The kernel turns into an accidental internal framework             | Over-abstraction can slow delivery and create its own lock-in                                                                                                                                                                 | Keep the kernel small, freeze only the seams listed above, and reject speculative abstractions that do not correspond to an immediate integration point |

## Roadmap

### Initial month

Days 1–30 should produce the non-negotiable core. Build the Python
package, the CLI entrypoint, the `RunEnvelope` and `RunEvent` schemas,
the SQLite-backed `StateStore`, the append-only JSONL audit writer, the
`ToolSpec` and `ToolExecutor` interfaces, and a first `ContextProvider`
for Semantic Substrate plus a first `ExceptionSink` for Exception Lake.
Implement only a handful of safe local tools. The exit criterion for
this month is not multi-agent behavior. It is the ability to run, pause,
approve, resume, and audit a single deterministic flow end to end.

### Expansion month

Days 31–60 should harden the boundaries. Add subprocess-isolated tools,
explicit policy and approval gating, redaction rules, usage accounting,
and a basic OpenTelemetry-compatible trace sink. Add an MCP client
adapter so at least one tool can run over stdio or Streamable HTTP
without changing the kernel. Build one optional Agents SDK adapter for a
narrowly scoped workflow where handoffs or native approvals are
materially useful. Add replay-oriented integration tests based on saved
event fixtures. The exit criterion for this month is that the same
kernel can drive local tools and one protocol tool while producing a
unified audit and failure trail.

### Hardening month

Days 61–90 should validate the migration path rather than broadening the
MVP indiscriminately. Add a service entrypoint that wraps the same
kernel behind HTTP while preserving the CLI. Run a constrained LangGraph
spike to prove that a selected flow can map to graph state, checkpoints,
and interrupts without changing LawFirm OS contracts. Run a constrained
Temporal design spike for one long-lived approval or retry-heavy
workflow, but only behind the existing kernel contracts. Finalize the
trigger rules for when LangGraph becomes the default runtime for a class
of flows and when Temporal becomes mandatory for background durability.
The exit criterion for this month is architectural confidence: the team
should be able to prove that the same domain contracts survive CLI,
service, MCP, and durable-workflow experiments without rewriting the
core orchestration model.

[\[1\]](https://openai.github.io/openai-agents-js/guides/tracing)
[\[2\]](https://openai.github.io/openai-agents-js/guides/tracing)
[\[12\]](https://openai.github.io/openai-agents-js/guides/tracing)
[\[21\]](https://openai.github.io/openai-agents-js/guides/tracing)
[\[22\]](https://openai.github.io/openai-agents-js/guides/tracing)
https://openai.github.io/openai-agents-js/guides/tracing

<https://openai.github.io/openai-agents-js/guides/tracing>

[\[3\]](https://openai.github.io/openai-agents-python/)
[\[9\]](https://openai.github.io/openai-agents-python/)
[\[20\]](https://openai.github.io/openai-agents-python/)
https://openai.github.io/openai-agents-python/

<https://openai.github.io/openai-agents-python/>

[\[4\]](https://modelcontextprotocol.io/registry/authentication)
[\[24\]](https://modelcontextprotocol.io/registry/authentication)
https://modelcontextprotocol.io/registry/authentication

<https://modelcontextprotocol.io/registry/authentication>

[\[5\]](https://modelcontextprotocol.io/docs/learn/architecture)
[\[10\]](https://modelcontextprotocol.io/docs/learn/architecture)
https://modelcontextprotocol.io/docs/learn/architecture

<https://modelcontextprotocol.io/docs/learn/architecture>

[\[6\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
[\[7\]](https://openai.github.io/openai-agents-python/human_in_the_loop/)
https://openai.github.io/openai-agents-python/human_in_the_loop/

<https://openai.github.io/openai-agents-python/human_in_the_loop/>

[\[8\]](https://docs.langchain.com/oss/python/langgraph/overview)
https://docs.langchain.com/oss/python/langgraph/overview

<https://docs.langchain.com/oss/python/langgraph/overview>

[\[11\]](https://github.com/openai/openai-agents-python/blob/main/LICENSE)
https://github.com/openai/openai-agents-python/blob/main/LICENSE

<https://github.com/openai/openai-agents-python/blob/main/LICENSE>

[\[13\]](https://docs.langchain.com/oss/javascript/langgraph/durable-execution)
https://docs.langchain.com/oss/javascript/langgraph/durable-execution

<https://docs.langchain.com/oss/javascript/langgraph/durable-execution>

[\[14\]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
https://modelcontextprotocol.io/specification/2025-03-26/basic/transports

<https://modelcontextprotocol.io/specification/2025-03-26/basic/transports>

[\[15\]](https://openai.github.io/openai-agents-python/agents/)
https://openai.github.io/openai-agents-python/agents/

<https://openai.github.io/openai-agents-python/agents/>

[\[16\]](https://openai.github.io/openai-agents-python/sessions/)
https://openai.github.io/openai-agents-python/sessions/

<https://openai.github.io/openai-agents-python/sessions/>

[\[17\]](https://openai.github.io/openai-agents-python/running_agents/)
https://openai.github.io/openai-agents-python/running_agents/

<https://openai.github.io/openai-agents-python/running_agents/>

[\[18\]](https://docs.langchain.com/oss/python/langgraph/durable-execution)
https://docs.langchain.com/oss/python/langgraph/durable-execution

<https://docs.langchain.com/oss/python/langgraph/durable-execution>

[\[19\]](https://openai.github.io/openai-agents-python/ref/run_state/)
https://openai.github.io/openai-agents-python/ref/run_state/

<https://openai.github.io/openai-agents-python/ref/run_state/>

[\[23\]](https://openai.github.io/openai-agents-python/mcp/)
https://openai.github.io/openai-agents-python/mcp/

<https://openai.github.io/openai-agents-python/mcp/>

[\[25\]](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

<https://modelcontextprotocol.io/specification/2025-06-18/server/tools>

[\[26\]](https://docs.langchain.com/oss/python/langchain/test/unit-testing)
https://docs.langchain.com/oss/python/langchain/test/unit-testing

<https://docs.langchain.com/oss/python/langchain/test/unit-testing>
