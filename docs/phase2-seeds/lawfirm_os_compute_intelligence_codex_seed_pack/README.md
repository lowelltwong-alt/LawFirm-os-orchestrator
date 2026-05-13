# LawFirm OS Compute Intelligence + Game/Scenario + Self-Learning Seed Pack

This pack is a Codex-ready seed and implementation-instruction bundle for the next LawFirm OS phase after the current Orchestrator PR02/PR03 work and the planned PR04 inert Codex task packet builder.

It converts the token-efficiency / future-readiness / game-theory discussion into a controlled set of seed artifacts, schemas, algorithms, and prompts.

## Main doctrine

```text
Risk color controls authority.
Hardness controls harness depth.
Leverage controls priority.
Stakes size controls escalation sensitivity.
Reversibility controls autonomy.
Frequency controls compounding value.
Compute/token budgets are strategic allocations, not just dollar costs.
Research Radar may inform scenario probabilities, not directly change authority.
Exception Lake evidence is the learning source of truth for optimizer feedback.
Humans create or restore non-preapproved green authority.
```

## What this pack is for

Use it to seed future phases:

- `PR09_COMPUTE_INTELLIGENCE_TOKEN_ROI_SEED`
- `PR10_GAME_STATE_MONTE_CARLO_SCENARIO_SEED`
- `PR11_SELF_LEARNING_COMPUTE_OPTIMIZER_SEED`
- `PR12_FRONTIER_MATH_ALGORITHM_RADAR_SEED`

These phases are designed to run after the current Orchestrator PR04 seed work, unless you explicitly approve earlier doc-only seeding.

## What this pack must not do

This pack must not be used to add live research automation, model calls, external APIs, scheduled jobs, external writes, or self-modifying behavior.

All outputs are proposals, evidence, local simulations, or future implementation plans.

## Recommended use

1. Finish PR04: inert Codex task packet builder.
2. Run `00_PASTE_THIS_TO_CODEX.md` in Codex to add this seed pack into the Orchestrator docs/phase2-seeds area.
3. Have Claude Code run `claude/CLAUDE_CODE_RECHECK_READ_ONLY.md` as an independent review.
4. Only after review, implement PR09–PR12 one phase at a time.

## Pack layout

```text
00_PASTE_THIS_TO_CODEX.md
01_CODEX_MASTER_INSTRUCTIONS.md
02_DESIGN_RATIONALE.md
03_ARCHITECTURE_AND_PLACEMENT.md
04_ALGORITHM_CATALOG.md
05_FRONTIER_MATH_RADAR.md
06_GAME_THEORY_MONTE_CARLO.md
07_SELF_LEARNING_COMPUTE_OPTIMIZER.md
08_ACCEPTANCE_CHECKLIST.md
09_VALIDATION_COMMANDS.md
10_STOP_CONDITIONS.md
codex_prompts/
claude/
docs/phase2-seeds/
schemas/
examples/
reference_algorithms/local_only/
reports/
```

## v2 Claude-review fixes

This v2 pack incorporates Claude Code review feedback before seeding. It fixes
reference-algorithm defects, tightens schemas, adds a seed-pack safety scanner,
adds reproducible Monte Carlo seeds, makes optimizer outputs proposal-only, and
adds `docs/phase2-seeds/KILL_SWITCH.md` for future fail-closed implementation.
