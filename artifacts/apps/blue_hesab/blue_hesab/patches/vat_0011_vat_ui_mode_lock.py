"""VAT-11

UI hardening for MIXED VAT:

1) Ensure custom fields exist and are updated:
   - Sales Invoice.bh_vat_price_mode
   - Purchase Invoice.bh_vat_price_mode
2) Ensure the field is placed near the intended UI section (Taxes by default).

Idempotent: safe to run multiple times.
"""

from __future__ import annotations

import frappe


def execute():
    # 1) Create/update CF + translations + (safe) templates
    from blue_hesab.bh_core.vat_setup import ensure_vat_ui_and_templates

    ensure_vat_ui_and_templates()

    # 2) Enforce UI placement (default: Taxes section)
    from blue_hesab.bh_core.vat_ui_layout import apply_vat_ui_layout

    apply_vat_ui_layout("taxes")

    try:
        frappe.clear_cache()
    except Exception:
        pass
