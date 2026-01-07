from __future__ import annotations

import json
from typing import Any, Dict, Tuple

import frappe


SCHEMA = "BH-MODIAN-CANON-V1"


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


def build_modian_payload(doc, *, output_type: str, correction_reason: str | None) -> Tuple[Dict[str, Any], list[dict]]:
    """
    Canonical payload for Modian integration.
    Returns: (payload_dict, attachments[])
    """
    ev = _event(correction_reason)

    posting_date = str(_get(doc, "posting_date", default="") or "")
    posting_time = str(_get(doc, "posting_time", default="00:00:00") or "00:00:00")
    invoice_no = str(getattr(doc, "name", "") or "")

    header = {
        "event": ev,
        "doctype": doc.doctype,
        "name": invoice_no,
        "posting_date": posting_date,
        "posting_time": posting_time,
        "company": _get(doc, "company", default=None),
        "party": _get(doc, "customer", "supplier", default=None),
        "currency": _get(doc, "currency", default=None),
        "conversion_rate": _num(_get(doc, "conversion_rate", default=1)),
        "is_return": int(_get(doc, "is_return", default=0) or 0),
    }

    net = _num(_get(doc, "base_net_total", "net_total", default=0))
    taxes = _num(_get(doc, "base_total_taxes_and_charges", "total_taxes_and_charges", default=0))
    grand = _num(_get(doc, "base_grand_total", "grand_total", default=net + taxes))

    lines = []
    for it in (getattr(doc, "items", None) or []):
        lines.append({
            "item_code": _get(it, "item_code", default=None),
            "item_name": _get(it, "item_name", default=None),
            "qty": _num(_get(it, "qty", default=0)),
            "uom": _get(it, "uom", default=None),
            "rate": _num(_get(it, "rate", default=0)),
            "amount": _num(_get(it, "amount", default=0)),
        })

    payload = {
        "payload_schema": SCHEMA,
        "output_type": output_type,
        "event": ev,
        "header": header,
        "amounts": {"net": net, "tax": taxes, "total": grand},
        "lines": lines,
        "warnings": [],
    }

    attachments = [{
        "filename": f"MODIAN_{doc.doctype}_{invoice_no}_{ev}.json",
        "content": json.dumps(payload, ensure_ascii=False, indent=2),
        "mimetype": "application/json; charset=utf-8",
        "is_private": 1,
    }]

    return payload, attachments
