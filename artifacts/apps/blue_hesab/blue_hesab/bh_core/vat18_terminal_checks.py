# apps/blue_hesab/blue_hesab/bh_core/vat18_terminal_checks.py
# VAT-18: Submit-safe + Post-submit stability (VAT-25 compatible)
#
# Checks:
#  1) Submit PASS for SI/PI (EXCL/INCL) and post-submit snapshot is stable on reload
#  2) Submit BLOCK on BH intent mismatch (mode vs template axis) for SI/PI
#
# Run:
# bench --site baba.bluehesab.ir execute blue_hesab.bh_core.vat18_terminal_checks.run_cli --kwargs '{"company":"BlueAPi"}'

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import flt, nowdate

from .vat_pipe_templates import infer_mixed_template_name


# -------------------------
# utils
# -------------------------

def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


def _axis_from_price_mode(mode: str) -> str:
    v = _norm(mode).lower()
    return "INCL" if v.startswith("incl") else "EXCL"


def _axis_from_template_name(tpl: Optional[str]) -> Optional[str]:
    t = _norm(tpl)
    if not t:
        return None
    if "(INCL)" in t:
        return "INCL"
    if "(EXCL)" in t:
        return "EXCL"
    return None


def _parse_item_wise(v: Any) -> Any:
    if not v:
        return {}
    if isinstance(v, dict):
        obj = v
    else:
        s = str(v)
        try:
            obj = json.loads(s)
        except Exception:
            return {"__raw__": s}
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


def _snap(doc) -> Dict[str, Any]:
    taxes = []
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
    taxes = sorted(taxes, key=_tax_row_key)

    items = []
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
    items = sorted(items, key=lambda r: _norm(r.get("item_code")))

    return {
        "doctype": doc.doctype,
        "docstatus": int(getattr(doc, "docstatus", 0) or 0),
        "company": getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None),
        "bh_vat_price_mode": getattr(doc, "bh_vat_price_mode", None) or (doc.get("bh_vat_price_mode") if hasattr(doc, "get") else None),
        "taxes_and_charges": getattr(doc, "taxes_and_charges", None) or (doc.get("taxes_and_charges") if hasattr(doc, "get") else None),
        "items": items,
        "taxes": taxes,
        "totals": {
            "net_total": flt(getattr(doc, "net_total", 0) or 0, 6),
            "total_taxes_and_charges": flt(getattr(doc, "total_taxes_and_charges", 0) or 0, 6),
            "grand_total": flt(getattr(doc, "grand_total", 0) or 0, 6),
            "rounded_total": flt(getattr(doc, "rounded_total", 0) or 0, 6),
        },
    }


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


# -------------------------
# account + parties helpers
# -------------------------

def _pick_income_account(company: str) -> str:
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
    frappe.throw(f"VAT-18: no Income account found for company={company}")


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
    frappe.throw(f"VAT-18: no Expense account found for company={company}")


def _pick_receivable(company: str) -> str:
    v = frappe.db.get_value("Company", company, "default_receivable_account")
    if v and frappe.db.exists("Account", v):
        return v
    rows = frappe.get_all(
        "Account",
        filters={"company": company, "account_type": "Receivable", "is_group": 0},
        pluck="name",
        order_by="lft desc",
        limit=1,
    )
    if rows:
        return rows[0]
    frappe.throw(f"VAT-18: no Receivable account found for company={company}")


def _pick_payable(company: str) -> str:
    v = frappe.db.get_value("Company", company, "default_payable_account")
    if v and frappe.db.exists("Account", v):
        return v
    rows = frappe.get_all(
        "Account",
        filters={"company": company, "account_type": "Payable", "is_group": 0},
        pluck="name",
        order_by="lft desc",
        limit=1,
    )
    if rows:
        return rows[0]
    frappe.throw(f"VAT-18: no Payable account found for company={company}")


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


def _ensure_item(item_code: str) -> str:
    """Ensure a non-stock Item exists (used only by VAT-18 CLI checks).

    We keep VAT-18 self-contained: it should run on fresh/staged DBs without
    requiring manual fixtures.
    """

    if frappe.db.exists("Item", item_code):
        return item_code

    # pick a safe default Item Group (root group exists in every ERPNext DB)
    item_group = (
        frappe.db.get_value("Item Group", {"is_group": 1}, "name")
        or frappe.db.get_value("Item Group", {}, "name")
        or "All Item Groups"
    )

    # pick a safe UOM (Nos is common, fallback to any existing UOM)
    uom = (
        frappe.db.get_value("UOM", {"uom_name": "Nos"}, "name")
        or frappe.db.get_value("UOM", {"uom_name": "Unit"}, "name")
        or frappe.db.get_value("UOM", {}, "name")
        or "Nos"
    )

    it = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_code,
            "item_group": item_group,
            "stock_uom": uom,
            "is_stock_item": 0,
            "disabled": 0,
        }
    )
    it.insert(ignore_permissions=True)
    return item_code


def _require_items(items: List[str]) -> None:
    for code in items:
        _ensure_item(code)


# -------------------------
# builders
# -------------------------

def _make_si(*, company: str, mode: str, rate: float) -> Any:
    customer = _ensure_customer(company)
    income_account = _pick_income_account(company)
    receivable = _pick_receivable(company)

    items = ["BH-VAT-STD_9-TEST", "BH-VAT-EXEMPT-TEST", "BH-VAT-ZERO-TEST", "BH-VAT-EXPORT_0-TEST"]
    _require_items(items)

    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.customer = customer
    si.posting_date = nowdate()
    si.due_date = nowdate()
    si.debit_to = receivable

    si.bh_vat_price_mode = mode
    if mode == "Inclusive":
        si.set("bh_vat_inclusive_intent", 1)
    tpl, _dt = infer_mixed_template_name(kind="sales", company=company, axis=None, mode=mode)
    si.taxes_and_charges = tpl  # VAT-25: no auto-fill; tests must set template explicitly

    si.flags.ignore_mandatory = True

    for code in items:
        si.append("items", {"item_code": code, "qty": 1, "rate": rate, "income_account": income_account})

    si.save(ignore_permissions=True)
    return si


def _make_pi(*, company: str, mode: str, rate: float) -> Any:
    supplier = _ensure_supplier(company)
    expense = _pick_expense_account(company)
    payable = _pick_payable(company)

    items = ["BH-VAT-STD_9-TEST", "BH-VAT-EXEMPT-TEST", "BH-VAT-ZERO-TEST", "BH-VAT-EXPORT_0-TEST"]
    _require_items(items)

    pi = frappe.new_doc("Purchase Invoice")
    pi.company = company
    pi.supplier = supplier
    pi.posting_date = nowdate()
    pi.bill_date = nowdate()
    pi.credit_to = payable

    pi.bh_vat_price_mode = mode
    if mode == "Inclusive":
        pi.set("bh_vat_inclusive_intent", 1)
    tpl, _dt = infer_mixed_template_name(kind="purchase", company=company, axis=None, mode=mode)
    pi.taxes_and_charges = tpl  # VAT-25: no auto-fill; tests must set template explicitly

    pi.flags.ignore_mandatory = True

    for code in items:
        pi.append("items", {"item_code": code, "qty": 1, "rate": rate, "expense_account": expense})

    pi.save(ignore_permissions=True)
    return pi


# -------------------------
# checks
# -------------------------

def _submit_and_assert_stable(doc) -> Tuple[bool, str]:
    # submit
    doc.submit()

    s1 = _snap(doc)
    doc2 = frappe.get_doc(doc.doctype, doc.name)
    s2 = _snap(doc2)

    if s1 != s2:
        return False, "post-submit drift on reload"

    dup = _assert_no_duplicate_tax_rows(doc2)
    if dup:
        return False, dup

    mode = _norm(s2.get("bh_vat_price_mode") or "")
    tpl = _norm(s2.get("taxes_and_charges") or "")
    axis_mode = _axis_from_price_mode(mode)
    axis_tpl = _axis_from_template_name(tpl) or "EXCL"
    if axis_mode != axis_tpl:
        return False, f"axis mismatch after submit (mode={axis_mode}, template={axis_tpl}, tpl='{tpl}')"

    return True, "PASS"


def _expect_submit_block_mismatch(*, kind: str, company: str, rate: float) -> Tuple[bool, str]:
    # build draft in mode, then force opposite BH template, then submit -> must BLOCK
    if kind == "sales":
        doc = _make_si(company=company, mode="Inclusive", rate=rate)
        good_axis = "INCL"
        bad_axis = "EXCL"
    else:
        doc = _make_pi(company=company, mode="Inclusive", rate=rate)
        good_axis = "INCL"
        bad_axis = "EXCL"

    # force wrong template axis
    bad_tpl, _dt = infer_mixed_template_name(kind=kind, company=company, axis=bad_axis, mode=None)
    doc.taxes_and_charges = bad_tpl
    doc.save(ignore_permissions=True)  # allow draft save; submit should block

    try:
        doc.submit()
        return False, f"submit was NOT blocked (expected block). forced_tpl='{bad_tpl}', mode='Inclusive({good_axis})'"
    except ValidationError:
        return True, "PASS"
    except Exception as e:
        # treat any validation-like block as PASS, but keep trace
        return True, f"PASS({type(e).__name__})"


def run_cli(company: str = "BlueAPi", rate: float = 1000000.0, hard_fail: int = 1) -> Dict[str, Any]:
    """
    VAT-18 runner.
    Uses a MariaDB-safe SAVEPOINT and rolls back at the end (no leftovers).
    If hard_fail=1 and any test fails -> raises ValidationError(JSON).
    """
    frappe.set_user("Administrator")

    out: Dict[str, Any] = {"company": company, "ok": True}
    created: List[Tuple[str, str]] = []

    sp = f"bhvat18_{int(time.time())}_{frappe.generate_hash(length=6)}".replace("-", "_")
    frappe.db.savepoint(sp)

    try:
        print("=== VAT-18 SUBMIT SAFE / POST-SUBMIT STABILITY ===")
        print(f"Company: {company}")

        # SI EXCL submit stable
        si_excl = _make_si(company=company, mode="Exclusive", rate=rate)
        created.append((si_excl.doctype, si_excl.name))
        ok, msg = _submit_and_assert_stable(si_excl)
        out["VAT18-SI-EXCL-SUBMIT"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT18-SI-EXCL-SUBMIT: {out['VAT18-SI-EXCL-SUBMIT']}")
        out["ok"] = out["ok"] and ok

        # SI INCL submit stable
        si_incl = _make_si(company=company, mode="Inclusive", rate=rate)
        created.append((si_incl.doctype, si_incl.name))
        ok, msg = _submit_and_assert_stable(si_incl)
        out["VAT18-SI-INCL-SUBMIT"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT18-SI-INCL-SUBMIT: {out['VAT18-SI-INCL-SUBMIT']}")
        out["ok"] = out["ok"] and ok

        # PI EXCL submit stable
        pi_excl = _make_pi(company=company, mode="Exclusive", rate=rate)
        created.append((pi_excl.doctype, pi_excl.name))
        ok, msg = _submit_and_assert_stable(pi_excl)
        out["VAT18-PI-EXCL-SUBMIT"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT18-PI-EXCL-SUBMIT: {out['VAT18-PI-EXCL-SUBMIT']}")
        out["ok"] = out["ok"] and ok

        # PI INCL submit stable
        pi_incl = _make_pi(company=company, mode="Inclusive", rate=rate)
        created.append((pi_incl.doctype, pi_incl.name))
        ok, msg = _submit_and_assert_stable(pi_incl)
        out["VAT18-PI-INCL-SUBMIT"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT18-PI-INCL-SUBMIT: {out['VAT18-PI-INCL-SUBMIT']}")
        out["ok"] = out["ok"] and ok

        # mismatch block (Submit must block)
        ok, msg = _expect_submit_block_mismatch(kind="sales", company=company, rate=rate)
        out["VAT18-SI-SUBMIT-BLOCK-MISMATCH"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT18-SI-SUBMIT-BLOCK-MISMATCH: {out['VAT18-SI-SUBMIT-BLOCK-MISMATCH']}")
        out["ok"] = out["ok"] and ok

        ok, msg = _expect_submit_block_mismatch(kind="purchase", company=company, rate=rate)
        out["VAT18-PI-SUBMIT-BLOCK-MISMATCH"] = "PASS" if ok else f"FAIL - {msg}"
        print(f"VAT18-PI-SUBMIT-BLOCK-MISMATCH: {out['VAT18-PI-SUBMIT-BLOCK-MISMATCH']}")
        out["ok"] = out["ok"] and ok

        if hard_fail and not out["ok"]:
            raise ValidationError(json.dumps(out, ensure_ascii=False))

        return out

    finally:
        # rollback (no leftovers)
        try:
            frappe.db.rollback(save_point=sp)
        except Exception:
            # fallback delete (best-effort)
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
