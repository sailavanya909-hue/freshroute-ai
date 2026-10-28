# Advanced Excel planning lab

The working FreshRoute_Planner.xlsx workbook is now included. It uses the US USD/lb snapshot and explicit route assumptions. This original guide also documents optional future Excel features, such as Solver and live Power Query imports, that are not embedded in the delivered workbook. Use Microsoft 365 Excel for dynamic arrays. Read MySQL views through Power Query with a read-only database account; install the compatible MySQL connector required by your Excel version. Keep source observations separate from editable assumptions.

## Workbook structure

- **Planner:** principal outputs above the scenario table; editable freight/shrink inputs with explicit units and assumption labels.
- **MarketPrices:** Power Query output table `Prices` from `market_price`; preserve source dates, source URL, retrieval time and grade.
- **Routes:** customer quotes in `Routes`, using a unique RouteID. Reject duplicates before lookups.

Create an Excel table `Plan` with columns QuantityKg, BuyINRKg, SellINRKg, FreightINRKg, Spoilage, SaleableKg, CostINR, RevenueINR, ContributionINR and BreakEvenINRKg. The first five are inputs, the others formulas:

```excel
=[@QuantityKg]*(1-[@Spoilage])
=[@QuantityKg]*([@BuyINRKg]+[@FreightINRKg])
=[@SaleableKg]*[@SellINRKg]
=[@RevenueINR]-[@CostINR]
=IF([@SaleableKg]>0,[@CostINR]/[@SaleableKg],NA())
```

Validate quantity > 0, prices >= 0 and 0 <= spoilage < 1. A blank required input must display “Missing input” before calculation; do not allow Excel's blank-as-zero behavior to imply a valid plan. Add `=COUNTBLANK([@[QuantityKg]:[Spoilage]])` as the prerequisite check and gate calculated outputs using `IF(check>0,NA(),calculation)`.

## Useful advanced features

1. Power Query: preserve a raw query, set explicit data types, normalize INR/quintal to INR/kg only once, reject invalid price ranges and duplicate natural keys, expose an error query. Do not silently remove errors.
2. `XLOOKUP`: `=XLOOKUP([@RouteID],Routes[RouteID],Routes[FreightINRKg],NA(),0)` after proving unique route keys.
3. Dynamic sourcing list: use `FILTER` on Prices with commodity, variety, grade and exact observation date; then `SORTBY` the resulting range by modal price. Distinguish market quote ranking from a delivered-cost recommendation.
4. PivotTables and slicers: market, commodity, grade and observation month; connect related pivots to the same cache. Plot observation coverage alongside price trends.
5. Solver allocation: objective = total modeled contribution; decision cells = purchased kg by route; constraints = total saleable kg >= customer demand, route quantities <= capacities, nonnegative quantities, and arrival before expiry. Use Simplex LP only while prices/shrink/freight are fixed and all constraints linear. Infeasible demand must be reported explicitly.
6. Break-even analysis: cost per saleable kg above; compare against actual sale invoice price. Use one shared model for freight/spoilage what-if changes.

## Reconciliation example — hypothetical only

100 kg purchased, INR 20/kg buy, INR 30/kg sale, INR 2/kg freight, 10% spoilage produces 90 saleable kg, INR 2,200 total variable cost, INR 2,700 revenue, INR 500 contribution, and INR 24.4444 break-even per saleable kg. This is a formula test, not observed business performance.

Validate the same numbers in MySQL, Python, Power BI and Excel. Check zero spoilage, nearly total spoilage, missing inputs, no market observations and duplicate routes before delivery.
