# apps/blue_hesab/blue_hesab/bh_core/bh_settings_core.py
from __future__ import annotations

import frappe

def get_bh_settings(company: str | None = None) -> dict:
    """
    Canonical BH Settings fetcher.
    Single DocType: "BH Settings" (Singleton).
    company is optional; keep it for future per-company expansion.
    """
    doc = frappe.get_cached_doc("BH Settings", "BH Settings")
    data = doc.as_dict()

    # optional: resolve company (keeps behavior deterministic)
    resolved = company or data.get("default_company")
    data["_resolved_company"] = resolved

    return data
