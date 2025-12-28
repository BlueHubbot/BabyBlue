import frappe
from blue_hesab.bh_core import get_bh_settings, is_iran_mode_enabled


def _get_settings():
    return get_bh_settings()


def _log(msg: str, **kw):
    try:
        logger = frappe.logger("blue_hesab_vat")
        logger.info(msg, kw)
    except Exception:
        print("[BLUE_HESAB_VAT]", msg, kw)


def apply_vat_on_sales_invoice(doc):
    if not is_iran_mode_enabled():
        return

    s = _get_settings()
    if not getattr(s, "enable_vat", 0):
        return

    account = getattr(s, "default_sales_vat_account", None)
    rate = getattr(s, "default_sales_vat_rate", None)

    if not account or rate is None:
        _log("SI VAT skipped (no account/rate in BH Settings)", name=getattr(doc, "name", None))
        return

    # اگر قبلاً همین VAT اضافه شده، کاری نکن
    for row in (doc.taxes or []):
        if getattr(row, "account_head", None) == account and float(getattr(row, "rate", 0) or 0) == float(rate):
            return

    tax_row = doc.append("taxes", {})
    tax_row.charge_type = "On Net Total"
    tax_row.account_head = account
    tax_row.rate = rate
    tax_row.description = f"VAT {rate}% (BlueHesab)"
    tax_row.included_in_print_rate = 0

    _log("SI VAT row added", name=getattr(doc, "name", None), account=account, rate=rate)


def apply_vat_on_purchase_invoice(doc):
    if not is_iran_mode_enabled():
        return

    s = _get_settings()
    if not getattr(s, "enable_vat", 0):
        return

    account = getattr(s, "default_purchase_vat_account", None)
    rate = getattr(s, "default_purchase_vat_rate", None)

    if not account or rate is None:
        _log("PI VAT skipped (no account/rate in BH Settings)", name=getattr(doc, "name", None))
        return

    for row in (doc.taxes or []):
        if getattr(row, "account_head", None) == account and float(getattr(row, "rate", 0) or 0) == float(rate):
            return

    tax_row = doc.append("taxes", {})
    tax_row.charge_type = "On Net Total"
    tax_row.account_head = account
    tax_row.rate = rate
    tax_row.description = f"VAT {rate}% (BlueHesab)"
    tax_row.included_in_print_rate = 0

    _log("PI VAT row added", name=getattr(doc, "name", None), account=account, rate=rate)
