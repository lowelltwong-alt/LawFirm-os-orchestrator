from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class LegalKnowledgeRequest(StrictModel):
    operation: Literal["ingest_preflight", "assemble_bundle"]
    manifest_path: str = Field(min_length=1)
    substrate_path: str | None = None
    bundle_type: str | None = None
    out_dir: str = ".lawfirm-os-legal-knowledge/runs"
    synthetic_only: bool = True


class LegalKnowledgeReceipt(StrictModel):
    mode: Literal["disabled", "local"]
    attempted: bool
    status: Literal["not_attempted", "accepted", "blocked", "failed"]
    run_id: str | None = None
    evidence_packet_path: str | None = None
    errors: list[str] = Field(default_factory=list)
