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


def run(company: str = "BlueAPi"):
    frappe.set_user("Administrator")
    out = {}

    si_sample = _latest_submitted("Sales Invoice", company)
    pi_sample = _latest_submitted("Purchase Invoice", company)

    si_incl = vat_mixed.mixed_template_name("sales", company, "INCL")
    si_excl = vat_mixed.mixed_template_name("sales", company, "EXCL")

    pi_incl = vat_mixed.mixed_template_name("purchase", company, "INCL")
    pi_excl = vat_mixed.mixed_template_name("purchase", company, "EXCL")

    # T11-1: Template should NOT infer bh_vat_price_mode (no_infer policy) (Sales)
    try:
        d = _draft_copy(si_sample)
        d._action = None
        d.bh_vat_price_mode = ""
        d.taxes_and_charges = si_incl
        vat_pipeline.before_validate_sales_invoice(d)
        out["T11_1_SI_TEMPLATE_TO_MODE"] = "PASS(no_infer)" if not ((d.bh_vat_price_mode or "").strip().lower().startswith("incl")) else f"FAIL(mode={d.bh_vat_price_mode})"
    except Exception as e:
        out["T11_1_SI_TEMPLATE_TO_MODE"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    # T11-2: Draft should NOT auto-fix taxes_and_charges to match doc mode (no_autofix policy) (Sales)
    try:
        d = _draft_copy(si_sample)
        d._action = None
        d.bh_vat_price_mode = "Exclusive"
        d.taxes_and_charges = si_incl
        vat_pipeline.before_validate_sales_invoice(d)
        out["T11_2_SI_DOC_WINS_TEMPLATE"] = "PASS(no_autofix)" if d.taxes_and_charges == si_incl else f"FAIL(changed_to={d.taxes_and_charges})"
    except Exception as e:
        out["T11_2_SI_DOC_WINS_TEMPLATE"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    # T11-3: Submit mismatch -> hard-block (Sales)
    try:
        d = _draft_copy(si_sample)
        d._action = "submit"
        d.bh_vat_price_mode = "Exclusive"
        d.taxes_and_charges = si_incl
        try:
            vat_pipeline.before_validate_sales_invoice(d)
            out["T11_3_SI_SUBMIT_BLOCK_MISMATCH"] = "FAIL(no block)"
        except Exception:
            out["T11_3_SI_SUBMIT_BLOCK_MISMATCH"] = "PASS"
    except Exception as e:
        out["T11_3_SI_SUBMIT_BLOCK_MISMATCH"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    # T11-4: Template should NOT infer bh_vat_price_mode (no_infer policy) (Purchase)
    try:
        d = _draft_copy(pi_sample)
        d._action = None
        d.bh_vat_price_mode = ""
        d.taxes_and_charges = pi_incl
        vat_pipeline.before_validate_purchase_invoice(d)
        out["T11_4_PI_TEMPLATE_TO_MODE"] = "PASS(no_infer)" if not ((d.bh_vat_price_mode or "").strip().lower().startswith("incl")) else f"FAIL(mode={d.bh_vat_price_mode})"
    except Exception as e:
        out["T11_4_PI_TEMPLATE_TO_MODE"] = f"FAIL({type(e).__name__}: {str(e)[:120]})"

    print("=== VAT-11 TERMINAL CHECKS ===")
    for k in [
        "T11_1_SI_TEMPLATE_TO_MODE",
        "T11_2_SI_DOC_WINS_TEMPLATE",
        "T11_3_SI_SUBMIT_BLOCK_MISMATCH",
        "T11_4_PI_TEMPLATE_TO_MODE",
    ]:
        print(f"{k}: {out.get(k)}")

    out["ok"] = True
    return out


def run_cli(company: str = "BlueAPi"):
    return run(company=company)
