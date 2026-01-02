# -*- coding: utf-8 -*-
from __future__ import annotations

import frappe
from frappe import ValidationError

from blue_hesab.bh_core import vat_period_lock


def _last_closed_period(company: str):
    return frappe.db.get_value(
        "BH VAT Period",
        {"company": company, "docstatus": 1, "status": "Closed"},
        ["name", "period_start_date", "period_end_date"],
        as_dict=True,
        order_by="period_start_date desc",
    )


def _hook_first(hooks_list, must_contain: str) -> bool:
    if not isinstance(hooks_list, (list, tuple)) or not hooks_list:
        return False
    return must_contain in (hooks_list[0] or "")


def run_v01(company: str = "BlueAPi"):
    out = {"company": company, "total": 0, "passed": 0, "failed": 0, "results": []}

    p = _last_closed_period(company)
    if not p:
        frappe.throw("هیچ دورهٔ VAT بسته‌ای برای این شرکت پیدا نشد. اول یک BH VAT Period را Submit/Close کنید.")

    lock_date = str(p["period_end_date"])

    # 1) Precedence (must run first)
    hooks = frappe.get_hooks("doc_events") or {}
    si = (hooks.get("Sales Invoice") or {})
    pi = (hooks.get("Purchase Invoice") or {})
    checks = [
        ("LOCK-ORDER-SI-before_validate", _hook_first(si.get("before_validate", []), "vat_period_lock")),
        ("LOCK-ORDER-SI-before_submit", _hook_first(si.get("before_submit", []), "vat_period_lock")),
        ("LOCK-ORDER-SI-before_cancel", _hook_first(si.get("before_cancel", []), "vat_period_lock")),
        ("LOCK-ORDER-PI-before_validate", _hook_first(pi.get("before_validate", []), "vat_period_lock")),
        ("LOCK-ORDER-PI-before_submit", _hook_first(pi.get("before_submit", []), "vat_period_lock")),
        ("LOCK-ORDER-PI-before_cancel", _hook_first(pi.get("before_cancel", []), "vat_period_lock")),
    ]
    for name, ok in checks:
        out["total"] += 1
        if ok:
            out["passed"] += 1
            out["results"].append({"name": name, "pass": True, "error": None})
        else:
            out["failed"] += 1
            out["results"].append({"name": name, "pass": False, "error": "vat_period_lock اول نیست یا hook خالی است."})

    # 2) SI submit block inside closed period (handler-level)
    out["total"] += 1
    try:
        doc = frappe._dict(doctype="Sales Invoice", company=company, posting_date=lock_date)
        doc._action = "submit"
        vat_period_lock.bh_before_validate_sales_invoice(doc, "before_validate")
        out["failed"] += 1
        out["results"].append({"name": "LOCK-SI-submit-block", "pass": False, "error": "نباید اجازه submit بدهد."})
    except ValidationError as e:
        msg = str(e)
        ok = ("دوره" in msg) and ("بسته" in msg)
        out["passed" if ok else "failed"] += 1
        out["results"].append({"name": "LOCK-SI-submit-block", "pass": ok, "error": None if ok else msg})

    # 3) SI cancel block after close (handler-level)
    out["total"] += 1
    try:
        doc = frappe._dict(doctype="Sales Invoice", company=company, posting_date=lock_date)
        vat_period_lock.bh_before_cancel_sales_invoice(doc, "before_cancel")
        out["failed"] += 1
        out["results"].append({"name": "LOCK-SI-cancel-block", "pass": False, "error": "نباید اجازه cancel بدهد."})
    except ValidationError as e:
        msg = str(e)
        ok = ("ابطال" in msg) or ("Cancel" in msg) or (("دوره" in msg) and ("بسته" in msg))
        out["passed" if ok else "failed"] += 1
        out["results"].append({"name": "LOCK-SI-cancel-block", "pass": ok, "error": None if ok else msg})

    # 4) SI amend block after close (handler-level)
    out["total"] += 1
    try:
        doc = frappe._dict(doctype="Sales Invoice", company=company, posting_date=lock_date, amended_from="SI-DUMMY-0001")
        doc._action = "submit"
        vat_period_lock.bh_before_validate_sales_invoice(doc, "before_validate")
        out["failed"] += 1
        out["results"].append({"name": "LOCK-SI-amend-block", "pass": False, "error": "نباید اجازه amend بدهد."})
    except ValidationError as e:
        msg = str(e)
        ok = ("دوره" in msg) and ("بسته" in msg)
        out["passed" if ok else "failed"] += 1
        out["results"].append({"name": "LOCK-SI-amend-block", "pass": ok, "error": None if ok else msg})

    # 5) JE VAT tampering block inside closed period (handler-level)
    out["total"] += 1
    try:
        sales_vat = (frappe.get_single("BH Settings").default_sales_vat_account or "").strip()
        if not sales_vat:
            raise Exception("BH Settings.default_sales_vat_account خالی است.")
        je = frappe._dict(
            doctype="Journal Entry",
            company=company,
            posting_date=lock_date,
            accounts=[frappe._dict(account=sales_vat)],
        )
        vat_period_lock.bh_before_submit_journal_entry(je, "before_submit")
        out["failed"] += 1
        out["results"].append({"name": "LOCK-JE-vat-block", "pass": False, "error": "نباید اجازه JE روی حساب VAT بدهد."})
    except ValidationError as e:
        msg = str(e)
        ok = ("حساب‌های VAT" in msg) or (("دوره" in msg) and ("بسته" in msg))
        out["passed" if ok else "failed"] += 1
        out["results"].append({"name": "LOCK-JE-vat-block", "pass": ok, "error": None if ok else msg})
    except Exception as e:
        out["failed"] += 1
        out["results"].append({"name": "LOCK-JE-vat-block", "pass": False, "error": str(e)})

    return out
