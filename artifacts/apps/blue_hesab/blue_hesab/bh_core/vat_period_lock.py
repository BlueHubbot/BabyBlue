from __future__ import annotations
import frappe
from frappe import _

def _get(doc, key: str):
    if hasattr(doc, key):
        return getattr(doc, key)
    return (doc or {}).get(key)

def _find_closed_period(company: str, posting_date) -> str | None:
    if not company or not posting_date:
        return None
    return frappe.db.get_value(
        "BH VAT Period",
        {
            "company": company,
            "docstatus": 1,
            "status": "Closed",
            "period_start_date": ["<=", posting_date],
            "period_end_date": [">=", posting_date],
        },
        "name",
    )

def _block_if_closed(doc, label: str):
    company = _get(doc, "company")
    posting_date = _get(doc, "posting_date")
    period = _find_closed_period(company, posting_date)
    if period:
        frappe.throw(
            _("این سند داخل دوره VAT بسته‌شده است و اجازه ثبت/لغو ندارد. دوره: {0}").format(period)
        )

def bh_before_submit_sales_invoice(doc, method=None):
    _block_if_closed(doc, "Sales Invoice")

def bh_before_cancel_sales_invoice(doc, method=None):
    _block_if_closed(doc, "Sales Invoice")

def bh_before_submit_purchase_invoice(doc, method=None):
    _block_if_closed(doc, "Purchase Invoice")

def bh_before_cancel_purchase_invoice(doc, method=None):
    _block_if_closed(doc, "Purchase Invoice")

def bh_before_submit_sales_invoice(doc, method=None):
    _guard(doc, "Sales Invoice (Submit)")

def bh_before_submit_purchase_invoice(doc, method=None):
    _guard(doc, "Purchase Invoice (Submit)")

def bh_before_cancel_sales_invoice(doc, method=None):
    _guard(doc, "Sales Invoice (Cancel)")

def bh_before_cancel_purchase_invoice(doc, method=None):
    _guard(doc, "Purchase Invoice (Cancel)")

def bh_before_submit_sales_invoice(doc, method=None):
    return before_validate_sales_invoice(doc, method)

def bh_before_submit_purchase_invoice(doc, method=None):
    return before_validate_purchase_invoice(doc, method)

def bh_before_cancel_sales_invoice(doc, method=None):
    return before_cancel_sales_invoice(doc, method)

def bh_before_cancel_purchase_invoice(doc, method=None):
    return before_cancel_purchase_invoice(doc, method)
