# skill: org-context-mapper
Purpose: Prepare organization context so the workflow agent knows reporting lines, departments, roles, groups, and likely handoffs.
Use when: A workflow intake mentions a person, department, role, approver, owner, queue, group, team, office, or escalation path.
Separate named people from functional roles.
Map people to department, title, manager, direct reports, group membership, team membership, office, and practice area when available.
Map formal reporting lines separately from actual workflow handoffs.
Identify possible approvers based on role, policy, and workflow authority.
Identify missing or conflicting org data.
Mark org context as time-bound because roles and reporting lines change.
Use org chart context to ask better follow-up questions.
Use org chart context to detect unlikely handoffs or missing stakeholders.
Do not assume the formal manager is the workflow owner.
Do not assume the workflow doer has approval authority.
Do not expose unnecessary personal data in workflow diagrams.
Output org_context_packet, role_person_mapping, authority_candidates, missing_org_data, and workflow_followup_questions.
