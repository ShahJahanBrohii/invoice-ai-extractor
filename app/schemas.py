import re
from typing import List, Optional

from pydantic import BaseModel, field_validator


def clean_number(value):


    if value is None:
        return None

    
    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        stripped = value.strip()

        if stripped == "":
            return None

        
        cleaned = re.sub(r"[^\d.\-]", "", stripped)

        if cleaned in ("", "-", "."):
            return None

        try:
            return float(cleaned)
        except ValueError:
            
            return value

    return value


class InvoiceItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

    @field_validator("quantity", "unit_price", "total", mode="before")
    @classmethod
    def _clean_numbers(cls, value):
        return clean_number(value)


class InvoiceSchema(BaseModel):

    invoice_number: Optional[str] = None

    invoice_date: Optional[str] = None

    supplier_name: Optional[str] = None

    customer_name: Optional[str] = None

    vat_number: Optional[str] = None

    subtotal: Optional[float] = None

    vat: Optional[float] = None

    grand_total: Optional[float] = None

    currency: Optional[str] = None

    items: List[InvoiceItem] = []

    @field_validator("subtotal", "vat", "grand_total", mode="before")
    @classmethod
    def _clean_numbers(cls, value):
        return clean_number(value)
    