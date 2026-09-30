# Reason-code audit prompt

You are auditing a Vireo Audio support refund. Choose exactly one:
GW-OTHER, DOA-REPL, LOST-TRANSIT, DUP-PAYMENT, CANCEL, PRICE-ADJ, RETURN-QC-OK, WTY-BUYBACK, REVIEW.

Use both the customer's opening message and the agent's closing note. Select the most specific code supported by the text. If the text does not support a specific code, use REVIEW. Do not infer facts not present.

Return JSON:
{"reason":"<CODE>","confidence":0.0,"basis":"<short evidence phrase>"}
