-- ====================================================================
-- ANALYTICAL SQL VIEWS
-- Power BI and Web Dashboard Analytical Foundations
-- ====================================================================

-- View 1: Comprehensive Vendor Performance Summary
CREATE OR REPLACE VIEW vw_vendor_performance_summary AS
WITH vendor_procurement AS (
    SELECT 
        p.vendor_id,
        COUNT(p.purchase_id) AS total_orders,
        SUM(p.quantity) AS total_purchase_volume,
        SUM(p.total_purchase_value) AS total_procurement_cost,
        AVG(p.unit_purchase_price) AS avg_purchase_price
    FROM FactPurchases p
    GROUP BY p.vendor_id
),
product_sourcing_share AS (
    SELECT 
        p.product_id,
        p.vendor_id,
        SUM(p.quantity)::NUMERIC / NULLIF(SUM(SUM(p.quantity)) OVER(PARTITION BY p.product_id), 0) AS sourcing_share
    FROM FactPurchases p
    GROUP BY p.product_id, p.vendor_id
),
vendor_attributed_sales AS (
    SELECT 
        pss.vendor_id,
        SUM(pss.sourcing_share * s.total_sales_value) AS attributed_sales_revenue,
        SUM(pss.sourcing_share * s.quantity) AS attributed_sales_volume
    FROM product_sourcing_share pss
    JOIN FactSales s ON pss.product_id = s.product_id
    GROUP BY pss.vendor_id
),
vendor_inv AS (
    SELECT 
        i.vendor_id,
        SUM(i.stock_quantity) AS current_stock,
        SUM(i.stock_quantity * pr.standard_cost) AS total_inventory_value
    FROM FactInventory i
    JOIN DimProduct pr ON i.product_id = pr.product_id
    GROUP BY i.vendor_id
)
SELECT 
    v.vendor_id,
    v.vendor_code,
    v.vendor_name,
    v.vendor_category,
    v.country AS location,
    v.status,
    v.rating,
    v.payment_terms,
    COALESCE(vp.total_orders, 0) AS total_purchase_orders,
    COALESCE(vp.total_purchase_volume, 0) AS total_purchase_volume,
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
    END AS purchase_to_sales_ratio,
    COALESCE(vi.current_stock, 0) AS current_stock_qty,
    ROUND(COALESCE(vi.total_inventory_value, 0)::NUMERIC, 2) AS current_inventory_value,
    CASE
        WHEN COALESCE(vp.total_orders, 0) < 3 OR COALESCE(vp.total_procurement_cost, 0) = 0
        THEN 'New / Insufficient Data'
        ELSE 'Established Vendor'
    END AS vendor_maturity
FROM DimVendor v
LEFT JOIN vendor_procurement vp ON v.vendor_id = vp.vendor_id
LEFT JOIN vendor_attributed_sales vas ON v.vendor_id = vas.vendor_id
LEFT JOIN vendor_inv vi ON v.vendor_id = vi.vendor_id;

-- View 2: Monthly Procurement vs Sales Trends
CREATE OR REPLACE VIEW vw_monthly_procurement_sales AS
WITH monthly_proc AS (
    SELECT 
        d.month_year AS month_key,
        MIN(d.date) AS start_of_month,
        SUM(p.total_purchase_value) AS procurement_spend,
        SUM(p.quantity) AS purchase_volume,
        COUNT(p.purchase_id) AS purchase_orders
    FROM FactPurchases p
    JOIN DimDate d ON p.purchase_date = d.date
    GROUP BY d.month_year
),
monthly_sales AS (
    SELECT 
        d.month_year AS month_key,
        MIN(d.date) AS start_of_month,
        SUM(s.total_sales_value) AS sales_revenue,
        SUM(s.quantity) AS sales_volume,
        COUNT(s.sale_id) AS sales_orders
    FROM FactSales s
    JOIN DimDate d ON s.sale_date = d.date
    GROUP BY d.month_year
)
SELECT 
    COALESCE(ms.month_key, mp.month_key) AS month_key,
    ROUND(COALESCE(ms.sales_revenue, 0)::NUMERIC, 2) AS sales_revenue,
    ROUND(COALESCE(mp.procurement_spend, 0)::NUMERIC, 2) AS procurement_spend,
    ROUND((COALESCE(ms.sales_revenue, 0) - COALESCE(mp.procurement_spend, 0))::NUMERIC, 2) AS monthly_gross_profit,
    CASE 
        WHEN COALESCE(ms.sales_revenue, 0) > 0 
        THEN ROUND(((COALESCE(ms.sales_revenue, 0) - COALESCE(mp.procurement_spend, 0)) / ms.sales_revenue * 100)::NUMERIC, 2)
        ELSE 0.00 
    END AS monthly_margin_pct,
    COALESCE(ms.sales_volume, 0) AS sales_volume,
    COALESCE(mp.purchase_volume, 0) AS purchase_volume
FROM monthly_sales ms
FULL OUTER JOIN monthly_proc mp ON ms.month_key = mp.month_key
ORDER BY COALESCE(ms.start_of_month, mp.start_of_month);

-- View 3: Category Performance & Profitability
CREATE OR REPLACE VIEW vw_category_profitability AS
WITH cat_sales AS (
    SELECT 
        c.category_name,
        SUM(s.total_sales_value) AS total_sales,
        SUM(s.quantity) AS total_units_sold
    FROM FactSales s
    JOIN DimProduct p ON s.product_id = p.product_id
    JOIN DimCategory c ON p.category_id = c.category_id
    GROUP BY c.category_name
),
cat_proc AS (
    SELECT 
        c.category_name,
        SUM(pu.total_purchase_value) AS total_spend,
        SUM(pu.quantity) AS total_units_procured
    FROM FactPurchases pu
    JOIN DimProduct p ON pu.product_id = p.product_id
    JOIN DimCategory c ON p.category_id = c.category_id
    GROUP BY c.category_name
)
SELECT 
    cs.category_name,
    ROUND(cs.total_sales::NUMERIC, 2) AS sales_revenue,
    ROUND(cp.total_spend::NUMERIC, 2) AS procurement_spend,
    ROUND((cs.total_sales - cp.total_spend)::NUMERIC, 2) AS gross_profit,
    ROUND(((cs.total_sales - cp.total_spend) / cs.total_sales * 100)::NUMERIC, 2) AS gross_margin_pct,
    cs.total_units_sold,
    cp.total_units_procured
FROM cat_sales cs
JOIN cat_proc cp ON cs.category_name = cp.category_name;

-- View 4: Sourcing Concentration Risk by Category
CREATE OR REPLACE VIEW vw_vendor_concentration AS
WITH vendor_cat_spend AS (
    SELECT 
        v.vendor_id,
        v.vendor_name,
        v.vendor_category,
        SUM(p.total_purchase_value) AS vendor_spend
    FROM FactPurchases p
    JOIN DimVendor v ON p.vendor_id = v.vendor_id
    GROUP BY v.vendor_id, v.vendor_name, v.vendor_category
),
cat_total_spend AS (
    SELECT 
        v.vendor_category,
        SUM(p.total_purchase_value) AS total_category_spend
    FROM FactPurchases p
    JOIN DimVendor v ON p.vendor_id = v.vendor_id
    GROUP BY v.vendor_category
)
SELECT 
    vcs.vendor_id,
    vcs.vendor_name,
    vcs.vendor_category,
    ROUND(vcs.vendor_spend::NUMERIC, 2) AS vendor_spend,
    ROUND(cts.total_category_spend::NUMERIC, 2) AS total_category_spend,
    ROUND((vcs.vendor_spend / cts.total_category_spend * 100)::NUMERIC, 2) AS concentration_pct,
    CASE 
        WHEN (vcs.vendor_spend / cts.total_category_spend) > 0.35 
        THEN 'HIGH CONCENTRATION RISK'
        WHEN (vcs.vendor_spend / cts.total_category_spend) > 0.20 
        THEN 'MODERATE CONCENTRATION'
        ELSE 'BALANCED'
    END AS risk_tier
FROM vendor_cat_spend vcs
JOIN cat_total_spend cts ON vcs.vendor_category = cts.vendor_category
ORDER BY concentration_pct DESC;
