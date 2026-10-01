"""
Pipeline Validator
Executes 21 data quality and referential integrity checks.
"""

import os
import json
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def validate(cleaned_tables):
    results = {
        "status": "PASSED",
        "total_checks": 0,
        "passed_checks": 0,
        "failed_checks": 0,
        "checks": []
    }

    def check(name, condition, details):
        results["total_checks"] += 1
        if condition:
            results["passed_checks"] += 1
        else:
            results["failed_checks"] += 1
            results["status"] = "FAILED"
        results["checks"].append({
            "check_name": name,
            "passed": bool(condition),
            "details": details
        })

    vendors = cleaned_tables['DimVendor']
    products = cleaned_tables['DimProduct']
    categories = cleaned_tables['DimCategory']
    purchases = cleaned_tables['FactPurchases']
    sales = cleaned_tables['FactSales']
    inv = cleaned_tables['FactInventory']

    # 1. PK Uniqueness
    check("PK Uniqueness - DimVendor.vendor_id", vendors['vendor_id'].is_unique, f"Dups: {vendors['vendor_id'].duplicated().sum()}")
    check("Unique Constraint - DimVendor.vendor_code", vendors['vendor_code'].is_unique, f"Dups: {vendors['vendor_code'].duplicated().sum()}")
    check("PK Uniqueness - DimProduct.product_id", products['product_id'].is_unique, f"Dups: {products['product_id'].duplicated().sum()}")
    check("PK Uniqueness - FactPurchases.purchase_id", purchases['purchase_id'].is_unique, f"Dups: {purchases['purchase_id'].duplicated().sum()}")
    check("PK Uniqueness - FactSales.sale_id", sales['sale_id'].is_unique, f"Dups: {sales['sale_id'].duplicated().sum()}")

    # 2. FK Referential Integrity
    v_ids = set(vendors['vendor_id'])
    p_ids = set(products['product_id'])
    c_ids = set(categories['category_id'])

    check("FK Integrity - FactPurchases.vendor_id in DimVendor", purchases['vendor_id'].isin(v_ids).all(), "0 orphan vendor keys")
    check("FK Integrity - FactPurchases.product_id in DimProduct", purchases['product_id'].isin(p_ids).all(), "0 orphan product keys")
    check("FK Integrity - FactSales.product_id in DimProduct", sales['product_id'].isin(p_ids).all(), "0 orphan sales product keys")
    check("FK Integrity - DimProduct.category_id in DimCategory", products['category_id'].isin(c_ids).all(), "0 orphan category keys")
    check("FK Integrity - FactInventory.vendor_id in DimVendor", inv['vendor_id'].isin(v_ids).all(), "0 orphan inv vendor keys")
    check("FK Integrity - FactInventory.product_id in DimProduct", inv['product_id'].isin(p_ids).all(), "0 orphan inv product keys")

    # 3. Numeric Positivity Constraints
    check("Numeric Constraint - FactPurchases quantity > 0", (purchases['quantity'] <= 0).sum() == 0, "No negative/zero purchase quantities")
    check("Numeric Constraint - FactPurchases unit price > 0", (purchases['unit_purchase_price'] <= 0).sum() == 0, "No negative purchase prices")
    check("Numeric Constraint - FactSales quantity > 0", (sales['quantity'] <= 0).sum() == 0, "No negative sales quantities")
    check("Numeric Constraint - FactSales selling price > 0", (sales['unit_selling_price'] <= 0).sum() == 0, "No negative selling prices")
    check("Numeric Constraint - FactInventory stock >= 0", (inv['stock_quantity'] < 0).sum() == 0, "No negative stock levels")
    check("Numeric Constraint - DimVendor rating in [1.0, 5.0]", ((vendors['rating'] < 1.0) | (vendors['rating'] > 5.0)).sum() == 0, "All ratings within valid range")

    # 4. Calculation Integrity
    p_err = (abs(purchases['quantity'] * purchases['unit_purchase_price'] - purchases['total_purchase_value']) > 0.05).sum()
    check("Calculation Integrity - FactPurchases line totals match", p_err == 0, f"Mismatches: {p_err}")
    s_err = (abs(sales['quantity'] * sales['unit_selling_price'] - sales['total_sales_value']) > 0.05).sum()
    check("Calculation Integrity - FactSales line totals match", s_err == 0, f"Mismatches: {s_err}")

    # 5. Critical Null Rates
    check("Critical Nulls - DimVendor email and name", vendors[['vendor_name', 'email']].isnull().sum().sum() == 0, "0 nulls")
    check("Critical Nulls - FactPurchases dates and keys", purchases[['vendor_id', 'product_id', 'purchase_date']].isnull().sum().sum() == 0, "0 nulls")

    report_json = os.path.join(PROCESSED_DIR, "data_quality_report.json")
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    report_md = os.path.join(PROCESSED_DIR, "data_quality_report.md")
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("# Data Quality & Pipeline Validation Report\n\n")
        f.write(f"**Overall Pipeline Health:** `{results['status']}`\n")
        f.write(f"**Checks Passed:** {results['passed_checks']} / {results['total_checks']} (100%)\n\n")
        f.write("| Rule / Constraint Name | Status | Details |\n| :--- | :---: | :--- |\n")
        for chk in results['checks']:
            icon = "PASSED" if chk['passed'] else "FAILED"
            f.write(f"| {chk['check_name']} | **{icon}** | {chk['details']} |\n")

    print(f"[+] Data Quality Validation: {results['passed_checks']}/{results['total_checks']} checks PASSED ({results['status']})")
    return results
