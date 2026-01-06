from __future__ import annotations

import frappe
from frappe.utils import today

from blue_hesab.bh_core import vat_pipeline, vat_mixed


def _latest_submitted(doctype: str, company: str):
    row = frappe.get_all(
        doctype,
        filters={"company": company, "docstatus": 1},
        fields=["name", "modified"],
        order_by="modified desc",
        limit=1,
    )
    if not row:
        raise Exception(f"No submitted {doctype} found for company={company}")
    return frappe.get_doc(doctype, row[0]["name"])


def _draft_copy(doc):
    d = frappe.copy_doc(doc)
    d.set("name", None)
    d.docstatus = 0
    if hasattr(d, "posting_date"):
        d.posting_date = today()
    if hasattr(d, "set_posting_time"):
        d.set_posting_time = 1
    d.flags.ignore_permissions = True
    d.flags.ignore_links = True
    return d


def _first_item_group():
    ig = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
    if not ig:
        ig = frappe.db.get_value("Item Group", {}, "name")
    return ig


def _first_uom():
    u = frappe.db.get_value("UOM", {}, "name")
    return u or "Nos"


def _create_item_without_mapping() -> str:
    code = f"BH-NO-VAT-TPL-{frappe.generate_hash(length=6)}"
    it = frappe.new_doc("Item")
    it.item_code = code
    it.item_name = code
    it.item_group = _first_item_group()
    it.stock_uom = _first_uom()

    if hasattr(it, "is_stock_item"):
        it.is_stock_item = 0
    if hasattr(it, "is_sales_item"):
        it.is_sales_item = 1
    if hasattr(it, "is_purchase_item"):
        it.is_purchase_item = 1

    # force blank custom fields if exist
    if frappe.db.has_column("Item", "bh_item_tax_template"):
        it.set("bh_item_tax_template", None)
    if frappe.db.has_column("Item", "bh_vat_profile"):
        it.set("bh_vat_profile", None)

    it.flags.ignore_permissions = True
    it.insert()

    # ensure blank at DB-level (in case any hook populated)
    fields = {}
    if frappe.db.has_column("Item", "bh_item_tax_template"):
        fields["bh_item_tax_template"] = None
    if frappe.db.has_column("Item", "bh_vat_profile"):
        fields["bh_vat_profile"] = None
    if fields:
        frappe.db.set_value("Item", it.name, fields, update_modified=False)

    return it.name


def _is_expected_missing_tpl_error(e: Exception) -> bool:
    msg = str(e) or ""
    return ("item_tax_template" in msg) and ("ندارند" in msg or "missing" in msg.lower())


def run(company: str = "BlueAPi"):
    frappe.set_user("Administrator")
    out = {}

    # canonical names (as your app generates them)
    exp_si_excl = vat_mixed.mixed_template_name("sales", company, "EXCL")
    wrong_si_incl = vat_mixed.mixed_template_name("sales", company, "INCL")
    exp_pi_excl = vat_mixed.mixed_template_name("purchase", company, "EXCL")
    wrong_pi_incl = vat_mixed.mixed_template_name("purchase", company, "INCL")

    si_sample = _latest_submitted("Sales Invoice", company)
    pi_sample = _latest_submitted("Purchase Invoice", company)

    # ---------------------------
    # T1A: Draft should NOT auto-fix template (no_autofix policy)
    # ---------------------------
    try:
        si = _draft_copy(si_sample)
        si._action = None
        if hasattr(si, "bh_vat_price_mode"):
            si.bh_vat_price_mode = "Exclusive"
        si.taxes_and_charges = wrong_si_incl
        vat_pipeline.bh_before_validate_sales_invoice(si)

        out["T1A_SI_DRAFT_LOCK"] = "PASS(no_autofix)" if (si.taxes_and_charges or "").strip() == (wrong_si_incl or "").strip() else f"FAIL(changed_to={si.taxes_and_charges})"
    except Exception as e:
        out["T1A_SI_DRAFT_LOCK"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    # ---------------------------
    # T1B: Submit should block wrong template/mode mismatch
    # ---------------------------
    try:
        si2 = _draft_copy(si_sample)
        si2._action = "submit"
        if hasattr(si2, "bh_vat_price_mode"):
            si2.bh_vat_price_mode = "Exclusive"
        si2.taxes_and_charges = wrong_si_incl

        try:
            vat_pipeline.bh_before_validate_sales_invoice(si2)
            out["T1B_SI_SUBMIT_LOCK"] = "FAIL(no block)"
        except Exception as e:
            out["T1B_SI_SUBMIT_LOCK"] = f"PASS({type(e).__name__})"
    except Exception as e:
        out["T1B_SI_SUBMIT_LOCK"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    # ---------------------------
    # T1A/T1B for Purchase (no_autofix draft, submit-block mismatch)
    # ---------------------------
    try:
        pi = _draft_copy(pi_sample)
        pi._action = None
        if hasattr(pi, "bh_vat_price_mode"):
            pi.bh_vat_price_mode = "Exclusive"
        pi.taxes_and_charges = wrong_pi_incl
        vat_pipeline.bh_before_validate_purchase_invoice(pi)

        out["T1A_PI_DRAFT_LOCK"] = "PASS(no_autofix)" if (pi.taxes_and_charges or "").strip() == (wrong_pi_incl or "").strip() else f"FAIL(changed_to={pi.taxes_and_charges})"
    except Exception as e:
        out["T1A_PI_DRAFT_LOCK"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    try:
        pi2 = _draft_copy(pi_sample)
        pi2._action = "submit"
        if hasattr(pi2, "bh_vat_price_mode"):
            pi2.bh_vat_price_mode = "Exclusive"
        pi2.taxes_and_charges = wrong_pi_incl

        try:
            vat_pipeline.bh_before_validate_purchase_invoice(pi2)
            out["T1B_PI_SUBMIT_LOCK"] = "FAIL(no block)"
        except Exception as e:
            out["T1B_PI_SUBMIT_LOCK"] = f"PASS({type(e).__name__})"
    except Exception as e:
        out["T1B_PI_SUBMIT_LOCK"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    # ---------------------------
    # T2B/T2C: missing item mapping should fail-fast (either before_validate or validate)
    # ---------------------------
    item_name = None
    try:
        item_name = _create_item_without_mapping()

        # Sales
        si3 = _draft_copy(si_sample)
        si3._action = "submit"
        if hasattr(si3, "bh_vat_price_mode"):
            si3.bh_vat_price_mode = "Exclusive"
        si3.items[0].item_code = item_name
        if "item_tax_template" in si3.items[0].as_dict():
            si3.items[0].item_tax_template = None

        try:
            vat_pipeline.bh_before_validate_sales_invoice(si3)
            # if no error here, expect later validate to fail
            try:
                vat_pipeline.validate_sales_invoice(si3)
                out["T2B_SI_MISSING_ITEM_TPL"] = "FAIL(no block)"
            except Exception as e:
                out["T2B_SI_MISSING_ITEM_TPL"] = f"PASS({type(e).__name__}: {str(e)[:100]})"
        except Exception as e:
            out["T2B_SI_MISSING_ITEM_TPL"] = "PASS(ValidationError)" if _is_expected_missing_tpl_error(e) else f"FAIL({type(e).__name__}: {str(e)[:120]})"

        # Purchase
        pi3 = _draft_copy(pi_sample)
        pi3._action = "submit"
        if hasattr(pi3, "bh_vat_price_mode"):
            pi3.bh_vat_price_mode = "Exclusive"
        pi3.items[0].item_code = item_name
        if "item_tax_template" in pi3.items[0].as_dict():
            pi3.items[0].item_tax_template = None

        try:
            vat_pipeline.bh_before_validate_purchase_invoice(pi3)
            try:
                vat_pipeline.validate_purchase_invoice(pi3)
                out["T2C_PI_MISSING_ITEM_TPL"] = "FAIL(no block)"
            except Exception as e:
                out["T2C_PI_MISSING_ITEM_TPL"] = f"PASS({type(e).__name__}: {str(e)[:100]})"
        except Exception as e:
            out["T2C_PI_MISSING_ITEM_TPL"] = "PASS(ValidationError)" if _is_expected_missing_tpl_error(e) else f"FAIL({type(e).__name__}: {str(e)[:120]})"

    finally:
        if item_name and frappe.db.exists("Item", item_name):
            try:
                frappe.delete_doc("Item", item_name, ignore_permissions=True, force=1)
            except Exception:
                pass

    print("=== VAT-10B TERMINAL CHECKS ===")
    keys = [
        "T1A_SI_DRAFT_LOCK",
        "T1B_SI_SUBMIT_LOCK",
        "T1A_PI_DRAFT_LOCK",
        "T1B_PI_SUBMIT_LOCK",
        "T2B_SI_MISSING_ITEM_TPL",
        "T2C_PI_MISSING_ITEM_TPL",
    ]
    for k in keys:
        print(f"{k}: {out.get(k)}")

    out["ok"] = True
    return out


def run_cli(company: str = "BlueAPi"):
    return run(company=company)
