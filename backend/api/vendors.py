"""
Vendors API Router
Handles manual vendor entry with duplicate detection, listing with filters/search/pagination,
editing, and soft deactivation.
"""

import os
import re
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from backend.models.schemas import VendorCreate, VendorUpdate, VendorStatusUpdate

router = APIRouter(prefix="/vendors", tags=["Vendors"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def load_vendors_df():
    path = os.path.join(PROCESSED_DIR, "DimVendor.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_vendors_df(df):
    path = os.path.join(PROCESSED_DIR, "DimVendor.csv")
    df.to_csv(path, index=False)
    try:
        from pipeline.database.db import get_db
        db = get_db()
        df.to_sql("DimVendor", db.engine, if_exists="replace", index=False)
    except Exception as e:
        pass

def load_summary_df():
    path = os.path.join(PROCESSED_DIR, "vendor_analytics_summary.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@router.get("")
def list_vendors(
    q: str = None,
    category: str = None,
    location: str = None,
    status: str = None,
    tier: str = None,
    sort_by: str = "vendor_code",
    ascending: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100)
):
    df = load_summary_df()
    if df.empty:
        df = load_vendors_df()

    if df.empty:
        return {"total": 0, "page": page, "limit": limit, "items": []}

    if q:
        q_lower = q.lower().strip()
        df = df[
            df['vendor_name'].astype(str).str.lower().str.contains(q_lower) |
            df['vendor_code'].astype(str).str.lower().str.contains(q_lower) |
            df['vendor_category'].astype(str).str.lower().str.contains(q_lower) |
            df['email'].astype(str).str.lower().str.contains(q_lower)
        ]

    if category and category != "all":
        df = df[df['vendor_category'] == category]

    if location and location != "all":
        if 'country' in df.columns:
            df = df[df['country'] == location]
        elif 'location' in df.columns:
            df = df[df['location'] == location]

    if status and status != "all":
        df = df[df['status'] == status]

    if tier and tier != "all":
        if 'performance_tier' in df.columns:
            df = df[df['performance_tier'].astype(str).str.contains(tier, case=False, na=False)]

    total_records = len(df)

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_items = df.iloc[start_idx:end_idx].to_dict(orient="records")

    return {
        "total": total_records,
        "page": page,
        "limit": limit,
        "total_pages": (total_records + limit - 1) // limit,
        "items": page_items
    }

@router.post("", status_code=201)
def create_vendor(vendor: VendorCreate):
    df = load_vendors_df()
    
    # 1. Check vendor_code
    code_match = df[df['vendor_code'].astype(str).str.upper() == vendor.vendor_code.strip().upper()]
    if not code_match.empty:
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate vendor code: Vendor '{vendor.vendor_code}' already exists ({code_match.iloc[0]['vendor_name']})."
        )

    # 2. Check normalized vendor name
    norm_name = re.sub(r'[^a-zA-Z0-9]', '', vendor.vendor_name).lower()
    df_norm_names = df['vendor_name'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x).lower())
    if (df_norm_names == norm_name).any():
        matched_idx = df_norm_names[df_norm_names == norm_name].index[0]
        existing_vendor = df.iloc[matched_idx]
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate vendor name: A vendor matching '{vendor.vendor_name}' already exists with code '{existing_vendor['vendor_code']}'."
        )

    # 3. Check email
    email_match = df[df['email'].astype(str).str.lower() == vendor.email.strip().lower()]
    if not email_match.empty:
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate vendor email: An account with email '{vendor.email}' already exists ({email_match.iloc[0]['vendor_name']})."
        )

    new_num = len(df) + 1
    new_id = f"VND-{new_num:03d}"
    while (df['vendor_id'] == new_id).any():
        new_num += 1
        new_id = f"VND-{new_num:03d}"

    new_row = {
        "vendor_id": new_id,
        "vendor_code": vendor.vendor_code.strip().upper(),
        "vendor_name": vendor.vendor_name.strip().title(),
        "vendor_category": vendor.vendor_category.strip(),
        "contact_person": vendor.contact_person.strip().title(),
        "email": vendor.email.strip().lower(),
        "phone": vendor.phone.strip(),
        "address": vendor.address.strip(),
        "city": vendor.city.strip(),
        "state": vendor.state.strip(),
        "country": vendor.country.strip(),
        "rating": round(float(vendor.rating), 2),
        "contract_start_date": vendor.contract_start_date,
        "payment_terms": vendor.payment_terms,
        "status": "New / Insufficient Data"
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_vendors_df(df)

    summary_df = load_summary_df()
    if not summary_df.empty:
        new_sum_row = dict(new_row)
        new_sum_row.update({
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
        summary_df = pd.concat([summary_df, pd.DataFrame([new_sum_row])], ignore_index=True)
        summary_df.to_csv(os.path.join(PROCESSED_DIR, "vendor_analytics_summary.csv"), index=False)

    return {"message": "Vendor created successfully", "vendor": new_row}

@router.get("/{vendor_id}")
def get_vendor(vendor_id: str):
    df = load_summary_df()
    v = df[df['vendor_id'] == vendor_id]
    if v.empty:
        v = df[df['vendor_code'] == vendor_id]
    if v.empty:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    vendor_profile = v.iloc[0].to_dict()

    pu_path = os.path.join(PROCESSED_DIR, "FactPurchases.csv")
    prod_path = os.path.join(PROCESSED_DIR, "DimProduct.csv")
    products_supplied = []
    monthly_trend = []

    if os.path.exists(pu_path) and os.path.exists(prod_path):
        pu = pd.read_csv(pu_path)
        prods = pd.read_csv(prod_path)
        v_pu = pu[pu['vendor_id'] == vendor_profile['vendor_id']]
        if not v_pu.empty:
            p_grp = v_pu.groupby('product_id').agg(
                orders_count=('purchase_id', 'count'),
                units_purchased=('quantity', 'sum'),
                total_spend=('total_purchase_value', 'sum'),
                avg_price_paid=('unit_purchase_price', 'mean')
            ).reset_index()
            p_merged = pd.merge(p_grp, prods, on='product_id', how='left')
            p_merged['price_variance_pct'] = (
                (p_merged['avg_price_paid'] - p_merged['standard_cost']) / p_merged['standard_cost'] * 100
            ).round(2)
            p_merged['avg_price_paid'] = p_merged['avg_price_paid'].round(2)
            p_merged['total_spend'] = p_merged['total_spend'].round(2)
            products_supplied = p_merged.sort_values('total_spend', ascending=False).to_dict(orient='records')

            v_pu['month'] = pd.to_datetime(v_pu['purchase_date']).dt.strftime('%Y-%m')
            m_grp = v_pu.groupby('month').agg(spend=('total_purchase_value', 'sum')).reset_index().sort_values('month')
            monthly_trend = m_grp.to_dict(orient='records')

    return {
        "profile": vendor_profile,
        "monthly_trend": monthly_trend,
        "products": products_supplied
    }

@router.patch("/{vendor_id}/status")
def update_vendor_status(vendor_id: str, payload: VendorStatusUpdate):
    df = load_vendors_df()
    idx = df[df['vendor_id'] == vendor_id].index
    if idx.empty:
        idx = df[df['vendor_code'] == vendor_id].index
    if idx.empty:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    df.at[idx[0], 'status'] = payload.status
    save_vendors_df(df)

    summary_df = load_summary_df()
    s_idx = summary_df[summary_df['vendor_id'] == vendor_id].index
    if not s_idx.empty:
        summary_df.at[s_idx[0], 'status'] = payload.status
        summary_df.to_csv(os.path.join(PROCESSED_DIR, "vendor_analytics_summary.csv"), index=False)

    return {"message": f"Vendor status updated to {payload.status}", "vendor_id": vendor_id}
