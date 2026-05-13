from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ModelTaskProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    task_name: str
    complexity: float = Field(ge=0.0, le=1.0)
    output_risk: float = Field(ge=0.0, le=1.0)
    context_tokens_estimate: int = Field(ge=0)
    latency_sensitivity: float = Field(ge=0.0, le=1.0)
    cost_sensitivity: float = Field(ge=0.0, le=1.0)
    evidence_gap: float = Field(ge=0.0, le=1.0)


MODEL_CLASSES = {
    "small_structured_extractor": {"quality": 0.62, "relative_cost": 0.18, "latency": 0.2, "risk_ceiling": 0.35},
    "medium_workflow_reasoner": {"quality": 0.78, "relative_cost": 0.45, "latency": 0.45, "risk_ceiling": 0.65},
    "large_governance_reasoner": {"quality": 0.9, "relative_cost": 1.0, "latency": 0.8, "risk_ceiling": 1.0},
}


def score_model_class(profile: ModelTaskProfile) -> dict:
    """AI-agnostic token-efficiency router for Workflow Atlas tasks.

    The score balances quality need, risk, latency, and relative token cost.
    It returns a model class, not a vendor model name.
    """
    results = []
    quality_need = max(profile.complexity, profile.output_risk, profile.evidence_gap)
    for model_class, spec in MODEL_CLASSES.items():
        if profile.output_risk > spec["risk_ceiling"]:
            allowed = False
            score = 0.0
        else:
            allowed = True
            quality_fit = 1.0 - abs(spec["quality"] - quality_need)
            cost_penalty = spec["relative_cost"] * (0.4 + profile.cost_sensitivity)
            latency_penalty = spec["latency"] * profile.latency_sensitivity
            context_penalty = min(0.3, profile.context_tokens_estimate / 250_000)
            score = max(0.0, quality_fit - cost_penalty - latency_penalty - context_penalty)
        results.append({"model_class": model_class, "allowed": allowed, "token_efficiency_score": round(score, 4), "spec": spec})
    results.sort(key=lambda r: r["token_efficiency_score"], reverse=True)
    return {
        "schema_type": "workflow-atlas-model-class-recommendation",
        "schema_version": "v1",
        "task_name": profile.task_name,
        "recommended_model_class": results[0]["model_class"],
        "candidates": results,
        "authority_boundary": {
            "model_class_only": True,
            "provider_agnostic": True,
            "policy_registry_must_map_class_to_vendor_model": True,
        },
    }
