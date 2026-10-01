# Power BI Business Intelligence Package
### Vendor Performance & Procurement Intelligence Dashboard

This directory contains the actual Microsoft Power BI deliverables for the project:
- **`Vendor_Performance_Dashboard.pbit`**: Microsoft Power BI Template file containing the Star Schema data model and 5 pre-configured report pages.
- **`Vendor_Performance_Dashboard.pbix`**: Power BI Report package.
- **`dax/measures.dax`**: Complete library of 14 production DAX measures.
- **`model/power_query.m`**: Power Query M scripts for PostgreSQL and local CSV connections.
- **`model/star_schema.json`**: Tabular Model Definition Language (TMDL) JSON schema.

---

## 1. Five Core Report Pages
1. **Page 1: Executive Overview**
   - KPI Cards: Total Sales, Total Procurement, Gross Profit, Gross Margin %, Active Vendors, Products.
   - Monthly Sales vs Procurement dual-axis area chart.
   - Top 10 Suppliers by Attributed Revenue bar chart.
   - Slicers: Date, Vendor Category, Region, Vendor Status.
2. **Page 2: Vendor Performance & Scorecard**
   - Interactive vendor ranking matrix.
   - Vendor Performance Score (VPS) badges and conditional formatting.
   - Sourcing concentration risk breakdown.
3. **Page 3: Pricing & Procurement Intelligence**
   - Purchase price variance vs category standard cost benchmark.
   - Purchase-to-Sales Efficiency Matrix (Scatter Plot).
   - High-cost / low-margin vendor detection.
4. **Page 4: Product & Inventory**
   - Category and subcategory profit breakdown.
   - Days of inventory on hand, reorder alerts, and safety stock deficit.
5. **Page 5: Vendor Drill-Through (Drill-Through Target)**
   - Right-click any vendor across the report -> **Drill Through -> Vendor Details**.
   - Granular supplier profile, monthly historical trajectory, supplied SKUs table, and strategic recommendations.

---

## 2. Refreshing Data in Power BI Desktop
1. Open **`Vendor_Performance_Dashboard.pbit`** (or `.pbix`) in Microsoft Power BI Desktop.
2. When prompted for parameters, specify the data source directory (e.g. `data/processed/` or PostgreSQL connection string).
3. Click **Home -> Refresh** in Power BI Desktop.
4. Any newly added vendors or imported CSV records stored in PostgreSQL/CSV will immediately populate across all 5 report pages!
