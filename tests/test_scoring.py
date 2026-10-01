"""
Unit tests for Vendor Performance Scoring (VPS) Mathematical Properties
"""
import os
import pandas as pd
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def test_vps_score_bounds():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, 'vendor_analytics_summary.csv'))
    assert len(df) == 25
    assert (df['vendor_performance_score'] < 0.0).sum() == 0
    assert (df['vendor_performance_score'] > 100.0).sum() == 0

def test_vps_tier_assignments():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, 'vendor_analytics_summary.csv'))
    for _, row in df.iterrows():
        score = row['vendor_performance_score']
        tier = row['performance_tier']
        if score >= 78.0:
            assert 'Tier 1' in tier
        elif score >= 64.0:
            assert 'Tier 2' in tier
        elif score >= 50.0:
            assert 'Tier 3' in tier
        else:
            assert 'Tier 4' in tier

def test_metrics_sanity():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, 'vendor_analytics_summary.csv'))
    assert (df['total_procurement_cost'] <= 0).sum() == 0
    assert (df['total_revenue'] <= 0).sum() == 0
    assert (df['gross_margin_pct'] < -100).sum() == 0
    assert (df['gross_margin_pct'] > 100).sum() == 0
