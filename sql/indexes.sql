-- ====================================================================
-- PERFORMANCE INDEXING STRATEGY
-- Carefully indexed to optimize frequent dashboard slicing, foreign-key joins,
-- and time-series aggregations without unnecessary indexing overhead.
-- ====================================================================

-- 1. FactPurchases composite index for vendor time-series analysis
-- Justification: Drastically speeds up vendor monthly spend queries, historical price trend lookups,
-- and date-range slicers (Index Scan vs sequential scan over 10k+ rows).
CREATE INDEX idx_purchases_vendor_date ON FactPurchases(vendor_id, purchase_date);

-- 2. FactPurchases product foreign key
-- Justification: Accelerates joins between DimProduct and FactPurchases for category-level spend
-- and product-level vendor sourcing share calculations.
CREATE INDEX idx_purchases_product_id ON FactPurchases(product_id);

-- 3. FactSales composite index for product time-series sales
-- Justification: Powers product sales velocity, revenue aggregations, and monthly trend slicing.
CREATE INDEX idx_sales_product_date ON FactSales(product_id, sale_date);

-- 4. DimVendor category and location composite index
-- Justification: Accelerates dashboard categorical and geographical drill-down filters.
CREATE INDEX idx_vendors_cat_loc ON DimVendor(vendor_category, country);

-- 5. DimVendor unique lookup helpers for duplicate detection
-- Justification: Used in manual entry and CSV import to check existing vendor codes, names, and emails.
CREATE INDEX idx_vendors_name_lower ON DimVendor(LOWER(vendor_name));
CREATE INDEX idx_vendors_email_lower ON DimVendor(LOWER(email));

-- 6. FactInventory product & vendor lookup
-- Justification: Accelerates real-time reorder deficit calculations and stockout alerts.
CREATE INDEX idx_inventory_lookup ON FactInventory(product_id, vendor_id);
