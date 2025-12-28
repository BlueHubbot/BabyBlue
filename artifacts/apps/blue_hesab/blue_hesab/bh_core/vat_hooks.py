from __future__ import annotations

import json
import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
from frappe.utils import flt

from . import get_bh_settings

# Cache Item Tax Template -> item_tax_rate JSON
_TEMPLATE_RATE_CACHE: dict[str, str] = {}


def _get_vat_account_and_rate(doc):
    s = get_bh_settings()
    if doc.doctype == "Sales Invoice":
        return (s.get("default_sales_vat_account"), flt(s.get("default_sales_vat_rate") or 0))
    if doc.doctype == "Purchase Invoice":
        return (s.get("default_purchase_vat_account"), flt(s.get("default_purchase_vat_rate") or 0))
    return (None, 0.0)


def _ensure_tax_row(doc, vat_account: str, default_rate: float):
    """Ensure a VAT tax row exists with charge_type=On Net Total for the given VAT account."""
    vat_account = (vat_account or "").strip()
    if not vat_account:
        return None

    row = None
    for t in (doc.get("taxes") or []):
        head = (t.get("account_head") or t.get("tax_type") or "").strip()
        if head == vat_account:
            row = t
            break

    if not row:
        row = doc.append("taxes", {})

    # Standard ERPNext fields
    if "account_head" in row.as_dict():
        row.account_head = vat_account
    if "tax_type" in row.as_dict() and not (row.get("tax_type") or "").strip():
        row.tax_type = vat_account

    row.charge_type = "On Net Total"
    row.rate = flt(default_rate or 0)

    # Stable defaults
    if "add_deduct_tax" in row.as_dict() and not (row.get("add_deduct_tax") or "").strip():
        row.add_deduct_tax = "Add"

    if not (row.get("description") or "").strip():
        row.description = "VAT"

    return row


def _item_tax_rate_json(template_name: str) -> str:
    """Return json string for child row field `item_tax_rate` based on Item Tax Template."""
    template_name = (template_name or "").strip()
    if not template_name:
        return "{}"

    cached = _TEMPLATE_RATE_CACHE.get(template_name)
    if cached is not None:
        return cached

    try:
        itt = frappe.get_doc("Item Tax Template", template_name)
    except Exception:
        j = "{}"
        _TEMPLATE_RATE_CACHE[template_name] = j
        return j

    d = {}
    for r in (itt.get("taxes") or []):
        tax_type = (r.get("tax_type") or "").strip()
        if not tax_type:
            continue
        d[tax_type] = flt(r.get("tax_rate") or 0)

    j = json.dumps(d, ensure_ascii=False)
    _TEMPLATE_RATE_CACHE[template_name] = j
    return j


def _apply_item_templates(doc):
    """Enforce item_tax_template from Item.bh_item_tax_template for ALL items on invoice."""
    item_codes = [d.get("item_code") for d in (doc.get("items") or []) if d.get("item_code")]
    if not item_codes:
        return

    items = frappe.get_all(
        "Item",
        filters={"name": ["in", sorted(set(item_codes))]},
        fields=["name", "bh_item_tax_template"],
    )
    imap = {d["name"]: (d.get("bh_item_tax_template") or "").strip() for d in items}

    missing = []
    for it in (doc.get("items") or []):
        code = (it.get("item_code") or "").strip()
        if not code:
            continue

        tpl = (imap.get(code) or "").strip()
        if not tpl:
            missing.append(code)
            continue

        it.item_tax_template = tpl

        # Keep item_tax_rate in-sync if the field exists on child row
        if "item_tax_rate" in it.as_dict():
            it.item_tax_rate = _item_tax_rate_json(tpl)

    if missing:
        raise_bh_vat_error(BH_VAT_E_GENERIC, 
            "BH VAT: برای این آیتم‌ها bh_item_tax_template ست نشده است: "
            + ", ".join(sorted(set(missing)))
        )


def _recalc(doc):
    """Recalculate taxes & totals deterministically."""
    try:
        doc.calculate_taxes_and_totals()
    except Exception:
        try:
            doc.set_missing_values()
            doc.calculate_taxes_and_totals()
        except Exception:
            pass


def _detect_existing_inclusive(doc, vat_account: str) -> int:
    """Preserve inclusive intent if it was already set (row/template/doc/ui/flags)."""
    vat_account = (vat_account or "").strip()
    if not vat_account:
        return 0

    # 1) Explicit VAT row included_in_print_rate=1
    try:
        for t in (doc.get("taxes") or []):
            if (t.get("account_head") or "").strip() == vat_account and int(t.get("included_in_print_rate") or 0) == 1:
                return 1
    except Exception:
        pass

    # 2) Document UI field (canonical)
    try:
        pm = (getattr(doc, "bh_vat_price_mode", None) or (doc.get("bh_vat_price_mode") if hasattr(doc, "get") else "") or "").strip().lower()
        if pm.startswith("incl"):
            return 1
    except Exception:
        pass

    # 3) Taxes & Charges Template marker
    try:
        tac = (getattr(doc, "taxes_and_charges", None) or (doc.get("taxes_and_charges") if hasattr(doc, "get") else "") or "").strip()
        if "(INCL)" in tac:
            return 1
    except Exception:
        pass

    # 4) Pipeline flag (Sales)
    try:
        if int(getattr(getattr(doc, "flags", None), "bh_si_incl_req", 0) or 0) == 1:
            return 1
    except Exception:
        pass

    # 5) Legacy flags used in tests
    try:
        if int(getattr(getattr(doc, "flags", None), "bh_vat_inclusive", 0) or 0) == 1:
            return 1
    except Exception:
        pass

    return 0



def apply_sales_invoice_vat(doc, method=None):
    """Production VAT apply for Sales Invoice (MIXED-ready via per-item templates)."""
    if doc.doctype != "Sales Invoice":
        return

    s = get_bh_settings()
    if not int(s.get("enable_vat") or 0):
        return

    vat_account, default_rate = _get_vat_account_and_rate(doc)
    vat_account = (vat_account or "").strip()
    if not vat_account:
        raise_bh_vat_error(BH_VAT_E_GENERIC, "BH VAT: default_sales_vat_account تنظیم نشده است.")

    incl_req = _detect_existing_inclusive(doc, vat_account)

    row = _ensure_tax_row(doc, vat_account, default_rate)
    _apply_item_templates(doc)

    if incl_req and row:
        try:
            row.included_in_print_rate = 1
        except Exception:
            pass

    _recalc(doc)

    # Post-guard
    _ensure_tax_row(doc, vat_account, default_rate)


def apply_purchase_invoice_vat(doc, method=None):
    """Production VAT apply for Purchase Invoice (MIXED-ready via per-item templates)."""
    if doc.doctype != "Purchase Invoice":
        return

    s = get_bh_settings()
    if not int(s.get("enable_vat") or 0):
        return

    vat_account, default_rate = _get_vat_account_and_rate(doc)
    vat_account = (vat_account or "").strip()
    if not vat_account:
        raise_bh_vat_error(BH_VAT_E_GENERIC, "BH VAT: default_purchase_vat_account تنظیم نشده است.")

    incl_req = _detect_existing_inclusive(doc, vat_account)

    row = _ensure_tax_row(doc, vat_account, default_rate)
    _apply_item_templates(doc)

    if incl_req and row:
        try:
            row.included_in_print_rate = 1
        except Exception:
            pass

    _recalc(doc)

    # Post-guard
    _ensure_tax_row(doc, vat_account, default_rate)
