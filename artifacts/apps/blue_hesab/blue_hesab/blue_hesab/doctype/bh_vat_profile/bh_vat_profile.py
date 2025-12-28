# /home/frappe/frappe-bench/apps/blue_hesab/blue_hesab/blue_hesab/doctype/bh_vat_profile/bh_vat_profile.py
from __future__ import annotations

import frappe
from frappe.model.document import Document


class BHVATProfile(Document):
    """پروفایل VAT ایران برای BlueHesab.

    این DocType فقط مدل داده است؛ منطق روی آن بعداً در bh_core/vat_hooks.py سوار می‌شود.
    """
    pass
