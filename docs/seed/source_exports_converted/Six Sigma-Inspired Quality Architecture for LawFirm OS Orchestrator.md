# Six Sigma-Inspired Quality Architecture for LawFirm OS Orchestrator

## Design premise

A Six Sigma-like orchestrator should treat orchestration as a controlled
process, not as a pile of model calls. DMAIC from
ASQ[\[1\]](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf) is
meant to improve existing processes that miss performance expectations;
the AI RMF from the National Institute of Standards and
Technology[\[2\]](https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_)
expects risk management to be continuous, iterative, and documented
across the AI lifecycle; machine-readable API contracts such as those
defined by the OpenAPI
Initiative[\[3\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
make interfaces explicit; and an observability framework such as
OpenTelemetry[\[4\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
makes traces, metrics, and logs first-class telemetry. For LawFirm OS,
that implies a three-plane quality design: keep the **Semantic
Substrate** canonical and slow-changing, keep the **Orchestrator**
fast-changing but contract-bound, and make the **Exception Lake
Runtime** the immutable evidence layer for every material decision,
validation result, override, incident, and recovery step.
[\[5\]](https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t)

The practical definition of quality should be narrow enough to automate.
In this architecture, a **defect** is any deviation from a declared
contract, risk policy, approval rule, evidence obligation, or CTQ
threshold at the level of a run, state transition, tool call,
model/router decision, human handoff, or audit record. If the
orchestrator cannot prove that a step is allowed, well-formed, and
adequately evidenced, it should **fail closed**: stop, downgrade, or
hand off to a human rather than continue optimistically. That aligns
with default-deny control guidance, AI RMF guidance on risk tolerance
and documented knowledge limits, and the requirement that some AI
configurations explicitly require human oversight and safe failure
behavior.
[\[6\]](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf)

## DMAIC and AI RMF operating model

The right mental model is that **DMAIC is the improvement backbone** and
**Govern/Map/Measure/Manage is the operating control layer**. DMAIC
tells LawFirm OS how to improve the orchestrator over time; the AI RMF
tells it what must be governed, contextualized, measured, and managed
during runtime and promotion.
[\[7\]](https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t)

**DMAIC mapping table for LawFirm OS Orchestrator**

| DMAIC phase | Orchestrator purpose                                                     | Small-start implementation                                                                                   | Evidence written to Exception Lake                                         |
|-------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Define      | Define what “good orchestration” means for each task class and risk tier | Versioned task charter, protected state list, CTQ set, defect taxonomy, approval matrix                      | Charter version, CTQ baseline, risk-tier mapping, policy references        |
| Measure     | Instrument every run and controlled step                                 | Immutable run ledger, traces, metrics, logs, validation results, exception events                            | Per-run metrics, per-tool metrics, state path, validator outputs           |
| Analyze     | Determine dominant defect modes and causes                               | Weekly Pareto by defect class, cohort slicing by model/prompt/router/tool, trace replay dossiers             | Defect clusters, recurrence rates, blast radius, suspected causal surfaces |
| Improve     | Change the orchestrator without mutating canon                           | Shadow tests, canary rules, prompt patches, router policy changes, validator additions, handoff rule changes | Proposal objects, test results, approval decisions, rollback data          |
| Control     | Keep the process in a known state                                        | Runtime gates, baselines, control charts, release approvals, rollback triggers                               | Gate results, out-of-control signals, promotion/rollback records           |

The AI RMF mapping below specializes that operating model for agentic
orchestration, especially around human oversight, source verification,
third-party dependencies, incident handling, and post-deployment
improvement.
[\[8\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)

**NIST AI RMF mapping table**

| AI RMF function | What it means in the orchestrator                                                                                                | Primary controls                                                                                                    |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Govern          | Establish ownership, policies, risk tolerance, change control, separation of duties, and approval authority                      | Risk tiers, tool allowlists, contract registry, promotion board, dual-authorization for protected changes           |
| Map             | Understand context, legal/task impact, knowledge limits, third-party dependencies, and where human oversight is required         | Task classification, matter classification, protected transitions, domain-coverage matrix, dependency registry      |
| Measure         | Measure trustworthiness and runtime behavior in deployment-like and deployed conditions                                          | Validation pass rates, defect rates, source-verification rates, override rates, evidence completeness, latency/cost |
| Manage          | Act on measured risks with monitoring, appeal/override, incident response, recovery, decommissioning, and continuous improvement | Exception workflows, rollback triggers, handoff queues, canary promotion rules, retirement/fallback rules           |

For a legal orchestrator, the GenAI profile is especially useful because
it explicitly calls for well-defined contracts and SLAs, minimum
incident-reporting criteria, source and citation verification,
monitoring of overrides, continuous monitoring of third-party systems,
and sharing pre-deployment test results with release-approval
authorities.
[\[9\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

## Defect definition and critical-to-quality attributes

The orchestrator’s CTQs should be derived from trustworthy-AI attributes
and then decomposed into operational measurements. In practice, LawFirm
OS should not define quality primarily as “the model sounded plausible.”
It should define quality as **contract conformance, protected autonomy,
reliable legal grounding, complete evidence, safe escalation, and
controlled economics**. That is consistent with CTQ flowdown, which
turns strategic objectives into measurable CTQs, and with the AI RMF
trustworthiness characteristics of validity/reliability, safety,
security/resilience, accountability/transparency, explainability,
privacy, and fairness.
[\[10\]](https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_)

**Orchestration defect taxonomy**

| Defect class                   | What counts as a defect                                           | Typical examples                                                                                      | Default containment                             |
|--------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Intake and contract defects    | Input or output violates declared schema/contract                 | Missing matter ID, malformed request, schema mismatch, unsupported intent                             | Block run before planning                       |
| State-transition defects       | Transition violates allowed state machine or approval rules       | Skipped review, duplicate completion, out-of-order publish, silent retry loop                         | Freeze transition and write exception           |
| Routing defects                | Wrong agent/model/tool path for the task/risk tier                | Research model used for filing-ready draft, router ignores protected state                            | Re-route or hand off                            |
| Tool invocation defects        | Tool call violates authz, contract, scope, or side-effect policy  | Unauthorized tool, missing idempotency key, invalid parameters, external side effect without approval | Deny call and record failed authorization       |
| Grounding and evidence defects | Output lacks verifiable support or required runtime evidence      | Unverifiable citation, missing source bundle, missing trace linkage, missing exception record         | Mark run defective even if outcome looks useful |
| Output-quality defects         | Result is materially incorrect, incomplete, or unsafe for context | Fabricated authority, wrong client entity, omitted mandatory clause, stale law                        | Require rework or human review                  |
| Human-governance defects       | Handoff or approval process fails policy                          | Approval bypass, wrong approver role, insufficient approval packet, unresolved override               | Lock protected transition                       |
| Security and privacy defects   | System crosses governance boundary or leaks information           | Cross-matter leakage, prompt injection success, sensitive-data exposure, secret exfiltration          | Stop run, elevate severity, isolate surface     |
| Auditability defects           | Records cannot reconstruct what happened                          | Missing timestamps, missing versions, non-correlated logs, absent actor identity                      | Treat as process defect regardless of outcome   |
| Economic control defects       | Process exceeds bounded operating envelope                        | Runaway retries, cost explosion, latency breach, tool-thrashing                                       | Abort or degrade to smaller/simpler path        |

For a law-firm setting, one important quality choice is that **missing
evidence is itself a defect**. The GenAI profile explicitly emphasizes
content provenance, source/citation review, incident criteria, and
records that preserve sources, timestamps, and metadata; the AI RMF also
treats documentation and tracking over time as part of trustworthy
operation.
[\[11\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

**Critical-to-quality attributes for the orchestrator**

| CTQ attribute                    | Operational meaning                                                                     | Primary measures                                                            |
|----------------------------------|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Contract conformance             | Every ingress, egress, state transition, and tool call is schema-valid and policy-valid | Validation pass rate, contract-failure rate                                 |
| Legal grounding                  | Material claims are supported by approved evidence paths                                | Citation/source verification pass rate, unsupported-claim rate              |
| Controlled autonomy              | The system stays inside its authorized action envelope                                  | Unauthorized transition rate, approval-bypass rate                          |
| Provenance completeness          | A reviewer can reconstruct what happened end-to-end                                     | Evidence completeness score, missing-audit-field rate                       |
| Human-governed finality          | High-impact transitions have the right human in the loop                                | Mandatory-approval compliance, time-to-handoff, override outcomes           |
| Security and privacy containment | Runs do not cross matter, tenant, or secret boundaries                                  | Leakage incidents, policy-denial counts, injection-success rate             |
| Recovery and resilience          | Defects are contained without cascading failures                                        | Retry success after safe recovery, rollback rate, incident containment time |
| Timeliness and cost discipline   | Quality is achieved inside bounded operating envelopes                                  | Median and p95 latency, cost per run, rework rate                           |

## Metrics model and run ledger

A CTQ only becomes actionable when it is turned into measurements, and
observability in software depends on traces, metrics, and logs that
share context. The right metrics model for LawFirm OS is hierarchical: a
few executive measures from day one, plus deeper measures at the run,
tool, prompt, router/model, and human-handoff levels. AI RMF measurement
guidance also stresses documented metrics, tracking risks over time, and
evaluating performance in conditions similar to deployment and in
ongoing monitoring.
[\[12\]](https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_)

**Metrics to track from day one**

| Metric                                            | Definition                                                                     | Why it matters                                |
|---------------------------------------------------|--------------------------------------------------------------------------------|-----------------------------------------------|
| Defect rate per 1,000 orchestration opportunities | Defects / controlled steps                                                     | Single headline quality measure               |
| Run defect rate                                   | Defective runs / total runs                                                    | Executive quality view                        |
| Fail-closed rate                                  | Runs stopped or downgraded by policy/validation                                | Shows whether controls are actually enforcing |
| Validation failure rate                           | Failed validations / attempted validations                                     | Early warning on contracts and prompts        |
| Evidence completeness score                       | Required evidence fields present / required fields                             | Measures audit readiness                      |
| Mandatory-approval compliance                     | Protected transitions with required approval / protected transitions attempted | Shows governance integrity                    |
| Citation/source verification pass rate            | Verified legal claims / claims requiring verification                          | Critical for legal usefulness                 |
| Tool authorization denial rate                    | Denied tool calls / requested tool calls                                       | Indicates pressure against policy boundaries  |
| Human handoff median time                         | Median elapsed time from handoff creation to decision                          | Measures operational practicality             |
| Median and p95 latency                            | End-to-end runtime timing                                                      | Detects process instability                   |
| Median cost per completed run                     | All inference/tool costs / completed runs                                      | Prevents silent economic drift                |
| Rework rate                                       | Runs reopened, retried, or re-routed after initial completion path             | Captures hidden quality loss                  |

An **orchestration opportunity** should be explicitly counted. In
practice, that means every controlled step where quality can fail:
ingress validation, plan validation, router decision, model decision,
tool authorization, tool result validation, protected state transition,
human handoff, egress validation, and evidence write. This makes defect
density measurable without pretending the model itself is the unit of
quality.
[\[13\]](https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t)

**What to measure by scope**

| Scope                     | Must-measure items                                                                                                                                                                                                                                                       |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Per run                   | Run ID; matter/task class; risk tier; orchestrator/router/policy versions; state path; outcome class; defect count by class; total latency; total cost; evidence completeness; protected transitions attempted; approvals required/obtained; exception count by severity |
| Per tool call             | Tool ID/version; contract version; authorization outcome; side-effect class; args-hash; latency; retries; timeout/error code; result-validation outcome; evidence reference; rollback/compensation outcome if applicable                                                 |
| Per prompt version        | Invocation count by task cohort; validation-failure rate; unsupported-claim rate; citation-verification rate; human-override rate; rework rate; completion rate; median latency/cost; rollback frequency after promotion                                                 |
| Per model/router decision | Candidate set; selected model/tool path; reason code; predicted risk tier; actual defect outcome; human override afterward; domain-shift warning; cost/latency delta versus baseline; “regret” rate when later re-routed or defected                                     |
| Per human handoff         | Trigger reason; mandatory vs discretionary; approver role; packet completeness; time to accept; time to resolve; approve/deny/modify outcome; downstream success rate; prevented-defect estimate                                                                         |
| Per cohort                | Slice every major measure by task class, matter type, risk tier, orchestrator version, and prompt/model/router version to avoid misleading averages                                                                                                                      |

One especially important rule is **never compare prompts or models
across mixed cohorts**. Prompt Version A may look “better” only because
it handled low-risk research runs and Prompt Version B handled protected
drafting transitions. Stratification by task class and risk tier is
mandatory if the metrics are going to inform promotion decisions. That
follows directly from the AI RMF emphasis on context, mapped knowledge
limits, and context-specific measurement.
[\[14\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)

**Audit fields**

| Field group             | Minimum fields                                                                                                                 |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Identity                | run_id, parent_run_id, matter_id, tenant_id, actor_type, actor_id                                                              |
| Event core              | event_type, event_time, source_component, target_component, outcome, severity                                                  |
| Versioning              | orchestrator_version, router_version, prompt_version(s), model_version, tool_version, policy_pack_version, contract_version(s) |
| Decision context        | task_class, risk_tier, reason_code, requested_transition, resulting_transition                                                 |
| Validation              | validator_id/version, phase, result, violations, recovery action                                                               |
| Human governance        | approval_required, approver_role, decision, response_time, override_reason                                                     |
| Evidence and provenance | trace_id, span_id, correlation_id, source_refs, artifact hashes, Exception Lake refs                                           |
| Economics               | tokens_in, tokens_out, tool_latency_ms, total_latency_ms, cost_usd, retry_count                                                |
| Incident context        | title, reporter, date of incident, description, impact(s), stakeholders impacted                                               |

**Run ledger schema draft**

    run_ledger:
      run_id: uuid
      parent_run_id: uuid | null
      matter_id: string
      tenant_id: string
      task_class: string
      risk_tier: low | medium | high | protected
      requested_outcome: string

      states:
        start_state: string
        end_state: completed | blocked | handed_off | aborted
        transition_path: [string]

      versions:
        orchestrator_version: string
        router_version: string
        policy_pack_version: string
        prompt_bundle_versions: [string]
        model_version: string

      contracts:
        input_contract_id: string
        output_contract_id: string
        state_machine_version: string
        tool_contract_ids: [string]

      trace:
        trace_id: string
        span_id: string
        correlation_id: string

      decisions:
        - decision_type: route | model_select | tool_select | transition
          reason_code: string
          rationale_hash: string
          predicted_risk_tier: string
          realized_outcome_ref: string

      validations:
        - validator_id: string
          validator_version: string
          phase: ingress | planning | tool_pre | tool_post | transition | egress
          result: pass | fail | warn
          violation_codes: [string]
          containment_action: string

      tool_calls:
        - tool_call_id: uuid
          tool_id: string
          tool_version: string
          authz_scope: string
          side_effect_class: none | internal | external
          args_hash: string
          latency_ms: integer
          retry_count: integer
          result_validation: pass | fail | warn
          evidence_ref: string

      human_handoffs:
        - handoff_id: uuid
          trigger_reason: string
          required: boolean
          approver_role: string
          decision: approve | deny | modify
          response_ms: integer
          override_reason: string | null

      exceptions:
        - event_id: uuid
          event_type: string
          defect_class: string
          severity: low | medium | high | critical
          detected_at: timestamp
          source_component: string
          impacted_transition: string | null
          description: string
          impact_summary: string
          containment_action: string
          exception_lake_ref: string

      metrics:
        total_latency_ms: integer
        llm_tokens_in: integer
        llm_tokens_out: integer
        tool_latency_ms: integer
        cost_usd: decimal
        defect_count: integer
        evidence_completeness_score: decimal

      artifacts:
        source_refs: [string]
        output_hash: string
        artifact_refs: [string]

      timestamps:
        started_at: timestamp
        ended_at: timestamp

Those fields are intentionally shaped by four authoritative patterns:
AU-3 audit-record content, AU-12-style event generation and
cross-component auditability, the GenAI profile’s minimum
incident-report fields, and provenance records that preserve sources,
timestamps, and metadata.
[\[15\]](https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf)

## Control gates and auditability

Uncontrolled agent behavior is prevented by making **authority explicit
and layered**. The orchestrator should default to deny, grant only the
least privilege needed for the current state, separate roles that can
request, approve, and promote changes, and require positive
authorization for protected transitions. The AI RMF also requires
documented human oversight where appropriate, while NIST change-control
guidance supports access restrictions, review, testing, and even dual
authorization for selected changes.
[\[16\]](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf)

**Control gates**

| Gate                      | What it checks                                                                                     | Fail-closed outcome                               | Evidence captured                  |
|---------------------------|----------------------------------------------------------------------------------------------------|---------------------------------------------------|------------------------------------|
| Ingress contract gate     | Request schema, task type, matter binding, tenant/matter permissions                               | Reject request or downgrade to intake review      | Input validation record            |
| Context and risk gate     | Task class, impact class, protected-state eligibility, domain coverage                             | Reclassify to higher risk or require human triage | Risk assessment record             |
| Plan gate                 | Plan shape, allowed branching, max steps, budget envelope, mandatory validators                    | Block autonomous execution                        | Plan validation record             |
| Route/model gate          | Approved model family, allowed capability set, domain/risk fit, reason code present                | Re-route to safer/default path                    | Router decision record             |
| Tool authorization gate   | Tool allowlist, contract version, authz scope, side-effect class, idempotency requirements         | Deny tool call                                    | Tool authz event                   |
| Tool result gate          | Output schema, side-effect confirmation, compensation path if external action failed               | Block downstream transition                       | Tool post-validation record        |
| Protected transition gate | Requested move into client-visible, signatory, filing, disclosure, or other protected state        | Freeze transition pending approval                | Transition validation record       |
| Human approval gate       | Correct approver role, complete packet, reason code, approval SLA                                  | Hand off and hold state                           | Approval packet + decision         |
| Egress and evidence gate  | Output schema, required sources, required audit fields, trace completeness, exception completeness | Do not emit final output                          | Final validation + ledger closeout |

The orchestrator’s equivalent of a control chart should be an
**Orchestration Stability Chart**. Start with two charts per cohort: a
**p-chart** for the fraction of defecting runs and an **individuals
chart** for single-run latency, realized risk score, or cost. Add
separate p-charts for evidence incompleteness, approval bypass, and
unverifiable-citation rates. Use historical in-control baselines and
investigate special-cause signals instead of patching reactively.
[\[17\]](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm)

The orchestrator’s equivalent of root-cause analysis should be a **Trace
Replay Dossier**. Reconstruct the run from the time-correlated audit
trail; produce a Pareto ranking of defect classes or contributing
factors; and then complete a fishbone that forces analysis across
prompt, router, model, tool, retrieval, policy, human handoff, and
contract surfaces. In a legal system, this should be paired with version
diffs and evidence diffs so the reviewer can see whether the defect came
from a bad rule, a bad route, a missing source, or a missing approval.
[\[18\]](https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf)

## Improvement loop and rollout path

The improvement loop should convert runtime defects into **bounded
proposals against the orchestrator**, not silent mutation of the
Semantic Substrate. The AI RMF Manage function expects post-deployment
monitoring, appeal and override, incident response, recovery, change
management, and measurable continual improvement; the GenAI profile adds
source verification, monitoring of overrides, monitoring of third-party
systems, and active-learning style identification of failures or
unexpected outputs.
[\[19\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)

**Example defect → exception event → pressure vector → proposal path**

| Stage              | Example                                                                                                                                                                                                                                               |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Defect             | A litigation-drafting run reaches `draft_ready` with one fabricated citation and no verified source bundle                                                                                                                                            |
| Exception event    | `output.citation_verification_failed`; defect_class=`grounding`; severity=`high`; impacted_transition=`validated -> draft_ready`; source_component=`egress_validator`                                                                                 |
| Pressure vector    | Over 14 days, this defect clusters in `task_class=litigation_brief`, `prompt=v12`, `router_rule=fast_lit_draft`, `model_family=general_large`, with elevated rework and human overrides                                                               |
| Proposal           | Keep canon unchanged; change the orchestrator by requiring citation-verifier pass before `draft_ready`, routing litigation briefs to retrieval-backed path, and forcing human approval before any transition into `client_visible` or `ready_to_file` |
| Validation         | Shadow on prior failing traces, canary on low-volume live cohort, compare defect rate, latency, cost, and override rate against baseline                                                                                                              |
| Promotion decision | Promote only if defect rate drops without CTQ regressions and rollback remains available                                                                                                                                                              |

The “pressure vector” is the mechanism that turns noisy exception data
into a ranked improvement signal. A good pressure vector includes the
affected surface, cohort, recurrence, impact, detectability, confidence,
candidate causes, and the smallest plausible intervention. If the
evidence points to an orchestrator issue, fix the orchestrator. If it
points to an ambiguity or gap in canonical semantics, open a governed
semantic-change request instead of mutating canon at runtime. That is
exactly the kind of disciplined change control that NIST expects for
controlled systems.
[\[20\]](https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf)

**What may auto-improve versus what requires a promotion decision**

| Surface              | Auto-improve allowed                                                                                                             | Promotion decision required                                                                        |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Telemetry            | Add non-sensitive log fields, new counters, new traces, new dashboards                                                           | Changes that remove required audit fields or reduce evidence completeness                          |
| Runtime tuning       | Retry/backoff values, timeout ceilings, cache TTL, retrieval top-k, low-risk ranking weights, but only inside approved envelopes | Any change that expands privileges, adds side effects, or changes protected-state reachability     |
| Prompts              | Low-impact internal summarization wording after shadow validation and rollback path                                              | Any prompt for client-visible, signatory, filing, disclosure, or other protected outputs           |
| Router rules         | Low-risk tie-break tuning for already-approved candidate set                                                                     | Any change to risk-tier routing, domain coverage, model family, or protected transition behavior   |
| Tools                | None beyond metadata or observability refinements                                                                                | New tool, new permission, new authz scope, new side-effect surface, changed tool contract          |
| Validators           | Threshold tuning within pre-approved range                                                                                       | New validator logic that changes pass/fail semantics on protected paths                            |
| Governance artifacts | None                                                                                                                             | Approval matrix, state machine, policy pack, contracts, schemas, registries, governance boundaries |

The governing rule is simple: **auto-improvement may optimize within a
pre-approved envelope, but it may not expand authority, alter canon, or
change protected-path semantics**. Changes that affect trust boundaries,
legal exposure, or allowed side effects need explicit promotion and, for
the most sensitive paths, dual authorization and release-approval
review. [\[21\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

**MVP quality gates**

| Capability area        | MVP quality gates                                                                                       | Enterprise quality gates                                                                               |
|------------------------|---------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Contracts              | Input/output schemas for every run type; tool contracts for every tool call                             | Full contract registry with compatibility rules, schema diffs, and automated conformance tests         |
| Runtime control        | Ingress, tool-authz, protected-transition, and egress gates                                             | Full gate stack plus plan gate, compensation controls, and continuous policy simulation                |
| Human oversight        | Mandatory approval for client-visible, signatory, filing, disclosure, and irreversible external actions | Tiered approval policies, escalation trees, delegation rules, and override analytics                   |
| Evidence               | One immutable run ledger and one exception schema                                                       | Cross-system evidence reconciliation, retention policies, tamper alarms, and lineage search            |
| Metrics                | Day-one metrics, cohort slicing by task and risk                                                        | Full CTQ scorecards, drift/regret analytics, portfolio rollups, and per-practice-area baselines        |
| Root-cause analysis    | Weekly Pareto + trace replay review                                                                     | Automated defect clustering, causal dashboards, experiment tracking, and controlled replay labs        |
| Promotion              | Manual promotion board for prompt/router/policy/model changes                                           | Formal change advisory board, canary automation, dual authorization, signed releases, auto-rollback    |
| Third-party/model risk | Basic vendor/tool inventory and fallback list                                                           | Continuous third-party monitoring, supplier scorecards, provenance testing, and contingency rehearsals |

A sensible small-start build is therefore not huge: one contract
registry, one state machine with protected states, one immutable run
ledger, one exception schema, a small policy pack with risk tiers, and a
weekly quality review that only promotes bounded improvements. That is
enough to make the Orchestrator measurable, controlled, auditable,
defect-aware, and continuously improvable without turning the Semantic
Substrate into a runtime mutation surface.
[\[22\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)

[\[1\]](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf)
[\[6\]](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf)
[\[16\]](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf)
https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf

<https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf>

[\[2\]](https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_)
[\[10\]](https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_)
[\[12\]](https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_)
https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb\_

<https://asq.org/quality-resources/articles/the-ctq-flowdown-as-a-conceptual-model-of-project-objectives?id=45e5a2c29ed648ea92010a3bd05dfeea&srsltid=AfmBOoo1RkLEBwkKcBHAroos9x26FSzqQpH0SYof105Y_YQwGv9kuOb_>

[\[3\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
[\[8\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
[\[14\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
[\[19\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
[\[22\]](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf

<https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf>

[\[4\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
[\[9\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
[\[11\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
[\[21\]](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

<https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf>

[\[5\]](https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t)
[\[7\]](https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t)
[\[13\]](https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t)
https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t

<https://asq.org/quality-resources/dmaic?srsltid=AfmBOoro-BbImSYghKBKg7kwEptDWiWfeVs3TVbi7AkYdIGvQcCiYt9t>

[\[15\]](https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf)
[\[18\]](https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf)
[\[20\]](https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf)
https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf

<https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf>

[\[17\]](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm)
https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm

<https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm>
