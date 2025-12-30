from __future__ import annotations

import datetime as _dt
from typing import Any, Dict

import frappe

from blue_hesab.bh_core import smoke_invoices
from blue_hesab.bh_core.legal_hooks import _emit_issue, _emit_cancel


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
