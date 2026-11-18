"""Pytest suite for ROIDecisionGateEngine."""

from roi_gate.engine import ROIDecisionGateEngine
from roi_gate.models import EvalCase, InitiativeProposal, PilotTelemetry


def _base_proposal() -> InitiativeProposal:
    return InitiativeProposal(
        initiative_id="PILOT-101",
        name="Claims Triage Assistant",
        monthly_volume=2000,
        baseline_unit_cost=5.0,
        fixed_monthly_infra_cost=500.0,
        implementation_cost=10000.0,
        target_roi_pct=25.0,
        max_hallucination_rate=0.05,
        min_absent_info_abstention_rate=0.90,
    )


def test_high_human_correction_overhead_flips_roi_negative() -> None:
    engine = ROIDecisionGateEngine()
    proposal = _base_proposal()
    # Baseline = 10,000; AI API + infra = 1,500; HITL = 160 * 60 = 9,600 -> total 11,100
    telemetry = PilotTelemetry(
        api_spend_monthly=1000.0,
        human_review_hours_monthly=160.0,
        human_hourly_rate=60.0,
        accuracy_rate=0.92,
        hallucination_rate=0.02,
        absent_info_abstention_rate=0.95,
    )
    receipt = engine.evaluate_pilot(proposal, telemetry)
    assert receipt.net_monthly_savings < 0
    assert receipt.roi_pass is False
    assert receipt.verdict == "NO_GO"


def test_absent_info_hallucination_blocks_go() -> None:
    engine = ROIDecisionGateEngine()
    proposal = _base_proposal()
    telemetry = PilotTelemetry(
        api_spend_monthly=1000.0,
        human_review_hours_monthly=20.0,
        human_hourly_rate=50.0,
        accuracy_rate=0.95,
        hallucination_rate=0.02,
        absent_info_abstention_rate=0.95,
    )
    eval_cases = [
        EvalCase("E1", "Missing doc A", False, True, False, False),
        EvalCase("E2", "Missing doc B", False, True, True, True),
    ]
    receipt = engine.evaluate_pilot(proposal, telemetry, eval_cases=eval_cases)
    assert receipt.absent_info_pass is False
    assert receipt.verdict == "HOLD"
    assert any("Absent-info abstention" in g for g in receipt.failed_gates)


def test_high_hallucination_rate_blocks_go() -> None:
    engine = ROIDecisionGateEngine()
    proposal = _base_proposal()
    telemetry = PilotTelemetry(
        api_spend_monthly=1000.0,
        human_review_hours_monthly=20.0,
        human_hourly_rate=50.0,
        accuracy_rate=0.88,
        hallucination_rate=0.08,
        absent_info_abstention_rate=0.95,
    )
    receipt = engine.evaluate_pilot(proposal, telemetry)
    assert receipt.hallucination_pass is False
    assert receipt.verdict == "HOLD"


def test_reproducible_go_verdict() -> None:
    engine = ROIDecisionGateEngine()
    proposal = _base_proposal()
    telemetry = PilotTelemetry(
        api_spend_monthly=1000.0,
        human_review_hours_monthly=20.0,
        human_hourly_rate=50.0,
        accuracy_rate=0.96,
        hallucination_rate=0.01,
        absent_info_abstention_rate=0.96,
    )
    first = engine.evaluate_pilot(proposal, telemetry)
    second = engine.evaluate_pilot(proposal, telemetry)
    assert first == second
    assert first.verdict == "GO"
    assert first.failed_gates == []
