# Data Dictionary & Schema Specifications

## 1. Raw Datasets (`data/raw/`)

### 1.1 `vendors_raw.csv` / Sheet `Vendors`
| Column | Type | Nullable | Description | Sample Value |
| :--- | :--- | :---: | :--- | :--- |
| `vendor_id` | VARCHAR(10) | No | Unique supplier identifier | `VND001` |
| `vendor_name` | VARCHAR(100) | No | Supplier trade name (may contain casing noise) | `Apex Global Technologies  ` |
| `location` | VARCHAR(50) | No | Geographical region | `US-West` |
| `vendor_category` | VARCHAR(50) | No | Primary operational category | `Electronics` |
| `contact_name` | VARCHAR(100) | Yes | Primary vendor account manager | `Alice Zhang` |
| `contact_email` | VARCHAR(100) | Yes | Account manager email (may have nulls) | `alice@apexglobal.com` |
| `phone` | VARCHAR(30) | Yes | Contact phone number | `+1-415-555-0101` |
| `rating` | NUMERIC(3,2) | No | Vendor quality assessment rating (1.0 - 5.0) | `4.7` |
| `contract_start_date`| DATE | No | Master agreement commencement date | `2022-01-15` |

### 1.2 `products_raw.csv` / Sheet `Products`
| Column | Type | Nullable | Description | Sample Value |
| :--- | :--- | :---: | :--- | :--- |
| `product_id` | VARCHAR(10) | No | Unique stock keeping unit (SKU) identifier | `PRD001` |
| `product_name` | VARCHAR(150) | No | Catalog descriptive name | `Microcontroller Core X4` |
| `category` | VARCHAR(50) | No | Sourcing classification | `Electronics` |
| `subcategory` | VARCHAR(50) | No | Granular classification | `Semiconductors` |
| `unit_cost` | NUMERIC(10,2)| No | Benchmark target cost per unit | `42.00` |
| `selling_price` | NUMERIC(10,2)| No | Manufacturer suggested retail price (MSRP)| `79.99` |

### 1.3 `purchases_raw.csv` / Sheet `Purchases_Sample`
| Column | Type | Nullable | Description | Sample Value |
| :--- | :--- | :---: | :--- | :--- |
| `purchase_id` | VARCHAR(20) | No | Purchase order identifier | `PO-000001` |
| `vendor_id` | VARCHAR(10) | No | Supplying vendor FK | `VND002` |
| `product_id` | VARCHAR(10) | No | Sourced product FK | `PRD001` |
| `purchase_date` | VARCHAR(30) | No | Order date (mixed formatting) | `2024-03-15` / `03/15/2024` |
| `quantity` | INTEGER | No | Units ordered (may contain noise/negatives)| `150` |
| `purchase_price` | NUMERIC(10,2)| No | Invoiced unit price (may contain outliers) | `38.64` |
| `total_purchase_value`| NUMERIC(12,2)| No | Total purchase spend | `5796.00` |

### 1.4 `sales_raw.csv` / Sheet `Sales_Sample`
| Column | Type | Nullable | Description | Sample Value |
| :--- | :--- | :---: | :--- | :--- |
| `sale_id` | VARCHAR(20) | No | Sales order identifier | `SO-000001` |
| `product_id` | VARCHAR(10) | No | Product SKU sold FK | `PRD001` |
| `sale_date` | VARCHAR(30) | No | Transaction date | `2024-01-20` |
| `quantity` | INTEGER | No | Units sold to customer | `120` |
| `selling_price` | NUMERIC(10,2)| No | Actual realized selling price | `76.50` |
| `total_sales_value` | NUMERIC(12,2)| No | Realized gross sales | `9180.00` |

### 1.5 `inventory_raw.csv` / Sheet `Inventory`
| Column | Type | Nullable | Description | Sample Value |
| :--- | :--- | :---: | :--- | :--- |
| `product_id` | VARCHAR(10) | No | Product SKU FK | `PRD001` |
| `vendor_id` | VARCHAR(10) | No | Designated replenishment vendor FK | `VND001` |
| `stock_quantity` | INTEGER | No | Current on-hand quantity | `1250` |
| `reorder_level` | INTEGER | Yes| Buffer trigger point | `600` |
| `safety_stock` | INTEGER | No | Critical reserve threshold | `360` |
| `inventory_date` | DATE | No | Snapshot audit date | `2026-01-15` |

---

## 2. Processed Analytical Tables (`data/processed/`)

### 2.1 `vendor_analytics_summary.csv`
- `vendor_id`: Unique identifier.
- `vendor_name`: Standardized vendor name.
- `vendor_category`: Operational category.
- `location`: Supplier region.
- `rating`: Quality assessment rating (1.0 to 5.0).
- `total_procurement_cost`: Sum of all validated purchase values.
- `total_revenue`: Attributed customer sales revenue based on sourcing share.
- `gross_profit`: Total Revenue - Total Procurement Cost.
- `gross_margin_pct`: (Gross Profit / Total Revenue) * 100.
- `purchase_to_sales_ratio`: Total Procurement Cost / Total Revenue.
- `price_variance_pct`: Average percentage variance vs product benchmark costs.
- `inventory_turnover`: Annualized procurement cost / current inventory value.
- `vendor_performance_score`: Weighted multi-factor score [0.0 - 100.0].
- `performance_tier`: Tier 1 (Strategic), Tier 2 (Preferred), Tier 3 (Operational), Tier 4 (At-Risk).
- `recommendation`: Automated strategic sourcing recommendation.
