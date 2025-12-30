from __future__ import annotations

import json
from contextlib import contextmanager
import hashlib
import datetime as _dt
from typing import Any, Dict, Optional

import frappe

from blue_hesab.bh_core.legal_meta import get_schema_version, get_generator_build
from blue_hesab.bh_core.legal_audit import log_chain

from contextlib import contextmanager

def dumps_json(obj) -> str:
    """Deterministic JSON for hashing/storage (handles date/datetime)."""

    def _default(o):
        if isinstance(o, (_dt.date, _dt.datetime)):
            return o.isoformat()
        return str(o)

    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_default,
    )


def _safe_json_loads(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


@contextmanager
def _bh_legal_emit_flag():
    old = bool(getattr(frappe.flags, "bh_legal_emit", False))
    frappe.flags.bh_legal_emit = True
    try:
        yield
    finally:
        frappe.flags.bh_legal_emit = old


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
    correction_reason: str | None = None,   # None | "CANCEL" | "AMEND"
    previous_output: str | None = None,
    source: dict | None = None,
    payload: dict | None = None,
    event: str | None = None,
    schema_version: str | None = None,
    generator_build: str | None = None,
    generated_by: str | None = None,
    generated_at: str | None = None,
    amended_from: str | None = None,
) -> str:
    """Create BH Legal Output (submitted, immutable) via the official generator path only.

    LEGAL-08:
    - wraps insert/submit with frappe.flags.bh_legal_emit so BH Legal Output validate() can hard-block UI/manual writes.
    - auto builds payload for TTMS/MODIAN (skeleton), keeps VAT deterministic for now.
    """
    from blue_hesab.bh_core import legal_meta

    meta = legal_meta.get_legal_meta(schema_version=schema_version, generator_build=generator_build)
    schema_version = meta["schema_version"]
    generator_build = meta["generator_build"]
    generated_by = generated_by or frappe.session.user
    generated_at = generated_at or meta["generated_at"]

    if source is None:
        source = {"ref": {"doctype": reference_doctype, "name": reference_name}, "company": company, "output_type": output_type}

    # LEGAL-08 payload auto build for TTMS/MODIAN until real generators land
    if payload is None:
        if output_type in ("TTMS_EXPORT", "MODIAN_PAYLOAD"):
            try:
                from blue_hesab.bh_core.legal_payloads import build_legal_payload_v1
                ref_doc = frappe.get_doc(reference_doctype, reference_name)
                payload = build_legal_payload_v1(doc=ref_doc, output_type=output_type, correction_reason=correction_reason)
            except Exception:
                payload = {"type": output_type, "ref": {"doctype": reference_doctype, "name": reference_name}, "company": company}
        else:
            payload = {"type": output_type, "ref": {"doctype": reference_doctype, "name": reference_name}, "company": company}

    source_json = dumps_json(source)
    payload_json = dumps_json(payload)
    source_hash = hash_obj(source)
    payload_hash = hash_obj(payload)

    doc = frappe.new_doc("BH Legal Output")
    doc.company = company
    doc.output_type = output_type
    doc.reference_doctype = reference_doctype
    doc.reference_name = reference_name
    doc.schema_version = schema_version
    doc.generator_build = generator_build
    doc.generated_by = generated_by
    doc.generated_at = generated_at

    doc.correction_reason = correction_reason
    doc.previous_output = previous_output
    doc.amended_from = amended_from

    doc.source_json = source_json
    doc.payload_json = payload_json
    doc.source_hash = source_hash
    doc.payload_hash = payload_hash

    if hasattr(doc, "event"):
        setattr(doc, "event", event)

    # IMPORTANT: policy-lock bypass ONLY inside this context
    with _bh_legal_emit_flag():
        doc.insert(ignore_permissions=True)

        # submit if doctype is submittable (immutability)
        if int(frappe.get_meta(doc.doctype).is_submittable) == 1:
            doc.submit()

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
