# Data contract and provenance

## Working US terminal-market demo

`terminal_quotes.csv` contains 22 selected, manually transcribed observations from USDA's Boston (BH_FV030), Chicago (HX_FV030), and New York (NX_FV030) reports. Product scope: Idaho, U.S. One, conventional Russet Norkotah, 50 lb cartons. Counts 40–120 describe potato counts per carton, not pounds. Source URLs point to changing report endpoints, not permanent version archives.

Boston and Chicago source reports: October 26, 2026. New York: October 27, 2026. Retrieved and transcribed October 27, 2026 from the official published report text. Full original PDFs could not be downloaded in this environment. The checked-in data preserves selected dated observations and source report IDs; verify archived publisher copies for audited use.

Grain: report date + market + origin + commodity + variety + grade + size count + package. Use the overall low–high range, not the narrower “mostly” interval. Midpoint = (low + high)/2, divided by 50 for USD/lb. It is not a modal price or confirmed executable quote. Boston has a 120-count observation that is unavailable in the other selected reports.

Route inputs and inventory are illustrative. The generic distribution center does not represent a measured route network. Capacity applies to purchased pounds. Inventory remaining days are simulation-relative and are not actual expiry dates.

`tools/build_data.py` reproduces the CSVs, JSON snapshot, checksum manifest and SQLite database. It never fetches a new report or changes observation dates automatically. Adding records requires verifying the source and extending the checked-in transcription. No daily price history sufficient for forecasting is claimed.

Power BI embeds the same records. Its `UseMySQL` parameter switches quote reads to the MySQL view. Excel contains a portable editable snapshot; writeback from Excel to the database is not implemented.

## AGMARKNET export

Expected headers: `State,District,Market,Commodity,Variety,Grade,Arrival_Date,Min_Price,Max_Price,Modal_Price`. Date format: DD/MM/YYYY. Confirm the chosen export's prices are INR/quintal before using the importer; divide by 100 to obtain INR/kg. Exports with alternate headers/units must be explicitly mapped, not guessed.

Grain: date + state + district + market + commodity + variety + grade. Conflicting duplicates require source-revision review. Missing grades, nonfinite prices, impossible price ordering and malformed dates fail import. The importer validates the entire file before opening its output, and does not silently discard bad records.

Modal price is a reported market statistic, not a promised executable quote. No arrivals, supplier service levels, OTIF, customer demand, inventory or measured spoilage are inferred from price records. A daily snapshot may have sparse market coverage. Collect history before training a temporal model; use chronologically split validation.

## USDA file

`data/usda_ppi_annual_raw.csv` is an unmodified public download from https://www.ers.usda.gov/media/6470/annual-percent-changes-in-selected-producer-price-indexes-1974-through-2025.csv?v=53011

Retrieved 2026-10-27. Source landing page: https://www.ers.usda.gov/data-products/food-price-outlook . Annual percent changes, US producer prices, 1974–2025 coverage per the publisher. Inspect headers and notes before transformation. Do not interpret percentages as prices, monthly data, or Indian observations. The file provides macro context only.

Before publishing data, check the source's applicable reuse terms, attribution and any third-party restrictions. The code license does not relicense datasets.
