from __future__ import annotations

from typing import Any, Dict, Optional

def build_legal_payload_v1(*, doc, output_type: str, correction_reason: Optional[str] = None) -> Dict[str, Any]:
    # LEGAL-08: skeleton payloads (stable, extend later)
    base: Dict[str, Any] = {
        "kind": output_type,
        "correction_reason": correction_reason,
        "ref": {"doctype": doc.doctype, "name": doc.name},
        "company": getattr(doc, "company", None),
        "posting_date": getattr(doc, "posting_date", None),
        "customer": getattr(doc, "customer", None),
        "supplier": getattr(doc, "supplier", None),
        "grand_total": getattr(doc, "grand_total", None),
        "net_total": getattr(doc, "net_total", None),
        "currency": getattr(doc, "currency", None),
    }

    try:
        base["taxes"] = [
            {
                "account_head": getattr(t, "account_head", None),
                "rate": getattr(t, "rate", None),
                "tax_amount": getattr(t, "tax_amount", None),
                "total": getattr(t, "total", None),
            }
            for t in (getattr(doc, "taxes", None) or [])
        ]
    except Exception:
        base["taxes"] = []

    try:
        base["items"] = [
            {
                "item_code": getattr(it, "item_code", None),
                "qty": getattr(it, "qty", None),
                "rate": getattr(it, "rate", None),
                "amount": getattr(it, "amount", None),
                "item_tax_template": getattr(it, "item_tax_template", None),
            }
            for it in (getattr(doc, "items", None) or [])
        ]
    except Exception:
        base["items"] = []

    return base
