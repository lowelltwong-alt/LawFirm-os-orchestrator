# 02 — Phased V1 Roadmap

## Phase 0 — Stabilize MVP scaffold

**Codex level:** Medium / High

Goals:

- Commit MVP scaffold cleanly.
- Add `.gitignore` if missing.
- Ensure tests pass.
- Ensure CLI smoke test passes.
- Ensure substrate client has no write methods.
- Ensure Lake mode defaults to disabled.

## Phase 1 — Seed architecture memory

**Codex level:** Medium

Add this seed pack into the repo and summarize the source exports into stable docs. Do not change runtime code except references to docs.

## Phase 2 — Eval and metrics spine

**Codex level:** High

Add:

- `evals/fixtures/classify_exception_cases.jsonl`
- `evals/gold/classify_exception_gold.jsonl`
- `src/lawfirm_os_orchestrator/evals/graders.py`
- `scripts/run_evals.py`
- metrics output JSON

Target metrics:

- route exact match;
- event class exact match;
- first-pass validation rate;
- evidence completeness;
- high-confidence error rate;
- model calls per accepted packet;
- cost placeholder fields.

## Phase 3 — Learning objects

**Codex level:** High

Add strict Pydantic models:

- `ReviewerLabel`
- `DefectTag`
- `PressureVectorRef`
- `LearningCandidate`
- `UpgradeHypothesis`
- `ExperimentPlan`
- `ShadowEvalResult`
- `UpgradeProposal`
- `ActionRecommendation`

No auto-patching.

## Phase 4 — Research Radar local mode

**Codex level:** High

Add local import commands:

```bash
python -m lawfirm_os_orchestrator research-radar import-signal --input path/to/signal.json
python -m lawfirm_os_orchestrator research-radar list-signals
python -m lawfirm_os_orchestrator research-radar propose-upgrades --signals ... --out ...
```

No web crawler yet. No autonomous source scanning yet. Local curated signals only.

## Phase 5 — Algorithm/math intelligence

**Codex level:** High

Represent frontier methods as structured `AlgorithmInsight` records, not code patches.

Fields:

- source ref;
- claim;
- technique family;
- target orchestrator surface;
- expected lift;
- risk;
- verifiability;
- experiment plan ref.

## Phase 6 — Shadow eval loop

**Codex level:** High

Run proposed prompt/validator/router changes against fixture corpora without changing production defaults.

Outputs:

- `ShadowEvalResult`
- metric deltas;
- regression warnings;
- recommended next action.

## Phase 7 — Upgrade proposal generator

**Codex level:** High

Generate human-reviewable proposal packets:

```text
upgrade_proposals/<proposal_id>/
├── proposal.json
├── evidence_refs.json
├── experiment_plan.json
├── shadow_eval_result.json
├── risk_review.md
└── codex_task_draft.md
```

The `codex_task_draft.md` is a proposed prompt for a future Codex run. It is not executed automatically.

## Phase 8 — Runtime/Substrate integration hardening

**Codex level:** Extra High if it touches multiple repos

Only after substrate/runtime PRs merge:

- consume real orchestrator contract export;
- update orchestrator `contracts.lock.json`;
- make Lake dry-run receipts richer;
- keep runtime-safe ingest dual-gated and off by default.
