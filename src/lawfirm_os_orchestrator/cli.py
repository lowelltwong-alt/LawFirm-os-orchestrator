from __future__ import annotations

import argparse
import json

from lawfirm_os_orchestrator.commands.autonomy_harness import (
    run_generate_codex_task,
    run_classify_autonomy,
    run_select_harness,
    run_watch_green_lanes,
)
from lawfirm_os_orchestrator.commands.classify_exception import (
    run as run_classify_exception,
)
from lawfirm_os_orchestrator.commands.intake_workflow import run as run_intake_workflow
from lawfirm_os_orchestrator.commands.learning import run as run_learning
from lawfirm_os_orchestrator.commands.research_radar import run as run_research_radar
from lawfirm_os_orchestrator.commands.workflow_atlas import run as run_workflow_atlas
from lawfirm_os_orchestrator.policy.agent_hostile_controls import (
    DEFAULT_AGENT_CONTROL_SOURCE,
    DEFAULT_CLASSIFIER_TOOL_ID,
    DEFAULT_CLASSIFY_PROMPT_REF,
    DEFAULT_TENANT_ID,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lawfirm-os-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)
    autonomy = sub.add_parser("classify-autonomy")
    autonomy.add_argument("--action", required=True)
    autonomy.add_argument("--out", required=True)
    autonomy.add_argument("--stdout", choices=["json", "text"], default="text")
    harness = sub.add_parser("select-harness")
    harness.add_argument("--autonomy", required=True)
    harness.add_argument("--scorecard", required=True)
    harness.add_argument("--out", required=True)
    harness.add_argument("--stdout", choices=["json", "text"], default="text")
    watcher = sub.add_parser("watch-green-lanes")
    watcher.add_argument("--signals", required=True)
    watcher.add_argument("--lanes", required=True)
    watcher.add_argument("--out", required=True)
    watcher.add_argument("--stdout", choices=["json", "text"], default="text")
    task_packet = sub.add_parser("generate-codex-task")
    task_packet.add_argument("--opportunity", required=True)
    task_packet.add_argument("--scorecard", required=True)
    task_packet.add_argument("--autonomy", required=True)
    task_packet.add_argument("--harness", required=True)
    task_packet.add_argument("--out", required=True)
    task_packet.add_argument("--stdout", choices=["json", "text"], default="text")
    classify = sub.add_parser("classify-exception")
    classify.add_argument("--input", required=True)
    classify.add_argument("--substrate", default="tests/fixtures/substrate")
    classify.add_argument("--ledger-dir", default=".lawfirm-os-orchestrator/ledger")
    classify.add_argument("--packet-out", default=".lawfirm-os-orchestrator/runs")
    classify.add_argument(
        "--lake-mode",
        choices=["disabled", "dry-run", "runtime-safe"],
        default="disabled",
    )
    classify.add_argument("--stdout", choices=["json", "text"], default="json")
    classify.add_argument("--agent-id")
    classify.add_argument("--delegating-user-id")
    classify.add_argument("--tenant-id", default=DEFAULT_TENANT_ID)
    classify.add_argument("--tool-id", default=DEFAULT_CLASSIFIER_TOOL_ID)
    classify.add_argument(
        "--agent-control-source",
        choices=["substrate", "local-fixture", "local_fixture"],
        default=DEFAULT_AGENT_CONTROL_SOURCE,
    )
    classify.add_argument("--agent-control-substrate")
    classify.add_argument("--agent-control-contract-sha")
    classify.add_argument("--tool-manifest")
    classify.add_argument("--prompt-ref", default=DEFAULT_CLASSIFY_PROMPT_REF)
    classify.add_argument("--prompt-registry")
    classify.add_argument("--revocation-registry")

    atlas = sub.add_parser("workflow-atlas")
    atlas_sub = atlas.add_subparsers(dest="workflow_atlas_command", required=True)
    prep = atlas_sub.add_parser("prepare-meeting")
    prep.add_argument("--topic", required=True)
    prep.add_argument(
        "--intake",
        action="append",
        required=True,
        help="Repeatable transcript or intake file path",
    )
    prep.add_argument("--substrate", default="tests/fixtures/substrate")
    prep.add_argument("--ledger-dir", default=".lawfirm-os-orchestrator/ledger")
    prep.add_argument("--out-dir", default=".lawfirm-os-orchestrator/workflow_atlas")
    prep.add_argument(
        "--lake-mode",
        choices=["disabled", "dry-run", "runtime-safe"],
        default="disabled",
    )
    prep.add_argument("--stdout", choices=["json", "text"], default="json")

    intake = sub.add_parser("intake")
    intake_sub = intake.add_subparsers(dest="intake_command", required=True)
    owner_packet = intake_sub.add_parser("prepare-owner-packet")
    owner_packet.add_argument("--input", required=True)
    owner_packet.add_argument(
        "--out-dir",
        default=".lawfirm-os-orchestrator/intake_owner_review",
    )
    owner_packet.add_argument(
        "--ledger-dir",
        default=".lawfirm-os-orchestrator/ledger",
    )
    owner_packet.add_argument("--stdout", choices=["json", "text"], default="json")
    lake_review = intake_sub.add_parser("build-lake-admission-review-packet")
    lake_review.add_argument("--owner-packet", required=True)
    lake_review.add_argument(
        "--out-dir",
        default=".lawfirm-os-orchestrator/intake_lake_admission_review",
    )
    lake_review.add_argument(
        "--ledger-dir",
        default=".lawfirm-os-orchestrator/ledger",
    )
    lake_review.add_argument("--stdout", choices=["json", "text"], default="json")

    radar = sub.add_parser("research-radar")
    radar_sub = radar.add_subparsers(dest="research_command", required=True)
    import_local = radar_sub.add_parser("import-local")
    import_local.add_argument("--input", required=True)
    import_local.add_argument(
        "--out", default=".lawfirm-os-orchestrator/research/signals.jsonl"
    )
    import_local.add_argument("--stdout", choices=["json", "text"], default="text")
    list_signals = radar_sub.add_parser("list-signals")
    list_signals.add_argument(
        "--signals", default=".lawfirm-os-orchestrator/research/signals.jsonl"
    )
    list_signals.add_argument("--stdout", choices=["json", "text"], default="text")

    learning = sub.add_parser("learning")
    learning_sub = learning.add_subparsers(dest="learning_command", required=True)
    shadow = learning_sub.add_parser("run-shadow-eval")
    shadow.add_argument("--proposal", required=True)
    shadow.add_argument(
        "--fixture", default="evals/fixtures/classify_exception_cases.jsonl"
    )
    shadow.add_argument("--gold", default="evals/gold/classify_exception_gold.jsonl")
    shadow.add_argument("--substrate", default="tests/fixtures/substrate")
    shadow.add_argument(
        "--artifacts", default=".lawfirm-os-orchestrator/shadow_eval/artifacts"
    )
    shadow.add_argument(
        "--out", default=".lawfirm-os-orchestrator/shadow_eval/latest_shadow_eval.json"
    )
    shadow.add_argument("--stdout", choices=["json", "text"], default="text")
    proposal = learning_sub.add_parser("build-upgrade-proposal")
    proposal.add_argument("--input", required=True)
    proposal.add_argument("--out", default=".lawfirm-os-orchestrator/upgrade_proposals")
    proposal.add_argument("--stdout", choices=["json", "text"], default="text")
    task = learning_sub.add_parser("render-codex-task")
    task.add_argument("--input", required=True)
    task.add_argument(
        "--out", default=".lawfirm-os-orchestrator/codex_task_drafts/example"
    )
    task.add_argument("--stdout", choices=["json", "text"], default="text")
    insight = learning_sub.add_parser("score-insight")
    insight.add_argument("--input", required=True)
    insight.add_argument("--out")
    insight.add_argument("--stdout", choices=["json", "text"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "classify-autonomy":
        code, summary = run_classify_autonomy(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "select-harness":
        code, summary = run_select_harness(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "watch-green-lanes":
        code, summary = run_watch_green_lanes(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "generate-codex-task":
        code, summary = run_generate_codex_task(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "classify-exception":
        code, summary = run_classify_exception(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code

    if args.command == "workflow-atlas":
        code, summary = run_workflow_atlas(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "intake":
        code, summary = run_intake_workflow(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "research-radar":
        code, summary = run_research_radar(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    if args.command == "learning":
        code, summary = run_learning(args)
        if args.stdout == "json":
            print(json.dumps(summary, indent=2, sort_keys=False))
        else:
            print(summary.get("status", "unknown"))
        return code
    parser.error("unknown command")
    return 2
