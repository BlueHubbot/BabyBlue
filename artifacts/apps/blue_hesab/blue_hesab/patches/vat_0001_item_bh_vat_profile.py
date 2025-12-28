from __future__ import annotations

import frappe
from blue_hesab.bh_core.vat_custom_fields import ensure_item_bh_vat_profile_field


def execute():
    changed = ensure_item_bh_vat_profile_field()
    if changed:
        frappe.db.commit()
