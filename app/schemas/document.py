from pydantic import BaseModel
from typing import Optional

class DocumentFields(BaseModel):
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    seller_name: Optional[str]
    buyer_name: Optional[str]
    total_amount: Optional[str]
    iban: Optional[str]