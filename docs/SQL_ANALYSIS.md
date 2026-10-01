# SQL Star Schema, Indexes & Analytical Query Justifications

This document explains the schema design, index strategy, and business insights driven by the analytical SQL queries in `sql/`.

---

## 1. Schema Design Justification
The database implements a **Star Schema** design:
- **Fact Tables:** `FactPurchases`, `FactSales`, `FactInventory` contain high-volume numerical events and foreign keys.
- **Dimension Tables:** `DimVendor`, `DimProduct`, `DimDate`, `DimCategory` contain descriptive attributes.
- **Why Star Schema?** Minimizes query join depth to $O(1)$ fact-to-dimension hops, eliminating multi-table snowflake traversals and maximizing cache efficiency in both PostgreSQL and SQLite.

---

## 2. B-Tree Composite Index Justification
The indexes in `sql/indexes.sql` were engineered based on PostgreSQL/SQLite `EXPLAIN QUERY PLAN` profiling:

1. `idx_purchases_vd (vendor_id, po_date)`:
   - **Justification:** Vendor drill-down queries filter by `vendor_id` and sort/range by `po_date`. A composite B-tree index eliminates table scans and in-memory file sorts, reducing query time from $O(N)$ to $O(\log N)$.
2. `idx_purchases_pid (product_id)`:
   - **Justification:** Accelerates fact-to-fact product reconciliation joins between `FactPurchases` and `FactSales`.
3. `idx_sales_pdate (product_id, sale_date)`:
   - **Justification:** Enables index-only scans for product revenue time-series aggregation.
4. `idx_vendors_code (vendor_code)`:
   - **Justification:** Guarantees $O(1)$ point lookups for intake duplicate checks and natural business key searches.

---

## 3. Core Analytical Business Queries

### Query 1: Top 10 Suppliers by Total Spend & Category Sourcing Share
```sql
SELECT
    v.vendor_name,
    c.category_name,
    COUNT(fp.purchase_id) AS total_orders,
    ROUND(SUM(fp.total_purchase_value), 2) AS total_spend,
    ROUND(SUM(fp.total_purchase_value) / SUM(SUM(fp.total_purchase_value)) OVER () * 100, 2) AS enterprise_spend_pct
FROM FactPurchases fp
JOIN DimVendor v ON fp.vendor_id = v.vendor_id
JOIN DimCategory c ON v.category_id = c.category_id
GROUP BY v.vendor_name, c.category_name
ORDER BY total_spend DESC
LIMIT 10;
```
- **Business Insight:** Identifies the vital 20% of suppliers driving 80% of enterprise spend (Pareto Principle), directing executive supplier management focus.

### Query 2: Single-Source Concentration Risk Alert (>35% Category Spend)
```sql
WITH category_totals AS (
    SELECT category_id, SUM(total_purchase_value) AS cat_total_spend
    FROM FactPurchases fp
    JOIN DimProduct p ON fp.product_id = p.product_id
    GROUP BY category_id
)
SELECT
    c.category_name,
    v.vendor_name,
    ROUND(SUM(fp.total_purchase_value), 2) AS vendor_spend,
    ROUND(ct.cat_total_spend, 2) AS category_total_spend,
    ROUND(SUM(fp.total_purchase_value) / ct.cat_total_spend * 100, 2) AS concentration_pct
FROM FactPurchases fp
JOIN DimVendor v ON fp.vendor_id = v.vendor_id
JOIN DimProduct p ON fp.product_id = p.product_id
JOIN DimCategory c ON p.category_id = c.category_id
JOIN category_totals ct ON c.category_id = ct.category_id
GROUP BY c.category_name, v.vendor_name, ct.cat_total_spend
HAVING (SUM(fp.total_purchase_value) / ct.cat_total_spend * 100) > 35.0
ORDER BY concentration_pct DESC;
```
- **Business Insight:** Identifies single points of failure in the supply chain where disruption at one supplier could shut down entire product lines.
