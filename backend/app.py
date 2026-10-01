"""
Vendor Performance Analytics - FastAPI Backend Server
Serves analytical endpoints, KPI metrics, vendor drill-downs, time-series trends,
and automated business insights from the underlying processed data and database.
"""

import os
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

app = FastAPI(
    title="Vendor Performance Analytics API",
    description="Production analytics backend powering the Power BI-style Vendor Performance Dashboard",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_df(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@app.get("/api/kpis")
def get_kpis(
    vendor: str = None,
    category: str = None,
    location: str = None,
    start_date: str = None,
    end_date: str = None
):
    """Returns top executive KPI cards with aggregated totals and margins."""
    purchases = load_df('purchases_clean.csv')
    sales = load_df('sales_clean.csv')
    vendors = load_df('vendors_clean.csv')
    products = load_df('products_clean.csv')
    scores = load_df('vendor_analytics_summary.csv')

    # Apply date filters to purchases
    if start_date:
        purchases = purchases[purchases['purchase_date'] >= start_date]
        sales = sales[sales['sale_date'] >= start_date]
    if end_date:
        purchases = purchases[purchases['purchase_date'] <= end_date]
        sales = sales[sales['sale_date'] <= end_date]

    if vendor and vendor != 'all':
        purchases = purchases[purchases['vendor_id'] == vendor]
        # filter sales to products supplied by this vendor
        v_prods = purchases['product_id'].unique()
        sales = sales[sales['product_id'].isin(v_prods)]
        scores = scores[scores['vendor_id'] == vendor]

    if category and category != 'all':
        cat_prods = products[products['category'] == category]['product_id'].unique()
        purchases = purchases[purchases['product_id'].isin(cat_prods)]
        sales = sales[sales['product_id'].isin(cat_prods)]
        scores = scores[scores['vendor_category'] == category]

    if location and location != 'all':
        loc_vendors = vendors[vendors['location'] == location]['vendor_id'].unique()
        purchases = purchases[purchases['vendor_id'].isin(loc_vendors)]
        scores = scores[scores['location'] == location]

    total_spend = float(purchases['total_purchase_value'].sum())
    total_sales = float(sales['total_sales_value'].sum())
    gross_profit = float(total_sales - total_spend)
    gross_margin = round((gross_profit / total_sales * 100), 2) if total_sales > 0 else 0.0

    purchase_volume = int(purchases['quantity'].sum())
    sales_volume = int(sales['quantity'].sum())
    active_vendors = int(purchases['vendor_id'].nunique())
    total_products = int(products['product_id'].nunique())
    avg_vps = round(float(scores['vendor_performance_score'].mean()), 1) if not scores.empty else 0.0

    return {
        "total_sales": round(total_sales, 2),
        "total_procurement": round(total_spend, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_margin_pct": gross_margin,
        "purchase_volume": purchase_volume,
        "sales_volume": sales_volume,
        "active_vendors": active_vendors,
        "total_products": total_products,
        "avg_vendor_performance_score": avg_vps,
        "purchase_to_sales_ratio": round(total_spend / total_sales, 3) if total_sales > 0 else 0.0
    }

@app.get("/api/trends")
def get_trends(
    vendor: str = None,
    category: str = None,
    start_date: str = None,
    end_date: str = None
):
    """Returns monthly time series for sales, procurement spend, and profit margins."""
    purchases = load_df('purchases_clean.csv')
    sales = load_df('sales_clean.csv')
    products = load_df('products_clean.csv')

    if vendor and vendor != 'all':
        purchases = purchases[purchases['vendor_id'] == vendor]
        v_prods = purchases['product_id'].unique()
        sales = sales[sales['product_id'].isin(v_prods)]

    if category and category != 'all':
        cat_prods = products[products['category'] == category]['product_id'].unique()
        purchases = purchases[purchases['product_id'].isin(cat_prods)]
        sales = sales[sales['product_id'].isin(cat_prods)]

    purchases['month'] = pd.to_datetime(purchases['purchase_date']).dt.strftime('%Y-%m')
    sales['month'] = pd.to_datetime(sales['sale_date']).dt.strftime('%Y-%m')

    m_proc = purchases.groupby('month').agg(procurement_spend=('total_purchase_value', 'sum')).reset_index()
    m_sales = sales.groupby('month').agg(sales_revenue=('total_sales_value', 'sum')).reset_index()

    trends = pd.merge(m_sales, m_proc, on='month', how='outer').sort_values('month').fillna(0)
    trends['gross_profit'] = (trends['sales_revenue'] - trends['procurement_spend']).round(2)
    trends['gross_margin_pct'] = np.where(
        trends['sales_revenue'] > 0,
        (trends['gross_profit'] / trends['sales_revenue'] * 100).round(1),
        0.0
    )
    trends['sales_revenue'] = trends['sales_revenue'].round(2)
    trends['procurement_spend'] = trends['procurement_spend'].round(2)

    if start_date:
        start_m = start_date[:7]
        trends = trends[trends['month'] >= start_m]
    if end_date:
        end_m = end_date[:7]
        trends = trends[trends['month'] <= end_m]

    return trends.to_dict(orient='records')

@app.get("/api/vendors")
def get_vendors(
    category: str = None,
    location: str = None,
    tier: str = None,
    sort_by: str = "vendor_performance_score",
    ascending: bool = False
):
    """Returns ranked list of vendors with scores, spend, revenue, margin, and tier."""
    df = load_df('vendor_analytics_summary.csv')
    if df.empty:
        return []

    if category and category != 'all':
        df = df[df['vendor_category'] == category]
    if location and location != 'all':
        df = df[df['location'] == location]
    if tier and tier != 'all':
        df = df[df['performance_tier'].str.contains(tier, case=False, na=False)]

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    return df.to_dict(orient='records')

@app.get("/api/vendors/{vendor_id}")
def get_vendor_details(vendor_id: str):
    """Returns detailed scorecard, product matrix, and historical trends for a single vendor."""
    scores = load_df('vendor_analytics_summary.csv')
    vendor_row = scores[scores['vendor_id'] == vendor_id]
    if vendor_row.empty:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    vendor_profile = vendor_row.iloc[0].to_dict()

    # Product breakdown for this vendor
    purchases = load_df('purchases_clean.csv')
    products = load_df('products_clean.csv')
    v_purchases = purchases[purchases['vendor_id'] == vendor_id]

    prod_summary = v_purchases.groupby('product_id').agg(
        orders_count=('purchase_id', 'count'),
        units_purchased=('quantity', 'sum'),
        total_spend=('total_purchase_value', 'sum'),
        avg_price_paid=('purchase_price', 'mean')
    ).reset_index()

    prod_summary = pd.merge(prod_summary, products, on='product_id', how='left')
    prod_summary['price_variance_pct'] = (
        (prod_summary['avg_price_paid'] - prod_summary['unit_cost']) / prod_summary['unit_cost'] * 100
    ).round(2)
    prod_summary['avg_price_paid'] = prod_summary['avg_price_paid'].round(2)
    prod_summary['total_spend'] = prod_summary['total_spend'].round(2)

    # Monthly spend trend for this vendor
    v_purchases['month'] = pd.to_datetime(v_purchases['purchase_date']).dt.strftime('%Y-%m')
    m_spend = v_purchases.groupby('month').agg(
        spend=('total_purchase_value', 'sum'),
        units=('quantity', 'sum')
    ).reset_index().sort_values('month')
    m_spend['spend'] = m_spend['spend'].round(2)

    return {
        "profile": vendor_profile,
        "monthly_trend": m_spend.to_dict(orient='records'),
        "products": prod_summary.sort_values('total_spend', ascending=False).to_dict(orient='records')
    }

@app.get("/api/categories")
def get_categories():
    """Returns product category profitability and spend aggregation."""
    cat_df = load_df('category_performance.csv')
    return cat_df.to_dict(orient='records')

@app.get("/api/scatter")
def get_scatter_data():
    """Returns purchase spend vs sales revenue per vendor for efficiency frontier plot."""
    df = load_df('vendor_analytics_summary.csv')
    records = []
    for _, r in df.iterrows():
        records.append({
            "vendor_id": r['vendor_id'],
            "vendor_name": r['vendor_name'],
            "vendor_category": r['vendor_category'],
            "total_procurement_cost": r['total_procurement_cost'],
            "total_revenue": r['total_revenue'],
            "gross_margin_pct": r['gross_margin_pct'],
            "purchase_to_sales_ratio": r['purchase_to_sales_ratio'],
            "vendor_performance_score": r['vendor_performance_score'],
            "performance_tier": r['performance_tier']
        })
    return records

@app.get("/api/pricing-anomalies")
def get_pricing_anomalies():
    """Returns products and vendors with high pricing variance vs catalog benchmarks."""
    purchases = load_df('purchases_clean.csv')
    products = load_df('products_clean.csv')
    vendors = load_df('vendors_clean.csv')

    merged = pd.merge(purchases, products[['product_id', 'product_name', 'category', 'unit_cost']], on='product_id')
    merged = pd.merge(merged, vendors[['vendor_id', 'vendor_name']], on='vendor_id')

    agg = merged.groupby(['vendor_id', 'vendor_name', 'product_id', 'product_name', 'category', 'unit_cost']).agg(
        avg_purchase_price=('purchase_price', 'mean'),
        order_count=('purchase_id', 'count'),
        total_qty=('quantity', 'sum')
    ).reset_index()

    agg['price_variance_pct'] = ((agg['avg_purchase_price'] - agg['unit_cost']) / agg['unit_cost'] * 100).round(2)
    agg['avg_purchase_price'] = agg['avg_purchase_price'].round(2)

    # Filter significant anomalies (> 7% variance)
    anomalies = agg[abs(agg['price_variance_pct']) >= 7.0].sort_values('price_variance_pct', ascending=False)
    return anomalies.to_dict(orient='records')

@app.get("/api/inventory")
def get_inventory_status():
    """Returns inventory health, stockout risks, and turnover."""
    inventory = load_df('inventory_clean.csv')
    products = load_df('products_clean.csv')
    vendors = load_df('vendors_clean.csv')

    df = pd.merge(inventory, products[['product_id', 'product_name', 'category', 'unit_cost']], on='product_id', how='left')
    df = pd.merge(df, vendors[['vendor_id', 'vendor_name']], on='vendor_id', how='left')

    df['inventory_value'] = (df['stock_quantity'] * df['unit_cost']).round(2)
    df['reorder_deficit'] = df['reorder_level'] - df['stock_quantity']

    conditions = [
        df['stock_quantity'] <= df['safety_stock'],
        df['stock_quantity'] <= df['reorder_level']
    ]
    statuses = ['CRITICAL: Stockout Risk', 'WARNING: Reorder Needed']
    df['status'] = np.select(conditions, statuses, default='HEALTHY')

    return df.sort_values('reorder_deficit', ascending=False).to_dict(orient='records')

@app.get("/api/insights")
def get_automated_insights():
    """Generates automated natural language executive insights from live dataset."""
    df = load_df('vendor_analytics_summary.csv')
    trends = load_df('monthly_trends.csv')
    cat_df = load_df('category_performance.csv')

    insights = []

    # 1. Top Revenue Contributor
    top_rev = df.sort_values('total_revenue', ascending=False).iloc[0]
    insights.append({
        "type": "revenue",
        "severity": "positive",
        "title": "Top Revenue Generator",
        "message": f"<b>{top_rev['vendor_name']}</b> leads all suppliers, contributing <b>{top_rev['revenue_share_pct']}%</b> of total company revenue (${top_rev['total_revenue']:,.2f}) with a healthy gross margin of {top_rev['gross_margin_pct']}%."
    })

    # 2. Spend vs Revenue Asymmetry (Inefficiency)
    inefficient = df.sort_values('purchase_to_sales_ratio', ascending=False).iloc[0]
    insights.append({
        "type": "efficiency",
        "severity": "warning",
        "title": "Procurement Efficiency Alert",
        "message": f"<b>{inefficient['vendor_name']}</b> accounts for <b>{inefficient['spend_share_pct']}%</b> of procurement spend but yields only <b>{inefficient['revenue_share_pct']}%</b> of attributed sales (Purchase-to-Sales ratio: {inefficient['purchase_to_sales_ratio']})."
    })

    # 3. Highest Margin Supplier
    top_margin = df.sort_values('gross_margin_pct', ascending=False).iloc[0]
    insights.append({
        "type": "margin",
        "severity": "positive",
        "title": "Profitability Champion",
        "message": f"<b>{top_margin['vendor_name']}</b> delivers the highest gross profit margin at <b>{top_margin['gross_margin_pct']}%</b>, generating ${top_margin['gross_profit']:,.2f} in gross profit."
    })

    # 4. Pricing Premium / Inflation Discrepancy
    highest_var = df.sort_values('price_variance_pct', ascending=False).iloc[0]
    insights.append({
        "type": "pricing",
        "severity": "danger",
        "title": "Pricing Anomaly Warning",
        "message": f"<b>{highest_var['vendor_name']}</b> charges an average purchase price <b>{highest_var['price_variance_pct']}% above the catalog benchmark cost</b>. Priority candidate for cost renegotiation."
    })

    # 5. Cost-Leader Supplier
    best_pricing = df.sort_values('price_variance_pct', ascending=True).iloc[0]
    insights.append({
        "type": "savings",
        "severity": "info",
        "title": "Cost Leader Advantage",
        "message": f"<b>{best_pricing['vendor_name']}</b> provides significant price leadership at <b>{abs(best_pricing['price_variance_pct'])}% below benchmark</b>, presenting volume consolidation opportunities."
    })

    return insights

@app.get("/api/pipeline-status")
def get_pipeline_status():
    """Returns ETL pipeline health, row counts, and data quality checks."""
    report_path = os.path.join(PROCESSED_DIR, 'data_quality_report.json')
    report = {}
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

    # Get row counts
    tables = ['vendors', 'products', 'purchases', 'sales', 'inventory']
    counts = {}
    for t in tables:
        clean_file = os.path.join(PROCESSED_DIR, f"{t}_clean.csv")
        raw_file = os.path.join(BASE_DIR, 'data', 'raw', f"{t}_raw.csv")
        counts[t] = {
            "clean_rows": len(pd.read_csv(clean_file)) if os.path.exists(clean_file) else 0,
            "raw_rows": len(pd.read_csv(raw_file)) if os.path.exists(raw_file) else 0
        }

    return {
        "pipeline_health": "OPTIMAL",
        "last_sync": "Automated ETL",
        "data_quality": report,
        "table_counts": counts
    }


# Mount frontend dist static files if built
DIST_DIR = os.path.join(BASE_DIR, 'dashboard', 'dist')
if os.path.exists(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")

if __name__ == '__main__':
    import uvicorn
    print("[+] Starting FastAPI server on http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
