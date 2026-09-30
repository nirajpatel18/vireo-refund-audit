# Submission Form — Draft

## What did you build, and what business outcome does it move? State the number and the money.
A reproducible refund-audit tool that reconciles migration duplicates and legacy monetary units, produces monthly refund-by-reason and refund-by-agent views, and audits reason codes against customer/agent text.

The primary control opportunity is refund+replacement: 166 refund tickets (7.1%) contain both, representing about ₹871,161 of gross exposure over 18 months. I would target a 50% reduction, protecting about ₹435,580 over the period or ₹72,597 per quarter.

## What does one run cost, and what would a month cost at Vireo's volume?
Default run: **₹0/run and ₹0/month** because reconciliation and the fallback audit are local. Optional LLM mode uses a user-supplied API key/model, so cost is model- and token-dependent and is not hard-coded.

## How do you know it works?
Core reconciliation was mechanically checked: duplicate IDs have identical ticket fields apart from source system/legacy amount, and paired legacy refund values are consistently 100× the helpdesk value.

For reason quality, I manually reviewed a 60-ticket stratified sample including 30 GW-OTHER cases. Existing reason-code agreement was **48.3%** in that sample; **29/30 GW-OTHER** cases had a more specific reason evident in the text. The classifier is therefore a review assistant, not an autonomous approval system.

## Did you change, narrow, or push back on the client's ask?
Yes. I changed raw “who gives away money” into a comparable management view because Returns Desk is expected to process many refunds and Tier 2 should not be compared with Tier 1 on volume.

I narrowed the financial control target to refund+replacement exceptions because this is directly tied to a documented policy violation and has calculable rupee exposure.

## What is wrong with what you are handing us?
The text audit can return REVIEW; optional LLM mode requires a user key/model; the 50% target is a management target rather than a forecast; and the reason audit does not prove commercial correctness.

## What did you deliberately leave out, and why?
I left out predictive refund forecasting, agent performance scoring, and automated refund approval. They add complexity without being necessary for the Finance question in the five-hour window.

## Anything you built or found that nobody asked for?
A policy-exception queue for refund+replacement cases and a reason-code audit for GW-OTHER.

## What did you use AI for?
ChatGPT was used to inspect the brief, challenge reconciliation logic, design the reason-audit prompt, and draft the business narrative. I did not use an LLM for arithmetic or financial reconciliation.

The production tool has a no-cost local fallback and optional LLM mode. I discarded approaches that ranked agents purely by raw refund value and approaches that treated the agent-selected reason as ground truth.

**Three-minute screen recording:** [PASTE PUBLIC GOOGLE DRIVE LINK]

## Your Public Google Drive Link
[PASTE LINK]

## Someone picks this up on Monday and you are unreachable. The three things they need to know.
1. Run `python analyze.py --data-dir <folder>`.
2. Duplicate tickets prefer the helpdesk row; legacy monetary values are divided by the empirically observed 100× scale.
3. Start with `outputs/board_summary.md`, `monthly_refunds_by_reason.csv`, `monthly_refunds_by_agent.csv`, and `review_queue.csv`.

## Honest hours spent.
[ENTER ACTUAL HOURS]

## Github Repo Link
[PASTE PUBLIC GITHUB URL]
