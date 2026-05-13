# skill: model-token-efficiency-router
Purpose: Choose the cheapest adequate model class for a Workflow Atlas step without sacrificing quality or governance.
Use when: A Workflow Atlas task may call an LLM for extraction, diagramming, contradiction analysis, scoring, or review.
Estimate complexity, output risk, context tokens, latency sensitivity, cost sensitivity, and evidence gap.
Choose a model class, not a vendor model name.
Use small structured extractors for low-risk atom extraction with strict schemas.
Use medium workflow reasoners for workflow synthesis and integrity analysis.
Use large governance reasoners only for high-risk ambiguity, ontology review, or cross-system digital-twin reasoning.
Start evals with the strongest approved class, then downgrade only when quality is proven.
Record model class, reason code, expected cost, actual tokens, and outcome in the run ledger.
Do not let token savings override protected risk boundaries.
Do not compare model performance across mixed risk or task cohorts.
Output model_class_recommendation, token_efficiency_score, reason_code, and eval_followup_needed.
