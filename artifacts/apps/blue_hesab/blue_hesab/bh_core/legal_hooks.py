# -*- coding: utf-8 -*-
"""
Doc-event hooks + internal emit helpers for regress.

Regress scripts import:
  from blue_hesab.bh_core.legal_hooks import _emit_issue, _emit_cancel
So these names must exist and be stable.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import frappe

from blue_hesab.bh_core.legal_policy import (
    CORR_AMEND,
    CORR_CANCEL,
    OUT_MODIAN_PAYLOAD,
    OUT_TTMS_EXPORT,
    OUT_VAT_INVOICE,
    get_enabled_outputs,
)
from blue_hesab.bh_core.legal_output import create_legal_output
from blue_hesab.bh_core.legal_repo import find_last_output_for_ref


def _emit_for_ref(
    company: str,
    reference_doctype: str,
    reference_name: str,
    correction_reason: Optional[str] = None,
    previous_reference_name: Optional[str] = None,
) -> Dict[str, str]:
    enabled = get_enabled_outputs(company, reference_doctype)
    out: Dict[str, str] = {}
    for output_type in enabled:
        # idempotency for CANCEL: do not re-create if exists
        if (correction_reason or "").upper() == CORR_CANCEL:
            existing = find_last_output_for_ref(reference_doctype, reference_name, output_type=output_type, correction_reason=CORR_CANCEL)
            if existing:
                out[output_type] = existing["name"]
                continue

        kwargs = dict(
            company=company,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
            output_type=output_type,
            correction_reason=correction_reason,
        )

        # AMEND: previous_output should point to last CANCEL of original invoice
        if (correction_reason or "").upper() == CORR_AMEND and previous_reference_name:
            kwargs["previous_reference_doctype"] = reference_doctype
            kwargs["previous_reference_name"] = previous_reference_name

        out[output_type] = create_legal_output(**kwargs)
    return out


def _emit_issue(reference_doctype: str, reference_name: str, company: str) -> str:
    outs = _emit_for_ref(company, reference_doctype, reference_name, correction_reason=None)
    return outs.get(OUT_VAT_INVOICE) or next(iter(outs.values()))


def _emit_cancel(reference_doctype: str, reference_name: str, company: str) -> str:
    outs = _emit_for_ref(company, reference_doctype, reference_name, correction_reason=CORR_CANCEL)
    return outs.get(OUT_VAT_INVOICE) or next(iter(outs.values()))


def _emit_amend(reference_doctype: str, amended_name: str, original_name: str, company: str) -> str:
    outs = _emit_for_ref(company, reference_doctype, amended_name, correction_reason=CORR_AMEND, previous_reference_name=original_name)
    return outs.get(OUT_VAT_INVOICE) or next(iter(outs.values()))


# Optional: wire into Frappe hooks (doc_events) if you want.
def sales_invoice_on_submit(doc, method=None):
    company = getattr(doc, "company", None) or frappe.db.get_value("Company", {"name": ["!=", ""]}, "name")
    if getattr(doc, "amended_from", None):
        _emit_amend("Sales Invoice", doc.name, doc.amended_from, company)
    else:
        _emit_issue("Sales Invoice", doc.name, company)


def sales_invoice_on_cancel(doc, method=None):
    company = getattr(doc, "company", None) or frappe.db.get_value("Company", {"name": ["!=", ""]}, "name")
    _emit_cancel("Sales Invoice", doc.name, company)


def purchase_invoice_on_submit(doc, method=None):
    company = getattr(doc, "company", None) or frappe.db.get_value("Company", {"name": ["!=", ""]}, "name")
    if getattr(doc, "amended_from", None):
        _emit_amend("Purchase Invoice", doc.name, doc.amended_from, company)
    else:
        _emit_issue("Purchase Invoice", doc.name, company)


def purchase_invoice_on_cancel(doc, method=None):
    company = getattr(doc, "company", None) or frappe.db.get_value("Company", {"name": ["!=", ""]}, "name")
    _emit_cancel("Purchase Invoice", doc.name, company)
