from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

from .contracts import LegalKnowledgeReceipt, LegalKnowledgeRequest


class DisabledLegalKnowledgeClient:
    mode = "disabled"

    def run(self, request: LegalKnowledgeRequest) -> LegalKnowledgeReceipt:
        return LegalKnowledgeReceipt(mode="disabled", attempted=False, status="not_attempted")


class LocalLegalKnowledgeClient:
    """Local import adapter for the sibling Legal Knowledge Runtime.

    This is intentionally an adapter seam. The Orchestrator does not own legal
    knowledge schemas, does not parse full legal document content, and does not
    mutate the Semantic Substrate.
    """

    mode = "local"

    def run(self, request: LegalKnowledgeRequest) -> LegalKnowledgeReceipt:
        if not request.synthetic_only:
            return LegalKnowledgeReceipt(mode="local", attempted=False, status="blocked", errors=["MVP requires synthetic_only"])
        try:
            cli = import_module("lawfirm_os_legal_knowledge.cli")
        except Exception as exc:
            return LegalKnowledgeReceipt(mode="local", attempted=False, status="failed", errors=[f"legal knowledge runtime unavailable: {exc}"])

        if request.operation == "ingest_preflight":
            args = SimpleNamespace(
                manifest=request.manifest_path,
                substrate=request.substrate_path,
                out_dir=request.out_dir,
                stdout="json",
            )
            code, payload = cli.run_ingest_preflight(args)
        elif request.operation == "assemble_bundle":
            if not request.bundle_type:
                return LegalKnowledgeReceipt(mode="local", attempted=False, status="blocked", errors=["bundle_type is required for assemble_bundle"])
            args = SimpleNamespace(
                manifest=request.manifest_path,
                bundle_type=request.bundle_type,
                out_dir=request.out_dir,
                stdout="json",
            )
            code, payload = cli.run_assemble_bundle(args)
        else:  # pragma: no cover
            return LegalKnowledgeReceipt(mode="local", attempted=False, status="blocked", errors=["unsupported operation"])

        if code != 0:
            return LegalKnowledgeReceipt(
                mode="local",
                attempted=True,
                status="blocked" if payload.get("status") == "blocked" else "failed",
                run_id=payload.get("run_id"),
                evidence_packet_path=payload.get("evidence_packet_path"),
                errors=payload.get("failures", []) or [payload.get("error", "legal knowledge runtime failed")],
            )
        return LegalKnowledgeReceipt(
            mode="local",
            attempted=True,
            status="accepted",
            run_id=payload.get("run_id"),
            evidence_packet_path=payload.get("evidence_packet_path"),
            errors=[],
        )
