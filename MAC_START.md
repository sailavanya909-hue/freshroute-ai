# Use FreshRoute on your Mac

1. Download and extract this project.
2. Double-click **Start FreshRoute.command**.
3. Open **http://127.0.0.1:8765** in your browser. Keep the launcher window open while using the app.

If the launcher opens in an editor, open Terminal in the project folder and run:

```sh
bash "Start FreshRoute.command"
```

The included local chatbot and dashboard do not require Docker, MySQL or a paid AI key. Python 3 must be installed. The launcher creates the portable data snapshot on first use. It does not replace an existing local database.

Open **excel/FreshRoute_Planner.xlsx** in Microsoft Excel for Mac for the planning workbook. Numbers may handle Excel charts and formulas differently, so the workbook has not been certified for Apple Numbers.

The editable **powerbi/FreshRoute.pbip** report project is included for Power BI Desktop. Power BI Desktop cannot run natively on macOS, and native rendering was not validated here. The working browser dashboard provides the Mac demonstration; it is a separate application, not an embedded Power BI report.

Stop the app with **Control+C** in the launcher window. Launch it again whenever you want to use it.
