"""
Analytics API Router
Serves executive KPIs, monthly trends, procurement concentration, pricing anomalies,
and automated natural language insights.
"""

import os
import pandas as pd
from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def load_df(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@router.get("/kpis")
def get_kpis(
    vendor: str = None,
    category: str = None,
    location: str = None,
    start_date: str = None,
    end_date: str = None
):
    purchases = load_df('FactPurchases.csv')
    sales = load_df('FactSales.csv')
    vendors = load_df('DimVendor.csv')
    products = load_df('DimProduct.csv')
    scores = load_df('vendor_analytics_summary.csv')

    if start_date:
        purchases = purchases[purchases['purchase_date'] >= start_date]
        sales = sales[sales['sale_date'] >= start_date]
    if end_date:
        purchases = purchases[purchases['purchase_date'] <= end_date]
        sales = sales[sales['sale_date'] <= end_date]

    if vendor and vendor != 'all':
        purchases = purchases[purchases['vendor_id'] == vendor]
        v_prods = purchases['product_id'].unique()
        sales = sales[sales['product_id'].isin(v_prods)]

    if category and category != 'all':
        cat_p = products[products['category_name'] == category]['product_id'].unique() if 'category_name' in products.columns else []
        if len(cat_p) > 0:
            purchases = purchases[purchases['product_id'].isin(cat_p)]
            sales = sales[sales['product_id'].isin(cat_p)]

    total_procurement = float(purchases['total_purchase_value'].sum())
    total_sales = float(sales['total_sales_value'].sum())
    gross_profit = float(total_sales - total_procurement)
    gross_margin = round((gross_profit / total_sales * 100), 2) if total_sales > 0 else 0.0

    est_scores = scores.dropna(subset=['vendor_performance_score'])
    avg_vps = round(float(est_scores['vendor_performance_score'].mean()), 1) if not est_scores.empty else 0.0

    return {
        "total_sales": round(total_sales, 2),
        "total_procurement": round(total_procurement, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_margin_pct": gross_margin,
        "purchase_volume": int(purchases['quantity'].sum()),
        "sales_volume": int(sales['quantity'].sum()),
        "active_vendors": int(vendors[vendors['status'] == 'Active']['vendor_id'].nunique()),
        "total_vendors": len(vendors),
        "total_products": len(products),
        "avg_vendor_performance_score": avg_vps,
        "purchase_to_sales_ratio": round(total_procurement / total_sales, 3) if total_sales > 0 else 0.0
    }

@router.get("/trends")
def get_trends():
    trends = load_df('monthly_trends.csv')
    return trends.to_dict(orient='records')

@router.get("/concentration")
def get_concentration():
    scores = load_df('vendor_analytics_summary.csv')
    if scores.empty:
        return []
    
    records = []
    for _, r in scores.iterrows():
        conc = r.get('concentration_pct', 0)
        records.append({
            "vendor_id": r['vendor_id'],
            "vendor_code": r['vendor_code'],
            "vendor_name": r['vendor_name'],
            "vendor_category": r['vendor_category'],
            "total_procurement_cost": r['total_procurement_cost'],
            "concentration_pct": conc,
            "risk_tier": "HIGH CONCENTRATION RISK" if conc > 35 else "MODERATE CONCENTRATION" if conc > 20 else "BALANCED"
        })
    return sorted(records, key=lambda x: x['concentration_pct'], reverse=True)

@router.get("/pricing-anomalies")
def get_pricing_anomalies():
    purchases = load_df('FactPurchases.csv')
    products = load_df('DimProduct.csv')
    vendors = load_df('DimVendor.csv')

    merged = pd.merge(purchases, products[['product_id', 'product_name', 'standard_cost']], on='product_id')
    merged = pd.merge(merged, vendors[['vendor_id', 'vendor_name']], on='vendor_id')

    agg = merged.groupby(['vendor_id', 'vendor_name', 'product_id', 'product_name', 'standard_cost']).agg(
        avg_purchase_price=('unit_purchase_price', 'mean'),
        total_qty=('quantity', 'sum')
    ).reset_index()

    agg['price_variance_pct'] = ((agg['avg_purchase_price'] - agg['standard_cost']) / agg['standard_cost'] * 100).round(2)
    agg['avg_purchase_price'] = agg['avg_purchase_price'].round(2)

    anomalies = agg[abs(agg['price_variance_pct']) >= 6.0].sort_values('price_variance_pct', ascending=False)
    return anomalies.head(50).to_dict(orient='records')

@router.get("/insights")
def get_insights():
    df = load_df('vendor_analytics_summary.csv')
    if df.empty:
        return []

    insights = []
    top_r = df.sort_values('total_revenue', ascending=False).iloc[0]
    insights.append({
        "type": "revenue",
        "severity": "positive",
        "title": "Top Revenue Driver",
        "message": f"<b>{top_r['vendor_name']}</b> generated <b>${top_r['total_revenue']:,.2f}</b> in attributed sales with a gross margin of {top_r['gross_margin_pct']}%."
    })

    est = df[df['performance_tier'] != 'New / Insufficient Data']
    if not est.empty:
        ineff = est.sort_values('purchase_to_sales_ratio', ascending=False).iloc[0]
        insights.append({
            "type": "efficiency",
            "severity": "warning",
            "title": "Procurement Asymmetry Alert",
            "message": f"<b>{ineff['vendor_name']}</b> accounts for ${ineff['total_procurement_cost']:,.2f} in spend with a high purchase-to-sales ratio of <b>{ineff['purchase_to_sales_ratio']}</b>."
        })

        high_p = est.sort_values('price_variance_pct', ascending=False).iloc[0]
        insights.append({
            "type": "pricing",
            "severity": "danger",
            "title": "Pricing Premium Anomaly",
            "message": f"<b>{high_p['vendor_name']}</b> unit purchase price is <b>+{high_p['price_variance_pct']}% above standard cost benchmark</b>. Candidate for renegotiation."
        })

    high_conc = df[df['concentration_pct'] > 30].sort_values('concentration_pct', ascending=False)
    if not high_conc.empty:
        hc = high_conc.iloc[0]
        insights.append({
            "type": "concentration",
            "severity": "warning",
            "title": "Sourcing Concentration Risk",
            "message": f"<b>{hc['vendor_name']}</b> holds <b>{hc['concentration_pct']}%</b> of category procurement in {hc['vendor_category']}. High single-source dependency."
        })

    return insights
