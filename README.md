# AI ROI Decision Gate Engine (Project 16)

**L1: AI Leader — AI Initiative Decision and Delivery Workflow**

A quantitative AI pilot ROI and stage-gate governance engine that accounts for baseline unit cost, LLM API spend, human-in-the-loop (HITL) review overhead, and absent-information ("I don't know" / abstention) evaluations before promoting an AI initiative to production.

## Architecture

```
InitiativeProposal + PilotTelemetry + EvalCases
                     │
                     ▼
        ┌────────────────────────┐
        │   ROIDecisionGateEngine │
        │  - Cost & ROI Model    │
        │  - Absent-Info Eval    │
        │  - 6-Stage Gate Policy │
        └────────────────────────┘
                     │
                     ▼
          GateDecisionReceipt
   (GO / CONDITIONAL_GO / HOLD / NO_GO)
```

## 6-Stage Delivery Workflow

1. **Stage 1 — Problem Framing & Baseline Audit**: Quantify baseline human/legacy unit cost, monthly volume, and error rate.
2. **Stage 2 — Data & Absent-Information Readiness**: Verify ground-truth coverage and explicit abstention cases where the model must refuse rather than hallucinate.
3. **Stage 3 — Offline Evaluation & Guardrails**: Run `evaluation/eval_cases.json` for accuracy, hallucination rate, and absent-info abstention recall.
4. **Stage 4 — Pilot Unit-Economics & ROI Gate**: Compute net monthly savings:
   `net_monthly_savings = (baseline_unit_cost * volume) - (api_spend + human_review_overhead + infra_fixed_cost)`
   and payback period / ROI percentage.
5. **Stage 5 — Production Controls & Shadow Rollout**: Enforce spend caps, latency SLAs, human escalation thresholds, and drift alerts.
6. **Stage 6 — Scale Decision & Continuous Governance**: Issue final `GO`, `CONDITIONAL_GO`, `HOLD`, or `NO_GO` stage-gate verdict with audit trail.

## Data Contract

- `InitiativeProposal`: Initiative ID, name, monthly volume, baseline unit cost, fixed monthly infra cost, target ROI threshold, max hallucination rate, min absent-info abstention rate.
- `PilotTelemetry`: API token/inference spend, human review hours & hourly rate, observed accuracy, hallucination rate, absent-info abstention rate.
- `EvalCase`: Structured prompt/context test case with `expects_abstention` flag and expected decision.
- `GateDecisionReceipt`: Deterministic breakdown of baseline cost, AI total cost (API + human review + infra), net monthly savings, ROI %, payback months, eval pass/fail flags, and final gate decision.

## Production Controls

- **Hard Spend & Unit-Cost Guardrails**: Blocks promotion if AI unit cost (API + HITL review) exceeds baseline unit cost.
- **Absent-Info Abstention Gate**: Rejects pilots that guess on unanswerable/missing-context queries below threshold.
- **Hallucination Ceiling**: Enforces strict maximum hallucination rate before production sign-off.
- **Deterministic Auditability**: Every decision receipt records exact inputs, formula outputs, and failed gate reasons.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
python -m roi_gate.cli
```

## Attribution

Inspired by **Ed Donner's AI Leader course** (L1: AI Leader — AI initiative decision and delivery workflow).

## License

MIT License — see [LICENSE](LICENSE).
