# apps/blue_hesab/blue_hesab/bh_core/vat_templates_mixed.py
from __future__ import annotations

import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
from frappe.utils import flt

BH_SETTINGS_DOCTYPE = "BH Settings"

PREFIX_SALES = "BH VAT MIXED Sales"
PREFIX_PURCHASE = "BH VAT MIXED Purchase"

def _normalize_mixed_template(kind: str, chosen: str) -> str:
    chosen = (chosen or "").strip()
    if not chosen:
        return chosen

    if kind == "Sales" and chosen.startswith(PREFIX_PURCHASE):
        return PREFIX_SALES + chosen[len(PREFIX_PURCHASE):]

    if kind == "Purchase" and chosen.startswith(PREFIX_SALES):
        return PREFIX_PURCHASE + chosen[len(PREFIX_SALES):]

    return chosen

def _abbr(company: str) -> str:
    try:
        return frappe.db.get_value("Company", company, "abbr") or "BA"
    except Exception:
        return "BA"


def _bh_settings():
    try:
        return frappe.get_single(BH_SETTINGS_DOCTYPE)
    except Exception:
        return None


def _get_defaults():
    s = _bh_settings()
    sales_acc = getattr(s, "default_sales_vat_account", None) if s else None
    purchase_acc = getattr(s, "default_purchase_vat_account", None) if s else None
    sales_rate = flt(getattr(s, "default_sales_vat_rate", 9.0) if s else 9.0) or 9.0
    purchase_rate = flt(getattr(s, "default_purchase_vat_rate", 9.0) if s else 9.0) or 9.0
    return sales_acc, sales_rate, purchase_acc, purchase_rate


def _is_our_template(name: str | None) -> bool:
    if not name:
        return False
    return (
        name.startswith(PREFIX_SALES)
        or name.startswith(PREFIX_PURCHASE)
        or name.startswith("BH VAT MIXED")
    )


def _upsert_template(doctype: str, name: str, company: str, account_head: str, rate: float, included: int) -> str:
    """
    Creates/updates a Taxes and Charges Template with exactly one VAT row.
    included: 1 => included_in_print_rate, 0 => not included.
    """
    if not account_head:
        raise_bh_vat_error(BH_VAT_E_GENERIC, f"[VAT] Missing VAT account in BH Settings for template: {name}")

    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
    else:
        doc = frappe.new_doc(doctype)
        doc.name = name

    # common fields
    doc.company = company
    doc.title = name

    # reset taxes rows
    doc.set("taxes", [])

    row = doc.append("taxes", {})
    row.charge_type = "On Net Total"
    row.account_head = account_head
    row.description = "VAT (MIXED)"
    row.rate = flt(rate)
    row.included_in_print_rate = 1 if int(included) else 0

    doc.save(ignore_permissions=True)
    return doc.name


def ensure_bh_vat_mixed_templates(company: str) -> dict:
    """
    Ensures 4 templates exist (Sales EXCL/INCL + Purchase EXCL/INCL).
    Returns their names.
    """
    ab = _abbr(company)
    sales_acc, sales_rate, purchase_acc, purchase_rate = _get_defaults()

    sales_excl = f"{PREFIX_SALES} (EXCL) - {ab}"
    sales_incl = f"{PREFIX_SALES} (INCL) - {ab}"
    purchase_excl = f"{PREFIX_PURCHASE} (EXCL) - {ab}"
    purchase_incl = f"{PREFIX_PURCHASE} (INCL) - {ab}"

    _upsert_template(
        "Sales Taxes and Charges Template",
        sales_excl,
        company,
        account_head=sales_acc,
        rate=sales_rate,
        included=0,
    )
    _upsert_template(
        "Sales Taxes and Charges Template",
        sales_incl,
        company,
        account_head=sales_acc,
        rate=sales_rate,
        included=1,
    )

    _upsert_template(
        "Purchase Taxes and Charges Template",
        purchase_excl,
        company,
        account_head=purchase_acc,
        rate=purchase_rate,
        included=0,
    )
    _upsert_template(
        "Purchase Taxes and Charges Template",
        purchase_incl,
        company,
        account_head=purchase_acc,
        rate=purchase_rate,
        included=1,
    )

    frappe.db.commit()
    return {
        "sales_excl": sales_excl,
        "sales_incl": sales_incl,
        "purchase_excl": purchase_excl,
        "purchase_incl": purchase_incl,
    }


def ensure_bh_vat_price_mode_fields():
    """
    Creates Custom Field bh_vat_price_mode on Sales Invoice & Purchase Invoice.
    Safe to run multiple times.
    """
    def _ensure(dt: str):
        if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "bh_vat_price_mode"}):
            return

        cf = frappe.new_doc("Custom Field")
        cf.dt = dt
        cf.label = "VAT Price Mode"
        cf.fieldname = "bh_vat_price_mode"
        cf.fieldtype = "Select"
        cf.options = "Auto\nExclusive\nInclusive"
        cf.insert_after = "taxes_and_charges"
        cf.in_list_view = 0
        cf.read_only = 0
        cf.no_copy = 1
        cf.save(ignore_permissions=True)

    _ensure("Sales Invoice")
    _ensure("Purchase Invoice")
    frappe.db.commit()


def _mode_from_doc(doc) -> str:
    """Return one of: Auto / Exclusive / Inclusive.

    - Prefer doc.flags (regress/pipeline intent)
    - Then real field on DocType (bh_vat_price_mode)
    - Default to Auto
    """
    # flags intent (regress / pipeline)
    flags = getattr(doc, "flags", None)
    if flags:
        try:
            if int(getattr(flags, "bh_vat_inclusive", 0) or 0):
                return "Inclusive"
        except Exception:
            pass

        pm = getattr(flags, "bh_vat_price_mode", None)
        if pm:
            pm = str(pm).strip()
            if pm:
                return pm

    # real field (if exists)
    pm2 = getattr(doc, "bh_vat_price_mode", None)
    if pm2:
        pm2 = str(pm2).strip()
        if pm2:
            return pm2

    return "Auto"



def _apply_template_rows(doc, template_doctype: str, template_name: str):
    """
    Copies template taxes rows into doc.taxes (hard reset).
    """
    tpl = frappe.get_doc(template_doctype, template_name)
    doc.set("taxes", [])
    for t in tpl.get("taxes") or []:
        r = doc.append("taxes", {})
        r.charge_type = t.charge_type
        r.account_head = t.account_head
        r.description = t.description
        r.rate = t.rate
        r.included_in_print_rate = t.included_in_print_rate


def auto_apply_sales_vat_template(doc):
    """
    Template محور Default + Field محور Override.
    - Auto + user set taxes/template => don't override.
    - Exclusive/Inclusive => enforce our template + taxes rows.
    Also sets doc.flags.bh_si_incl_req (pipeline compatibility).
    """
    company = getattr(doc, "company", None)
    if not company:
        return

    names = ensure_bh_vat_mixed_templates(company)
    mode = _mode_from_doc(doc)

    # decide if we should override
    has_user_template = bool(getattr(doc, "taxes_and_charges", None))
    has_user_taxes = bool(getattr(doc, "taxes", None))

    if mode == "Auto":
        # If user already picked something and it's not ours, do not override.
        if has_user_template and not _is_our_template(doc.taxes_and_charges):
            return
        if has_user_taxes and (not has_user_template):
            return
        chosen = names["sales_excl"]  # safe default
        incl_flag = 0
    elif mode == "Inclusive":
        chosen = names["sales_incl"]
        incl_flag = 1
    else:  # Exclusive
        chosen = names["sales_excl"]
        incl_flag = 0

    # enforce template + taxes rows if needed
    if (getattr(doc, "taxes_and_charges", None) != chosen) or (not doc.get("taxes")) or _is_our_template(chosen):
        chosen = _normalize_mixed_template("Sales", chosen)
        chosen = _normalize_mixed_template("Purchase", chosen)
        doc.taxes_and_charges = chosen
        _apply_template_rows(doc, "Sales Taxes and Charges Template", chosen)

    # pipeline compatibility (you already have detection for this flag)
    try:
        doc.flags.bh_si_incl_req = int(incl_flag)
    except Exception:
        pass


def auto_apply_purchase_vat_template(doc):
    """
    Same logic for Purchase Invoice. Sets doc.flags.bh_pi_incl_req.
    Default = Exclusive.
    """
    company = getattr(doc, "company", None)
    if not company:
        return

    names = ensure_bh_vat_mixed_templates(company)
    mode = _mode_from_doc(doc)

    has_user_template = bool(getattr(doc, "taxes_and_charges", None))
    has_user_taxes = bool(getattr(doc, "taxes", None))

    if mode == "Auto":
        if has_user_template and not _is_our_template(doc.taxes_and_charges):
            return
        if has_user_taxes and (not has_user_template):
            return
        chosen = names["purchase_excl"]
        incl_flag = 0
    elif mode == "Inclusive":
        chosen = names["purchase_incl"]
        incl_flag = 1
    else:
        chosen = names["purchase_excl"]
        incl_flag = 0

    if (getattr(doc, "taxes_and_charges", None) != chosen) or (not doc.get("taxes")) or _is_our_template(chosen):
        doc.taxes_and_charges = chosen
        _apply_template_rows(doc, "Purchase Taxes and Charges Template", chosen)

    try:
        doc.flags.bh_pi_incl_req = int(incl_flag)
    except Exception:
        pass
