# Memo — Refund control review
**To:** Arjun Mehta, Finance Controller  
**Period:** Jan 2025–Jun 2026

## Executive summary
I reconciled the migration duplicates and legacy monetary representation before calculating the board view. The canonical dataset contains **11,600 tickets**, **2,340 refund tickets**, and **₹6,709,932 of normalized refunds**.

The clearest control exception is **166 refund tickets where both a refund and a replacement were recorded**, creating about **₹871,161 of gross exposure**. The policy says a customer must not receive both and that such an error must be escalated to the Team Lead and Finance the same day.

A practical management target is to halve the exception rate from **7.1% to 3.5%**, protecting about **₹435,580 over 18 months / ₹72,597 per quarter** if prevented.

## What was wrong with the export
The pack contains duplicate ticket IDs from migration re-imports. Where both systems contain the same ticket, I retain the helpdesk copy. Paired refund rows show the legacy amount is consistently 100× the helpdesk amount, so legacy values are divided by 100 before aggregation.

## What the money is for
GW-OTHER accounts for **991 refunds / ₹2,907,036 (43.3% of refund value)**. In a 60-ticket manual audit containing 30 GW-OTHER cases, **29/30 GW-OTHER cases had a more specific reason visible in the customer/agent text**. This makes the reason-code field a reporting-quality problem, not evidence that those refunds were illegitimate.

## Management view
Use monthly refund value by reason and agent, but do not rank people on raw refund value. Returns Desk is designed to process most refunds, and Tier 2 is explicitly not comparable with Tier 1 on volume.

## Recommended action
1. Put refund+replacement exceptions on a daily control queue.
2. Require Team Lead/Finance review before both transactions complete.
3. Use the AI-assisted reason audit to propose a specific policy reason and route low-confidence cases to review.
4. Reconcile legacy rows before every Finance extract.

## Limitation
The reason audit checks whether the selected reason is supported by text. It does not decide whether the underlying refund was commercially correct.
