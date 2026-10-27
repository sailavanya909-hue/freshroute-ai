# Power BI implementation specification

This is a design and measure starter; create the report in Power BI Desktop. No rendered report is included.

## Model

Import `market_price` and `scenario_economics` from MySQL. Add DimDate, DimCommodity, DimMarket and a scenario selector. Use unique surrogate keys in dimensions and one-to-many, single-direction relationships into facts. Market identity includes state, district and market; product identity includes commodity, variety and grade. Do not relate facts directly. Scenario comparisons must use the same quantity, destination, date and product specification.

## Pages and interactions

1. **Today's decision desk:** cards for modeled contribution, cost per saleable kg, and latest source date; commodity/grade/date/market slicers; ranked sourcing table; scatter of cost versus modeled shrink. Selecting a market cross-filters detail; a drillthrough button opens the corresponding market and product. Show “No observations for selection” for empty filters.
2. **Sourcing intelligence:** comparable market price trends, price-spread matrix, distribution chart, stale-source highlight. Report dates with actual observations; leave missing dates blank. Tooltip shows source, unit, date, grade and record count. Never present minimum quote as achievable procurement price.
3. **What-if lab:** disconnected decimal parameter tables for freight change and shrink change. Sliders update scenario contribution using the measure in `measures.dax`. Buttons/bookmarks switch table and chart views. Clearly display active parameter values and original assumptions.
4. **Inventory rescue:** FEFO lot table, expiry buckets, quantity and modeled markdown economics. Requires actual customer lots; show unavailable until loaded. Add transit versus remaining shelf-life feasibility filters before suggesting rerouting.
5. **Impact verification:** separate modeled savings from realized savings measured on matched invoice baselines; customer approval/date and baseline definitions. Never sum alternatives for the same shipment as independent savings.
6. **Data and macro context:** source freshness and coverage; USDA annual PPI context on a separate US page. No geographic or currency substitution.

## Finish and usability

16:9 canvas; dark navy background, white labels, teal for selected actions, amber for assumptions. Use consistent page navigation, dynamic titles, reset-filters bookmark, report-page tooltips and accessible contrast. Use color plus text labels. Limit visuals to approximately six per page. Make stale data visible next to the relevant value. Restrict customer-level data using tested row-level security before sharing.

## Acceptance checks

Cross-filter a commodity and verify every related card; drill through to one market; reset filters; test no-data and stale-data selections; change each what-if parameter and reconcile one scenario against Python and Excel. Confirm blanks are not displayed as zero. Publish only after data reconciliation and permission checks.
