import os
import pytest
import sqlite3
import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app
from pipeline.database.db import get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_vendors" in data

def test_kpis_endpoint():
    response = client.get("/api/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_sales" in data
    assert "total_procurement" in data
    assert "gross_margin_pct" in data
    assert data["total_sales"] > 0
    assert data["total_procurement"] > 0

def test_vendors_list_and_tiers():
    response = client.get("/api/vendors")
    assert response.status_code == 200
    vendors = response.json()
    assert len(vendors) >= 75
    tiers = {v["performance_tier"] for v in vendors if v.get("performance_tier")}
    assert any("Strategic" in t or "Tier 1" in t for t in tiers)

def test_duplicate_prevention_on_create():
    # Attempting to add an existing vendor code should return 400 Bad Request
    existing_vendor = {
        "vendor_code": "VND-001",
        "vendor_name": "Apex Micro Electronics Inc",
        "category_id": 1,
        "email": "procurement@apexmicro.com",
        "country": "USA"
    }
    res = client.post("/api/vendors/create", json=existing_vendor)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()

def test_create_new_vendor_and_insufficient_data_logic():
    unique_code = f"VND-TST{os.getpid()}"
    new_vendor = {
        "vendor_code": unique_code,
        "vendor_name": f"Test Vendor Logistics {os.getpid()}",
        "category_id": 2,
        "contact_name": "Test Manager",
        "email": f"test_mgr_{os.getpid()}@example.com",
        "city": "Chicago",
        "country": "USA",
        "payment_terms": "Net 30",
        "lead_time_days": 14
    }
    
    # Create vendor
    res = client.post("/api/vendors/create", json=new_vendor)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["vendor_code"] == unique_code

    # Check vendor list - should be classified as "New / Insufficient Data" with score None or 0
    res_list = client.get("/api/vendors")
    assert res_list.status_code == 200
    vendors = {v["vendor_id"]: v for v in res_list.json()}
    assert unique_code in vendors
    created = vendors[unique_code]
    assert "New / Insufficient Data" in created["performance_tier"]
    assert created["vendor_performance_score"] is None or created["vendor_performance_score"] == 0

def test_csv_import_preview_and_duplicate_handling():
    sample_csv_path = os.path.join(r"C:\Users\Dhruv\.gemini\antigravity\scratch\vendor-performance-dashboard", "data", "raw", "sample_vendor_import.csv")
    assert os.path.exists(sample_csv_path), "Sample CSV file missing"
    
    with open(sample_csv_path, "rb") as f:
        res = client.post("/api/vendors/import/preview", files={"file": ("sample.csv", f, "text/csv")})
    
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 15
    assert data["valid_rows"] == 10
    assert data["duplicate_rows"] == 3
    assert data["invalid_rows"] == 2
    assert len(data["error_details"]) == 5

def test_csv_import_confirm():
    unique_code = f"VND-CSV{os.getpid()}"
    records_to_insert = [{
        "vendor_code": unique_code,
        "vendor_name": f"CSV Import Test Vendor {os.getpid()}",
        "category_id": 1,
        "contact_name": "Import Contact",
        "email": f"csv_{os.getpid()}@example.com",
        "phone": "+1-555-9999",
        "city": "Denver",
        "country": "USA",
        "payment_terms": "Net 30",
        "lead_time_days": 10,
        "status": "Active"
    }]
    
    res = client.post("/api/vendors/import/confirm", json=records_to_insert)
    assert res.status_code == 200
    assert res.json()["inserted"] == 1

def test_powerbi_deliverables_exist():
    pbi_dir = os.path.join(r"C:\Users\Dhruv\.gemini\antigravity\scratch\vendor-performance-dashboard", "powerbi")
    assert os.path.exists(os.path.join(pbi_dir, "Vendor_Performance_Dashboard.pbit"))
    assert os.path.exists(os.path.join(pbi_dir, "Vendor_Performance_Dashboard.pbix"))
    assert os.path.exists(os.path.join(pbi_dir, "dax", "measures.dax"))
    assert os.path.exists(os.path.join(pbi_dir, "model", "power_query.m"))
    assert os.path.exists(os.path.join(pbi_dir, "model", "star_schema.json"))
