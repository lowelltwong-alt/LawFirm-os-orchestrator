# skill: digital-twin-candidate-builder
Purpose: Convert reviewed workflow fragments into candidate graph edges, ontology deltas, and digital-twin updates.
Use when: A workflow fragment has survived visual correction and evidence checks.
Create graph nodes for workflow, role, system, artifact, decision, exception, constraint, metric, and handoff.
Connect fragments through shared roles, systems, artifacts, constraints, exceptions, and downstream metrics.
Mark every new node and edge as candidate until semantic review.
Attach evidence refs, transcript hashes, correction events, and integrity scores to each candidate edge.
Separate spoken, corrected, corroborated, observed, and approved truth tiers.
Do not update the digital twin as firm truth without approval.
Do not merge same-sounding terms without synonym or same-as review.
Output digital_twin_candidate_update, fragment_edges, ontology_delta_candidate, and promotion_review_packet.
