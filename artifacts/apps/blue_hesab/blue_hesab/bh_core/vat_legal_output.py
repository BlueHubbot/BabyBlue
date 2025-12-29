from __future__ import annotations

from typing import Any, Dict, Optional

import frappe

from blue_hesab.bh_core.legal_output import create_legal_output


def _conf_get(*keys: str) -> Optional[str]:
    for k in keys:
        v = getattr(frappe.conf, k, None)
        if v:
            return str(v)
    return None


def _get_schema_version(company: str) -> str:
    v = _conf_get("bh_schema_version", "bh_legal_schema_version", "schema_version")
    if v:
        return v
    try:
        v2 = frappe.db.get_single_value("BH Settings", "schema_version")
        if v2:
            return str(v2)
    except Exception:
        pass
    return "BH-DEV"


def _get_generator_build(company: str, schema_version: str) -> str:
    v = _conf_get("bh_generator_build", "bh_legal_generator_build", "generator_build")
    if v:
        return v
    return schema_version


def _as_float(v: Any) -> float:
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _build_vat_invoice_source(doc) -> Dict[str, Any]:
    items = []
    for it in getattr(doc, "items", []) or []:
        items.append(
            {
                "item_code": getattr(it, "item_code", None),
                "item_name": getattr(it, "item_name", None),
                "qty": _as_float(getattr(it, "qty", None)),
                "uom": getattr(it, "uom", None),
                "rate": _as_float(getattr(it, "rate", None)),
                "amount": _as_float(getattr(it, "amount", None)),
                "net_amount": _as_float(getattr(it, "net_amount", None)),
                "item_tax_template": getattr(it, "item_tax_template", None)
                or getattr(it, "bh_item_tax_template", None),
            }
        )

    taxes = []
    for tx in getattr(doc, "taxes", []) or []:
        taxes.append(
            {
                "charge_type": getattr(tx, "charge_type", None),
                "account_head": getattr(tx, "account_head", None),
                "rate": _as_float(getattr(tx, "rate", None)),
                "tax_amount": _as_float(getattr(tx, "tax_amount", None)),
                "total": _as_float(getattr(tx, "total", None)),
                "description": getattr(tx, "description", None),
            }
        )

    return {
        "doctype": doc.doctype,
        "name": doc.name,
        "company": getattr(doc, "company", None),
        "docstatus": int(getattr(doc, "docstatus", 0) or 0),
        "amended_from": getattr(doc, "amended_from", None),
        "posting_date": str(getattr(doc, "posting_date", "") or ""),
        "posting_time": str(getattr(doc, "posting_time", "") or ""),
        "customer": getattr(doc, "customer", None),
        "supplier": getattr(doc, "supplier", None),
        "bh_vat_price_mode": getattr(doc, "bh_vat_price_mode", None),
        "taxes_and_charges": getattr(doc, "taxes_and_charges", None),
        "net_total": _as_float(getattr(doc, "net_total", None)),
        "total_taxes_and_charges": _as_float(getattr(doc, "total_taxes_and_charges", None)),
        "grand_total": _as_float(getattr(doc, "grand_total", None)),
        "rounded_total": _as_float(getattr(doc, "rounded_total", None)),
        "items": items,
        "taxes": taxes,
    }


def _build_vat_invoice_payload(doc) -> Dict[str, Any]:
    return {
        "type": "VAT_INVOICE",
        "reference": {"doctype": doc.doctype, "name": doc.name},
        "data": _build_vat_invoice_source(doc),
    }


def _emit_vat_invoice(doc, *, event: str = "SUBMIT") -> str:
    company = getattr(doc, "company", None)
    if not company:
        frappe.throw("Company روی سند مشخص نیست؛ امکان صدور خروجی قانونی وجود ندارد.")

    schema_version = _get_schema_version(company)
    generator_build = _get_generator_build(company, schema_version)

    ev = (event or "").upper().strip()
    if ev in {"CANCEL", "BEFORE_CANCEL"}:
        correction_reason = "CANCEL"
        emit_event = "BEFORE_CANCEL"
    else:
        correction_reason = "AMEND" if getattr(doc, "amended_from", None) else None
        emit_event = None

    return create_legal_output(
        company=company,
        output_type="VAT_INVOICE",
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        schema_version=schema_version,
        generator_build=generator_build,
        source=_build_vat_invoice_source(doc),
        payload=_build_vat_invoice_payload(doc),
        correction_reason=correction_reason,
        previous_output=None,
        event=emit_event,
    )


# Legacy handlers (اگر hooks.py هنوز به این‌ها وصل بود، نشکند)
def on_submit_sales_invoice(doc, method: Optional[str] = None) -> str:
    return _emit_vat_invoice(doc, event="SUBMIT")


def on_submit_purchase_invoice(doc, method: Optional[str] = None) -> str:
    return _emit_vat_invoice(doc, event="SUBMIT")


def before_cancel_sales_invoice(doc, method: Optional[str] = None) -> str:
    return _emit_vat_invoice(doc, event="BEFORE_CANCEL")


def before_cancel_purchase_invoice(doc, method: Optional[str] = None) -> str:
    return _emit_vat_invoice(doc, event="BEFORE_CANCEL")
