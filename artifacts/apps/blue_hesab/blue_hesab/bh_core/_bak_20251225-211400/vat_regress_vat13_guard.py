# apps/blue_hesab/blue_hesab/bh_core/vat_regress_vat13_guard.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import frappe

PASS = "PASS"
FAIL = "FAIL"

import re
import hashlib

def _vat13_safe_savepoint(name: str) -> str:
    """MariaDB SAVEPOINT identifiers must be bare (no quotes) and contain no hyphens/spaces.
    Keep deterministic + short.
    """
    raw = (name or "sp").strip()

    # idempotent: if already safe + prefixed, keep it
    if raw.startswith("vat13_") and re.fullmatch(r"[0-9A-Za-z_]{1,64}", raw):
        return raw[:64]

    base = re.sub(r"[^0-9A-Za-z_]+", "_", raw).strip("_") or "sp"
    if len(base) > 48:
        h = hashlib.md5(base.encode("utf-8")).hexdigest()[:10]
        base = f"{base[:37]}_{h}"
    out = f"vat13_{base}"
    return re.sub(r"[^0-9A-Za-z_]+", "_", out)[:64]
from frappe.utils import add_days, today


BH_SALES_PREFIX = "BH VAT MIXED Sales"
BH_PUR_PREFIX = "BH VAT MIXED Purchase"


@dataclass
class Case:
    id: str
    ok: bool
    detail: str


def _get_default_company() -> str:
    # prefer BH Settings.default_company if exists
    try:
        if frappe.db.exists("DocType", "BH Settings"):
            v = frappe.db.get_single_value("BH Settings", "default_company")
            if v:
                return v
    except Exception:
        pass
    # fallback: first Company
    return frappe.get_all("Company", pluck="name", limit=1)[0]


def _pick_cost_center(company: str) -> str:
    cc = frappe.get_all("Cost Center", filters={"company": company, "is_group": 0}, pluck="name", limit=1)
    if cc:
        return cc[0]
    v = frappe.db.get_value("Company", company, "cost_center")
    if v:
        return v
    raise RuntimeError("No Cost Center found for company")


def _pick_account(company: str, root_type: str, preferred: Optional[str] = None) -> str:
    if preferred and frappe.db.exists("Account", preferred):
        return preferred
    acc = frappe.get_all(
        "Account",
        filters={"company": company, "root_type": root_type, "is_group": 0},
        pluck="name",
        limit=1,
    )
    if not acc:
        raise RuntimeError(f"No {root_type} leaf account found for company")
    return acc[0]


def _pick_item(filters: Dict[str, Any]) -> str:
    # prefer non-stock items to avoid stock side-effects
    items = frappe.get_all("Item", filters=filters, fields=["name", "item_code", "is_stock_item"], limit_page_length=200)
    for r in items:
        if int(r.get("is_stock_item") or 0) == 0:
            return r.get("item_code") or r.get("name")
    if items:
        r = items[0]
        return r.get("item_code") or r.get("name")
    return frappe.get_all("Item", pluck="name", limit=1)[0]


def _pick_customer() -> str:
    if frappe.db.exists("Customer", "مشتری تست VAT"):
        return "مشتری تست VAT"
    return frappe.get_all("Customer", pluck="name", limit=1)[0]


def _pick_supplier() -> str:
    if frappe.db.exists("Supplier", "BH VAT REG Supplier"):
        return "BH VAT REG Supplier"
    return frappe.get_all("Supplier", pluck="name", limit=1)[0]


def _pick_bh_template(dt: str, company: str, prefix: str, axis: str) -> str:
    # axis = INCL / EXCL
    for n in frappe.get_all(dt, filters={"company": company}, pluck="name", limit_page_length=500):
        if n.startswith(prefix) and f"({axis})" in n:
            return n
    raise RuntimeError(f"BH template not found: {prefix} ({axis}) for company={company}")


def _pick_non_bh_template(dt: str, company: str, bh_prefix: str) -> str:
    # pick any template NOT starting with BH prefix (must exist to test reject)
    names = frappe.get_all(dt, filters={"company": company}, pluck="name", limit_page_length=500)
    for n in names:
        if not n.startswith(bh_prefix):
            return n
    raise RuntimeError(f"No non-BH template exists to test reject for dt={dt}, company={company}")


def _looks_like_guard_error(msg: str) -> bool:
    m = (msg or "").lower()
    # be tolerant: message could be short or html
    return ("vat" in m) or ("bh vat" in m) or ("قالب" in msg) or ("غیرمجاز" in msg) or ("قفل" in msg)


def _save_should_reject(doc, label: str) -> Case:
    sp = f"vat13_{label}".replace(" ", "_")
    frappe.db.savepoint(_vat13_safe_savepoint(sp))
    try:
        doc.save(ignore_permissions=True)
        # if save succeeded => FAIL
        return Case(label, False, f"UNEXPECTED SAVED: TAC={getattr(doc, 'taxes_and_charges', None)!r}")
    except Exception as e:
        frappe.db.rollback(save_point=_vat13_safe_savepoint(sp))
        msg = (str(e) or "")
        if _looks_like_guard_error(msg):
            return Case(label, True, f"REJECTED: {type(e).__name__}")
        return Case(label, False, f"REJECTED but suspicious: {type(e).__name__}: {msg[:180]}")
    finally:
        # ensure no partial writes
        try:
            frappe.db.rollback(save_point=_vat13_safe_savepoint(sp))
        except Exception:
            pass



def _mode_flip_should_not_autofix_and_submit_block(doc, label: str, flip_to: str, expected_suggested: str) -> Case:
    """
    VAT-25 policy:
      - Changing bh_vat_price_mode must NOT auto-change taxes_and_charges on save.
      - Submit must BLOCK when mode axis != template axis, and must include suggested template in message.

    VAT-26 addition:
      - If flip_to == Inclusive (on non-POS docs), explicitly set bh_vat_inclusive_intent=1 so the test
        reaches the mismatch-on-submit guard (instead of being blocked earlier).
    """
    sp = f"vat13_{label}".replace(" ", "_")
    frappe.db.savepoint(_vat13_safe_savepoint(sp))
    try:
        from frappe.exceptions import ValidationError

        doc.save(ignore_permissions=True)
        before = getattr(doc, "taxes_and_charges", None)

        doc.bh_vat_price_mode = flip_to
        if flip_to == "Inclusive":
            # non-POS Inclusive requires explicit intent
            doc.set("bh_vat_inclusive_intent", 1)

        doc.save(ignore_permissions=True)
        after = getattr(doc, "taxes_and_charges", None)

        no_flip_ok = (after == before)

        # submit must be blocked
        blocked_ok = False
        err = ""
        try:
            doc.submit()
            err = "SUBMITTED_UNEXPECTEDLY"
            blocked_ok = False
        except ValidationError as e:
            msg = str(e)
            blocked_ok = (expected_suggested in msg) and ("اعمال قالب پیشنهادی" in msg)
            err = msg[:260]
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:240]}"
            blocked_ok = False

        ok = no_flip_ok and blocked_ok
        detail = (
            f"before={before!r} after={after!r} (no_flip={no_flip_ok}) | "
            f"submit_block={blocked_ok} | suggested={expected_suggested!r} | err={err!r}"
        )
        return Case(label, ok, detail)
    except Exception as e:
        return Case(label, False, f"EXCEPTION: {type(e).__name__}: {str(e)[:220]}")
    finally:
        try:
            frappe.db.rollback(save_point=_vat13_safe_savepoint(sp))
        except Exception:
            pass



def run_vat13_guard(rate: float = 1000000, company: Optional[str] = None) -> Dict[str, Any]:
    """
    VAT-13:
      1) non-BH template must reject (SI + PI)
      2) flip bh_vat_price_mode must NOT switch taxes_and_charges; submit must BLOCK on mismatch (SI + PI)
    Must leave no docs behind (savepoint+rollback).
    """
    company = company or _get_default_company()

    pd = today()
    dd = add_days(pd, 1)
    cc = _pick_cost_center(company)

    # templates
    non_bh_sales = _pick_non_bh_template("Sales Taxes and Charges Template", company, BH_SALES_PREFIX)
    non_bh_pur = _pick_non_bh_template("Purchase Taxes and Charges Template", company, BH_PUR_PREFIX)

    sales_excl = _pick_bh_template("Sales Taxes and Charges Template", company, BH_SALES_PREFIX, "EXCL")
    sales_incl = _pick_bh_template("Sales Taxes and Charges Template", company, BH_SALES_PREFIX, "INCL")
    pur_excl = _pick_bh_template("Purchase Taxes and Charges Template", company, BH_PUR_PREFIX, "EXCL")
    pur_incl = _pick_bh_template("Purchase Taxes and Charges Template", company, BH_PUR_PREFIX, "INCL")

    income = _pick_account(company, "Income", "سرویس - BA")
    expense = _pick_account(company, "Expense", "اختلال - BA")

    # docs
    si_non_bh = frappe.get_doc({
        "doctype": "Sales Invoice",
        "company": company,
        "customer": _pick_customer(),
        "posting_date": pd,
        "due_date": dd,
        "bh_vat_price_mode": "Exclusive",
        "taxes_and_charges": non_bh_sales,
        "items": [{
            "item_code": _pick_item({"disabled": 0, "is_sales_item": 1}),
            "qty": 1,
            "rate": float(rate),
            "income_account": income,
            "cost_center": cc,
        }],
    })

    pi_non_bh = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "company": company,
        "supplier": _pick_supplier(),
        "posting_date": pd,
        "due_date": dd,
        "bh_vat_price_mode": "Exclusive",
        "taxes_and_charges": non_bh_pur,
        "items": [{
            "item_code": _pick_item({"disabled": 0, "is_purchase_item": 1}),
            "qty": 1,
            "rate": float(rate),
            "expense_account": expense,
            "cost_center": cc,
        }],
    })

    si_flip = frappe.get_doc({
        "doctype": "Sales Invoice",
        "company": company,
        "customer": _pick_customer(),
        "posting_date": pd,
        "due_date": dd,
        "bh_vat_price_mode": "Exclusive",
        "taxes_and_charges": sales_excl,
        "items": [{
            "item_code": _pick_item({"disabled": 0, "is_sales_item": 1}),
            "qty": 1,
            "rate": float(rate),
            "income_account": income,
            "cost_center": cc,
        }],
    })

    pi_flip = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "company": company,
        "supplier": _pick_supplier(),
        "posting_date": pd,
        "due_date": dd,
        "bh_vat_price_mode": "Inclusive",
        "bh_vat_inclusive_intent": 1,
        "taxes_and_charges": pur_incl,
        "items": [{
            "item_code": _pick_item({"disabled": 0, "is_purchase_item": 1}),
            "qty": 1,
            "rate": float(rate),
            "expense_account": expense,
            "cost_center": cc,
        }],
    })

    print("\n=== VAT-13 GUARD REGRESS v0.2 (VAT-25 lock) ===")
    print("Company:", company)

    cases = []
    cases.append(_save_should_reject(si_non_bh, "VAT13-SI-01 non-BH reject"))
    cases.append(_save_should_reject(pi_non_bh, "VAT13-PI-01 non-BH reject"))
    cases.append(_mode_flip_should_not_autofix_and_submit_block(si_flip, "VAT13-SI-02 no auto flip + submit blocks", flip_to="Inclusive", expected_suggested=sales_incl))
    cases.append(_mode_flip_should_not_autofix_and_submit_block(pi_flip, "VAT13-PI-02 no auto flip + submit blocks", flip_to="Exclusive", expected_suggested=pur_excl))

    passed = sum(1 for c in cases if c.ok)
    total = len(cases)
    failed = total - passed
    ok = (failed == 0)

    for c in cases:
        print(f"[{c.id}] {PASS if c.ok else FAIL} | {c.detail}")

    summary = {"total": total, "passed": passed, "failed": failed}
    return {"ok": ok, "summary": summary, "cases": [c.__dict__ for c in cases]}
