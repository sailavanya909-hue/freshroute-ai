# FreshRoute AI

## Fresh food. Better sourcing. Explainable decisions.

A supply chain analytics portfolio project for a proposed subscription business serving regional fresh-food distributors. Compare market sourcing costs, model spoilage and freight, and explain procurement decisions through an evidence-grounded assistant.

**Status: implementation starter, not a deployed product.** MySQL schema, importer, tested decision engine, Power BI DAX and design, and Excel formulas are included. A `.pbix`, finished Excel workbook, live LLM connection, and production data connections are not included.

## The business problem

The cheapest quoted produce can become the most expensive delivered product after freight and shrink. FreshRoute evaluates cost per saleable kilogram, highlights stale observations, and quantifies how sensitive each sourcing choice is to spoilage assumptions.

**Buyer:** procurement managers at regional distributors supplying restaurants and small retailers.

**Business model hypothesis:** monthly subscription per distribution location; optional performance fee on savings verified against a customer-approved baseline. Validate willingness to pay through interviews and a pilot. No revenue or savings claims are presented as real outcomes.

**Pilot scope:** tomatoes, onions, and potatoes; one region, matching variety/grade, three sourcing markets; daily purchasing review. A sourcing market is not an individual supplier.

## Data: real observations versus scenarios

1. [India AGMARKNET via data.gov.in](https://www.data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi): market/date/commodity/variety/grade and minimum, maximum, modal prices. Download an official export and run `src/import_prices.py`. Requires access to an export or a personal API key for automated retrieval. No AGMARKNET rows are fabricated or bundled.
2. [USDA annual producer price changes](https://www.ers.usda.gov/data-products/food-price-outlook): the included raw CSV is a real public macroeconomic reference. It is US annual percentage-change data, not Indian market prices. Keep it on a separate context page; never join it as a local selling price or mix currencies.
3. **Customer inputs required:** actual purchase/sale invoices, inventory lots, freight quotes, route times, capacity, actual spoilage, and demand. Until available, these are explicit user-entered assumptions. FAO loss estimates can provide context, not measured loss for a particular shipment.

Record retrieval date, source URL, source publication date, units, coverage, checksum, and revisions. Archive each daily source export: today's snapshot cannot reconstruct historical backtests.

## Quick start

Requires Python 3.10+ and MySQL 8.0.16+ for enforced CHECK constraints.

```sh
python3 -m unittest discover -s tests -v
mysql -u YOUR_USER -p < sql/schema.sql
python3 src/import_prices.py --input YOUR_OFFICIAL_EXPORT.csv --output data/prices_clean.csv
```

Use the exact export headers documented in `docs/data-contract.md`. Import the normalized file using the MySQL import wizard into `market_price`; map headers explicitly and skip duplicates only after reviewing them. Connect Power BI and Excel to the resulting views. Keep credentials out of Git.

## Project components

| Folder | What it delivers |
|---|---|
| `sql` | normalized market observations, lot and route inputs, audit-friendly scenario results, analysis view |
| `src` | validated CSV normalizer and deterministic sourcing-cost engine |
| `tests` | price-unit conversion, invalid observations, and shrink-cost boundary checks |
| `powerbi` | dashboard specification, DAX measures, color theme |
| `excel` | advanced planning formulas and Solver setup |
| `docs` | data contract, AI design, implementation roadmap and business validation |

## What makes it distinctive

- Decision queue ranked by modeled value rather than another sales KPI page.
- Freight/spoilage sensitivity and break-even analysis.
- Price freshness and comparable-grade filters alongside every recommendation.
- Chat answers include observation dates, units, filters, assumptions, and evidence IDs.
- Track predicted savings separately from realized, invoice-verified savings.

See `docs/roadmap.md` for implementation stages and acceptance criteria. Code is MIT licensed; external data retains its source terms and attribution requirements.
