from __future__ import annotations

import frappe
from frappe.utils import now

OUTPUT_TYPE_VAT = "VAT_INVOICE"


def _latest_output_name(ref_doctype: str, ref_name: str, company: str) -> str | None:
    return frappe.db.get_value(
        "BH Legal Output",
        {"reference_doctype": ref_doctype, "reference_name": ref_name, "company": company, "output_type": OUTPUT_TYPE_VAT, "docstatus": 1},
        "name",
    )


def regress_legal07_amend_without_cancel_should_fail(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: amend بدون cancel باید FAIL شود (اگر core زودتر fail کند هم PASS حساب می‌کنیم)."""
    passed = False
    err = None
    orig = None
    draft_amend = None

    try:
        from blue_hesab.bh_core import smoke_invoices
        from blue_hesab.bh_core.legal_hooks import _emit_amend

        created = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive")
        orig = created["sales_invoice"]

        old_doc = frappe.get_doc("Sales Invoice", orig)
        new_doc = frappe.copy_doc(old_doc)
        new_doc.amended_from = orig

        # اینجا ممکنه خود ERPNext fail بده (کاملاً OK و مطلوبه)
        new_doc.insert(ignore_permissions=True)
        draft_amend = new_doc.name

        # اگر insert رد نشد، اینجا باید fail کنیم چون cancel نداریم
        _emit_amend(new_doc, output_type=OUTPUT_TYPE_VAT)

        passed = False
        err = "amend unexpectedly succeeded"
    except Exception as e:
        passed = True
        err = str(e)

    return {
        "name": "LEGAL07-AMEND-WITHOUT-CANCEL",
        "ts": now(),
        "company": company,
        "original": orig,
        "draft_amend": draft_amend,
        "pass": passed,
        "error": err,
    }


def regress_legal07_amend_links_to_last_cancel(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: amend باید previous_output را به آخرین CANCEL وصل کند (نه ISSUE)."""
    from blue_hesab.bh_core import smoke_invoices

    created = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive")
    orig = created["sales_invoice"]

    # cancel original (should create CANCEL output for orig)
    smoke_invoices.cancel_doc(doctype="Sales Invoice", name=orig)

    cancel_out = _latest_output_name("Sales Invoice", orig, company)

    # create amended doc (core اجازه می‌دهد چون orig کنسل شده)
    old_doc = frappe.get_doc("Sales Invoice", orig)
    new_doc = frappe.copy_doc(old_doc)
    new_doc.amended_from = orig
    new_doc.insert(ignore_permissions=True)
    new_doc.submit()

    amend_out = _latest_output_name("Sales Invoice", new_doc.name, company)

    prev = frappe.db.get_value("BH Legal Output", amend_out, "previous_output") if amend_out else None

    return {
        "name": "LEGAL07-AMEND-PREV-IS-CANCEL",
        "ts": now(),
        "company": company,
        "original": orig,
        "cancel_output": cancel_out,
        "amended_doc": new_doc.name,
        "amend_output": amend_out,
        "prev": prev,
        "pass": bool(cancel_out and amend_out and prev == cancel_out),
    }


def regress_legal07_cancel_twice_behavior(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: cancel دوباره باید idempotent باشد (خروجی CANCEL جدید نسازد)."""
    from blue_hesab.bh_core import smoke_invoices
    from blue_hesab.bh_core.legal_hooks import _emit_cancel

    created = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive")
    orig = created["sales_invoice"]

    smoke_invoices.cancel_doc(doctype="Sales Invoice", name=orig)

    doc = frappe.get_doc("Sales Invoice", orig)
    out1 = _emit_cancel(doc, output_type=OUTPUT_TYPE_VAT)
    out2 = _emit_cancel(doc, output_type=OUTPUT_TYPE_VAT)

    return {
        "name": "LEGAL07-CANCEL-TWICE",
        "ts": now(),
        "company": company,
        "original": orig,
        "out1": out1,
        "out2": out2,
        "pass": out1 == out2,
    }


def regress_legal07_tamper_after_submit_blocked(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: دستکاری BH Legal Output بعد submit باید fail شود (UI/API + DB trigger)."""
    from blue_hesab.bh_core import smoke_invoices
    from blue_hesab.bh_core.legal_immutability import check_db_triggers

    created = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive")
    orig = created["sales_invoice"]

    out_name = _latest_output_name("Sales Invoice", orig, company)
    doc = frappe.get_doc("BH Legal Output", out_name)

    ui_blocked = False
    ui_err = None
    try:
        doc.generator_build = "HACK"
        doc.save(ignore_permissions=True)
    except Exception as e:
        ui_blocked = True
        ui_err = str(e)

    db_blocked = False
    db_err = None
    try:
        frappe.db.set_value("BH Legal Output", out_name, "generator_build", "HACK2")
    except Exception as e:
        db_blocked = True
        db_err = str(e)

    trig = check_db_triggers()

    return {
        "name": "LEGAL07-TAMPER-IMMUTABLE",
        "ts": now(),
        "company": company,
        "original": orig,
        "legal_output": out_name,
        "ui_blocked": ui_blocked,
        "ui_error": ui_err,
        "db_blocked": db_blocked,
        "db_error": db_err,
        "trigger": trig,
        "pass": bool(ui_blocked and db_blocked and trig.get("ok")),
    }


def run_legal07_regress(*, company: str = "BlueAPi") -> dict:
    results = []
    for fn in (
        regress_legal07_amend_without_cancel_should_fail,
        regress_legal07_amend_links_to_last_cancel,
        regress_legal07_cancel_twice_behavior,
        regress_legal07_tamper_after_submit_blocked,
    ):
        try:
            results.append(fn(company=company))
        except Exception as e:
            results.append({"name": fn.__name__, "pass": False, "error": str(e)})

    return {
        "ts": now(),
        "company": company,
        "total": len(results),
        "passed": sum(1 for r in results if r.get("pass")),
        "failed": sum(1 for r in results if not r.get("pass")),
        "results": results,
    }
