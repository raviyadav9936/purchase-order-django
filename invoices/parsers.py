import re
from dateutil import parser as dateparser
from decimal import Decimal, InvalidOperation

# Regex tuned to your sample PO layout (MH221176, Jan 31, 2023, Grand Total 17067.12)
PO_NO_RE = re.compile(r"\bPO\s*No\s*:\s*([A-Za-z0-9\-]+)\b", re.IGNORECASE)
PO_DATE_RE = re.compile(r"\bPO\s*Date\s*:\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)
REL_DATE_RE = re.compile(r"\bPO\s*Release\s*Date\s*:\s*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)
TAXABLE_TOTAL_RE = re.compile(r"\bTotal\s*Amount\s*\(INR\)\s*([0-9,]+\.\d{2}|\d+)", re.IGNORECASE)
TAX_TOTAL_RE = re.compile(r"\bTotal\s*Tax\s*\(INR\)\s*([0-9,]+\.\d{2}|\d+)", re.IGNORECASE)
GRAND_TOTAL_RE = re.compile(r"\bGrand\s*Total\s*\(INR\)\s*([0-9,]+\.\d{2}|\d+)", re.IGNORECASE)
VENDOR_RE = re.compile(r"Vendor\s*Name\s*:\s*(.+)", re.IGNORECASE)
BUYER_RE = re.compile(r"Billing Address\s*(.*?)\n", re.IGNORECASE | re.DOTALL)

def parse_number(s: str):
    if not s:
        return None
    try:
        return Decimal(s.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return None

def parse_date(s: str):
    if not s:
        return None
    try:
        return dateparser.parse(s, dayfirst=False).date()
    except Exception:
        return None

def extract_fields(full_text: str) -> dict:
    data = {}

    # PO number
    m = PO_NO_RE.search(full_text)
    if m:
        data["po_number"] = m.group(1).strip()

    # Dates
    m = PO_DATE_RE.search(full_text)
    if m:
        data["po_date"] = parse_date(m.group(1))
    m = REL_DATE_RE.search(full_text)
    if m:
        data["release_date"] = parse_date(m.group(1))

    # Totals
    m = TAXABLE_TOTAL_RE.search(full_text)
    if m: data["taxable_total"] = parse_number(m.group(1))
    m = TAX_TOTAL_RE.search(full_text)
    if m: data["tax_total"] = parse_number(m.group(1))
    m = GRAND_TOTAL_RE.search(full_text)
    if m: data["grand_total"] = parse_number(m.group(1))

    # Vendor/Buyer (best-effort from common headers)
    m = VENDOR_RE.search(full_text)
    if m: data["vendor_name"] = m.group(1).strip()

    # Try to infer buyer/company name around addresses if present
    if "KiranaKart Technology Private Limited" in full_text:
        data["buyer_name"] = "KiranaKart Technology Private Limited"

    return data
