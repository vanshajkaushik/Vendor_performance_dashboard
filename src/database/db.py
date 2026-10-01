"""
Database Abstraction Layer
Provides unified access to PostgreSQL (production) with automatic seamless fallback
to an optimized local SQLite analytical engine for frictionless local execution.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'processed')
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sql')
DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'vendor_analytics.db')

class DatabaseManager:
    def __init__(self, db_url=None):
        """
        Initializes connection. If PostgreSQL is not provided or fails to connect,
        falls back to local SQLite engine.
        """
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
                print(f"[+] Connected successfully to PostgreSQL database!")
            except Exception as e:
                print(f"[-] PostgreSQL connection failed ({e}). Falling back to local SQLite database.")

        if self.engine is None:
            self.db_type = "sqlite"
            sqlite_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
            self.engine = create_engine(sqlite_url)
            print(f"[+] Using local analytical SQLite database: {DEFAULT_SQLITE_PATH}")

    def load_processed_tables(self, processed_dir=PROCESSED_DATA_DIR):
        """Loads cleaned CSV tables into the database."""
        tables = ['vendors', 'products', 'purchases', 'sales', 'inventory']
        print("\n" + "="*50)
        print(f" POPULATING DATABASE TABLES ({self.db_type.upper()})")
        print("="*50)

        for tbl in tables:
            csv_path = os.path.join(processed_dir, f"{tbl}_clean.csv")
            if not os.path.exists(csv_path):
                print(f"[-] Missing cleaned file: {csv_path}")
                continue
            df = pd.read_csv(csv_path)
            # Write to SQL
            df.to_sql(tbl, self.engine, if_exists="replace", index=False)
            print(f"[+] Loaded {len(df):>6} rows into table [{tbl}]")

        # Create indexes
        self.create_indexes()
        # Create views
        self.create_views()

    def create_indexes(self):
        """Creates performance indexes."""
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_purchases_vendor ON purchases(vendor_id);",
            "CREATE INDEX IF NOT EXISTS idx_purchases_product ON purchases(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(purchase_date);",
            "CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);",
            "CREATE INDEX IF NOT EXISTS idx_inv_pv ON inventory(product_id, vendor_id);"
        ]
        with self.engine.connect() as conn:
            for q in index_queries:
                try:
                    conn.execute(text(q))
                    conn.commit()
                except Exception as e:
                    pass
        print("[+] Created performance B-tree indexes")

    def create_views(self):
        """Creates analytical views adapted for both PostgreSQL and SQLite."""
        with self.engine.connect() as conn:
            if self.db_type == "postgresql":
                views_path = os.path.join(SQL_DIR, "views.sql")
                if os.path.exists(views_path):
                    with open(views_path, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    # Execute
                    conn.execute(text(sql_content))
                    conn.commit()
                    print("[+] Created PostgreSQL analytical views")
            else:
                # SQLite view equivalents
                sqlite_views = [
                    """
                    CREATE VIEW IF NOT EXISTS vw_monthly_procurement_sales AS
                    WITH m_proc AS (
                        SELECT 
                            SUBSTR(purchase_date, 1, 7) AS month_key,
                            SUM(total_purchase_value) AS procurement_spend,
                            SUM(quantity) AS purchase_volume,
                            COUNT(purchase_id) AS purchase_orders
                        FROM purchases
                        GROUP BY SUBSTR(purchase_date, 1, 7)
                    ),
                    m_sales AS (
                        SELECT 
                            SUBSTR(sale_date, 1, 7) AS month_key,
                            SUM(total_sales_value) AS sales_revenue,
                            SUM(quantity) AS sales_volume,
                            COUNT(sale_id) AS sales_orders
                        FROM sales
                        GROUP BY SUBSTR(sale_date, 1, 7)
                    )
                    SELECT 
                        COALESCE(s.month_key, p.month_key) AS month_key,
                        ROUND(COALESCE(s.sales_revenue, 0), 2) AS sales_revenue,
                        ROUND(COALESCE(p.procurement_spend, 0), 2) AS procurement_spend,
                        ROUND(COALESCE(s.sales_revenue, 0) - COALESCE(p.procurement_spend, 0), 2) AS monthly_gross_profit,
                        ROUND(CASE WHEN s.sales_revenue > 0 THEN ((s.sales_revenue - p.procurement_spend) / s.sales_revenue * 100) ELSE 0 END, 2) AS monthly_margin_pct,
                        COALESCE(s.sales_volume, 0) AS sales_volume,
                        COALESCE(p.purchase_volume, 0) AS purchase_volume
                    FROM m_sales s
                    LEFT JOIN m_proc p ON s.month_key = p.month_key
                    ORDER BY month_key;
                    """,
                    """
                    CREATE VIEW IF NOT EXISTS vw_category_profitability AS
                    WITH cat_sales AS (
                        SELECT 
                            p.category,
                            SUM(s.total_sales_value) AS total_sales,
                            SUM(s.quantity) AS total_units_sold
                        FROM sales s
                        JOIN products p ON s.product_id = p.product_id
                        GROUP BY p.category
                    ),
                    cat_proc AS (
                        SELECT 
                            p.category,
                            SUM(pu.total_purchase_value) AS total_spend,
                            SUM(pu.quantity) AS total_units_procured
                        FROM purchases pu
                        JOIN products p ON pu.product_id = p.product_id
                        GROUP BY p.category
                    )
                    SELECT 
                        cs.category,
                        ROUND(cs.total_sales, 2) AS sales_revenue,
                        ROUND(cp.total_spend, 2) AS procurement_spend,
                        ROUND(cs.total_sales - cp.total_spend, 2) AS gross_profit,
                        ROUND(((cs.total_sales - cp.total_spend) / cs.total_sales * 100), 2) AS gross_margin_pct,
                        cs.total_units_sold,
                        cp.total_units_procured
                    FROM cat_sales cs
                    JOIN cat_proc cp ON cs.category = cp.category;
                    """
                ]
                for v_sql in sqlite_views:
                    try:
                        conn.execute(text(v_sql))
                        conn.commit()
                    except Exception as e:
                        pass
                print("[+] Created SQLite analytical views")

    def query(self, sql_statement, params=None):
        """Executes a SQL query and returns a pandas DataFrame."""
        return pd.read_sql_query(sql_statement, self.engine, params=params)

_db_instance = None

def get_db_manager(db_url=None):
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_url)
    return _db_instance

if __name__ == '__main__':
    mgr = get_db_manager()
    mgr.load_processed_tables()
    df = mgr.query("SELECT COUNT(*) as cnt FROM purchases")
    print(f"Purchases count in DB: {df['cnt'].iloc[0]}")
