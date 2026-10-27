# Data contract and provenance

## AGMARKNET export

Expected headers: `State,District,Market,Commodity,Variety,Grade,Arrival_Date,Min_Price,Max_Price,Modal_Price`. Date format: DD/MM/YYYY. Confirm the chosen export's prices are INR/quintal before using the importer; divide by 100 to obtain INR/kg. Exports with alternate headers/units must be explicitly mapped, not guessed.

Grain: date + state + district + market + commodity + variety + grade. Conflicting duplicates require source-revision review. Missing grades, nonfinite prices, impossible price ordering and malformed dates fail import. The importer validates the entire file before opening its output, and does not silently discard bad records.

Modal price is a reported market statistic, not a promised executable quote. No arrivals, supplier service levels, OTIF, customer demand, inventory or measured spoilage are inferred from price records. A daily snapshot may have sparse market coverage. Collect history before training a temporal model; use chronologically split validation.

## USDA file

`data/usda_ppi_annual_raw.csv` is an unmodified public download from https://www.ers.usda.gov/media/6470/annual-percent-changes-in-selected-producer-price-indexes-1974-through-2025.csv?v=53011

Retrieved 2026-10-27. Source landing page: https://www.ers.usda.gov/data-products/food-price-outlook . Annual percent changes, US producer prices, 1974–2025 coverage per the publisher. Inspect multi-row headers and notes before transformation. Do not interpret percentages as prices, monthly data, or Indian observations. The file provides macro context only.

Before publishing data, check the source's applicable reuse terms, attribution and any third-party restrictions. The code license does not relicense datasets.
