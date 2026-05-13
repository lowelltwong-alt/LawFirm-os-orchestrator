# skill: tech-workflow-discoverer
Purpose: Expand vague technology steps into granular system, screen, field, status, queue, API, export, and portal behavior.
Use when: A person says work goes into BillBlast, Aderant, iManage, NetDocuments, Teams, Outlook, Excel, SharePoint, an insurance portal, or a billing system.
Ask what system the user starts in.
Ask what screen, module, queue, tab, report, form, dashboard, template, or portal page is used.
Ask what record is opened, created, edited, submitted, exported, imported, copied, reconciled, or approved.
Ask what fields are required.
Ask what statuses exist and what changes each status.
Ask what errors, rejections, validations, or warnings appear.
Ask whether data is retyped, pasted, downloaded, uploaded, emailed, or manually reconciled.
Ask what credentials, portal accounts, roles, or permissions are needed without collecting secrets.
Ask what confirmation, receipt, status, log, report, or email proves completion.
Ask whether the system has an API, export, nightly feed, audit log, or only UI access.
Create system_step records with system_name, module_hint, screen_hint, field_refs, status_refs, input_artifacts, output_artifacts, and evidence_refs.
Do not treat “goes into the system” as one step.
Do not treat an external insurance portal as outside the workflow.
Do not store credentials, secrets, session cookies, or unapproved screenshots.
Output system_step_map, portal_step_map, field_and_status_candidates, system_evidence_sources, and automation_surface_assessment.
