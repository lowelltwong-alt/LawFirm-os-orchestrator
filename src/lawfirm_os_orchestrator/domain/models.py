from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceClaimRef(StrictModel):
    claim_ref: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class SyntheticExceptionInput(StrictModel):
    schema_version: str = "1.0"
    input_id: str = Field(min_length=1)
    synthetic: bool
    contains_real_client_data: bool = False
    contains_real_matter_data: bool = False
    source_type: str = Field(min_length=1)
    route_hint: str | None = None
    confidentiality_label: Literal["synthetic"] = "synthetic"
    privilege_label: Literal["none"] = "none"
    source_claim_refs: list[SourceClaimRef] = Field(min_length=1)
    payload: dict[str, Any]

    @model_validator(mode="after")
    def enforce_synthetic_only(self) -> "SyntheticExceptionInput":
        if not self.synthetic:
            raise ValueError("synthetic must be true")
        if self.contains_real_client_data or self.contains_real_matter_data:
            raise ValueError("real client or matter data flags are not allowed")
        return self


class CanonicalRoute(StrictModel):
    route_id: str
    event_class: str
    allowed_source_layers: list[str] = []
    promotion_gate_required: bool = True
    allowed_raw_actions: list[str] = []
    prohibited_direct_actions: list[str] = []


class SubstrateManifest(StrictModel):
    manifest_id: str
    manifest_version: str = "1.0"
    policy_bundle_id: str = "runtime-policy-v1"
    canonical_schema_keys: list[str] = []
    registry_refs: list[str] = []


class ClassificationResult(StrictModel):
    route_id: str
    event_class: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    reason_codes: list[str] = Field(default_factory=list)
    supporting_claim_refs: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str | None = None
    abstain_reason: str | None = None


class ValidationResult(StrictModel):
    validator: str
    status: Literal["pass", "fail"]
    reason: str | None = None


class LakeReceipt(StrictModel):
    mode: Literal["disabled", "dry-run", "runtime-safe"]
    attempted: bool
    status: Literal["not_attempted", "accepted", "rejected"]
    receipt_id: str | None = None
    rejection_reasons: list[str] = Field(default_factory=list)
