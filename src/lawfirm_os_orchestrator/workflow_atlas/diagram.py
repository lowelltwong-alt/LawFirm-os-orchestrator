from __future__ import annotations

import re

from lawfirm_os_orchestrator.workflow_atlas.models import WorkflowFragment


def _label(text: str, limit: int = 64) -> str:
    cleaned = re.sub(r"[\[\]{}<>|]", " ", text).replace('"', "'")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:limit] + ("..." if len(cleaned) > limit else "")


def render_mermaid(fragment: WorkflowFragment) -> str:
    lines = ["flowchart TD", f"    T([Trigger: {_label(fragment.trigger, 80)}])"]
    previous = "T"
    for step in fragment.steps:
        node = step.step_id
        system = f"\\nSystem: {_label(step.system)}" if step.system else ""
        lines.append(f"    {node}[{_label(step.actor_role)}: {_label(step.activity)}{system}]")
        lines.append(f"    {previous} --> {node}")
        previous = node
        if step.exceptions:
            exc_node = f"{node}_EX"
            lines.append(f"    {exc_node}{{Exception or rework?}}")
            lines.append(f"    {node} --> {exc_node}")
            lines.append(f"    {exc_node} -->|yes| REVIEW[Human review / capture gap]")
            lines.append(f"    {exc_node} -->|no| CONTINUE_{node}[Continue]")
            previous = f"CONTINUE_{node}"
    if fragment.decision_points:
        for decision in fragment.decision_points[:3]:
            dnode = decision.decision_id
            lines.append(f"    {dnode}{{{_label(decision.question, 90)}}}")
            lines.append(f"    {previous} --> {dnode}")
            for idx, path in enumerate(decision.paths or ["path_a", "path_b"]):
                pnode = f"{dnode}_P{idx+1}"
                lines.append(f"    {pnode}[{_label(path)}]")
                lines.append(f"    {dnode} --> {pnode}")
            previous = dnode
    lines.append("    REVIEW --> OUT[Meeting prep / instrumentation / pilot decision]")
    return "\n".join(lines) + "\n"
