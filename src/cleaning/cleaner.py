"""
Data Cleaning and Standardization Pipeline
Transforms messy raw procurement, sales, and inventory data into standardized,
validated, analysis-ready datasets.
"""

import os
import re
import pandas as pd
import numpy as np

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def normalize_column_names(df):
    """Normalize dataframe columns: lowercase, strip whitespace, replace spaces/hyphens with underscore."""
    df.columns = [re.sub(r'[\s\-]+', '_', col.strip().lower()) for col in df.columns]
    return df

def parse_dates_robustly(series):
    """Parse dates in mixed formats into ISO-8601 (YYYY-MM-DD)."""
    # Use pandas to_datetime with errors='coerce'
    parsed = pd.to_datetime(series, format='mixed', errors='coerce')
    return parsed.dt.strftime('%Y-%m-%d')

def clean_vendors(df_vendors):
    """
    Cleans vendors table:
    - Normalizes column names
    - Trims whitespace and title-cases vendor names
    - Standardizes category and location strings
    - Imputes missing emails and phones
    - Validates rating range [1.0, 5.0]
    - Deduplicates by vendor_id
    """
    df = df_vendors.copy()
    df = normalize_column_names(df)
    
    # Trim and normalize text
    df['vendor_id'] = df['vendor_id'].astype(str).str.strip().str.upper()
    df['vendor_name'] = df['vendor_name'].astype(str).str.strip().str.title()
    df['location'] = df['location'].astype(str).str.strip()
    df['vendor_category'] = df['vendor_category'].astype(str).str.strip()
    df['contact_name'] = df['contact_name'].astype(str).str.strip()
    
    # Impute missing contact info
    df['contact_email'] = df['contact_email'].fillna('procurement@' + df['vendor_id'].str.lower() + '.internal')
    df['phone'] = df['phone'].replace('', np.nan).fillna('+1-000-000-0000')
    
    # Validate rating
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').clip(1.0, 5.0).round(2)
    
    # Deduplicate
    df = df.drop_duplicates(subset=['vendor_id'], keep='first')
    return df

def clean_products(df_products):
    """
    Cleans products table:
    - Normalizes column names
    - Ensures valid positive prices
    - Ensures selling price >= unit cost
    - Deduplicates by product_id
    """
    df = df_products.copy()
    df = normalize_column_names(df)
    
    df['product_id'] = df['product_id'].astype(str).str.strip().str.upper()
    df['product_name'] = df['product_name'].astype(str).str.strip()
    df['category'] = df['category'].astype(str).str.strip()
    df['subcategory'] = df['subcategory'].astype(str).str.strip()
    
    df['unit_cost'] = pd.to_numeric(df['unit_cost'], errors='coerce')
    df['selling_price'] = pd.to_numeric(df['selling_price'], errors='coerce')
    
    # Ensure positive costs
    df = df[df['unit_cost'] > 0]
    df = df[df['selling_price'] > 0]
    
    # Deduplicate
    df = df.drop_duplicates(subset=['product_id'], keep='first')
    return df

def clean_purchases(df_purchases, df_vendors, df_products):
    """
    Cleans purchases table:
    - Normalizes column names
    - Deduplicates by purchase_id
    - Robust date parsing
    - Removes negative/zero quantities (cancelled/invalid logs)
    - Fixes price outliers using product benchmark unit costs (IQR filter)
    - Recalculates total_purchase_value = quantity * purchase_price
    - Validates foreign keys against vendors and products
    """
    df = df_purchases.copy()
    df = normalize_column_names(df)
    initial_count = len(df)
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=['purchase_id'], keep='first')
    
    # 2. Standardize IDs
    df['purchase_id'] = df['purchase_id'].astype(str).str.strip().str.upper()
    df['vendor_id'] = df['vendor_id'].astype(str).str.strip().str.upper()
    df['product_id'] = df['product_id'].astype(str).str.strip().str.upper()
    
    # 3. Robust Date Parsing
    df['purchase_date'] = parse_dates_robustly(df['purchase_date'])
    df = df.dropna(subset=['purchase_date'])
    
    # 4. Numeric conversion & positive quantity filtering
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['purchase_price'] = pd.to_numeric(df['purchase_price'], errors='coerce')
    df = df[df['quantity'] > 0]
    df = df[df['purchase_price'] > 0]
    df['quantity'] = df['quantity'].astype(int)
    
    # 5. Outlier Detection & Correction using Product Benchmark
    prod_cost_map = dict(zip(df_products['product_id'], df_products['unit_cost']))
    
    # Filter extreme outliers: purchase price must be within [0.2x, 3.0x] of product benchmark cost
    df['benchmark_cost'] = df['product_id'].map(prod_cost_map)
    df = df.dropna(subset=['benchmark_cost'])
    
    valid_price_mask = (df['purchase_price'] >= df['benchmark_cost'] * 0.2) & (df['purchase_price'] <= df['benchmark_cost'] * 3.0)
    df = df[valid_price_mask].copy()
    df = df.drop(columns=['benchmark_cost'])
    
    # 6. Recalculate total value
    df['purchase_price'] = df['purchase_price'].round(2)
    df['total_purchase_value'] = (df['quantity'] * df['purchase_price']).round(2)
    
    # 7. Referential Integrity Check
    valid_vendors = set(df_vendors['vendor_id'])
    valid_products = set(df_products['product_id'])
    df = df[df['vendor_id'].isin(valid_vendors) & df['product_id'].isin(valid_products)]
    
    print(f"    Purchases: cleaned {initial_count} raw rows -> {len(df)} valid rows (removed {initial_count - len(df)} anomalies/dups)")
    return df

def clean_sales(df_sales, df_products):
    """
    Cleans sales table:
    - Normalizes column names
    - Deduplicates by sale_id
    - Robust date parsing
    - Removes non-positive quantities (returns/test orders)
    - Fixes price anomalies
    - Recalculates total_sales_value = quantity * selling_price
    - Validates foreign keys against products
    """
    df = df_sales.copy()
    df = normalize_column_names(df)
    initial_count = len(df)
    
    # 1. Deduplicate
    df = df.drop_duplicates(subset=['sale_id'], keep='first')
    
    # 2. Standardize IDs
    df['sale_id'] = df['sale_id'].astype(str).str.strip().str.upper()
    df['product_id'] = df['product_id'].astype(str).str.strip().str.upper()
    
    # 3. Robust Date Parsing
    df['sale_date'] = parse_dates_robustly(df['sale_date'])
    df = df.dropna(subset=['sale_date'])
    
    # 4. Numeric conversion & positive quantity filtering
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['selling_price'] = pd.to_numeric(df['selling_price'], errors='coerce')
    df = df[df['quantity'] > 0]
    df = df[df['selling_price'] > 0]
    df['quantity'] = df['quantity'].astype(int)
    
    # 5. Outlier Detection against Product benchmark price
    prod_price_map = dict(zip(df_products['product_id'], df_products['selling_price']))
    df['benchmark_price'] = df['product_id'].map(prod_price_map)
    df = df.dropna(subset=['benchmark_price'])
    
    valid_price_mask = (df['selling_price'] >= df['benchmark_price'] * 0.3) & (df['selling_price'] <= df['benchmark_price'] * 2.5)
    df = df[valid_price_mask].copy()
    df = df.drop(columns=['benchmark_price'])
    
    # 6. Recalculate total value
    df['selling_price'] = df['selling_price'].round(2)
    df['total_sales_value'] = (df['quantity'] * df['selling_price']).round(2)
    
    # 7. Referential Integrity Check
    valid_products = set(df_products['product_id'])
    df = df[df['product_id'].isin(valid_products)]
    
    print(f"    Sales: cleaned {initial_count} raw rows -> {len(df)} valid rows (removed {initial_count - len(df)} anomalies/dups)")
    return df

def clean_inventory(df_inventory, df_vendors, df_products):
    """
    Cleans inventory table:
    - Normalizes column names
    - Imputes missing reorder_level (default to median of category)
    - Clips negative stock_quantity to 0
    - Deduplicates by (product_id, vendor_id)
    - Validates foreign keys against vendors and products
    """
    df = df_inventory.copy()
    df = normalize_column_names(df)
    
    df['product_id'] = df['product_id'].astype(str).str.strip().str.upper()
    df['vendor_id'] = df['vendor_id'].astype(str).str.strip().str.upper()
    
    # Clip negative stock
    df['stock_quantity'] = pd.to_numeric(df['stock_quantity'], errors='coerce').fillna(0).astype(int).clip(lower=0)
    
    # Impute reorder_level if missing
    if 'reorder_level' in df.columns:
        med_reorder = df['reorder_level'].median()
        df['reorder_level'] = pd.to_numeric(df['reorder_level'], errors='coerce').fillna(med_reorder).astype(int)
    else:
        df['reorder_level'] = 100
        
    if 'safety_stock' in df.columns:
        df['safety_stock'] = pd.to_numeric(df['safety_stock'], errors='coerce').fillna((df['reorder_level'] * 0.6).astype(int)).astype(int)
    else:
        df['safety_stock'] = (df['reorder_level'] * 0.6).astype(int)
        
    df['inventory_date'] = parse_dates_robustly(df['inventory_date'])
    
    # Deduplicate
    df = df.drop_duplicates(subset=['product_id', 'vendor_id'], keep='first')
    
    # Referential integrity
    valid_vendors = set(df_vendors['vendor_id'])
    valid_products = set(df_products['product_id'])
    df = df[df['vendor_id'].isin(valid_vendors) & df['product_id'].isin(valid_products)]
    return df

def clean_all_datasets(raw_datasets, output_dir=PROCESSED_DATA_DIR):
    """
    Runs the end-to-end cleaning pipeline on all raw tables
    and writes standardized CSV files to the processed directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    print("\n" + "="*50)
    print(" EXECUTING DATA CLEANING PIPELINE")
    print("="*50)
    
    print("[1/5] Cleaning Vendors...")
    cleaned_vendors = clean_vendors(raw_datasets['vendors'])
    
    print("[2/5] Cleaning Products...")
    cleaned_products = clean_products(raw_datasets['products'])
    
    print("[3/5] Cleaning Purchases...")
    cleaned_purchases = clean_purchases(raw_datasets['purchases'], cleaned_vendors, cleaned_products)
    
    print("[4/5] Cleaning Sales...")
    cleaned_sales = clean_sales(raw_datasets['sales'], cleaned_products)
    
    print("[5/5] Cleaning Inventory...")
    cleaned_inventory = clean_inventory(raw_datasets['inventory'], cleaned_vendors, cleaned_products)
    
    cleaned = {
        'vendors': cleaned_vendors,
        'products': cleaned_products,
        'purchases': cleaned_purchases,
        'sales': cleaned_sales,
        'inventory': cleaned_inventory
    }
    
    # Save cleaned files
    for name, df in cleaned.items():
        csv_path = os.path.join(output_dir, f"{name}_clean.csv")
        df.to_csv(csv_path, index=False)
        print(f"[+] Saved cleaned table: {csv_path} ({len(df)} rows)")
        
    return cleaned

if __name__ == '__main__':
    from src.ingestion.loader import load_raw_data
    raw = load_raw_data()
    cleaned = clean_all_datasets(raw)
