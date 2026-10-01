"""
Data Ingestion Loader
Loads raw CSV/Excel datasets and performs initial schema inspection.
"""

import os
import pandas as pd

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw')

def load_raw_data(data_dir=RAW_DATA_DIR, prefer_excel=False):
    """
    Loads raw tables from either CSV or multi-tab Excel.
    Returns a dict of DataFrames: vendors, products, purchases, sales, inventory.
    """
    datasets = {}
    excel_file = os.path.join(data_dir, "vendor_procurement_raw.xlsx")
    
    if prefer_excel and os.path.exists(excel_file):
        print(f"[*] Loading raw tables from multi-tab Excel: {excel_file}")
        xls = pd.ExcelFile(excel_file, engine="openpyxl")
        datasets["vendors"] = pd.read_excel(xls, "Vendors")
        datasets["products"] = pd.read_excel(xls, "Products")
        # Load full CSVs for high-volume transactions if available, else Excel sample
        purchases_csv = os.path.join(data_dir, "purchases_raw.csv")
        sales_csv = os.path.join(data_dir, "sales_raw.csv")
        datasets["purchases"] = pd.read_csv(purchases_csv) if os.path.exists(purchases_csv) else pd.read_excel(xls, "Purchases_Sample")
        datasets["sales"] = pd.read_csv(sales_csv) if os.path.exists(sales_csv) else pd.read_excel(xls, "Sales_Sample")
        datasets["inventory"] = pd.read_excel(xls, "Inventory")
    else:
        print(f"[*] Loading raw tables from CSV directory: {data_dir}")
        datasets["vendors"] = pd.read_csv(os.path.join(data_dir, "vendors_raw.csv"))
        datasets["products"] = pd.read_csv(os.path.join(data_dir, "products_raw.csv"))
        datasets["purchases"] = pd.read_csv(os.path.join(data_dir, "purchases_raw.csv"))
        datasets["sales"] = pd.read_csv(os.path.join(data_dir, "sales_raw.csv"))
        datasets["inventory"] = pd.read_csv(os.path.join(data_dir, "inventory_raw.csv"))

    return datasets

def inspect_raw_schemas(datasets):
    """
    Inspects schemas, row counts, null distributions, and memory usage.
    """
    report = {}
    print("\n" + "="*50)
    print(" RAW DATA SCHEMA INSPECTION")
    print("="*50)
    for name, df in datasets.items():
        null_counts = df.isnull().sum().to_dict()
        report[name] = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": null_counts,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }
        print(f"\nTable: [{name.upper()}] ({len(df)} rows, {len(df.columns)} cols, {report[name]['memory_usage_mb']} MB)")
        print(f"  Columns: {', '.join(df.columns)}")
        nulls = {k: v for k, v in null_counts.items() if v > 0}
        if nulls:
            print(f"  Null Values Detected: {nulls}")
        else:
            print("  Null Values: None")
    return report

if __name__ == '__main__':
    data = load_raw_data()
    inspect_raw_schemas(data)
