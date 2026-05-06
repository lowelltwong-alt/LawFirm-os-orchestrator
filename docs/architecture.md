# Architecture

```mermaid
flowchart LR
    SS[Semantic Substrate / authority] -->|pinned manifest + registries| O[Orchestrator / execution]
    O -->|contract-locked evidence packet| L[Exception Lake gateway]
    L -->|receipt or rejection| O
    L -->|learning candidates only| G[Governance inbox]
    G -->|approved promotion only| SS
```

The Orchestrator coordinates runs. It does not define truth.
