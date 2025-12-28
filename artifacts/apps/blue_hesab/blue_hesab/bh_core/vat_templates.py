# apps/blue_hesab/blue_hesab/bh_core/vat_templates.py
# BlueHesab VAT Templates (schema-tolerant + canonical naming)
# - Ensure MIXED Sales/Purchase Taxes & Charges Templates (EXCL/INCL)
# - Sync Item Tax Templates from BH VAT Profiles (canonical code + correct rate)
# - Ensure Item custom fields and sync Items' bh_item_tax_template

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import re

import frappe


from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
BH_SETTINGS_DOCTYPE = "BH Settings"
BH_VAT_PROFILE_DOCTYPE = "BH VAT Profile"

# Canonical profile codes and labels (stable)
PROFILE_LABELS = {
    "STD_9": "VAT ۹٪ استاندارد",
    "ZERO": "VAT صفر درصد",
    "EXEMPT": "VAT معاف",
    "EXPORT_0": "VAT صادرات ۰٪",
}


# ---------------- utils ----------------

_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _digits_to_ascii(s: str) -> str:
    return (s or "").translate(_PERSIAN_DIGITS)


def _f(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return float(default)
        return float(v)
    except Exception:
        return float(default)


def _table_cols(doctype: str) -> set:
    try:
        return set(frappe.db.get_table_columns(f"tab{doctype}"))
    except Exception:
        return set()


def _with_abbr(name: str, abbr: str) -> str:
    name = (name or "").strip()
    abbr = (abbr or "").strip()
    if not abbr:
        return name
    suffix = f" - {abbr}"
    if name.endswith(suffix):
        return name
    return name + suffix


def _get_single_settings() -> Any:
    try:
        return frappe.get_single(BH_SETTINGS_DOCTYPE)
    except Exception:
        return frappe.get_doc(BH_SETTINGS_DOCTYPE)


def _get_company(company: Optional[str]) -> str:
    if company:
        return company
    s = _get_single_settings()
    v = getattr(s, "default_company", None)
    if v:
        return v
    c = frappe.get_all("Company", pluck="name", limit_page_length=1)
    if not c:
        raise_bh_vat_error(BH_VAT_E_GENERIC, "No Company found. Set BH Settings.default_company first.")
    return c[0]


def _company_abbr(company: str) -> str:
    try:
        return frappe.db.get_value("Company", company, "abbr") or ""
    except Exception:
        return ""


def _get_vat_accounts_from_settings() -> Tuple[str, str]:
    s = _get_single_settings()
    sales = getattr(s, "default_sales_vat_account", None) or ""
    purchase = getattr(s, "default_purchase_vat_account", None) or ""
    if not sales or not purchase:
        raise_bh_vat_error(BH_VAT_E_GENERIC, 
            "BH Settings VAT accounts are not set. "
            "Set default_sales_vat_account and default_purchase_vat_account."
        )
    return sales, purchase


def _get_default_vat_rate_from_settings(default: float = 9.0) -> float:
    s = _get_single_settings()
    r = getattr(s, "default_sales_vat_rate", None)
    if r is None:
        r = getattr(s, "default_purchase_vat_rate", None)
    return _f(r, default)


def _profile_text(doc: Any) -> str:
    # Best-effort: collect any human-readable fields
    parts = []
    for fn in ("profile_code", "vat_code", "code", "title", "profile_title", "name"):
        v = getattr(doc, fn, None)
        if v:
            parts.append(str(v))
    return " | ".join(parts).strip() or str(getattr(doc, "name", "")).strip()


def _infer_profile_code(text: str) -> str:
    t = _digits_to_ascii(text).lower()

    # priority: export
    if "صادرات" in text or "export" in t:
        return "EXPORT_0"
    if "معاف" in text or "exempt" in t:
        return "EXEMPT"

    # detect 9% (standard)
    if re.search(r"\b9(\.0+)?\b", t) or "۹" in text or "9%" in t or "٪" in text:
        # if text has explicit 9 anywhere it's STD_9
        if "9" in t or "۹" in text:
            return "STD_9"

    # detect zero
    if "صفر" in text or "zero" in t or re.search(r"\b0(\.0+)?\b", t) or "۰" in text:
        return "ZERO"

    # fallback: keep something stable
    return "STD_9"  # safest default for VAT systems


def _infer_rate(code: str, text: str, fallback_rate: float) -> float:
    # If explicit numeric percent exists in text, use it
    ta = _digits_to_ascii(text)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|٪)", ta)
    if m:
        return _f(m.group(1), fallback_rate)

    if code == "STD_9":
        return 9.0
    return 0.0


def _item_tax_template_name(code: str, abbr: str) -> str:
    label = PROFILE_LABELS.get(code, code)
    base = f"{label} ({code})"
    return _with_abbr(base, abbr)


# ---------------- ensure item custom fields ----------------

def bh_ensure_item_custom_fields(update: int = 1) -> Dict[str, Any]:
    """
    Creates required Item custom fields if missing:
      - Item.bh_vat_profile (Link -> BH VAT Profile)
      - Item.bh_item_tax_template (Link -> Item Tax Template)
    NOTE: after running this, run `bench --site ... migrate` to create DB columns.
    """
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    meta = frappe.get_meta("Item")
    need_profile = not meta.has_field("bh_vat_profile")
    need_tpl = not meta.has_field("bh_item_tax_template")

    if not (need_profile or need_tpl):
        return {"ok": True, "changed": False, "missing": []}

    fields = {"Item": []}
    missing = []

    if need_profile:
        fields["Item"].append(
            dict(
                fieldname="bh_vat_profile",
                label="BH VAT Profile",
                fieldtype="Link",
                options=BH_VAT_PROFILE_DOCTYPE,
                insert_after="item_group",
            )
        )
        missing.append("bh_vat_profile")

    if need_tpl:
        fields["Item"].append(
            dict(
                fieldname="bh_item_tax_template",
                label="BH Item Tax Template",
                fieldtype="Link",
                options="Item Tax Template",
                insert_after="bh_vat_profile",
            )
        )
        missing.append("bh_item_tax_template")

    create_custom_fields(fields, update=1 if update else 0)
    frappe.db.commit()
    return {"ok": True, "changed": True, "missing": missing}


# ---------------- Item Tax Template sync ----------------

def _get_enabled_profile_names() -> List[str]:
    cols = _table_cols(BH_VAT_PROFILE_DOCTYPE)
    filters: Dict[str, Any] = {}
    if "disabled" in cols:
        filters["disabled"] = 0
    elif "enabled" in cols:
        filters["enabled"] = 1
    elif "is_enabled" in cols:
        filters["is_enabled"] = 1

    try:
        return frappe.get_all(BH_VAT_PROFILE_DOCTYPE, filters=filters, pluck="name")
    except Exception:
        return frappe.get_all(BH_VAT_PROFILE_DOCTYPE, pluck="name")


def _upsert_item_tax_template(
    name: str,
    company: str,
    sales_vat_account: str,
    purchase_vat_account: str,
    rate: float,
    force: bool,
    dry_run: bool,
) -> Tuple[str, bool]:
    exists = bool(frappe.db.exists("Item Tax Template", name))
    if exists:
        if not force:
            return name, False
        doc = frappe.get_doc("Item Tax Template", name)
    else:
        doc = frappe.new_doc("Item Tax Template")
        doc.title = name  # naming is by title in ERPNext
    doc.company = company
    doc.taxes = []
    doc.append("taxes", {"tax_type": sales_vat_account, "tax_rate": rate})
    doc.append("taxes", {"tax_type": purchase_vat_account, "tax_rate": rate})

    if dry_run:
        return name, True

    if exists:
        doc.save(ignore_permissions=True)
    else:
        doc.insert(ignore_permissions=True)

    return doc.name, True


def bh_sync_item_tax_templates_from_profiles(
    company: Optional[str] = None,
    force: int = 0,
    dry_run: int = 1,
) -> Dict[str, Any]:
    company = _get_company(company)
    abbr = _company_abbr(company) or ""
    sales_vat, purchase_vat = _get_vat_accounts_from_settings()
    fallback_rate = _get_default_vat_rate_from_settings(9.0)

    names = _get_enabled_profile_names()
    out = {
        "company": company,
        "abbr": abbr,
        "scanned_profiles": len(names),
        "created_or_updated": 0,
        "skipped": 0,
        "dry_run": int(bool(dry_run)),
        "force": int(bool(force)),
        "templates": [],
    }

    for n in names:
        doc = frappe.get_doc(BH_VAT_PROFILE_DOCTYPE, n)
        text = _profile_text(doc)
        code = _infer_profile_code(text)
        rate = _infer_rate(code, text, fallback_rate)
        tpl_name = _item_tax_template_name(code, abbr)

        name2, changed = _upsert_item_tax_template(
            name=tpl_name,
            company=company,
            sales_vat_account=sales_vat,
            purchase_vat_account=purchase_vat,
            rate=rate,
            force=bool(force),
            dry_run=bool(dry_run),
        )

        if changed:
            out["created_or_updated"] += 1
        else:
            out["skipped"] += 1

        out["templates"].append(
            {"profile": n, "code": code, "rate": rate, "item_tax_template": name2}
        )

    return out


def bh_sync_items_vat_templates(
    company: Optional[str] = None,
    only_missing_template: int = 1,
    dry_run: int = 1,
) -> Dict[str, Any]:
    company = _get_company(company)
    abbr = _company_abbr(company) or ""

    meta = frappe.get_meta("Item")
    if not meta.has_field("bh_vat_profile") or not meta.has_field("bh_item_tax_template"):
        raise_bh_vat_error(BH_VAT_E_GENERIC, 
            "Missing Item custom fields in Meta. Run:\n"
            "  bench --site baba.bluehesab.ir execute blue_hesab.bh_core.vat_templates.bh_ensure_item_custom_fields\n"
            "then migrate."
        )

    # DB columns check (hard requirement for set_value)
    cols = _table_cols("Item")
    if "bh_vat_profile" not in cols or "bh_item_tax_template" not in cols:
        raise_bh_vat_error(BH_VAT_E_GENERIC, 
            "Item custom fields exist in Meta but DB columns are missing.\n"
            "Run migrate to create columns:\n"
            "  bench --site baba.bluehesab.ir migrate"
        )

    # map profile name -> canonical template name
    prof_names = _get_enabled_profile_names()
    prof_to_tpl: Dict[str, str] = {}
    for n in prof_names:
        doc = frappe.get_doc(BH_VAT_PROFILE_DOCTYPE, n)
        code = _infer_profile_code(_profile_text(doc))
        prof_to_tpl[str(n)] = _item_tax_template_name(code, abbr)

    items = frappe.get_all(
        "Item",
        fields=["name", "bh_vat_profile", "bh_item_tax_template"],
        limit_page_length=5000,
    )

    out = {
        "company": company,
        "abbr": abbr,
        "scanned_items": len(items),
        "updated": 0,
        "skipped": 0,
        "missing_profile": 0,
        "dry_run": int(bool(dry_run)),
        "only_missing_template": int(bool(only_missing_template)),
    }

    for it in items:
        prof = (it.get("bh_vat_profile") or "").strip()
        if not prof:
            out["missing_profile"] += 1
            continue

        target = prof_to_tpl.get(prof)
        if not target:
            out["skipped"] += 1
            continue

        cur = (it.get("bh_item_tax_template") or "").strip()
        if only_missing_template and cur:
            out["skipped"] += 1
            continue

        if dry_run:
            out["updated"] += 1
            continue

        frappe.db.set_value("Item", it["name"], "bh_item_tax_template", target, update_modified=False)
        out["updated"] += 1

    if not dry_run:
        frappe.db.commit()

    return out


# ---------------- MIXED Taxes & Charges Templates ----------------

def _tax_tpl_expected_name(title_base: str, abbr: str) -> str:
    title_base = (title_base or "").strip()
    abbr = (abbr or "").strip()
    if not abbr:
        return title_base
    return f"{title_base} - {abbr}"


def _tax_tpl_legacy_name(title_base: str, abbr: str) -> str:
    # legacy bug: title already had "- ABR" and ERPNext appended again => "- ABR - ABR"
    exp = _tax_tpl_expected_name(title_base, abbr)
    if not abbr:
        return exp
    return f"{exp} - {abbr}"


def _get_or_new_tax_charge_template(
    doctype: str,
    title_base: str,
    company: str,
    abbr: str,
    dry_run: bool,
) -> Any:
    """
    IMPORTANT:
      - For these doctypes, ERPNext autoname appends company abbr to *title*.
      - Therefore title_base MUST NOT include "- ABR".
    We support legacy docs named "... - ABR - ABR" by updating them instead of inserting new.
    """
    expected = _tax_tpl_expected_name(title_base, abbr)
    legacy = _tax_tpl_legacy_name(title_base, abbr)

    if frappe.db.exists(doctype, expected):
        doc = frappe.get_doc(doctype, expected)
        # normalize title (no abbr)
        if getattr(doc, "title", "") != title_base:
            doc.title = title_base
            if not dry_run:
                doc.save(ignore_permissions=True)
        return doc

    if abbr and frappe.db.exists(doctype, legacy):
        doc = frappe.get_doc(doctype, legacy)
        # keep legacy name to avoid rename complexity; just normalize title
        if getattr(doc, "title", "") != title_base:
            doc.title = title_base
            if not dry_run:
                doc.save(ignore_permissions=True)
        return doc

    doc = frappe.new_doc(doctype)
    doc.title = title_base  # <-- no "- BA"
    doc.company = company
    return doc


def _upsert_tax_charge_template(
    doctype: str,
    title_base: str,
    company: str,
    account_head: str,
    rate: float,
    included_in_print_rate: int,
    force: bool,
    dry_run: bool,
) -> Tuple[str, bool]:
    doc = _get_or_new_tax_charge_template(
        doctype=doctype,
        title_base=title_base,
        company=company,
        abbr=_company_abbr(company) or "",
        dry_run=dry_run,
    )

    # If exists and not force, skip
    if not doc.is_new() and not force:
        return doc.name, False

    doc.company = company
    doc.taxes = []
    doc.append(
        "taxes",
        {
            "charge_type": "On Net Total",
            "account_head": account_head,
            "description": "VAT",
            "rate": rate,
            "included_in_print_rate": int(bool(included_in_print_rate)),
        },
    )

    if dry_run:
        # name is either existing doc.name or (for new doc) will be created on insert
        return (doc.name or title_base), True

    if doc.is_new():
        doc.insert(ignore_permissions=True)   # ERPNext will name it: "<title_base> - BA"
    else:
        doc.save(ignore_permissions=True)

    return doc.name, True


def bh_ensure_mixed_tax_charge_templates(
    company: Optional[str] = None,
    force: int = 0,
    dry_run: int = 1,
    rate: Optional[float] = None,
) -> Dict[str, Any]:
    company = _get_company(company)
    sales_vat, purchase_vat = _get_vat_accounts_from_settings()
    r = _f(rate, _get_default_vat_rate_from_settings(9.0))

    targets = [
        ("Sales Taxes and Charges Template", "BH VAT MIXED Sales (EXCL)", sales_vat, 0),
        ("Sales Taxes and Charges Template", "BH VAT MIXED Sales (INCL)", sales_vat, 1),
        ("Purchase Taxes and Charges Template", "BH VAT MIXED Purchase (EXCL)", purchase_vat, 0),
        ("Purchase Taxes and Charges Template", "BH VAT MIXED Purchase (INCL)", purchase_vat, 1),
    ]

    out = {
        "company": company,
        "abbr": _company_abbr(company) or "",
        "rate": r,
        "dry_run": int(bool(dry_run)),
        "force": int(bool(force)),
        "created_or_updated": 0,
        "skipped": 0,
        "templates": {},
    }

    for doctype, title_base, acc, incl in targets:
        name2, changed = _upsert_tax_charge_template(
            doctype=doctype,
            title_base=title_base,
            company=company,
            account_head=acc,
            rate=r,
            included_in_print_rate=incl,
            force=bool(force),
            dry_run=bool(dry_run),
        )
        out["templates"][doctype + "::" + title_base] = {
            "name": name2,
            "account_head": acc,
            "included_in_print_rate": incl,
        }
        if changed:
            out["created_or_updated"] += 1
        else:
            out["skipped"] += 1

    return out

def bh_fix_mixed_template_names(company: str | None = None, dry_run: int = 1):
    company = _get_company(company)
    abbr = (_company_abbr(company) or "").strip()

    targets = [
        ("Sales Taxes and Charges Template", "BH VAT MIXED Sales (EXCL)"),
        ("Sales Taxes and Charges Template", "BH VAT MIXED Sales (INCL)"),
        ("Purchase Taxes and Charges Template", "BH VAT MIXED Purchase (EXCL)"),
        ("Purchase Taxes and Charges Template", "BH VAT MIXED Purchase (INCL)"),
    ]

    out = {"company": company, "abbr": abbr, "dry_run": int(bool(dry_run)), "renamed": [], "skipped": []}

    for doctype, title_base in targets:
        expected = _tax_tpl_expected_name(title_base, abbr)      # "... - BA"
        legacy = _tax_tpl_legacy_name(title_base, abbr)          # "... - BA - BA"

        if not abbr:
            out["skipped"].append({"doctype": doctype, "reason": "missing abbr"})
            continue

        if frappe.db.exists(doctype, legacy) and not frappe.db.exists(doctype, expected):
            if not dry_run:
                frappe.rename_doc(doctype, legacy, expected, force=True)
            out["renamed"].append({"doctype": doctype, "from": legacy, "to": expected})
        else:
            out["skipped"].append({"doctype": doctype, "expected": expected, "legacy": legacy})

    return out


def bh_force_item_columns(dry_run: int = 1):
    needed = {
        "bh_vat_profile": "varchar(140)",
        "bh_item_tax_template": "varchar(140)",
    }
    added = []
    for col, sql_type in needed.items():
        if not frappe.db.has_column("Item", col):
            if not dry_run:
                frappe.db.sql(f"ALTER TABLE `tabItem` ADD COLUMN `{col}` {sql_type} NULL")
            added.append(col)
    return {"dry_run": int(bool(dry_run)), "added": added}
