from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, Tuple

import frappe


SCHEMA = "BH-TTMS-CANON-V1"


def _event(correction_reason: str | None) -> str:
    if correction_reason == "CANCEL":
        return "CANCEL"
    if correction_reason == "AMEND":
        return "AMEND"
    return "ISSUE"


def _num(x) -> float:
    try:
        return float(x or 0)
    except Exception:
        return 0.0


def _get(doc, *names, default=None):
    for n in names:
        try:
            v = getattr(doc, n, None)
        except Exception:
            v = None
        if v is not None:
            return v
    return default


def build_ttms_payload(doc, *, output_type: str, correction_reason: str | None) -> Tuple[Dict[str, Any], list[dict]]:
    """
    Returns: (payload_dict, attachments[])
    attachments[] items: {filename, content, mimetype, is_private}
    """
    ev = _event(correction_reason)

    party_type = "Customer" if doc.doctype == "Sales Invoice" else "Supplier"
    party_name = _get(doc, "customer", "supplier", default=None)

    posting_date = str(_get(doc, "posting_date", default="") or "")
    invoice_no = str(getattr(doc, "name", "") or "")

    net = _num(_get(doc, "base_net_total", "net_total", default=0))
    taxes = _num(_get(doc, "base_total_taxes_and_charges", "total_taxes_and_charges", default=0))
    grand = _num(_get(doc, "base_grand_total", "grand_total", default=net + taxes))

    sign = -1.0 if ev == "CANCEL" else 1.0

    row = {
        "event": ev,
        "doctype": doc.doctype,
        "name": invoice_no,
        "posting_date": posting_date,
        "party_type": party_type,
        "party_name": party_name,
        "base_amount": net * sign,
        "vat_amount": taxes * sign,
        "total_amount": grand * sign,
        "currency": _get(doc, "currency", default=None),
        "conversion_rate": _num(_get(doc, "conversion_rate", default=1)),
    }

    payload = {
        "payload_schema": SCHEMA,
        "output_type": output_type,
        "event": ev,
        "invoice": row,
        "warnings": [],
    }

    # CSV attachment (canonical)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(row.keys()))
    w.writeheader()
    w.writerow(row)
    csv_text = buf.getvalue()

    attachments = [{
        "filename": f"TTMS_{doc.doctype}_{invoice_no}_{ev}.csv",
        "content": csv_text,
        "mimetype": "text/csv; charset=utf-8",
        "is_private": 1,
    }]

    return payload, attachments
