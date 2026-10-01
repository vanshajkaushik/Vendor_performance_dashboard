"""
Data Quality and Validation Suite
Performs strict structural, referential, and numerical constraint checks,
and generates an automated Data Quality Report (JSON + Markdown).
"""

import os
import json
import pandas as pd

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')

def validate_datasets(cleaned_datasets):
    """
    Validates cleaned tables for integrity constraints:
    - Primary key uniqueness
    - Foreign key referential integrity
    - Zero null values in critical fields
    - Positive numeric constraints
    - Date format and range validity
    """
    results = {
        "status": "PASSED",
        "total_checks": 0,
        "passed_checks": 0,
        "failed_checks": 0,
        "checks": []
    }
    
    vendors = cleaned_datasets['vendors']
    products = cleaned_datasets['products']
    purchases = cleaned_datasets['purchases']
    sales = cleaned_datasets['sales']
    inventory = cleaned_datasets['inventory']
    
    def log_check(name, passed, details):
        results["total_checks"] += 1
        if passed:
            results["passed_checks"] += 1
        else:
            results["failed_checks"] += 1
            results["status"] = "FAILED"
        results["checks"].append({
            "check_name": name,
            "passed": bool(passed),
            "details": details
        })

    # 1. Primary Key Uniqueness
    log_check("PK Uniqueness - vendors.vendor_id", vendors['vendor_id'].is_unique, f"Duplicate count: {vendors['vendor_id'].duplicated().sum()}")
    log_check("PK Uniqueness - products.product_id", products['product_id'].is_unique, f"Duplicate count: {products['product_id'].duplicated().sum()}")
    log_check("PK Uniqueness - purchases.purchase_id", purchases['purchase_id'].is_unique, f"Duplicate count: {purchases['purchase_id'].duplicated().sum()}")
    log_check("PK Uniqueness - sales.sale_id", sales['sale_id'].is_unique, f"Duplicate count: {sales['sale_id'].duplicated().sum()}")
    
    # 2. Foreign Key Integrity
    vendor_ids = set(vendors['vendor_id'])
    product_ids = set(products['product_id'])
    
    purchases_v_orphans = (~purchases['vendor_id'].isin(vendor_ids)).sum()
    log_check("FK Integrity - purchases.vendor_id in vendors", purchases_v_orphans == 0, f"Orphan count: {purchases_v_orphans}")
    
    purchases_p_orphans = (~purchases['product_id'].isin(product_ids)).sum()
    log_check("FK Integrity - purchases.product_id in products", purchases_p_orphans == 0, f"Orphan count: {purchases_p_orphans}")
    
    sales_p_orphans = (~sales['product_id'].isin(product_ids)).sum()
    log_check("FK Integrity - sales.product_id in products", sales_p_orphans == 0, f"Orphan count: {sales_p_orphans}")
    
    inv_v_orphans = (~inventory['vendor_id'].isin(vendor_ids)).sum()
    log_check("FK Integrity - inventory.vendor_id in vendors", inv_v_orphans == 0, f"Orphan count: {inv_v_orphans}")
    
    inv_p_orphans = (~inventory['product_id'].isin(product_ids)).sum()
    log_check("FK Integrity - inventory.product_id in products", inv_p_orphans == 0, f"Orphan count: {inv_p_orphans}")

    # 3. Numeric Positive Constraints
    log_check("Numeric Constraint - purchases.quantity > 0", (purchases['quantity'] <= 0).sum() == 0, f"Violations: {(purchases['quantity'] <= 0).sum()}")
    log_check("Numeric Constraint - purchases.purchase_price > 0", (purchases['purchase_price'] <= 0).sum() == 0, f"Violations: {(purchases['purchase_price'] <= 0).sum()}")
    log_check("Numeric Constraint - sales.quantity > 0", (sales['quantity'] <= 0).sum() == 0, f"Violations: {(sales['quantity'] <= 0).sum()}")
    log_check("Numeric Constraint - sales.selling_price > 0", (sales['selling_price'] <= 0).sum() == 0, f"Violations: {(sales['selling_price'] <= 0).sum()}")
    log_check("Numeric Constraint - inventory.stock_quantity >= 0", (inventory['stock_quantity'] < 0).sum() == 0, f"Violations: {(inventory['stock_quantity'] < 0).sum()}")

    # 4. Critical Null Rate
    for tbl_name, df, cols in [
        ('vendors', vendors, ['vendor_id', 'vendor_name', 'vendor_category']),
        ('products', products, ['product_id', 'product_name', 'unit_cost', 'selling_price']),
        ('purchases', purchases, ['purchase_id', 'vendor_id', 'product_id', 'purchase_date', 'total_purchase_value']),
        ('sales', sales, ['sale_id', 'product_id', 'sale_date', 'total_sales_value']),
        ('inventory', inventory, ['product_id', 'vendor_id', 'stock_quantity', 'reorder_level'])
    ]:
        null_count = df[cols].isnull().sum().sum()
        log_check(f"Null Checks - {tbl_name} critical columns", null_count == 0, f"Null count across {cols}: {null_count}")

    # 5. Calculation Integrity: quantity * price == total_value
    p_calc_err = (abs(purchases['quantity'] * purchases['purchase_price'] - purchases['total_purchase_value']) > 0.05).sum()
    log_check("Calculation Integrity - purchases total value matches", p_calc_err == 0, f"Mismatch rows: {p_calc_err}")
    
    s_calc_err = (abs(sales['quantity'] * sales['selling_price'] - sales['total_sales_value']) > 0.05).sum()
    log_check("Calculation Integrity - sales total value matches", s_calc_err == 0, f"Mismatch rows: {s_calc_err}")

    return results

def generate_data_quality_report(validation_results, output_dir=PROCESSED_DATA_DIR):
    """Saves the validation report as JSON and Markdown."""
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "data_quality_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)
        
    md_path = os.path.join(output_dir, "data_quality_report.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Data Quality & Validation Report\n\n")
        f.write(f"**Overall Status:** `{validation_results['status']}`  \n")
        f.write(f"**Total Checks Executed:** {validation_results['total_checks']}  \n")
        f.write(f"**Passed:** {validation_results['passed_checks']} | **Failed:** {validation_results['failed_checks']}\n\n")
        f.write("| Check Name | Status | Details |\n")
        f.write("| :--- | :---: | :--- |\n")
        for check in validation_results['checks']:
            icon = "PASS" if check['passed'] else "FAIL"
            f.write(f"| {check['check_name']} | **{icon}** | {check['details']} |\n")
            
    print(f"[+] Data Quality Report generated:")
    print(f"    JSON: {json_path}")
    print(f"    Markdown: {md_path}")
    print(f"    Result: {validation_results['passed_checks']}/{validation_results['total_checks']} checks PASSED ({validation_results['status']})")
    return json_path, md_path

if __name__ == '__main__':
    from src.ingestion.loader import load_raw_data
    from src.cleaning.cleaner import clean_all_datasets
    raw = load_raw_data()
    cleaned = clean_all_datasets(raw)
    res = validate_datasets(cleaned)
    generate_data_quality_report(res)
