# Vireo Audio — Refund Audit Tool

## Quick start
Place the supplied CSV/TXT/PDF pack beside `analyze.py`, then:

```bash
python -m venv .venv
pip install -r requirements.txt
python analyze.py --data-dir .
```

Default run makes no paid model calls.

Optional AI audit:
```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="..."
python analyze.py --data-dir . --ai
```

## Reconciliation decisions
1. One canonical row per `ticket_id`.
2. If both systems contain the same ticket, retain the helpdesk row.
3. Infer legacy scale from paired duplicate refund rows; this pack gives 100×.
4. Flag refund+replacement as a policy exception.
5. Do not compare Tier 2 and Tier 1 on raw ticket volume.

## Current pack
Canonical tickets: 11,600
Normalized refunds: ₹6,709,932
Refund+replacement exceptions: 166
Gross exception exposure: ₹871,161

## Outputs
- `outputs/monthly_refunds_by_reason.csv`
- `outputs/monthly_refunds_by_agent.csv`
- `outputs/agent_summary.csv`
- `outputs/review_queue.csv`
- `outputs/board_summary.md`
