# Implementation roadmap

## 1. Validate the customer and source

Interview procurement managers. Test whether freight, shrink and market-price comparisons change decisions. Obtain a real AGMARKNET export, verify units, import it, and archive provenance. Define one pilot region and matching product specifications. Acceptance: source count, grain and price totals reconcile.

## 2. Deliver the analytical model

Run schema in MySQL 8, load prices, add customer-owned route quotes and lot data. Reconcile modeled contribution to the deterministic example and check freshness. Acceptance: a reviewer traces one recommendation back to dated observations and explicit assumptions.

## 3. Build Power BI and Excel

Implement dashboard pages, relationships, measures, drillthrough, bookmarks, slicers and what-if controls. Build the Excel planning lab. Acceptance: identical selected scenario outputs across Python, SQL, Excel and Power BI; missing-data and invalid-scenario behavior tested.

## 4. Add the AI assistant

Implement allowlisted read-only tools and evidence-grounded explanations. Acceptance: no unsupported numeric claims on the evaluation set, and no writable database privileges. Keep keys server-side.

## 5. Validate the business model

Track adoption, decisions reviewed, modeled versus realized contribution, and verified shrink. Measure subscription willingness to pay. A pilot-approved baseline must account for product mix, date, volume and all included variable costs; do not claim causal savings from a simple before/after chart. Revenue targets remain assumptions until customers pay.

## Portfolio presentation

Demonstrate one complete sourcing decision, explain why the lowest quote loses after freight/shrink, move a slider, inspect the evidence and ask the assistant to explain it. Include a data dictionary, architecture, test results and clear limitations. Publish `.pbix` and a sanitized workbook only after removing private data and credentials.
