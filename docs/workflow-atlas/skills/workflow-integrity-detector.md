# skill: workflow-integrity-detector
Purpose: Detect weak, contradictory, impossible, exaggerated, or adversarial workflow claims without making it personal.
Use when: Workflow claims affect priority, ontology, automation, risk, or digital-twin updates.
Classify each claim as spoken, documented, observed, logged, instrumented, or approved.
Prefer independent corroboration over repeated hearsay.
Compare voice claims against org chart, system logs, task data, audit logs, documents, emails, tickets, process-mining data, and Exception Lake events.
Run multiple same-job intakes and compare system involvement, step order, handoffs, and exception descriptions.
Lower confidence when a claim is unsupported, contradicted, impossible, stale, or outside firsthand knowledge.
Raise confidence only when evidence is specific, source-linked, and independently corroborated.
Flag likely manual-process-outside-lake when work lives in email, Teams, spreadsheets, portals, or hallway work.
Flag incentive distortion when a claim increases someone’s priority while shifting cost to another group.
Do not label a demographic group as unreliable.
Do not accuse a person; classify evidence quality and follow-up needs.
Output integrity_report, contradiction_findings, confidence_score, and recommended_integrity_action.
