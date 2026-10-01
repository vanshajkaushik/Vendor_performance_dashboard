-- ====================================================================
-- BUSINESS ANALYTICAL QUERIES (OPTIMIZED SQL)
-- Direct implementations answering core business & interview questions
-- ====================================================================

-- Query 1: Top 10 Suppliers by Total Spend with Company-Wide Contribution %
WITH total_company_spend AS (
    SELECT SUM(total_purchase_value) AS total_spend FROM FactPurchases
)
SELECT 
    v.vendor_code,
    v.vendor_name,
    v.vendor_category,
    v.country,
    COUNT(p.purchase_id) AS order_count,
    ROUND(SUM(p.total_purchase_value)::NUMERIC, 2) AS total_spend,
    ROUND((SUM(p.total_purchase_value) / MAX(tcs.total_spend) * 100)::NUMERIC, 2) AS spend_contribution_pct,
    DENSE_RANK() OVER(ORDER BY SUM(p.total_purchase_value) DESC) AS spend_rank
FROM FactPurchases p
JOIN DimVendor v ON p.vendor_id = v.vendor_id
CROSS JOIN total_company_spend tcs
GROUP BY v.vendor_code, v.vendor_name, v.vendor_category, v.country
ORDER BY total_spend DESC
LIMIT 10;

-- Query 2: High-Cost Low-Margin Suppliers (At-Risk Identification)
SELECT 
    vendor_code,
    vendor_name,
    vendor_category,
    total_procurement_cost,
    attributed_revenue,
    gross_margin_pct,
    purchase_to_sales_ratio
FROM vw_vendor_performance_summary
WHERE vendor_maturity = 'Established Vendor'
  AND (purchase_to_sales_ratio > 0.70 OR gross_margin_pct < 25.0)
ORDER BY purchase_to_sales_ratio DESC;

-- Query 3: Single-Source Product Dependency Risk Analysis (>65% Volume Dependency)
WITH product_sourcing AS (
    SELECT 
        p.product_id,
        pr.product_code,
        pr.product_name,
        c.category_name,
        p.vendor_id,
        v.vendor_name,
        SUM(p.quantity) AS vendor_qty,
        SUM(SUM(p.quantity)) OVER(PARTITION BY p.product_id) AS total_product_qty
    FROM FactPurchases p
    JOIN DimProduct pr ON p.product_id = pr.product_id
    JOIN DimCategory c ON pr.category_id = c.category_id
    JOIN DimVendor v ON p.vendor_id = v.vendor_id
    GROUP BY p.product_id, pr.product_code, pr.product_name, c.category_name, p.vendor_id, v.vendor_name
)
SELECT 
    product_code,
    product_name,
    category_name,
    vendor_name,
    vendor_qty,
    total_product_qty,
    ROUND((vendor_qty::NUMERIC / total_product_qty * 100), 2) AS volume_dependency_pct
FROM product_sourcing
WHERE (vendor_qty::NUMERIC / total_product_qty) >= 0.65
ORDER BY volume_dependency_pct DESC;

-- Query 4: Sourcing Concentration Risks (>35% of Category Spend in Single Vendor)
SELECT 
    vendor_name,
    vendor_category,
    vendor_spend,
    total_category_spend,
    concentration_pct,
    risk_tier
FROM vw_vendor_concentration
WHERE concentration_pct >= 30.0
ORDER BY concentration_pct DESC;
