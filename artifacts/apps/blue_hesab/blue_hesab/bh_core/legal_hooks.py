from __future__ import annotations

import json
from typing import List, Optional, Union

import frappe

from blue_hesab.bh_core.legal_meta import legal_emit_scope
from blue_hesab.bh_core.legal_output import create_legal_output
from blue_hesab.bh_core.legal_payloads import build_legal_payload_v1
from blue_hesab.bh_core import legal_policy


def _resolve_company(doc) -> str:
    return (getattr(doc, "company", None) or "").strip()


def _mk_source(doc) -> dict:
    return {
        "doctype": getattr(doc, "doctype", None),
        "name": getattr(doc, "name", None),
        "docstatus": getattr(doc, "docstatus", None),
    }


def _normalize_output_type(ot: str | None) -> str | None:
    if not ot:
        return ot
    ot = ot.strip()
    # keep backward-compat with older regress calls
    if ot == "TTMS":
        return "TTMS_EXPORT"
    if ot == "MODIAN":
        return "MODIAN_PAYLOAD"
    return ot


def _enabled_output_types(company: Optional[str] = None) -> List[str]:
    return legal_policy.enabled_output_types(company=company)


def _mk_payload(doc, ot: str, correction_reason: str | None) -> tuple[dict, list[dict]]:
    payload, attachments = build_legal_payload_v1(doc=doc, output_type=ot, correction_reason=correction_reason)
    return payload, attachments


def _attach_files_to_legal_output(out_name: str, attachments: list[dict]) -> None:
    """
    Attach files to BH Legal Output using File doctype.
    No update to BH Legal Output itself (so immutability triggers remain intact).
    """
    if not out_name or not attachments:
        return

    for a in attachments:
        fn = a.get("filename")
        content = a.get("content")
        mimetype = a.get("mimetype") or None
        is_private = int(a.get("is_private", 1) or 1)

        if not fn or content is None:
            continue

        try:
            f = frappe.get_doc({
                "doctype": "File",
                "file_name": fn,
                "is_private": is_private,
                "attached_to_doctype": "BH Legal Output",
                "attached_to_name": out_name,
                "content": content,
            })
            if mimetype:
                f.file_type = mimetype
            f.insert(ignore_permissions=True)
        except Exception:
            # do not break legal chain if attachment fails
            frappe.log_error(title="BH LEGAL attach failed", message=frappe.get_traceback())


def _emit_issue(
    doc,
    company: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    ot = _normalize_output_type(output_type)

    if ot:
        payload, atts = _mk_payload(doc, ot, correction_reason=None)
        out = create_legal_output(
            company=company,
            schema_version=legal_policy.get_schema_version(company=company),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=payload,
            correction_reason=None,
            previous_output=None,
            docstatus_override=docstatus_override,
            output_type=ot,
        )
        _attach_files_to_legal_output(out, atts)
        return out

    created: List[str] = []
    for ot in _enabled_output_types(company):
        payload, atts = _mk_payload(doc, ot, correction_reason=None)
        out = create_legal_output(
            company=company,
            schema_version=legal_policy.get_schema_version(company=company),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=payload,
            correction_reason=None,
            previous_output=None,
            docstatus_override=docstatus_override,
            output_type=ot,
        )
        _attach_files_to_legal_output(out, atts)
        created.append(out)
    return created


def _emit_cancel(
    doc,
    company: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    ot = _normalize_output_type(output_type)

    if ot:
        payload, atts = _mk_payload(doc, ot, correction_reason="CANCEL")
        out = create_legal_output(
            company=company,
            schema_version=legal_policy.get_schema_version(company=company),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=payload,
            correction_reason="CANCEL",
            previous_output=None,
            docstatus_override=docstatus_override,
            output_type=ot,
        )
        _attach_files_to_legal_output(out, atts)
        return out

    created: List[str] = []
    for ot in _enabled_output_types(company):
        payload, atts = _mk_payload(doc, ot, correction_reason="CANCEL")
        out = create_legal_output(
            company=company,
            schema_version=legal_policy.get_schema_version(company=company),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=payload,
            correction_reason="CANCEL",
            previous_output=None,
            docstatus_override=docstatus_override,
            output_type=ot,
        )
        _attach_files_to_legal_output(out, atts)
        created.append(out)
    return created


def _emit_amend(
    doc,
    company: Optional[str] = None,
    original: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    ot = _normalize_output_type(output_type)
    original = original or getattr(doc, "amended_from", None) or getattr(doc, "name", None) or doc.name

    if ot:
        payload, atts = _mk_payload(doc, ot, correction_reason="AMEND")
        out = create_legal_output(
            company=company,
            schema_version=legal_policy.get_schema_version(company=company),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=payload,
            correction_reason="AMEND",
            previous_output=None,
            docstatus_override=docstatus_override,
            output_type=ot,
        )
        _attach_files_to_legal_output(out, atts)
        return out

    created: List[str] = []
    for ot in _enabled_output_types(company):
        payload, atts = _mk_payload(doc, ot, correction_reason="AMEND")
        out = create_legal_output(
            company=company,
            schema_version=legal_policy.get_schema_version(company=company),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=payload,
            correction_reason="AMEND",
            previous_output=None,
            docstatus_override=docstatus_override,
            output_type=ot,
        )
        _attach_files_to_legal_output(out, atts)
        created.append(out)
    return created


# ---- Doc Event handlers (expected by hooks.py) ----

def on_submit_sales_invoice(doc, method=None, *args, **kwargs):
    with legal_emit_scope("Sales Invoice", doc.name):
        _emit_issue(doc)


def on_cancel_sales_invoice(doc, method=None, *args, **kwargs):
    with legal_emit_scope("Sales Invoice", doc.name):
        _emit_cancel(doc)


def on_update_after_submit_sales_invoice(doc, method=None, *args, **kwargs):
    # no-op (immutable); amendments handled via amended docs
    return


def on_submit_purchase_invoice(doc, method=None, *args, **kwargs):
    with legal_emit_scope("Purchase Invoice", doc.name):
        _emit_issue(doc)


def on_cancel_purchase_invoice(doc, method=None, *args, **kwargs):
    with legal_emit_scope("Purchase Invoice", doc.name):
        _emit_cancel(doc)
