# Litigation Simulation Adapter Execution Plan

Status: future execution-plane plan; no connector is implemented.

## Authority

This repo consumes the Substrate boundaries read-only:

- `../LawFirm-os-semantic-substrate/governance/LITIGATION_SIMULATION_ADAPTER_BOUNDARY.md`
- `../LawFirm-os-semantic-substrate/governance/REAL_WORK_SHADOW_MODE_PILOT_GATES.md`

The Orchestrator may later host a local no-write adapter runner for Albers
mock-trial style tools, ALS simulator tools, or other litigation simulation
systems only after Substrate approves the contract shape. This document does
not authorize any simulator call, model call, connector call, external write,
Lake write, SQLite write, production automation, real client data use, trial
strategy reliance, settlement authority, conflict clearance, matter opening,
or budget submission.

## Future Adapter Shape

A future adapter should produce a local reviewer packet with:

- simulator name and version;
- input schema sketch;
- output schema sketch;
- synthetic fixture references;
- jurisdiction and practice-area assumptions;
- source-binding and provenance notes;
- attorney review checklist;
- blocked actions;
- eval results;
- rollback or kill-switch notes.

The first runnable command, if approved later, should be synthetic-only and
no-write. It should resemble the intake vertical-slice demo pattern: check
sibling governance surfaces, build local review artifacts, and stop as
`blocked_pending_attorney_and_owner_review`.

## Required Stop Conditions

Stop before implementation or execution if:

- the simulator requires real client or matter data;
- the simulator stores privileged material or vendor traces without approval;
- the workflow would send or publish output externally;
- a user wants the simulator output treated as legal advice, trial strategy,
  settlement authority, conflict clearance, budget approval, or matter-opening
  authority;
- Substrate has not approved the local contract shape;
- the real-work shadow-mode gates are not satisfied.

## Open Questions

- Which exact Albers and ALS simulator products, versions, and terms apply?
- What data retention, training, trace, and deletion controls do they provide?
- Which jurisdiction, practice area, and matter stage should be in scope?
- Which attorney role reviews outputs before any reliance?
- Which synthetic fixtures prove the adapter is useful before real-work review?
