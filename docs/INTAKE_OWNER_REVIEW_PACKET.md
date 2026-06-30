# Intake Owner Review Packet

Status: `candidate_execution_artifact`

`lawfirm-os-orchestrator intake prepare-owner-packet` turns a synthetic intake owner-review request into local review artifacts:

- `intake_owner_review_packet.json`
- `carrier_rejection_report.json`
- `budget_actuals_variance_report.json`
- `exception_lake_handoff_preview.json`
- one local JSONL ledger line

The packet is not a promoted workflow contract. It is an execution-plane proof that the Orchestrator can own the outer intake-to-budget gates without creating canonical route IDs, event classes, budget approval authority, matter-opening authority, connector authority, or Exception Lake write authority.

## Controls

- synthetic-only input;
- raw client, matter, privileged, or production transcript fields fail closed;
- human pauses remain required for matter family, posture, principal party roles, budget external submission, and Lake handoff;
- missing budget preconditions block the packet;
- every carrier rejection notice lands in a known candidate bucket or `unknown_or_new_rejection_pattern`;
- appeal/fix action remains blocked without human authorization;
- appeal results append as outcome records;
- budget actuals variance compares proposed, carrier-compliant projection, approved-if-known, actual, and write-down/disallowed amounts by phase and task;
- Lake handoff is preview-only with `lake_write_authority_now=false`.

The packet also records that no promoted intake-to-budget decision model exists in the current substrate seed registry. That keeps the artifact reviewable as owner-docket evidence while preventing it from becoming a decision-ready request.
