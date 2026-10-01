"""
Database Abstraction Layer
Loads Star Schema tables and analytical views into PostgreSQL (or local SQLite fallback).
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sql')
DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'vendor_analytics.db')

class DatabaseManager:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        self.engine = None
        self.db_type = "sqlite"

        if self.db_url and ("postgresql" in self.db_url or "postgres" in self.db_url):
            try:
                pg_engine = create_engine(self.db_url, pool_pre_ping=True)
                with pg_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.engine = pg_engine
                self.db_type = "postgresql"
                print("[+] Connected to PostgreSQL database")
            except Exception as e:
                print(f"[-] PostgreSQL connection error ({e}). Using local SQLite analytical engine.")

        if self.engine is None:
            self.db_type = "sqlite"
            self.engine = create_engine(f"sqlite:///{DEFAULT_SQLITE_PATH}")
            print(f"[+] Using local analytical SQLite database: {DEFAULT_SQLITE_PATH}")

    def load_star_schema(self, processed_dir=PROCESSED_DIR):
        tables = [
            'DimCategory', 'DimDate', 'DimVendor', 'DimProduct',
            'FactPurchases', 'FactSales', 'FactInventory'
        ]
        print("\n" + "="*50)
        print(f" LOADING STAR SCHEMA INTO DATABASE ({self.db_type.upper()})")
        print("="*50)

        for tbl in tables:
            csv_path = os.path.join(processed_dir, f"{tbl}.csv")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.to_sql(tbl, self.engine, if_exists="replace", index=False)
                print(f"[+] Synced {len(df):>6} records -> [{tbl}]")

        self.create_indexes()
        self.create_views()

    def create_indexes(self):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_purchases_vd ON FactPurchases(vendor_id, purchase_date);",
            "CREATE INDEX IF NOT EXISTS idx_purchases_pid ON FactPurchases(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_sales_pdate ON FactSales(product_id, sale_date);",
            "CREATE INDEX IF NOT EXISTS idx_vendors_code ON DimVendor(vendor_code);",
            "CREATE INDEX IF NOT EXISTS idx_inv_pvid ON FactInventory(product_id, vendor_id);"
        ]
        with self.engine.connect() as conn:
            for q in indexes:
                try:
                    conn.execute(text(q))
                    conn.commit()
                except Exception:
                    pass
        print("[+] Created performance B-tree indexes")

    def create_views(self):
        with self.engine.connect() as conn:
            if self.db_type == "postgresql":
                v_path = os.path.join(SQL_DIR, "views.sql")
                if os.path.exists(v_path):
                    with open(v_path, 'r', encoding='utf-8') as f:
                        conn.execute(text(f.read()))
                        conn.commit()
            else:
                v_queries = [
                    """
                    CREATE VIEW IF NOT EXISTS vw_vendor_performance_summary AS
                    WITH vp AS (
                        SELECT vendor_id, COUNT(purchase_id) AS total_orders,
                               SUM(total_purchase_value) AS total_procurement_cost
                        FROM FactPurchases GROUP BY vendor_id
                    )
                    SELECT v.vendor_id, v.vendor_code, v.vendor_name, v.vendor_category, v.country AS location, v.status,
                           COALESCE(vp.total_orders, 0) AS total_purchase_orders,
                           ROUND(COALESCE(vp.total_procurement_cost, 0), 2) AS total_procurement_cost
                    FROM DimVendor v
                    LEFT JOIN vp ON v.vendor_id = vp.vendor_id;
                    """
                ]
                for q in v_queries:
                    try:
                        conn.execute(text(q))
                        conn.commit()
                    except Exception:
                        pass
        print("[+] Synced analytical views")

    def query(self, sql_str, params=None):
        return pd.read_sql_query(sql_str, self.engine, params=params)

_db = None
def get_db(db_url=None):
    global _db
    if _db is None:
        _db = DatabaseManager(db_url)
    return _db
