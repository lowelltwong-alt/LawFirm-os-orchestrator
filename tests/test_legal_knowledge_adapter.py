from lawfirm_os_orchestrator.legal_knowledge import DisabledLegalKnowledgeClient, LegalKnowledgeRequest


def test_disabled_legal_knowledge_client_is_safe_by_default() -> None:
    request = LegalKnowledgeRequest(operation="ingest_preflight", manifest_path="examples/synthetic.json")
    receipt = DisabledLegalKnowledgeClient().run(request)
    assert receipt.mode == "disabled"
    assert receipt.attempted is False
    assert receipt.status == "not_attempted"


def test_legal_knowledge_request_blocks_non_synthetic_by_policy_shape() -> None:
    request = LegalKnowledgeRequest(operation="assemble_bundle", manifest_path="examples/synthetic.json", bundle_type="contract_review_context.v1")
    assert request.synthetic_only is True
