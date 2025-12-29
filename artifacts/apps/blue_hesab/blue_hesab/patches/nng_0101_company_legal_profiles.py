from __future__ import annotations

import frappe


def execute():
    # Ensure doctypes exist
    frappe.reload_doc("blue_hesab", "doctype", "bh_company_legal_profile")

    try:
        s = frappe.get_single("BH Settings")
    except Exception:
        s = None

    default_company = (getattr(s, "default_company", None) or "").strip() if s else ""

    companies = frappe.get_all("Company", pluck="name") or []
    for company in companies:
        exists = frappe.db.exists("BH Company Legal Profile", {"company": company})
        if exists:
            continue

        doc = frappe.new_doc("BH Company Legal Profile")
        doc.company = company

        # Only enable VAT for the default company (explicit boundary). Others remain disabled until configured.
        if s and company and company == default_company:
            doc.enable_vat = int(getattr(s, "enable_vat", 0) or 0)
            doc.default_vat_category = getattr(s, "default_vat_category", None)
            doc.default_sales_vat_account = getattr(s, "default_sales_vat_account", None)
            doc.default_purchase_vat_account = getattr(s, "default_purchase_vat_account", None)
            doc.default_sales_vat_rate = getattr(s, "default_sales_vat_rate", 0) or 0
            doc.default_purchase_vat_rate = getattr(s, "default_purchase_vat_rate", 0) or 0
            doc.auto_vat_on_sales = int(getattr(s, "auto_vat_on_sales", 0) or 0)
            doc.auto_vat_on_purchase = int(getattr(s, "auto_vat_on_purchase", 0) or 0)
            doc.enforce_dimensions = 1
            doc.notes = "Migrated VAT defaults from BH Settings (one-time)."
        else:
            doc.enable_vat = 0
            doc.enforce_dimensions = 1
            doc.notes = "Created by patch. Configure VAT defaults per-company before use."

        doc.insert(ignore_permissions=True)
