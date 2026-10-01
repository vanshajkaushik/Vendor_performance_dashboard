"""
Pipeline Metrics Engine
Computes sourcing shares, gross margins, price variance vs standard cost,
procurement concentration %, and monthly trends.
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def compute_all_metrics(cleaned_tables, output_dir=PROCESSED_DIR):
    vendors = cleaned_tables['DimVendor'].copy()
    products = cleaned_tables['DimProduct'].copy()
    purchases = cleaned_tables['FactPurchases'].copy()
    sales = cleaned_tables['FactSales'].copy()
    inv = cleaned_tables['FactInventory'].copy()

    # 1. Procurement spend by vendor
    proc_summary = purchases.groupby('vendor_id').agg(
        total_procurement_cost=('total_purchase_value', 'sum'),
        total_purchase_quantity=('quantity', 'sum'),
        avg_purchase_price=('unit_purchase_price', 'mean'),
        total_orders=('purchase_id', 'count')
    ).reset_index()

    # 2. Product Sourcing Shares
    prod_v_qty = purchases.groupby(['product_id', 'vendor_id'])['quantity'].sum().reset_index()
    prod_tot_qty = purchases.groupby('product_id')['quantity'].sum().reset_index().rename(columns={'quantity': 'tot_prod_qty'})
    sourcing = pd.merge(prod_v_qty, prod_tot_qty, on='product_id')
    sourcing['sourcing_share'] = sourcing['quantity'] / sourcing['tot_prod_qty']

    # 3. Product Sales
    prod_sales = sales.groupby('product_id').agg(
        tot_sales=('total_sales_value', 'sum'),
        tot_sales_qty=('quantity', 'sum')
    ).reset_index()

    # 4. Attributed Sales by Vendor
    v_prod_sales = pd.merge(sourcing, prod_sales, on='product_id', how='left')
    v_prod_sales['attr_sales'] = v_prod_sales['sourcing_share'] * v_prod_sales['tot_sales'].fillna(0)
    v_prod_sales['attr_sales_qty'] = v_prod_sales['sourcing_share'] * v_prod_sales['tot_sales_qty'].fillna(0)

    v_sales = v_prod_sales.groupby('vendor_id').agg(
        total_revenue=('attr_sales', 'sum'),
        total_sales_quantity=('attr_sales_qty', 'sum')
    ).reset_index()

    # 5. Price Variance vs Standard Cost Benchmark
    p_with_cost = pd.merge(purchases, products[['product_id', 'standard_cost']], on='product_id')
    p_with_cost['price_diff_pct'] = ((p_with_cost['unit_purchase_price'] - p_with_cost['standard_cost']) / p_with_cost['standard_cost']) * 100
    v_pvar = p_with_cost.groupby('vendor_id').agg(
        price_variance_pct=('price_diff_pct', 'mean')
    ).reset_index()

    # 6. Sourcing Concentration % within Category
    v_spend = purchases.groupby('vendor_id')['total_purchase_value'].sum().reset_index().rename(columns={'total_purchase_value': 'v_spend'})
    v_spend_cat = pd.merge(v_spend, vendors[['vendor_id', 'vendor_category']], on='vendor_id')
    cat_tot = v_spend_cat.groupby('vendor_category')['v_spend'].sum().reset_index().rename(columns={'v_spend': 'cat_total_spend'})
    v_conc = pd.merge(v_spend_cat, cat_tot, on='vendor_category')
    v_conc['concentration_pct'] = ((v_conc['v_spend'] / v_conc['cat_total_spend']) * 100).round(2)

    # 7. Inventory Turnover
    inv_with_cost = pd.merge(inv, products[['product_id', 'standard_cost']], on='product_id')
    inv_with_cost['inv_val'] = inv_with_cost['stock_quantity'] * inv_with_cost['standard_cost']
    v_inv = inv_with_cost.groupby('vendor_id').agg(
        current_inventory_quantity=('stock_quantity', 'sum'),
        current_inventory_value=('inv_val', 'sum')
    ).reset_index()

    # Merge into summary dataframe
    df = pd.merge(vendors, proc_summary, on='vendor_id', how='left')
    df = pd.merge(df, v_sales, on='vendor_id', how='left')
    df = pd.merge(df, v_pvar, on='vendor_id', how='left')
    df = pd.merge(df, v_conc[['vendor_id', 'concentration_pct']], on='vendor_id', how='left')
    df = pd.merge(df, v_inv, on='vendor_id', how='left')

    df['total_procurement_cost'] = df['total_procurement_cost'].fillna(0).round(2)
    df['total_revenue'] = df['total_revenue'].fillna(0).round(2)
    df['total_orders'] = df['total_orders'].fillna(0).astype(int)
    df['total_purchase_quantity'] = df['total_purchase_quantity'].fillna(0).astype(int)
    df['total_sales_quantity'] = df['total_sales_quantity'].fillna(0).astype(int)
    df['price_variance_pct'] = df['price_variance_pct'].fillna(0).round(2)
    df['concentration_pct'] = df['concentration_pct'].fillna(0).round(2)
    df['current_inventory_value'] = df['current_inventory_value'].fillna(0).round(2)

    # Derived
    df['gross_profit'] = (df['total_revenue'] - df['total_procurement_cost']).round(2)
    df['gross_margin_pct'] = np.where(df['total_revenue'] > 0, (df['gross_profit'] / df['total_revenue'] * 100).round(2), 0.0)
    df['purchase_to_sales_ratio'] = np.where(df['total_revenue'] > 0, (df['total_procurement_cost'] / df['total_revenue']).round(3), 0.0)
    df['inventory_turnover'] = np.where(df['current_inventory_value'] > 0, (df['total_procurement_cost'] / df['current_inventory_value']).round(2), 0.0)

    # Monthly Trends
    purchases['month'] = pd.to_datetime(purchases['purchase_date']).dt.strftime('%Y-%m')
    sales['month'] = pd.to_datetime(sales['sale_date']).dt.strftime('%Y-%m')

    m_proc = purchases.groupby('month').agg(procurement_spend=('total_purchase_value', 'sum')).reset_index()
    m_sal = sales.groupby('month').agg(sales_revenue=('total_sales_value', 'sum')).reset_index()
    trends = pd.merge(m_sal, m_proc, on='month', how='outer').sort_values('month').fillna(0)
    trends['gross_profit'] = (trends['sales_revenue'] - trends['procurement_spend']).round(2)
    trends['gross_margin_pct'] = np.where(trends['sales_revenue'] > 0, (trends['gross_profit'] / trends['sales_revenue'] * 100).round(1), 0.0)
    trends.to_csv(os.path.join(output_dir, "monthly_trends.csv"), index=False)

    return df
