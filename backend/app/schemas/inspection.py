from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InspectionCreate(BaseModel):
    inspection_type: str

    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    manufacturer_name: Optional[str] = None

    source_url: Optional[str] = None


class InspectionResponse(BaseModel):
    id: int
    inspection_number: str
    officer_id: int

    inspection_type: str

    product_name: Optional[str]
    brand_name: Optional[str]
    manufacturer_name: Optional[str]

    source_url: Optional[str]

    status: str
    overall_result: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True