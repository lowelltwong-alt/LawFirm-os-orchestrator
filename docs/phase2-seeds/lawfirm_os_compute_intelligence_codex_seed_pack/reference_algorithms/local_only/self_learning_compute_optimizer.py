# SPDX-License-Identifier: MIT
"""Local-only naive compute outcome aggregator.

Version: compute-intelligence-seed-v2
Provenance: lawfirm_os_compute_intelligence_codex_seed_pack v2.

This is a placeholder aggregator, not a production optimizer. It produces human-
review proposals only. It does not self-modify and does not execute actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Literal

__all__ = ["Authority", "Outcome", "recommend_bucket_shift"]

Authority = Literal["decision_support", "advisory", "proposal"]
AUTHORITY: Authority = "proposal"
MIN_SAMPLE_SIZE_FOR_STRONG_RECOMMENDATION = 30


@dataclass(frozen=True)
class Outcome:
    bucket: str
    spend: float
    value: float
    risk_event: bool = False
    policy_regime_id: str = "unknown"
    authority: Authority = AUTHORITY


def _wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - half), min(1.0, center + half)


def recommend_bucket_shift(outcomes: Iterable[Outcome], *, current_policy_regime_id: str | None = None) -> dict:
    rows = list(outcomes)
    if current_policy_regime_id is not None:
        rejected = [r for r in rows if r.policy_regime_id != current_policy_regime_id]
        rows = [r for r in rows if r.policy_regime_id == current_policy_regime_id]
    else:
        rejected = []

    by_bucket: dict[str, list[Outcome]] = {}
    for outcome in rows:
        by_bucket.setdefault(outcome.bucket, []).append(outcome)

    recommendations = []
    for bucket, bucket_rows in by_bucket.items():
        spend = sum(max(0.0, r.spend) for r in bucket_rows)
        value = sum(max(0.0, r.value) for r in bucket_rows)
        risk_events = sum(1 for r in bucket_rows if r.risk_event)
        n = len(bucket_rows)
        roi = value / max(spend, 0.1)
        non_risk_successes = max(0, n - risk_events)
        ci_low, ci_high = _wilson_interval(non_risk_successes, n)

        if risk_events:
            action = "propose_reduce_or_add_validation_for_human_review"
        elif n < MIN_SAMPLE_SIZE_FOR_STRONG_RECOMMENDATION:
            action = "propose_collect_more_evidence_for_human_review"
        elif roi > 1.5 and ci_low >= 0.80:
            action = "propose_increase_for_human_review"
        elif roi < 0.5:
            action = "propose_decrease_or_redesign_for_human_review"
        else:
            action = "propose_hold_for_human_review"
        recommendations.append({
            "bucket": bucket,
            "sample_size": n,
            "roi": roi,
            "risk_events": risk_events,
            "non_risk_success_ci_low": ci_low,
            "non_risk_success_ci_high": ci_high,
            "recommended_action": action,
        })

    return {
        "authority": AUTHORITY,
        "recommendations": recommendations,
        "rejected_cross_regime_evidence_count": len(rejected),
        "authority_note": "optimizer_recommendations_are_proposals_only_for_human_review",
        "forbidden_actions": [
            "self_modify",
            "restore_green",
            "mutate_canon",
            "external_write",
            "model_call",
            "network_call",
            "auto_apply_budget_change",
        ],
    }
