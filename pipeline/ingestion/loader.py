"""
Pipeline Loader
Loads raw CSV and Excel sources into Pandas DataFrames.
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw')

def load_raw_data(raw_dir=RAW_DIR):
    return {
        "categories": pd.read_csv(os.path.join(raw_dir, "categories_raw.csv")),
        "calendar": pd.read_csv(os.path.join(raw_dir, "calendar_raw.csv")),
        "vendors": pd.read_csv(os.path.join(raw_dir, "vendors_raw.csv")),
        "products": pd.read_csv(os.path.join(raw_dir, "products_raw.csv")),
        "purchases": pd.read_csv(os.path.join(raw_dir, "purchases_raw.csv")),
        "sales": pd.read_csv(os.path.join(raw_dir, "sales_raw.csv")),
        "inventory": pd.read_csv(os.path.join(raw_dir, "inventory_raw.csv"))
    }
