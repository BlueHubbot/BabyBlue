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

from . import versioning as _bh_ver


# ---- Stable constants (do NOT rename; regress imports rely on these) ----
LEGAL_SCHEMA_VERSION_DEFAULT = _bh_ver.get_schema_version()
LEGAL_GENERATOR_BUILD_DEFAULT = _bh_ver.get_generator_build()

OUTPUT_VAT_INVOICE = "VAT_INVOICE"
OUTPUT_TTMS_EXPORT = "TTMS_EXPORT"
OUTPUT_MODIAN_PAYLOAD = "MODIAN_PAYLOAD"


def _get_bh_settings() -> "frappe._dict":
    """Singleton settings. Keep minimal; per-company boundary stays in output rows."""
    try:
        return frappe.get_single("BH Settings")  # type: ignore
    except Exception:
        return frappe._dict({})


def enabled_output_types(settings: dict) -> tuple[list[str], dict[str, int]]:
    """
    Legacy signature (kept): enabled_output_types(settings_dict) -> (list[str], flags)
    """
    out: list[str] = []
    flags: dict[str, int] = {}
    if int(settings.get("enable_vat", 0) or 0):
        out.append(OUTPUT_VAT_INVOICE)
        flags[OUTPUT_VAT_INVOICE] = 1
    if int(settings.get("enable_ttms", 0) or 0):
        out.append(OUTPUT_TTMS_EXPORT)
        flags[OUTPUT_TTMS_EXPORT] = 1
    if int(settings.get("enable_modian", 0) or 0):
        out.append(OUTPUT_MODIAN_PAYLOAD)
        flags[OUTPUT_MODIAN_PAYLOAD] = 1
    return out, flags


def get_schema_version(company: Optional[str] = None, output_type: Optional[str] = None) -> str:
    """schema_version MUST match Git tag (apps/blue_hesab/VERSION)."""
    return _bh_ver.get_schema_version()


def get_generator_build(company: Optional[str] = None) -> str:
    """generator_build default == schema_version (tag)."""
    return _bh_ver.get_generator_build()

# Backwards-compat alias (some older code/tests imported these)
SCHEMA_VERSION = LEGAL_SCHEMA_VERSION_DEFAULT
GENERATOR_BUILD = LEGAL_GENERATOR_BUILD_DEFAULT


# === BH HOTFIX: enabled_output_types(company=...) compat + canonical codes ===
# هدف: جلوگیری از TypeError و برگرداندن کدهای واقعی خروجی‌ها:
# VAT_INVOICE / TTMS_EXPORT / MODIAN_PAYLOAD
def enabled_output_types(*args, company=None, **kwargs):
    ctx = kwargs.get("ctx")
    if company is None:
        company = kwargs.get("company")
    if company is None and isinstance(ctx, dict):
        company = ctx.get("company")

    from .bh_settings import get_bh_settings  # shim -> bh_settings_core
    try:
        s = get_bh_settings(company=company) if company else get_bh_settings()
    except TypeError:
        s = get_bh_settings()

    out = []
    if getattr(s, "enable_vat", 0):
        out.append("VAT_INVOICE")
    if getattr(s, "enable_ttms", 0):
        out.append("TTMS_EXPORT")
    if getattr(s, "enable_modian", 0):
        out.append("MODIAN_PAYLOAD")
    return out
