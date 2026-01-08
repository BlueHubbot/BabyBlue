from __future__ import annotations

from typing import List, Optional, Union, Tuple
from contextlib import contextmanager

import frappe
from frappe.model.document import Document

from blue_hesab.bh_core.legal_meta import legal_emit_scope
from blue_hesab.bh_core.legal_output import create_legal_output
from blue_hesab.bh_core.legal_payloads import build_legal_payload_v1
from blue_hesab.bh_core import legal_policy


# -----------------------------------------------------------------------------
# Safe scope (handles old/new legal_emit_scope signatures)
# -----------------------------------------------------------------------------
@contextmanager
def _scope(company: str, doctype: str, name: str):
    try:
        with legal_emit_scope(company=company, doctype=doctype, name=name):
            yield
        return
    except TypeError:
        pass

    try:
        with legal_emit_scope(doctype, name):
            yield
        return
    except TypeError:
        pass

    # fallback: no scope
    yield


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _s(v) -> str:
    return (v or "").strip()


def _resolve_company(doc) -> str:
    return _s(getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None))


def _mk_source(doc) -> dict:
    return {
        "doctype": getattr(doc, "doctype", None),
        "name": getattr(doc, "name", None),
        "docstatus": getattr(doc, "docstatus", None),
    }


def _normalize_output_type(ot: Optional[str]) -> Optional[str]:
    if not ot:
        return ot
    ot = ot.strip()
    if ot == "TTMS":
        return "TTMS_EXPORT"
    if ot == "MODIAN":
        return "MODIAN_PAYLOAD"
    return ot


def _enabled_output_types(company: Optional[str] = None) -> List[str]:
    return legal_policy.enabled_output_types(company=company)


def _mk_payload(doc, ot: str, correction_reason: Optional[str]) -> Tuple[dict, list[dict]]:
    payload, attachments = build_legal_payload_v1(doc=doc, output_type=ot, correction_reason=correction_reason)
    return payload, attachments


def _attach_files_to_legal_output(out_name: str, attachments: list[dict]) -> None:
    """
    Attach files to BH Legal Output using File doctype.
    Must not mutate BH Legal Output (immutability triggers remain intact).
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
            f = frappe.get_doc(
                {
                    "doctype": "File",
                    "file_name": fn,
                    "is_private": is_private,
                    "attached_to_doctype": "BH Legal Output",
                    "attached_to_name": out_name,
                    "content": content,
                }
            )
            if mimetype:
                f.file_type = mimetype
            f.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(title="BH LEGAL attach failed", message=frappe.get_traceback())


def _existing_output_name(
    company: str,
    ref_doctype: str,
    ref_name: str,
    output_type: str,
    correction_reason: Optional[str],
) -> Optional[str]:
    return frappe.db.get_value(
        "BH Legal Output",
        {
            "company": company,
            "reference_doctype": ref_doctype,
            "reference_name": ref_name,
            "output_type": output_type,
            "correction_reason": correction_reason,
            "docstatus": 1,
        },
        "name",
    )


def _latest_output_name(
    company: str,
    ref_doctype: str,
    ref_name: str,
    output_type: str,
    correction_reason: Optional[str],
) -> Optional[str]:
    rows = frappe.get_all(
        "BH Legal Output",
        filters={
            "company": company,
            "reference_doctype": ref_doctype,
            "reference_name": ref_name,
            "output_type": output_type,
            "correction_reason": correction_reason,
            "docstatus": 1,
        },
        fields=["name"],
        order_by="creation desc",
        limit=1,
    )
    return rows[0]["name"] if rows else None


def _emit_one(
    *,
    doc: Document,
    company: str,
    output_type: str,
    correction_reason: Optional[str],
    previous_output: Optional[str],
    docstatus_override: Optional[int] = None,
) -> str:
    # idempotent: if already emitted, return existing (do NOT re-attach)
    existing = _existing_output_name(company, doc.doctype, doc.name, output_type, correction_reason)
    if existing:
        return existing

    payload, atts = _mk_payload(doc, output_type, correction_reason)

    out_name = create_legal_output(
        company=company,
        schema_version=legal_policy.get_schema_version(company=company),
        generator_build=legal_policy.get_generator_build(company=company),
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        source=_mk_source(doc),
        payload=payload,
        correction_reason=correction_reason,
        previous_output=previous_output,
        docstatus_override=docstatus_override,
        output_type=output_type,
    )
    _attach_files_to_legal_output(out_name, atts)
    return out_name


def _emit_issue(
    doc: Document,
    company: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    ot = _normalize_output_type(output_type)

    if ot:
        return _emit_one(
            doc=doc,
            company=company,
            output_type=ot,
            correction_reason=None,
            previous_output=None,
            docstatus_override=docstatus_override,
        )

    created: List[str] = []
    for ot2 in _enabled_output_types(company):
        created.append(
            _emit_one(
                doc=doc,
                company=company,
                output_type=ot2,
                correction_reason=None,
                previous_output=None,
                docstatus_override=docstatus_override,
            )
        )
    return created


def _emit_cancel(
    doc: Document,
    company: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    ot = _normalize_output_type(output_type)

    def prev_for(otx: str) -> Optional[str]:
        # CANCEL prev should point to ISSUE (same doc)
        return _latest_output_name(company, doc.doctype, doc.name, otx, None)

    if ot:
        return _emit_one(
            doc=doc,
            company=company,
            output_type=ot,
            correction_reason="CANCEL",
            previous_output=prev_for(ot),
            docstatus_override=docstatus_override,
        )

    created: List[str] = []
    for ot2 in _enabled_output_types(company):
        created.append(
            _emit_one(
                doc=doc,
                company=company,
                output_type=ot2,
                correction_reason="CANCEL",
                previous_output=prev_for(ot2),
                docstatus_override=docstatus_override,
            )
        )
    return created


def _emit_amend(
    doc: Document,
    company: Optional[str] = None,
    original: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    ot = _normalize_output_type(output_type)

    # original doc name (the one that SHOULD be cancelled before amendment)
    original = _s(original) or _s(getattr(doc, "amended_from", None))
    if not original:
        # No original -> nothing to chain against; still emit AMEND as standalone (rare)
        original = doc.name

    def prev_for(otx: str) -> Optional[str]:
        # AMEND prev should point to CANCEL of the ORIGINAL doc (preferred),
        # fallback to ISSUE of the ORIGINAL doc.
        prev_cancel = _latest_output_name(company, doc.doctype, original, otx, "CANCEL")
        if prev_cancel:
            return prev_cancel
        return _latest_output_name(company, doc.doctype, original, otx, None)

    if ot:
        return _emit_one(
            doc=doc,
            company=company,
            output_type=ot,
            correction_reason="AMEND",
            previous_output=prev_for(ot),
            docstatus_override=docstatus_override,
        )

    created: List[str] = []
    for ot2 in _enabled_output_types(company):
        created.append(
            _emit_one(
                doc=doc,
                company=company,
                output_type=ot2,
                correction_reason="AMEND",
                previous_output=prev_for(ot2),
                docstatus_override=docstatus_override,
            )
        )
    return created


# -----------------------------------------------------------------------------
# Doc Event handlers (called by hooks.py)
# -----------------------------------------------------------------------------
def on_submit_sales_invoice(doc: Document, method=None):
    company = _resolve_company(doc)
    with _scope(company, doc.doctype, doc.name):
        _emit_issue(doc, company=company)
        if _s(doc.get("amended_from") if hasattr(doc, "get") else getattr(doc, "amended_from", None)):
            _emit_amend(doc, company=company, original=_s(doc.amended_from))


def on_cancel_sales_invoice(doc: Document, method=None, *args, **kwargs):
    company = _resolve_company(doc)
    with _scope(company, doc.doctype, doc.name):
        _emit_cancel(doc, company=company)


def on_update_after_submit_sales_invoice(doc: Document, method=None, *args, **kwargs):
    # immutable by design; amendments handled via amended docs
    return


def on_submit_purchase_invoice(doc: Document, method=None):
    company = _resolve_company(doc)
    with _scope(company, doc.doctype, doc.name):
        _emit_issue(doc, company=company)
        if _s(doc.get("amended_from") if hasattr(doc, "get") else getattr(doc, "amended_from", None)):
            _emit_amend(doc, company=company, original=_s(doc.amended_from))


def on_cancel_purchase_invoice(doc: Document, method=None, *args, **kwargs):
    company = _resolve_company(doc)
    with _scope(company, doc.doctype, doc.name):
        _emit_cancel(doc, company=company)


def on_update_after_submit_purchase_invoice(doc: Document, method=None, *args, **kwargs):
    return
