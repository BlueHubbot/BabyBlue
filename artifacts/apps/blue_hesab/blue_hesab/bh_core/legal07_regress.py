from __future__ import annotations

import inspect
from frappe.utils import now
import frappe

from blue_hesab.bh_core.legal_repo import get_previous_output

OUTPUT_TYPE_VAT = "VAT_INVOICE"


def _call_emit(fn, doc, *, output_type: str) -> str | None:
    """Call _emit_* with signature-safe kwargs."""
    sig = inspect.signature(fn)
    kwargs = {}
    if "output_type" in sig.parameters:
        kwargs["output_type"] = output_type
    return fn(doc, **kwargs)


def regress_legal07_amend_without_cancel_should_fail(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: amend بدون cancel باید FAIL شود (اگر core زودتر fail کند هم PASS حساب می‌کنیم)."""
    passed = False
    err = None
    orig = None
    draft_amend = None

    try:
        from blue_hesab.bh_core import smoke_invoices
        from blue_hesab.bh_core.legal_hooks import _emit_amend

        created = smoke_invoices.create_sales_invoice_and_submit(
            company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive"
        )
        orig = created["sales_invoice"]

        old_doc = frappe.get_doc("Sales Invoice", orig)
        new_doc = frappe.copy_doc(old_doc)
        new_doc.amended_from = orig
        new_doc.name = None  # مهم: اسم جدید بساز
        new_doc.docstatus = 0

        # اینجا ممکنه خود ERPNext fail بده (مطلوبه)
        new_doc.insert(ignore_permissions=True)
        draft_amend = new_doc.name

        # اگر insert رد نشد، اینجا باید fail کنیم چون cancel نداریم
        _call_emit(_emit_amend, new_doc, output_type=OUTPUT_TYPE_VAT)

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
    """
    LEGAL-07: amend باید previous_output را به آخرین CANCEL وصل کند (نه ISSUE).
    نکته: این تست خودش خروجی ISSUE و CANCEL را emit می‌کند تا به doc_events وابسته نباشیم.
    """
    from blue_hesab.bh_core import smoke_invoices
    from blue_hesab.bh_core.legal_hooks import _emit_issue, _emit_cancel, _emit_amend

    created = smoke_invoices.create_sales_invoice_and_submit(
        company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive"
    )
    orig = created["sales_invoice"]

    # 1) ISSUE output (وجودش لازم است تا مطمئن شویم AMEND به ISSUE لینک نمی‌شود)
    orig_doc = frappe.get_doc("Sales Invoice", orig)
    issue_out = _call_emit(_emit_issue, orig_doc, output_type=OUTPUT_TYPE_VAT)

    # 2) Cancel original + CANCEL output
    smoke_invoices.cancel_doc(doctype="Sales Invoice", name=orig)
    canceled_doc = frappe.get_doc("Sales Invoice", orig)  # docstatus=2
    cancel_out = _call_emit(_emit_cancel, canceled_doc, output_type=OUTPUT_TYPE_VAT)

    # 3) Create amended doc (core اجازه می‌دهد چون orig کنسل شده)
    base = frappe.get_doc("Sales Invoice", orig)
    new_doc = frappe.copy_doc(base)
    new_doc.amended_from = orig
    new_doc.name = None
    new_doc.docstatus = 0
    new_doc.insert(ignore_permissions=True)
    new_doc.submit()

    # 4) AMEND output برای سند اصلاحی
    amend_out = _call_emit(_emit_amend, new_doc, output_type=OUTPUT_TYPE_VAT)

    prev = get_previous_output(amend_out) if amend_out else None

    return {
        "name": "LEGAL07-AMEND-PREV-IS-CANCEL",
        "ts": now(),
        "company": company,
        "original": orig,
        "issue_output": issue_out,
        "cancel_output": cancel_out,
        "amended_doc": new_doc.name,
        "amend_output": amend_out,
        "prev": prev,
        "pass": bool(cancel_out and amend_out and prev == cancel_out and prev != issue_out),
    }


def regress_legal07_cancel_twice_behavior(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: cancel دوباره باید idempotent باشد (خروجی CANCEL جدید نسازد)."""
    from blue_hesab.bh_core import smoke_invoices
    from blue_hesab.bh_core.legal_hooks import _emit_cancel

    created = smoke_invoices.create_sales_invoice_and_submit(
        company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive"
    )
    orig = created["sales_invoice"]

    smoke_invoices.cancel_doc(doctype="Sales Invoice", name=orig)
    doc = frappe.get_doc("Sales Invoice", orig)

    out1 = _call_emit(_emit_cancel, doc, output_type=OUTPUT_TYPE_VAT)
    out2 = _call_emit(_emit_cancel, doc, output_type=OUTPUT_TYPE_VAT)

    return {
        "name": "LEGAL07-CANCEL-TWICE",
        "ts": now(),
        "company": company,
        "original": orig,
        "out1": out1,
        "out2": out2,
        "pass": bool(out1 and out1 == out2),
    }


def _latest_vat_issue_output_name(ref_doctype: str, ref_name: str, company: str) -> str | None:
    rows = frappe.db.get_all(
        "BH Legal Output",
        filters={
            "reference_doctype": ref_doctype,
            "reference_name": ref_name,
            "company": company,
            "output_type": OUTPUT_TYPE_VAT,
            "docstatus": 1,
        },
        fields=["name", "correction_reason", "creation"],
        order_by="creation desc",
        limit=20,
    )
    # ISSUE معمولاً correction_reason خالی/None است
    for r in rows:
        if (r.get("correction_reason") in (None, "", "ISSUE")):
            return r["name"]
    return None


def regress_legal07_tamper_after_submit_blocked(*, company: str = "BlueAPi") -> dict:
    """LEGAL-07: دستکاری BH Legal Output بعد submit باید fail شود (UI/API + DB trigger)."""
    from blue_hesab.bh_core import smoke_invoices
    from blue_hesab.bh_core.legal_immutability import check_db_triggers
    from blue_hesab.bh_core.legal_hooks import _emit_issue  # کلید حل مشکل همین است

    orig = None
    out_name = None

    try:
        created = smoke_invoices.create_sales_invoice_and_submit(
            company=company, qty=1, rate=1_000_000, vat_price_mode="Exclusive"
        )
        orig = created["sales_invoice"]

        sinv = frappe.get_doc("Sales Invoice", orig)

        # ✅ اینجا خروجی را حتماً می‌سازیم تا چیزی برای tamper داشته باشیم
        out_name = _emit_issue(sinv, output_type=OUTPUT_TYPE_VAT)

        if not out_name:
            return {
                "name": "LEGAL07-TAMPER-AFTER-SUBMIT-BLOCKED",
                "ts": now(),
                "company": company,
                "original": orig,
                "legal_output": None,
                "pass": False,
                "error": "_emit_issue returned None (emit failed).",
            }

        meta = frappe.db.get_value(
            "BH Legal Output",
            out_name,
            ["docstatus", "output_type", "correction_reason", "generator_build"],
            as_dict=True,
        )

        # UI/API tamper (باید با Policy lock fail شود)
        ui_blocked = False
        ui_err = None
        try:
            doc = frappe.get_doc("BH Legal Output", out_name)
            doc.generator_build = "HACK"
            doc.save(ignore_permissions=True)
        except Exception as e:
            ui_blocked = True
            ui_err = str(e)

        # DB tamper (باید با DB trigger fail شود) — SQL خام
        db_blocked = False
        db_err = None
        try:
            frappe.db.sql(
                "UPDATE `tabBH Legal Output` SET generator_build=%s WHERE name=%s",
                ("HACK2", out_name),
            )
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            db_blocked = True
            db_err = str(e)

        trig = check_db_triggers()

        return {
            "name": "LEGAL07-TAMPER-AFTER-SUBMIT-BLOCKED",
            "ts": now(),
            "company": company,
            "original": orig,
            "legal_output": out_name,
            "meta": meta,
            "ui_blocked": ui_blocked,
            "ui_error": ui_err,
            "db_blocked": db_blocked,
            "db_error": db_err,
            "trigger": trig,
            "pass": bool(ui_blocked and db_blocked and trig.get("ok")),
        }

    except Exception as e:
        return {
            "name": "LEGAL07-TAMPER-AFTER-SUBMIT-BLOCKED",
            "ts": now(),
            "company": company,
            "original": orig,
            "legal_output": out_name,
            "pass": False,
            "error": str(e),
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
