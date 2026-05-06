# 01 — Accepted Architecture

## Core shape

LawFirm OS Orchestrator is the third leg of the LawFirm OS architecture:

```text
Semantic Substrate  = authority / control plane
Orchestrator        = execution / coordination plane
Exceptions Lake     = evidence / audit / learning plane
```

The first durable unit remains:

```text
contract-locked evidence packet + append-only run ledger
```

The V1 system should evolve from the MVP command:

```bash
python -m lawfirm_os_orchestrator classify-exception   --input examples/synthetic_exception_event.json   --substrate tests/fixtures/substrate   --lake-mode disabled   --stdout json
```

## V1 capabilities

V1 should add, in order:

1. Architecture memory and seed docs.
2. Eval harness and metrics ledger.
3. Defect taxonomy and reviewer-label intake.
4. Pressure-vector intake and learning candidates.
5. Research Radar local import of external discoveries.
6. Algorithm/math intelligence as `AlgorithmInsight` objects.
7. Upgrade hypotheses and experiment plans.
8. Shadow evals.
9. Upgrade proposal generation.
10. Human-approved Codex task draft generation.

## Not V1 yet

Do not add:

- real client/matter data paths;
- production connectors;
- autonomous code mutation;
- substrate writes;
- runtime Lake ingest by default;
- LangGraph-first runtime;
- Temporal-first runtime;
- MCP server mode;
- background daemon;
- dashboard-first UI;
- uncontrolled multi-agent swarm.

## Critical distinction

“Self-learning” means:

```text
runtime/research evidence
→ defect or insight object
→ hypothesis
→ shadow eval
→ proposal
→ human approval
→ versioned implementation
→ measured result
```

It does **not** mean:

```text
paper/blog/model suggestion
→ automatic code rewrite
→ automatic production deployment
```
