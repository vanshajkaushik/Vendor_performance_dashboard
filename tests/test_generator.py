"""
Unit tests for Synthetic Data Generator
"""
import os
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')

def test_raw_files_exist():
    assert os.path.exists(os.path.join(RAW_DIR, 'vendors_raw.csv'))
    assert os.path.exists(os.path.join(RAW_DIR, 'products_raw.csv'))
    assert os.path.exists(os.path.join(RAW_DIR, 'purchases_raw.csv'))
    assert os.path.exists(os.path.join(RAW_DIR, 'sales_raw.csv'))
    assert os.path.exists(os.path.join(RAW_DIR, 'inventory_raw.csv'))
    assert os.path.exists(os.path.join(RAW_DIR, 'vendor_procurement_raw.xlsx'))

def test_raw_data_volume():
    purchases = pd.read_csv(os.path.join(RAW_DIR, 'purchases_raw.csv'))
    sales = pd.read_csv(os.path.join(RAW_DIR, 'sales_raw.csv'))
    vendors = pd.read_csv(os.path.join(RAW_DIR, 'vendors_raw.csv'))
    products = pd.read_csv(os.path.join(RAW_DIR, 'products_raw.csv'))

    assert len(purchases) >= 10000, f"Expected 10k+ purchases, got {len(purchases)}"
    assert len(sales) >= 10000, f"Expected 10k+ sales, got {len(sales)}"
    assert len(vendors) == 25
    assert len(products) == 60
