# skill: microsoft-signal-collector
Purpose: Collect authorized Microsoft 365 signals that corroborate workflow stories and discover hidden process evidence.
Use when: A workflow may be evidenced by Teams, Outlook, SharePoint, OneDrive, Planner, To Do, Purview audit, Entra ID, Power Automate, or Fabric.
Fetch only authorized data for the approved scope.
Prefer metadata, references, hashes, and summaries over full payloads.
Use Teams transcripts to support voice-to-workflow extraction when authorized.
Use Entra and Microsoft Graph data to support org context.
Use SharePoint and OneDrive metadata to identify documents and last-modified evidence.
Use Outlook calendar and meeting metadata to identify handoffs and recurring process rituals.
Use Planner and task data to identify work queues, owners, status transitions, and due dates.
Use Purview audit or Management Activity records to corroborate user, file, admin, system, and policy actions.
Use Power Automate process and task mining outputs to corroborate observed process variants.
Record every source reference, permission scope, and access reason.
Do not pull tenant-wide content without approved scope.
Do not treat Microsoft telemetry as complete truth.
Do not store raw transcripts or sensitive content in the Exception Lake.
Do not use employee surveillance as a default workflow discovery method.
Output microsoft_signal_packet, authorized_source_refs, evidence_confidence_notes, missing_signal_report, and privacy_boundary_flags.
