# apps/blue_hesab/blue_hesab/bh_core/vat17_terminal_checks.py
# VAT-17: Idempotency / No-Drift checks (Draft save/save + reload/save)
#
# هدف:
# - اجرای چندباره‌ی Save روی Draft نباید باعث "drift" شود:
#   - taxes_and_charges ثابت بماند
#   - ردیف‌های taxes تکثیر نشوند
#   - item_wise_tax_detail و مجموع‌ها ثابت بمانند
#
# اجرا:
# bench --site baba.bluehesab.ir execute blue_hesab.bh_core.vat17_terminal_checks.run_cli --kwargs '{"company":"BlueAPi"}'

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import frappe
from frappe.utils import flt, nowdate


# ---------- small utils ----------

def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


def _axis_from_template_name(tpl: Optional[str]) -> Optional[str]:
    t = _norm(tpl)
    if not t:
        return None
    if "(INCL)" in t:
        return "INCL"
    if "(EXCL)" in t:
        return "EXCL"
    return None


def _axis_from_price_mode(mode: str) -> str:
    v = _norm(mode).lower()
    if v.startswith("incl"):
        return "INCL"
    return "EXCL"


def _round_any(x: Any) -> Any:
    # normalize floats for stable comparisons
    if x is None:
        return None
    if isinstance(x, (int,)):
        return x
    if isinstance(x, float):
        return float(flt(x, 6))
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return [_round_any(i) for i in x]
    if isinstance(x, dict):
        return {k: _round_any(v) for k, v in x.items()}
    return x


def _parse_item_wise(value: Any) -> Any:
    if not value:
        return {}
    if isinstance(value, dict):
        obj = value
    else:
        s = str(value)
        try:
            obj = json.loads(s)
        except Exception:
            return {"__raw__": s}
    # stable ordering for compare
    if isinstance(obj, dict):
        return {k: obj[k] for k in sorted(obj.keys())}
    return obj


def _tax_row_key(r: Dict[str, Any]) -> Tuple:
    return (
        _norm(r.get("account_head")),
        _norm(r.get("charge_type")),
        float(flt(r.get("rate") or 0, 6)),
        int(r.get("included_in_print_rate") or 0),
    )


def _snap_doc(doc) -> Dict[str, Any]:
    # keep only stable, business-relevant keys (exclude name/modified/idx noise)
    taxes: List[Dict[str, Any]] = []
    for t in (getattr(doc, "taxes", None) or []):
        d = t.as_dict() if hasattr(t, "as_dict") else dict(t)
        taxes.append(
            {
                "account_head": d.get("account_head"),
                "charge_type": d.get("charge_type"),
                "rate": flt(d.get("rate") or 0, 6),
                "tax_amount": flt(d.get("tax_amount") or 0, 6),
                "total": flt(d.get("total") or 0, 6),
                "included_in_print_rate": int(d.get("included_in_print_rate") or 0),
                "item_wise_tax_detail": _parse_item_wise(d.get("item_wise_tax_detail")),
            }
        )

    # stable order (ERP might reorder)
    taxes_sorted = sorted(taxes, key=_tax_row_key)

    items: List[Dict[str, Any]] = []
    for it in (getattr(doc, "items", None) or []):
        d = it.as_dict() if hasattr(it, "as_dict") else dict(it)
        items.append(
            {
                "item_code": d.get("item_code"),
                "qty": flt(d.get("qty") or 0, 6),
                "rate": flt(d.get("rate") or 0, 6),
                "amount": flt(d.get("amount") or 0, 6),
                "net_amount": flt(d.get("net_amount") or 0, 6),
                "item_tax_template": d.get("item_tax_template") or d.get("bh_item_tax_template") or None,
            }
        )
    items_sorted = sorted(items, key=lambda r: _norm(r.get("item_code")))

    snap = {
        "doctype": getattr(doc, "doctype", ""),
        "company": getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None),
        "bh_vat_price_mode": getattr(doc, "bh_vat_price_mode", None) or (doc.get("bh_vat_price_mode") if hasattr(doc, "get") else None),
        "taxes_and_charges": getattr(doc, "taxes_and_charges", None) or (doc.get("taxes_and_charges") if hasattr(doc, "get") else None),
        "items": items_sorted,
        "taxes": taxes_sorted,
        "totals": {
            "net_total": flt(getattr(doc, "net_total", 0) or 0, 6),
            "total_taxes_and_charges": flt(getattr(doc, "total_taxes_and_charges", 0) or 0, 6),
            "grand_total": flt(getattr(doc, "grand_total", 0) or 0, 6),
            "rounded_total": flt(getattr(doc, "rounded_total", 0) or 0, 6),
        },
    }
    return _round_any(snap)


def _assert_no_duplicate_tax_rows(doc) -> Optional[str]:
    seen = set()
    dups = []
    for r in (getattr(doc, "taxes", None) or []):
        rr = r.as_dict() if hasattr(r, "as_dict") else dict(r)
        k = _tax_row_key(rr)
        if k in seen:
            dups.append(k)
        else:
            seen.add(k)
    if dups:
        return f"duplicate taxes rows detected: {dups}"
    return None


# ---------- fixtures ----------

def _pick_income_account(company: str) -> str:
    # prefer Company default
    v = frappe.db.get_value("Company", company, "default_income_account")
    if v and frappe.db.exists("Account", v):
        return v

    rows = frappe.get_all(
        "Account",
        filters={"company": company, "root_type": "Income", "is_group": 0},
        pluck="name",
        order_by="lft desc",
        limit=1,
    )
    if rows:
        return rows[0]
    frappe.throw(f"VAT-17: no Income account found for company={company}")


def _pick_expense_account(company: str) -> str:
    v = frappe.db.get_value("Company", company, "default_expense_account")
    if v and frappe.db.exists("Account", v):
        return v

    rows = frappe.get_all(
        "Account",
        filters={"company": company, "root_type": "Expense", "is_group": 0},
        pluck="name",
        order_by="lft desc",
        limit=1,
    )
    if rows:
        return rows[0]
    frappe.throw(f"VAT-17: no Expense account found for company={company}")


def _ensure_customer(company: str, name: str = "مشتری تست VAT") -> str:
    if frappe.db.exists("Customer", name):
        return name
    cust = frappe.new_doc("Customer")
    cust.customer_name = name
    cust.customer_group = "All Customer Groups"
    cust.territory = "All Territories"
    cust.disabled = 0
    cust.flags.ignore_mandatory = True
    cust.insert(ignore_permissions=True)
    return cust.name


def _ensure_supplier(company: str, name: str = "BH VAT REG Supplier") -> str:
    if frappe.db.exists("Supplier", name):
        return name
    sup = frappe.new_doc("Supplier")
    sup.supplier_name = name
    sup.supplier_group = "All Supplier Groups"
    sup.disabled = 0
    sup.flags.ignore_mandatory = True
    sup.insert(ignore_permissions=True)
    return sup.name


def _require_items(items: List[str]) -> None:
    missing = [c for c in items if not frappe.db.exists("Item", c)]
    if missing:
        frappe.throw(f"VAT-17: missing Items: {missing}")


# ---------- doc builders ----------

def _make_sales_invoice(*, company: str, mode: str, rate: float) -> Any:
    # IMPORTANT: For VAT-17 (idempotency), we intentionally build a *consistent* draft
    # (mode + template aligned) so we can measure "drift" across repeated saves.
    from blue_hesab.bh_core import vat_mixed

    customer = _ensure_customer(company)
    income_account = _pick_income_account(company)

    items = [
        ("BH-VAT-STD_9-TEST", rate),
        ("BH-VAT-EXEMPT-TEST", rate),
        ("BH-VAT-ZERO-TEST", rate),
        ("BH-VAT-EXPORT_0-TEST", rate),
    ]
    _require_items([c for c, _ in items])

    axis = _axis_from_price_mode(mode)  # EXCL / INCL
    tpl = vat_mixed.mixed_template_name("sales", company, axis)

    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.customer = customer
    si.posting_date = nowdate()
    si.due_date = nowdate()
    si.bh_vat_price_mode = mode
    si.taxes_and_charges = tpl or ""
    if axis == "INCL" and hasattr(si, "bh_vat_inclusive_intent"):
        si.bh_vat_inclusive_intent = 1

    si.flags.ignore_mandatory = True

    for code, r in items:
        si.append(
            "items",
            {"item_code": code, "qty": 1, "rate": r, "income_account": income_account},
        )

    si.save(ignore_permissions=True)  # triggers VAT hooks
    return si


def _make_purchase_invoice(*, company: str, mode: str, rate: float) -> Any:
    # IMPORTANT: For VAT-17 (idempotency), we intentionally build a *consistent* draft
    # (mode + template aligned) so we can measure "drift" across repeated saves.
    from blue_hesab.bh_core import vat_mixed

    supplier = _ensure_supplier(company)
    expense_account = _pick_expense_account(company)

    items = [
        ("BH-VAT-STD_9-TEST", rate),
        ("BH-VAT-EXEMPT-TEST", rate),
        ("BH-VAT-ZERO-TEST", rate),
        ("BH-VAT-EXPORT_0-TEST", rate),
    ]
    _require_items([c for c, _ in items])

    axis = _axis_from_price_mode(mode)  # EXCL / INCL
    tpl = vat_mixed.mixed_template_name("purchase", company, axis)

    pi = frappe.new_doc("Purchase Invoice")
    pi.company = company
    pi.supplier = supplier
    pi.posting_date = nowdate()
    pi.bh_vat_price_mode = mode
    pi.taxes_and_charges = tpl or ""
    if axis == "INCL" and hasattr(pi, "bh_vat_inclusive_intent"):
        pi.bh_vat_inclusive_intent = 1

    pi.flags.ignore_mandatory = True

    for code, r in items:
        pi.append(
            "items",
            {"item_code": code, "qty": 1, "rate": r, "expense_account": expense_account},
        )

    pi.save(ignore_permissions=True)  # triggers VAT hooks
    return pi

# ---------- checks ----------

def _idempotency_check(doc) -> Tuple[bool, str]:
    s1 = _snap_doc(doc)

    # save again (same instance)
    doc.save(ignore_permissions=True)
    s2 = _snap_doc(doc)

    # reload and save
    doc2 = frappe.get_doc(doc.doctype, doc.name)
    doc2.save(ignore_permissions=True)
    s3 = _snap_doc(doc2)

    if s1 != s2:
        return False, "drift on second save (same instance)"
    if s1 != s3:
        return False, "drift after reload/save"

    dup = _assert_no_duplicate_tax_rows(doc2)
    if dup:
        return False, dup

    # sanity: template axis must match mode
    mode = _norm(s3.get("bh_vat_price_mode") or "")
    tpl = _norm(s3.get("taxes_and_charges") or "")
    axis_mode = _axis_from_price_mode(mode)
    axis_tpl = _axis_from_template_name(tpl) or "EXCL"
    if axis_mode != axis_tpl:
        return False, f"axis mismatch (mode={axis_mode}, template={axis_tpl}, tpl='{tpl}')"

    return True, "PASS"


def run_cli(company: str = "BlueAPi", rate: float = 1000000.0) -> Dict[str, Any]:
    """
    VAT-17 runner.
    - creates Draft SI/PI (EXCL + INCL)
    - checks no drift across save/save + reload/save
    - uses DB savepoint and rollbacks at the end (no leftovers)
    """
    frappe.set_user("Administrator")

    out: Dict[str, Any] = {"company": company, "ok": True}
    created: List[Tuple[str, str]] = []  # (doctype, name)

    sp = f"bhvat17_{int(time.time())}_{frappe.generate_hash(length=6)}".replace("-", "_")
    frappe.db.savepoint(sp)

    try:
        print("=== VAT-17 IDEMPOTENCY / NO-DRIFT ===")
        print(f"Company: {company}")

        # Sales EXCL
        si_excl = _make_sales_invoice(company=company, mode="Exclusive", rate=rate)
        created.append((si_excl.doctype, si_excl.name))
        ok, msg = _idempotency_check(si_excl)
        out["VAT17-SI-EXCL"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT17-SI-EXCL: {out['VAT17-SI-EXCL']}")
        out["ok"] = out["ok"] and ok

        # Sales INCL
        si_incl = _make_sales_invoice(company=company, mode="Inclusive", rate=rate)
        created.append((si_incl.doctype, si_incl.name))
        ok, msg = _idempotency_check(si_incl)
        out["VAT17-SI-INCL"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT17-SI-INCL: {out['VAT17-SI-INCL']}")
        out["ok"] = out["ok"] and ok

        # Purchase EXCL
        pi_excl = _make_purchase_invoice(company=company, mode="Exclusive", rate=rate)
        created.append((pi_excl.doctype, pi_excl.name))
        ok, msg = _idempotency_check(pi_excl)
        out["VAT17-PI-EXCL"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT17-PI-EXCL: {out['VAT17-PI-EXCL']}")
        out["ok"] = out["ok"] and ok

        # Purchase INCL
        pi_incl = _make_purchase_invoice(company=company, mode="Inclusive", rate=rate)
        created.append((pi_incl.doctype, pi_incl.name))
        ok, msg = _idempotency_check(pi_incl)
        out["VAT17-PI-INCL"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT17-PI-INCL: {out['VAT17-PI-INCL']}")
        out["ok"] = out["ok"] and ok

        return out

    finally:
        # rollback everything created in this run (no leftovers)
        try:
            frappe.db.rollback(save_point=sp)
        except Exception:
            # fallback: best-effort delete if rollback fails
            for dt, name in created:
                try:
                    if frappe.db.exists(dt, name):
                        frappe.delete_doc(dt, name, ignore_permissions=True, force=True)
                except Exception:
                    pass
        try:
            frappe.db.commit()
        except Exception:
            pass
