"""
Vendor Performance Scoring (VPS) Methodology
Calculates a defensible, multi-dimensional weighted performance score (0-100)
for every vendor with objective tiering and tactical business recommendations.

Methodology Breakdown:
1. Revenue Contribution Score (25% weight):
   Normalized scale of vendor-attributed revenue.
2. Gross Margin Score (25% weight):
   Vendor gross margin % scaled across benchmark threshold [15%, 55%].
3. Capital & Procurement Efficiency (20% weight):
   Reward lower Purchase-to-Sales ratios (high revenue capture per $ of procurement).
4. Price Competitiveness (15% weight):
   Reward negative/low purchase price variances vs catalog benchmark costs.
5. Inventory & Operational Health (15% weight):
   Composite of vendor contract rating (60%) and inventory turnover ratio (40%).
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def min_max_scale(series, lower=0.0, upper=100.0):
    """Normalizes a series between lower and upper bounds."""
    s_min = series.min()
    s_max = series.max()
    if s_max == s_min:
        return pd.Series(50.0, index=series.index)
    return ((series - s_min) / (s_max - s_min)) * (upper - lower) + lower

def calculate_vendor_scores(vendor_summary_df, output_dir=PROCESSED_DATA_DIR):
    """
    Computes VPS score and assigns tier badges and actionable procurement recommendations.
    """
    df = vendor_summary_df.copy()

    # 1. Revenue Contribution Component (25%)
    s_revenue = min_max_scale(df['total_revenue'], 20.0, 100.0)

    # 2. Gross Margin Component (25%): 15% margin -> 0, 55% margin -> 100
    s_margin = ((df['gross_margin_pct'] - 15.0) / (55.0 - 15.0) * 100.0).clip(0.0, 100.0)

    # 3. Purchase-to-Sales Efficiency Component (20%):
    # Ratio 0.45 is excellent (100 score), Ratio 0.85 is poor (0 score)
    s_efficiency = ((0.85 - df['purchase_to_sales_ratio']) / (0.85 - 0.45) * 100.0).clip(0.0, 100.0)

    # 4. Pricing Competitiveness Component (15%):
    # -12% variance is best (100 score), +15% variance is poor (0 score)
    s_pricing = ((15.0 - df['price_variance_pct']) / (15.0 - (-12.0)) * 100.0).clip(0.0, 100.0)

    # 5. Inventory & Operational Health (15%):
    # Rating [1.0, 5.0] + min-max inventory turnover
    s_rating = ((df['rating'] - 1.0) / 4.0 * 100.0).clip(0.0, 100.0)
    s_turnover = min_max_scale(df['inventory_turnover'], 20.0, 100.0)
    s_ops = (0.6 * s_rating + 0.4 * s_turnover)

    # Weighted Composite Score
    df['score_revenue'] = s_revenue.round(1)
    df['score_margin'] = s_margin.round(1)
    df['score_efficiency'] = s_efficiency.round(1)
    df['score_pricing'] = s_pricing.round(1)
    df['score_ops'] = s_ops.round(1)

    vps = (
        0.25 * df['score_revenue'] +
        0.25 * df['score_margin'] +
        0.20 * df['score_efficiency'] +
        0.15 * df['score_pricing'] +
        0.15 * df['score_ops']
    ).round(1)
    df['vendor_performance_score'] = vps

    # Assign Tier Badges
    # Tier 1 (Strategic Partner): >= 78
    # Tier 2 (Preferred Vendor): 64 - 77.9
    # Tier 3 (Operational): 50 - 63.9
    # Tier 4 (At-Risk / Renegotiate): < 50
    conditions = [
        df['vendor_performance_score'] >= 78.0,
        (df['vendor_performance_score'] >= 64.0) & (df['vendor_performance_score'] < 78.0),
        (df['vendor_performance_score'] >= 50.0) & (df['vendor_performance_score'] < 64.0)
    ]
    tiers = ['Tier 1: Strategic', 'Tier 2: Preferred', 'Tier 3: Operational']
    df['performance_tier'] = np.select(conditions, tiers, default='Tier 4: At-Risk')

    # Tactical Business Recommendations
    recommendations = []
    for _, row in df.iterrows():
        score = row['vendor_performance_score']
        margin = row['gross_margin_pct']
        p_var = row['price_variance_pct']
        p2s = row['purchase_to_sales_ratio']

        rec_parts = []
        if score >= 78.0:
            rec_parts.append("Key strategic partner; expand volume allocation and negotiate long-term master supply agreement.")
        elif score >= 64.0:
            rec_parts.append("High-performing preferred vendor; maintain current allocation and review volume rebate thresholds.")
        elif score >= 50.0:
            rec_parts.append("Standard operational vendor; monitor fulfillment lead times and maintain dual-source backup.")
        else:
            rec_parts.append("At-risk vendor with compressed margins; initiate quarterly performance audit or re-tender.")

        if p_var > 6.0:
            rec_parts.append(f"Unit purchase cost is {p_var}% above benchmark; renegotiate pricing.")
        elif p_var < -4.0:
            rec_parts.append(f"Favorable pricing ({p_var}% vs benchmark); explore volume consolidation.")

        recommendations.append(" ".join(rec_parts))

    df['recommendation'] = recommendations
    df = df.sort_values('vendor_performance_score', ascending=False).reset_index(drop=True)

    # Save finalized analytical summary
    out_csv = os.path.join(output_dir, "vendor_analytics_summary.csv")
    df.to_csv(out_csv, index=False)
    print(f"[+] Finalized Vendor Scorecard saved: {out_csv} ({len(df)} vendors ranked)")
    return df

if __name__ == '__main__':
    from src.ingestion.loader import load_raw_data
    from src.cleaning.cleaner import clean_all_datasets
    from src.transformation.metrics import calculate_all_metrics
    raw = load_raw_data()
    clean = clean_all_datasets(raw)
    metrics = calculate_all_metrics(clean)
    scores = calculate_vendor_scores(metrics['vendor_summary'])
