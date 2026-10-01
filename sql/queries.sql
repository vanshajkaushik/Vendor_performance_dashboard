-- ====================================================================
-- BUSINESS ANALYTICAL QUERIES & EXECUTION PLAN ANALYSIS
-- Demonstrates production SQL proficiency, aggregations, window functions,
-- CTEs, and index-optimized query patterns.
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Top 10 Vendors by Total Procurement Spend & Contribution %
-- Business Question: Which vendors consume the majority of our procurement capital?
-- --------------------------------------------------------------------
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
-- EXPLAIN PLAN: Uses idx_purchases_vendor_date for HashAggregate on vendor_id.

-- --------------------------------------------------------------------
-- QUERY 2: Top Vendors by Generated Attributed Sales & Margin %
-- Business Question: Which vendors generate the most revenue and highest margins?
-- --------------------------------------------------------------------
SELECT 
    vendor_id,
    vendor_name,
    vendor_category,
    attributed_revenue,
    total_procurement_cost,
    gross_profit,
    gross_margin_pct,
    purchase_to_sales_ratio
FROM vw_vendor_performance_summary
ORDER BY attributed_revenue DESC
LIMIT 10;

-- --------------------------------------------------------------------
-- QUERY 3: High-Cost / Low-Efficiency Vendors (At-Risk Identification)
-- Business Question: Which vendors have high spend but poor sales conversion or compressed margins?
-- --------------------------------------------------------------------
SELECT 
    vendor_id,
    vendor_name,
    vendor_category,
    total_procurement_cost,
    attributed_revenue,
    gross_margin_pct,
    purchase_to_sales_ratio
FROM vw_vendor_performance_summary
WHERE purchase_to_sales_ratio > 0.70 OR gross_margin_pct < 25.0
ORDER BY purchase_to_sales_ratio DESC;

-- --------------------------------------------------------------------
-- QUERY 4: Single-Source Product Dependency Risk Analysis
-- Business Question: Which products are dangerously dependent (>70% volume) on a single vendor?
-- --------------------------------------------------------------------
WITH product_sourcing AS (
    SELECT 
        p.product_id,
        pr.product_name,
        pr.category,
        p.vendor_id,
        v.vendor_name,
        SUM(p.quantity) AS vendor_qty,
        SUM(p.total_purchase_value) AS vendor_spend,
        SUM(SUM(p.quantity)) OVER(PARTITION BY p.product_id) AS total_product_qty,
        SUM(SUM(p.total_purchase_value)) OVER(PARTITION BY p.product_id) AS total_product_spend
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
    ROUND((vendor_qty::NUMERIC / total_product_qty * 100), 2) AS volume_dependency_pct,
    ROUND((vendor_spend::NUMERIC / total_product_spend * 100), 2) AS spend_dependency_pct
FROM product_sourcing
WHERE (vendor_qty::NUMERIC / total_product_qty) >= 0.65
ORDER BY volume_dependency_pct DESC;

-- --------------------------------------------------------------------
-- QUERY 5: Vendor Purchase Price Inflation & Volatility Over Time
-- Business Question: Which vendors are exhibiting the highest price inflation quarter-over-quarter?
-- --------------------------------------------------------------------
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

-- --------------------------------------------------------------------
-- QUERY 6: Inventory Health & Stockout Risk by Product & Vendor
-- Business Question: Which products are below reorder thresholds, and who is the primary supplier?
-- --------------------------------------------------------------------
SELECT 
    i.product_id,
    p.product_name,
    p.category,
    i.vendor_id,
    v.vendor_name,
    i.stock_quantity,
    i.reorder_level,
    i.safety_stock,
    (i.reorder_level - i.stock_quantity) AS units_below_reorder,
    CASE 
        WHEN i.stock_quantity <= i.safety_stock THEN 'CRITICAL: Stockout Risk'
        WHEN i.stock_quantity <= i.reorder_level THEN 'WARNING: Reorder Required'
        ELSE 'HEALTHY'
    END AS stock_status
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN vendors v ON i.vendor_id = v.vendor_id
WHERE i.stock_quantity <= i.reorder_level
ORDER BY units_below_reorder DESC;

-- --------------------------------------------------------------------
-- QUERY 7: Monthly Procurement Spend vs Sales Revenue Growth (MoM)
-- Business Question: Are procurement expenses outpacing sales revenue growth?
-- --------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT 
        month_key,
        sales_revenue,
        procurement_spend,
        monthly_gross_profit,
        monthly_margin_pct,
        LAG(sales_revenue) OVER(ORDER BY month_key) AS prev_sales,
        LAG(procurement_spend) OVER(ORDER BY month_key) AS prev_spend
    FROM vw_monthly_procurement_sales
)
SELECT 
    month_key,
    sales_revenue,
    procurement_spend,
    ROUND(((sales_revenue - prev_sales) / NULLIF(prev_sales, 0) * 100)::NUMERIC, 2) AS sales_growth_mom_pct,
    ROUND(((procurement_spend - prev_spend) / NULLIF(prev_spend, 0) * 100)::NUMERIC, 2) AS spend_growth_mom_pct,
    monthly_margin_pct
FROM monthly_metrics
ORDER BY month_key;
