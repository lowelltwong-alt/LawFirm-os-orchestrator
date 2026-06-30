# Intake Orchestrator Adoption Review

## Purpose

This is an Orchestrator-owned review docket for the intake-to-budget vertical proposals emitted by `LawFirm-os-intake`. It records what this repo should review next, not what is already promoted.

The docket is candidate-only. It does not create canonical route IDs, event classes, schemas, connector authority, Lake admission authority, budget approval authority, or appeal-submission authority.

## Source Package

Read-only source: `LawFirm-os-intake:promotion/cross_repo_promotion_package.json`.

The current Orchestrator review items are:

- `orchestrator.workflow-human-pauses-evidence-packet.v0_1`
- `orchestrator.carrier-rejection-capture-appeal.v0_1`

The local registry is `registry/intake-orchestrator-adoption-review-registry.json`.

## Intake-To-Budget Workflow Ownership

Future Orchestrator adoption should decide one outer runtime owner for:

- source inventory and source-bound evidence preservation;
- human confirmation pauses for matter family, posture, principal party roles, and budget approval;
- missing-budget-precondition blocks;
- evidence packet assembly;
- run ledger integrity;
- disabled or validate-only Lake handoff until Lake contracts are promoted.

Observed evidence, practice-context priors, and human-confirmed facts must stay separate throughout the handoff.

## Carrier Rejection Capture

Carrier rejection capture should be deterministic at the envelope level. Every future notice from email or a portal should be capturable as one of:

- a known candidate rejection bucket; or
- `unknown_or_new_rejection_pattern`.

That unknown bucket is required. It lets the system capture 100 percent of future notices without pretending every carrier reason code is known in advance.

Each rejection record should preserve source metadata, source hashes, attachment hashes, notice identifiers, channel metadata, matter/budget/invoice reconciliation candidates, human review outcomes, appeal/fix actions, appeal results, financial outcomes, and learning candidates.

## Human And Lake Gates

Appeals and fixes require human authorization before any submission. Appeal results append outcome records; they do not rewrite the original rejection record.

Exception Lake handoff remains disabled or validate-only in this repo until the Lake repo owns and promotes admission schemas, append-only storage, and event mapping. This repo may prepare evidence packets for review, but it must not write Lake records by default.

## Validation

Run:

```powershell
python scripts/validate_intake_orchestrator_adoption_review.py
python scripts/run_full_pytest.py tests/test_intake_orchestrator_adoption_review.py -q
```
