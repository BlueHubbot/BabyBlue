from __future__ import annotations

import frappe


from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
def ensure_item_bh_vat_profile_field() -> bool:
    """Creates Custom Field Item.bh_vat_profile (Link -> BH VAT Profile) if missing."""
    frappe.reload_doc("core", "doctype", "custom_field")

    meta = frappe.get_meta("Item")
    if meta.has_field("bh_vat_profile"):
        return False

    insert_after = "item_tax_template" if meta.has_field("item_tax_template") else "disabled"

    cf = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Item",
        "fieldname": "bh_vat_profile",
        "label": "BH VAT Profile",
        "fieldtype": "Link",
        "options": "BH VAT Profile",
        "insert_after": insert_after,
        "reqd": 0,
        "read_only": 0,
        "no_copy": 0,
        "print_hide": 0,
    })
    cf.insert(ignore_permissions=True)
    return True
