from __future__ import annotations

import datetime as _dt
from typing import Any, Dict

import frappe

from blue_hesab.bh_core import smoke_invoices
from blue_hesab.bh_core.legal_hooks import _emit_issue, _emit_cancel


from blue_hesab.bh_core.legal_immutability import install_db_triggers, _POLICY_LOCK_MSG, _IMMUTABLE_MSG
from blue_hesab.bh_core.legal_meta import legal_emit_scope
from blue_hesab.bh_core.smoke_invoices import create_sales_invoice_and_submit



def _cleanup_outputs_for_ref(company: str, reference_doctype: str, reference_name: str) -> None:
    with legal_emit_scope():
        frappe.db.sql(
            """
            DELETE FROM `tabBH Legal Output`
            WHERE company=%s AND reference_doctype=%s AND reference_name=%s
            """,
            (company, reference_doctype, reference_name),
        )
    frappe.db.commit()


def _issue_one_ttms(company: str) -> tuple[str, str]:
    sinv_name = create_sales_invoice_and_submit(company=company, intent="Exclusive")
    doc = frappe.get_doc("Sales Invoice", sinv_name)
    out_name = _emit_issue(doc, company=company, output_type="TTMS")
    return sinv_name, out_name


def regress_legal08_issue_emit_succeeds(company: str) -> dict:
    install_db_triggers()

    try:
        sinv_name, out_name = _issue_one_ttms(company)
        exists = bool(frappe.db.exists("BH Legal Output", out_name))
        return {"name": "LEGAL08-ISSUE-EMIT-SUCCEEDS", "pass": exists, "meta": {"sinv": sinv_name, "out": out_name}}
    except Exception as e:
        return {"name": "LEGAL08-ISSUE-EMIT-SUCCEEDS", "pass": False, "error": str(e)}
    finally:
        try:
            _cleanup_outputs_for_ref(company, "Sales Invoice", sinv_name)  # noqa: F821
        except Exception:
            frappe.db.rollback()


def regress_legal08_policy_lock_blocks_delete(company: str) -> dict:
    install_db_triggers()

    sinv_name = None
    out_name = None
    try:
        sinv_name, out_name = _issue_one_ttms(company)

        # بدون emit flag → باید DB trigger جلو حذف را بگیرد
        try:
            frappe.db.sql("DELETE FROM `tabBH Legal Output` WHERE name=%s", (out_name,))
            frappe.db.commit()
            return {"name": "LEGAL08-POLICY-LOCK-BLOCKS-DELETE", "pass": False, "error": "delete unexpectedly succeeded"}
        except Exception as e:
            frappe.db.rollback()
            ok = (_POLICY_LOCK_MSG in str(e))
            return {"name": "LEGAL08-POLICY-LOCK-BLOCKS-DELETE", "pass": ok, "meta": {"out": out_name}, "error": None if ok else str(e)}
    except Exception as e:
        return {"name": "LEGAL08-POLICY-LOCK-BLOCKS-DELETE", "pass": False, "error": str(e)}
    finally:
        try:
            if sinv_name:
                _cleanup_outputs_for_ref(company, "Sales Invoice", sinv_name)
        except Exception:
            frappe.db.rollback()


def regress_legal08_immutable_blocks_update(company: str) -> dict:
    install_db_triggers()

    sinv_name = None
    out_name = None
    try:
        sinv_name, out_name = _issue_one_ttms(company)

        # آپدیت روی docstatus=1 → باید immutable trigger جلوش را بگیرد
        try:
            frappe.db.sql(
                "UPDATE `tabBH Legal Output` SET payload_json=%s WHERE name=%s",
                ('{"x":1}', out_name),
            )
            frappe.db.commit()
            return {"name": "LEGAL08-IMMUTABLE-BLOCKS-UPDATE", "pass": False, "error": "update unexpectedly succeeded"}
        except Exception as e:
            frappe.db.rollback()
            ok = (_IMMUTABLE_MSG in str(e))
            return {"name": "LEGAL08-IMMUTABLE-BLOCKS-UPDATE", "pass": ok, "meta": {"out": out_name}, "error": None if ok else str(e)}
    except Exception as e:
        return {"name": "LEGAL08-IMMUTABLE-BLOCKS-UPDATE", "pass": False, "error": str(e)}
    finally:
        try:
            if sinv_name:
                _cleanup_outputs_for_ref(company, "Sales Invoice", sinv_name)
        except Exception:
            frappe.db.rollback()


def run_legal08_regress(*, company: str = "BlueAPi") -> Dict[str, Any]:
    out: Dict[str, Any] = {"ts": str(_dt.datetime.utcnow()), "company": company, "total": 3, "passed": 0, "failed": 0, "results": []}

    def ok(name: str, **kw):
        out["passed"] += 1
        out["results"].append({"name": name, "pass": True, **kw})

    def fail(name: str, error: str, **kw):
        out["failed"] += 1
        out["results"].append({"name": name, "pass": False, "error": error, **kw})

    # 1) manual insert must be blocked (policy lock)
    try:
        frappe.flags.bh_legal_emit = False
        d = frappe.new_doc("BH Legal Output")
        d.company = company
        d.output_type = "VAT_INVOICE"
        d.reference_doctype = "Sales Invoice"
        d.reference_name = "DUMMY"
        d.insert(ignore_permissions=True)
        fail("LEGAL08-POLICY-LOCK-MANUAL-INSERT", "unexpected: insert succeeded")
    except Exception as e:
        ok("LEGAL08-POLICY-LOCK-MANUAL-INSERT", error=str(e))
    finally:
        frappe.flags.bh_legal_emit = False

    # 2) VAT generator must still work
    try:
        si = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=111111, vat_price_mode="Exclusive")
        ok("LEGAL08-VAT-STILL-WORKS", sales_invoice=si.get("sales_invoice"), legal_output=si.get("legal_output"))
    except Exception as e:
        fail("LEGAL08-VAT-STILL-WORKS", str(e))

    # 3) TTMS/MODIAN skeleton issue+cancel emits (manual call)
    try:
        si2 = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=222222, vat_price_mode="Exclusive")
        doc = frappe.get_doc("Sales Invoice", si2["sales_invoice"])

        ttms_issue = _emit_issue(doc, output_type="TTMS_EXPORT")
        mod_issue = _emit_issue(doc, output_type="MODIAN_PAYLOAD")

        smoke_invoices.cancel_doc(doctype="Sales Invoice", name=doc.name)
        doc2 = frappe.get_doc("Sales Invoice", doc.name)

        ttms_cancel = _emit_cancel(doc2, output_type="TTMS_EXPORT")
        mod_cancel = _emit_cancel(doc2, output_type="MODIAN_PAYLOAD")

        ok("LEGAL08-TTMS-MODIAN-SKELETON", ref=doc.name, ttms=[ttms_issue, ttms_cancel], modian=[mod_issue, mod_cancel])
    except Exception as e:
        fail("LEGAL08-TTMS-MODIAN-SKELETON", str(e))

    return out
