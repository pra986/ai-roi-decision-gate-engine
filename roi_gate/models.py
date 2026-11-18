from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal


GateVerdict = Literal["GO", "CONDITIONAL_GO", "HOLD", "NO_GO"]


@dataclass(frozen=True)
class InitiativeProposal:
    initiative_id: str
    name: str
    monthly_volume: int
    baseline_unit_cost: float
    fixed_monthly_infra_cost: float = 0.0
    implementation_cost: float = 0.0
    target_roi_pct: float = 25.0
    max_hallucination_rate: float = 0.05
    min_absent_info_abstention_rate: float = 0.90


@dataclass(frozen=True)
class PilotTelemetry:
    api_spend_monthly: float
    human_review_hours_monthly: float
    human_hourly_rate: float
    accuracy_rate: float
    hallucination_rate: float
    absent_info_abstention_rate: float


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt: str
    context_present: bool
    expects_abstention: bool
    model_abstained: bool
    answer_correct: bool


@dataclass(frozen=True)
class GateDecisionReceipt:
    initiative_id: str
    baseline_monthly_cost: float
    ai_total_monthly_cost: float
    human_review_overhead: float
    net_monthly_savings: float
    roi_pct: float
    payback_months: float | None
    absent_info_pass: bool
    hallucination_pass: bool
    roi_pass: bool
    verdict: GateVerdict
    failed_gates: List[str] = field(default_factory=list)
