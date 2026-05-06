# README — Codex V1 Seed for LawFirm OS Orchestrator

This seed turns the MVP scaffold into a staged V1 buildout plan.

The core thesis:

```text
Semantic Substrate = authority / control plane
Orchestrator       = execution / coordination plane
Exception Lake     = evidence / audit / learning plane
```

The Orchestrator may recommend improvements to itself, but it must not autonomously mutate its own production code, the Semantic Substrate, or runtime persistence rules. It may create `UpgradeProposal`, `ExperimentPlan`, `ShadowEvalResult`, and `ActionRecommendation` artifacts for human approval.

Read order for Codex:

1. `docs/seed/00_CODEX_READ_FIRST.md`
2. `docs/seed/01_ACCEPTED_ARCHITECTURE.md`
3. `docs/seed/02_PHASED_V1_ROADMAP.md`
4. `docs/seed/03_LEARNING_LOOP_AND_RESEARCH_RADAR_SPEC.md`
5. `docs/seed/04_QUALITY_BOTTLENECK_SIX_SIGMA_SPEC.md`
6. `docs/seed/05_STOP_CONDITIONS_AND_SCOPE_GATES.md`
7. One file from `prompts/codex/v1/tasks/`

Raw exports are preserved under `docs/seed/source_exports/` and converted DOCX research files are under `docs/seed/source_exports_converted/`.
