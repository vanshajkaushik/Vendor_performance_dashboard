"""
Analytical Transformations and Metric Engineering
Computes procurement spend, attributed sales revenue, gross margins, price variances,
inventory turnover, and monthly trend aggregates across vendors and product categories.
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def compute_vendor_summary(cleaned_datasets):
    """
    Computes comprehensive vendor analytics:
    - Procurement Spend
    - Attributed Sales Revenue
    - Gross Profit & Gross Margin %
    - Sourced Volume vs Sold Volume
    - Average Purchase Price
    - Purchase-to-Sales Ratio
    - Price Variance % vs Product Benchmark
    - Inventory Value & Turnover
    """
    vendors = cleaned_datasets['vendors'].copy()
    products = cleaned_datasets['products'].copy()
    purchases = cleaned_datasets['purchases'].copy()
    sales = cleaned_datasets['sales'].copy()
    inventory = cleaned_datasets['inventory'].copy()

    # 1. Procurement by Vendor
    proc_summary = purchases.groupby('vendor_id').agg(
        total_procurement_cost=('total_purchase_value', 'sum'),
        total_purchase_quantity=('quantity', 'sum'),
        avg_purchase_price=('purchase_price', 'mean'),
        total_orders=('purchase_id', 'count')
    ).reset_index()

    # 2. Product Sourcing Shares by Vendor
    # How much of each product's total incoming supply comes from each vendor?
    prod_vendor_qty = purchases.groupby(['product_id', 'vendor_id'])['quantity'].sum().reset_index()
    prod_total_qty = purchases.groupby('product_id')['quantity'].sum().reset_index().rename(columns={'quantity': 'total_prod_purchased'})
    prod_sourcing = pd.merge(prod_vendor_qty, prod_total_qty, on='product_id')
    prod_sourcing['sourcing_share'] = prod_sourcing['quantity'] / prod_sourcing['total_prod_purchased']

    # 3. Sales by Product
    prod_sales = sales.groupby('product_id').agg(
        total_sales_value=('total_sales_value', 'sum'),
        total_sales_quantity=('quantity', 'sum'),
        avg_selling_price=('selling_price', 'mean')
    ).reset_index()

    # 4. Attributed Sales by Vendor: Vendor Share * Product Sales
    vendor_prod_attr = pd.merge(prod_sourcing, prod_sales, on='product_id', how='left')
    vendor_prod_attr['attributed_sales'] = vendor_prod_attr['sourcing_share'] * vendor_prod_attr['total_sales_value']
    vendor_prod_attr['attributed_sales_qty'] = vendor_prod_attr['sourcing_share'] * vendor_prod_attr['total_sales_quantity']

    vendor_sales_attr = vendor_prod_attr.groupby('vendor_id').agg(
        total_revenue=('attributed_sales', 'sum'),
        total_sales_quantity=('attributed_sales_qty', 'sum')
    ).reset_index()

    # 5. Price Variance vs Product Benchmark Unit Cost
    purchases_with_bm = pd.merge(purchases, products[['product_id', 'unit_cost', 'category']], on='product_id', how='left')
    purchases_with_bm['price_diff_pct'] = ((purchases_with_bm['purchase_price'] - purchases_with_bm['unit_cost']) / purchases_with_bm['unit_cost']) * 100
    vendor_price_var = purchases_with_bm.groupby('vendor_id').agg(
        price_variance_pct=('price_diff_pct', 'mean')
    ).reset_index()

    # 6. Inventory Turnover by Vendor
    # Inventory value = stock_quantity * average purchase price
    inv_with_cost = pd.merge(inventory, products[['product_id', 'unit_cost']], on='product_id', how='left')
    inv_with_cost['inv_value'] = inv_with_cost['stock_quantity'] * inv_with_cost['unit_cost']
    inv_summary = inv_with_cost.groupby('vendor_id').agg(
        current_inventory_quantity=('stock_quantity', 'sum'),
        current_inventory_value=('inv_value', 'sum')
    ).reset_index()

    # 7. Merge all analytical dimensions into vendors dataframe
    df = pd.merge(vendors, proc_summary, on='vendor_id', how='left')
    df = pd.merge(df, vendor_sales_attr, on='vendor_id', how='left')
    df = pd.merge(df, vendor_price_var, on='vendor_id', how='left')
    df = pd.merge(df, inv_summary, on='vendor_id', how='left')

    # Fill any NaNs
    df['total_procurement_cost'] = df['total_procurement_cost'].fillna(0).round(2)
    df['total_revenue'] = df['total_revenue'].fillna(0).round(2)
    df['total_purchase_quantity'] = df['total_purchase_quantity'].fillna(0).astype(int)
    df['total_sales_quantity'] = df['total_sales_quantity'].fillna(0).astype(int)
    df['price_variance_pct'] = df['price_variance_pct'].fillna(0).round(2)
    df['current_inventory_value'] = df['current_inventory_value'].fillna(0).round(2)

    # Derived Calculations
    df['gross_profit'] = (df['total_revenue'] - df['procurement_cost']).round(2) if 'procurement_cost' in df else (df['total_revenue'] - df['total_procurement_cost']).round(2)
    df['gross_margin_pct'] = np.where(df['total_revenue'] > 0, (df['gross_profit'] / df['total_revenue'] * 100).round(2), 0.0)
    df['purchase_to_sales_ratio'] = np.where(df['total_revenue'] > 0, (df['total_procurement_cost'] / df['total_revenue']).round(3), 0.0)
    df['inventory_turnover'] = np.where(df['current_inventory_value'] > 0, (df['total_procurement_cost'] / df['current_inventory_value']).round(2), 0.0)
    
    total_spend = df['total_procurement_cost'].sum()
    total_rev = df['total_revenue'].sum()
    df['spend_share_pct'] = ((df['total_procurement_cost'] / total_spend) * 100).round(2)
    df['revenue_share_pct'] = ((df['total_revenue'] / total_rev) * 100).round(2)

    return df

def compute_monthly_trends(cleaned_datasets):
    """
    Computes monthly time-series for Sales, Procurement, Gross Profit, and Margin %.
    """
    purchases = cleaned_datasets['purchases'].copy()
    sales = cleaned_datasets['sales'].copy()

    purchases['month'] = pd.to_datetime(purchases['purchase_date']).dt.strftime('%Y-%m')
    sales['month'] = pd.to_datetime(sales['sale_date']).dt.strftime('%Y-%m')

    m_proc = purchases.groupby('month').agg(
        procurement_cost=('total_purchase_value', 'sum'),
        purchase_quantity=('quantity', 'sum'),
        purchase_orders=('purchase_id', 'count')
    ).reset_index()

    m_sales = sales.groupby('month').agg(
        sales_revenue=('total_sales_value', 'sum'),
        sales_quantity=('quantity', 'sum'),
        sales_orders=('sale_id', 'count')
    ).reset_index()

    trends = pd.merge(m_sales, m_proc, on='month', how='outer').sort_values('month').fillna(0)
    trends['gross_profit'] = (trends['sales_revenue'] - trends['procurement_cost']).round(2)
    trends['gross_margin_pct'] = np.where(
        trends['sales_revenue'] > 0,
        (trends['gross_profit'] / trends['sales_revenue'] * 100).round(2),
        0.0
    )
    trends['procurement_cost'] = trends['procurement_cost'].round(2)
    trends['sales_revenue'] = trends['sales_revenue'].round(2)
    return trends

def compute_category_performance(cleaned_datasets):
    """
    Computes category-level spend, revenue, margin %, and product count.
    """
    products = cleaned_datasets['products'].copy()
    purchases = cleaned_datasets['purchases'].copy()
    sales = cleaned_datasets['sales'].copy()

    p_with_cat = pd.merge(purchases, products[['product_id', 'category']], on='product_id')
    cat_proc = p_with_cat.groupby('category').agg(
        procurement_cost=('total_purchase_value', 'sum'),
        purchase_quantity=('quantity', 'sum')
    ).reset_index()

    s_with_cat = pd.merge(sales, products[['product_id', 'category']], on='product_id')
    cat_sales = s_with_cat.groupby('category').agg(
        sales_revenue=('total_sales_value', 'sum'),
        sales_quantity=('quantity', 'sum')
    ).reset_index()

    cat_df = pd.merge(cat_sales, cat_proc, on='category', how='outer').fillna(0)
    cat_df['gross_profit'] = (cat_df['sales_revenue'] - cat_df['procurement_cost']).round(2)
    cat_df['gross_margin_pct'] = np.where(
        cat_df['sales_revenue'] > 0,
        (cat_df['gross_profit'] / cat_df['sales_revenue'] * 100).round(2),
        0.0
    )
    
    prod_counts = products.groupby('category')['product_id'].count().reset_index().rename(columns={'product_id': 'product_count'})
    cat_df = pd.merge(cat_df, prod_counts, on='category', how='left')
    return cat_df

def compute_product_dependency(cleaned_datasets):
    """
    Calculates single-source dependency: which vendors supply what share of each product.
    """
    purchases = cleaned_datasets['purchases'].copy()
    products = cleaned_datasets['products'].copy()
    vendors = cleaned_datasets['vendors'].copy()

    prod_v_spend = purchases.groupby(['product_id', 'vendor_id']).agg(
        vendor_spend=('total_purchase_value', 'sum'),
        vendor_qty=('quantity', 'sum')
    ).reset_index()

    prod_total_spend = purchases.groupby('product_id')['total_purchase_value'].sum().reset_index().rename(
        columns={'total_purchase_value': 'total_product_spend'}
    )

    dep = pd.merge(prod_v_spend, prod_total_spend, on='product_id')
    dep['dependency_pct'] = ((dep['vendor_spend'] / dep['total_product_spend']) * 100).round(2)

    dep = pd.merge(dep, products[['product_id', 'product_name', 'category', 'unit_cost', 'selling_price']], on='product_id')
    dep = pd.merge(dep, vendors[['vendor_id', 'vendor_name']], on='vendor_id')
    return dep

def calculate_all_metrics(cleaned_datasets, output_dir=PROCESSED_DATA_DIR):
    """Calculates all analytical views and writes summary files."""
    print("\n" + "="*50)
    print(" CALCULATING ANALYTICAL METRICS & AGGREGATIONS")
    print("="*50)
    
    vendor_summary = compute_vendor_summary(cleaned_datasets)
    monthly_trends = compute_monthly_trends(cleaned_datasets)
    category_perf = compute_category_performance(cleaned_datasets)
    product_dep = compute_product_dependency(cleaned_datasets)

    vendor_summary.to_csv(os.path.join(output_dir, "vendor_summary_pre_scoring.csv"), index=False)
    monthly_trends.to_csv(os.path.join(output_dir, "monthly_trends.csv"), index=False)
    category_perf.to_csv(os.path.join(output_dir, "category_performance.csv"), index=False)
    product_dep.to_csv(os.path.join(output_dir, "product_dependency.csv"), index=False)

    print(f"[+] Computed metrics across {len(vendor_summary)} vendors, {len(monthly_trends)} months, {len(category_perf)} categories")
    return {
        "vendor_summary": vendor_summary,
        "monthly_trends": monthly_trends,
        "category_performance": category_perf,
        "product_dependency": product_dep
    }
