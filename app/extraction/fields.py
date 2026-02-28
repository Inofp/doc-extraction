import re
from app.schemas.document import DocumentFields

INVNO_RE = re.compile(r"\b(Invoice|Inv|Invoice#|Invoice No|Invoice Number)\s*[:#]?\s*([A-Za-z0-9-_/]+)\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(\d{2}[./-]\d{2}[./-]\d{4}|\d{4}[./-]\d{2}[./-]\d{2})\b")
AMOUNT_RE = re.compile(r"\b(\$|€|£)?\s?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})\b")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")

def _pick_amount(text: str) -> str | None:
    matches = [m.group(0) for m in AMOUNT_RE.finditer(text)]
    if not matches:
        return None
    return matches[-1]

class FieldExtractor:
    def extract(self, text: str) -> DocumentFields:
        inv = INVNO_RE.search(text)
        dt = DATE_RE.search(text)
        iban = IBAN_RE.search(text)
        amt = _pick_amount(text)

        return DocumentFields(
            invoice_number=inv.group(2) if inv else None,
            invoice_date=dt.group(1) if dt else None,
            total_amount=amt,
            iban=iban.group(0) if iban else None,
            seller_name=None,
            buyer_name=None
        )