# -*- coding: utf-8 -*-
"""
BH VAT Period Lock (NNG)

- قفل دوره بسته برای SI/PI
- ممنوعیت دستکاری VAT در JE/Payment Entry مگر مسیر تسویه
"""

from __future__ import annotations

import frappe
from frappe.utils import getdate

from blue_hesab.bh_core import get_bh_settings


def find_closed_vat_period(company: str, posting_date) -> dict | None:
    if not company or not posting_date:
        return None

    dt = getdate(posting_date)
    rows = frappe.get_all(
        "BH VAT Period",
        filters={
            "company": company,
            "docstatus": 1,
            "status": "Closed",
            "period_start_date": ["<=", dt],
            "period_end_date": [">=", dt],
        },
        fields=["name", "period_start_date", "period_end_date"],
        limit=1,
    )
    if not rows:
        return None
    r = rows[0]
    return {"name": r["name"], "start": str(r["period_start_date"]), "end": str(r["period_end_date"])}


def _throw_period_locked(*, action_fa: str, doctype_fa: str, posting_date, period: dict):
    msg = (
        f"{doctype_fa} با تاریخ {posting_date} داخل دوره مالیات بر ارزش افزوده بسته است.\n"
        f"دوره: {period['name']} | بازه: {period['start']} تا {period['end']}\n"
        f"عملیات «{action_fa}» در دوره بسته ممنوع است."
    )
    frappe.throw(msg, title="دوره VAT بسته است")


def _lock_doc_if_period_closed(*, company: str, posting_date, doctype_fa: str, action_fa: str):
    period = find_closed_vat_period(company, posting_date)
    if period:
        _throw_period_locked(action_fa=action_fa, doctype_fa=doctype_fa, posting_date=str(getdate(posting_date)), period=period)


def _lock_amend_if_needed(*, doc, company: str, doctype: str, doctype_fa: str):
    amended_from = doc.get("amended_from")
    if not amended_from:
        return
    src = frappe.db.get_value(doctype, amended_from, ["posting_date"], as_dict=True)
    if not src or not src.get("posting_date"):
        return

    period = find_closed_vat_period(company, src["posting_date"])
    if period:
        msg = (
            f"{doctype_fa} مرجع ({amended_from}) داخل دوره VAT بسته است.\n"
            f"دوره: {period['name']} | بازه: {period['start']} تا {period['end']}\n"
            f"ایجاد/ارسال اصلاحیه (Amend) برای دوره بسته ممنوع است."
        )
        frappe.throw(msg, title="اصلاحیه در دوره بسته ممنوع است")


def _get_vat_accounts(company: str) -> set[str]:
    out: set[str] = set()

    try:
        s = get_bh_settings()
        if getattr(s, "default_sales_vat_account", None):
            out.add(s.default_sales_vat_account)
        if getattr(s, "default_purchase_vat_account", None):
            out.add(s.default_purchase_vat_account)
    except Exception:
        pass

    rows = frappe.get_all("Account", filters={"company": company, "is_group": 0}, fields=["name"])
    for r in rows:
        n = r["name"] or ""
        if "مالیات بر ارزش افزوده" not in n:
            continue
        if "پرداختنی" in n or "دریافتنی" in n:
            out.add(n)

    return out


def _touches_vat_accounts_in_je(doc, vat_accounts: set[str]) -> bool:
    for row in (doc.get("accounts") or []):
        acc = row.get("account")
        if acc and acc in vat_accounts:
            return True
    return False


def _touches_vat_accounts_in_payment_entry(doc, vat_accounts: set[str]) -> bool:
    for acc in [doc.get("paid_from"), doc.get("paid_to")]:
        if acc and acc in vat_accounts:
            return True
    for row in (doc.get("deductions") or []):
        acc = row.get("account")
        if acc and acc in vat_accounts:
            return True
    return False


def _is_bh_vat_settlement_je(je_name: str) -> bool:
    if not je_name:
        return False
    return bool(frappe.db.exists("BH VAT Period", {"docstatus": 1, "settlement_journal_entry": je_name}))


def _forbid_manual_vat_touch(doctype_fa: str):
    msg = (
        f"{doctype_fa} شما شامل حساب‌های VAT است.\n"
        f"دست‌کاری دستی حساب‌های VAT ممنوع است و فقط از مسیر «تسویه دوره VAT» مجاز می‌باشد."
    )
    frappe.throw(msg, title="دست‌کاری VAT ممنوع است")


def _vat_affecting_guard(*, doc, company: str, posting_date, doctype_fa: str, touches_vat: bool, allow_if_settlement: bool = True):
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa=doctype_fa, action_fa="ثبت/ارسال/ابطال")

    if not touches_vat:
        return

    if allow_if_settlement:
        if getattr(frappe.flags, "bh_vat_settlement", False):
            return
        if doc.doctype == "Journal Entry" and _is_bh_vat_settlement_je(doc.name):
            return

    _forbid_manual_vat_touch(doctype_fa)


def bh_before_validate_sales_invoice(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    _lock_amend_if_needed(doc=doc, company=company, doctype="Sales Invoice", doctype_fa="فاکتور فروش")
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa="فاکتور فروش", action_fa="ذخیره/ویرایش")


def bh_before_submit_sales_invoice(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    _lock_amend_if_needed(doc=doc, company=company, doctype="Sales Invoice", doctype_fa="فاکتور فروش")
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa="فاکتور فروش", action_fa="ارسال (Submit)")


def bh_before_cancel_sales_invoice(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa="فاکتور فروش", action_fa="ابطال (Cancel)")


def bh_before_validate_purchase_invoice(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    _lock_amend_if_needed(doc=doc, company=company, doctype="Purchase Invoice", doctype_fa="فاکتور خرید")
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa="فاکتور خرید", action_fa="ذخیره/ویرایش")


def bh_before_submit_purchase_invoice(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    _lock_amend_if_needed(doc=doc, company=company, doctype="Purchase Invoice", doctype_fa="فاکتور خرید")
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa="فاکتور خرید", action_fa="ارسال (Submit)")


def bh_before_cancel_purchase_invoice(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    _lock_doc_if_period_closed(company=company, posting_date=posting_date, doctype_fa="فاکتور خرید", action_fa="ابطال (Cancel)")


def bh_before_submit_journal_entry(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    vat_accounts = _get_vat_accounts(company)
    touches = _touches_vat_accounts_in_je(doc, vat_accounts)
    _vat_affecting_guard(doc=doc, company=company, posting_date=posting_date, doctype_fa="ثبت روزنامه", touches_vat=touches)


def bh_before_cancel_journal_entry(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    vat_accounts = _get_vat_accounts(company)
    touches = _touches_vat_accounts_in_je(doc, vat_accounts)
    _vat_affecting_guard(doc=doc, company=company, posting_date=posting_date, doctype_fa="ثبت روزنامه", touches_vat=touches)


def bh_before_submit_payment_entry(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    vat_accounts = _get_vat_accounts(company)
    touches = _touches_vat_accounts_in_payment_entry(doc, vat_accounts)
    _vat_affecting_guard(doc=doc, company=company, posting_date=posting_date, doctype_fa="ثبت پرداخت", touches_vat=touches, allow_if_settlement=False)


def bh_before_cancel_payment_entry(doc, method=None):
    company = doc.get("company")
    posting_date = doc.get("posting_date")
    vat_accounts = _get_vat_accounts(company)
    touches = _touches_vat_accounts_in_payment_entry(doc, vat_accounts)
    _vat_affecting_guard(doc=doc, company=company, posting_date=posting_date, doctype_fa="ثبت پرداخت", touches_vat=touches, allow_if_settlement=False)
