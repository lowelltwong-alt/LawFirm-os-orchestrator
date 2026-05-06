# Contracts

The MVP consumes the following read-only surfaces from a local Semantic Substrate checkout or fixture:

- `manifests/contract_manifest.v1.json`
- `registry/exception-route-registry.json`

It writes:

- append-only JSONL ledger records;
- local evidence packet directories;
- optional dry-run Exception Lake request and receipt artifacts.
