# Loyal Company — Sales Transactions Analysis (2022–2025)

A complete data-analysis project for **Loyal Company**: raw transaction data, a cleaning pipeline, an interactive Power BI–style HTML dashboard, and a Somali-language analysis report.

## What's inside

| File | What it is |
|---|---|
| `data/Sales_transactions_2022-2025.csv` | Raw source data (18,045 rows) |
| `data/Sales_transactions_CLEANED_2022-2025.csv` | Cleaned dataset (18,000 unique transactions) |
| `dashboard/Sales_Dashboard_2022-2025.html` | **Interactive dashboard** — open in any browser, no internet needed |
| `report/Warbixinta_Iibka_2022-2025.pdf` | Somali-language analysis report (3 pages) |
| `report/Warbixinta_Iibka_2022-2025.md` | Same report in Markdown |
| `scripts/build_dashboard.py` | Regenerates the HTML dashboard from the CSV |
| `scripts/build_report.py` | Regenerates the PDF + Markdown report |
| `README.md` | This file |

## Quick start

1. **View the dashboard:** open `dashboard/Sales_Dashboard_2022-2025.html` in any browser.
2. **Read the report:** open `report/Warbixinta_Iibka_2022-2025.pdf`.

No installation, no server, no internet required — everything is self-contained.

## The dashboard

A multi-page, Power BI–style dashboard built with ECharts:

- **Left sidebar** with page navigation + persistent filters (Year, Channel, Segment, Gender, Age)
- **5 pages:** Overview · Trends · Customers · Timing · Loyalty
- Filters recompute every chart, KPI, and insight live in the browser
- Clean white theme, professional muted palette, callout labels on charts

## Key findings

- **18,000** transactions · **4,882** unique customers · **14,541** unique orders
- **Online** is the largest channel — **45.5%**
- **Consumer** is the largest segment — **44.6%**
- **Female** leads **52.8%** vs Male 47.2%
- Peak purchasing time **15:00**; **68.4%** of sales happen 09:00–17:00
- Sales **grew +21.6%** from 2022 to 2025

## Data cleaning

The raw CSV (18,045 rows) was cleaned to **18,000** unique transactions:

- Removed 45 duplicate `Transaction_ID`s
- Standardized gender casing (`male`/`MALE` → Male, `FEMALE` → Female, `Non Binary` → Non-binary)
- Filled 216 missing ages with the median; capped ages to 18–100
- Filled 108 missing names with "Anonymous"
- Merged Non-binary / Unknown into Female per management decision

## Rebuilding

Requires Python 3 with `pandas` and `fpdf2`:

```bash
python scripts/build_dashboard.py   # regenerates dashboard/ HTML
python scripts/build_report.py      # regenerates report/ PDF + MD
```

Both scripts read the raw CSV and the dashboard template, and self-verify their output before writing.

---
*Generated for Loyal Company. Data source: `Sales_transactions_2022-2025.csv`.*
