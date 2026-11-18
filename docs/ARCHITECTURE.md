# Architecture: AI ROI Decision Gate Engine

## Overview

The AI ROI Decision Gate Engine evaluates whether an AI pilot initiative is financially viable and operationally reliable enough for production promotion.

## Core Components

- **`roi_gate/models.py`**: Defines immutable-friendly dataclasses (`InitiativeProposal`, `PilotTelemetry`, `EvalCase`, `GateDecisionReceipt`) and `GateVerdict` (`GO`, `CONDITIONAL_GO`, `HOLD`, `NO_GO`).
- **`roi_gate/engine.py`**: Implements `ROIDecisionGateEngine`, computing:
  - Baseline monthly cost (`monthly_volume * baseline_unit_cost`)
  - Total AI monthly cost (`api_spend_monthly + fixed_monthly_infra_cost + human_review_overhead`)
  - Net monthly savings, ROI percentage, and payback period in months
  - Absent-information abstention pass rate across `EvalCase` records
  - Hallucination threshold compliance
- **`roi_gate/cli.py`**: Runnable CLI demo entrypoint that evaluates a sample initiative and prints a JSON `GateDecisionReceipt`.
- **`evaluation/eval_cases.json`**: Reference evaluation suite testing absent-information abstention and grounded extraction.

## Stage-Gate Decision Flow

1. **Financial Viability Check**: If `net_monthly_savings <= 0`, issue `NO_GO`.
2. **Reliability Gate Check**: If `absent_info_pass` or `hallucination_pass` fails, issue `HOLD`.
3. **Target ROI Check**: If `roi_pct >= proposal.target_roi_pct`, issue `GO`; otherwise issue `CONDITIONAL_GO`.
