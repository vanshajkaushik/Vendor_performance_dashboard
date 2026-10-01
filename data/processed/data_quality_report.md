# Data Quality & Pipeline Validation Report

**Overall Pipeline Health:** `PASSED`
**Checks Passed:** 21 / 21 (100%)

| Rule / Constraint Name | Status | Details |
| :--- | :---: | :--- |
| PK Uniqueness - DimVendor.vendor_id | **PASSED** | Dups: 0 |
| Unique Constraint - DimVendor.vendor_code | **PASSED** | Dups: 0 |
| PK Uniqueness - DimProduct.product_id | **PASSED** | Dups: 0 |
| PK Uniqueness - FactPurchases.purchase_id | **PASSED** | Dups: 0 |
| PK Uniqueness - FactSales.sale_id | **PASSED** | Dups: 0 |
| FK Integrity - FactPurchases.vendor_id in DimVendor | **PASSED** | 0 orphan vendor keys |
| FK Integrity - FactPurchases.product_id in DimProduct | **PASSED** | 0 orphan product keys |
| FK Integrity - FactSales.product_id in DimProduct | **PASSED** | 0 orphan sales product keys |
| FK Integrity - DimProduct.category_id in DimCategory | **PASSED** | 0 orphan category keys |
| FK Integrity - FactInventory.vendor_id in DimVendor | **PASSED** | 0 orphan inv vendor keys |
| FK Integrity - FactInventory.product_id in DimProduct | **PASSED** | 0 orphan inv product keys |
| Numeric Constraint - FactPurchases quantity > 0 | **PASSED** | No negative/zero purchase quantities |
| Numeric Constraint - FactPurchases unit price > 0 | **PASSED** | No negative purchase prices |
| Numeric Constraint - FactSales quantity > 0 | **PASSED** | No negative sales quantities |
| Numeric Constraint - FactSales selling price > 0 | **PASSED** | No negative selling prices |
| Numeric Constraint - FactInventory stock >= 0 | **PASSED** | No negative stock levels |
| Numeric Constraint - DimVendor rating in [1.0, 5.0] | **PASSED** | All ratings within valid range |
| Calculation Integrity - FactPurchases line totals match | **PASSED** | Mismatches: 0 |
| Calculation Integrity - FactSales line totals match | **PASSED** | Mismatches: 0 |
| Critical Nulls - DimVendor email and name | **PASSED** | 0 nulls |
| Critical Nulls - FactPurchases dates and keys | **PASSED** | 0 nulls |
