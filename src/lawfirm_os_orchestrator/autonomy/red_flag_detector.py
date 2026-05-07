from __future__ import annotations

from lawfirm_os_orchestrator.research.research_signal_ingest import ResearchSignal

HARD_RED_TRIGGERS: frozenset[str] = frozenset(
    {
        "real_client_data",
        "privileged_content",
        "external_write_send_or_publish",
        "canon_mutation",
        "new_route_id",
        "new_event_class",
        "legal_billing_finality",
        "client_visible_finality",
        "secret_exposure",
        "destructive_operation_risk",
        "approval_bypass",
        "attempted_human_green_restoration_by_agent",
        "live_research_radar_automation",
        "scheduled_job",
        "model_call",
        "external_api_network_call",
        "runtime_mutation_of_substrate",
    }
)


def hard_red_triggers(signal: ResearchSignal) -> list[str]:
    triggers = sorted(set(signal.hard_red_triggers) & HARD_RED_TRIGGERS)
    if signal.indicates_green_restoration:
        triggers.append("attempted_human_green_restoration_by_agent")
    return sorted(set(triggers))


def has_hard_red(signal: ResearchSignal) -> bool:
    return bool(hard_red_triggers(signal))
