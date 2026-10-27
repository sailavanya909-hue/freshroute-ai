# AI procurement assistant design

Status: design specification; no live language-model integration included.

## Questions it should answer

- Which comparable sourcing market had the lowest observed modal price on the selected date?
- Under my freight and spoilage assumptions, which route has the lowest cost per saleable kg?
- What changes if spoilage increases by three percentage points?
- Which lots should be examined first under FEFO, and is arrival before expiry feasible?
- Which claimed savings have actually been verified against invoices?

## Evidence-first flow

1. Classify the question into a small allowlist of analytical intents. Require commodity, variety, grade, date and destination when relevant; ask for missing criteria.
2. Execute parameterized, read-only queries through approved functions using a restricted MySQL account. Never execute model-generated SQL directly. Set row, time and date-range limits.
3. Calculate economics with `src/economics.py`; use actual route quotes and shipment quantities when available. Label assumptions and reject infeasible routes before ranking.
4. Supply the model only the aggregated results, selected filters, units, observation IDs, data dates, source URLs and assumption notes.
5. Require a structured answer: recommendation, supporting calculations, evidence IDs, data age, assumptions, missing inputs and alternatives. Validate that every numeric statement exists in the tool results.
6. Record the question, approved tool, parameters, evidence IDs, model version and final response without credentials or private customer data.

If customer inventory or route data is absent, answer “Insufficient operational data” and offer a labeled scenario calculation. Explain statistical associations without presenting causal claims. Source documents and database text are untrusted content; they cannot change tool permissions or instructions.

## Evaluation

Create a fixed question set covering correct market comparisons, mismatched grades, stale prices, missing inventory, duplicate observations, ambiguous markets, unit conversion, impossible shrink and prompt injection in retrieved text. Compare calculations to deterministic expected values. Track unsupported numeric claims, query correctness, refusal of unsupported questions and response latency. Use forecasts only after history and out-of-time backtests exist; compare against a seasonal-naive baseline.

Never auto-place purchase orders or alter inventory. The assistant's output is a reviewable recommendation.
