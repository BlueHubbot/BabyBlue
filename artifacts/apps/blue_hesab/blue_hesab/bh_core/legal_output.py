from __future__ import annotations

import json
from contextlib import contextmanager
import hashlib
import datetime as _dt
from typing import Any, Dict, Optional

import frappe

from blue_hesab.bh_core.legal_meta import get_schema_version, get_generator_build
from blue_hesab.bh_core.legal_audit import log_chain


@contextmanager
def bh_legal_emit_context():
    """Allow internal creation/submit of BH Legal Output."""
    prev = getattr(frappe.flags, "bh_legal_emit", False)
    frappe.flags.bh_legal_emit = True
    try:
        yield
    finally:
        frappe.flags.bh_legal_emit = prev


def _json_default(o: Any):
    if isinstance(o, (_dt.datetime, _dt.date)):
        return o.isoformat()
    if hasattr(o, "as_dict"):
        try:
            return o.as_dict()
        except Exception:
            pass
    return str(o)


def _stable_dumps(obj: Any) -> str:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    )


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_obj(obj: Any) -> str:
    return _sha256_hex(_stable_dumps(obj))


def _now_ts() -> str:
    return frappe.utils.now()


def _session_user() -> str:
    try:
        u = getattr(frappe, "session", None) and frappe.session.user
        return u or "Administrator"
    except Exception:
        return "Administrator"


def build_source_minimal(
    *,
    reference_doctype: str,
    reference_name: str,
    company: str,
    output_type: str,
    event: Optional[str] = None,
    correction_reason: Optional[str] = None,
    previous_output: Optional[str] = None,
    amended_from: Optional[str] = None,
    docstatus: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "company": company,
        "output_type": output_type,
        "event": event,
        "correction_reason": correction_reason,
        "previous_output": previous_output,
        "amended_from": amended_from,
        "docstatus": docstatus,
    }


def _set_if_field(doc, fieldname: str, value: Any):
    if not value and value not in (0, False):
        return
    try:
        if doc.meta.has_field(fieldname):
            setattr(doc, fieldname, value)
    except Exception:
        return


def create_legal_output(
    *,
    reference_doctype: str,
    reference_name: str,
    company: str,
    output_type: str,
    correction_reason: Optional[str] = None,
    previous_output: Optional[str] = None,
    # LEGAL-06 introduced source kw-only; keep it OPTIONAL for backward compatibility
    source: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    # legacy callers used event=...; accept it (ignored if not needed)
    event: Optional[str] = None,
    # allow explicit override; otherwise derive from VERSION/git
    schema_version: Optional[str] = None,
    generator_build: Optional[str] = None,
    generated_at: Optional[str] = None,
    generated_by: Optional[str] = None,
    # ignore any historical/stray kwargs safely
    **_ignored,
) -> str:
    schema_version = schema_version or get_schema_version()
    generator_build = generator_build or get_generator_build()
    generated_at = generated_at or _now_ts()
    generated_by = generated_by or _session_user()

    if source is None:
        # minimum stable source (so we never crash because source is missing)
        amended_from = None
        docstatus = None
        try:
            if reference_doctype and reference_name:
                docstatus = frappe.db.get_value(reference_doctype, reference_name, "docstatus")
                amended_from = frappe.db.get_value(reference_doctype, reference_name, "amended_from")
        except Exception:
            pass

        source = build_source_minimal(
            reference_doctype=reference_doctype,
            reference_name=reference_name,
            company=company,
            output_type=output_type,
            event=event,
            correction_reason=correction_reason,
            previous_output=previous_output,
            amended_from=amended_from,
            docstatus=docstatus,
        )

    if payload is None:
        # until we formalize VAT payload v1, keep payload deterministic (at least)
        payload = {"type": output_type, "ref": {"doctype": reference_doctype, "name": reference_name}, "company": company}

    source_hash = hash_obj(source)
    payload_hash = hash_obj(payload)

    doc = frappe.new_doc("BH Legal Output")

    _set_if_field(doc, "company", company)
    _set_if_field(doc, "reference_doctype", reference_doctype)
    _set_if_field(doc, "reference_name", reference_name)
    _set_if_field(doc, "output_type", output_type)

    _set_if_field(doc, "correction_reason", correction_reason)
    _set_if_field(doc, "previous_output", previous_output)

    _set_if_field(doc, "schema_version", schema_version)
    _set_if_field(doc, "generator_build", generator_build)
    _set_if_field(doc, "generated_at", generated_at)
    _set_if_field(doc, "generated_by", generated_by)

    _set_if_field(doc, "source_hash", source_hash)
    _set_if_field(doc, "payload_hash", payload_hash)

    # optional storage fields (depending on doctype schema)
    src_json = _stable_dumps(source)
    pay_json = _stable_dumps(payload)

    for f in ("source_json", "source", "source_payload", "source_data"):
        _set_if_field(doc, f, src_json)
    for f in ("payload_json", "payload", "payload_data"):
        _set_if_field(doc, f, pay_json)

    with bh_legal_emit_context():
        doc.insert(ignore_permissions=True)

        # submit if doctype is submittable (immutability)
        try:
            if getattr(doc.meta, "is_submittable", 0) and doc.docstatus == 0:
                doc.submit()
        except Exception:
            # if not submittable or submit blocked, leave inserted (docstatus=0)
            pass

    try:
        log_chain(
            "emit",
            ref_doctype=getattr(doc, "reference_doctype", None),
            ref_name=getattr(doc, "reference_name", None),
            out_name=doc.name,
            details={
                "output_type": getattr(doc, "output_type", None),
                "correction_reason": getattr(doc, "correction_reason", None),
            },
        )
    except Exception:
        pass

    return doc.name


def get_latest_output_for_ref(
    *,
    reference_doctype: str,
    reference_name: str,
    company: str,
    output_type: str,
    correction_reason: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    filters = {
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "company": company,
        "output_type": output_type,
    }
    if correction_reason is None:
        pass
    else:
        filters["correction_reason"] = correction_reason

    rows = frappe.get_all(
        "BH Legal Output",
        filters=filters,
        fields=["name", "output_type", "correction_reason", "previous_output", "schema_version", "generator_build", "modified", "generated_at"],
        order_by="modified desc",
        limit=1,
    )
    return rows[0] if rows else None
