"""
Pydantic Schemas for Vendor Performance & Procurement Intelligence
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class VendorBase(BaseModel):
    vendor_code: str = Field(..., description="Unique business vendor code e.g. VND-001")
    vendor_name: str = Field(..., min_length=2, max_length=100)
    vendor_category: str = Field(..., description="Electronics, Industrial Machinery, etc.")
    contact_person: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Business contact email")
    phone: Optional[str] = "+1-555-0100"
    address: Optional[str] = "100 Commerce Blvd"
    city: Optional[str] = "San Jose"
    state: Optional[str] = "CA"
    country: str = "United States"
    rating: float = Field(default=4.0, ge=1.0, le=5.0)
    contract_start_date: str = Field(default="2025-01-01", description="YYYY-MM-DD")
    payment_terms: str = Field(default="Net 30")
    status: str = Field(default="New / Insufficient Data")

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = None
    vendor_category: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None

class VendorStatusUpdate(BaseModel):
    status: str = Field(..., description="Active, Inactive, Suspended")

class ImportRowError(BaseModel):
    row_index: int
    vendor_code: Optional[str] = ""
    field: str
    reason: str
    raw_data: Dict[str, Any]

class ImportPreviewResponse(BaseModel):
    total_rows: int
    valid_count: int
    duplicate_count: int
    invalid_count: int
    valid_rows: List[Dict[str, Any]]
    errors: List[ImportRowError]
    duplicates: List[Dict[str, Any]]

class ImportConfirmRequest(BaseModel):
    confirmed_rows: List[Dict[str, Any]]

class ImportConfirmResponse(BaseModel):
    status: str
    imported_count: int
    message: str
