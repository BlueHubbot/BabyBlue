from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def _insert_after(doctype: str, candidates: list[str], fallback: str) -> str:
    meta = frappe.get_meta(doctype)
    for c in candidates:
        if meta.get_field(c):
            return c
    return fallback


def execute():
    doctype = "BH Settings"

    sales_after = _insert_after(
        doctype,
        candidates=["default_sales_vat_rate", "default_sales_vat_account", "enable_vat"],
        fallback="enable_vat",
    )
    purchase_after = _insert_after(
        doctype,
        candidates=["default_purchase_vat_rate", "default_purchase_vat_account", "enable_vat"],
        fallback="enable_vat",
    )

    fields = {
        doctype: [
            {
                "fieldname": "default_sales_vat_price_mode",
                "label": "نوع قیمت‌گذاری مالیات فروش (پیش‌فرض)",
                "fieldtype": "Select",
                "options": "Exclusive\nInclusive",
                "default": "Exclusive",
                "insert_after": sales_after,
            },
            {
                "fieldname": "default_purchase_vat_price_mode",
                "label": "نوع قیمت‌گذاری مالیات خرید (پیش‌فرض)",
                "fieldtype": "Select",
                "options": "Exclusive\nInclusive",
                "default": "Exclusive",
                "insert_after": purchase_after,
            },
        ]
    }

    create_custom_fields(fields, ignore_validate=True)
