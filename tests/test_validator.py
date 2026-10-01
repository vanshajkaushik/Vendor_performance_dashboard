"""
Unit tests for Referential Integrity and Schema Validation
"""
import os
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def test_referential_integrity():
    vendors = pd.read_csv(os.path.join(PROCESSED_DIR, 'vendors_clean.csv'))
    products = pd.read_csv(os.path.join(PROCESSED_DIR, 'products_clean.csv'))
    purchases = pd.read_csv(os.path.join(PROCESSED_DIR, 'purchases_clean.csv'))
    sales = pd.read_csv(os.path.join(PROCESSED_DIR, 'sales_clean.csv'))

    valid_v_ids = set(vendors['vendor_id'])
    valid_p_ids = set(products['product_id'])

    assert purchases['vendor_id'].isin(valid_v_ids).all()
    assert purchases['product_id'].isin(valid_p_ids).all()
    assert sales['product_id'].isin(valid_p_ids).all()

def test_date_validity():
    purchases = pd.read_csv(os.path.join(PROCESSED_DIR, 'purchases_clean.csv'))
    sales = pd.read_csv(os.path.join(PROCESSED_DIR, 'sales_clean.csv'))

    p_dates = pd.to_datetime(purchases['purchase_date'])
    s_dates = pd.to_datetime(sales['sale_date'])

    assert p_dates.min() >= pd.Timestamp("2024-01-01")
    assert p_dates.max() <= pd.Timestamp("2025-12-31")
    assert s_dates.min() >= pd.Timestamp("2024-01-01")
    assert s_dates.max() <= pd.Timestamp("2025-12-31")
