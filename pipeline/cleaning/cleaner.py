"""
Pipeline Data Cleaner
Standardizes schemas, trims casing, parses mixed dates, removes duplicates and anomalies,
and outputs normalized star schema dimension and fact tables.
"""

import os
import re
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def clean_text(s):
    if pd.isna(s):
        return ""
    return str(s).strip()

def parse_dates_robustly(series):
    parsed = pd.to_datetime(series, format='mixed', errors='coerce')
    return parsed.dt.strftime('%Y-%m-%d')

def clean_all(raw_data, output_dir=PROCESSED_DIR):
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "="*50)
    print(" PANDAS ETL CLEANING & NORMALIZATION PIPELINE")
    print("="*50)

    # 1. DimCategory
    df_cat = raw_data['categories'].copy()
    df_cat['category_id'] = df_cat['category_id'].str.strip()
    df_cat['category_name'] = df_cat['category_name'].str.strip()

    # 2. DimDate
    df_date = raw_data['calendar'].copy()
    df_date['date'] = parse_dates_robustly(df_date['date'])

    # 3. DimVendor
    print("[1/5] Cleaning DimVendor...")
    df_v = raw_data['vendors'].copy()
    init_v = len(df_v)
    df_v['vendor_id'] = df_v['vendor_id'].astype(str).str.strip()
    df_v['vendor_code'] = df_v['vendor_code'].astype(str).str.strip()
    df_v['vendor_name'] = df_v['vendor_name'].astype(str).str.strip().str.title()
    df_v['vendor_category'] = df_v['vendor_category'].astype(str).str.strip()
    df_v['contact_person'] = df_v['contact_person'].astype(str).str.strip()
    df_v['email'] = df_v['email'].fillna('procurement@' + df_v['vendor_code'].str.lower() + '.com').str.strip()
    df_v['phone'] = df_v['phone'].replace('', np.nan).fillna('+1-555-0100').str.strip()
    df_v['rating'] = pd.to_numeric(df_v['rating'], errors='coerce').clip(1.0, 5.0).fillna(4.0).round(2)
    df_v['contract_start_date'] = parse_dates_robustly(df_v['contract_start_date'])
    df_v['status'] = df_v['status'].fillna('Active')
    df_v = df_v.drop_duplicates(subset=['vendor_id'], keep='first')
    df_v = df_v.drop_duplicates(subset=['vendor_code'], keep='first')
    print(f"    DimVendor: {init_v} raw -> {len(df_v)} unique cleaned vendors")

    # 4. DimProduct
    print("[2/5] Cleaning DimProduct...")
    df_p = raw_data['products'].copy()
    df_p['product_id'] = df_p['product_id'].astype(str).str.strip()
    df_p['product_code'] = df_p['product_code'].astype(str).str.strip()
    df_p['product_name'] = df_p['product_name'].astype(str).str.strip()
    df_p['category_id'] = df_p['category_id'].astype(str).str.strip()
    df_p['standard_cost'] = pd.to_numeric(df_p['standard_cost'], errors='coerce')
    df_p['selling_price'] = pd.to_numeric(df_p['selling_price'], errors='coerce')
    df_p = df_p[(df_p['standard_cost'] > 0) & (df_p['selling_price'] > 0)]
    df_p = df_p.drop_duplicates(subset=['product_id'], keep='first')

    # 5. FactPurchases
    print("[3/5] Cleaning FactPurchases...")
    df_pu = raw_data['purchases'].copy()
    init_pu = len(df_pu)
    df_pu = df_pu.drop_duplicates(subset=['purchase_id'], keep='first')
    df_pu['vendor_id'] = df_pu['vendor_id'].astype(str).str.strip()
    df_pu['product_id'] = df_pu['product_id'].astype(str).str.strip()
    df_pu['purchase_date'] = parse_dates_robustly(df_pu['purchase_date'])
    df_pu['quantity'] = pd.to_numeric(df_pu['quantity'], errors='coerce')
    df_pu['unit_purchase_price'] = pd.to_numeric(df_pu['unit_purchase_price'], errors='coerce')
    
    df_pu = df_pu[(df_pu['quantity'] > 0) & (df_pu['unit_purchase_price'] > 0)]
    df_pu['quantity'] = df_pu['quantity'].astype(int)

    cost_map = dict(zip(df_p['product_id'], df_p['standard_cost']))
    df_pu['benchmark'] = df_pu['product_id'].map(cost_map)
    df_pu = df_pu.dropna(subset=['benchmark'])
    valid_mask = (df_pu['unit_purchase_price'] >= df_pu['benchmark'] * 0.25) & (df_pu['unit_purchase_price'] <= df_pu['benchmark'] * 3.0)
    df_pu = df_pu[valid_mask].copy()
    df_pu = df_pu.drop(columns=['benchmark'])
    
    df_pu['unit_purchase_price'] = df_pu['unit_purchase_price'].round(2)
    df_pu['total_purchase_value'] = (df_pu['quantity'] * df_pu['unit_purchase_price']).round(2)
    
    valid_v = set(df_v['vendor_id'])
    valid_p = set(df_p['product_id'])
    df_pu = df_pu[df_pu['vendor_id'].isin(valid_v) & df_pu['product_id'].isin(valid_p)]
    print(f"    FactPurchases: {init_pu} raw -> {len(df_pu)} valid orders (removed {init_pu - len(df_pu)} anomalies)")

    # 6. FactSales
    print("[4/5] Cleaning FactSales...")
    df_s = raw_data['sales'].copy()
    init_s = len(df_s)
    df_s = df_s.drop_duplicates(subset=['sale_id'], keep='first')
    df_s['product_id'] = df_s['product_id'].astype(str).str.strip()
    df_s['sale_date'] = parse_dates_robustly(df_s['sale_date'])
    df_s['quantity'] = pd.to_numeric(df_s['quantity'], errors='coerce')
    df_s['unit_selling_price'] = pd.to_numeric(df_s['unit_selling_price'], errors='coerce')
    df_s = df_s[(df_s['quantity'] > 0) & (df_s['unit_selling_price'] > 0)]
    df_s['quantity'] = df_s['quantity'].astype(int)
    df_s['unit_selling_price'] = df_s['unit_selling_price'].round(2)
    df_s['total_sales_value'] = (df_s['quantity'] * df_s['unit_selling_price']).round(2)
    df_s = df_s[df_s['product_id'].isin(valid_p)]
    print(f"    FactSales: {init_s} raw -> {len(df_s)} valid sales (removed {init_s - len(df_s)} anomalies)")

    # 7. FactInventory
    print("[5/5] Cleaning FactInventory...")
    df_inv = raw_data['inventory'].copy()
    df_inv['product_id'] = df_inv['product_id'].astype(str).str.strip()
    df_inv['vendor_id'] = df_inv['vendor_id'].astype(str).str.strip()
    df_inv['stock_quantity'] = pd.to_numeric(df_inv['stock_quantity'], errors='coerce').fillna(0).astype(int).clip(lower=0)
    df_inv['reorder_level'] = pd.to_numeric(df_inv['reorder_level'], errors='coerce').fillna(100).astype(int)
    df_inv['safety_stock'] = (df_inv['reorder_level'] * 0.6).astype(int)
    df_inv = df_inv.drop_duplicates(subset=['product_id', 'vendor_id'], keep='first')
    df_inv = df_inv[df_inv['product_id'].isin(valid_p) & df_inv['vendor_id'].isin(valid_v)]

    cleaned = {
        "DimCategory": df_cat,
        "DimDate": df_date,
        "DimVendor": df_v,
        "DimProduct": df_p,
        "FactPurchases": df_pu,
        "FactSales": df_s,
        "FactInventory": df_inv
    }

    for name, df in cleaned.items():
        csv_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"[+] Saved clean table: {name}.csv ({len(df)} rows)")

    return cleaned
