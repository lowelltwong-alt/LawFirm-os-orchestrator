# Intake No-Write Vertical Slice Demo

Status: candidate execution-plane demo.

This demo is the Orchestrator-owned proof that the intake-to-review path can run as a local, synthetic, no-write vertical slice without turning any child repo into upstream authority.

```powershell
python -m lawfirm_os_orchestrator intake run-vertical-slice-demo `
  --input examples/intake_owner_review_request.synthetic.json `
  --workspace .. `
  --stdout json
```

The command:

- checks required sibling governance/readiness surfaces in Semantic Substrate, Intake, Legal Knowledge Runtime, Exceptions Lake, and Skills Registry;
- builds the candidate Intake owner-review packet;
- builds the candidate Exception Lake admission-review packet from that owner packet;
- writes a local attorney-review demo report and Markdown summary with source-binding, matter-posture, conflicts, budget, Lake-admission, and client-use review gates;
- appends a local JSONL ledger row.

It does not call models, submit budgets, clear conflicts, open matters, write to Semantic Substrate, write to Exception Lake, write SQLite, call connectors, externalize data, create canonical route IDs, or create event classes.

Expected current status is `blocked_pending_attorney_and_owner_review` because attorney, owner, conflicts, engagement, budget-review, and Lake-admission approvals are intentionally not automated.

Validate a generated report with:

```powershell
python scripts/validate_intake_vertical_slice_demo.py `
  --report .lawfirm-os-orchestrator/intake_vertical_slice_demo/<demo_id>/intake_vertical_slice_demo_report.json
```
