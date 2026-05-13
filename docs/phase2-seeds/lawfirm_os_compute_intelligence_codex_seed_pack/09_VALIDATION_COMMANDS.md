# Validation Commands

Use these for the Orchestrator seed pass.

## Hard preflight gate

Before running validation, verify the expected scripts/files exist. If any are
missing, **stop and report**. Do not treat a missing validation script as a pass.

Required local files:

```text
scripts/check_safety.py
scripts/run_evals.py
evals/fixtures/classify_exception_cases.jsonl
evals/gold/classify_exception_gold.jsonl
```

Required seed-pack safety script:

```text
scripts/check_seed_pack_safety.py
```

## Commands

```bash
python -m pytest
python scripts/check_safety.py --stdout json
python scripts/run_evals.py --fixture evals/fixtures/classify_exception_cases.jsonl --gold evals/gold/classify_exception_gold.jsonl --stdout json
python docs/phase2-seeds/scripts/check_seed_pack_safety.py .
git diff --check
```

If Windows temp-directory issues occur, use a local `--basetemp` folder for pytest,
but do not weaken assertions.

## Failure rule

If any validation command exits non-zero, do not commit. Stop and report the exact
command, exit status, and relevant output.

## Safety checks to inspect manually

- No `requests`, `urllib`, `httpx`, `aiohttp`, `subprocess`, schedule/cron, or Git execution added for live behavior.
- No model SDK imports added for PR09–PR12 seeds.
- No writes to Substrate or Exception Lake.
- No route_id/event_class invention.
- No automatic green restoration.
- Compute ROI outputs remain decision support only.
- Monte Carlo outputs remain decision support only and record random seeds.
- Self-learning outputs remain proposals for human review only.
