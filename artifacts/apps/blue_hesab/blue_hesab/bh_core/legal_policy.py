# -*- coding: utf-8 -*-
"""
BlueHesab Legal Outputs — Policy (BH Legal Output)
Authoritative, stable API surface for regress suites:
- LEGAL_SCHEMA_VERSION_DEFAULT
- get_schema_version(), get_generator_build()
- enabled_output_types() / _enabled_output_types()
"""

from __future__ import annotations

from typing import List, Optional

import frappe


# ---- Stable constants (do NOT rename; regress imports rely on these) ----
LEGAL_SCHEMA_VERSION_DEFAULT = "LEGAL-V1"
LEGAL_GENERATOR_BUILD_DEFAULT = "BH-DEV"

OUTPUT_VAT_INVOICE = "VAT_INVOICE"
OUTPUT_TTMS_EXPORT = "TTMS_EXPORT"
OUTPUT_MODIAN_PAYLOAD = "MODIAN_PAYLOAD"


def _get_bh_settings() -> "frappe._dict":
    """Singleton settings. Keep minimal; per-company boundary stays in output rows."""
    try:
        return frappe.get_single("BH Settings")  # type: ignore
    except Exception:
        return frappe._dict({})


def enabled_output_types(company: Optional[str] = None) -> List[str]:
    """
    Returns enabled legal output types based on BH Settings toggles.
    `company` is accepted for future per-company overrides (but currently settings are singleton).
    """
    s = _get_bh_settings()

    out: List[str] = []
    try:
        if int(getattr(s, "enable_vat", 0) or 0) == 1:
            out.append(OUTPUT_VAT_INVOICE)
        if int(getattr(s, "enable_ttms", 0) or 0) == 1:
            out.append(OUTPUT_TTMS_EXPORT)
        if int(getattr(s, "enable_modian", 0) or 0) == 1:
            out.append(OUTPUT_MODIAN_PAYLOAD)
    except Exception:
        # safest fallback: keep VAT enabled by default if settings read fails
        out = [OUTPUT_VAT_INVOICE]

    # make deterministic ordering for regress outputs
    order = {OUTPUT_VAT_INVOICE: 10, OUTPUT_TTMS_EXPORT: 20, OUTPUT_MODIAN_PAYLOAD: 30}
    out.sort(key=lambda x: order.get(x, 999))
    return out


def get_schema_version(company: Optional[str] = None, output_type: Optional[str] = None) -> str:
    """Schema version for legal outputs. Keep stable unless you bump DB schema intentionally."""
    # Future: per-company legal profile override
    return LEGAL_SCHEMA_VERSION_DEFAULT


def get_generator_build(company: Optional[str] = None) -> str:
    """Build identifier for audit. Override later from CI tag if needed."""
    return LEGAL_GENERATOR_BUILD_DEFAULT
