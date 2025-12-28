# apps/blue_hesab/blue_hesab/bh_core/vat_item_autofill.py
from __future__ import annotations

from typing import Any, Dict, Optional

import frappe

# both old codes and new Persian names (after rename) → code
PROFILE_CODE_MAP: Dict[str, str] = {
    "STD_9": "STD_9",
    "ZERO": "ZERO",
    "EXEMPT": "EXEMPT",
    "EXPORT_0": "EXPORT_0",
    "استاندارد ۹٪": "STD_9",
    "صفر درصد": "ZERO",
    "معاف": "EXEMPT",
    "صادرات ۰٪": "EXPORT_0",
}


def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


def get_default_company(company: Optional[str] = None) -> Optional[str]:
    """Resolve default company with a strict preference order."""
    company = _norm(company)
    if company and frappe.db.exists("Company", company):
        return company

    if frappe.db.exists("DocType", "BH Settings"):
        c = _norm(frappe.db.get_single_value("BH Settings", "default_company"))
        if c and frappe.db.exists("Company", c):
            return c

    c = _norm(frappe.defaults.get_user_default("Company"))
    if c and frappe.db.exists("Company", c):
        return c

    try:
        return frappe.db.get_value("Company", {}, "name")
    except Exception:
        return None


def normalize_profile_code(profile_value: Optional[str]) -> Optional[str]:
    v = _norm(profile_value)
    if not v:
        return None
    return PROFILE_CODE_MAP.get(v)


def guess_item_tax_template(company: str, code: str) -> Optional[str]:
    """Best-effort guess by searching Item Tax Template names/titles for the VAT code."""
    company = _norm(company)
    code = _norm(code)
    if not company or not code:
        return None

    rows = frappe.get_all(
        "Item Tax Template",
        filters={"company": company},
        fields=["name", "title"],
        limit_page_length=500,
    )

    def score(r: Dict[str, Any]) -> int:
        hay = f"{r.get('name','')} {r.get('title','')}"
        s = 0
        if code in hay:
            s += 100
        if "VAT" in hay:
            s += 10
        return s

    best: Optional[str] = None
    best_s = -1
    for r in rows:
        hay = f"{r.get('name','')} {r.get('title','')}"
        if code not in hay:
            continue
        sc = score(r)
        if sc > best_s:
            best_s = sc
            best = r.get("name")
    return _norm(best) or None


def _meta_from_profile(profile: Optional[str], company: Optional[str] = None) -> Dict[str, Any]:
    """Internal: return UI meta dict (company, code, template)."""
    company = get_default_company(company)
    code = normalize_profile_code(profile)
    tmpl = guess_item_tax_template(company, code) if (company and code) else None
    return {"company": company, "code": code, "template": tmpl}


@frappe.whitelist()
def get_default_item_tax_template(profile: Optional[str] = None, company: Optional[str] = None) -> Dict[str, Any]:
    """
    UI API (whitelisted): returns meta dict to auto-fill Item.bh_item_tax_template based on bh_vat_profile.
    JS expects: {company, code, template}
    """
    return _meta_from_profile(profile, company)


def resolve_item_tax_template(item_code: Optional[str], company: Optional[str] = None) -> Optional[str]:
    """
    Server API: returns a template NAME (str) or None for an Item code.

    Priority:
      1) Item.bh_item_tax_template (explicit override)
      2) Item.bh_vat_profile -> code -> guess Item Tax Template in the given company
    """
    item_code = _norm(item_code)
    if not item_code:
        return None

    row = frappe.db.get_value(
        "Item",
        item_code,
        ["bh_item_tax_template", "bh_vat_profile"],
        as_dict=True,
    ) or {}

    tpl = _norm(row.get("bh_item_tax_template"))
    if tpl:
        return tpl

    profile = row.get("bh_vat_profile")
    meta = _meta_from_profile(profile, company)
    return _norm(meta.get("template")) or None


def item_validate(doc, method=None):
    """On Item validate: if profile changed OR template empty, auto-fill bh_item_tax_template."""
    profile = doc.get("bh_vat_profile")
    if not profile:
        return

    prev_profile = None
    if doc.name and not doc.is_new():
        prev_profile = frappe.db.get_value("Item", doc.name, "bh_vat_profile")

    profile_changed = (prev_profile != profile)

    # Rule: auto-set if profile changed OR template empty. Otherwise keep user's manual override.
    if profile_changed or not doc.get("bh_item_tax_template"):
        company = get_default_company()
        meta = _meta_from_profile(profile, company)
        tmpl = _norm(meta.get("template"))
        if tmpl:
            doc.set("bh_item_tax_template", tmpl)
