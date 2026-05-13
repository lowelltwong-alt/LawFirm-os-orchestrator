from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.models import ClassificationResult, LakeReceipt, SyntheticExceptionInput
from lawfirm_os_orchestrator.lake.envelope import build_exception_event_payload
from lawfirm_os_orchestrator.substrate.reader import SubstrateSnapshot
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import write_json


class DisabledLakeClient:
    mode = "disabled"

    def handoff(self, packet: dict[str, Any], packet_dir: Path, **_: Any) -> LakeReceipt:
        return LakeReceipt(mode="disabled", attempted=False, status="not_attempted")


class DryRunLakeClient:
    mode = "dry-run"

    def handoff(self, packet: dict[str, Any], packet_dir: Path, **_: Any) -> LakeReceipt:
        request = {"mode": self.mode, "packet_hash": packet.get("packet_hash"), "evidence_id": packet.get("evidence_id")}
        receipt = LakeReceipt(mode="dry-run", attempted=True, status="accepted", receipt_id=new_id("lake_receipt"))
        write_json(packet_dir / "ingest_request.json", request)
        write_json(packet_dir / "ingest_receipt.json", receipt.model_dump())
        return receipt


class RuntimeSafeLakeClient:
    mode = "runtime-safe"

    def handoff(
        self,
        packet: dict[str, Any],
        packet_dir: Path,
        *,
        event: SyntheticExceptionInput | None = None,
        snapshot: SubstrateSnapshot | None = None,
        classification: ClassificationResult | None = None,
    ) -> LakeReceipt:
        if os.environ.get("LAWFIRM_OS_ORCHESTRATOR_ALLOW_RUNTIME_SAFE") != "true":
            return LakeReceipt(mode="runtime-safe", attempted=False, status="rejected", rejection_reasons=["runtime-safe mode requires config allow switch"])
        if event is None or snapshot is None or classification is None:
            return LakeReceipt(mode="runtime-safe", attempted=False, status="rejected", rejection_reasons=["runtime-safe mode requires event, snapshot, and classification context"])
        try:
            from exceptions_lake_runtime.api import build_synthetic_envelope, ingest_synthetic_event
        except ImportError as exc:
            return LakeReceipt(mode="runtime-safe", attempted=False, status="rejected", rejection_reasons=[f"exceptions_lake_runtime is unavailable: {exc}"])

        payload = build_exception_event_payload(
            packet=packet,
            event=event,
            classification=classification,
            snapshot=snapshot,
        )
        envelope = build_synthetic_envelope(payload, actor="lawfirm-os-orchestrator")
        write_json(packet_dir / "runtime_safe_exception_event.json", payload)
        write_json(packet_dir / "runtime_safe_ingest_envelope.json", envelope)
        try:
            result = ingest_synthetic_event(envelope)
        except Exception as exc:
            write_json(packet_dir / "runtime_safe_ingest_error.json", {"error": str(exc)})
            return LakeReceipt(mode="runtime-safe", attempted=True, status="rejected", rejection_reasons=[str(exc)])
        write_json(packet_dir / "runtime_safe_ingest_result.json", result)
        if result.get("accepted") is True:
            receipt_id = result.get("audit_record", {}).get("audit_id") or new_id("lake_receipt")
            return LakeReceipt(mode="runtime-safe", attempted=True, status="accepted", receipt_id=str(receipt_id))
        reasons = result.get("validation", {}).get("errors") or result.get("policy", {}).get("reasons") or ["Exception Lake rejected runtime-safe ingest"]
        return LakeReceipt(mode="runtime-safe", attempted=True, status="rejected", rejection_reasons=[str(reason) for reason in reasons])


def build_lake_client(mode: str):
    if mode == "disabled":
        return DisabledLakeClient()
    if mode == "dry-run":
        return DryRunLakeClient()
    if mode == "runtime-safe":
        return RuntimeSafeLakeClient()
    raise ValueError(f"Unsupported lake mode: {mode}")
