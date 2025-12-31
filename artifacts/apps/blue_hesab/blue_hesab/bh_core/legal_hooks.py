# -*- coding: utf-8 -*-
"""
Frappe Doc Event handlers + emit helpers for legal outputs.

Regress suites depend on these public symbols (keep stable):
- on_submit_sales_invoice / on_cancel_sales_invoice
- on_submit_purchase_invoice / on_cancel_purchase_invoice
- _emit_issue / _emit_cancel / _emit_amend
- _enabled_output_types

Important behavioral contract (for regress):
- If output_type is provided -> return a SINGLE output name (str)
- Otherwise -> return list[str] (multiple output types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import frappe

from blue_hesab.bh_core import legal_policy, legal_payloads
from blue_hesab.bh_core.legal_output import create_legal_output
from blue_hesab.bh_core.legal_repo import find_last_output_for_ref


__BH_LEGAL_HOOKS_VER__ = "LEGAL-HOOKS-V10"


def _resolve_company(doc) -> str:
    # Source of truth: doc.company for SI/PI
    c = getattr(doc, "company", None) or getattr(doc, "company_name", None)
    if c:
        return c

    # Fallback: BH Settings default company
    try:
        s = frappe.get_single("BH Settings")
        dc = getattr(s, "default_company", None)
        if dc:
            return dc
    except Exception:
        pass

    # Last fallback (safe default for regress/dev)
    return "BlueAPi"


def _enabled_output_types(company: Optional[str] = None) -> List[str]:
    return legal_policy.enabled_output_types(company=company)


def _mk_source(doc) -> Dict[str, Any]:
    return {
        "doctype": doc.doctype,
        "name": doc.name,
        "amended_from": getattr(doc, "amended_from", None),
        "docstatus": int(getattr(doc, "docstatus", 0) or 0),
        "modified": str(getattr(doc, "modified", "")),
    }


def _mk_payload(doc, output_type: str, correction_reason: Optional[str]):
    # build_legal_payload_v1 is keyword-only => doc MUST be passed as keyword
    return legal_payloads.build_legal_payload_v1(
        doc=doc,
        output_type=output_type,
        correction_reason=correction_reason,
    )


def _emit_issue(
    doc,
    company: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)

    # If caller requests a single output type, return str (regress expects this).
    if output_type:
        ot = output_type
        out_name = create_legal_output(
            company=company,
            output_type=ot,
            schema_version=legal_policy.get_schema_version(company=company, output_type=ot),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            source=_mk_source(doc),
            payload=_mk_payload(doc, ot, correction_reason=None),
            correction_reason=None,
            previous_output=None,
        )
        return out_name

    # Otherwise emit for all enabled output types (return list[str])
    created: List[str] = []
    for ot in _enabled_output_types(company):
        created.append(
            create_legal_output(
                company=company,
                output_type=ot,
                schema_version=legal_policy.get_schema_version(company=company, output_type=ot),
                generator_build=legal_policy.get_generator_build(company=company),
                reference_doctype=doc.doctype,
                reference_name=doc.name,
                source=_mk_source(doc),
                payload=_mk_payload(doc, ot, correction_reason=None),
                correction_reason=None,
                previous_output=None,
            )
        )
    return created


def _emit_cancel(
    doc,
    company: Optional[str] = None,
    *,
    output_type: Optional[str] = None,
    original: Optional[str] = None,
    docstatus_override: Optional[int] = None,
) -> Union[str, List[str]]:
    company = company or _resolve_company(doc)
    original = original or getattr(doc, "name", None)

    if not original:
        # should never happen, but keep safe
        original = doc.name

    # Single output type => str
    if output_type:
        ot = output_type

        # 1) idempotent: if CANCEL already exists, return it (do NOT create again)
        existing_cancel = find_last_output_for_ref(
            company=company,
            reference_doctype=doc.doctype,
            reference_name=original,
            output_type=ot,
            correction_reason="CANCEL",
        )
        if existing_cancel:
            return existing_cancel

        # 2) chain: CANCEL should link to latest ISSUE (correction_reason=None)
        prev_issue = find_last_output_for_ref(
            company=company,
            reference_doctype=doc.doctype,
            reference_name=original,
            output_type=ot,
            correction_reason=None,
        )

        out_name = create_legal_output(
            company=company,
            output_type=ot,
            schema_version=legal_policy.get_schema_version(company=company, output_type=ot),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=original,
            source=_mk_source(doc),
            payload=_mk_payload(doc, ot, correction_reason="CANCEL"),
            correction_reason="CANCEL",
            previous_output=prev_issue,
            submit=True,
        )
        return out_name

    # Multi output types => list[str]
    created: List[str] = []
    for ot in _enabled_output_types(company):
        existing_cancel = find_last_output_for_ref(
            company=company,
            reference_doctype=doc.doctype,
            reference_name=original,
            output_type=ot,
            correction_reason="CANCEL",
        )
        if existing_cancel:
            created.append(existing_cancel)
            continue

        prev_issue = find_last_output_for_ref(
            company=company,
            reference_doctype=doc.doctype,
            reference_name=original,
            output_type=ot,
            correction_reason=None,
        )

        created.append(
            create_legal_output(
                company=company,
                output_type=ot,
                schema_version=legal_policy.get_schema_version(company=company, output_type=ot),
                generator_build=legal_policy.get_generator_build(company=company),
                reference_doctype=doc.doctype,
                reference_name=original,
                source=_mk_source(doc),
                payload=_mk_payload(doc, ot, correction_reason="CANCEL"),
                correction_reason="CANCEL",
                previous_output=prev_issue,
                submit=True,
            )
        )

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
    original = original or getattr(doc, "amended_from", None) or getattr(doc, "name", None)

    if not original:
        original = doc.name

    # Single output type => str (regress expects this)
    if output_type:
        ot = output_type
        prev_cancel = find_last_output_for_ref(
            company=company,
            reference_doctype=doc.doctype,
            reference_name=original,
            output_type=ot,
            correction_reason="CANCEL",
        )

        out_name = create_legal_output(
            company=company,
            output_type=ot,
            schema_version=legal_policy.get_schema_version(company=company, output_type=ot),
            generator_build=legal_policy.get_generator_build(company=company),
            reference_doctype=doc.doctype,
            reference_name=doc.name,  # new amended document
            source=_mk_source(doc),
            payload=_mk_payload(doc, ot, correction_reason="AMEND"),
            correction_reason="AMEND",
            previous_output=prev_cancel,
        )
        return out_name

    # Multi output types => list[str]
    created: List[str] = []
    for ot in _enabled_output_types(company):
        prev_cancel = find_last_output_for_ref(
            company=company,
            reference_doctype=doc.doctype,
            reference_name=original,
            output_type=ot,
            correction_reason="CANCEL",
        )
        created.append(
            create_legal_output(
                company=company,
                output_type=ot,
                schema_version=legal_policy.get_schema_version(company=company, output_type=ot),
                generator_build=legal_policy.get_generator_build(company=company),
                reference_doctype=doc.doctype,
                reference_name=doc.name,
                source=_mk_source(doc),
                payload=_mk_payload(doc, ot, correction_reason="AMEND"),
                correction_reason="AMEND",
                previous_output=prev_cancel,
            )
        )
    return created


# ---- Doc Event handlers (names expected by regress and hooks.py) ----

def on_submit_sales_invoice(doc, method: Optional[str] = None):
    company = _resolve_company(doc)
    if getattr(doc, "amended_from", None):
        return _emit_amend(doc, company=company)
    return _emit_issue(doc, company=company)


def before_cancel_sales_invoice(doc, method: Optional[str] = None):
    # Placeholder (some hooks/regress expect it to exist)
    return


def on_cancel_sales_invoice(doc, method: Optional[str] = None):
    company = _resolve_company(doc)
    return _emit_cancel(doc, company=company)


def on_submit_purchase_invoice(doc, method: Optional[str] = None):
    company = _resolve_company(doc)
    if getattr(doc, "amended_from", None):
        return _emit_amend(doc, company=company)
    return _emit_issue(doc, company=company)


def before_cancel_purchase_invoice(doc, method: Optional[str] = None):
    # Placeholder (some hooks/regress expect it to exist)
    return


def on_cancel_purchase_invoice(doc, method: Optional[str] = None):
    company = _resolve_company(doc)
    return _emit_cancel(doc, company=company)


# ---- Backwards-compatible aliases (if older hooks used different names) ----
sales_invoice_on_submit = on_submit_sales_invoice
purchase_invoice_on_submit = on_submit_purchase_invoice
