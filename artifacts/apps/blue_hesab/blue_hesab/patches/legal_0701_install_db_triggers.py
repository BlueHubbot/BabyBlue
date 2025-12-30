from __future__ import annotations

import frappe


def execute():
    """LEGAL-07 Hardening: best-effort DB immutability triggers.

    IMPORTANT: must never break migrate. If DB user lacks TRIGGER privilege, we skip and log.
    """
    try:
        if not frappe.db.exists("DocType", "BH Legal Output"):
            return
        from blue_hesab.bh_core.legal_immutability import install_db_triggers
        install_db_triggers()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "BH LEGAL-07: install_db_triggers skipped")
