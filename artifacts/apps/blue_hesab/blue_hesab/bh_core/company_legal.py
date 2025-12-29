from __future__ import annotations

from typing import Optional, Tuple

import frappe
from frappe.utils import flt

from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error


def _bh_settings_safe():
    try:
        return frappe.get_single("BH Settings")
    except Exception:
        return None


def get_company_legal_profile(company: Optional[str]):
    if not company:
        return None
    try:
        name = frappe.db.get_value("BH Company Legal Profile", {"company": company}, "name")
        if not name:
            return None
        return frappe.get_doc("BH Company Legal Profile", name)
    except Exception:
        return None


def require_company_legal_profile(company: str):
    p = get_company_legal_profile(company)
    if p:
        return p
    raise_bh_vat_error(
        BH_VAT_E_GENERIC,
        f"BH VAT: برای شرکت «{company}» پروفایل قانونی تعریف نشده است. "
        f"از مسیر «BH Company Legal Profile» یک رکورد بسازید و VAT را برای این شرکت فعال کنید.",
        context={"company": company},
    )


def is_iran_mode_enabled() -> bool:
    s = _bh_settings_safe()
    try:
        return bool(int(getattr(s, "enable_iran_mode", 0) or 0) == 1)
    except Exception:
        return True


def is_vat_globally_enabled() -> bool:
    s = _bh_settings_safe()
    try:
        return bool(int(getattr(s, "enable_vat", 0) or 0) == 1)
    except Exception:
        return True


def is_vat_enabled_for_company(company: Optional[str]) -> bool:
    # Global switch
    if not is_iran_mode_enabled():
        return False
    if not is_vat_globally_enabled():
        return False

    if not company:
        return True

    p = get_company_legal_profile(company)
    if not p:
        # In HARD mode, treat missing profile as enforced (so code raises explicit config errors).
        return True
    try:
        return bool(int(getattr(p, "enable_vat", 0) or 0) == 1)
    except Exception:
        return True


def should_enforce_dimensions(company: Optional[str]) -> bool:
    if not is_iran_mode_enabled():
        return False

    if not company:
        return True

    p = get_company_legal_profile(company)
    if not p:
        return True

    try:
        return bool(int(getattr(p, "enforce_dimensions", 0) or 0) == 1)
    except Exception:
        return True


def get_vat_account_and_rate(company: Optional[str], *, kind: str) -> Tuple[Optional[str], float]:
    """Resolve VAT account + rate from BH Company Legal Profile (fallback: BH Settings only for migration)."""
    p = get_company_legal_profile(company) if company else None
    if p and int(getattr(p, "enable_vat", 0) or 0) == 1:
        if kind == "sales":
            return getattr(p, "default_sales_vat_account", None), flt(getattr(p, "default_sales_vat_rate", 0) or 0)
        if kind == "purchase":
            return getattr(p, "default_purchase_vat_account", None), flt(getattr(p, "default_purchase_vat_rate", 0) or 0)

    # fallback to BH Settings (legacy)
    s = _bh_settings_safe()
    if not s:
        return None, 0.0

    if kind == "sales":
        return getattr(s, "default_sales_vat_account", None), flt(getattr(s, "default_sales_vat_rate", 0) or 0)
    if kind == "purchase":
        return getattr(s, "default_purchase_vat_account", None), flt(getattr(s, "default_purchase_vat_rate", 0) or 0)

    return None, 0.0
