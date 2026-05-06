# LawFirm OS Orchestrator MVP Repository Design

## Design stance

The MVP should be a **single-package, local-first CLI** whose entire happy path works from a developer machine, writes its own run artifacts locally, and never depends on a web app, a background daemon, or agent-to-agent coordination. The strongest precedent from the broader Python and local-first ecosystems is to keep the importable code in a `src/` layout, keep runtime entry points explicit through `__main__.py`, and prefer static package metadata in `pyproject.toml`. Local-first principles emphasize offline operation, privacy, and user control, while the `src` layout helps prevent accidental imports from the working tree instead of the installed package. citeturn13view5turn25search0turn21view0turn14view0

One important consequence of your fixed command contract is that the import package should be **`lawfirm_os_orchestrator`**, not a shared namespace package. Python packaging absolutely does support namespace packages across multiple distributions, but that pattern is most appropriate when several projects intentionally contribute modules into a single import namespace. Here, the more conservative MVP move is to keep the orchestrator as its own import package and integrate the sibling repos through **narrow adapters** rather than by assuming their Python package names or internals. citeturn24view0turn21view0

Because the actual artifacts from `LawFirm-os-semantic-substrate` and `LawFirm-os-exceptions-lake-runtime` were not provided here, the design below treats them as **upstream systems of record**. The orchestrator must consume their canon exactly as published, snapshot what it read, and refuse to invent or reinterpret IDs or schema meaning. That is why the example outputs below use **placeholders** for canonical `event_class_id` and `route_id` values rather than fabricating them.

## Repository shape

The repo should use a standard installable CLI package with a small, readable surface area. Python’s `-m` execution model is driven by `__main__.py`, and `argparse` is the standard-library parser designed for command-line options, arguments, and subcommands. The result is a package that stays dependency-light while still supporting the exact command you specified. citeturn21view0turn16view0turn9search1

```text
LawFirm-os-orchestrator/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── examples/
│   ├── synthetic_exception_event.json
│   └── expected/
│       ├── classify_exception_stdout.json
│       ├── classify_exception_ledger_record.jsonl
│       └── evidence_packet_manifest.json
├── docs/
│   ├── architecture.md
│   ├── contracts.md
│   └── decisions/
│       ├── local_first.md
│       ├── read_only_substrate.md
│       └── synthetic_only_policy.md
├── src/
│   └── lawfirm_os_orchestrator/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── app.py
│       ├── commands/
│       │   └── classify_exception.py
│       ├── config/
│       │   ├── models.py
│       │   ├── loader.py
│       │   └── defaults.py
│       ├── domain/
│       │   ├── exception_event.py
│       │   ├── classification.py
│       │   ├── ledger.py
│       │   ├── evidence.py
│       │   └── policy.py
│       ├── policy/
│       │   ├── gate.py
│       │   └── synthetic_only.py
│       ├── substrate/
│       │   ├── base.py
│       │   ├── reader.py
│       │   ├── snapshot.py
│       │   └── resolver.py
│       ├── model_router/
│       │   ├── base.py
│       │   ├── router.py
│       │   ├── schema_factory.py
│       │   ├── prompts/
│       │   │   └── classify_exception_system.txt
│       │   └── adapters/
│       │       ├── mock.py
│       │       └── openai_structured.py
│       ├── evidence/
│       │   ├── packet.py
│       │   └── manifest.py
│       ├── ledger/
│       │   └── writer.py
│       ├── lake/
│       │   ├── base.py
│       │   ├── disabled.py
│       │   ├── dry_run.py
│       │   └── runtime_safe.py
│       └── util/
│           ├── files.py
│           ├── hashing.py
│           ├── ids.py
│           ├── time.py
│           └── json_io.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│       ├── substrate/
│       ├── model_outputs/
│       └── lake_runtime/
└── scripts/
    └── smoke_classify_exception.sh
```

The module responsibilities should be divided by **pipeline stage**, not by framework. `commands/classify_exception.py` is the orchestrating use-case layer; `domain/` contains the strict Pydantic contracts; `policy/` decides what is allowed before the model runs and before any ingestion can happen; `substrate/` is a read-only boundary for canonical IDs and schemas; `model_router/` owns provider selection and structured-output constraints; `ledger/` and `evidence/` write immutable artifacts; and `lake/` is the only outbound write boundary, defaulting to disabled. Pydantic’s configuration system supports strict validation, forbidding extra fields, and faux-immutability, which are exactly the behaviors you want for upstream-canonical, safety-sensitive contracts. citeturn14view4turn15view0turn15view1turn15view3

## Packaging and configuration

The packaging baseline should be a modern `pyproject.toml` with static metadata in `[project]`, optional extras for provider-specific adapters, a console script for convenience, and `python_requires >= 3.11` so the repo can rely on the standard-library `tomllib` parser. Python’s packaging specifications explicitly support static project metadata in `[project]`, optional feature-specific dependencies in `[project.optional-dependencies]`, and installable commands in `[project.scripts]`. `tomllib` was added in Python 3.11 and is purpose-built for reading TOML configuration. citeturn14view0turn22search0turn14view2turn14view1

A good MVP `pyproject.toml` dependency shape is:

```toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "LawFirm-os-orchestrator"
version = "0.1.0"
description = "Local-first orchestration for synthetic exception classification."
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.11,<3",
  "pydantic-settings>=2.6,<3",
]

[project.optional-dependencies]
openai = [
  "openai>=2.0,<3",
]
dev = [
  "pytest>=8.3,<9",
  "pytest-cov>=5,<6",
  "hypothesis>=6.0,<7",
  "ruff>=0.6,<1",
  "mypy>=1.11,<2",
  "build>=1.2,<2",
]

[project.scripts]
lawfirm-os-orchestrator = "lawfirm_os_orchestrator.cli:main"

[tool.setuptools]
package-dir = {"" = "src"}
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]
include = ["lawfirm_os_orchestrator*"]

[tool.setuptools.package-data]
lawfirm_os_orchestrator = [
  "model_router/prompts/*.txt",
]
```

This keeps the **core wheel intentionally small**. The CLI, config loading, logging, JSON handling, hashing, argument parsing, timestamps, UUIDs, and file operations all come from the standard library. The only always-on third-party requirements are the schema/config primitives. The provider adapter lives behind an extra so that a local developer can still install and run the pipeline shape without committing to a cloud dependency on day one. The packaging guide’s extras model is exactly built for feature-specific dependency expansion. citeturn22search0turn22search2

The config model should be a nested Pydantic settings object loaded from, in order, **code defaults**, an optional local TOML file, and environment overrides. `pydantic-settings` is designed to load settings from environment variables and secrets files, while Pydantic’s strict mode and `extra='forbid'` help ensure config and data contracts fail closed instead of silently coercing or ignoring mistakes. citeturn13view1turn15view1turn15view0

A practical config model looks like this:

```python
class WorkspaceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    run_root: Path = Path(".lawfirm-os-orchestrator/runs")
    ledger_path: Path = Path(".lawfirm-os-orchestrator/ledger/classify_exception.jsonl")

class SubstrateConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_kind: Literal["path", "package"]
    root_path: Path | None = None
    package_name: str | None = None
    manifest_relpath: str = "exports/orchestrator_manifest.json"

class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    adapter: Literal["mock", "openai_structured"] = "mock"
    model_name: str | None = None
    timeout_seconds: int = 20
    temperature: float = 0.0
    max_output_tokens: int = 600
    structured_only: bool = True

class LakeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    mode: Literal["disabled", "dry-run", "runtime_safe"] = "disabled"
    allow_commit: bool = False
    safe_callable: str | None = None

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LAWFIRM_OS_ORCHESTRATOR_",
        extra="forbid"
    )
    workspace: WorkspaceConfig = WorkspaceConfig()
    substrate: SubstrateConfig
    model: ModelConfig = ModelConfig()
    lake: LakeConfig = LakeConfig()
    synthetic_only: bool = True
```

## Runtime contract and artifacts

The CLI contract should remain brutally simple. The canonical invocation is your required one:

```bash
python -m lawfirm_os_orchestrator classify-exception --input examples/synthetic_exception_event.json
```

A fuller contract should be:

```text
usage: python -m lawfirm_os_orchestrator classify-exception
       --input PATH
       [--config PATH]
       [--run-root PATH]
       [--ledger-path PATH]
       [--model-adapter {mock,openai_structured}]
       [--ingest {disabled,dry-run,commit}]
       [--stdout {json,text}]
       [--fail-on-needs-review]
```

The standard-library guidance for `__main__` is to keep it thin and call a `main()` function, which is exactly what this contract wants. `argparse` supports subcommands and informative usage/help without any extra runtime dependency. citeturn21view0turn16view0

The exit codes should be explicit:

- `0` — success
- `2` — input/config/policy validation failed
- `3` — substrate load or canonical lookup failed
- `4` — model classification failed
- `5` — artifact writing failed
- `6` — ingestion failed after a successful classification

The input event should be strict and should operationalize the synthetic-data rule rather than leaving it as a convention. An example input shape:

```json
{
  "schema_version": "1.0",
  "event_id": "synexc_2026_05_05_001",
  "occurred_at": "2026-05-05T14:23:11Z",
  "data_origin": "synthetic",
  "contains_real_client_data": false,
  "contains_real_matter_data": false,
  "source_system": "synthetic_fixture",
  "reported_by": "example_generator",
  "summary": "Synthetic deadline reminder failed to fire for a synthetic matter.",
  "details": "A scheduled synthetic reminder job did not emit the expected notification event.",
  "signals": {
    "severity": "high",
    "deadline_related": true,
    "notification_expected": true
  },
  "attachments": []
}
```

The output shown to stdout should be a concise machine-readable summary. Because canonical IDs must come from the Semantic Substrate and cannot be invented here, the example deliberately uses placeholders:

```json
{
  "run_id": "01JTGK8J9Y4R8J8A7R2M7V7S8F",
  "status": "ok",
  "event_class_id": "<canonical_event_class_id_from_substrate>",
  "route_id": "<canonical_route_id_from_substrate>",
  "confidence": 0.93,
  "needs_human_review": true,
  "ledger_path": ".lawfirm-os-orchestrator/ledger/classify_exception.jsonl",
  "evidence_packet_path": ".lawfirm-os-orchestrator/runs/01JTGK8J9Y4R8J8A7R2M7V7S8F/evidence",
  "ingestion": {
    "mode": "disabled",
    "status": "not_attempted"
  }
}
```

The model-output contract should be defined once as a Pydantic model, then used in two directions: first to generate a **validation JSON Schema** for any adapter that supports native schema-constrained outputs, and second to validate the returned JSON locally with `model_validate_json()` or `TypeAdapter.validate_json()`. Pydantic can generate validation-oriented JSON Schema, and both Pydantic and provider-side structured-output systems are explicitly designed for this exact pattern. Structured-output providers can be given a schema that enumerates the canonical route and event-class IDs, which is the cleanest MVP way to prevent the model from returning off-canon IDs. citeturn13view0turn26view1turn26view0turn26view2

The **run ledger** should be JSONL, not SQLite, for the MVP. JSON Lines is explicitly designed for one-record-at-a-time processing and is a good fit for log files and shell pipelines. citeturn13view4

Recommended ledger schema per line:

```json
{
  "ledger_version": "1",
  "run_id": "01JTGK8J9Y4R8J8A7R2M7V7S8F",
  "command": "classify-exception",
  "started_at": "2026-05-05T14:23:12Z",
  "finished_at": "2026-05-05T14:23:14Z",
  "status": "ok",
  "input_path": "examples/synthetic_exception_event.json",
  "input_sha256": "<sha256>",
  "synthetic_only_passed": true,
  "substrate": {
    "source_kind": "path",
    "source_ref": "../LawFirm-os-semantic-substrate",
    "manifest_sha256": "<sha256>",
    "canon_version": "<substrate_version_or_commit>"
  },
  "model": {
    "adapter": "openai_structured",
    "model_name": "<configured_model_name>",
    "structured_only": true
  },
  "classification": {
    "event_class_id": "<canonical_event_class_id_from_substrate>",
    "route_id": "<canonical_route_id_from_substrate>",
    "confidence": 0.93,
    "needs_human_review": true
  },
  "evidence_packet_path": ".lawfirm-os-orchestrator/runs/01JTGK8J9Y4R8J8A7R2M7V7S8F/evidence",
  "ingestion": {
    "mode": "disabled",
    "attempted": false,
    "status": "not_attempted"
  }
}
```

The **evidence packet** should be a directory, not a database blob, so it remains easy to inspect, diff, archive, and hand off. The packet should contain:

```text
evidence/
├── manifest.json
├── input_event.json
├── policy_gate.json
├── substrate_snapshot.json
├── model_request.json
├── model_response.json
├── classification_result.json
├── stdout_summary.json
├── ingest_request.json         # optional
└── ingest_receipt.json         # optional
```

`manifest.json` should include the run ID, timestamps, schema version, and a SHA-256 hash for every included file.

## Boundary clients and policy controls

The **policy gate** should be a first-class module, not scattered `if` statements. It should run twice: once **before classification** and once **before ingestion**. Before classification, it should verify that the input is explicitly marked synthetic, that all “contains real data” flags are false, that the selected adapter is allowed for this run, and that the substrate source is readable and configured as read-only. After classification, it should verify that the returned IDs are in the canonical sets loaded from the substrate, that no extra fields were returned, and that confidence or review flags meet your configured rules. This is exactly the kind of fail-closed contract Pydantic strict mode and `extra='forbid'` were built to support. citeturn15view1turn15view0turn26view0

A good substrate client design is **read-only, versioned, and snapshot-oriented**:

```python
class SubstrateClient(Protocol):
    def load_manifest(self) -> SubstrateManifest: ...
    def load_event_classes(self) -> list[CanonicalEventClass]: ...
    def load_routes(self) -> list[CanonicalRoute]: ...
    def resolve_ids(self) -> CanonicalIdSets: ...
    def snapshot(self) -> SubstrateSnapshot: ...
```

Implement only two sources in the MVP: `PathSubstrateClient` and `PackageResourceSubstrateClient`. The latter should read package-shipped files through `importlib.resources`, which the standard library provides specifically for package data access. Do **not** expose any write/update methods at all; that absence is part of the safety model. citeturn13view6

The **model router** should be intentionally narrow. It should choose exactly one adapter per run and make exactly one bounded classification call. No tools. No retries that mutate prompts. No planner/executor split. No chain-of-thought harvesting. The adapter interface can be as small as:

```python
class ClassificationAdapter(Protocol):
    def classify(
        self,
        event: SyntheticExceptionEvent,
        allowed_event_class_ids: list[str],
        allowed_route_ids: list[str],
        prompt_bundle: PromptBundle,
    ) -> RawClassificationResponse: ...
```

The best MVP pattern is:

1. Load canonical IDs from the substrate.
2. Build a **per-run output schema** whose `event_class_id` and `route_id` fields are `enum`-bounded to those canonical values.
3. Pass that schema to the adapter if the provider supports native structured outputs.
4. Locally validate the returned JSON again using the same Pydantic model.
5. Refuse free-form text parsing fallbacks.

That gives you two guardrails at once: provider-side schema adherence and local strict validation. citeturn13view0turn26view1turn26view0

Ship two adapters in the repo structure, but only one of them needs to be “real” on day one:

- `mock`: deterministic, zero-network, fixture-friendly, used by examples and CI.
- `openai_structured`: optional-extra adapter for production-like runs where a provider supports JSON Schema constrained output.

That balance keeps the repo genuinely local-first while still proving the adapter architecture.

The **Exception Lake client** should also be narrow and safe by construction:

```python
class ExceptionLakeClient(Protocol):
    def ingest(self, request: SafeIngestRequest) -> IngestReceipt: ...
```

The MVP implementations should be:

- `DisabledLakeClient`
- `DryRunLakeClient`
- `RuntimeSafeLakeClient`

`RuntimeSafeLakeClient` should call a **single configured safe function** exported by the runtime package, passing a strict Pydantic request model and expecting a strict Pydantic receipt model back. Ingestion should require **both** a config allow-switch and an explicit CLI `--ingest commit` request. That dual control prevents accidental writes and keeps “optional call through a safe interface” faithful to your no-autonomous-write rule.

## Validation roadmap and sequencing

The test plan should lean on `pytest` for readable unit and integration tests, `monkeypatch` for safe environment/config isolation, parametrization for matrix-like contract checks, and Hypothesis for property-based edge cases around input validation and ledger/evidence invariants. Those tools are well suited to exactly this kind of pipeline-heavy CLI package. citeturn13view3turn18search3turn18search4turn18search2

The testing layers should be:

- **Unit tests** for Pydantic contracts, ID membership checks, policy gate outcomes, and file/hash helpers.
- **Schema tests** that prove extra fields, missing required fields, and non-canonical IDs fail closed.
- **Substrate tests** against fixture manifests and fixture route/event-class catalogs.
- **Adapter tests** where `mock` is deterministic and the provider adapter is exercised behind a fake/mock transport or recorded fixture.
- **CLI integration tests** that invoke `python -m lawfirm_os_orchestrator classify-exception ...` end to end.
- **Property-based tests** asserting that malformed synthetic events never produce successful classifications, and that every successful run yields a ledger line plus a complete evidence packet.
- **Safety tests** proving ingestion never occurs unless explicitly enabled both in config and on the command line.

The first five PR-sized tasks should be:

1. **Scaffold the package and command path.**  
   Add `pyproject.toml`, `src/` layout, `__main__.py`, `cli.py`, the `classify-exception` subcommand stub, README quickstart, and editable-install instructions.

2. **Define the strict contracts and local artifact writers.**  
   Implement Pydantic models for input, classification output, ledger record, evidence manifest, plus JSON and hash utilities and the local run/evidence/ledger writers.

3. **Add the read-only substrate boundary.**  
   Implement `PathSubstrateClient`, substrate fixture manifests, canonical ID loading, and snapshot capture into the evidence packet.

4. **Add the policy gate and model router.**  
   Implement synthetic-only checks, dynamic allowed-ID schema building, the `mock` adapter, and local validation of the returned classification payload.

5. **Add safe lake integration and end-to-end tests.**  
   Implement `disabled`, `dry-run`, and `runtime_safe` clients, dual opt-in commit semantics, and the first full pipeline tests from input fixture to ledger line and evidence packet.

The **do not build yet** list should be explicit, because scope creep here would be unusually expensive:

- no web app or dashboard
- no background worker or daemon
- no autonomous write actions
- no substrate mutation tools
- no route or event-class authoring workflow
- no multi-agent planner/executor system
- no real client, matter, or firm data connectors
- no broad RAG layer or vector database
- no durability layer beyond local filesystem artifacts
- no human-in-the-loop task queue UI
- no analytics warehouse or metrics backend
- no generic workflow engine beyond `classify-exception`

## Open questions

The design above is high-confidence, but a few implementation-driving details remain unresolved because the upstream repo contracts were not included:

- **How does the Semantic Substrate publish canon?**  
  A manifest file, package resources, JSON exports, or Python objects all work, but the orchestrator should support exactly the upstream publication method rather than guessing.

- **What is the safe interface exposed by Exception Lake runtime?**  
  The orchestrator needs one stable callable or request/receipt contract to target.

- **How large are the canonical route and event-class catalogs?**  
  If they are modest, schema-time `enum` constraints are ideal. If they are extremely large, the repo may eventually need a staged classifier, but that should be deferred beyond the MVP.

- **Is a provider-backed adapter required on day one, or is the local deterministic adapter sufficient for the first merge?**  
  The architecture supports both, but the delivery plan changes slightly depending on that answer.