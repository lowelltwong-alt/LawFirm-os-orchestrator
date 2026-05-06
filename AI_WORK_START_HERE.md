# AI Work Start Here

Route: `orchestrator.mvp.classify_exception`
Mode: `synthetic_only_local_first`
V1 seed read-first doc: `docs/seed/00_CODEX_READ_FIRST.md`
Allowed paths: `src/lawfirm_os_orchestrator/**`, `tests/**`, `examples/**`, `docs/**`
Forbidden paths: Semantic Substrate and Exceptions Lake runtime repos except through documented patches.
Contract surfaces touched: read-only manifest, route registry, event-class registry, policy bundle, ledger, evidence packet.
Validation plan: run `python -m pytest` and CLI smoke test.
Stop conditions: see `docs/decisions/synthetic_only_policy.md`.
