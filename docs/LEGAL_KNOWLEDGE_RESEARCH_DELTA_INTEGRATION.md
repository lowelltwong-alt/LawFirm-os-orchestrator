# Legal Knowledge Research Delta Integration

The latest agent-systems research does not require Orchestrator to take ownership of legal knowledge. It requires stronger adapter boundaries.

## Orchestrator changes from this patch

- Treat Legal Knowledge Runtime evals as outcome-based checks on final bundles, not transcripts.
- Prefer one manager/default adapter path; only fan out where the task is genuinely parallelizable.
- Require document-integrity and safety-check results before high-impact legal drafting or document transformation workflows are considered review-ready.
- Treat hostile instructions inside retrieved text or tool results as untrusted data.
- Preserve working-memory vs. record-memory separation.

## Still forbidden

- Orchestrator must not define legal document types, bundle types, guardrail IDs, or canonical eval schema meaning.
- Orchestrator must not store or index legal documents directly.
- Orchestrator must not spawn uncontrolled subagents for retrieval.
- Orchestrator must not store hidden reasoning or unrestricted prompt transcripts in Exception Lake.
