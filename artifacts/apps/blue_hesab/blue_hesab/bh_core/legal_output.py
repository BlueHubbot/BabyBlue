# -*- coding: utf-8 -*-

import hashlib
import json
from typing import Any, Dict, Optional, Union

import frappe
from frappe.utils import now_datetime

from blue_hesab.bh_core.legal_immutability import legal_emit_session
from blue_hesab.bh_core.versioning import get_generator_build, get_schema_version

try:
    # optional (exists in your tree)
    from blue_hesab.bh_core.legal_payloads import PAYLOAD_SCHEMA_VERSION_V1
except Exception:
    PAYLOAD_SCHEMA_VERSION_V1 = "BH-PAYLOAD-V1"


JsonLike = Union[Dict[str, Any], list, str, int, float, bool, None]


def _canon_json(obj: JsonLike) -> str:
    # canonical JSON for stable hashes (auditable & reproducible)
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_hex(data: Union[str, bytes]) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _sha256_json(obj: JsonLike) -> str:
    return _sha256_hex(_canon_json(obj))


def create_legal_output(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    payload: Optional[Union[Dict[str, Any], str]] = None,
    source: Optional[Union[Dict[str, Any], str]] = None,
    correction_reason: Optional[str] = None,
    previous_output: Optional[str] = None,
    schema_version: Optional[str] = None,
    generator_build: Optional[str] = None,
    generated_by: Optional[str] = None,
    generated_at=None,
    docstatus_override: Optional[int] = None,
) -> str:
    """
    Inserts + submits BH Legal Output under legal_emit_session.

    - Default is docstatus=1 (submitted) to match repo queries and regress tests.
    - Idempotent for submitted outputs with same (company, ref, type, reason).
    - Uses hashlib (no frappe.utils.sha256).
    - Ensures payload_schema_version exists if payload is dict (LEGAL09 guard).
    """

    schema_version = schema_version or get_schema_version()
    generator_build = generator_build or get_generator_build()
    generated_by = generated_by or getattr(frappe.session, "user", None) or "Administrator"
    generated_at = generated_at or now_datetime()

    # default: submitted
    desired_docstatus = 1 if docstatus_override is None else int(docstatus_override)

    # idempotent (submitted)
    if desired_docstatus == 1:
        existing = frappe.db.get_value(
            "BH Legal Output",
            {
                "company": company,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "output_type": output_type,
                "correction_reason": correction_reason,
                "docstatus": 1,
            },
            "name",
        )
        if existing:
            return existing

    # normalize payload/source -> json strings + stable hashes
    payload_json: Optional[str] = None
    payload_hash: Optional[str] = None

    if payload is not None:
        if isinstance(payload, dict):
            payload.setdefault("payload_schema_version", PAYLOAD_SCHEMA_VERSION_V1)
            payload_json = _canon_json(payload)
            payload_hash = _sha256_json(payload)
        else:
            payload_json = str(payload)
            payload_hash = _sha256_hex(payload_json)

    source_json: Optional[str] = None
    source_hash: Optional[str] = None
    if source is not None:
        if isinstance(source, dict):
            source_json = _canon_json(source)
            source_hash = _sha256_json(source)
        else:
            source_json = str(source)
            source_hash = _sha256_hex(source_json)

    doc = frappe.get_doc(
        {
            "doctype": "BH Legal Output",
            "company": company,
            "output_type": output_type,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "correction_reason": correction_reason,
            "previous_output": previous_output,
            "schema_version": schema_version,
            "generator_build": generator_build,
            "generated_by": generated_by,
            "generated_at": generated_at,
            "payload_json": payload_json,
            "payload_hash": payload_hash,
            "source_json": source_json,
            "source_hash": source_hash,
        }
    )

    # MUST be inside legal_emit_session (DB triggers require it)
    with legal_emit_session():
        doc.insert(ignore_permissions=True)
        if desired_docstatus == 1:
            doc.submit()

    return doc.name
