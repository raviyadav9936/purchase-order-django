import re
from dateutil import parser as dateparser
from decimal import Decimal, InvalidOperation

# Regex patterns
PO_NO_RE = re.compile(r"\bPO\s*No\s*:\s*([A-Za-z0-9\-]+)\b", re.IGNORECASE)
PO_DATE_RE = re.compile(r"\bPO\s*Date\s*:\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)
GRAND_TOTAL_RE = re.compile(r"\bGrand\s*Total\s*\(INR\)\s*([0-9,]+\.\d{2}|\d+)", re.IGNORECASE)
VENDOR_RE = re.compile(r"Vendor\s*Name\s*:\s*(.+)", re.IGNORECASE)

# Helper functions
def parse_number(s: str):
    try:
        return Decimal(s.replace(",", "")) if s else None
    except (InvalidOperation, AttributeError):
        return None

def parse_date(s: str):
    try:
        return dateparser.parse(s, dayfirst=False).date() if s else None
    except Exception:
        return None


def extract_fields(full_text: str) -> dict:
    data = {}

    # PO number
    m = PO_NO_RE.search(full_text)
    if m:
        data["po_number"] = m.group(1).strip()

    # PO Date
    m = PO_DATE_RE.search(full_text)
    if m:
        data["po_date"] = parse_date(m.group(1))

    # Grand Total
    m = GRAND_TOTAL_RE.search(full_text)
    if m:
        data["grand_total"] = parse_number(m.group(1))

    # Vendor
    m = VENDOR_RE.search(full_text)
    if m:
        data["vendor_name"] = m.group(1).strip()


    if "KiranaKart Technology Private Limited" in full_text:
        data["buyer_name"] = "KiranaKart Technology Private Limited"

    return data
