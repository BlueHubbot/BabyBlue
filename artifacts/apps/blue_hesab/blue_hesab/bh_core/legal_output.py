# -*- coding: utf-8 -*-
"""
BH Legal Output creation + hashing + audit logging.

Key requirement: must pass both UI-level and DB-level policy locks:
- sets frappe.flags.bh_legal_emit
- sets DB session var @bh_legal_emit=1

Public API:
- hash_obj(obj)
- create_legal_output(...)
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from typing import Any, Dict, Optional

import frappe

from blue_hesab.bh_core import legal_policy
from blue_hesab.bh_core.legal_immutability import legal_emit_session
from blue_hesab.bh_core.legal_repo import find_last_output_for_ref


def _append_log(filename: str, obj: Dict[str, Any]) -> None:
    try:
        base = frappe.get_site_path("private", "files", "bh_regress")
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, filename)
        payload = dict(obj)
        payload.setdefault("ts", str(_dt.datetime.utcnow()))
        payload.setdefault("site", frappe.local.site)
        payload.setdefault("user", getattr(frappe.session, "user", None))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def hash_obj(obj: Any) -> str:
    """
    Stable sha256 hash of an object after canonical JSON serialization.
    """
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _coerce_dict(v: Any) -> Dict[str, Any]:
    if v is None:
        return {}
    if isinstance(v, dict):
        return v
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return {}
        try:
            parsed = json.loads(v)
            return parsed if isinstance(parsed, dict) else {"value": parsed}
        except Exception:
            return {"value": v}
    # fallback
    return {"value": v}


def create_legal_output(*args, **kwargs) -> str:
    """
    Backward/forward compatible creator.

    Accepts either:
      - reference_doctype/reference_name
      - ref_doctype/ref_name
    plus:
      - company, output_type
      - correction_reason (None | 'CANCEL' | 'AMEND' | ...)
      - previous_output (optional)
      - source (dict | json str)
      - payload (dict | json str)
      - schema_version (optional)
      - generator_build (optional)
      - submit (bool, default True)
    Returns: created output `name`
    """
    company = kwargs.get("company")
    output_type = kwargs.get("output_type")

    # Aliases
    reference_doctype = kwargs.get("reference_doctype") or kwargs.get("ref_doctype")
    reference_name = kwargs.get("reference_name") or kwargs.get("ref_name")

    if not company or not output_type or not reference_doctype or not reference_name:
        raise frappe.ValidationError("create_legal_output: missing required arguments")

    correction_reason = kwargs.get("correction_reason")
    previous_output = kwargs.get("previous_output")

    source = _coerce_dict(kwargs.get("source"))
    payload = _coerce_dict(kwargs.get("payload"))

    schema_version = kwargs.get("schema_version") or legal_policy.get_schema_version(company=company, output_type=output_type)
    generator_build = kwargs.get("generator_build") or legal_policy.get_generator_build(company=company)

    generated_by = kwargs.get("generated_by") or getattr(frappe.session, "user", None) or "Administrator"
    generated_at = kwargs.get("generated_at") or frappe.utils.now_datetime()

    # auto-link previous output if not supplied:
    if previous_output is None:
        # default: link to last output of same type for same ref
        previous_output = find_last_output_for_ref(
            company, reference_doctype, reference_name, output_type, correction_reason=None
        )

    src_hash = hash_obj(source)
    pay_hash = hash_obj(payload)

    submit = bool(kwargs.get("submit", True))

    doc = frappe.get_doc(
        {
            "doctype": "BH Legal Output",
            "company": company,
            "output_type": output_type,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "schema_version": schema_version,
            "generator_build": generator_build,
            "generated_by": generated_by,
            "generated_at": generated_at,
            "source_hash": src_hash,
            "payload_hash": pay_hash,
            "source_json": json.dumps(source, ensure_ascii=False, sort_keys=True),
            "payload_json": json.dumps(payload, ensure_ascii=False, sort_keys=True),
            "previous_output": previous_output,
            "correction_reason": correction_reason,
        }
    )


    # Forward-compat: some installs have extra audit fields.
    if doc.meta.has_field("payload_schema_version") and not doc.get("payload_schema_version"):
        doc.set("payload_schema_version", schema_version)
    with legal_emit_session():
        doc.insert(ignore_permissions=True)
        if submit and int(getattr(doc, "docstatus", 0) or 0) == 0:
            doc.submit()

    _append_log(
        "legal_chain.log",
        {
            "event": "LEGAL-EMIT",
            "action": "emit",
            "company": company,
            "ref_doctype": reference_doctype,
            "ref_name": reference_name,
            "out_name": doc.name,
            "details": {
                "output_type": output_type,
                "schema_version": schema_version,
                "generator_build": generator_build,
                "correction_reason": correction_reason,
                "previous_output": previous_output,
                "source_hash": src_hash,
                "payload_hash": pay_hash,
            },
        },
    )
    return doc.name