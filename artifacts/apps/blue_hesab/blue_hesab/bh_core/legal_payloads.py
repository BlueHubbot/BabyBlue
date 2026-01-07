from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, Tuple

from .legal_ttms_v1 import build_ttms_payload
from .legal_modian_v1 import build_modian_payload

PAYLOAD_SCHEMA_VERSION_V1 = "BH-PAYLOAD-V1"


def _now_iso() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def build_legal_payload_v1(*, doc, output_type: str, correction_reason: str | None = None) -> Tuple[Dict[str, Any], list[dict]]:
    """
    Returns: (payload_dict, attachments[])
    attachments is a list of dicts that will be attached to BH Legal Output (File doctype).
    """
    ot = (output_type or "").strip()

    # Specialized outputs
    if ot in ("TTMS_EXPORT",):
        return build_ttms_payload(doc, output_type=ot, correction_reason=correction_reason)
    if ot in ("MODIAN_PAYLOAD",):
        return build_modian_payload(doc, output_type=ot, correction_reason=correction_reason)

    # Default/generic payload (VAT + others)
    payload = {
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION_V1,
        "output_type": ot,
        "created_at_utc": _now_iso(),
        "reference": {
            "doctype": getattr(doc, "doctype", None),
            "name": getattr(doc, "name", None),
        },
        "correction_reason": correction_reason,
    }
    return payload, []
