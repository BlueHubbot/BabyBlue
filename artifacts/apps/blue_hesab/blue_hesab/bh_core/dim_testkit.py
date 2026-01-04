# apps/blue_hesab/blue_hesab/bh_core/dim_testkit.py
from __future__ import annotations

from typing import Any, Dict, Optional

import frappe


def _has_db_column(doctype: str, fieldname: str) -> bool:
    """Hard check against DB schema (not only DocType meta)."""
    try:
        return bool(frappe.db.has_column(f"tab{doctype}", fieldname))
    except Exception:
        return False


def _first_existing(doctype: str) -> Optional[str]:
    return frappe.db.get_value(doctype, {}, "name")


def _get_or_create_branch(company: str) -> str:
    """
    Branch is core ERPNext. بعضی نصب‌ها ستون company ندارند.
    ما اول تلاش می‌کنیم company-filter بزنیم اگر DB ستون داشت؛ وگرنه اولین Branch را می‌گیریم.
    """
    name = None

    if _has_db_column("Branch", "company"):
        name = frappe.db.get_value("Branch", {"company": company}, "name")

    if not name:
        name = _first_existing("Branch")

    if name:
        return name

    # create minimal Branch
    b = frappe.new_doc("Branch")
    # common field is "branch"
    if hasattr(b, "branch"):
        b.branch = "اصلی"
    elif hasattr(b, "branch_name"):
        b.branch_name = "اصلی"
    else:
        b.set("branch", "اصلی")

    if _has_db_column("Branch", "company"):
        b.company = company

    b.insert(ignore_permissions=True)
    return b.name


def _get_or_create_tafsili(company: str, idx: int) -> str:
    # BH Tafsili (autoname = field:title) and has no company column in your schema
    title = f"تفصیلی تست {idx} ({company})"
    name = frappe.db.get_value("BH Tafsili", {"title": title}, "name")
    if name:
        return name

    t = frappe.new_doc("BH Tafsili")
    t.title = title
    if hasattr(t, "enabled"):
        t.enabled = 1
    t.insert(ignore_permissions=True)
    return t.name


def _get_or_create_project(company: str) -> str:
    # Project usually has company column; if not, we still create without it.
    pname = f"پروژه تست ({company})"
    name = frappe.db.get_value("Project", {"project_name": pname}, "name")
    if name:
        return name

    p = frappe.new_doc("Project")
    if hasattr(p, "project_name"):
        p.project_name = pname
    else:
        p.set("project_name", pname)

    if _has_db_column("Project", "company"):
        p.company = company

    p.insert(ignore_permissions=True)
    return p.name


def _get_any_cost_center(company: str) -> Optional[str]:
    # Prefer existing BA one if present, else any cost center.
    for cc in ["اصلی - BA", "Main - BA", "Main - " + (frappe.get_value("Company", company, "abbr") or "").strip()]:
        if cc and frappe.db.exists("Cost Center", cc):
            return cc
    return frappe.db.get_value("Cost Center", {"is_group": 0}, "name") or frappe.db.get_value("Cost Center", {}, "name")


def apply_required_dims(doc: Any, *, company: str) -> Dict[str, Any]:
    """
    Fills required BH dimensions on header + rows for regression docs before submit.
    Works with Sales Invoice / Purchase Invoice objects.
    """
    out: Dict[str, Any] = {}

    # Header dims (only if fields exist on this doc)
    if hasattr(doc, "bh_branch"):
        if not getattr(doc, "bh_branch", None):
            doc.bh_branch = _get_or_create_branch(company)
        out["bh_branch"] = doc.bh_branch

    if hasattr(doc, "bh_tafsili_1"):
        if not getattr(doc, "bh_tafsili_1", None):
            doc.bh_tafsili_1 = _get_or_create_tafsili(company, 1)
        out["bh_tafsili_1"] = doc.bh_tafsili_1

    if hasattr(doc, "bh_tafsili_2"):
        if not getattr(doc, "bh_tafsili_2", None):
            doc.bh_tafsili_2 = _get_or_create_tafsili(company, 2)
        out["bh_tafsili_2"] = doc.bh_tafsili_2

    # Row dims
    proj = _get_or_create_project(company)
    cc = _get_any_cost_center(company)

    rows = getattr(doc, "items", None) or []
    touched = 0
    for r in rows:
        if hasattr(r, "project") and not getattr(r, "project", None):
            r.project = proj
            touched += 1
        if hasattr(r, "cost_center") and cc and not getattr(r, "cost_center", None):
            r.cost_center = cc
            touched += 1

    out["rows_touched"] = touched
    out["project"] = proj
    out["cost_center"] = cc
    return out


# Backward-compatible name used by LEGAL regress suites (don’t break imports)
def apply_invoice_dimensions(doc: Any, *, company: str) -> Dict[str, Any]:
    return apply_required_dims(doc, company=company)
