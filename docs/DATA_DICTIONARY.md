# Enterprise Data Dictionary & Star Schema Reference

The underlying analytical database is modeled in a third-normal-form Star Schema optimized for high-performance aggregation and Power BI DirectQuery/Import.

---

## 1. Dimension Tables

### `DimCategory`
Stores product taxonomy and strategic spend categories.
- `category_id` (INT, PK): Unique category identifier (1 to 5).
- `category_name` (VARCHAR, UNIQUE): Electronics & Components, Raw Materials, Industrial Machinery, Packaging, MRO Supplies.
- `description` (TEXT): Business scope of category.

### `DimVendor`
Stores master supplier registry.
- `vendor_id` (VARCHAR, PK): Business vendor identifier (e.g. `VND-001`).
- `vendor_code` (VARCHAR, UNIQUE): Standardized vendor code.
- `vendor_name` (VARCHAR, NOT NULL): Registered legal supplier entity.
- `category_id` (INT, FK -> DimCategory): Primary category alignment.
- `contact_name` (VARCHAR): Primary procurement contact.
- `email` (VARCHAR, UNIQUE): Contact email address.
- `phone` (VARCHAR): International phone format.
- `city` (VARCHAR): Operating city.
- `country` (VARCHAR): Country of origin.
- `payment_terms` (VARCHAR): Net 15, Net 30, Net 45, Net 60, 2/10 Net 30.
- `lead_time_days` (INT): Contractual quoted lead time.
- `rating` (DECIMAL): Initial vendor audit rating (1.0 to 5.0).
- `status` (VARCHAR): Active, Inactive, Suspended, or `New / Insufficient Data`.

### `DimProduct`
Stores product catalog and pricing benchmarks.
- `product_id` (VARCHAR, PK): Unique product identifier (e.g. `PRD-0001`).
- `product_name` (VARCHAR, NOT NULL): Product title.
- `category_id` (INT, FK -> DimCategory): Category foreign key.
- `standard_cost` (DECIMAL): Baseline catalog standard cost ($).
- `list_price` (DECIMAL): Suggested retail selling price ($).

### `DimDate`
Stores 731-day enterprise calendar (2024-01-01 to 2025-12-31).
- `date_id` (INT, PK): YYYYMMDD integer key.
- `date` (DATE, UNIQUE): Calendar date (YYYY-MM-DD).
- `year` (INT): Calendar year.
- `quarter` (INT): Q1 to Q4.
- `month` (INT): Month number (1 to 12).
- `month_name` (VARCHAR): Full month name.
- `day_of_week` (INT): Day of week (1 to 7).
- `is_weekend` (BOOLEAN): Weekend flag.

---

## 2. Fact Tables

### `FactPurchases`
Records procurement purchase order (PO) transactions (13,400+ rows).
- `purchase_id` (VARCHAR, PK): Unique PO line ID.
- `po_date` (DATE, FK -> DimDate): Date PO was issued.
- `vendor_id` (VARCHAR, FK -> DimVendor): Supplier foreign key.
- `product_id` (VARCHAR, FK -> DimProduct): Product foreign key.
- `quantity` (INT): Units ordered (positive integer).
- `unit_purchase_price` (DECIMAL): Actual price paid per unit ($).
- `total_purchase_value` (DECIMAL): Quantity * Unit Purchase Price ($).
- `delivery_status` (VARCHAR): `ON_TIME`, `LATE`, or `CANCELLED`.
- `actual_lead_time_days` (INT): Actual elapsed days to warehouse receipt.
- `defect_rate` (DECIMAL): Inspection defect percentage (0.00 to 0.05).

### `FactSales`
Records downstream sales transactions (19,000+ rows).
- `sale_id` (VARCHAR, PK): Unique sales line ID.
- `sale_date` (DATE, FK -> DimDate): Transaction date.
- `product_id` (VARCHAR, FK -> DimProduct): Product sold.
- `quantity` (INT): Units sold.
- `unit_sale_price` (DECIMAL): Selling price per unit ($).
- `total_sales_value` (DECIMAL): Quantity * Unit Sale Price ($).

### `FactInventory`
Stores warehouse stock positions across all active products.
- `inventory_id` (VARCHAR, PK): Unique inventory line ID.
- `product_id` (VARCHAR, FK -> DimProduct): Product foreign key.
- `vendor_id` (VARCHAR, FK -> DimVendor): Primary supplier foreign key.
- `stock_quantity` (INT): On-hand warehouse stock.
- `reorder_level` (INT): Reorder trigger point.
- `safety_stock` (INT): Safety buffer stock.
- `last_stock_date` (DATE): Timestamp of last inventory count.
