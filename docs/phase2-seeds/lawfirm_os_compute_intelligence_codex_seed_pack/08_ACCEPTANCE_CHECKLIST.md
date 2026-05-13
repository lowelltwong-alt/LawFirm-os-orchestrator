# Acceptance Checklist

## Seed pass acceptance

- [ ] PR09 seed doc exists.
- [ ] PR10 seed doc exists.
- [ ] PR11 seed doc exists.
- [ ] PR12 seed doc exists.
- [ ] Compute Intelligence object graph exists.
- [ ] Mermaid-ready data flow exists.
- [ ] Seed index JSON exists and parses.
- [ ] Reference algorithms exist or are documented as pseudocode.
- [ ] README / AI TOC / DATA_FLOW_MAP / RECENT_WORK mention seeds.
- [ ] No code claims PR09–PR12 are implemented.
- [ ] No live research automation.
- [ ] No model calls.
- [ ] No external API calls.
- [ ] No scheduled jobs.
- [ ] No external writes.
- [ ] No authority changes.
- [ ] Tests pass.
- [ ] Safety check passes.
- [ ] Evals do not regress.
- [ ] git diff --check passes.

## Future implementation acceptance

When PR09–PR12 are later implemented, each must have:

- schemas or local models;
- CLI if appropriate;
- tests;
- data-flow map updates;
- Exception Lake evidence plan;
- stop conditions;
- human authority boundaries.
