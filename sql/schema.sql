-- ====================================================================
-- VENDOR PERFORMANCE & PROCUREMENT INTELLIGENCE - STAR SCHEMA DDL
-- Compatible with PostgreSQL 13+ and ANSI SQL standards
-- ====================================================================

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS FactInventory CASCADE;
DROP TABLE IF EXISTS FactSales CASCADE;
DROP TABLE IF EXISTS FactPurchases CASCADE;
DROP TABLE IF EXISTS DimProduct CASCADE;
DROP TABLE IF EXISTS DimDate CASCADE;
DROP TABLE IF EXISTS DimVendor CASCADE;
DROP TABLE IF EXISTS DimCategory CASCADE;

-- 1. DimCategory (Master Sourcing Categories)
CREATE TABLE DimCategory (
    category_id VARCHAR(10) PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    target_margin_pct NUMERIC(5, 2) DEFAULT 45.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. DimVendor (Supplier Master Dimension)
CREATE TABLE DimVendor (
    vendor_id VARCHAR(15) PRIMARY KEY,
    vendor_code VARCHAR(20) NOT NULL UNIQUE,
    vendor_name VARCHAR(100) NOT NULL,
    vendor_category VARCHAR(50) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) NOT NULL,
    rating NUMERIC(3, 2) CHECK (rating >= 1.0 AND rating <= 5.0),
    contract_start_date DATE NOT NULL,
    payment_terms VARCHAR(30) DEFAULT 'Net 30',
    status VARCHAR(30) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'New / Insufficient Data', 'Suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. DimProduct (Catalog Product Master Dimension)
CREATE TABLE DimProduct (
    product_id VARCHAR(15) PRIMARY KEY,
    product_code VARCHAR(25) NOT NULL UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    category_id VARCHAR(10) NOT NULL REFERENCES DimCategory(category_id) ON DELETE RESTRICT,
    subcategory VARCHAR(50) NOT NULL,
    unit VARCHAR(20) DEFAULT 'Each',
    standard_cost NUMERIC(10, 2) NOT NULL CHECK (standard_cost > 0),
    selling_price NUMERIC(10, 2) NOT NULL CHECK (selling_price > 0),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Discontinued')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. DimDate (Enterprise Calendar Dimension for Power BI & SQL Time Intelligence)
CREATE TABLE DimDate (
    date_id INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter VARCHAR(5) NOT NULL,
    month_num INTEGER NOT NULL CHECK (month_num BETWEEN 1 AND 12),
    month_name VARCHAR(15) NOT NULL,
    month_year VARCHAR(10) NOT NULL,
    day_of_month INTEGER NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_of_week_name VARCHAR(15) NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE
);

-- 5. FactPurchases (Procurement Transactions Fact Table)
CREATE TABLE FactPurchases (
    purchase_id VARCHAR(25) PRIMARY KEY,
    vendor_id VARCHAR(15) NOT NULL REFERENCES DimVendor(vendor_id) ON DELETE RESTRICT,
    product_id VARCHAR(15) NOT NULL REFERENCES DimProduct(product_id) ON DELETE RESTRICT,
    purchase_date DATE NOT NULL REFERENCES DimDate(date) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_purchase_price NUMERIC(10, 2) NOT NULL CHECK (unit_purchase_price > 0),
    total_purchase_value NUMERIC(12, 2) NOT NULL CHECK (total_purchase_value > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. FactSales (Customer Outbound Sales Fact Table)
CREATE TABLE FactSales (
    sale_id VARCHAR(25) PRIMARY KEY,
    product_id VARCHAR(15) NOT NULL REFERENCES DimProduct(product_id) ON DELETE RESTRICT,
    sale_date DATE NOT NULL REFERENCES DimDate(date) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_selling_price NUMERIC(10, 2) NOT NULL CHECK (unit_selling_price > 0),
    total_sales_value NUMERIC(12, 2) NOT NULL CHECK (total_sales_value > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. FactInventory (Warehouse Inventory Snapshot Fact Table)
CREATE TABLE FactInventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id VARCHAR(15) NOT NULL REFERENCES DimProduct(product_id) ON DELETE RESTRICT,
    vendor_id VARCHAR(15) NOT NULL REFERENCES DimVendor(vendor_id) ON DELETE RESTRICT,
    inventory_date DATE NOT NULL,
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),
    safety_stock INTEGER NOT NULL CHECK (safety_stock >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_prod_vendor_inv UNIQUE (product_id, vendor_id)
);
