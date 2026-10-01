# Power BI Enterprise Deliverables & Deployment Guide

This project includes a complete, production-grade Power BI report solution (`.pbit` / `.pbix`), DAX calculation library, and Power Query (M) data mashup scripts.

---

## 1. Deliverables Checklist
- **`powerbi/Vendor_Performance_Dashboard.pbit`**: Parameterized Power BI Template file ready to open in Microsoft Power BI Desktop.
- **`powerbi/Vendor_Performance_Dashboard.pbix`**: Power BI Report package.
- **`powerbi/dax/measures.dax`**: 14 enterprise-grade DAX measures with formatting and error-handling.
- **`powerbi/model/power_query.m`**: Power Query M script to load and parse all 7 Star Schema CSVs with correct data types.
- **`powerbi/model/star_schema.json`**: Tabular Model Definition (TMDL/BIM schema) declaring table relationships.

---

## 2. Report Suite Architecture (5 Interactive Pages)

### Page 1: Executive Spend & Vendor Overview
- **KPI Cards:** Total Spend ($), Attributed Revenue ($), Overall Gross Margin %, Active Vendor Count.
- **Visualizations:**
  - Month-over-Month spend & revenue trend (Line & Clustered Column Chart).
  - Spend by Product Category (Donut Chart).
  - Top 10 Suppliers by Total Procurement Spend with Pareto 80/20 cumulative curve.
  - Slicers: Fiscal Year, Category, Supplier Tier.

### Page 2: Delivery Performance & Sourcing Reliability
- **KPI Cards:** On-Time In-Full (OTIF %) with Target Goal Indicator ($\ge 90\%$), Average Lead Time Variance.
- **Visualizations:**
  - Lead Time Variance Scatter Plot: Quoted Lead Time vs Actual Lead Time (bubble size = order count).
  - Defect Rate by Category (Bar Chart with conditional red threshold formatting).
  - Bottom 10 At-Risk Delivery Vendors table with OTIF %, defect %, and late shipments.

### Page 3: Pricing Intelligence & Cost Variance
- **KPI Cards:** Purchase Price Variance (PPV %), Total Unfavorable Price Drift ($).
- **Visualizations:**
  - Purchase Price vs Catalog Standard Cost Variance Distribution (Histogram / Column Chart).
  - Unit Cost Drift Heatmap: Category unit price variance across 2024-Q1 through 2025-Q4.
  - Pricing Anomaly Matrix: Highlights products where purchase price exceeds benchmark by &gt;7%.

### Page 4: Vendor Risk & Concentration Matrix
- **KPI Cards:** Herfindahl-Hirschman Index (HHI), High-Risk Sourcing Categories Count.
- **Visualizations:**
  - Sourcing Concentration Matrix: Category vs Vendor spend share heatmap.
  - Single-Source Dependency Alert Table: Flags any vendor capturing &gt;35% of a category's spend.
  - Vendor Tier Distribution (Donut Chart: Strategic, Preferred, Standard, At-Risk, New).

### Page 5: Vendor 360° Scorecard (Target Drill-Through Page)
- **Target Page for Right-Click Drill-Through:** Right-clicking any vendor across Pages 1-4 navigates to Page 5.
- **Visualizations:**
  - Vendor Profile Card: Vendor code, category, contact, email, rating, payment terms.
  - 5-Pillar VPS Radar / Gauge Chart: OTIF, Quality, Pricing, Lead Time, Concentration.
  - 12-Month PO Spend & Delivery Reliability Trend.
  - Line-Item Product Supply Table: Units supplied, average price paid, price variance %.

---

## 3. Deployment & Refresh Instructions
1. Open **Microsoft Power BI Desktop**.
2. Go to **File -> Open** and select `powerbi/Vendor_Performance_Dashboard.pbit`.
3. When prompted for the parameter **`DataFolderPath`**, enter the path to `data/processed` (or leave default).
4. Power Query will load the 7 clean Star Schema CSV tables and automatically establish relationships.
5. Click **Refresh** anytime new transactions are ingested by the Python ETL pipeline.
