# -*- coding: utf-8 -*-
"""
Legal / Compliance exports built on top of VAT Core.

Important:
- Output is PER-COMPANY and must be reproducible/auditable.
- We generate BH Legal Output records (immutable after submit).
"""

from __future__ import annotations

import json
import frappe
from frappe.utils import now_datetime

from blue_hesab.bh_core.legal_output import create_legal_output

def _legal_output_to_dict(out):
    # create_legal_output returns "name" (str) by design in your codebase
    if hasattr(out, "as_dict"):
        return _legal_output_to_dict(out)
    if isinstance(out, str):
        try:
            return frappe.get_doc("BH Legal Output", out).as_dict()
        except Exception:
            return {"name": out}
    return {"value": out}


def _as_source_for_period(period) -> dict:
    src = {
        "doctype": "BH VAT Period",
        "name": period.name,
        "company": period.company,
        "status": period.status,
        "start": str(period.period_start_date),
        "end": str(period.period_end_date),
        "settlement_journal_entry": period.settlement_journal_entry,
        "source_hash": period.source_hash,
        "payload_hash": period.payload_hash,
    }
    # snapshot_json may be large; keep as parsed json for reproducibility
    if getattr(period, "snapshot_json", None):
        try:
            src["snapshot"] = json.loads(period.snapshot_json)
        except Exception:
            src["snapshot_json_raw"] = period.snapshot_json
    return src


def emit_vat_return_for_period(period_name: str, *, schema_version: str = "VATRET-01", generator_build: str | None = None, submit: int = 1) -> dict:
    """
    Build a VAT Return payload from BH VAT Period totals + snapshot and persist it as BH Legal Output (VAT_RETURN).
    """
    period = frappe.get_doc("BH VAT Period", period_name)

    payload = {
        "schema_version": schema_version,
        "company": period.company,
        "period": {
            "name": period.name,
            "start": str(period.period_start_date),
            "end": str(period.period_end_date),
            "status": period.status,
        },
        "totals": {
            "sales_vat_total": float(period.sales_vat_total or 0),
            "purchase_vat_total": float(period.purchase_vat_total or 0),
            "net_payable": float(period.net_payable or 0),
            "net_receivable": float(period.net_receivable or 0),
        },
        "settlement_journal_entry": period.settlement_journal_entry,
        "generated_at": str(now_datetime()),
        "generated_by": frappe.session.user,
    }

    out = create_legal_output(
        company=period.company,
        output_type="VAT_RETURN",
        schema_version=schema_version,
        generator_build=generator_build or schema_version,
        reference_doctype="BH VAT Period",
        reference_name=period.name,
        source=_as_source_for_period(period),
        payload=payload,
        submit=int(submit or 0),
    )
    return _legal_output_to_dict(out)



def emit_ttms_vat_report_for_period(period_name: str, *, schema_version: str = "TTMSVAT-00", generator_build: str | None = None, submit: int = 0) -> dict:
    """
    Phase-A placeholder: TTMS report payload (normalized) sourced from BH VAT Period.
    In later phases this function will be upgraded to the official TTMS format.
    """
    period = frappe.get_doc("BH VAT Period", period_name)

    payload = {
        "schema_version": schema_version,
        "format": "BH-TTMS-NORMALIZED-V1",
        "company": period.company,
        "period": {
            "name": period.name,
            "start": str(period.period_start_date),
            "end": str(period.period_end_date),
        },
        "totals": {
            "sales_vat_total": float(period.sales_vat_total or 0),
            "purchase_vat_total": float(period.purchase_vat_total or 0),
            "net_payable": float(period.net_payable or 0),
            "net_receivable": float(period.net_receivable or 0),
        },
        "notes": [
            "این خروجی هنوز «فرمت رسمی TTMS» نیست؛ فعلاً دیتاست نرمال‌شده برای فاز بعدی است."
        ],
        "generated_at": str(now_datetime()),
        "generated_by": frappe.session.user,
    }

    out = create_legal_output(
        company=period.company,
        output_type="TTMS_VAT_REPORT",
        schema_version=schema_version,
        generator_build=generator_build or schema_version,
        reference_doctype="BH VAT Period",
        reference_name=period.name,
        source=_as_source_for_period(period),
        payload=payload,
        submit=int(submit or 0),
    )
    return _legal_output_to_dict(out)



def emit_modian_e_invoice_stub(sales_invoice_name: str, *, schema_version: str = "MODIAN-00", generator_build: str | None = None, submit: int = 0) -> dict:
    """
    Phase-A placeholder: normalized Modian e-invoice payload from Sales Invoice (not official schema).
    """
    si = frappe.get_doc("Sales Invoice", sales_invoice_name)

    items = []
    for row in (si.get("items") or []):
        items.append({
            "item_code": row.get("item_code"),
            "item_name": row.get("item_name"),
            "qty": float(row.get("qty") or 0),
            "rate": float(row.get("rate") or 0),
            "amount": float(row.get("amount") or 0),
            "item_tax_template": row.get("item_tax_template"),
        })

    payload = {
        "schema_version": schema_version,
        "format": "BH-MODIAN-NORMALIZED-V1",
        "company": si.company,
        "sales_invoice": {
            "name": si.name,
            "posting_date": str(si.posting_date),
            "customer": si.customer,
            "grand_total": float(si.grand_total or 0),
            "net_total": float(si.net_total or 0),
            "total_taxes_and_charges": float(si.total_taxes_and_charges or 0),
            "bh_vat_price_mode": si.get("bh_vat_price_mode"),
        },
        "items": items,
        "notes": [
            "این خروجی هنوز «اسکیما رسمی مودیان» نیست؛ فعلاً دیتاست نرمال‌شده برای فاز بعدی است."
        ],
        "generated_at": str(now_datetime()),
        "generated_by": frappe.session.user,
    }

    out = create_legal_output(
        company=si.company,
        output_type="MODIAN_E_INVOICE",
        schema_version=schema_version,
        generator_build=generator_build or schema_version,
        reference_doctype="Sales Invoice",
        reference_name=si.name,
        source={"doctype": "Sales Invoice", "name": si.name},
        payload=payload,
        submit=int(submit or 0),
    )
    return _legal_output_to_dict(out)

