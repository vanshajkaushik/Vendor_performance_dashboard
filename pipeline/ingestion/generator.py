"""
Realistic Enterprise Sourcing Dataset Generator
Generates 75 vendors, 520 products, full calendar dimension, 13k+ purchases, 19k+ sales,
inventory records, deliberate data quality defects, and a sample import testing CSV.
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw')

CATEGORIES = [
    ("CAT-001", "Electronics", "Semiconductors, PCBs, Displays, and Electronic Components", 48.00),
    ("CAT-002", "Industrial Machinery", "Hydraulics, Pumps, Actuators, Motors, and Mechanical Assemblies", 52.00),
    ("CAT-003", "Raw Materials", "High-purity metals, polymers, industrial chemicals, and paper pulp", 28.00),
    ("CAT-004", "Office Supplies", "Workplace ergonomic furnishings, equipment, and consumables", 38.00),
    ("CAT-005", "Packaging", "Corrugated boxes, protective films, adhesives, and eco-void fill", 32.00),
]

LOCATIONS = [
    ("US-West", "San Jose", "CA", "United States"),
    ("US-East", "New York", "NY", "United States"),
    ("US-Midwest", "Chicago", "IL", "United States"),
    ("US-South", "Houston", "TX", "United States"),
    ("Germany", "Munich", "Bavaria", "Germany"),
    ("Japan", "Tokyo", "Kanto", "Japan"),
    ("Taiwan", "Hsinchu", "Northern", "Taiwan"),
    ("Canada", "Toronto", "Ontario", "Canada"),
]

VENDOR_BASES = [
    ("Apex Global Tech", "Electronics"), ("NovaChip Semiconductor", "Electronics"),
    ("Pioneer Circuit Corp", "Electronics"), ("Horizon Display Systems", "Electronics"),
    ("Silicon Core Ltd", "Electronics"), ("OptoWave Photonics", "Electronics"),
    ("Quantum MicroDevices", "Electronics"), ("Kyoto Micro Electronics", "Electronics"),
    ("Delta Silicon Labs", "Electronics"), ("Sensory Matrix Dynamics", "Electronics"),
    ("TaiPower Integrated", "Electronics"), ("NexGen Logic Systems", "Electronics"),
    ("Vanguard Semiconductor", "Electronics"), ("Circuit Craft International", "Electronics"),
    ("AeroChip Assemblies", "Electronics"),
    
    ("Titan Precision Machinery", "Industrial Machinery"), ("Vanguard Heavy Dynamics", "Industrial Machinery"),
    ("Apex Hydraulic Systems", "Industrial Machinery"), ("Quantum Fluidics & Motors", "Industrial Machinery"),
    ("Nordic Industrial Gear", "Industrial Machinery"), ("Rheinland Heavy Power", "Industrial Machinery"),
    ("Hans Mech Works", "Industrial Machinery"), ("Dynamic Actuator Works", "Industrial Machinery"),
    ("Atlas Turbine & Pumps", "Industrial Machinery"), ("Continental Servo Tech", "Industrial Machinery"),
    ("Alpine Precision Drive", "Industrial Machinery"), ("Stuttgart Machine Co", "Industrial Machinery"),
    ("Krupp Mechanical Dynamics", "Industrial Machinery"), ("TorqueMaster Gearboxes", "Industrial Machinery"),
    ("HydraFlow Industrial", "Industrial Machinery"),

    ("Alliance Alloys & Steel", "Raw Materials"), ("Vertex Chemical Solutions", "Raw Materials"),
    ("Summit Polymer Industries", "Raw Materials"), ("EcoFiber Paper & Pulp", "Raw Materials"),
    ("Nippon High-Purity Metals", "Raw Materials"), ("Bavaria Polymer Fab", "Raw Materials"),
    ("Great Lakes Steel Co", "Raw Materials"), ("Pacific Resin & Chemical", "Raw Materials"),
    ("Kobe High Conductive Metals", "Raw Materials"), ("Titanium Core International", "Raw Materials"),
    ("EuroPulp Specialty Paper", "Raw Materials"), ("Montreal Specialty Fibers", "Raw Materials"),
    ("Keystone Composite Tech", "Raw Materials"), ("CarbonTech Materials", "Raw Materials"),
    ("BioSilicone Resins", "Raw Materials"),

    ("Metro Office Supplies", "Office Supplies"), ("Global Workspace Solutions", "Office Supplies"),
    ("Sterling Stationery Ltd", "Office Supplies"), ("Crestview Ergonomics", "Office Supplies"),
    ("OmniDesk Furnishings", "Office Supplies"), ("Hanseatic Office Group", "Office Supplies"),
    ("Pacific Ergonomic Systems", "Office Supplies"), ("Toronto Executive Paper", "Office Supplies"),
    ("Apex Workplace Accessories", "Office Supplies"), ("Nordic Workstation Design", "Office Supplies"),
    ("Evergreen Office Consumables", "Office Supplies"), ("Precision Office Tech", "Office Supplies"),
    ("Modular Desk Dynamics", "Office Supplies"), ("Kanto Business Supplies", "Office Supplies"),
    ("Beacon Office Systems", "Office Supplies"),

    ("Pacific Corrugated Packaging", "Packaging"), ("BioWrap Eco Packaging", "Packaging"),
    ("SecurePak Industrial", "Packaging"), ("FlexiFilm Polymers", "Packaging"),
    ("EuroBox Container Logistics", "Packaging"), ("GreenShield Packaging", "Packaging"),
    ("Nordic Carton Solutions", "Packaging"), ("Apex Pallet Dynamics", "Packaging"),
    ("EcoCushion Void Fill", "Packaging"), ("ShieldGuard Industrial Bags", "Packaging"),
    ("Kanto Corrugated Box", "Packaging"), ("Great Plains Container", "Packaging"),
    ("ThermalShield Cold Chain", "Packaging"), ("BioPolymer Packaging Group", "Packaging"),
    ("OmniCarton Logistics", "Packaging")
]

SUBCATEGORIES = {
    "Electronics": ["Semiconductors", "Circuit Boards", "Sensors", "Displays", "Passive Components", "Power Systems"],
    "Industrial Machinery": ["Hydraulics", "Drives & Motors", "Pneumatics", "Bearings & Seals", "Instrumentation", "Pumps"],
    "Raw Materials": ["Metals", "Chemicals & Polymers", "Composites", "Paper & Pulp", "Minerals"],
    "Office Supplies": ["Furniture", "Equipment", "Accessories", "Paper Products", "Consumables"],
    "Packaging": ["Boxes", "Void Fill", "Films", "Adhesives", "Protective", "Cold Chain"]
}

def generate_calendar_dim(start_year=2024, end_year=2025):
    """Generates a complete calendar dimension table."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    dates = []
    cur = start
    while cur <= end:
        dates.append({
            "date_id": int(cur.strftime("%Y%m%d")),
            "date": cur.strftime("%Y-%m-%d"),
            "year": cur.year,
            "quarter": f"Q{(cur.month - 1) // 3 + 1}",
            "month_num": cur.month,
            "month_name": cur.strftime("%B"),
            "month_year": cur.strftime("%Y-%m"),
            "day_of_month": cur.day,
            "day_of_week_name": cur.strftime("%A"),
            "is_weekend": cur.weekday() >= 5
        })
        cur += timedelta(days=1)
    return pd.DataFrame(dates)

def generate_all_data(target_dir=RAW_DIR):
    os.makedirs(target_dir, exist_ok=True)
    print(f"[*] Generating enterprise dataset in {target_dir}...")

    # 1. DimCategory
    df_cat = pd.DataFrame([
        {"category_id": c[0], "category_name": c[1], "description": c[2], "target_margin_pct": c[3]}
        for c in CATEGORIES
    ])

    # 2. DimDate
    df_date = generate_calendar_dim()

    # 3. DimVendor (75 vendors)
    vendors = []
    cat_to_vendors = {}
    price_factors = {}
    
    first_names = ["James", "Emma", "Michael", "Sophie", "Kenji", "Hans", "Elena", "Chen", "Sarah", "David"]
    last_names = ["Smith", "Muller", "Tanaka", "Wei", "Zhang", "Gruber", "O'Connor", "Tremblay", "Garcia", "Adams"]

    for i, (v_name, v_cat) in enumerate(VENDOR_BASES, start=1):
        v_id = f"VND-{i:03d}"
        v_code = f"VND-{i:03d}"
        loc = random.choice(LOCATIONS)
        contact = f"{random.choice(first_names)} {random.choice(last_names)}"
        clean_name = v_name.lower().replace(" ", "").replace("&", "").replace("-", "")[:12]
        email = f"{contact.lower().replace(' ', '.')}@{clean_name}.com"
        phone = f"+1-{random.randint(200, 999)}-555-{random.randint(1000, 9999)}"
        rating = round(random.uniform(3.5, 4.95), 2)
        start_date = (datetime(2021, 1, 1) + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d")
        terms = random.choice(["Net 30", "Net 30", "Net 60", "Net 90", "2/10 Net 30"])

        # Pricing factor: < 1.0 means cost advantage, > 1.0 means premium
        factor = round(random.uniform(0.88, 1.18), 2)
        price_factors[v_id] = factor

        cat_to_vendors.setdefault(v_cat, []).append(v_id)

        vendors.append({
            "vendor_id": v_id,
            "vendor_code": v_code,
            "vendor_name": v_name,
            "vendor_category": v_cat,
            "contact_person": contact,
            "email": email,
            "phone": phone,
            "address": f"{random.randint(100, 999)} Commerce Blvd",
            "city": loc[1],
            "state": loc[2],
            "country": loc[3],
            "rating": rating,
            "contract_start_date": start_date,
            "payment_terms": terms,
            "status": "Active"
        })

    df_vendors = pd.DataFrame(vendors)

    # Injected raw vendor noise:
    # A. Inconsistent casing & whitespace
    df_vendors_raw = df_vendors.copy()
    df_vendors_raw.at[2, "vendor_name"] = "  " + df_vendors_raw.at[2, "vendor_name"].upper() + "   "
    df_vendors_raw.at[7, "vendor_name"] = df_vendors_raw.at[7, "vendor_name"].lower()
    # B. Missing emails & phones
    df_vendors_raw.at[14, "email"] = None
    df_vendors_raw.at[21, "phone"] = ""
    # C. Out-of-bounds rating
    df_vendors_raw.at[33, "rating"] = 5.8
    # D. Duplicate rows
    df_vendors_raw = pd.concat([df_vendors_raw, df_vendors_raw.iloc[[4, 18]].copy()], ignore_index=True)

    # 4. DimProduct (520 products across 5 categories)
    products = []
    prod_id_counter = 1

    for cat_id, cat_name, _, _ in CATEGORIES:
        subcats = SUBCATEGORIES[cat_name]
        # Generate ~104 products per category = 520 total
        for j in range(1, 105):
            p_id = f"PRD-{prod_id_counter:04d}"
            p_code = f"SKU-{cat_name[:3].upper()}-{j:03d}"
            subcat = random.choice(subcats)
            
            # Pricing based on category
            if cat_name == "Electronics":
                cost = round(random.uniform(8.0, 350.0), 2)
                markup = random.uniform(1.4, 2.0)
            elif cat_name == "Industrial Machinery":
                cost = round(random.uniform(45.0, 950.0), 2)
                markup = random.uniform(1.5, 2.2)
            elif cat_name == "Raw Materials":
                cost = round(random.uniform(30.0, 480.0), 2)
                markup = random.uniform(1.25, 1.6)
            elif cat_name == "Office Supplies":
                cost = round(random.uniform(12.0, 220.0), 2)
                markup = random.uniform(1.35, 1.8)
            else: # Packaging
                cost = round(random.uniform(1.5, 75.0), 2)
                markup = random.uniform(1.3, 1.7)

            selling_price = round(cost * markup, 2)
            p_name = f"{subcat} Model-{j:03d} {cat_name[:3]}"

            products.append({
                "product_id": p_id,
                "product_code": p_code,
                "product_name": p_name,
                "category_id": cat_id,
                "category_name": cat_name,
                "subcategory": subcat,
                "unit": "Each" if cat_name != "Packaging" else "Bundle",
                "standard_cost": cost,
                "selling_price": selling_price,
                "status": "Active"
            })
            prod_id_counter += 1

    df_products = pd.DataFrame(products)

    # 5. FactPurchases (13,500+ records)
    purchases = []
    start_dt = datetime(2024, 1, 1)
    end_dt = datetime(2025, 12, 31)
    total_days = (end_dt - start_dt).days

    for i in range(1, 13501):
        day_offset = random.randint(0, total_days)
        cur_date = start_dt + timedelta(days=day_offset)
        month = cur_date.month

        prod = random.choice(products)
        p_id = prod["product_id"]
        cat_name = prod["category_name"]
        std_cost = prod["standard_cost"]

        # Select vendor
        avail_vendors = cat_to_vendors.get(cat_name, [vendors[0]["vendor_id"]])
        v_id = random.choice(avail_vendors)
        factor = price_factors.get(v_id, 1.0)
        fluct = random.uniform(0.95, 1.05)
        unit_price = round(std_cost * factor * fluct, 2)

        if cat_name == "Packaging":
            qty = random.randint(80, 1200)
        elif cat_name == "Industrial Machinery":
            qty = random.randint(3, 40)
        elif cat_name == "Raw Materials":
            qty = random.randint(15, 200)
        else:
            qty = random.randint(20, 250)

        # Q4 seasonal boost
        if month in [11, 12]:
            qty = int(qty * random.uniform(1.2, 1.4))

        # Mixed date formats for raw data
        r = random.random()
        if r < 0.70:
            date_str = cur_date.strftime("%Y-%m-%d")
        elif r < 0.85:
            date_str = cur_date.strftime("%m/%d/%Y")
        else:
            date_str = cur_date.strftime("%d-%m-%Y")

        total_val = round(qty * unit_price, 2)

        purchases.append({
            "purchase_id": f"PO-{i:07d}",
            "vendor_id": v_id,
            "product_id": p_id,
            "purchase_date": date_str,
            "quantity": qty,
            "unit_purchase_price": unit_price,
            "total_purchase_value": total_val
        })

    df_purchases_raw = pd.DataFrame(purchases)
    # Inject purchase duplicates & invalid quantities
    dup_p = df_purchases_raw.iloc[random.sample(range(len(df_purchases_raw)), 200)].copy()
    df_purchases_raw = pd.concat([df_purchases_raw, dup_p], ignore_index=True)
    # Bad quantities (negatives/zeros)
    for idx in random.sample(range(len(df_purchases_raw)), 100):
        df_purchases_raw.at[idx, "quantity"] = -random.randint(1, 15)
        df_purchases_raw.at[idx, "total_purchase_value"] = round(df_purchases_raw.at[idx, "quantity"] * df_purchases_raw.at[idx, "unit_purchase_price"], 2)

    # 6. FactSales (19,000+ records)
    sales = []
    for i in range(1, 19001):
        day_offset = random.randint(0, total_days)
        cur_date = start_dt + timedelta(days=day_offset)
        month = cur_date.month

        prod = random.choice(products)
        p_id = prod["product_id"]
        cat_name = prod["category_name"]
        sp = prod["selling_price"]
        sp_realized = round(sp * random.uniform(0.94, 1.04), 2)

        if cat_name == "Packaging":
            qty = random.randint(70, 1000)
        elif cat_name == "Industrial Machinery":
            qty = random.randint(2, 35)
        elif cat_name == "Raw Materials":
            qty = random.randint(10, 180)
        else:
            qty = random.randint(15, 220)

        if month in [11, 12]:
            qty = int(qty * random.uniform(1.25, 1.45))

        r = random.random()
        if r < 0.75:
            date_str = cur_date.strftime("%Y-%m-%d")
        elif r < 0.90:
            date_str = cur_date.strftime("%m/%d/%Y")
        else:
            date_str = cur_date.strftime("%Y/%m/%d")

        sales.append({
            "sale_id": f"SO-{i:07d}",
            "product_id": p_id,
            "sale_date": date_str,
            "quantity": qty,
            "unit_selling_price": sp_realized,
            "total_sales_value": round(qty * sp_realized, 2)
        })

    df_sales_raw = pd.DataFrame(sales)
    # Inject duplicates
    dup_s = df_sales_raw.iloc[random.sample(range(len(df_sales_raw)), 220)].copy()
    df_sales_raw = pd.concat([df_sales_raw, dup_s], ignore_index=True)

    # 7. FactInventory
    inv_records = []
    for prod in products:
        p_id = prod["product_id"]
        cat_name = prod["category_name"]
        v_list = cat_to_vendors.get(cat_name, [vendors[0]["vendor_id"]])
        primary_vendor = v_list[0]
        
        if cat_name == "Packaging":
            stock = random.randint(2000, 10000)
            reorder = random.randint(1500, 3000)
        elif cat_name == "Industrial Machinery":
            stock = random.randint(10, 80)
            reorder = random.randint(15, 40)
        elif cat_name == "Raw Materials":
            stock = random.randint(200, 2000)
            reorder = random.randint(300, 600)
        else:
            stock = random.randint(250, 2500)
            reorder = random.randint(350, 700)

        inv_records.append({
            "product_id": p_id,
            "vendor_id": primary_vendor,
            "inventory_date": "2026-01-15",
            "stock_quantity": stock,
            "reorder_level": reorder,
            "safety_stock": int(reorder * 0.6)
        })
    df_inv_raw = pd.DataFrame(inv_records)

    # 8. Sample CSV for Testing the "Import Vendors" Feature
    # Contains:
    # - 10 valid vendors
    # - 2 in-file duplicates (duplicate vendor code)
    # - 1 database duplicate (matches VND-001)
    # - 2 invalid rows (invalid email format, invalid rating 7.5)
    sample_import_rows = [
        # Valid vendors
        {"vendor_code": "VND-IMP01", "vendor_name": "Zenith MicroTech", "vendor_category": "Electronics", "contact_person": "Laura Chen", "email": "laura.chen@zenithmicro.com", "phone": "+1-415-555-0991", "country": "United States", "rating": 4.6, "contract_start_date": "2025-01-10", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP02", "vendor_name": "Bavaria Servo Dynamics", "vendor_category": "Industrial Machinery", "contact_person": "Klaus Richter", "email": "k.richter@bavariaservo.de", "phone": "+49-89-555-0992", "country": "Germany", "rating": 4.8, "contract_start_date": "2025-02-01", "payment_terms": "Net 60"},
        {"vendor_code": "VND-IMP03", "vendor_name": "Nordic Pulp & Carton", "vendor_category": "Raw Materials", "contact_person": "Astrid Lind", "email": "astrid@nordicpulp.se", "phone": "+46-8-555-0993", "country": "Sweden", "rating": 4.2, "contract_start_date": "2025-01-15", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP04", "vendor_name": "Tokyo High Conductive", "vendor_category": "Electronics", "contact_person": "Takashi Sato", "email": "sato@tokyoconductive.jp", "phone": "+81-3-555-0994", "country": "Japan", "rating": 4.9, "contract_start_date": "2025-03-01", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP05", "vendor_name": "Apex EcoPack International", "vendor_category": "Packaging", "contact_person": "Mark Evans", "email": "mevans@apexecopack.com", "phone": "+1-206-555-0995", "country": "United States", "rating": 4.4, "contract_start_date": "2025-02-15", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP06", "vendor_name": "Cascade Ergonomic Desks", "vendor_category": "Office Supplies", "contact_person": "Rachel Green", "email": "rgreen@cascadedesks.com", "phone": "+1-503-555-0996", "country": "United States", "rating": 4.1, "contract_start_date": "2025-01-20", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP07", "vendor_name": "Solvent Chemical Works", "vendor_category": "Raw Materials", "contact_person": "Dmitri Volkov", "email": "dvolkov@solventworks.com", "phone": "+1-713-555-0997", "country": "United States", "rating": 3.9, "contract_start_date": "2025-02-28", "payment_terms": "Net 60"},
        {"vendor_code": "VND-IMP08", "vendor_name": "Pinnacle Actuators", "vendor_category": "Industrial Machinery", "contact_person": "Oliver Brown", "email": "obrown@pinnacleactuators.com", "phone": "+44-20-555-0998", "country": "United Kingdom", "rating": 4.7, "contract_start_date": "2025-03-10", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP09", "vendor_name": "FlexiSeal Industrial Tape", "vendor_category": "Packaging", "contact_person": "Hannah Scott", "email": "hscott@flexisealtape.com", "phone": "+1-312-555-0999", "country": "United States", "rating": 4.3, "contract_start_date": "2025-01-05", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP10", "vendor_name": "Summit Laser Optics", "vendor_category": "Electronics", "contact_person": "Victor Vance", "email": "vvance@summitlaser.com", "phone": "+1-408-555-0910", "country": "United States", "rating": 4.5, "contract_start_date": "2025-02-12", "payment_terms": "Net 30"},
        
        # In-file duplicate vendor code
        {"vendor_code": "VND-IMP01", "vendor_name": "Duplicate Zenith", "vendor_category": "Electronics", "contact_person": "Duplicate Person", "email": "dup@zenith.com", "phone": "+1-415-555-0991", "country": "United States", "rating": 4.0, "contract_start_date": "2025-01-10", "payment_terms": "Net 30"},
        {"vendor_code": "VND-IMP02", "vendor_name": "Duplicate Bavaria", "vendor_category": "Industrial Machinery", "contact_person": "Duplicate Person 2", "email": "dup2@bavaria.de", "phone": "+49-89-555-0992", "country": "Germany", "rating": 4.0, "contract_start_date": "2025-02-01", "payment_terms": "Net 60"},
        
        # Database duplicate (matching existing VND-001)
        {"vendor_code": "VND-001", "vendor_name": "Apex Global Tech Duplicate", "vendor_category": "Electronics", "contact_person": "James Smith", "email": "jsmith@apexglobaltech.com", "phone": "+1-415-555-0101", "country": "United States", "rating": 4.5, "contract_start_date": "2025-01-01", "payment_terms": "Net 30"},

        # Invalid rows
        {"vendor_code": "VND-INV01", "vendor_name": "Bad Email Corp", "vendor_category": "Electronics", "contact_person": "Bob Jones", "email": "invalid-email-address-format", "phone": "+1-212-555-0199", "country": "United States", "rating": 4.0, "contract_start_date": "2025-01-01", "payment_terms": "Net 30"},
        {"vendor_code": "VND-INV02", "vendor_name": "Out of Range Rating Corp", "vendor_category": "Packaging", "contact_person": "Alice Moore", "email": "amoore@ratingcorp.com", "phone": "+1-212-555-0299", "country": "United States", "rating": 7.5, "contract_start_date": "2025-01-01", "payment_terms": "Net 30"}
    ]
    df_sample_import = pd.DataFrame(sample_import_rows)
    df_sample_import.to_csv(os.path.join(target_dir, "sample_vendor_import.csv"), index=False)

    # Save all raw tables to CSV
    df_cat.to_csv(os.path.join(target_dir, "categories_raw.csv"), index=False)
    df_date.to_csv(os.path.join(target_dir, "calendar_raw.csv"), index=False)
    df_vendors_raw.to_csv(os.path.join(target_dir, "vendors_raw.csv"), index=False)
    df_products.to_csv(os.path.join(target_dir, "products_raw.csv"), index=False)
    df_purchases_raw.to_csv(os.path.join(target_dir, "purchases_raw.csv"), index=False)
    df_sales_raw.to_csv(os.path.join(target_dir, "sales_raw.csv"), index=False)
    df_inv_raw.to_csv(os.path.join(target_dir, "inventory_raw.csv"), index=False)

    # Multi-sheet Excel workbook
    excel_path = os.path.join(target_dir, "enterprise_procurement_raw.xlsx")
    print(f"[*] Writing multi-sheet Excel source: {excel_path}...")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_cat.to_excel(writer, sheet_name="DimCategory", index=False)
        df_vendors_raw.head(100).to_excel(writer, sheet_name="DimVendor", index=False)
        df_products.head(520).to_excel(writer, sheet_name="DimProduct", index=False)
        df_purchases_raw.head(5000).to_excel(writer, sheet_name="FactPurchases_Sample", index=False)
        df_sales_raw.head(5000).to_excel(writer, sheet_name="FactSales_Sample", index=False)
        df_inv_raw.to_excel(writer, sheet_name="FactInventory", index=False)

    print(f"[+] Data generation complete!")
    print(f"    Vendors:     {len(df_vendors_raw)} rows (75 unique + noise)")
    print(f"    Products:    {len(df_products)} rows (520 SKUs across 5 categories)")
    print(f"    Purchases:   {len(df_purchases_raw)} rows (with noise)")
    print(f"    Sales:       {len(df_sales_raw)} rows (with noise)")
    print(f"    Calendar:    {len(df_date)} days (2024-2025)")
    print(f"    Sample CSV:  {len(df_sample_import)} test import rows")
    return True

if __name__ == '__main__':
    generate_all_data()
