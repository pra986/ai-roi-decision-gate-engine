"""Runnable CLI demo entrypoint for the AI ROI Decision Gate Engine."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from roi_gate.engine import ROIDecisionGateEngine
from roi_gate.models import EvalCase, InitiativeProposal, PilotTelemetry


def load_eval_cases(path: Path) -> list[EvalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in raw]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate an AI pilot against financial ROI and reliability gates."
    )
    parser.add_argument(
        "--eval-cases",
        type=Path,
        default=Path("evaluation/eval_cases.json"),
        help="Path to evaluation cases JSON file.",
    )
    args = parser.parse_args()

    proposal = InitiativeProposal(
        initiative_id="FIN-PILOT-001",
        name="Accounts Payable Invoice Triage Copilot",
        monthly_volume=4000,
        baseline_unit_cost=4.50,
        fixed_monthly_infra_cost=600.0,
        implementation_cost=12000.0,
        target_roi_pct=25.0,
        max_hallucination_rate=0.05,
        min_absent_info_abstention_rate=0.90,
    )

    telemetry = PilotTelemetry(
        api_spend_monthly=1450.0,
        human_review_hours_monthly=85.0,
        human_hourly_rate=55.0,
        accuracy_rate=0.94,
        hallucination_rate=0.02,
        absent_info_abstention_rate=0.95,
    )

    eval_cases = load_eval_cases(args.eval_cases) if args.eval_cases.exists() else None
    engine = ROIDecisionGateEngine()
    receipt = engine.evaluate_pilot(proposal=proposal, telemetry=telemetry, eval_cases=eval_cases)
    print(json.dumps(asdict(receipt), indent=2))


if __name__ == "__main__":
    main()
