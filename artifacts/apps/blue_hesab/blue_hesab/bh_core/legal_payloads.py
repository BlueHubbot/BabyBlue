from __future__ import annotations

import datetime as _dt
from decimal import Decimal
from typing import Any, Dict, Optional


PAYLOAD_SCHEMA_VERSION_V1 = "BH-PAYLOAD-V1"


def _to_jsonable(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (_dt.datetime, _dt.date, _dt.time)):
        return v.isoformat()
    if isinstance(v, (list, tuple, set)):
        return [_to_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _to_jsonable(val) for k, val in v.items()}

    # Frappe/ERPNext child rows / Documents
    try:
        if hasattr(v, "as_dict"):
            return _to_jsonable(v.as_dict())
    except Exception:
        pass

    return str(v)


def build_legal_payload_v1(*, doc, output_type: str, correction_reason: Optional[str]) -> Dict[str, Any]:
    """
    Minimal, deterministic payload.
    Later we can specialize per output_type (TTMS/MODIAN) without breaking hashes,
    by bumping PAYLOAD_SCHEMA_VERSION.
    """
    payload: Dict[str, Any] = {
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION_V1,
        "kind": output_type,
        "correction_reason": correction_reason,
        "ref": {"doctype": getattr(doc, "doctype", None), "name": getattr(doc, "name", None)},
        "company": getattr(doc, "company", None),

        # common financial headers (best-effort)
        "posting_date": getattr(doc, "posting_date", None) or getattr(doc, "transaction_date", None),
        "currency": getattr(doc, "currency", None),
        "net_total": getattr(doc, "net_total", None),
        "total_taxes_and_charges": getattr(doc, "total_taxes_and_charges", None),
        "grand_total": getattr(doc, "grand_total", None),

        # chain hints
        "amended_from": getattr(doc, "amended_from", None),
        "is_return": getattr(doc, "is_return", None),
        "return_against": getattr(doc, "return_against", None),

        # parties
        "customer": getattr(doc, "customer", None),
        "supplier": getattr(doc, "supplier", None),
    }

    items = []
    for it in (getattr(doc, "items", None) or []):
        items.append(
            {
                "item_code": getattr(it, "item_code", None),
                "item_name": getattr(it, "item_name", None),
                "qty": getattr(it, "qty", None),
                "rate": getattr(it, "rate", None),
                "amount": getattr(it, "amount", None),
                "net_amount": getattr(it, "net_amount", None),
                # tolerate custom fields
                "item_tax_template": getattr(it, "item_tax_template", None) or getattr(it, "bh_item_tax_template", None),
                "vat_profile": getattr(it, "bh_vat_profile", None),
            }
        )
    payload["items"] = items

    return _to_jsonable(payload)
