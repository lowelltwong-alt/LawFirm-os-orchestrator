from __future__ import annotations

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.workflow_atlas.models import MuskAlgorithmReview, WorkflowFragment

DELETE_HINTS = ["manual", "copy", "paste", "retype", "spreadsheet", "email", "duplicate", "redo", "rewrite"]
ACCELERATE_HINTS = ["delay", "wait", "queue", "approval", "stuck", "late"]
SIDE_EFFECT_HINTS = ["send", "submit", "approve", "file", "publish", "write", "update"]


def review_with_musk_algorithm(fragment: WorkflowFragment) -> MuskAlgorithmReview:
    requirement_questions: list[str] = []
    deletion_candidates: list[str] = []
    simplification_candidates: list[str] = []
    acceleration_candidates: list[str] = []
    automation_candidates: list[str] = []
    must_not_automate_yet: list[str] = []

    for step in fragment.steps:
        requirement_questions.append(f"Who specifically requires step {step.step_id}: `{step.activity}`; is it client, court, carrier, law, policy, system limit, or habit?")
        low = f"{step.activity} {step.system or ''}".lower()
        if any(hint in low for hint in DELETE_HINTS):
            deletion_candidates.append(f"{step.step_id}: Try deleting or reducing `{step.activity}` before optimizing it.")
        if step.system and len(step.input_artifacts) >= 2:
            simplification_candidates.append(f"{step.step_id}: Simplify artifact flow around `{step.system}` and remove duplicate entry if possible.")
        if any(hint in low for hint in ACCELERATE_HINTS):
            acceleration_candidates.append(f"{step.step_id}: Accelerate only after the requirement and deletion checks pass.")
        if any(hint in low for hint in SIDE_EFFECT_HINTS):
            must_not_automate_yet.append(f"{step.step_id}: Side-effect step requires approval and evidence before automation: `{step.activity}`.")
        elif step.system:
            automation_candidates.append(f"{step.step_id}: Candidate for AI check/draft/recommend after deletion and simplification: `{step.activity}`.")

    if not deletion_candidates:
        deletion_candidates.append("No obvious deletion candidate found; ask reviewers to challenge every handoff, checklist, and approval before automation.")
    if not automation_candidates:
        automation_candidates.append("No safe automation candidate yet; use AI to ask better questions and capture evidence first.")

    return MuskAlgorithmReview(
        musk_review_id=new_id("musk"),
        workflow_fragment_id=fragment.workflow_fragment_id,
        requirement_questions=requirement_questions[:12],
        deletion_candidates=deletion_candidates[:12],
        simplification_candidates=simplification_candidates[:12],
        acceleration_candidates=acceleration_candidates[:12],
        automation_candidates_after_simplification=automation_candidates[:12],
        must_not_automate_yet=must_not_automate_yet[:12],
    )
