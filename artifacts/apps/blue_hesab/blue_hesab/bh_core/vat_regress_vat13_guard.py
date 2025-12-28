# apps/blue_hesab/blue_hesab/bh_core/vat_regress_vat13_guard.py
# VAT-13 GUARD REGRESS — mode flip should NOT auto-fix template; submit must block on mismatch
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import frappe


def _company_abbr(company: str) -> str:
    abbr = frappe.db.get_value("Company", company, "abbr")
    return (abbr or "").strip() or "BA"


def _infer_mixed_template_name(doctype: str, company: str, axis: str) -> str:
    # axis: "Exclusive" / "Inclusive"
    abbr = _company_abbr(company)
    if doctype == "Sales Invoice":
        return f"BH VAT MIXED Sales ({'INCL' if axis == 'Inclusive' else 'EXCL'}) - {abbr}"
    if doctype == "Purchase Invoice":
        return f"BH VAT MIXED Purchase ({'INCL' if axis == 'Inclusive' else 'EXCL'}) - {abbr}"
    raise ValueError(f"unsupported doctype: {doctype}")


def _pick_leaf_account(company: str, root_type: str) -> Optional[str]:
    row = frappe.db.sql(
        """select name
           from `tabAccount`
          where company=%s and is_group=0 and root_type=%s
          order by lft asc
          limit 1""",
        (company, root_type),
        as_dict=True,
    )
    return row[0]["name"] if row else None


def _pick_uom() -> str:
    for uom in ("Nos", "Unit", "عدد"):
        if frappe.db.exists("UOM", uom):
            return uom
    # fallback to any UOM
    row = frappe.db.get_value("UOM", {}, "name")
    return row or "Nos"


def _find_std9_item_tax_template(company: str) -> Optional[str]:
    # try best-effort name lookup
    patterns = ["%STD_9%", "%STD9%", "%۹%", "%9%"]
    for p in patterns:
        name = frappe.db.sql(
            """select name from `tabItem Tax Template`
               where company=%s and name like %s
               order by name asc
               limit 1""",
            (company, p),
        )
        if name:
            return name[0][0]
    return None


def _ensure_test_item_std9(company: str) -> str:
    item_code = "BH-VAT-STD_9-TEST"
    if frappe.db.exists("Item", item_code):
        return item_code

    # Create a safe non-stock service item
    income = _pick_leaf_account(company, "Income")
    expense = _pick_leaf_account(company, "Expense")

    it = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_code,
            "item_group": frappe.db.get_value("Item Group", {}, "name") or "All Item Groups",
            "stock_uom": _pick_uom(),
            "is_stock_item": 0,
            "is_sales_item": 1,
            "is_purchase_item": 1,
        }
    )

    # BH custom fields (ignore if not present)
    meta = frappe.get_meta("Item")
    if meta.has_field("bh_item_tax_template"):
        tmpl = _find_std9_item_tax_template(company)
        if tmpl:
            it.set("bh_item_tax_template", tmpl)

    it.insert(ignore_permissions=True)

    # per-company defaults (avoid missing income/expense)
    try:
        if income or expense:
            it.append(
                "item_defaults",
                {
                    "company": company,
                    "income_account": income,
                    "expense_account": expense,
                },
            )
            it.save(ignore_permissions=True)
    except Exception:
        # don't fail guard just for defaults; core may fill these
        pass

    return item_code


def _ensure_customer(company: str) -> str:
    name = "مشتری تست VAT"
    if frappe.db.exists("Customer", name):
        return name
    cg = frappe.db.get_value("Customer Group", {}, "name") or "All Customer Groups"
    terr = frappe.db.get_value("Territory", {}, "name") or "All Territories"
    doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": name,
            "customer_group": cg,
            "territory": terr,
        }
    )
    doc.insert(ignore_permissions=True)
    return name


def _ensure_supplier(company: str) -> str:
    name = "BH VAT REG Supplier"
    if frappe.db.exists("Supplier", name):
        return name
    sg = frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups"
    doc = frappe.get_doc(
        {
            "doctype": "Supplier",
            "supplier_name": name,
            "supplier_group": sg,
        }
    )
    doc.insert(ignore_permissions=True)
    return name


def _set_if_has(doc, fieldname: str, value):
    meta = frappe.get_meta(doc.doctype)
    if meta.has_field(fieldname):
        doc.set(fieldname, value)


def _try_submit(doc) -> Tuple[bool, str]:
    try:
        doc.submit()
        return True, "SUBMITTED"
    except Exception as e:
        return False, str(e)


def _cleanup(doc):
    try:
        if doc and doc.name and frappe.db.exists(doc.doctype, doc.name):
            frappe.delete_doc(doc.doctype, doc.name, force=1, ignore_permissions=True)
    except Exception:
        pass


def run_vat13_guard(company: str = "BlueAPi", rate: float = 1_000_000, **kwargs) -> Dict[str, Any]:
    """Returns a dict compatible with vat_ci expectations."""

    print("=== VAT-13 GUARD REGRESS v0.2 ===")
    print(f"Company: {company}")

    rows: List[Dict[str, Any]] = []

    item_code = _ensure_test_item_std9(company)

    # --- Sales Invoice: start EXCL, flip to INCL without changing template, submit must block ---
    si = None
    try:
        customer = _ensure_customer(company)
        t_excl = _infer_mixed_template_name("Sales Invoice", company, "Exclusive")

        si = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "company": company,
                "customer": customer,
                "taxes_and_charges": t_excl,
                "items": [{"item_code": item_code, "qty": 1, "rate": rate}],
            }
        )
        _set_if_has(si, "bh_vat_price_mode", "Exclusive")
        _set_if_has(si, "bh_vat_inclusive_intent", 0)
        si.insert(ignore_permissions=True)

        before = si.taxes_and_charges
        # flip axis only; do NOT touch template
        _set_if_has(si, "bh_vat_price_mode", "Inclusive")
        _set_if_has(si, "bh_vat_inclusive_intent", 1)
        si.save(ignore_permissions=True)
        after = si.taxes_and_charges

        # must not auto-fix template
        ok_no_autofix = (after == before)
        ok_submit, submit_msg = _try_submit(si)  # should fail
        ok = ok_no_autofix and (not ok_submit)

        rows.append(
            {
                "id": "VAT13-SI-02 flip EXCL->INCL submit-block",
                "ok": ok,
                "before": before,
                "after": after,
                "no_autofix": ok_no_autofix,
                "submit_blocked": (not ok_submit),
                "submit_msg": submit_msg,
            }
        )
        print(
            f"[{rows[-1]['id']}] {'PASS' if ok else 'FAIL'} | before='{before}' after='{after}' "
            f"no_autofix={ok_no_autofix} submit_blocked={not ok_submit}"
        )
    except Exception as e:
        rows.append({"id": "VAT13-SI-02 flip EXCL->INCL submit-block", "ok": False, "err": str(e)})
        print(f"[{rows[-1]['id']}] FAIL | {e}")
    finally:
        _cleanup(si)

    # --- Purchase Invoice: start INCL, flip to EXCL without changing template, submit must block ---
    pi = None
    try:
        supplier = _ensure_supplier(company)
        t_incl = _infer_mixed_template_name("Purchase Invoice", company, "Inclusive")

        pi = frappe.get_doc(
            {
                "doctype": "Purchase Invoice",
                "company": company,
                "supplier": supplier,
                "taxes_and_charges": t_incl,
                "items": [{"item_code": item_code, "qty": 1, "rate": rate}],
            }
        )
        _set_if_has(pi, "bh_vat_price_mode", "Inclusive")
        _set_if_has(pi, "bh_vat_inclusive_intent", 1)
        pi.insert(ignore_permissions=True)

        before = pi.taxes_and_charges
        # flip axis only; do NOT touch template
        _set_if_has(pi, "bh_vat_price_mode", "Exclusive")
        _set_if_has(pi, "bh_vat_inclusive_intent", 0)
        pi.save(ignore_permissions=True)
        after = pi.taxes_and_charges

        ok_no_autofix = (after == before)
        ok_submit, submit_msg = _try_submit(pi)  # should fail
        ok = ok_no_autofix and (not ok_submit)

        rows.append(
            {
                "id": "VAT13-PI-02 flip INCL->EXCL submit-block",
                "ok": ok,
                "before": before,
                "after": after,
                "no_autofix": ok_no_autofix,
                "submit_blocked": (not ok_submit),
                "submit_msg": submit_msg,
            }
        )
        print(
            f"[{rows[-1]['id']}] {'PASS' if ok else 'FAIL'} | before='{before}' after='{after}' "
            f"no_autofix={ok_no_autofix} submit_blocked={not ok_submit}"
        )
    except Exception as e:
        rows.append({"id": "VAT13-PI-02 flip INCL->EXCL submit-block", "ok": False, "err": str(e)})
        print(f"[{rows[-1]['id']}] FAIL | {e}")
    finally:
        _cleanup(pi)

    total = len(rows)
    passed = sum(1 for r in rows if r.get("ok"))
    failed = total - passed
    ok = failed == 0

    out = {
        "company": company,
        "ok": ok,
        "total": total,
        "passed": passed,
        "failed": failed,
        "rows": rows,
    }
    return out
