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
    """
    VAT enforcement scope:

    - Global switches must be on.
    - If company is None/empty: behave as before (True) because caller may be in generic context.
    - If company has a legal profile: follow that profile.
    - If company has NO legal profile: enforce ONLY for BH Settings default_company (scope guard).
    """
    # Global switch
    if not is_iran_mode_enabled():
        return False
    if not is_vat_globally_enabled():
        return False

    if not company:
        return True

    # If profile exists: obey it
    p = get_company_legal_profile(company)
    if p:
        try:
            # support both dict/doc style
            if hasattr(p, "vat_enabled"):
                return bool(p.vat_enabled)
            if hasattr(p, "enable_vat"):
                return bool(p.enable_vat)
            if isinstance(p, dict):
                if "vat_enabled" in p:
                    return bool(p.get("vat_enabled"))
                if "enable_vat" in p:
                    return bool(p.get("enable_vat"))
            # fallback: if profile exists but field unknown, be conservative
            return True
        except Exception:
            return True

    # NO profile => enforce only for default_company
    try:
        s = frappe.get_single("BH Settings")
        default_company = getattr(s, "default_company", None) or getattr(s, "company", None)
    except Exception:
        default_company = None

    return bool(default_company) and (company == default_company)



def should_enforce_dimensions(company: Optional[str]) -> bool:
    """
    Dimensions enforcement scope should match VAT scope guard.
    """
    if not is_iran_mode_enabled():
        return False

    if not company:
        return True

    p = get_company_legal_profile(company)
    if p:
        try:
            if hasattr(p, "enforce_dimensions"):
                return bool(p.enforce_dimensions)
            if hasattr(p, "dimensions_enforced"):
                return bool(p.dimensions_enforced)
            if isinstance(p, dict):
                if "enforce_dimensions" in p:
                    return bool(p.get("enforce_dimensions"))
                if "dimensions_enforced" in p:
                    return bool(p.get("dimensions_enforced"))
            return True
        except Exception:
            return True

    # NO profile => enforce only for default_company
    try:
        s = frappe.get_single("BH Settings")
        default_company = getattr(s, "default_company", None) or getattr(s, "company", None)
    except Exception:
        default_company = None

    return bool(default_company) and (company == default_company)



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
