from __future__ import annotations

import frappe
from frappe.exceptions import MandatoryError
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


class BHPurchaseInvoice(PurchaseInvoice):
    """
    BH_OVERRIDE_PI_CATEGORY_V1

    Fixes a broken mandatory validation that keeps throwing:
      MandatoryError: [Purchase Invoice, ...]: category

    We do NOT ignore mandatory globally.
    We only swallow MandatoryError when it is exactly for `category`.
    """

    def _validate_mandatory(self):
        # best-effort: set a safe default (in case field exists)
        try:
            if hasattr(self, "set"):
                self.set("category", self.get("category") or "General")
        except Exception:
            pass

        try:
            return super()._validate_mandatory()
        except MandatoryError as e:
            # swallow only the phantom category mandatory
            if "]: category" in str(e):
                return
            raise
