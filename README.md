# Vendor Performance & Procurement Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Star%20Schema%20DAX-F2C811.svg)](https://powerbi.microsoft.com/)
[![SQL Star Schema](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-336791.svg)](https://www.postgresql.org/)
[![Test Suite](https://img.shields.io/badge/Tests-8%2F8%20Passing-brightgreen.svg)]()

An end-to-end data analytics and procurement management system based on the resume project:
> **Vendor Performance Dashboard | Excel, Pandas, SQL, Power BI**
> - *Built an end-to-end data pipeline to ingest, clean, and analyze multi-table sales and purchase data using optimized SQL queries and Pandas transformations.*
> - *Created interactive Power BI dashboards with drill-down filters driving strategic decisions on pricing, procurement, and vendor management; reduced reporting turnaround by 40%.*

---

## System Capabilities & Highlights

1. **Realistic Synthetic Data Generator:**
   - Generates 75 vendors, 520 products across 5 categories, 731 calendar dates (2024-2025), 13,400+ purchases, 19,000+ sales, and warehouse inventory.
   - Raw multi-sheet Excel workbook (`data/raw/enterprise_procurement_raw.xlsx`) and raw CSV feeds.

2. **Automated Pandas ETL Pipeline:**
   - 21 schema and integrity checks generating automated `data_quality_report.json` and `.md`.
   - Vectorized data cleaning (dates, whitespace, outlier clipping via benchmarks, negative quantity removal).
   - Star Schema export to `data/processed/*.csv`.
   - 5-pillar **Vendor Performance Score (VPS)** algorithm with delivery reliability, defect rate, price variance, lead time, and concentration resilience.
   - **New Vendor Logic:** Newly registered or imported vendors with no purchase history are classified as `New / Insufficient Data` with `N/A` scores.

3. **Enterprise Power BI Solution:**
   - Native `.pbit` (Power BI Template) and `.pbix` deliverables.
   - Star Schema model with 1-to-many relationships and Power Query (M) mashup scripts.
   - 14 dynamic DAX measures.
   - 5 report pages: Executive Spend Overview, Delivery Performance & OTIF, Pricing Intelligence & Cost Variance, Sourcing Risk & Concentration, and Vendor 360° Scorecard (Target Drill-Through Page).

4. **Procurement Operations Web UI & FastAPI Backend:**
   - FastAPI server with dual database engine (PostgreSQL + SQLite fallback).
   - Duplicate-guarded vendor registration (rejects duplicate code, normalized name, or email).
   - Multi-stage CSV import workflow with validation preview (valid, duplicate, invalid breakdown + row-by-row error details) and confirmation.
   - Modern React/TypeScript dark-mode UI with interactive filters, scatter plot, pricing anomaly matrix, and data quality audit.

---

## Project Structure

```
vendor-performance-dashboard/
├── backend/                  # FastAPI backend server & routers
│   ├── api/                  # Modular endpoints: vendors, import_csv, analytics, pipeline
│   ├── models/schemas.py     # Pydantic schemas
│   └── main.py               # Application entry point & static UI mount
├── dashboard/                # React 18 / TypeScript / Tailwind CSS UI
│   ├── src/                  # Components, modals, charts, views
│   └── dist/                 # Production pre-built assets
├── data/
│   ├── raw/                  # Multi-sheet Excel & raw CSV feeds
│   ├── processed/            # Clean Star Schema tables (7 CSVs)
│   └── vendor_analytics.db   # Local analytical SQLite database
├── docs/                     # Technical documentation
│   ├── ARCHITECTURE.md       # Architecture diagrams & component flows
│   ├── BUSINESS_RULES.md     # Mathematical formulations & 40% turnaround proof
│   ├── DATA_DICTIONARY.md    # Star Schema table definitions & data dictionary
│   ├── POWERBI.md            # Power BI deployment, DAX reference & 5-page guide
│   └── SQL_ANALYSIS.md       # Star Schema DDL, B-tree indexes & SQL analysis
├── pipeline/                 # Pandas ETL Pipeline modules
│   ├── cleaning/             # Data cleaning & standardization
│   ├── database/             # SQLAlchemy dual PostgreSQL/SQLite manager
│   ├── ingestion/            # Excel/CSV loader & synthetic generator
│   ├── transformation/       # VPS scoring, gross margins, price variance
│   └── validation/           # 21 schema & data quality constraints
├── powerbi/                  # Enterprise Power BI Deliverables
│   ├── dax/measures.dax      # 14 enterprise DAX measures
│   ├── model/power_query.m   # Power Query M ingestion script
│   ├── model/star_schema.json# Tabular Model Schema definition
│   ├── Vendor_Performance_Dashboard.pbit  # Power BI Template
│   └── Vendor_Performance_Dashboard.pbix  # Power BI Report Package
├── sql/                      # DDL, indexes, views, and business queries
├── tests/                    # Pytest test suite (8/8 passing)
├── run_pipeline.py           # Master ETL execution CLI
├── requirements.txt          # Python dependencies
└── README.md                 # Root project documentation
```

---

## Quickstart Guide

### 1. Installation
Clone the repository and install the Python dependencies:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Full ETL Pipeline
Execute the end-to-end pipeline to generate synthetic data, clean, transform, score, and sync with the database:
```bash
python run_pipeline.py --generate --load-db
```

### 3. Launch the Backend & Web Dashboard
Start the FastAPI server (serves the pre-built React dashboard on port 8000):
```bash
python -m backend.main
```
Navigate to `http://localhost:8000` in your web browser.

### 4. Run the Pytest Test Suite
```bash
python -m pytest tests/test_suite.py -v
```

### 5. Open Power BI Report
Open `powerbi/Vendor_Performance_Dashboard.pbit` in Microsoft Power BI Desktop. When prompted for `DataFolderPath`, point to `data/processed` and click **Load**.

---

## Mathematical Turnaround Reduction Proof
For the complete mathematical formula and empirical calculation demonstrating the **40% reporting turnaround reduction**, see [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md).
