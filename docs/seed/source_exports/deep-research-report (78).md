# Bottleneck-first architecture for LawFirm OS Orchestrator

## Executive summary

Workspace note: no retrievable uploaded project/source file was accessible through the available workspace tools at report time, so this report treats the architecture decisions stated in your prompt as the authoritative project baseline.

The right design center for LawFirm OS Orchestrator is not “more agency.” It is **legal-grade, governance-safe throughput**: turning a raw exception into a contract-pinned, schema-valid, auditable, reviewable proposed evidence packet with the fewest possible model calls, the fewest possible decision points, and no semantic drift. That bias is reinforced by the legal obligations emphasized in entity["organization","American Bar Association","us lawyers association"] Formal Opinion 512, which frames generative AI use around competence, confidentiality, communication, supervision, and review, and by the NIST AI RMF and playbook, which emphasize documentation, monitoring, risk response, and clearly assigned responsibilities across the AI lifecycle. citeturn7search16turn7search5turn0search3turn8search0turn8search1

For this project, the orchestrator should be treated as a **bounded coordination layer**. It should coordinate tasks, model calls, tools, human approvals, policy gates, run ledgers, and proposed evidence packets. It should **never** define canonical meaning, invent schema authority, or bypass the Semantic Substrate or Exception Lake validation boundary. That stance is also aligned with current agent-building guidance: entity["company","Anthropic","ai company"] advises starting with the simplest workable solution and only adding complexity when needed, while recent OpenAI guidance emphasizes structured outputs, explicit tool approvals, traceability, and reducing injection risk in multi-step workflows. citeturn18search0turn17search2turn21search0turn10search1turn15search0

The best throughput unit for the orchestrator MVP is **accepted, decision-ready proposed exception packets per reviewer hour**, where “accepted” means substrate-aligned, schema-valid, evidence-sufficient, and admissible through the Exception Lake boundary. What should **not** be treated as throughput: number of agents, number of model calls, raw event count, prompt complexity, dashboard count, contract churn, or autonomous actions. Those are either costs, noise, or local optimizations rather than system value. This is the TOC distinction between optimizing the system and optimizing local activity, applied to a knowledge-work service flow rather than a factory. citeturn4search0turn6search1turn3search0turn3search8

The first bottleneck the orchestrator should attack is **contract-aligned exception classification and evidence-packet assembly at the governance boundary**, because that is where scarce human review attention is currently most likely to be consumed and where errors create downstream waste. The smallest architecture that attacks that bottleneck is a **local-first Python CLI** with a read-only substrate adapter, one bounded structured-output classifier, deterministic validators, immutable run ledgers, a proposed evidence-packet builder, and an optional validate-only Exception Lake handoff. No web app. No swarm. No production connectors. No autonomous writes. citeturn18search0turn21search0turn0search3turn8search1turn17search2

## First principles and system economics

Law-firm orchestration has to satisfy a stricter baseline than generic “agentic workflow” software. The system must preserve confidentiality, support competent supervision, keep humans accountable for material decisions, and make it possible to reconstruct who or what did what, under which policy, using which model, on which contract version. NIST’s trustworthiness framing adds the need for validity, reliability, safety, security, resilience, accountability, transparency, explainability, privacy enhancement, and bias management; the generative AI profile also explicitly highlights confabulation as a material risk for open-ended generation. citeturn7search16turn19search6turn19search20turn8search2

### First-principles breakdown

| First principle | What it means for LawFirm OS Orchestrator |
|---|---|
| Canonical meaning must stay upstream | Route IDs, `event_class`, schemas, and governance authority are imported from the Semantic Substrate by explicit pin, never inferred into existence by the orchestrator. |
| Runtime observations are evidence, not truth | Model outputs, tool results, and operator notes are candidates or evidence items until validated and admitted through the Exception Lake boundary. |
| Every material step must be attributable | Each run must preserve provenance for contract pin, prompt version, model, tool calls, approvals, validation results, and packet hashes. |
| Fail closed beats clever recovery | Missing contract, stale pin, invalid enum, absent approval, or failed validation should stop the run rather than trigger improvisation. |
| Human attention is the scarce resource | The orchestrator should reduce reviewer burden by improving packet quality, not by flooding reviewers with more proposals. |
| Least privilege is mandatory | Tool access should be allowlisted, approval-gated, and scoped to the run. No broad connectors in the MVP. |
| Learning must be governed | Improvements become proposals, eval findings, or substrate change requests. They do not silently rewrite meaning or policy. |
| Reproducibility is more valuable than autonomy | A replayable, idempotent run is more useful than a clever autonomous loop that cannot be trusted in audit. |

### System goal and throughput

The system goal is not “automate legal work.” The system goal is **to compress the time from exception detection to governed, auditable, correct operational disposition while preserving canonical semantics and legal-grade accountability**. Lean starts by defining value from the customer’s perspective, and TOC emphasizes global rather than local optimization; together, they imply that the orchestrator’s local metrics should only count if they improve the end-to-end value stream. citeturn3search0turn3search7turn3search8turn4search0turn6search1

| Item | Recommendation |
|---|---|
| Real goal of LawFirm OS | Faster, safer, auditable disposition of law-firm exceptions and operational bottlenecks without semantic drift. |
| Primary throughput unit | **Accepted proposed exception packets** per reviewer hour. |
| Definition of an accepted packet | Contract-pinned, route-valid, `event_class`-valid, schema-valid, evidence-sufficient, provenance-complete, approval-complete, Exception Lake-admissible. |
| Useful secondary outcomes | Reduced time-to-decision, lower review burden, fewer defects, higher first-pass validation, improved contract reuse, better improvement proposals. |
| Acceptable lagging measures | Cycle time from raw exception to admitted packet; reviewer acceptance rate; defect escape rate. |
| Useful leading measures | Exact route/event match rate on labeled fixtures, evidence completeness, stale-pin rate, duplicate-event rate, abstention rate, reviewer edits per packet. |
| What is **not** throughput | Agent count, model-call count, tokens, prompt length, number of dashboards, raw ingested events, number of proposed contract changes, repo activity. |

### Bottleneck map for the current architecture

This bottleneck map is an **architectural inference**, not an observed production telemetry report.

| Likely bottleneck | Why it is likely in your design | Attack now? | Why |
|---|---|---:|---|
| Contract-aligned exception classification | Every useful run must map messy runtime input into canonical route/event semantics without inventing meaning. | **Yes** | This is the first place where automation can reduce reviewer effort without threatening governance authority. |
| Evidence sufficiency and packet quality | Low-quality packets convert model time into human rework. | **Yes** | Packet quality determines whether review capacity is amplified or wasted. |
| Human approval / semantic review | Legal-grade workflows preserve human accountability. | Partly | Exploit it by improving packet quality; do not try to automate it away first. |
| Contract lock synchronization | Two repos plus pinned contracts create versioning and hash-alignment risk. | **Yes** | Add explicit pinning, manifest recording, and stale-pin hard failures immediately. |
| Prompt quality | Poor prompts increase classification defects. | Partly | Improve through fixture-based evals, not through big architecture. |
| Tool / model reliability | Real tools add variance, latency, and approval burden. | No for MVP | The MVP should avoid broad tool use entirely. |
| Event ingestion scale | Volume issues matter later. | No | Synthetic, local-first CLI means scale is not the first constraint. |
| Audit review | Auditability matters immediately, but review volume matters after packets start flowing. | Partly | Build ledgers now; optimize audit operations later. |
| Public release hygiene | Cross-repo publishing can become brittle. | No | Keep release steps explicit and manual until the intake/classification bottleneck moves. |
| Developer / operator attention | Always scarce. | **Yes** | The architecture should protect it through narrow scope, WIP limits, fixture tests, and append-only ledgers. |

### Value-stream map

Lean value-stream mapping is about making the full information and work flow visible, including non-value-adding steps that create delay or rework. Applied here, the orchestrator should be designed around one-piece flow for a single exception packet, not around parallel agent speculation. citeturn3search9turn3search4turn3search1

| Step | Required output | Common waste if done poorly | MVP posture |
|---|---|---|---|
| Raw exception intake | Normalized synthetic input artifact | Ambiguous inputs, missing fields, stale context | Strict input schema and hash the raw artifact. |
| Contract pin / context assembly | Immutable substrate release ref + allowed route/event enums | Floating “latest,” context pollution, wrong enum universe | Explicit pin only; no floating contract resolution in production mode. |
| Structured classification | Proposed `route_id`, `event_class`, confidence band, evidence needs | Freeform prose, invented enums, false confidence | One structured-output model call with abstain path. |
| Evidence assembly | Proposed evidence packet | Weak or missing evidence, duplicate artifacts | Deterministic packet builder with minimum evidence rules. |
| Deterministic validation | Pass/fail report | Silent coercions, lax schema checks | Fail closed; no auto-repair beyond one bounded retry. |
| Approval / policy gate | Human or policy decision where required | Skipped approvals, unclear ownership | Explicit approval records, no inferred approvals. |
| Exception Lake handoff | Validate-only or admitted packet result | Boundary bypass, duplicate writes | Validation boundary only, idempotency key required. |
| Eval / learning | Run labels, defect tags, improvement proposal | Uncaptured lessons, prompt drift | Append-only ledger plus labeled synthetic fixtures. |

## Constraint-centered operating model

### Theory of Constraints applied directly

entity["organization","TOCICO","theory constraints org"] describes the Five Focusing Steps as identifying the system constraint, exploiting it, subordinating everything else to it, elevating it, and then repeating without letting inertia become the next constraint. That sequence is the right backbone for the orchestrator because it forces the design to serve one bottleneck rather than accumulate features. citeturn4search0turn4search1

| TOC step | Direct application to LawFirm OS Orchestrator | Design decision |
|---|---|---|
| Identify the constraint | The first constraint is the conversion of raw exceptions into substrate-aligned, evidence-sufficient, reviewable packets. | The MVP is a **classifier-plus-validator** architecture, not a general orchestration platform. |
| Exploit the constraint | Get the most out of reviewer attention by making every packet easier to accept or reject quickly. | Versioned prompts, structured outputs, exact enum validation, confidence thresholds, packet templates, abstain when uncertain. |
| Subordinate everything else | Any work that does not increase packet validity or reduce review time is deferred. | No web UI, no connectors, no swarms, no long-running graph runtime, no broad tool registry. |
| Elevate the constraint | Only after the first bottleneck is measurably improved should you add supporting mechanisms. | Add duplicate detection, disagreement checks, a terminal approval flow, or replay/durable execution only if packet quality is no longer the main constraint. |
| Repeat and avoid inertia | Once packet quality is good, the bottleneck may move to approvals, release cadence, or replay reliability. | Keep run-level metrics and defect tags so the next bottleneck is found empirically, not guessed. |

### Drum-buffer-rope for LawFirm OS

The DBR idea is useful here if applied carefully. TOC’s DBR and buffer-management literature emphasizes buffer management as a signaling system for prioritizing, expediting, escalating, and targeting improvements rather than maximizing upstream output for its own sake. citeturn5search6turn5search0

| DBR concept | LawFirm OS meaning | Concrete control |
|---|---|---|
| Drum | The sustainable rate at which reviewers and validation gates can absorb **decision-ready packets** | Treat reviewer acceptance capacity as the pacing function. |
| Buffer | Small queue of prevalidated packets waiting for review; also a contract snapshot and evidence-completeness buffer | WIP cap per reviewer or route; required evidence checklist before review. |
| Rope | Admission control that prevents the orchestrator from overproducing low-value work | Run only when there is a valid contract pin, an eligible input, and review capacity. |

To stop overproduction of low-value agent work, the orchestrator should enforce **hard run budgets**: one primary classification call, one optional repair call on format failure, zero broad fan-out, zero autonomous write actions, one proposed packet per raw exception, explicit idempotency keys, and a hard-stop on loop count, token budget, or elapsed time. If validation fails, the run should stop or abstain; it should not recursively generate more tasks. This is the rope. citeturn18search0turn17search2turn10search1turn21search0

### Bottlenecks that should not be automated yet

| Bottleneck or activity | Why not now |
|---|---|
| Semantic contract changes | This would blur the boundary with the Semantic Substrate and let runtime pressure redefine canonical meaning. |
| Final semantic disputes | These are governance decisions, not orchestration decisions. |
| Policy waivers or exceptions | High-risk and low-frequency; they need explicit human judgment and audit. |
| Material writes to client or matter systems | The MVP should have no autonomous write actions at all. |
| Broad tool execution | Tool surfaces create prompt-injection, approval, and provenance complexity before core classification is stable. |
| Public release hygiene automation | Cross-repo action amplification is dangerous before pins, manifests, and validation boundaries are mature. |
| Multi-agent planning/executor/critic loops | They increase cost, latency, and trace complexity before you know whether one bounded classifier can already solve the first constraint. |

### Lean applied directly

entity["organization","Lean Enterprise Institute","lean thinking nonprofit"] defines Lean around specifying value from the customer’s standpoint, identifying the value stream, making value-creating steps flow, letting downstream demand pull upstream work, and iterating toward perfection. In parallel, Anthropic’s guidance for agent systems argues for simple, composable patterns before complex architectures. That combination points to a deliberately small orchestrator with one-piece flow and strict pull. citeturn3search0turn3search3turn18search0

For this system, **value** from the user/operator perspective is not “automation.” It is a **correct, reviewable, auditable proposed exception packet** that shortens time to a governed decision without leaking data, skipping approvals, or creating semantic debt. That means a model call that only produces more text is non-value-adding unless it increases the acceptance probability of the packet. citeturn3search7turn3search8turn7search16

| Waste | How it appears here | Lean countermeasure |
|---|---|---|
| Unnecessary model calls | “Thinking harder” with extra loops that do not improve validity | One bounded primary call plus one repair attempt max. |
| Agent chatter | Planner/executor/critic conversations with no new evidence | Single bounded classifier in MVP. |
| Duplicate prompts | Same semantic task implemented in multiple prompt files | Version one canonical task prompt per command. |
| Weak evidence | Packets with labels but no supporting artifacts | Minimum evidence schema and evidence checklist. |
| Unvalidated outputs | Freeform model text passed downstream | Structured outputs plus deterministic validation. |
| Premature tool integration | Adding MCP/connectors before core intake works | Defer external tools and connectors. |
| Unnecessary dashboards | UI before you have reliable underlying telemetry | Append-only JSONL run ledger first. |
| Excessive abstractions | Framework layers with no active bottleneck behind them | Narrow ports/adapters only around contracts, model, ledger, and handoff. |
| Stale context | Contract pins or reference material drifting from runtime | Explicit contract pin recorded per run. |
| Uncaptured decisions | Human edits and approvals not preserved | Append-only decision and approval records in the run ledger. |
| Overproduction | More packets than validators and reviewers can absorb | WIP limits and admission control. |
| Rework | Reviewer correcting route/event mappings repeatedly | Use labeled defect loops and prompt/validator improvements. |

**Flow** means a single exception should move through a single bounded pipeline with minimal waiting and no speculative side branches. **Pull** means the orchestrator should only start runs when the downstream system can absorb them: a valid contract pin exists, a packet can be validated, and reviewer capacity is available. “Perfection” for the small orchestrator means near-zero unauthorized actions, high first-pass validity, low review time, and replayable history—not maximum autonomy. citeturn3search6turn3search9turn18search0

### Six Sigma and DMAIC applied directly

entity["organization","ASQ","quality organization"] describes DMAIC as a structured way to improve an existing process that does not meet performance standards. For the orchestrator, DMAIC should not become a side program; it should be the operating discipline around the run ledger, fixture corpus, and controlled changes. NIST’s Playbook and Manage outcomes reinforce that risk responses, monitoring, error records, version history, and change management should be documented and maintained over time. citeturn3search5turn8search1turn8search5

| DMAIC phase | Applied to LawFirm OS Orchestrator |
|---|---|
| Define | The orchestrator solves one problem first: transforming raw exceptions into contract-pinned, schema-valid, auditable proposed evidence packets with less reviewer effort and fewer defects. |
| Measure | Capture per-run metrics for route/event accuracy, first-pass validation, evidence completeness, abstention rate, reviewer touches, approval latency, model calls, cost, stale-pin defects, duplicate events, and total cycle time. |
| Analyze | Use run ledgers and labeled fixtures to build a Pareto of defects: wrong route, wrong `event_class`, missing evidence, skipped approval, stale contract, duplicate event, false confidence, and budget overrun. |
| Improve | Ship changes as small versioned increments: prompt changes, stricter validators, improved evidence templates, better confidence thresholds, new synthetic cases, or a narrow helper tool if and only if metrics show it reduces the current bottleneck. |
| Control | Lock contract pins, require immutable ledger records, gate all changes through eval fixtures, require explicit approvals for sensitive actions, and maintain version histories for prompts, validators, and integration adapters. |

### Defect taxonomy

The NIST GenAI profile’s treatment of confabulation, OpenAI’s guidance on structured outputs and tool approvals, and LangGraph/OpenAI pause-resume approval models all point to the same thing: the orchestrator needs a crisp defect taxonomy with default fail-closed responses. citeturn19search20turn21search0turn10search1turn20search2turn16search2

| Defect | Class | Detect at | Default response |
|---|---|---|---|
| Wrong `route_id` | Semantic integrity | Enum + fixture comparison + reviewer label | Reject packet; require manual correction and defect tag. |
| Wrong `event_class` | Semantic integrity | Enum + fixture comparison + reviewer label | Reject packet; require correction. |
| Schema-invalid packet | Structural integrity | Deterministic validator | Hard fail. |
| Missing evidence | Evidence integrity | Evidence completeness gate | Hold for manual enrichment or abstain. |
| Policy bypass | Control failure | Policy gate / approval audit | Hard fail and flag. |
| Excessive model calls | Efficiency failure | Budget gate | Terminate run. |
| Tool called without permission | Control failure | Tool policy gate | Hard fail. |
| Hallucinated authority | Semantic/governance failure | Provenance checker / reviewer | Downgrade to hypothesis; require explicit evidence. |
| Duplicate event | Data integrity | Idempotency / canonical hash | Link or reject duplicate. |
| Stale substrate contract | Governance integrity | Pin/hash validation | Hard fail. |
| Untraceable decision | Audit failure | Ledger completeness gate | Reject run as non-admissible. |
| Human approval skipped | Oversight failure | Approval-state audit | Hard fail. |
| Wrong escalation | Routing failure | Escalation policy check | Re-route to manual triage. |
| False confidence | Calibration defect | Confidence vs outcome monitoring | Lower confidence threshold; increase abstentions. |
| Unbounded loop | Runtime defect | Loop counter / elapsed time budget | Hard stop. |
| Cost runaway | Runtime defect | Token/time/cost budget | Hard stop. |
| Context pollution | Context integrity | Context-source labeling / hash mismatch | Rebuild context and restart. |

## Smallest useful architecture

The minimum useful loop is the smallest loop that creates a better downstream decision than the operator would get from a raw exception. OpenAI’s structured-output tooling is directly relevant because it is designed to constrain model outputs to a supplied schema and expose refusals programmatically; Anthropic’s agent guidance is relevant because it argues for workflows before dynamic agents; ABA and NIST are relevant because they make traceability, review, and documentation load-bearing rather than optional. citeturn21search0turn21search1turn18search0turn7search16turn8search1

### Smallest useful loop

| Step | Purpose | Fail-closed condition |
|---|---|---|
| Load pinned substrate contract | Fix the semantic universe for the run | Missing or unresolved contract pin |
| Parse and normalize synthetic input | Create a stable input artifact | Invalid input schema |
| Run one structured classifier | Produce candidate `route_id`, `event_class`, confidence band, and evidence needs | Refusal, invalid schema, invalid enum |
| Validate deterministically | Check enums, schemas, policy, completeness | Any validation error |
| Write immutable run ledger | Preserve provenance and audit trail | Ledger write failure |
| Build proposed evidence packet | Package candidate classification + provenance + evidence refs | Missing required packet fields |
| Optional Exception Lake handoff | Submit to validation-only boundary | Boundary reject or unavailable boundary |
| Label outcome for learning | Feed defect/eval loop | Never blocks the run, but missing labels reduce learning quality |

### Recommended MVP repo structure

```text
lawfirm_os_orchestrator/
  pyproject.toml
  README.md
  src/lawfirm_os_orchestrator/
    __init__.py
    cli.py
    commands/
      classify_exception.py
    domain/
      contracts.py
      packets.py
      runs.py
      defects.py
      metrics.py
      policies.py
      approvals.py
    application/
      orchestrator.py
      classification_service.py
      validation_service.py
      packet_service.py
      ledger_service.py
    ports/
      contract_provider.py
      model_gateway.py
      ledger_writer.py
      exception_lake_gateway.py
      clock.py
      idempotency.py
    adapters/
      substrate_readonly_fs.py
      substrate_readonly_http.py
      openai_structured_gateway.py
      jsonl_ledger_writer.py
      exception_lake_validate_only.py
    prompts/
      classify_exception_v1.md
    schemas/
      input_exception.schema.json
      classifier_output.schema.json
      evidence_packet.schema.json
      run_ledger.schema.json
    examples/
      synthetic_exception_event.json
    evals/
      fixtures.jsonl
      gold_labels.jsonl
      graders.py
  tests/
    unit/
    integration/
```

### First command design

The first command should be exactly as narrow as your prompt suggests:

```bash
python -m lawfirm_os_orchestrator classify-exception \
  --input examples/synthetic_exception_event.json \
  --contract-pin substrate/releases/2026-05-01 \
  --ledger-dir .runs \
  --packet-out .artifacts/proposed_evidence_packet.json \
  --exception-lake-mode validate-only
```

The execution path should be:

1. resolve `--contract-pin` to an immutable substrate release;
2. load allowed route IDs, `event_class` values, packet rules, and validation contracts;
3. normalize the input and hash it;
4. call the model once using a strict structured-output schema;
5. reject if the output contains an unknown enum, unsupported field, refusal, or missing field;
6. validate the candidate against deterministic rules;
7. write an append-only run ledger entry;
8. emit a proposed evidence packet;
9. optionally pass that packet to the Exception Lake validation boundary;
10. record the boundary outcome and stop.

The classifier output schema should be intentionally small:

- `route_id`
- `event_class`
- `confidence_band` (`low|medium|high`)
- `evidence_requirements`
- `abstain_reason` (nullable)
- `reviewer_note` (optional, short)
- `contract_pin_echo`

It should **not** include freeform semantic definitions, route inventions, or any field that could masquerade as authority. OpenAI’s structured-output guidance supports this pattern because schema adherence is stronger than older JSON mode and refusals are explicitly detectable, but NIST’s confabulation warning still means that every structured output must be semantically revalidated. citeturn21search0turn21search1turn19search20

### Metrics model

The metrics model should separate **throughput**, **quality**, **safety/governance**, and **efficiency** so that local speed gains do not hide semantic or audit failures. NIST’s Playbook specifically points toward documented monitoring, error records, system changes, and version history; OpenAI and Anthropic both emphasize evals and trace-level analysis for agent systems. citeturn8search1turn8search5turn9search0turn17search7turn18search6

| Metric family | Metric | Why it matters |
|---|---|---|
| Throughput | Accepted packet rate per reviewer hour | Primary system measure for the MVP |
| Flow | Median cycle time from input to validated packet | Reveals waiting and rework |
| Quality | Exact route match rate | Measures semantic usefulness |
| Quality | Exact `event_class` match rate | Measures semantic usefulness |
| Quality | First-pass validation rate | Measures packet readiness |
| Quality | Evidence completeness score | Measures downstream reviewability |
| Governance | Stale-pin incidence | Detects semantic drift risk |
| Governance | Approval omission rate | Detects oversight failures |
| Governance | Audit completeness rate | Detects inadmissible runs |
| Safety | Tool denial / policy-bypass count | Detects control weakness |
| Efficiency | Median model calls per run | Prevents silent overproduction |
| Efficiency | Median cost per accepted packet | Prevents cost-world local optimization |
| Calibration | High-confidence error rate | Measures false confidence risk |
| Data integrity | Duplicate-event rate | Detects admission waste |
| Improvement | Defect recurrence by version | Shows whether changes actually worked |

### Run ledger fields

| Group | Required fields |
|---|---|
| Identity | `run_id`, `parent_run_id`, `command_name`, `status`, `started_at`, `ended_at` |
| Build / release | `orchestrator_version`, `git_commit`, `prompt_version`, `validator_version` |
| Contract context | `contract_pin`, `contract_hash`, `route_registry_hash`, `schema_bundle_hash` |
| Input provenance | `input_path`, `input_hash`, `input_schema_version`, `synthetic_fixture_id` |
| Model invocation | `provider`, `model_name`, `response_schema_version`, `temperature`, `max_output_tokens`, `call_count` |
| Tool activity | `tool_calls[]`, `tool_policy_mode`, `tool_denials[]` |
| Classification result | `route_id_candidate`, `event_class_candidate`, `confidence_band`, `abstain_reason` |
| Validation | `validation_passed`, `validation_errors[]`, `policy_gate_results[]`, `evidence_completeness_score` |
| Approval | `approval_required`, `approval_status`, `approver_id`, `approval_timestamp`, `approval_reason` |
| Packet outputs | `proposed_packet_hash`, `packet_path`, `idempotency_key`, `duplicate_check_result` |
| Exception Lake handoff | `handoff_mode`, `handoff_attempted`, `handoff_result`, `boundary_reject_reasons[]` |
| Cost / runtime | `elapsed_ms`, `input_tokens`, `output_tokens`, `estimated_cost` |
| Learning | `reviewer_edits`, `final_label_route_id`, `final_label_event_class`, `defect_tags[]` |

### Control gates

| Gate | Input | Pass criteria | Fail behavior |
|---|---|---|---|
| Admission gate | Input artifact + command args | Valid input schema and explicit contract pin present | Reject run |
| Contract gate | Substrate manifests | Pin resolves and hashes match expected artifacts | Reject run |
| Classification gate | Structured model output | Output schema valid; no refusal; enums recognized | Reject or abstain |
| Validation gate | Candidate packet | All deterministic validators pass | Reject packet |
| Policy gate | Planned tool / handoff activity | Action is allowed for this command and context | Reject action |
| Approval gate | Sensitive action or low-confidence result | Explicit approval recorded | Pause or reject |
| Handoff gate | Exception Lake submission | Boundary accepts on validation-only or admit mode | Record reject and stop |
| Control gate | Post-run labels / metrics | Run is complete and admissible for analytics | Exclude from performance metrics |

### Integration contract with Semantic Substrate

| Aspect | Contract |
|---|---|
| Direction | **Read-only** from orchestrator to substrate |
| Orchestrator may read | Pinned release ID, route registry, allowed `event_class` values, schemas, validation contracts, governance boundary metadata, handoff surface definitions |
| Orchestrator must record | Exact contract pin and content hashes in the run ledger and proposed packet |
| Orchestrator must not do | Create or modify route IDs, `event_class` values, schemas, registry entries, or governance rules |
| Required behavior | Hard fail if the pin is missing, unresolved, or internally inconsistent |
| Desirable format | Release manifest with immutable version ID and hashes for each canonical artifact |
| Change model | Substrate changes arrive as versioned releases; the orchestrator only consumes them after explicit adoption |

### Integration contract with Exception Lake Runtime

| Aspect | Contract |
|---|---|
| Direction | Orchestrator writes only through the **Exception Lake validation boundary** |
| Submission unit | Proposed evidence packet plus ledger reference and idempotency key |
| Required packet contents | Contract pin, candidate route/event, provenance, evidence refs, validator results, approval state, packet hash |
| Boundary behavior | Re-validate all inputs independently; never trust the orchestrator as semantic authority |
| MVP mode | `validate-only` by default |
| Orchestrator must not do | Write directly to underlying storage, skip validation, or treat observational evidence as canonical truth |
| Duplicate handling | Boundary should support idempotency/dedup semantics; orchestrator should pre-compute a stable idempotency key |
| Error model | Rejection reason codes should be machine-readable and stored in the run ledger |

## Roadmap by bottleneck

### Do now and defer later

| Do now | Defer later |
|---|---|
| Read-only substrate adapter | General tool marketplace |
| Strict structured classifier | Multi-agent planner/executor networks |
| Deterministic validators | Web UI |
| Append-only JSONL run ledger | Production connectors and client systems |
| Proposed evidence packet builder | Autonomous write actions |
| Validate-only Exception Lake gateway | Distributed queue and event bus |
| Synthetic fixtures and gold labels | Long-running durable engine |
| Hard WIP and cost limits | Dynamic model router |
| Manual approval via terminal or file | Rich human-approval UI |
| Contract pin recording and hash checks | Full observability stack |

### Thirty / sixty / ninety day roadmap

This roadmap is organized around bottlenecks, not features.

| Phase | Bottleneck | Exploit with minimal change | Subordinate other work | Elevate only if needed | Stop condition | Evidence of improvement |
|---|---|---|---|---|---|---|
| First month | Contract-aligned classification defects | Build the CLI, one structured classifier, exact enum validation, packet builder, run ledger, synthetic fixtures | No UI, no connectors, no multi-agent experiments | Add one bounded repair call only if format failures are frequent | Route/event exact-match accuracy and first-pass validation are both stable enough to trust the packet for review | Higher exact-match rate, low schema-failure rate, low abstention surprise |
| Second month | Reviewer touch time | Improve evidence templates, add confidence thresholds, record reviewer edits, improve packet readability | No new tools unless they reduce reviewer edits on the measured corpus | Add terminal approval command and duplicate detection if review is still slow | Reviewer edits and review time fall materially | Lower reviewer edits per packet, faster cycle time, same or better quality |
| Third month | Replayability and control drift | Add deterministic run replay, stricter versioning, policy-gate tests, stale-pin alarms | No production data integration | Add a resumable run abstraction if pause/resume becomes a real bottleneck | Runs are reproducible, stale-pin failures are explicit, and control failures are rare | Zero boundary bypasses, zero stale-pin escapes, stable ledgers |

### One-year roadmap

| Horizon | Bottleneck shift to expect | Architecture move |
|---|---|---|
| Early year | Intake quality remains the constraint | Keep improving fixtures, validators, confidence calibration, and evidence minimums. |
| Mid year | Review latency becomes the constraint | Add a lightweight human-approval terminal/TUI, duplicate detection, and route-specific review templates. |
| Later year | Replay / long-running approval pauses become the constraint | Introduce a durable execution abstraction, then choose a concrete runtime only if pause/resume is genuinely recurring. |
| Late year | Selective context/tool access becomes the constraint | Add an allowlisted read-only tool registry and approval-aware adapter layer. |
| End of year | Operating at higher volume becomes the constraint | Add an event-driven wrapper around the same bounded command semantics, preserving idempotency and contract pins. |

## Future-proofing without premature lock-in

The goal is to preserve optionality while keeping the MVP tiny. Current public tooling is useful, but it should sit **behind your abstractions**, never become the definition of your domain model. OpenAI’s Agents SDK is intentionally small and traceable; the MCP specification is modular and designed around explicit lifecycle/capability negotiation; LangGraph is explicitly low-level and focused on durable execution and HITL; Temporal is built around crash-proof long-running workflows; and entity["organization","OpenTelemetry","observability standard project"] organizes observability around traces, metrics, and logs. Those are powerful ingredients, but none of them should become the semantic source of truth or the legal audit record. citeturn16search5turn15search0turn2search2turn2search4turn20search0turn1search1turn12search6turn12search0

| Capability | Create now | Defer | Lock-in hazard | What preserves optionality |
|---|---|---|---|---|
| OpenAI Agents SDK | `ModelGateway`, `TraceAdapter`, `ApprovalPolicy` interfaces | Using the SDK as the core runtime | Domain state becoming SDK state | Keep your own run ledger, packet schema, and approval record format |
| Model Context Protocol | `ToolRegistry` and `ToolPermissionPolicy` interfaces | Remote MCP servers and connectors | Domain logic depending on MCP tool names or transports | Treat MCP as an adapter concern only |
| LangGraph from entity["company","LangChain","ai framework company"] | `RunState`, `Interrupt`, and `CheckpointRef` abstractions | Concrete graph runtime adoption | Business continuity depending on opaque graph checkpoints | Keep resumable business state in your own schema |
| Durable execution via entity["company","Temporal Technologies","workflow platform company"] or similar | Idempotent commands, stable run IDs, replay-safe steps | Workflow engine adoption | Event history becoming the only audit record | Keep the orchestrator ledger authoritative and engine traces secondary |
| Human-in-the-loop | Approval request / decision schema | Rich approval UI | Approval semantics hard-coded into a specific product | Store approvals as portable records |
| Tracing / observability | Stable trace IDs, span names, and metric names | Vendor dashboards | Only the vendor dashboard knows what happened | Emit traces, metrics, and logs from your own events |
| Evaluations | Synthetic fixtures, gold labels, gradable outcomes | Large eval platform integration | Eval data tied to one SaaS product | Keep fixtures in-repo and outcome labels portable |
| Model routing | `ModelSelectionStrategy` interface | Learned or dynamic routers | Architecture shaped around provider-specific routing heuristics | Start with one model and explicit substitution |
| Tool permissions | Static allowlist manifest | Dynamic per-user tool routing | Hidden permission logic in prompts | Keep permissions as code/config, not natural-language-only policy |
| Event-driven orchestration | Idempotent command envelope | Message bus / worker fleet | Queue semantics becoming business semantics | Preserve one bounded run contract whether invoked by CLI or event |

## Risk register

| Risk | Why it matters | Early signal | Mitigation |
|---|---|---|---|
| Source-of-truth inversion | The orchestrator starts behaving like a semantic authority | Runtime invents route IDs or accepts unknown enums | Read-only substrate adapter; hard enum validation |
| Governance bypass | Boundary assumptions erode | Packets appear downstream without full validation history | Exception Lake validation-only gateway and ledger checks |
| Approval overload | Reviewers become the new bottleneck | Rising queue depth and longer approval latency | Better packet quality, confidence thresholds, route templates |
| Prompt injection through future tools | Untrusted content influences actions | Tool arguments echo untrusted instructions | Keep tools off in MVP; later structured fields + approvals only |
| False confidence | Incorrect packets look “clean” | High-confidence error rate | Confidence calibration and abstain path |
| Stale contract pins | Runs use outdated semantics | Rising stale-pin failures or route mismatches | Explicit pins, hashes, manifest checks |
| Cost runaway | Agent loops consume budget with little value | Model-call count and cost per packet rise | Hard budgets, no fan-out loops |
| Context pollution | Wrong facts enter the run | Reviewer notes “where did this come from?” | Hashable context bundle and strict source labeling |
| Duplicate events | Same exception is proposed repeatedly | Increased duplicate-detection hits | Stable idempotency key and dedup logic |
| Audit gap | A decision cannot be reconstructed | Missing approval or provenance fields | Ledger completeness gate |
| Framework lock-in | Runtime choice dictates semantics | Business rules mirror framework primitives | Domain-first schemas and adapter boundaries |
| Release hygiene failure | Cross-repo changes break compatibility | Handoff rejects spike after releases | Explicit release manifests, validate-only smoke tests |

## Final recommendation

The **first bottleneck** this orchestrator should attack is **the conversion of raw exception input into a contract-pinned, route-valid, `event_class`-valid, evidence-sufficient proposed packet that a reviewer can accept or reject quickly**. That is the true leverage point because it sits directly in front of scarce human review capacity and directly on top of your governance boundary. If you improve anything else first, you risk creating faster waste. citeturn4search0turn3search0turn18search0turn7search16

The **smallest architecture** that attacks that bottleneck without creating new ones is:

- a **local-first Python CLI**;
- a **read-only Semantic Substrate adapter** that loads an explicit contract pin;
- **one structured-output classifier** with a narrow JSON schema;
- **deterministic enum/schema/policy validators** that fail closed;
- an **append-only run ledger**;
- a **proposed evidence-packet builder**;
- an **optional Exception Lake validate-only gateway**;
- **no autonomous writes**, **no web app**, **no client data**, **no connectors**, **no agent swarm**, and **no framework-owned business state**.

In practical terms, that means the orchestrator should start life as a **bottleneck-protecting packet factory**, not as a “smart agent platform.” Once packet validity and reviewer throughput are no longer the constraint, then—and only then—you should elevate the next bottleneck with approvals UX, replayability, limited tool access, or durable execution. citeturn21search0turn17search2turn15search0turn20search0turn12search6

## Sources

The most important public sources used in this report were:

- ABA Formal Opinion 512 and related ABA coverage, for legal obligations around competence, confidentiality, supervision, communication, review, and reasonable fees in generative-AI-assisted practice. citeturn7search16turn7search5
- NIST AI RMF 1.0, the NIST AI RMF Playbook, and the NIST Generative AI Profile, for governance, documentation, monitoring, risk response, TEVV orientation, and confabulation risk. citeturn0search3turn8search0turn8search1turn8search5turn8search2turn19search20
- TOCICO materials on the Five Focusing Steps, throughput-vs-cost-world thinking, and DBR/buffer management, for constraint-centered system design. citeturn4search0turn4search1turn6search1turn5search6
- Lean Enterprise Institute materials on value, value-stream mapping, flow, pull, and perfection, for waste elimination and pull-based orchestration. citeturn3search0turn3search8turn3search9turn3search6
- ASQ’s DMAIC overview, for the Define/Measure/Analyze/Improve/Control operating discipline. citeturn3search5
- Anthropic’s “Building effective agents,” for the recommendation to begin with the simplest workable workflow and add complexity only when justified. citeturn18search0
- OpenAI documentation on structured outputs, agents, traces, evals, tool approvals, and agent safety, for bounded model calls, schema-constrained outputs, HITL, and observability. citeturn21search0turn21search1turn15search0turn9search0turn17search2turn10search1turn16search2
- The Model Context Protocol specification, for future tool integration via modular lifecycle and capability negotiation rather than domain-layer coupling. citeturn2search2turn2search4
- LangGraph documentation on low-level orchestration, durable execution, and interrupts/HITL, for optionally resumable future workflows. citeturn20search0turn1search1turn20search2
- Temporal documentation and OpenTelemetry concepts, for future durable execution and observability patterns that should remain subordinate to your own ledger and packet schemas. citeturn12search6turn12search0