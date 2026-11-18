from __future__ import annotations

from typing import Iterable, List

from roi_gate.models import (
    EvalCase,
    GateDecisionReceipt,
    GateVerdict,
    InitiativeProposal,
    PilotTelemetry,
)


class ROIDecisionGateEngine:
    """Quantitative AI pilot ROI and stage-gate governance engine."""

    def evaluate_absent_info_rate(self, eval_cases: Iterable[EvalCase]) -> float:
        absent_cases = [case for case in eval_cases if case.expects_abstention]
        if not absent_cases:
            return 1.0
        abstained = sum(1 for case in absent_cases if case.model_abstained)
        return round(abstained / len(absent_cases), 4)

    def evaluate_pilot(
        self,
        proposal: InitiativeProposal,
        telemetry: PilotTelemetry,
        eval_cases: Iterable[EvalCase] | None = None,
    ) -> GateDecisionReceipt:
        baseline_monthly_cost = round(proposal.monthly_volume * proposal.baseline_unit_cost, 2)
        human_review_overhead = round(
            telemetry.human_review_hours_monthly * telemetry.human_hourly_rate, 2
        )
        ai_total_monthly_cost = round(
            telemetry.api_spend_monthly + human_review_overhead + proposal.fixed_monthly_infra_cost,
            2,
        )
        net_monthly_savings = round(baseline_monthly_cost - ai_total_monthly_cost, 2)

        if ai_total_monthly_cost > 0:
            roi_pct = round((net_monthly_savings / ai_total_monthly_cost) * 100.0, 2)
        else:
            roi_pct = 0.0

        payback_months = (
            round(proposal.implementation_cost / net_monthly_savings, 2)
            if net_monthly_savings > 0 and proposal.implementation_cost > 0
            else (0.0 if net_monthly_savings > 0 else None)
        )

        absent_rate = (
            self.evaluate_absent_info_rate(eval_cases)
            if eval_cases is not None
            else telemetry.absent_info_abstention_rate
        )
        absent_info_pass = absent_rate >= proposal.min_absent_info_abstention_rate
        hallucination_pass = telemetry.hallucination_rate <= proposal.max_hallucination_rate
        roi_pass = net_monthly_savings > 0 and roi_pct >= proposal.target_roi_pct

        failed_gates: List[str] = []
        if not absent_info_pass:
            failed_gates.append(
                f"absent_info_abstention_rate {absent_rate:.2%} < {proposal.min_absent_info_abstention_rate:.2%}"
            )
        if not hallucination_pass:
            failed_gates.append(
                f"hallucination_rate {telemetry.hallucination_rate:.2%} > {proposal.max_hallucination_rate:.2%}"
            )
        if not roi_pass:
            failed_gates.append(
                f"roi_pct {roi_pct:.2f}% < target {proposal.target_roi_pct:.2f}% or negative savings"
            )

        verdict: GateVerdict
        if not failed_gates:
            verdict = "GO"
        elif absent_info_pass and hallucination_pass and net_monthly_savings > 0:
            verdict = "CONDITIONAL_GO"
        elif net_monthly_savings <= 0:
            verdict = "NO_GO"
        else:
            verdict = "HOLD"

        return GateDecisionReceipt(
            initiative_id=proposal.initiative_id,
            baseline_monthly_cost=baseline_monthly_cost,
            ai_total_monthly_cost=ai_total_monthly_cost,
            human_review_overhead=human_review_overhead,
            net_monthly_savings=net_monthly_savings,
            roi_pct=roi_pct,
            payback_months=payback_months,
            absent_info_pass=absent_info_pass,
            hallucination_pass=hallucination_pass,
            roi_pass=roi_pass,
            verdict=verdict,
            failed_gates=failed_gates,
        )
