# Enterprise System Architecture

The **Vendor Performance & Procurement Intelligence System** is architected as an end-to-end data analytics and procurement management platform.

```
+-----------------------------------------------------------------------------+
|                          RAW DATA INGESTION LAYER                           |
|  - Enterprise Multi-Sheet Excel: data/raw/enterprise_procurement_raw.xlsx   |
|  - Raw CSV Data Feeds: vendors_raw.csv, products_raw.csv, purchases_raw... |
|  - Ad-hoc Vendor Ingestion: data/raw/sample_vendor_import.csv               |
+--------------------------------------|--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                           PANDAS ETL PIPELINE                               |
|  1. Ingestion: pipeline/ingestion/loader.py (chunked loading)               |
|  2. Validation: pipeline/validation/validator.py (21 integrity rules)       |
|  3. Cleaning: pipeline/cleaning/cleaner.py (outlier clipping, parsing)      |
|  4. Transformation: pipeline/transformation/metrics.py (margins, shares)    |
|  5. Scoring Engine: pipeline/transformation/scoring.py (5-factor VPS)       |
|  6. Output Export: data/processed/*.csv (Clean Star Schema tables)          |
+--------------------------------------|--------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
+--------------------------------------+   +----------------------------------+
|           SQL DATABASE LAYER         |   |         POWER BI PLATFORM        |
|  - PostgreSQL / SQLite Dual-Engine   |   |  - Template: .pbit / .pbix       |
|  - Star Schema: 4 Dims, 3 Facts      |   |  - 1-to-Many Relationships       |
|  - Views: vw_vendor_performance...   |   |  - 14 Dynamic DAX Measures       |
|  - B-Tree Composite Indexes          |   |  - 5 Interactive Report Pages    |
|  - Path: data/vendor_analytics.db    |   |  - Drill-Through Vendor 360      |
+------------------|-------------------+   +----------------------------------+
                   |
                   v
+-----------------------------------------------------------------------------+
|                             FASTAPI BACKEND                                 |
|  - CRUD & Intake: /api/vendors, /api/vendors/create (Duplicate Rejection)   |
|  - Multi-Stage Import: /api/vendors/import/preview, /api/vendors/import/confirm
|  - SQL Analytics: /api/kpis, /api/trends, /api/pricing-anomalies            |
|  - Health & Quality: /api/health, /api/pipeline-status                      |
+--------------------------------------|--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                     REACT / VITE PROCUREMENT WEB UI                         |
|  - Modern Dark-Themed Executive Dashboard (TypeScript + Tailwind CSS)       |
|  - Duplicate-Guarded "Add Vendor" Modal                                     |
|  - Multi-Stage "Import CSV" Modal (Validation, Duplicate Breakdown, Commit) |
|  - Dedicated Power BI Architecture & Integration View                       |
|  - Efficiency Scatter Plot, Pricing Variance Matrix & Data Quality Audit    |
+-----------------------------------------------------------------------------+
```

## Key Architectural Principles
1. **Separation of Concerns:** Business logic resides in Python/SQL; presentation is served by React and Power BI.
2. **Dual Database Engine:** Zero-configuration local SQLite for instant developer setup; production PostgreSQL engine via SQLAlchemy connection string.
3. **Data Integrity First:** 21 automated validation rules guard against duplicate keys, orphaned foreign keys, negative quantities, and unclipped price anomalies.
4. **Resilient Vendor Intake:** New vendors without historical transactions are never falsely scored or classified as "Poor Performing", maintaining audit credibility.
