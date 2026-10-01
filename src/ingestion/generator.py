"""
Synthetic Data Generator for Vendor Performance Analytics
Generates realistic multi-table relational data for procurement, sales, and inventory,
including deliberate data quality defects (duplicates, missing values, date format inconsistencies,
and price/quantity anomalies) to exercise the ETL cleaning pipeline.
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw')

VENDORS_DATA = [
    ("VND001", "Apex Global Technologies", "US-West", "Electronics", "Alice Zhang", "alice@apexglobal.com", "+1-415-555-0101", 4.7, "2022-01-15"),
    ("VND002", "NovaChip Semiconductor", "Taiwan", "Electronics", "Chen Wei", "chen.wei@novachip.tw", "+886-2-555-0102", 4.8, "2021-06-01"),
    ("VND003", "Pioneer Circuit Systems", "Japan", "Electronics", "Kenji Sato", "sato@pioneercircuit.jp", "+81-3-555-0103", 4.4, "2022-03-10"),
    ("VND004", "Horizon Display Corp", "US-East", "Electronics", "Sarah Jenkins", "sjenkins@horizondisplay.com", "+1-212-555-0104", 4.2, "2022-08-20"),
    ("VND005", "Silicon Valley Components", "US-West", "Electronics", "Marcus Reed", "mreed@svcomponents.io", "+1-408-555-0105", 4.6, "2021-11-12"),
    ("VND006", "Titan Precision Machinery", "Germany", "Industrial Machinery", "Hans Gruber", "hgruber@titanprecision.de", "+49-89-555-0106", 4.9, "2021-03-01"),
    ("VND007", "Vanguard Heavy Dynamics", "US-Midwest", "Industrial Machinery", "Robert Miller", "bmiller@vanguarddynamics.com", "+1-312-555-0107", 4.3, "2022-05-18"),
    ("VND008", "Apex Hydraulic Systems", "US-South", "Industrial Machinery", "David Garcia", "dgarcia@apexhydraulics.com", "+1-713-555-0108", 3.9, "2023-01-10"),
    ("VND009", "Quantum Fluidics & Motors", "Germany", "Industrial Machinery", "Ingrid Weber", "iweber@quantumfluidics.de", "+49-711-555-0109", 4.5, "2022-04-05"),
    ("VND010", "Nordic Industrial Gear", "Germany", "Industrial Machinery", "Lars Lindholm", "lars@nordicgear.se", "+46-8-555-0110", 4.1, "2023-02-14"),
    ("VND011", "Alliance Alloys & Steel", "US-Midwest", "Raw Materials", "Frank O'Connor", "foconnor@alliancealloys.com", "+1-412-555-0111", 4.3, "2021-01-20"),
    ("VND012", "Vertex Chemical Solutions", "US-South", "Raw Materials", "Elena Rostova", "erostova@vertexchem.com", "+1-281-555-0112", 4.0, "2022-07-22"),
    ("VND013", "Summit Polymer Industries", "US-East", "Raw Materials", "Michael Chang", "mchang@summitpolymers.com", "+1-609-555-0113", 4.5, "2021-09-15"),
    ("VND014", "EcoFiber Paper & Pulp", "Canada", "Raw Materials", "Jean-Luc Tremblay", "jtremblay@ecofiber.ca", "+1-514-555-0114", 4.2, "2022-11-01"),
    ("VND015", "Nippon High-Purity Metals", "Japan", "Raw Materials", "Yuki Tanaka", "ytanaka@nipponmetals.co.jp", "+81-6-555-0115", 4.8, "2021-04-12"),
    ("VND016", "Metro Office Supplies", "US-East", "Office Supplies", "Jessica Taylor", "jtaylor@metrooffice.com", "+1-202-555-0116", 3.8, "2022-02-28"),
    ("VND017", "Global Workspace Solutions", "US-West", "Office Supplies", "Daniel Brooks", "dbrooks@globalworkspace.com", "+1-206-555-0117", 4.1, "2021-08-14"),
    ("VND018", "Sterling Stationery Ltd", "Canada", "Office Supplies", "Emily Watson", "ewatson@sterlingstationery.ca", "+1-416-555-0118", 4.4, "2022-10-10"),
    ("VND019", "Crestview Ergonomics", "US-Midwest", "Office Supplies", "Anthony Hopkins", "ahopkins@crestview.com", "+1-612-555-0119", 4.6, "2023-03-05"),
    ("VND020", "OmniDesk Furnishings", "US-South", "Office Supplies", "Carlos Mendoza", "cmendoza@omnidesk.com", "+1-404-555-0120", 3.7, "2023-04-18"),
    ("VND021", "Pacific Corrugated Packaging", "US-West", "Packaging", "Brian Lee", "blee@pacificcorrugated.com", "+1-503-555-0121", 4.5, "2021-05-10"),
    ("VND022", "BioWrap Eco Packaging", "Germany", "Packaging", "Greta Fischer", "gfischer@biowrapgroup.com", "+49-30-555-0122", 4.6, "2022-09-01"),
    ("VND023", "SecurePak Industrial", "US-South", "Packaging", "Raymond Scott", "rscott@securepak.com", "+1-972-555-0123", 3.9, "2022-12-05"),
    ("VND024", "FlexiFilm Polymers", "US-Midwest", "Packaging", "Rachel Adams", "radams@flexifilm.com", "+1-317-555-0124", 4.2, "2021-10-30"),
    ("VND025", "EuroBox Container Logistics", "Germany", "Packaging", "Stefan Muller", "smuller@eurobox.eu", "+49-40-555-0125", 4.3, "2023-05-20")
]

PRODUCT_CATALOG = [
    # Electronics (14 products)
    ("PRD001", "Microcontroller Core X4", "Electronics", "Semiconductors", 42.00, 79.99),
    ("PRD002", "FPGA Accelerated Matrix", "Electronics", "Semiconductors", 125.00, 249.50),
    ("PRD003", "Opto-Coupler High Speed", "Electronics", "Semiconductors", 4.50, 9.99),
    ("PRD004", "Multi-Layer Ceramic PCB v3", "Electronics", "Circuit Boards", 18.20, 39.99),
    ("PRD005", "High-Density Rigid-Flex PCB", "Electronics", "Circuit Boards", 32.50, 68.00),
    ("PRD006", "Embedded Sensor Array", "Electronics", "Sensors", 15.80, 34.50),
    ("PRD007", "Industrial LiDAR Sensor", "Electronics", "Sensors", 210.00, 399.00),
    ("PRD008", "Ultra-Bright OLED Panel 7in", "Electronics", "Displays", 68.00, 129.99),
    ("PRD009", "Touch TFT Module 10in", "Electronics", "Displays", 88.50, 169.00),
    ("PRD010", "e-Paper Display 13.3in", "Electronics", "Displays", 110.00, 215.00),
    ("PRD011", "ARM Cortex IoT Transceiver", "Electronics", "Semiconductors", 28.00, 56.00),
    ("PRD012", "Solid State Relay Module", "Electronics", "Power & Switches", 22.00, 48.00),
    ("PRD013", "Precision Shunt Resistor Kit", "Electronics", "Passive Components", 6.80, 14.50),
    ("PRD014", "Shielded Ethernet Interface", "Electronics", "Networking", 12.40, 27.90),

    # Industrial Machinery (12 products)
    ("PRD015", "Hydraulic Servo Valve 3000PSI", "Industrial Machinery", "Hydraulics", 340.00, 620.00),
    ("PRD016", "High-Pressure Gear Pump 50L", "Industrial Machinery", "Hydraulics", 480.00, 890.00),
    ("PRD017", "Variable Speed AC Drive 15kW", "Industrial Machinery", "Drives & Motors", 650.00, 1190.00),
    ("PRD018", "Brushless DC Motor 48V", "Industrial Machinery", "Drives & Motors", 180.00, 340.00),
    ("PRD019", "Pneumatic Linear Actuator 500mm", "Industrial Machinery", "Pneumatics", 145.00, 285.00),
    ("PRD020", "Heavy Duty Flange Bearing 80mm", "Industrial Machinery", "Bearings & Seals", 75.00, 155.00),
    ("PRD021", "Rotary Encoder Optical 5000PPR", "Industrial Machinery", "Instrumentation", 195.00, 375.00),
    ("PRD022", "Planetary Gearbox Ratio 25:1", "Industrial Machinery", "Gears & Transmissions", 520.00, 980.00),
    ("PRD023", "Industrial Chiller Heat Exchanger", "Industrial Machinery", "Thermal Systems", 820.00, 1490.00),
    ("PRD024", "Cast Iron Centrifugal Impeller", "Industrial Machinery", "Pumps", 215.00, 410.00),
    ("PRD025", "Vibration Damping Mount Heavy", "Industrial Machinery", "Mechanical Hardware", 38.00, 79.00),
    ("PRD026", "PLC Central Controller Unit", "Industrial Machinery", "Automation", 720.00, 1350.00),

    # Raw Materials (12 products)
    ("PRD027", "Stainless Steel Sheet 316L 2mm", "Raw Materials", "Metals", 85.00, 140.00),
    ("PRD028", "Aerospace Grade Aluminum 6061-T6", "Raw Materials", "Metals", 115.00, 195.00),
    ("PRD029", "Copper Rod High Conductive 20mm", "Raw Materials", "Metals", 98.00, 168.00),
    ("PRD030", "Titanium Alloy Ingot Grade 5", "Raw Materials", "Metals", 240.00, 420.00),
    ("PRD031", "Industrial Epoxy Resin 50kg", "Raw Materials", "Chemicals & Polymers", 160.00, 275.00),
    ("PRD032", "Polyurethane Elastomer Pellet", "Raw Materials", "Chemicals & Polymers", 72.00, 125.00),
    ("PRD033", "High-Density Polyethylene HDPE", "Raw Materials", "Chemicals & Polymers", 45.00, 78.00),
    ("PRD034", "Carbon Fiber Prepreg Roll 100m", "Raw Materials", "Composites", 310.00, 540.00),
    ("PRD035", "Bleached Sulfate Kraft Pulp 1T", "Raw Materials", "Paper & Pulp", 450.00, 720.00),
    ("PRD036", "Specialty Ceramic Powder Alumina", "Raw Materials", "Minerals", 130.00, 230.00),
    ("PRD037", "Liquid Silicone Rubber Shore 40", "Raw Materials", "Polymers", 88.00, 152.00),
    ("PRD038", "Galvanized Steel Wire Coils", "Raw Materials", "Metals", 54.00, 92.00),

    # Office Supplies (11 products)
    ("PRD039", "Ergonomic Mesh Task Chair", "Office Supplies", "Furniture", 145.00, 289.00),
    ("PRD040", "Motorized Standing Desk 60in", "Office Supplies", "Furniture", 290.00, 580.00),
    ("PRD041", "Dual Monitor Gas Spring Arm", "Office Supplies", "Accessories", 48.00, 99.00),
    ("PRD042", "Heavy Duty Desktop Shredder", "Office Supplies", "Equipment", 95.00, 185.00),
    ("PRD043", "Recycled Copy Paper 10 Reams", "Office Supplies", "Paper Products", 32.00, 58.00),
    ("PRD044", "Thermal Label Printer Pro", "Office Supplies", "Equipment", 110.00, 219.00),
    ("PRD045", "Acoustic Desk Privacy Screen", "Office Supplies", "Furnishings", 42.00, 85.00),
    ("PRD046", "High-Yield Toner Cartridge Black", "Office Supplies", "Consumables", 55.00, 115.00),
    ("PRD047", "Wireless Presentation Remote", "Office Supplies", "Electronics", 18.00, 39.00),
    ("PRD048", "Executive Leather Conference Chair", "Office Supplies", "Furniture", 210.00, 420.00),
    ("PRD049", "Cable Management Raceway Kit", "Office Supplies", "Accessories", 14.50, 32.00),

    # Packaging (11 products)
    ("PRD050", "Corrugated Shipping Box 12x12x12", "Packaging", "Boxes", 1.20, 2.50),
    ("PRD051", "Heavy Duty Double Wall Box 24x18", "Packaging", "Boxes", 2.80, 5.90),
    ("PRD052", "Biodegradable Air Pillow Roll", "Packaging", "Void Fill", 26.00, 52.00),
    ("PRD053", "Stretch Wrap Film 80 Gauge 4pk", "Packaging", "Films", 42.00, 84.00),
    ("PRD054", "Reinforced Kraft Water Tape 6pk", "Packaging", "Adhesives", 34.00, 68.00),
    ("PRD055", "Thermal Insulated Box Liner 50pk", "Packaging", "Cold Chain", 62.00, 125.00),
    ("PRD056", "Anti-Static Bubble Pouch 8x10", "Packaging", "Protective", 16.50, 35.00),
    ("PRD057", "Molded Pulp Corner Guards 500pk", "Packaging", "Protective", 38.00, 76.00),
    ("PRD058", "High-Tension Poly Strapping Roll", "Packaging", "Strapping", 48.00, 96.00),
    ("PRD059", "Compostable Poly Mailer 10x13", "Packaging", "Envelopes", 14.00, 29.50),
    ("PRD060", "Heavy Duty Pallet Stretch Hood", "Packaging", "Pallet Protection", 85.00, 165.00)
]

CATEGORY_TO_VENDORS = {}
for v in VENDORS_DATA:
    CATEGORY_TO_VENDORS.setdefault(v[3], []).append(v[0])

VENDOR_PRICE_FACTORS = {
    "VND001": 0.96, "VND002": 0.92, "VND003": 1.08, "VND004": 1.14, "VND005": 0.98,
    "VND006": 1.12, "VND007": 0.95, "VND008": 1.05, "VND009": 1.02, "VND010": 0.89,
    "VND011": 0.94, "VND012": 1.11, "VND013": 0.97, "VND014": 0.90, "VND015": 1.15,
    "VND016": 1.18, "VND017": 0.96, "VND018": 0.93, "VND019": 1.04, "VND020": 0.88,
    "VND021": 0.92, "VND022": 1.16, "VND023": 1.03, "VND024": 0.91, "VND025": 0.99
}

def generate_synthetic_data(num_purchases=13000, num_sales=19000, target_dir=RAW_DATA_DIR):
    os.makedirs(target_dir, exist_ok=True)
    print(f"[*] Generating synthetic vendor datasets in: {target_dir}")

    # 1. Vendors
    v_rows = []
    for v in VENDORS_DATA:
        name = v[1]
        cat = v[3]
        email = v[5]
        phone = v[6]
        
        # Noise
        if v[0] in ["VND003", "VND012"]:
            name = name.upper() + "  "
        elif v[0] == "VND008":
            name = "  " + name.lower()
            
        if v[0] == "VND016":
            email = None
        if v[0] == "VND020":
            phone = ""

        v_rows.append({
            "vendor_id": v[0],
            "vendor_name": name,
            "location": v[2],
            "vendor_category": cat,
            "contact_name": v[4],
            "contact_email": email,
            "phone": phone,
            "rating": v[7],
            "contract_start_date": v[8]
        })
    df_vendors = pd.DataFrame(v_rows)

    # 2. Products
    p_rows = []
    for p in PRODUCT_CATALOG:
        p_rows.append({
            "product_id": p[0],
            "product_name": p[1],
            "category": p[2],
            "subcategory": p[3],
            "unit_cost": p[4],
            "selling_price": p[5]
        })
    df_products = pd.DataFrame(p_rows)

    # 3. Purchases
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days

    purchases = []
    for i in range(1, num_purchases + 1):
        day_offset = random.randint(0, total_days)
        cur_date = start_date + timedelta(days=day_offset)
        month = cur_date.month

        prod = random.choice(PRODUCT_CATALOG)
        p_id = prod[0]
        cat = prod[2]
        base_cost = prod[4]

        available_vendors = CATEGORY_TO_VENDORS.get(cat, ["VND001"])
        v_id = random.choice(available_vendors)

        price_factor = VENDOR_PRICE_FACTORS.get(v_id, 1.0)
        fluctuation = random.uniform(0.94, 1.06)
        actual_price = round(base_cost * price_factor * fluctuation, 2)

        if cat == "Packaging":
            qty = random.randint(100, 1500)
        elif cat == "Industrial Machinery":
            qty = random.randint(5, 60)
        elif cat == "Raw Materials":
            qty = random.randint(20, 300)
        elif cat == "Office Supplies":
            qty = random.randint(15, 250)
        else:
            qty = random.randint(25, 400)

        if month in [11, 12]:
            qty = int(qty * random.uniform(1.2, 1.45))

        fmt_choice = random.random()
        if fmt_choice < 0.70:
            date_str = cur_date.strftime("%Y-%m-%d")
        elif fmt_choice < 0.85:
            date_str = cur_date.strftime("%m/%d/%Y")
        else:
            date_str = cur_date.strftime("%d-%m-%Y")

        total_val = round(qty * actual_price, 2)

        purchases.append({
            "purchase_id": f"PO-{i:06d}",
            "vendor_id": v_id,
            "product_id": p_id,
            "purchase_date": date_str,
            "quantity": qty,
            "purchase_price": actual_price,
            "total_purchase_value": total_val
        })

    df_purchases = pd.DataFrame(purchases)

    # Duplicates (~1.5%)
    dup_indices = random.sample(range(len(df_purchases)), int(len(df_purchases) * 0.015))
    df_purchases = pd.concat([df_purchases, df_purchases.iloc[dup_indices].copy()], ignore_index=True)

    # Bad quantities (~0.8%)
    bad_qty_idx = random.sample(range(len(df_purchases)), int(len(df_purchases) * 0.008))
    for idx in bad_qty_idx:
        bad_q = -random.randint(1, 20) if random.random() > 0.3 else 0
        df_purchases.at[idx, "quantity"] = bad_q
        df_purchases.at[idx, "total_purchase_value"] = round(bad_q * df_purchases.at[idx, "purchase_price"], 2)

    # Price outliers (~0.4%)
    outlier_idx = random.sample(range(len(df_purchases)), int(len(df_purchases) * 0.004))
    for idx in outlier_idx:
        if random.random() > 0.5:
            df_purchases.at[idx, "purchase_price"] = round(df_purchases.at[idx, "purchase_price"] * 10, 2)
        else:
            df_purchases.at[idx, "purchase_price"] = -abs(df_purchases.at[idx, "purchase_price"])
        df_purchases.at[idx, "total_purchase_value"] = round(df_purchases.at[idx, "quantity"] * df_purchases.at[idx, "purchase_price"], 2)

    # 4. Sales
    sales = []
    for i in range(1, num_sales + 1):
        day_offset = random.randint(0, total_days)
        cur_date = start_date + timedelta(days=day_offset)
        month = cur_date.month

        prod = random.choice(PRODUCT_CATALOG)
        p_id = prod[0]
        cat = prod[2]
        base_sp = prod[5]

        sp_factor = random.uniform(0.92, 1.05)
        selling_price = round(base_sp * sp_factor, 2)

        if cat == "Packaging":
            qty = random.randint(80, 1200)
        elif cat == "Industrial Machinery":
            qty = random.randint(3, 45)
        elif cat == "Raw Materials":
            qty = random.randint(15, 250)
        elif cat == "Office Supplies":
            qty = random.randint(10, 200)
        else:
            qty = random.randint(20, 350)

        if month in [11, 12]:
            qty = int(qty * random.uniform(1.25, 1.5))

        fmt_choice = random.random()
        if fmt_choice < 0.75:
            date_str = cur_date.strftime("%Y-%m-%d")
        elif fmt_choice < 0.90:
            date_str = cur_date.strftime("%m/%d/%Y")
        else:
            date_str = cur_date.strftime("%Y/%m/%d")

        total_sales = round(qty * selling_price, 2)

        sales.append({
            "sale_id": f"SO-{i:06d}",
            "product_id": p_id,
            "sale_date": date_str,
            "quantity": qty,
            "selling_price": selling_price,
            "total_sales_value": total_sales
        })

    df_sales = pd.DataFrame(sales)

    # Sales duplicates (~1.2%)
    s_dup_idx = random.sample(range(len(df_sales)), int(len(df_sales) * 0.012))
    df_sales = pd.concat([df_sales, df_sales.iloc[s_dup_idx].copy()], ignore_index=True)

    # Sales negative returns (~0.5%)
    s_neg_idx = random.sample(range(len(df_sales)), int(len(df_sales) * 0.005))
    for idx in s_neg_idx:
        df_sales.at[idx, "quantity"] = -random.randint(1, 15)
        df_sales.at[idx, "total_sales_value"] = round(df_sales.at[idx, "quantity"] * df_sales.at[idx, "selling_price"], 2)

    # 5. Inventory
    inv_rows = []
    inv_date = "2026-01-15"
    for p in PRODUCT_CATALOG:
        p_id = p[0]
        cat = p[2]
        cat_vendors = CATEGORY_TO_VENDORS.get(cat, ["VND001"])
        for v_id in cat_vendors[:2]:
            if cat == "Packaging":
                stock = random.randint(1500, 8000)
                reorder = random.randint(1000, 2000)
            elif cat == "Industrial Machinery":
                stock = random.randint(15, 120)
                reorder = random.randint(20, 50)
            elif cat == "Raw Materials":
                stock = random.randint(200, 2500)
                reorder = random.randint(300, 600)
            elif cat == "Office Supplies":
                stock = random.randint(100, 1500)
                reorder = random.randint(150, 400)
            else:
                stock = random.randint(300, 3500)
                reorder = random.randint(400, 800)

            safety_stock = int(reorder * 0.6)

            inv_rows.append({
                "product_id": p_id,
                "vendor_id": v_id,
                "stock_quantity": stock,
                "reorder_level": reorder,
                "safety_stock": safety_stock,
                "inventory_date": inv_date
            })

    df_inventory = pd.DataFrame(inv_rows)
    df_inventory.at[3, "reorder_level"] = np.nan
    df_inventory.at[11, "stock_quantity"] = -10

    # Save to CSV
    df_vendors.to_csv(os.path.join(target_dir, "vendors_raw.csv"), index=False)
    df_products.to_csv(os.path.join(target_dir, "products_raw.csv"), index=False)
    df_purchases.to_csv(os.path.join(target_dir, "purchases_raw.csv"), index=False)
    df_sales.to_csv(os.path.join(target_dir, "sales_raw.csv"), index=False)
    df_inventory.to_csv(os.path.join(target_dir, "inventory_raw.csv"), index=False)

    # Multi-sheet Excel
    excel_path = os.path.join(target_dir, "vendor_procurement_raw.xlsx")
    print(f"[*] Writing multi-sheet raw Excel: {excel_path}")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_vendors.to_excel(writer, sheet_name="Vendors", index=False)
        df_products.to_excel(writer, sheet_name="Products", index=False)
        df_purchases.head(5000).to_excel(writer, sheet_name="Purchases_Sample", index=False)
        df_sales.head(5000).to_excel(writer, sheet_name="Sales_Sample", index=False)
        df_inventory.to_excel(writer, sheet_name="Inventory", index=False)

    print(f"[+] Raw datasets generated successfully in {target_dir}!")
    print(f"    Vendors:     {len(df_vendors)} records")
    print(f"    Products:    {len(df_products)} records")
    print(f"    Purchases:   {len(df_purchases)} records")
    print(f"    Sales:       {len(df_sales)} records")
    print(f"    Inventory:   {len(df_inventory)} records")
    return {
        "vendors": df_vendors,
        "products": df_products,
        "purchases": df_purchases,
        "sales": df_sales,
        "inventory": df_inventory
    }

if __name__ == '__main__':
    generate_synthetic_data()
