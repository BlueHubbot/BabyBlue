from __future__ import annotations

import frappe

from .bh_core import get_bh_settings, debug_print_settings


def auto_configure_vat_defaults() -> None:
    """Set sensible default VAT fields in BH Settings for Iran."""
    settings = get_bh_settings()

    # پایه‌ها
    if not settings.default_company:
        companies = frappe.get_all(
            "Company",
            fields=["name", "default_currency"],
            limit=1,
        )
        if companies:
            settings.default_company = companies[0].name
            if not settings.base_currency:
                settings.base_currency = companies[0].default_currency or "IRR"

    settings.enable_iran_mode = 1
    settings.enable_vat = 1

    # VAT فروش
    if not settings.default_sales_vat_account:
        acc = frappe.get_all(
            "Account",
            filters={"account_name": ["like", "%مالیات%"]},
            fields=["name"],
            limit=1,
        )
        if acc:
            settings.default_sales_vat_account = acc[0].name

    if not settings.default_sales_vat_rate:
        settings.default_sales_vat_rate = 9.0

    # VAT خرید
    if not settings.default_purchase_vat_account:
        acc = frappe.get_all(
            "Account",
            filters={"account_name": ["like", "%بدهکاران%"]},
            fields=["name"],
            limit=1,
        )
        if acc:
            settings.default_purchase_vat_account = acc[0].name

    if not settings.default_purchase_vat_rate:
        settings.default_purchase_vat_rate = 9.0

    settings.save(ignore_permissions=True)
    frappe.db.commit()

    print("BH Settings VAT configured:")
    debug_print_settings()
