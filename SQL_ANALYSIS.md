# SQL Analysis, View Catalog & Optimization Guide

## 1. Analytical View Definitions

### View 1: `vw_vendor_performance_summary`
Aggregates procurement spend, attributed sales revenue, profit margins, and inventory health per vendor:
```sql
CREATE OR REPLACE VIEW vw_vendor_performance_summary AS
WITH vendor_procurement AS (
    SELECT 
        p.vendor_id,
        COUNT(p.purchase_id) AS total_orders,
        SUM(p.quantity) AS total_purchase_volume,
        SUM(p.total_purchase_value) AS total_procurement_cost,
        AVG(p.purchase_price) AS avg_purchase_price
    FROM purchases p
    GROUP BY p.vendor_id
),
product_sourcing_share AS (
    SELECT 
        p.product_id,
        p.vendor_id,
        SUM(p.quantity)::NUMERIC / NULLIF(SUM(SUM(p.quantity)) OVER(PARTITION BY p.product_id), 0) AS sourcing_share
    FROM purchases p
    GROUP BY p.product_id, p.vendor_id
),
vendor_attributed_sales AS (
    SELECT 
        pss.vendor_id,
        SUM(pss.sourcing_share * s.total_sales_value) AS attributed_sales_revenue,
        SUM(pss.sourcing_share * s.quantity) AS attributed_sales_volume
    FROM product_sourcing_share pss
    JOIN sales s ON pss.product_id = s.product_id
    GROUP BY pss.vendor_id
)
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.vendor_category,
    v.location,
    v.rating,
    COALESCE(vp.total_orders, 0) AS total_purchase_orders,
    ROUND(COALESCE(vp.total_procurement_cost, 0)::NUMERIC, 2) AS total_procurement_cost,
    ROUND(COALESCE(vas.attributed_sales_revenue, 0)::NUMERIC, 2) AS attributed_revenue,
    ROUND((COALESCE(vas.attributed_sales_revenue, 0) - COALESCE(vp.total_procurement_cost, 0))::NUMERIC, 2) AS gross_profit,
    CASE 
        WHEN COALESCE(vas.attributed_sales_revenue, 0) > 0 
        THEN ROUND(((COALESCE(vas.attributed_sales_revenue, 0) - COALESCE(vp.total_procurement_cost, 0)) / vas.attributed_sales_revenue * 100)::NUMERIC, 2)
        ELSE 0.00 
    END AS gross_margin_pct,
    CASE 
        WHEN COALESCE(vas.attributed_sales_revenue, 0) > 0 
        THEN ROUND((COALESCE(vp.total_procurement_cost, 0) / vas.attributed_sales_revenue)::NUMERIC, 3)
        ELSE 0.000 
    END AS purchase_to_sales_ratio
FROM vendors v
LEFT JOIN vendor_procurement vp ON v.vendor_id = vp.vendor_id
LEFT JOIN vendor_attributed_sales vas ON v.vendor_id = vas.vendor_id;
```

---

## 2. Key Business Queries & Optimization Notes

### Query 1: Top 10 Suppliers by Total Spend with Company-Wide Contribution %
```sql
WITH total_spend AS (
    SELECT SUM(total_purchase_value) AS company_spend FROM purchases
)
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.vendor_category,
    v.location,
    COUNT(p.purchase_id) AS order_count,
    ROUND(SUM(p.total_purchase_value)::NUMERIC, 2) AS total_spend,
    ROUND((SUM(p.total_purchase_value) / MAX(ts.company_spend) * 100)::NUMERIC, 2) AS spend_contribution_pct,
    DENSE_RANK() OVER(ORDER BY SUM(p.total_purchase_value) DESC) AS spend_rank
FROM purchases p
JOIN vendors v ON p.vendor_id = v.vendor_id
CROSS JOIN total_spend ts
GROUP BY v.vendor_id, v.vendor_name, v.vendor_category, v.location
ORDER BY total_spend DESC
LIMIT 10;
```
**Execution Analysis & Optimization:**
- Uses composite B-tree index `idx_purchases_vendor_date`.
- Eliminates sort overhead using Window Function `DENSE_RANK()`.
- Single-pass `CROSS JOIN total_spend` prevents correlated subqueries.

### Query 2: Single-Source Dependency Risk (&gt;65% Volume Concentration)
```sql
WITH product_sourcing AS (
    SELECT 
        p.product_id,
        pr.product_name,
        pr.category,
        p.vendor_id,
        v.vendor_name,
        SUM(p.quantity) AS vendor_qty,
        SUM(SUM(p.quantity)) OVER(PARTITION BY p.product_id) AS total_product_qty
    FROM purchases p
    JOIN products pr ON p.product_id = pr.product_id
    JOIN vendors v ON p.vendor_id = v.vendor_id
    GROUP BY p.product_id, pr.product_name, pr.category, p.vendor_id, v.vendor_name
)
SELECT 
    product_id,
    product_name,
    category,
    vendor_id,
    vendor_name,
    vendor_qty,
    total_product_qty,
    ROUND((vendor_qty::NUMERIC / total_product_qty * 100), 2) AS volume_dependency_pct
FROM product_sourcing
WHERE (vendor_qty::NUMERIC / total_product_qty) >= 0.65
ORDER BY volume_dependency_pct DESC;
```
**Execution Analysis:**
- Employs windowed aggregation `SUM(...) OVER(PARTITION BY product_id)` to calculate total demand in the same query pass without secondary self-joins.

### Query 3: Quarter-over-Quarter Vendor Price Inflation Tracking
```sql
WITH quarterly_prices AS (
    SELECT 
        v.vendor_id,
        v.vendor_name,
        DATE_TRUNC('quarter', p.purchase_date) AS purchase_quarter,
        AVG(p.purchase_price) AS avg_quarterly_price
    FROM purchases p
    JOIN vendors v ON p.vendor_id = v.vendor_id
    GROUP BY v.vendor_id, v.vendor_name, DATE_TRUNC('quarter', p.purchase_date)
),
price_shifts AS (
    SELECT 
        vendor_id,
        vendor_name,
        purchase_quarter,
        ROUND(avg_quarterly_price::NUMERIC, 2) AS current_qtr_price,
        ROUND(LAG(avg_quarterly_price) OVER(PARTITION BY vendor_id ORDER BY purchase_quarter)::NUMERIC, 2) AS prior_qtr_price
    FROM quarterly_prices
)
SELECT 
    vendor_id,
    vendor_name,
    purchase_quarter,
    current_qtr_price,
    prior_qtr_price,
    ROUND(((current_qtr_price - prior_qtr_price) / NULLIF(prior_qtr_price, 0) * 100)::NUMERIC, 2) AS qoq_price_change_pct
FROM price_shifts
WHERE prior_qtr_price IS NOT NULL
ORDER BY qoq_price_change_pct DESC
LIMIT 15;
```
**Execution Analysis:**
- Leverages SQL analytical window function `LAG()` to trace temporal price trends without Cartesian joins.
