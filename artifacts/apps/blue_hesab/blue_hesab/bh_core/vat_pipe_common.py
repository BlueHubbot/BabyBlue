from __future__ import annotations

from typing import Optional

import frappe


# ----------------------------
# Canonical VAT enums (BH)
# ----------------------------

KIND_SALES = "sales"
KIND_PURCHASE = "purchase"

AXIS_EXCL = "EXCL"
AXIS_INCL = "INCL"

# Back-compat aliases used across older/newer modules
VAT_AXIS_EXCL = AXIS_EXCL
VAT_AXIS_INCL = AXIS_INCL

MODE_EXCLUSIVE = "Exclusive"
MODE_INCLUSIVE = "Inclusive"

# Back-compat aliases
MODE_EXCL = MODE_EXCLUSIVE
MODE_INCL = MODE_INCLUSIVE
VAT_PRICE_MODE_EXCL = MODE_EXCLUSIVE
VAT_PRICE_MODE_INCL = MODE_INCLUSIVE

VALID_PRICE_MODES = (MODE_EXCLUSIVE, MODE_INCLUSIVE)


def normalize_axis(axis: Optional[str]) -> str:
    a = (axis or "").strip().upper()
    if a in ("INCL", "INCLUSIVE", "I"):
        return AXIS_INCL
    if a in ("EXCL", "EXCLUSIVE", "E"):
        return AXIS_EXCL
    return AXIS_EXCL


def normalize_price_mode(mode: Optional[str]) -> str:
    m = (mode or "").strip().lower()
    if m in ("incl", "inclusive", "include", "included", "۱", "1", "true", "yes"):
        return MODE_INCLUSIVE
    if m in ("excl", "exclusive", "exclude", "excluded", "۰", "0", "false", "no"):
        return MODE_EXCLUSIVE
    return MODE_EXCLUSIVE


def axis_from_price_mode(mode: Optional[str]) -> str:
    return AXIS_INCL if normalize_price_mode(mode) == MODE_INCLUSIVE else AXIS_EXCL


def price_mode_from_axis(axis: Optional[str]) -> str:
    return MODE_INCLUSIVE if normalize_axis(axis) == AXIS_INCL else MODE_EXCLUSIVE


def axis_from_template_name(template: Optional[str]) -> Optional[str]:
    t = (template or "").strip()
    if not t:
        return None
    u = t.upper()
    if "(INCL)" in u or " INCL" in u:
        return AXIS_INCL
    if "(EXCL)" in u or " EXCL" in u:
        return AXIS_EXCL
    return None


def company_abbr(company: str) -> str:
    c = (company or "").strip()
    if not c:
        return "BA"
    try:
        abbr = frappe.db.get_value("Company", c, "abbr")
        abbr = (abbr or "").strip()
        if abbr:
            return abbr
    except Exception:
        pass
    toks = [x for x in c.replace("-", " ").split() if x]
    if toks:
        return toks[-1][:5].upper()
    return c[:5].upper()


def _kind_label(kind: str) -> str:
    k = (kind or "").strip().lower()
    if k in (KIND_PURCHASE, "purchase", "pi", "purchase invoice"):
        return "Purchase"
    return "Sales"

def norm(s):
    """Normalize user input for internal comparisons."""
    if s is None:
        return ""
    return str(s).strip()


def label_for_kind(kind: str) -> str:
    """Human label used in template naming: Sales / Purchase"""
    k = norm(kind).lower()
    if k in ("sales", "sale", "si", "sales_invoice", "sales invoice"):
        return "Sales"
    if k in ("purchase", "buy", "pi", "purchase_invoice", "purchase invoice"):
        return "Purchase"
    return (norm(kind) or "").title()


def doctype_for_kind(kind: str) -> str:
    """
    MUST return the TEMPLATE doctype (not the invoice doctype).
    This is used by infer_mixed_template_name() to check template existence.
    """
    k = norm(kind).lower()
    if k in ("sales", "sale", "si", "sales_invoice", "sales invoice"):
        return "Sales Taxes and Charges Template"
    if k in ("purchase", "buy", "pi", "purchase_invoice", "purchase invoice"):
        return "Purchase Taxes and Charges Template"
    # safe fallback
    return "Sales Taxes and Charges Template"



def infer_mixed_template_name(
    *,
    kind: str,
    company: str,
    axis: Optional[str] = None,
    mode: Optional[str] = None,
    price_mode: Optional[str] = None,
) -> str:
    """
    BH MIXED Taxes & Charges Template name.

    ✅ Backward-compatible:
      - accepts both `mode` and `price_mode`
    """
    eff_mode = mode if (mode is not None and str(mode).strip() != "") else price_mode
    if eff_mode is not None and str(eff_mode).strip() != "":
        eff_axis = axis_from_price_mode(eff_mode)
    else:
        eff_axis = normalize_axis(axis)

    label = _kind_label(kind)
    abbr = company_abbr(company)
    return f"BH VAT MIXED {label} ({eff_axis}) - {abbr}"


def is_mixed_template(template: Optional[str], kind: Optional[str] = None) -> bool:
    t = (template or "").strip()
    if not t:
        return False
    k = (kind or "").strip().lower()
    if k and k in (KIND_SALES, "sales", "si", "sales invoice"):
        return t.startswith("BH VAT MIXED Sales")
    if k and k in (KIND_PURCHASE, "purchase", "pi", "purchase invoice"):
        return t.startswith("BH VAT MIXED Purchase")
    return t.startswith("BH VAT MIXED Sales") or t.startswith("BH VAT MIXED Purchase")


def bh_vat_enforced(company: str) -> bool:
    """
    VAT-10 scope: enforce only on BH Settings.default_company (unless missing => enforce all).
    """
    c = (company or "").strip()
    try:
        default_company = frappe.db.get_single_value("BH Settings", "default_company")
        default_company = (default_company or "").strip()
        if default_company:
            return c == default_company
    except Exception:
        pass
    return True


def in_http_request() -> bool:
    try:
        return bool(getattr(frappe.local, "request", None))
    except Exception:
        return False


def is_submit_action(doc) -> bool:
    try:
        a = getattr(doc, "_action", None)
        if a:
            return str(a).lower() == "submit"
    except Exception:
        pass
    try:
        if hasattr(doc, "get"):
            a2 = doc.get("_action")
            if a2:
                return str(a2).lower() == "submit"
    except Exception:
        pass
    try:
        return bool(getattr(frappe.flags, "in_submit", False))
    except Exception:
        return False


def ui_expected_hint(expected_template: str) -> str:
    exp = (expected_template or "").strip()
    if not exp:
        return ""
    return f"قالب پیشنهادی: {exp}"
