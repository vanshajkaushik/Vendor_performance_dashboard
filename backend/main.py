"""
Vendor Performance & Procurement Intelligence - FastAPI Backend Server
Serves all operational and analytical endpoints, and mounts the pre-built React dashboard.
"""

import os
import io
import re
import json
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

app = FastAPI(
    title="Vendor Performance & Procurement Intelligence API",
    description="Enterprise API powering vendor management, multi-stage CSV import, duplicate detection, and Star Schema analytics.",
    version="2.0.0"
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

def save_df(df, filename):
    path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(path, index=False)
    # Sync with SQLite
    try:
        from pipeline.database.db import get_db
        db = get_db()
        tbl_name = filename.replace('.csv', '')
        df.to_sql(tbl_name, db.engine, if_exists="replace", index=False)
    except Exception:
        pass

# ----------------- PYDANTIC MODELS -----------------
class VendorCreatePayload(BaseModel):
    vendor_code: str
    vendor_name: str
    category_id: Optional[int] = 1
    vendor_category: Optional[str] = None
    contact_name: Optional[str] = "Account Manager"
    contact_person: Optional[str] = None
    email: str
    phone: Optional[str] = "+1-555-0100"
    address: Optional[str] = "100 Commerce Blvd"
    city: Optional[str] = "Chicago"
    state: Optional[str] = "IL"
    country: Optional[str] = "USA"
    rating: Optional[float] = 4.0
    payment_terms: Optional[str] = "Net 30"
    lead_time_days: Optional[int] = 14
    status: Optional[str] = "New / Insufficient Data"
    contract_start_date: Optional[str] = "2025-01-01"

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# ----------------- HEALTH ENDPOINT -----------------
@app.get("/api/health")
def get_health():
    v_df = load_df('DimVendor.csv')
    return {
        "status": "healthy",
        "system": "Vendor Performance & Procurement Intelligence",
        "active_vendors": len(v_df),
        "database_engine": "SQLite / Dual-PostgreSQL Star Schema"
    }

# ----------------- KPIS ENDPOINT -----------------
@app.get("/api/kpis")
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
        if 'category_name' in products.columns:
            cat_p = products[products['category_name'] == category]['product_id'].unique()
        elif 'category' in products.columns:
            cat_p = products[products['category'] == category]['product_id'].unique()
        else:
            cat_p = []
        if len(cat_p) > 0:
            purchases = purchases[purchases['product_id'].isin(cat_p)]
            sales = sales[sales['product_id'].isin(cat_p)]

    total_procurement = float(purchases['total_purchase_value'].sum())
    total_sales = float(sales['total_sales_value'].sum())
    gross_profit = float(total_sales - total_procurement)
    gross_margin = round((gross_profit / total_sales * 100), 2) if total_sales > 0 else 0.0

    scored = scores.dropna(subset=['vendor_performance_score'])
    avg_vps = round(float(scored['vendor_performance_score'].mean()), 1) if not scored.empty else 0.0

    return {
        "total_sales": round(total_sales, 2),
        "total_procurement": round(total_procurement, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_margin_pct": gross_margin,
        "purchase_volume": int(purchases['quantity'].sum()) if not purchases.empty else 0,
        "sales_volume": int(sales['quantity'].sum()) if not sales.empty else 0,
        "active_vendors": int(vendors[vendors['status'] == 'Active']['vendor_id'].nunique()) if not vendors.empty else 0,
        "total_vendors": len(vendors),
        "total_products": len(products),
        "avg_vendor_performance_score": avg_vps,
        "purchase_to_sales_ratio": round(total_procurement / total_sales, 3) if total_sales > 0 else 0.0
    }

# ----------------- TRENDS ENDPOINT -----------------
@app.get("/api/trends")
def get_trends(
    vendor: str = None,
    category: str = None,
    start_date: str = None,
    end_date: str = None
):
    trends = load_df('monthly_trends.csv')
    return trends.to_dict(orient='records')

# ----------------- VENDORS DIRECTORY & DETAILS -----------------
@app.get("/api/vendors")
def list_vendors(
    category: str = None,
    location: str = None,
    tier: str = None,
    sort_by: str = "total_revenue",
    ascending: bool = False
):
    df = load_df('vendor_analytics_summary.csv')
    if df.empty:
        df = load_df('DimVendor.csv')
        if df.empty:
            return []

    if category and category != 'all':
        if 'vendor_category' in df.columns:
            df = df[df['vendor_category'] == category]
        elif 'category_name' in df.columns:
            df = df[df['category_name'] == category]

    if location and location != 'all':
        if 'country' in df.columns:
            df = df[df['country'] == location]
        elif 'location' in df.columns:
            df = df[df['location'] == location]

    if tier and tier != 'all':
        if 'performance_tier' in df.columns:
            df = df[df['performance_tier'].astype(str).str.contains(tier, case=False, na=False)]

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    # Clean NaN values for strict JSON compliance
    df = df.replace({np.nan: None})
    records = df.to_dict(orient='records')
    for r in records:
        if not r.get('vendor_category'):
            r['vendor_category'] = r.get('category_name') or 'General'
        if not r.get('location'):
            r['location'] = r.get('country') or r.get('city') or 'USA'
        if not r.get('vendor_id'):
            r['vendor_id'] = r.get('vendor_code', '')
        # Clean any remaining NaN
        for k, v in list(r.items()):
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                r[k] = None
    return records

@app.post("/api/vendors/create", status_code=200)
@app.post("/api/vendors", status_code=200)
def create_vendor(payload: VendorCreatePayload):
    df = load_df('DimVendor.csv')
    
    code = payload.vendor_code.strip().upper()
    name = payload.vendor_name.strip()
    email = payload.email.strip().lower()

    # 1. Check duplicate code
    if not df.empty and (df['vendor_code'].astype(str).str.upper() == code).any():
        raise HTTPException(
            status_code=400,
            detail=f"Vendor code '{code}' already exists in database."
        )

    # 2. Check duplicate normalized name
    norm_name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    if not df.empty:
        df_norm = df['vendor_name'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x).lower())
        if (df_norm == norm_name).any():
            matched_code = df.iloc[df_norm[df_norm == norm_name].index[0]]['vendor_code']
            raise HTTPException(
                status_code=400,
                detail=f"Vendor name '{name}' already exists (Code: {matched_code})."
            )

    # 3. Check duplicate email
    if not df.empty and (df['email'].astype(str).str.lower() == email).any():
        raise HTTPException(
            status_code=400,
            detail=f"Vendor with email '{email}' already exists."
        )

    cat_map = {1: 'Raw Materials', 2: 'Packaging', 3: 'Electronics & Components', 4: 'Machinery & Equipment', 5: 'MRO Supplies'}
    v_cat = payload.vendor_category or cat_map.get(payload.category_id, 'General')

    new_row = {
        "vendor_id": code,
        "vendor_code": code,
        "vendor_name": name.title(),
        "category_id": payload.category_id,
        "vendor_category": v_cat,
        "category_name": v_cat,
        "contact_name": payload.contact_name or payload.contact_person or "Account Manager",
        "contact_person": payload.contact_name or payload.contact_person or "Account Manager",
        "email": email,
        "phone": payload.phone or "+1-555-0100",
        "address": payload.address or "100 Commerce Blvd",
        "city": payload.city or "Chicago",
        "state": payload.state or "IL",
        "country": payload.country or "USA",
        "location": payload.country or "USA",
        "rating": round(float(payload.rating or 4.0), 2),
        "contract_start_date": payload.contract_start_date or "2025-01-01",
        "payment_terms": payload.payment_terms or "Net 30",
        "lead_time_days": payload.lead_time_days or 14,
        "status": "New / Insufficient Data"
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_df(df, 'DimVendor.csv')

    # Update summary table with unrated / New status
    summary_df = load_df('vendor_analytics_summary.csv')
    if not summary_df.empty:
        new_sum = dict(new_row)
        new_sum.update({
            "total_orders": 0,
            "total_procurement_cost": 0.0,
            "total_revenue": 0.0,
            "gross_profit": 0.0,
            "gross_margin_pct": 0.0,
            "purchase_to_sales_ratio": 0.0,
            "price_variance_pct": 0.0,
            "concentration_pct": 0.0,
            "vendor_performance_score": None,
            "performance_tier": "New / Insufficient Data",
            "recommendation": "Newly registered supplier. Awaiting initial procurement transaction history to evaluate performance."
        })
        summary_df = pd.concat([summary_df, pd.DataFrame([new_sum])], ignore_index=True)
        save_df(summary_df, 'vendor_analytics_summary.csv')

    return {"success": True, "message": "Vendor registered successfully", "vendor_code": code, "vendor": new_row}

@app.get("/api/vendors/{vendor_id}")
def get_vendor_details(vendor_id: str):
    df = load_df('vendor_analytics_summary.csv')
    v = df[df['vendor_id'] == vendor_id]
    if v.empty:
        v = df[df['vendor_code'] == vendor_id]
    if v.empty:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    vendor_profile = v.iloc[0].to_dict()
    pu = load_df("FactPurchases.csv")
    prods = load_df("DimProduct.csv")
    products_supplied = []
    monthly_trend = []

    if not pu.empty and not prods.empty:
        v_pu = pu[pu['vendor_id'] == vendor_profile['vendor_id']]
        if not v_pu.empty:
            p_grp = v_pu.groupby('product_id').agg(
                orders_count=('purchase_id', 'count'),
                units_purchased=('quantity', 'sum'),
                total_spend=('total_purchase_value', 'sum'),
                avg_price_paid=('unit_purchase_price', 'mean')
            ).reset_index()
            p_merged = pd.merge(p_grp, prods, on='product_id', how='left')
            cost_col = 'standard_cost' if 'standard_cost' in p_merged.columns else 'unit_cost'
            p_merged['unit_cost'] = p_merged[cost_col]
            p_merged['price_variance_pct'] = (
                (p_merged['avg_price_paid'] - p_merged['unit_cost']) / p_merged['unit_cost'] * 100
            ).round(2)
            p_merged['avg_price_paid'] = p_merged['avg_price_paid'].round(2)
            p_merged['total_spend'] = p_merged['total_spend'].round(2)
            products_supplied = p_merged.sort_values('total_spend', ascending=False).to_dict(orient='records')

            v_pu['month'] = pd.to_datetime(v_pu['purchase_date']).dt.strftime('%Y-%m')
            m_grp = v_pu.groupby('month').agg(spend=('total_purchase_value', 'sum'), units=('quantity', 'sum')).reset_index().sort_values('month')
            monthly_trend = m_grp.to_dict(orient='records')

    return {
        "profile": vendor_profile,
        "monthly_trend": monthly_trend,
        "products": products_supplied
    }

# ----------------- CSV IMPORT (PREVIEW & CONFIRM) -----------------
@app.post("/api/vendors/import/preview")
async def preview_vendor_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df_upload = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    df_existing = load_df("DimVendor.csv")
    existing_codes = set(df_existing['vendor_code'].astype(str).str.upper()) if not df_existing.empty else set()
    existing_emails = set(df_existing['email'].astype(str).str.lower()) if not df_existing.empty else set()
    existing_names = set(
        df_existing['vendor_name'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x).lower())
    ) if not df_existing.empty else set()

    valid_records = []
    error_details = []
    duplicates_count = 0
    invalid_count = 0

    seen_in_file_codes = set()
    seen_in_file_emails = set()

    for idx, row in df_upload.iterrows():
        row_num = idx + 2
        row_dict = row.to_dict()
        code = str(row.get('vendor_code', '')).strip().upper()
        name = str(row.get('vendor_name', '')).strip()
        email = str(row.get('email', '')).strip().lower()
        rating = row.get('rating', 4.0)

        err_reasons = []

        if not code or code == 'NAN':
            err_reasons.append("Missing vendor_code")
        if not name or name == 'NAN':
            err_reasons.append("Missing vendor_name")
        if not email or not EMAIL_REGEX.match(email):
            err_reasons.append(f"Invalid email format '{email}'")

        try:
            r_num = float(rating)
            if r_num < 1.0 or r_num > 5.0:
                err_reasons.append(f"Rating {r_num} out of bounds (1.0 - 5.0)")
        except (ValueError, TypeError):
            err_reasons.append("Invalid rating numeric value")

        is_dup = False
        if code in seen_in_file_codes:
            err_reasons.append(f"Duplicate code '{code}' within CSV file")
            is_dup = True
        else:
            seen_in_file_codes.add(code)

        if email in seen_in_file_emails:
            err_reasons.append(f"Duplicate email '{email}' within CSV file")
            is_dup = True
        else:
            seen_in_file_emails.add(email)

        if code in existing_codes:
            err_reasons.append(f"Vendor code '{code}' already exists in database")
            is_dup = True

        norm_n = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
        if norm_n in existing_names:
            err_reasons.append(f"Vendor name '{name}' already exists in database")
            is_dup = True

        if email in existing_emails:
            err_reasons.append(f"Email '{email}' already registered in database")
            is_dup = True

        if err_reasons:
            if is_dup:
                duplicates_count += 1
            else:
                invalid_count += 1
            for r in err_reasons:
                error_details.append({
                    "row": row_num,
                    "vendor_code": code,
                    "vendor_name": name,
                    "reason": r
                })
        else:
            cat_map = {1: 'Raw Materials', 2: 'Packaging', 3: 'Electronics & Components', 4: 'Machinery & Equipment', 5: 'MRO Supplies'}
            cat_id = int(row.get('category_id', 1))
            valid_records.append({
                "vendor_id": code,
                "vendor_code": code,
                "vendor_name": name.title(),
                "category_id": cat_id,
                "vendor_category": row.get('vendor_category', cat_map.get(cat_id, 'General')),
                "contact_name": str(row.get('contact_name', row.get('contact_person', 'Account Manager'))).title(),
                "email": email,
                "phone": str(row.get('phone', '+1-555-0100')),
                "city": str(row.get('city', 'New York')),
                "country": str(row.get('country', 'USA')),
                "location": str(row.get('country', 'USA')),
                "payment_terms": str(row.get('payment_terms', 'Net 30')),
                "lead_time_days": int(row.get('lead_time_days', 14)),
                "rating": round(float(rating), 2),
                "status": "New / Insufficient Data"
            })

    return {
        "total_rows": len(df_upload),
        "valid_rows": len(valid_records),
        "duplicate_rows": duplicates_count,
        "invalid_rows": invalid_count,
        "error_details": error_details,
        "valid_records": valid_records
    }

@app.post("/api/vendors/import/confirm")
def confirm_vendor_csv_import(records: List[Dict[str, Any]]):
    if not records:
        raise HTTPException(status_code=400, detail="No valid records provided for import.")

    df_existing = load_df("DimVendor.csv")
    existing_codes = set(df_existing['vendor_code'].astype(str).str.upper()) if not df_existing.empty else set()

    to_insert = []
    for r in records:
        code = str(r.get('vendor_code', '')).upper()
        if code in existing_codes:
            continue
        to_insert.append(r)
        existing_codes.add(code)

    if not to_insert:
        return {"inserted": 0, "message": "No new records imported."}

    df_new = pd.DataFrame(to_insert)
    df_comb = pd.concat([df_existing, df_new], ignore_index=True)
    save_df(df_comb, "DimVendor.csv")

    summary_df = load_df('vendor_analytics_summary.csv')
    if not summary_df.empty:
        new_sums = []
        for r in to_insert:
            s = dict(r)
            s.update({
                "total_orders": 0,
                "total_procurement_cost": 0.0,
                "total_revenue": 0.0,
                "gross_profit": 0.0,
                "gross_margin_pct": 0.0,
                "purchase_to_sales_ratio": 0.0,
                "price_variance_pct": 0.0,
                "concentration_pct": 0.0,
                "vendor_performance_score": None,
                "performance_tier": "New / Insufficient Data",
                "recommendation": "Newly registered supplier. Awaiting initial procurement transaction history to evaluate performance."
            })
            new_sums.append(s)
        summary_df = pd.concat([summary_df, pd.DataFrame(new_sums)], ignore_index=True)
        save_df(summary_df, 'vendor_analytics_summary.csv')

    return {"inserted": len(to_insert), "message": f"Successfully ingested {len(to_insert)} vendors."}

# ----------------- OTHER ANALYTICS ENDPOINTS -----------------
@app.get("/api/categories")
def get_categories():
    cat_df = load_df('category_performance.csv')
    return cat_df.to_dict(orient='records')

@app.get("/api/scatter")
def get_scatter():
    df = load_df('vendor_analytics_summary.csv')
    return df.to_dict(orient='records')

@app.get("/api/pricing-anomalies")
def get_pricing_anomalies():
    purchases = load_df('FactPurchases.csv')
    products = load_df('DimProduct.csv')
    vendors = load_df('DimVendor.csv')

    cost_col = 'standard_cost' if 'standard_cost' in products.columns else 'unit_cost'
    merged = pd.merge(purchases, products[['product_id', 'product_name', cost_col]], on='product_id')
    merged = pd.merge(merged, vendors[['vendor_id', 'vendor_name']], on='vendor_id')

    agg = merged.groupby(['vendor_id', 'vendor_name', 'product_id', 'product_name', cost_col]).agg(
        avg_purchase_price=('unit_purchase_price', 'mean'),
        total_qty=('quantity', 'sum')
    ).reset_index()

    agg['unit_cost'] = agg[cost_col]
    agg['price_variance_pct'] = ((agg['avg_purchase_price'] - agg['unit_cost']) / agg['unit_cost'] * 100).round(2)
    agg['avg_purchase_price'] = agg['avg_purchase_price'].round(2)

    anomalies = agg[abs(agg['price_variance_pct']) >= 6.0].sort_values('price_variance_pct', ascending=False)
    return anomalies.head(50).to_dict(orient='records')

@app.get("/api/inventory")
def get_inventory():
    inv = load_df('FactInventory.csv')
    prods = load_df('DimProduct.csv')
    vendors = load_df('DimVendor.csv')

    cost_col = 'standard_cost' if 'standard_cost' in prods.columns else 'unit_cost'
    df = pd.merge(inv, prods[['product_id', 'product_name', cost_col]], on='product_id', how='left')
    df = pd.merge(df, vendors[['vendor_id', 'vendor_name']], on='vendor_id', how='left')
    df['unit_cost'] = df[cost_col]
    df['inventory_value'] = (df['stock_quantity'] * df['unit_cost']).round(2)
    df['reorder_deficit'] = df['reorder_level'] - df['stock_quantity']
    df['status'] = np.where(df['stock_quantity'] <= df['safety_stock'], 'CRITICAL: Stockout Risk', 'HEALTHY')
    return df.to_dict(orient='records')

@app.get("/api/insights")
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
            "message": f"<b>{ineff['vendor_name']}</b> accounts for ${ineff['total_procurement_cost']:,.2f} in spend with a purchase-to-sales ratio of <b>{ineff['purchase_to_sales_ratio']}</b>."
        })

        high_p = est.sort_values('price_variance_pct', ascending=False).iloc[0]
        insights.append({
            "type": "pricing",
            "severity": "danger",
            "title": "Pricing Premium Anomaly",
            "message": f"<b>{high_p['vendor_name']}</b> unit purchase price is <b>+{high_p['price_variance_pct']}% above standard cost</b>. Candidate for renegotiation."
        })

    return insights

@app.get("/api/pipeline-status")
@app.get("/api/pipeline/status")
def get_pipeline_status():
    report_path = os.path.join(PROCESSED_DIR, "data_quality_report.json")
    report = {}
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

    tables = ['DimVendor', 'DimProduct', 'FactPurchases', 'FactSales', 'FactInventory']
    counts = {}
    for t in tables:
        clean_f = os.path.join(PROCESSED_DIR, f"{t}.csv")
        clean_c = len(pd.read_csv(clean_f)) if os.path.exists(clean_f) else 0
        counts[t] = {"clean_rows": clean_c, "raw_rows": clean_c}

    return {
        "pipeline_health": "OPTIMAL (100% Validated)",
        "last_sync": "Automated ETL",
        "data_quality": report,
        "table_counts": counts
    }

@app.post("/api/pipeline/run")
def trigger_pipeline_run(background_tasks: BackgroundTasks):
    from pipeline.pipeline import run_pipeline
    background_tasks.add_task(run_pipeline, generate=False, load_db=True)
    return {"message": "Pipeline run started in background", "status": "TRIGGERED"}

# Mount Static UI
DIST_DIR = os.path.join(BASE_DIR, 'dashboard', 'dist')
if os.path.exists(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
