import frappe

from blue_hesab.bh_core import get_bh_settings, is_iran_mode_enabled
from blue_hesab import bh_vat


def _log(msg: str, **kwargs):
    try:
        logger = frappe.logger("blue_hesab")
        logger.info(msg, kwargs)
    except Exception:
        print("[BLUE_HESAB]", msg, kwargs)


def _feature_enabled(flag: str) -> bool:
    try:
        s = get_bh_settings()
        return bool(getattr(s, flag, 0))
    except Exception:
        return False


# -------------------
# Sales Invoice hooks
# -------------------

def on_sales_invoice_validate(doc, method=None):
    if not is_iran_mode_enabled():
        return
    bh_vat.apply_vat_on_sales_invoice(doc)
    _log("SI.validate", name=getattr(doc, "name", None))


def on_sales_invoice_submit(doc, method=None):
    if not is_iran_mode_enabled():
        return
    _log("SI.on_submit", name=getattr(doc, "name", None))


def on_sales_invoice_cancel(doc, method=None):
    if not is_iran_mode_enabled():
        return
    _log("SI.on_cancel", name=getattr(doc, "name", None))


# ----------------------
# Purchase Invoice hooks
# ----------------------

def on_purchase_invoice_validate(doc, method=None):
    if not is_iran_mode_enabled():
        return
    bh_vat.apply_vat_on_purchase_invoice(doc)
    _log("PI.validate", name=getattr(doc, "name", None))


def on_purchase_invoice_submit(doc, method=None):
    if not is_iran_mode_enabled():
        return
    _log("PI.on_submit", name=getattr(doc, "name", None))


def on_purchase_invoice_cancel(doc, method=None):
    if not is_iran_mode_enabled():
        return
    _log("PI.on_cancel", name=getattr(doc, "name", None))


# ----------------
# Payroll / Salary
# ----------------

def on_payroll_entry_submit(doc, method=None):
    if not is_iran_mode_enabled() or not _feature_enabled("enable_payroll_legal_exports"):
        return
    _log("PE.on_submit", name=getattr(doc, "name", None))


def on_payroll_entry_cancel(doc, method=None):
    if not is_iran_mode_enabled() or not _feature_enabled("enable_payroll_legal_exports"):
        return
    _log("PE.on_cancel", name=getattr(doc, "name", None))


def on_salary_slip_submit(doc, method=None):
    if not is_iran_mode_enabled() or not _feature_enabled("enable_payroll_legal_exports"):
        return
    _log("SS.on_submit", name=getattr(doc, "name", None))


def on_salary_slip_cancel(doc, method=None):
    if not is_iran_mode_enabled() or not _feature_enabled("enable_payroll_legal_exports"):
        return
    _log("SS.on_cancel", name=getattr(doc, "name", None))
