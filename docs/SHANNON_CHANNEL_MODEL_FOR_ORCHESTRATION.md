# Shannon Channel Model for Orchestration

Status: Non-canonical concept note.
Authority: Explanatory only. Does not change runtime behavior, invent route IDs, alter substrate contracts, or modify the autonomy/harness gates.

## BLUF

The orchestrator is a transmitter/receiver inside a governed communication channel that runs from substrate canon to runtime evidence. Route classification, autonomy gating, harness selection, and structured-output validation are exactly the redundancy and error-control mechanisms that information theory describes. This note explains why those gates are not bureaucracy; it does not change any of them, propose new ones, or imply that high entropy alone is a promotion signal.

Master conceptual reference: `../_shared/SHANNON_INFORMATION_THEORY_FOR_AI_GOVERNANCE_MASTER.md` (workspace-shared, non-canonical).

## Boundary

This note does **not**:

- modify any runtime behavior in `src/`, `prompts/`, `evals/`, or `examples/`;
- invent route IDs, event classes, autonomy lane definitions, or harness levels;
- alter `manifests/contract_manifest.v1.json`, `contracts.lock.json`, or any substrate consumption;
- change the deterministic classifier, the strict-output validator, or the append-only JSONL ledger;
- assert that route entropy or channel-capacity numbers are required runtime metrics today.

The autonomy law remains exactly as stated in this repo's README:

```text
Risk color controls authority.
Hardness controls harness depth.
Leverage controls priority.
Stakes size controls escalation sensitivity.
Reversibility controls autonomy.
Frequency controls compounding value.
```

## Communication model

| Shannon layer | Orchestrator-local equivalent |
|---|---|
| Information source | The user/operator intent, the synthetic input payload, the canonical route registry |
| Transmitter | Prompt builder, deterministic route classifier, autonomy gate, harness selector |
| Channel | Pinned substrate manifest read → deterministic route/event-class allowlist validation → mock classifier → strict structured-output validator |
| Noise | Ambiguous input, stale substrate clone, prompt drift, classifier misfire, missing route allowlist, partial structured output |
| Receiver | Append-only JSONL ledger, evidence packet directory, autonomy decision record, harness plan artifact |
| Destination | Governed evidence packet, autonomy lane decision, harness plan, Codex task packet, downstream reviewer |
| Redundancy | `contracts.lock.json`, route-registry allowlist, strict structured-output validation, dual ledger+packet record, autonomy passport + assumption watch |
| Error correction | Reclassification (assumption watch downgrades green to yellow/red), exception emission, governed promotion path in substrate |
| Channel capacity | Model reliability, validator coverage, reviewer bandwidth, exception-lake throughput |

## Real math used

Notation:

- $R$ = route from a finite allowlist defined by the substrate registry.
- $e$ = the orchestrator's observed input/context (manifest + payload + history).
- $X$ = the canonical correct route/action class for the input.
- $Y$ = what the deterministic classifier emits.
- $Z$ = the structured output / evidence packet finally written.
- $\hat{X}$ = the classifier's chosen route.

### Route entropy (optional, only when probabilities are well defined)

```math
H(R \mid e) \;=\; -\sum_{r} p(r \mid e)\,\log_2 p(r \mid e)
```

Orchestrator interpretation:

- The current MVP classifier is deterministic; $p(r \mid e)$ is a delta on one route. Route entropy is therefore zero by construction in normal operation. Where a future probabilistic router is introduced, $H(R \mid e)$ becomes a meaningful uncertainty gauge. **Until then, do not surface route-entropy numbers as if they were live signals — they are not.**

### Mutual information

```math
I(X;Y) \;=\; H(X) - H(X \mid Y)
```

Orchestrator interpretation:

- A retrieval bundle, prompt, or input payload is valuable insofar as it reduces uncertainty about the correct route/action $X$. Bloated context that does not reduce $H(X \mid Y)$ adds noise without adding signal — and burns channel capacity.

### Channel capacity

```math
C \;=\; \max_{p(x)} I(X;Y)
```

Orchestrator interpretation (analogy, not a runtime number):

- The orchestrator's effective capacity is set by the weakest of: model reliability, validator coverage, reviewer bandwidth, substrate clarity. The autonomy law's "stakes size controls escalation sensitivity" rule is exactly a capacity guard — escalate when expected task complexity exceeds the channel.

### Noisy-channel coding theorem (operational paraphrase)

If transmission rate $R < C$, reliable communication is achievable with coding; if $R > C$, it is not.

Orchestrator interpretation:

- When the orchestrator is asked to handle more complexity than the model + validators + reviewers can carry, no clever prompt rescues reliability. Harness depth and autonomy lane downgrade are how this repo keeps $R < C$.

### Data processing inequality

If $X \to Y \to Z$:

```math
I(X;Z) \;\le\; I(X;Y)
```

Orchestrator interpretation (the structural rule):

- An evidence packet $Z$ cannot carry more information about the canonical action $X$ than the classifier's output $Y$ already carried. Downstream prose polish does not increase canonical authority. This is the substrate's mutation boundary, expressed at the orchestrator's seam.

### Fano-style lower bound for unavoidable error

For a class set $\mathcal{X}$ and a classifier $\hat{X}$ with error probability $P_e$:

```math
H(X \mid \hat{X}) \;\le\; h_2(P_e) \;+\; P_e \log_2(|\mathcal{X}| - 1)
```

Orchestrator interpretation:

- If residual classification uncertainty stays high, error probability cannot be small. **Design rule:** when an input's route is ambiguous, do not let the model paper over $H(X \mid \hat{X})$ with confident text — escalate via the autonomy gate (yellow/red), require human review, or refuse.

### Optional drift metric (only when baselines exist)

```math
D_{\mathrm{KL}}(P_{\text{observed route mix}} \,\Vert\, P_{\text{baseline route mix}})
```

Orchestrator interpretation:

- If a governed baseline route distribution is ever published, $D_{\mathrm{KL}}$ would be the natural drift gauge. **Today this is conceptual.** Any future drift gauge requires substrate-governed baselines and explicit smoothing of zero-count classes.

## Integration implications

These are conceptual implications, not new requirements:

1. **Route allowlist validation is structured redundancy.** It detects classifier misfire before the message is "transmitted" downstream; it does not correct intent, but it reliably catches an out-of-distribution route.
2. **Strict structured-output validation is a code.** It detects a corrupted/incomplete output frame and refuses to write it to the ledger. That is exactly the role of a parity check.
3. **Autonomy gating maps to channel capacity.** Red lanes restrict $R$, the effective rate, when stakes or complexity would push the workflow above $C$. Green lanes permit higher $R$ where capacity exists.
4. **Assumption-watch downgrades are governed error correction.** They preserve the property that green authority cannot be granted by the orchestrator alone; it must remain consistent with substrate signals.
5. **Codex task packets are compressed transmissions.** The data processing inequality applies: a packet cannot encode more substrate authority than was preserved through the channel.

## Safe design questions

For each candidate orchestrator change or new prompt/route:

1. What is the authoritative source for this route/action (substrate registry, route map, autonomy policy)?
2. How is the source encoded so the channel preserves it (pinned manifest, allowlist, schema)?
3. Where can channel noise enter (prompt drift, stale clone, partial output, missing fixture)?
4. Is the workflow inside capacity (validator coverage, reviewer bandwidth, lake throughput)?
5. What redundancy detects regression (route allowlist, structured-output validator, ledger + packet duality)?
6. What error-correction path applies (autonomy downgrade, exception emission, governed promotion)?
7. What residual classification uncertainty remains, and is the autonomy lane consistent with it?

## Non-goals

- This note does not introduce $H(R \mid e)$ or $D_{\mathrm{KL}}$ as required runtime gauges. Today the classifier is deterministic and substrate baselines are not published.
- This note does not propose new route IDs, event classes, autonomy lanes, or harness levels. Any such change must be proposed through the governed path.
- This note does not assert that Shannon math proves the orchestrator's design. The orchestrator's design comes from substrate governance, the autonomy law, and the contract-lock discipline.

## References

Conceptual only.

- Claude E. Shannon, "A Mathematical Theory of Communication," 1948.
- Thomas M. Cover and Joy A. Thomas, *Elements of Information Theory*, Wiley.
- David J. C. MacKay, *Information Theory, Inference, and Learning Algorithms*, Cambridge University Press.
- Workspace-shared master file: `../_shared/SHANNON_INFORMATION_THEORY_FOR_AI_GOVERNANCE_MASTER.md`.
