from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.models import LakeReceipt
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import write_json


class DisabledLakeClient:
    mode = "disabled"

    def handoff(self, packet: dict[str, Any], packet_dir: Path) -> LakeReceipt:
        return LakeReceipt(mode="disabled", attempted=False, status="not_attempted")


class DryRunLakeClient:
    mode = "dry-run"

    def handoff(self, packet: dict[str, Any], packet_dir: Path) -> LakeReceipt:
        request = {"mode": self.mode, "packet_hash": packet.get("packet_hash"), "evidence_id": packet.get("evidence_id")}
        receipt = LakeReceipt(mode="dry-run", attempted=True, status="accepted", receipt_id=new_id("lake_receipt"))
        write_json(packet_dir / "ingest_request.json", request)
        write_json(packet_dir / "ingest_receipt.json", receipt.model_dump())
        return receipt


class RuntimeSafeLakeClient:
    mode = "runtime-safe"

    def handoff(self, packet: dict[str, Any], packet_dir: Path) -> LakeReceipt:
        if os.environ.get("LAWFIRM_OS_ORCHESTRATOR_ALLOW_RUNTIME_SAFE") != "true":
            return LakeReceipt(mode="runtime-safe", attempted=False, status="rejected", rejection_reasons=["runtime-safe mode requires config allow switch"])
        return LakeReceipt(mode="runtime-safe", attempted=False, status="rejected", rejection_reasons=["runtime-safe implementation intentionally not wired in MVP scaffold"])


def build_lake_client(mode: str):
    if mode == "disabled":
        return DisabledLakeClient()
    if mode == "dry-run":
        return DryRunLakeClient()
    if mode == "runtime-safe":
        return RuntimeSafeLakeClient()
    raise ValueError(f"Unsupported lake mode: {mode}")
