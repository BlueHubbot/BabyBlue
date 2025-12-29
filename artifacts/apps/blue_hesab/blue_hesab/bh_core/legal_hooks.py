from __future__ import annotations

from typing import Optional, Dict, Any

import frappe

from blue_hesab.bh_core.legal_output import (
    create_legal_output,
    get_latest_output_for_ref,
    build_source_minimal,
)

OUTPUT_TYPE_VAT = "VAT_INVOICE"


def _company(doc) -> str:
    return getattr(doc, "company", None) or frappe.db.get_value(doc.doctype, doc.name, "company")


def _emit_issue(doc, *, output_type: str):
    company = _company(doc)

    # If this is an AMEND doc (doc.amended_from exists), route to amend emission
    if getattr(doc, "amended_from", None):
        return _emit_amend(doc, output_type=output_type)

    # de-dup: if already issued, return last ISSUE
    latest = get_latest_output_for_ref(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason=None,
    )
    if latest:
        return latest["name"]

    source = build_source_minimal(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        event="ON_SUBMIT",
        correction_reason=None,
        previous_output=None,
        amended_from=None,
        docstatus=getattr(doc, "docstatus", None),
    )

    return create_legal_output(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason=None,
        previous_output=None,
        source=source,
        event="ON_SUBMIT",
    )


def _emit_cancel(doc, *, output_type: str):
    company = _company(doc)

    # de-dup: if already emitted CANCEL, return it
    latest_cancel = get_latest_output_for_ref(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason="CANCEL",
    )
    if latest_cancel:
        return latest_cancel["name"]

    latest_any = get_latest_output_for_ref(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason=None,
    ) or get_latest_output_for_ref(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason="AMEND",
    )

    if not latest_any:
        # if issue never created, create issue then cancel (should be rare)
        _emit_issue(doc, output_type=output_type)
        latest_any = get_latest_output_for_ref(
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            company=company,
            output_type=output_type,
            correction_reason=None,
        )

    prev = latest_any["name"] if latest_any else None

    source = build_source_minimal(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        event="BEFORE_CANCEL",
        correction_reason="CANCEL",
        previous_output=prev,
        amended_from=getattr(doc, "amended_from", None),
        docstatus=getattr(doc, "docstatus", None),
    )

    return create_legal_output(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason="CANCEL",
        previous_output=prev,
        source=source,
        event="BEFORE_CANCEL",
    )


def _emit_amend(doc, *, output_type: str):
    company = _company(doc)
    original = getattr(doc, "amended_from", None)
    if not original:
        return _emit_issue(doc, output_type=output_type)

    # AMEND must chain from original CANCEL output
    cancel_out = get_latest_output_for_ref(
        reference_doctype=doc.doctype,
        reference_name=original,
        company=company,
        output_type=output_type,
        correction_reason="CANCEL",
    )
    if not cancel_out:
        frappe.throw(f"برای سند اصلاحی، خروجی اصلاح/ابطال پیدا نشد. ابتدا سند اصلی ({original}) باید ابطال شود.")

    # de-dup: if amended already has AMEND output, return it
    latest_amend = get_latest_output_for_ref(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason="AMEND",
    )
    if latest_amend:
        return latest_amend["name"]

    source = build_source_minimal(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        event="ON_SUBMIT",
        correction_reason="AMEND",
        previous_output=cancel_out["name"],
        amended_from=original,
        docstatus=getattr(doc, "docstatus", None),
    )

    return create_legal_output(
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        company=company,
        output_type=output_type,
        correction_reason="AMEND",
        previous_output=cancel_out["name"],
        source=source,
        event="ON_SUBMIT",
    )


# ---- DocType hooks ----
def on_submit_sales_invoice(doc, method=None):
    return _emit_issue(doc, output_type=OUTPUT_TYPE_VAT)

def on_submit_purchase_invoice(doc, method=None):
    return _emit_issue(doc, output_type=OUTPUT_TYPE_VAT)

def before_cancel_sales_invoice(doc, method=None):
    return _emit_cancel(doc, output_type=OUTPUT_TYPE_VAT)

def before_cancel_purchase_invoice(doc, method=None):
    return _emit_cancel(doc, output_type=OUTPUT_TYPE_VAT)

# optional no-op (in case hooks reference on_cancel)
def on_cancel_sales_invoice(doc, method=None):
    return None

def on_cancel_purchase_invoice(doc, method=None):
    return None
