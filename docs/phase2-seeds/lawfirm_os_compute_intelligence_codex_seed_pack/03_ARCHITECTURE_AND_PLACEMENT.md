# Architecture And Placement

## Recommended placement

This pack should be seeded first in the Orchestrator repo as future-phase documentation and reference algorithms:

```text
LawFirm-os-orchestrator/docs/phase2-seeds/
```

Do not alter the Substrate or Exception Lake repos during the seed pass.

## Later control-plane implementation

When PR09–PR12 are approved, the Substrate should own canonical schemas/registries for:

- compute-allocation-policy;
- compute-roi-record;
- scenario-simulation-request;
- scenario-simulation-result;
- game-state-classification;
- frontier-math-radar-item;
- self-learning-optimizer-recommendation.

## Later Exception Lake implementation

Exception Lake should eventually store append-only evidence records for:

- token-spend-record;
- compute-roi-record;
- scenario-run-record;
- optimizer-recommendation-record;
- realized-outcome-record;
- option-value-retrospective.

## Later Orchestrator implementation

The Orchestrator may implement deterministic local modules for:

- token ROI scoring;
- game-state classification;
- Monte Carlo simulation;
- option-value estimation;
- self-learning compute allocation recommendations.

These recommendations may shape task-packet proposals, not authority.
