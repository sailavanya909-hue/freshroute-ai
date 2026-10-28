# Verification record

## Performed locally

- 22 Python unit/API checks passed; one MySQL-service check skipped locally because MySQL/Docker is not installed on this Mac. Includes cost ranking reversal, date isolation, capacity, no-data handling, shrink sensitivity, grounded chat, explicit question context, source counts and HTTP download/export behavior.
- Microsoft schema validation passed for 34 Power BI metadata files. All 24 visual definitions reference existing model fields/measures. This does not execute DAX, M or native visuals.
- Excel formula checks passed in the artifact authoring engine: base delivered cost 0.7731958763, contribution USD 2,685, higher shrink raises cost, excessive capacity yields unavailable, and blank quantity cannot produce a recommendation. Formula-error scan found zero unexpected errors. All four sheets were rendered and visually reviewed. A native Excel application is not installed here.
- Browser QA: date switch to October 27 selects New York only; reset restores Boston/Chicago; changing spoilage updates contribution; excessive purchased quantity removes feasible recommendations; chat returns source-linked calculations.

## Reproducible automation

GitHub Actions `Validate FreshRoute` provisions MySQL 8.4, initializes the schema and SELECT-only reader, checks actual SQL constraints and ranking, and runs the API tests against MySQL. It also tests portable mode and validates the Power BI metadata. Check the latest Actions result before claiming that run passed.

## External checks still required

- Open and refresh `powerbi/FreshRoute.pbip` in Windows Power BI Desktop; verify DAX/M execution, visual rendering, slicer behavior, cross-filtering, source authentication and publishing. No `.pbix` or published Power BI workspace is claimed.
- Optional OpenAI intent routing requires your own API key and compatible model. The local assistant is tested; paid-model calls were not made. Its numerical answers are always produced by deterministic code.
- Actual operational recommendations require current executable prices, customer routes, inventory, measured spoilage and invoices. No realized savings are verified.
