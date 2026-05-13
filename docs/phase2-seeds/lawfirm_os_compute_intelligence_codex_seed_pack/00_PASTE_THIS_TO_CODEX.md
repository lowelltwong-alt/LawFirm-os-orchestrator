# Codex Prompt — Seed Compute Intelligence, Game Theory, Monte Carlo, Frontier Math Radar, and Self-Learning Optimizer

You are continuing LawFirm OS Phase 2 after Orchestrator PR02/PR03 and preferably after PR04.

This is a seed-only implementation unless explicitly approved otherwise.

## Scope

Target repo:

```text
C:\Users\lowel\OneDrive\Desktop\Git Projects\LawFirm-os-orchestrator
```

Work only in the Orchestrator repo for this seed pass.

Do not edit Substrate.
Do not edit Exception Lake.
Do not push.
Do not create GitHub PRs.
Do not install dependencies.
Do not call external services.
Do not add live Research Radar automation.
Do not add model calls.
Do not add scheduled jobs.
Do not add external APIs.
Do not add external writes.
Do not execute Git from application code.
Do not mutate canonical ontology.
Do not invent route_id or event_class.
Do not allow agents to restore green authority.
Do not let hardness, leverage, compute ROI, or game-theory recommendations upgrade risk authority.

## Goal

Add seed artifacts for future compute-intelligence phases:

- PR09: Compute Intelligence / Token ROI / Strategic Compute Allocation
- PR10: Game-State + Monte Carlo + What-If Scenario Engine
- PR11: Self-Learning Compute Optimizer
- PR12: Frontier Math / Algorithmic Breakthrough Radar

These are seed artifacts only.
They must not claim implementation is complete.
They must prepare a clear future build path.

## Required start inspection

Before editing:

1. Confirm current branch.
2. Confirm tracked working tree is clean.
3. Confirm PR02 and PR03 commits are present if applicable.
4. Confirm whether PR04 is already implemented.
5. Confirm docs/phase2-seeds exists or create it if absent.
6. Confirm current front-door docs exist.

If the working tree is dirty, stop and report.

## Branch

Create or use a local branch:

```text
phase2/pr09-pr12-compute-intelligence-seeds
```

Base it on the current Orchestrator branch/head after PR04 if PR04 exists, otherwise on the latest PR03 branch/head.

## Files to add

Create these files in the Orchestrator repo:

```text
docs/phase2-seeds/PR09_COMPUTE_INTELLIGENCE_TOKEN_ROI_SEED.md
docs/phase2-seeds/PR10_GAME_STATE_MONTE_CARLO_SCENARIO_SEED.md
docs/phase2-seeds/PR11_SELF_LEARNING_COMPUTE_OPTIMIZER_SEED.md
docs/phase2-seeds/PR12_FRONTIER_MATH_ALGORITHM_RADAR_SEED.md
docs/phase2-seeds/COMPUTE_INTELLIGENCE_OBJECT_GRAPH.md
docs/phase2-seeds/COMPUTE_INTELLIGENCE_DATA_FLOW.mmd
docs/phase2-seeds/compute-intelligence-seed-index.json
```

Also add a local-only reference directory if consistent with repo style:

```text
docs/phase2-seeds/reference_algorithms/
```

Copy or adapt the local-only algorithms from this pack as documentation/reference algorithms, not production runtime code:

```text
reference_algorithms/local_only/token_roi.py
reference_algorithms/local_only/game_state_classifier.py
reference_algorithms/local_only/monte_carlo_scenario.py
reference_algorithms/local_only/self_learning_compute_optimizer.py
```

If repo style prefers no Python in docs, place pseudocode in Markdown instead.

## Update front-door docs

Update:

```text
README.md
AI_TABLE_OF_CONTENTS.md
ENDPOINTS_AND_COMMANDS.md
DATA_FLOW_MAP.md
RECENT_WORK.md
```

If `AGENTS.md` or `AI_WORK_START_HERE.md` should reference the seeds, update them too.

Do not claim PR09–PR12 are implemented.
Say they are seed/planning/reference artifacts only.

## Required doctrine for these seeds

Token budgets are not only dollar budgets.
They represent dollar cost, latency, attention, context-window scarcity, human review burden, risk exposure, opportunity cost, cache/reuse value, learning value, future-option value, and strategic timing.

A high-token run is good only if the expected present + future + strategic value justifies compute, latency, attention, and risk.

A low-token run can be bad if it creates rework, risk, or strategic blindness.

Compute ROI must not override RYG authority.
Game theory must not override RYG authority.
Monte Carlo must not override RYG authority.
Self-learning optimizers must not self-modify policy, restore green authority, mutate canon, or execute external actions.

## Required PR09 seed content

PR09 must define:

- effective compute cost;
- token shadow price;
- compute ROI grade;
- strategic token allocation portfolio;
- cache/reuse credit;
- learning credit;
- future-option credit;
- reputation-protection reserve;
- opportunity cost;
- expected value per token;
- risk-adjusted future value per token;
- allocation buckets for production, validation, learning loop, Research Radar, future-option prep, exploration, and reputation-protection reserve.

## Required PR10 seed content

PR10 must define:

- game-state classifier;
- first-mover race;
- waiting game;
- coordination game;
- arms race;
- reputation/ruin game;
- adversarial game;
- option portfolio game;
- Monte Carlo simulation for uncertain high-token future bets;
- scenario inputs such as probability of breakthrough, future token cost decline, model capability gain, competitor adoption, first-mover advantage, fallback reuse value, downside risk, reputation exposure, and detection lag.

Outputs are decision support only.

## Required PR11 seed content

PR11 must define:

- self-learning compute optimizer;
- feedback from append-only Exception Lake evidence;
- recommendations for model, cache, compression, harness, budget, red-team, and research allocation;
- no self-modification;
- no automatic green restoration;
- no canon mutation;
- no external actions.

## Required PR12 seed content

PR12 must define:

- Frontier Math / Algorithmic Breakthrough Radar;
- local-only watchlist seeding;
- breakthrough readiness score;
- prep-option value;
- math-to-system application mapping;
- what-if staged readiness plan;
- competitor-game implications;
- no claim that a math breakthrough has occurred unless externally verified later;
- no live crawling or external research automation.

## Required issue report

Add or update:

```text
docs/phase2-seeds/COMPUTE_INTELLIGENCE_ISSUES_AND_FIXES.md
```

Include known issues and likely fixes:

- Token budgets can be optimized for cheapness instead of value.
- Future-readiness can become hype-driven waste.
- Research Radar can become unauthorized live automation.
- Monte Carlo outputs can create false precision.
- Self-learning can drift into self-modification.
- Game-theory framing can overfit to imagined competitors.
- Exception Lake evidence may not yet support optimizer feedback loops.
- Stakes/reputation risk may be underweighted.
- Cache/reuse value may be omitted.
- Human review burden may not be priced into token allocation.

For each issue, include likely fix and whether it is PR09/PR10/PR11/PR12 or future PR.

## Validation

Before validation, verify these files exist. If any are missing, stop and report; do not commit:

```text
scripts/check_safety.py
scripts/run_evals.py
evals/fixtures/classify_exception_cases.jsonl
evals/gold/classify_exception_gold.jsonl
docs/phase2-seeds/scripts/check_seed_pack_safety.py
```

Run:

```bash
python -m pytest
python scripts/check_safety.py --stdout json
python scripts/run_evals.py --fixture evals/fixtures/classify_exception_cases.jsonl --gold evals/gold/classify_exception_gold.jsonl --stdout json
python docs/phase2-seeds/scripts/check_seed_pack_safety.py .
git diff --check
```

If any command exits non-zero, stop and report. Do not commit.

If validation passes, commit locally:

```text
docs: seed compute intelligence and scenario planning phases
```

Do not push.

## Final report

Return:

- files changed;
- seed docs created;
- reference algorithms created/adapted;
- validations run;
- validation results;
- commit SHA;
- whether safe for Claude read-only review;
- remaining implementation phases.
