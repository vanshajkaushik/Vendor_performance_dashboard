"""
Unit tests for Data Cleaning and Standardization Pipeline
"""
import os
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

@pytest.fixture
def cleaned_data():
    return {
        'vendors': pd.read_csv(os.path.join(PROCESSED_DIR, 'vendors_clean.csv')),
        'products': pd.read_csv(os.path.join(PROCESSED_DIR, 'products_clean.csv')),
        'purchases': pd.read_csv(os.path.join(PROCESSED_DIR, 'purchases_clean.csv')),
        'sales': pd.read_csv(os.path.join(PROCESSED_DIR, 'sales_clean.csv')),
        'inventory': pd.read_csv(os.path.join(PROCESSED_DIR, 'inventory_clean.csv'))
    }

def test_no_duplicate_primary_keys(cleaned_data):
    assert cleaned_data['vendors']['vendor_id'].is_unique
    assert cleaned_data['products']['product_id'].is_unique
    assert cleaned_data['purchases']['purchase_id'].is_unique
    assert cleaned_data['sales']['sale_id'].is_unique

def test_no_negative_or_zero_quantities(cleaned_data):
    assert (cleaned_data['purchases']['quantity'] <= 0).sum() == 0
    assert (cleaned_data['sales']['quantity'] <= 0).sum() == 0
    assert (cleaned_data['inventory']['stock_quantity'] < 0).sum() == 0

def test_no_negative_prices(cleaned_data):
    assert (cleaned_data['purchases']['purchase_price'] <= 0).sum() == 0
    assert (cleaned_data['sales']['selling_price'] <= 0).sum() == 0
    assert (cleaned_data['products']['unit_cost'] <= 0).sum() == 0
    assert (cleaned_data['products']['selling_price'] <= 0).sum() == 0

def test_calculated_total_value_consistency(cleaned_data):
    p = cleaned_data['purchases']
    diff = abs(p['quantity'] * p['purchase_price'] - p['total_purchase_value'])
    assert (diff > 0.05).sum() == 0

    s = cleaned_data['sales']
    diff_s = abs(s['quantity'] * s['selling_price'] - s['total_sales_value'])
    assert (diff_s > 0.05).sum() == 0
