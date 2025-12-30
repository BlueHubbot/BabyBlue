from __future__ import annotations

from typing import Any, Dict, Optional


def build_legal_payload_v1(*, doc, output_type: str, correction_reason: Optional[str] = None) -> Dict[str, Any]:
    """LEGAL-08 (skeleton): deterministic payload for TTMS/MODIAN until real generators land."""
    return {
        "kind": output_type,
        "correction_reason": correction_reason,
        "ref": {"doctype": getattr(doc, "doctype", None), "name": getattr(doc, "name", None)},
        "company": getattr(doc, "company", None),
        "posting_date": getattr(doc, "posting_date", None),
        "transaction_date": getattr(doc, "transaction_date", None),
        "customer": getattr(doc, "customer", None),
        "supplier": getattr(doc, "supplier", None),
        "grand_total": getattr(doc, "grand_total", None),
        "net_total": getattr(doc, "net_total", None),
        "currency": getattr(doc, "currency", None),
    }
