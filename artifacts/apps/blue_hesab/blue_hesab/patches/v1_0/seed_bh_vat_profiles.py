from __future__ import annotations

import frappe
from frappe.utils import flt


def execute():
    """
    ایجاد/آپدیت پروفایل‌های پایه VAT به‌صورت idempotent.

    پروفایل‌ها:
      - STD_9      → مشمول ۹٪ استاندارد (فروش/خرید)
      - ZERO       → صفر درصد
      - EXEMPT     → معاف
      - EXPORT_0   → صادرات (صفر درصد قانونی)

    نکته: برای STD_9 اگر BH Settings حساب VAT فروش/خرید را داشته باشد،
    اینجا روی پروفایل ست می‌کنیم.
    """

    profiles = [
        {
            "vat_code": "STD_9",
            "title": "مشمول ۹٪ استاندارد",
            "vat_type": "Standard",
            "applies_on": "Both",  # اگر options محدود باشد، بعداً با UI درستش می‌کنیم
            "is_export": 0,
            "is_goods": 1,
            "is_service": 1,
            "sales_vat_rate": 9.0,
            "purchase_vat_rate": 9.0,
        },
        {
            "vat_code": "ZERO",
            "title": "صفر درصد (Zero Rated)",
            "vat_type": "Zero Rated",
            "applies_on": "Both",
            "is_export": 0,
            "is_goods": 1,
            "is_service": 1,
            "sales_vat_rate": 0.0,
            "purchase_vat_rate": 0.0,
        },
        {
            "vat_code": "EXEMPT",
            "title": "معاف از VAT",
            "vat_type": "Exempt",
            "applies_on": "Both",
            "is_export": 0,
            "is_goods": 1,
            "is_service": 1,
            "sales_vat_rate": 0.0,
            "purchase_vat_rate": 0.0,
        },
        {
            "vat_code": "EXPORT_0",
            "title": "صادرات (صفر درصد قانونی)",
            "vat_type": "Zero Rated",
            "applies_on": "Sales",
            "is_export": 1,
            "is_goods": 1,
            "is_service": 1,
            "sales_vat_rate": 0.0,
            "purchase_vat_rate": 0.0,
        },
    ]

    sales_account = None
    purchase_account = None

    # سعی می‌کنیم حساب‌های پیش‌فرض را از BH Settings بگیریم
    try:
        bh = frappe.get_single("BH Settings")
        sales_account = getattr(bh, "default_sales_vat_account", None)
        purchase_account = getattr(bh, "default_purchase_vat_account", None)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "BH VAT: load BH Settings failed in seed_bh_vat_profiles",
        )

    for p in profiles:
        vat_code = p["vat_code"]

        try:
            existing_name = frappe.db.get_value(
                "BH VAT Profile",
                filters={"vat_code": vat_code},
                fieldname="name",
            )

            if existing_name:
                doc = frappe.get_doc("BH VAT Profile", existing_name)
            else:
                doc = frappe.new_doc("BH VAT Profile")

            # فیلدهای اصلی
            for key, value in p.items():
                setattr(doc, key, value)

            # فعال بودن
            if not getattr(doc, "active", None) in (0, 1):
                doc.active = 1
            else:
                doc.active = 1

            # فقط برای STD_9 حساب‌ها را از BH Settings ست کن (اگر موجود باشد)
            if vat_code == "STD_9":
                if sales_account:
                    doc.sales_vat_account = sales_account
                if purchase_account:
                    doc.purchase_vat_account = purchase_account

            if existing_name:
                doc.save()
            else:
                doc.insert()

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"BH VAT: seed profile failed ({vat_code})",
            )
