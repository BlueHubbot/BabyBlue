# apps/blue_hesab/blue_hesab/patches/v1_0/create_bh_vat_profile_fields.py
from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """ایجاد فیلدهای لینک BH VAT Profile روی Item / Customer / Supplier.

    این پچ idempotent است؛ اگر فیلدها از قبل وجود داشته باشند، آپدیت می‌شوند.
    """

    custom_fields = {
        "Item": [
            {
                "fieldname": "bh_vat_profile",
                "label": "پروفایل VAT (ایران)",
                "fieldtype": "Link",
                "options": "BH VAT Profile",
                "insert_after": "item_group",
                "reqd": 0,
                "print_hide": 0,
                "hidden": 0
            }
        ],
        "Customer": [
            {
                "fieldname": "bh_default_vat_profile",
                "label": "پروفایل پیش‌فرض VAT (ایران)",
                "fieldtype": "Link",
                "options": "BH VAT Profile",
                "insert_after": "customer_group",
                "reqd": 0,
                "print_hide": 0,
                "hidden": 0
            }
        ],
        "Supplier": [
            {
                "fieldname": "bh_default_vat_profile",
                "label": "پروفایل پیش‌فرض VAT (ایران)",
                "fieldtype": "Link",
                "options": "BH VAT Profile",
                "insert_after": "supplier_group",
                "reqd": 0,
                "print_hide": 0,
                "hidden": 0
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)
