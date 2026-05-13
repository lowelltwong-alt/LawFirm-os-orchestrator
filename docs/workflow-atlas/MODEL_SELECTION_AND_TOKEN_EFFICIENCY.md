# Workflow Atlas Model Selection and Token Efficiency

Workflow Atlas should route AI work by task class, risk, context size, and evidence need.

The seed includes `workflow_atlas/model_policy.py` as a provider-agnostic model-class scorer.

It recommends a class such as `small_structured_extractor`, `medium_workflow_reasoner`, or `large_governance_reasoner`.

It does not name a vendor model; the Semantic Substrate model-policy registry should map model classes to approved providers.

Use small structured extractors for low-risk transcript atom extraction.

Use medium workflow reasoners for diagram synthesis, contradiction analysis, and priority coloring.

Use large governance reasoners only for high-risk ambiguity, ontology review packets, or cross-system digital-twin reasoning.

Always baseline quality first, then optimize cost and latency after evals prove the smaller class is good enough.
