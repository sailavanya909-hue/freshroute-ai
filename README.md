# FreshRoute AI

Fresh-food procurement analytics with a working dashboard, evidence-grounded chatbot, Excel planner, MySQL integration and editable Power BI report project.

## Start the working demo

Requires Python 3.10+. The local demo uses only the Python standard library.

```sh
python3 tools/build_data.py
python3 app/server.py
```

Open http://127.0.0.1:8765 . Use Ctrl+C to stop. The server listens only on your computer. This is a portfolio demo, not a public production service.

## What works

- Four dashboard views: decision desk, scenario lab, inventory rescue and data evidence.
- Exact report-date, market and carton-count filters, route capacity checks, CSV export and source drilldown.
- Freight/spoilage sliders, quantity and selling-price controls, price-range uncertainty and contribution sensitivity.
- Working local analytical chatbot with evidence links. Optional OpenAI intent routing is implemented but requires your own server-side key and model.
- Excel workbook with editable assumptions, exact-match quote checks, capacity guards, sensitivity heatmap, formulas, validation and an editable chart.
- Power BI project with four pages, 24 visual definitions, data-bound slicers, scenario controls, measures and an embedded snapshot. Its 34 metadata files pass Microsoft schema validation and field-binding checks. Windows Desktop rendering remains to be verified.
- MySQL 8 schema, ingestion, read-only application user setup, window-function ranking view, Docker Compose and integration tests.

## Real observations and explicit scenarios

The operational snapshot contains **22 manually transcribed USDA wholesale price observations** for Idaho U.S. One Russet Norkotah potatoes, conventional, in 50 lb cartons. Boston and Chicago reports are dated **October 26, 2026**. New York is dated **October 27, 2026**. The dashboard compares only matching dates and sizes.

Sources: [Boston](https://www.ams.usda.gov/mnreports/bh_fv030.pdf), [Chicago](https://www.ams.usda.gov/mnreports/hx_fv030.pdf), [New York](https://www.ams.usda.gov/mnreports/nx_fv030.pdf). These live report URLs can later change; the checked-in observation dates never update automatically. See `data/terminal_manifest.json` and `docs/data-contract.md`.

**Observed:** quote ranges and product specifications. **Derived:** range midpoint and USD/lb. **Assumed:** freight, capacity, transit, spoilage and selling price. **Simulated:** inventory lots. No customer revenue, actual inventory, supplier availability or realized savings is claimed.

The 832-row USDA annual PPI dataset remains available as separate macro context. It is never used as an operational quote. The original INR/kg AGMARKNET importer remains an optional separate workflow; its currencies and units are never mixed with the US demo.

## A decision worth demonstrating

For October 26, 80-count cartons and 10,000 purchased lb:

| Market | Derived quote USD/lb | Assumed freight USD/lb | Assumed shrink | Delivered USD/saleable lb | Modeled contribution USD |
|---|---:|---:|---:|---:|---:|
| Boston | 0.690 | 0.060 | 3% | 0.7732 | 2,685 |
| Chicago | 0.560 | 0.190 | 6% | 0.7979 | 2,370 |

Selling price is assumed at USD 1.05/lb. Chicago has the lower quote, while Boston has the lower modeled delivered cost. These ranges overlap: confirm current freight and executable quotes before purchasing. Contribution excludes fixed overhead, financing and taxes.

## Excel

Open `excel/FreshRoute_Planner.xlsx`. Amber cells are editable. Start on Planner, then inspect Sensitivity, Quotes and Routes. Select the report date and carton count; update purchased quantity and selling price. Formula recalculation, blank-quantity behavior, capacity failures and spoilage changes were verified in the authoring engine. Microsoft Excel application behavior has not been tested on this Mac.

## Power BI

Open `powerbi/FreshRoute.pbip` in a current Windows Power BI Desktop version supporting PBIP/PBIR. Refresh to load the embedded public snapshot, with no database credentials required. Default measures use October 26 and 80-count cartons until a single date/size is selected. Multi-date or multi-size selections return unavailable comparison measures.

To use MySQL instead, change Power Query parameters `UseMySQL` to true and `MySQLServer` to your server, then authenticate with the read-only account. Install the MySQL connector supported by your Power BI version if required. Apply `powerbi/theme.json` through the theme menu for FreshRoute colors. Desktop import, rendering, native interactions and DAX execution require a Windows validation pass; schema checks do not establish those results.

## MySQL 8 setup

Install the dependencies in your own Python environment:

```sh
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with local passwords, then start the database:

```sh
docker compose up -d --wait
```

Docker reads `.env`; Python reads environment variables. On macOS/Linux export the variables from your edited file before initialization:

```sh
set -a
. ./.env
set +a
python3 tools/setup_mysql.py
```

This creates/updates the public snapshot tables and a SELECT-only `freshroute_reader` account. To start the dashboard against MySQL:

```sh
export FRESHROUTE_DB=mysql
export MYSQL_USER=freshroute_reader
export MYSQL_PASSWORD="$MYSQL_READER_PASSWORD"
python3 app/server.py
```

PowerShell users can set the same variables through `$env:NAME` before running Python. Never commit `.env` or actual customer data. Setup is a development initializer, not a production migration strategy. Existing root credentials are required.

## Chatbot

The default assistant works without a paid service, using local retrieval-based intent matching and deterministic analytics. It can compare markets, test explicit freight or shrink changes, explain freshness, review simulated lots and explain the business model. It uses the dashboard filters and extracts explicit market/date/carton-size requests.

For optional LLM intent classification, export `OPENAI_API_KEY` and `OPENAI_MODEL` before starting the server. The key stays server-side. Only the question is sent to OpenAI; prices are calculated locally. This optional network path has not been tested with a live key. See `docs/ai-assistant.md`.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate_powerbi.py
```

MySQL tests run when `RUN_MYSQL_TESTS=1` with an initialized service. GitHub Actions provisions MySQL 8.4 and tests the actual MySQL view, constraints, and dashboard/chat API in both database modes. See the Actions tab for the latest execution result. Power BI schema validation downloads official Microsoft schemas and caches them locally.

## Business model

Buyer: a regional fresh-food distributor supplying restaurants and retailers. Proposed pricing: monthly subscription per distribution location, with an optional fee tied to invoice-verified savings. Validate willingness to pay and customer retention through a pilot. Track modeled opportunities separately from verified outcomes.

## Scope and limitations

This is a runnable historical decision demo with a small, documented public snapshot. It is not a live supplier platform or demand forecast. Operational adoption requires current executable quotes and customer inventory, routes and invoices. Power BI Desktop verification and optional live LLM credentials remain external validation steps. No trained forecasting model is claimed.

Code is MIT licensed. External data retains source terms. See `docs/verification.md` for performed checks and remaining limits.
