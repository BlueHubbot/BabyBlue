from __future__ import annotations

import frappe
from frappe.model.document import Document
from . import get_bh_settings


def apply_iran_vat(doc: Document, method: str | None = None) -> None:
    """
    قبل از validate روی Sales Invoice اجرا می‌شود.
    اگر Iran Mode و VAT فعال باشد و VAT روی BH Settings ست شده باشد،
    یک ردیف VAT روی جدول Taxes اضافه می‌کند (اگر قبلاً اضافه نشده باشد).
    """
    s = get_bh_settings()

    if not (getattr(s, "enable_iran_mode", 0) and getattr(s, "enable_vat", 0)):
        return

    account = getattr(s, "default_sales_vat_account", None)
    rate = getattr(s, "default_sales_vat_rate", None)

    if not account or not rate:
        return

    # اگر قبلاً ردیفی با همین account_head هست، دوباره نساز
    for tax in (doc.taxes or []):
        if tax.account_head == account:
            return

    tax = doc.append("taxes", {})
    tax.charge_type = "On Net Total"
    tax.account_head = account
    tax.rate = rate
    tax.description = "مالیات و عوارض ارزش افزوده"
    tax.included_in_print_rate = 0
