import re
from typing import Any
from rapidfuzz.distance import Levenshtein

IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
DATE_RE = re.compile(r"\b(\d{2}[./-]\d{2}[./-]\d{4}|\d{4}[./-]\d{2}[./-]\d{2})\b")
AMOUNT_RE = re.compile(r"\b(\$|€|£)?\s?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})\b")
INVNO_RE = re.compile(r"\b(Invoice|Inv|Invoice#|Invoice No|Invoice Number)\s*[:#]?\s*([A-Za-z0-9-_/]+)\b", re.IGNORECASE)

def field_presence_score(fields: dict[str, Any], keys: list[str]) -> float:
    present = 0
    for k in keys:
        v = fields.get(k)
        if v is not None and str(v).strip():
            present += 1
    return present / max(len(keys), 1)

def pattern_support_score(text: str, fields: dict[str, Any]) -> float:
    score = 0.0
    total = 4.0
    if fields.get("iban"):
        score += 1.0 if IBAN_RE.search(str(fields["iban"])) else 0.0
    if fields.get("invoice_date"):
        score += 1.0 if DATE_RE.search(str(fields["invoice_date"])) else 0.0
    if fields.get("total_amount"):
        score += 1.0 if AMOUNT_RE.search(str(fields["total_amount"])) else 0.0
    if fields.get("invoice_number"):
        score += 1.0 if str(fields["invoice_number"]).strip() else 0.0
    return score / total

def overall_confidence(ocr_conf: float, fields: dict[str, Any]) -> float:
    keys = ["invoice_number", "invoice_date", "total_amount", "iban", "seller_name", "buyer_name"]
    presence = field_presence_score(fields, keys)
    support = pattern_support_score("", fields)
    c = 0.55 * float(ocr_conf) + 0.30 * presence + 0.15 * support
    return max(0.0, min(1.0, c))

def exact_match(a: str | None, b: str | None) -> float:
    a = (a or "").strip()
    b = (b or "").strip()
    return 1.0 if a and b and a == b else 0.0

def similarity(a: str | None, b: str | None) -> float:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a or not b:
        return 0.0
    d = Levenshtein.distance(a, b)
    m = max(len(a), len(b), 1)
    return max(0.0, 1.0 - d / m)