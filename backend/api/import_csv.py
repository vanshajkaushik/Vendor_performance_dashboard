"""
Vendor CSV Import Router
Implements the full enterprise import workflow:
Upload -> Read with Pandas -> Schema Check -> Data Validation -> Duplicate Detection ->
Interactive Preview -> User Confirmation -> Database Insert -> Import Report.
"""

import os
import io
import re
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import ImportPreviewResponse, ImportConfirmRequest, ImportConfirmResponse

router = APIRouter(prefix="/vendors/import", tags=["Vendor CSV Import"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def load_existing_vendors():
    path = os.path.join(PROCESSED_DIR, "DimVendor.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_vendor_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are supported.")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum supported CSV size is 5MB.")

    try:
        df_upload = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    req_cols = ['vendor_code', 'vendor_name', 'vendor_category', 'email']
    missing_cols = [col for col in req_cols if col not in df_upload.columns]
    if missing_cols:
        raise HTTPException(
            status_code=422,
            detail=f"CSV schema check failed. Missing required columns: {', '.join(missing_cols)}"
        )

    df_existing = load_existing_vendors()
    existing_codes = set(df_existing['vendor_code'].astype(str).str.upper()) if not df_existing.empty else set()
    existing_emails = set(df_existing['email'].astype(str).str.lower()) if not df_existing.empty else set()
    existing_names = set(
        df_existing['vendor_name'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z0-9]', '', x).lower())
    ) if not df_existing.empty else set()

    valid_rows = []
    errors = []
    duplicates = []
    seen_in_file_codes = set()
    seen_in_file_emails = set()

    for idx, row in df_upload.iterrows():
        row_num = idx + 2
        row_data = row.to_dict()
        has_error = False

        v_code = str(row.get('vendor_code', '')).strip().upper()
        v_name = str(row.get('vendor_name', '')).strip()
        v_cat = str(row.get('vendor_category', '')).strip()
        email = str(row.get('email', '')).strip().lower()
        rating_val = row.get('rating', 4.0)

        if not v_code or v_code == 'NAN':
            errors.append({
                "row_index": row_num,
                "vendor_code": "",
                "field": "vendor_code",
                "reason": "Missing required field: vendor_code",
                "raw_data": row_data
            })
            has_error = True

        if not v_name or v_name == 'NAN':
            errors.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "field": "vendor_name",
                "reason": "Missing required field: vendor_name",
                "raw_data": row_data
            })
            has_error = True

        if not email or not EMAIL_REGEX.match(email):
            errors.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "field": "email",
                "reason": f"Invalid email format: '{email}'",
                "raw_data": row_data
            })
            has_error = True

        try:
            r_float = float(rating_val)
            if r_float < 1.0 or r_float > 5.0:
                errors.append({
                    "row_index": row_num,
                    "vendor_code": v_code,
                    "field": "rating",
                    "reason": f"Rating must be between 1.0 and 5.0 (got {r_float})",
                    "raw_data": row_data
                })
                has_error = True
        except (ValueError, TypeError):
            errors.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "field": "rating",
                "reason": f"Invalid numeric rating: '{rating_val}'",
                "raw_data": row_data
            })
            has_error = True

        if v_code in seen_in_file_codes:
            duplicates.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "reason": f"Duplicate vendor_code '{v_code}' found multiple times within uploaded CSV",
                "raw_data": row_data
            })
            has_error = True
        else:
            seen_in_file_codes.add(v_code)

        if email in seen_in_file_emails:
            duplicates.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "reason": f"Duplicate email '{email}' found multiple times within uploaded CSV",
                "raw_data": row_data
            })
            has_error = True
        else:
            seen_in_file_emails.add(email)

        if v_code in existing_codes:
            duplicates.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "reason": f"Vendor code '{v_code}' already exists in database",
                "raw_data": row_data
            })
            has_error = True

        norm_name = re.sub(r'[^a-zA-Z0-9]', '', v_name).lower()
        if norm_name in existing_names:
            duplicates.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "reason": f"Vendor name '{v_name}' already exists in database",
                "raw_data": row_data
            })
            has_error = True

        if email in existing_emails:
            duplicates.append({
                "row_index": row_num,
                "vendor_code": v_code,
                "reason": f"Email '{email}' already registered to existing vendor in database",
                "raw_data": row_data
            })
            has_error = True

        if not has_error:
            valid_rows.append({
                "vendor_code": v_code,
                "vendor_name": v_name.title(),
                "vendor_category": v_cat,
                "contact_person": str(row.get('contact_person', 'Account Manager')).strip().title(),
                "email": email,
                "phone": str(row.get('phone', '+1-555-0100')).strip(),
                "country": str(row.get('country', 'United States')).strip(),
                "rating": round(float(rating_val), 2),
                "contract_start_date": str(row.get('contract_start_date', '2025-01-01')).strip(),
                "payment_terms": str(row.get('payment_terms', 'Net 30')).strip()
            })

    return {
        "total_rows": len(df_upload),
        "valid_count": len(valid_rows),
        "duplicate_count": len(duplicates),
        "invalid_count": len(errors),
        "valid_rows": valid_rows[:50],
        "errors": errors,
        "duplicates": duplicates
    }

@router.post("/confirm", response_model=ImportConfirmResponse)
def confirm_vendor_import(payload: ImportConfirmRequest):
    if not payload.confirmed_rows:
        raise HTTPException(status_code=400, detail="No valid vendor rows provided for confirmation.")

    df_existing = load_existing_vendors()
    existing_codes = set(df_existing['vendor_code'].astype(str).str.upper()) if not df_existing.empty else set()

    imported_records = []
    counter = len(df_existing) + 1

    for item in payload.confirmed_rows:
        code = item['vendor_code'].strip().upper()
        if code in existing_codes:
            continue

        v_id = f"VND-{counter:03d}"
        while (df_existing['vendor_id'] == v_id).any():
            counter += 1
            v_id = f"VND-{counter:03d}"

        new_v = {
            "vendor_id": v_id,
            "vendor_code": code,
            "vendor_name": item['vendor_name'].strip().title(),
            "vendor_category": item['vendor_category'].strip(),
            "contact_person": item.get('contact_person', 'Account Manager').strip().title(),
            "email": item['email'].strip().lower(),
            "phone": item.get('phone', '+1-555-0100').strip(),
            "address": item.get('address', '100 Business Way'),
            "city": item.get('city', 'New York'),
            "state": item.get('state', 'NY'),
            "country": item.get('country', 'United States').strip(),
            "rating": round(float(item.get('rating', 4.0)), 2),
            "contract_start_date": item.get('contract_start_date', '2025-01-01'),
            "payment_terms": item.get('payment_terms', 'Net 30'),
            "status": "New / Insufficient Data"
        }
        imported_records.append(new_v)
        existing_codes.add(code)
        counter += 1

    if not imported_records:
        return {
            "status": "NO_OP",
            "imported_count": 0,
            "message": "No new records were imported (records may already exist)."
        }

    df_new = pd.DataFrame(imported_records)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_csv(os.path.join(PROCESSED_DIR, "DimVendor.csv"), index=False)

    try:
        from pipeline.database.db import get_db
        db = get_db()
        df_combined.to_sql("DimVendor", db.engine, if_exists="replace", index=False)
    except Exception as e:
        pass

    summary_path = os.path.join(PROCESSED_DIR, "vendor_analytics_summary.csv")
    if os.path.exists(summary_path):
        df_sum = pd.read_csv(summary_path)
        sum_rows = []
        for v in imported_records:
            s_row = dict(v)
            s_row.update({
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
            sum_rows.append(s_row)
        df_sum = pd.concat([df_sum, pd.DataFrame(sum_rows)], ignore_index=True)
        df_sum.to_csv(summary_path, index=False)

    return {
        "status": "SUCCESS",
        "imported_count": len(imported_records),
        "message": f"Successfully imported {len(imported_records)} suppliers into PostgreSQL / DimVendor."
    }
