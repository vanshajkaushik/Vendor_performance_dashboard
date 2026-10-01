"""
Pipeline Vendor Performance Scoring (VPS) Engine
Implements strict business logic:
- If a vendor is new or has insufficient transaction data (<3 orders or $0 procurement),
  they are explicitly labeled 'New / Insufficient Data' with VPS = None (never 'Poor Performing').
- Established vendors receive a 5-factor weighted score [0 - 100].
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def calculate_scores(summary_df, output_dir=PROCESSED_DIR):
    df = summary_df.copy()

    is_established = (df['total_orders'] >= 3) & (df['total_procurement_cost'] > 0)
    
    # 1. Revenue Component (25%)
    rev_established = df.loc[is_established, 'total_revenue']
    min_r, max_r = rev_established.min(), rev_established.max()
    s_revenue = pd.Series(np.nan, index=df.index)
    if max_r > min_r:
        s_revenue.loc[is_established] = ((df.loc[is_established, 'total_revenue'] - min_r) / (max_r - min_r) * 80.0 + 20.0)
    else:
        s_revenue.loc[is_established] = 50.0

    # 2. Gross Margin Component (25%): [15%, 55%]
    s_margin = pd.Series(np.nan, index=df.index)
    s_margin.loc[is_established] = ((df.loc[is_established, 'gross_margin_pct'] - 15.0) / (55.0 - 15.0) * 100.0).clip(0.0, 100.0)

    # 3. Purchase Efficiency Component (20%): Ratio 0.45 -> 100, Ratio 0.85 -> 0
    s_eff = pd.Series(np.nan, index=df.index)
    s_eff.loc[is_established] = ((0.85 - df.loc[is_established, 'purchase_to_sales_ratio']) / (0.85 - 0.45) * 100.0).clip(0.0, 100.0)

    # 4. Pricing Competitiveness Component (15%): -12% -> 100, +15% -> 0
    s_pricing = pd.Series(np.nan, index=df.index)
    s_pricing.loc[is_established] = ((15.0 - df.loc[is_established, 'price_variance_pct']) / (15.0 - (-12.0)) * 100.0).clip(0.0, 100.0)

    # 5. Inventory & Operational Component (15%)
    s_ops = pd.Series(np.nan, index=df.index)
    s_rating = ((df.loc[is_established, 'rating'] - 1.0) / 4.0 * 100.0).clip(0.0, 100.0)
    turnover_est = df.loc[is_established, 'inventory_turnover']
    min_t, max_t = turnover_est.min(), turnover_est.max()
    s_turnover = ((turnover_est - min_t) / (max_t - min_t) * 80.0 + 20.0) if max_t > min_t else 50.0
    s_ops.loc[is_established] = (0.6 * s_rating + 0.4 * s_turnover).round(1)

    vps = pd.Series(np.nan, index=df.index)
    vps.loc[is_established] = (
        0.25 * s_revenue.loc[is_established] +
        0.25 * s_margin.loc[is_established] +
        0.20 * s_eff.loc[is_established] +
        0.15 * s_pricing.loc[is_established] +
        0.15 * s_ops.loc[is_established]
    ).round(1)

    df['vendor_performance_score'] = vps

    tiers = []
    recs = []
    for _, row in df.iterrows():
        if pd.isna(row['vendor_performance_score']):
            tiers.append("New / Insufficient Data")
            recs.append("Newly registered supplier. Awaiting initial procurement transaction history to evaluate performance.")
        else:
            score = row['vendor_performance_score']
            p_var = row['price_variance_pct']
            conc = row.get('concentration_pct', 0)

            if score >= 78.0:
                tier = "Tier 1: Strategic"
                rec = "Strategic partner; expand procurement volume allocation and formalize long-term master agreement."
            elif score >= 64.0:
                tier = "Tier 2: Preferred"
                rec = "Consistent preferred supplier; maintain current volume and review volume rebate thresholds."
            elif score >= 50.0:
                tier = "Tier 3: Operational"
                rec = "Operational supplier; monitor delivery lead times and maintain active secondary sourcing."
            else:
                tier = "Tier 4: At-Risk"
                rec = "At-risk supplier with compressed margins; initiate quarterly performance audit or re-tender."

            if p_var > 6.0:
                rec += f" Average purchase price is {p_var}% above benchmark; prioritize price renegotiation."
            if conc > 35.0:
                rec += f" High category spend concentration ({conc}%); monitor supply chain bottleneck risk."

            tiers.append(tier)
            recs.append(rec)

    df['performance_tier'] = tiers
    df['recommendation'] = recs

    out_path = os.path.join(output_dir, "vendor_analytics_summary.csv")
    df.to_csv(out_path, index=False)
    print(f"[+] Finalized vendor scorecard saved: {out_path} ({len(df)} vendors)")
    return df
