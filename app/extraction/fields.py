import re
from app.schemas.document import DocumentFields

class FieldExtractor:
    def extract(self, text: str) -> DocumentFields:
        invoice_number = re.search(r"Invoice\s*#?\s*(\S+)", text)
        invoice_date = re.search(r"\d{2}/\d{2}/\d{4}", text)
        total_amount = re.search(r"\$\s?\d+[.,]?\d*", text)
        iban = re.search(r"[A-Z]{2}\d{2}[A-Z0-9]{1,30}", text)

        return DocumentFields(
            invoice_number=invoice_number.group(1) if invoice_number else None,
            invoice_date=invoice_date.group(0) if invoice_date else None,
            total_amount=total_amount.group(0) if total_amount else None,
            iban=iban.group(0) if iban else None
        )