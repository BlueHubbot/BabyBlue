# apps/blue_hesab/blue_hesab/bh_core/vat_regress_pi_v01.py
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import frappe
from frappe.utils import flt

from .vat_pipeline import infer_mixed_template_name, vat_axis_kind


@dataclass
class CaseResult:
    key: str
    ok: bool
    name: Optional[str] = None
    msg: str = ""
    data: Optional[Dict[str, Any]] = None


def _today() -> str:
    return datetime.date.today().isoformat()


def _ensure_company(company: str) -> None:
    if not frappe.db.exists("Company", company):
        frappe.throw(f"Company {company} not found")


def _ensure_supplier(company: str) -> str:
    # keep stable supplier name to avoid flakiness
    sup = "BH VAT REG Supplier"
    if not frappe.db.exists("Supplier", sup):
        s = frappe.get_doc(
            {
                "doctype": "Supplier",
                "supplier_name": sup,
                "supplier_group": "All Supplier Groups",
                "supplier_type": "Company",
                "country": "Iran",
            }
        )
        s.insert(ignore_permissions=True)
    return sup


def _ensure_item(company: str) -> str:
    # must exist for get_item_details
    item = "BH-VAT-REG-ITEM"
    if not frappe.db.exists("Item", item):
        it = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": item,
                "item_name": "BH VAT REG Item",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 0,
                "include_item_in_manufacturing": 0,
                "disabled": 0,
            }
        )
        it.insert(ignore_permissions=True)
    return item


def _ensure_accounts(company: str) -> Dict[str, str]:
    # prefer what your regress already uses (same as prior EP01)
    payable = "طلبکاران - BA"
    expense = "اختلال - BA"
    return {"payable": payable, "expense": expense}


def _get_vat_account_purchase(company: str) -> str:
    # match your current BH Settings output (leaf)
    return "مالیات بر ارزش افزوده خرید - BA"


def _new_pi(
    company: str,
    supplier: str,
    item_code: str,
    payable: str,
    expense: str,
    price_mode: str,
    taxes_and_charges: str,
    qty: float,
    rate: float,
) -> "frappe.model.document.Document":
    pi = frappe.get_doc(
        {
            "doctype": "Purchase Invoice",
            "company": company,
            "posting_date": _today(),
            "supplier": supplier,
            "credit_to": payable,
            "bh_vat_price_mode": price_mode,
            "taxes_and_charges": taxes_and_charges,
            "items": [
                {
                    "item_code": item_code,
                    "qty": qty,
                    "rate": rate,
                    "expense_account": expense,
                }
            ],
        }
    )

    # VAT-26: اگر سند Inclusive است باید intent صریح داشته باشد
    if hasattr(pi, "bh_vat_inclusive_intent") and getattr(pi, "bh_vat_price_mode", None) == "Inclusive":
        pi.bh_vat_inclusive_intent = 1

    return pi


def _run_one(
    key: str,
    *,
    company: str,
    price_mode: str,
    qty: float,
    rate: float,
    expected_vat: float,
    expected_grand: float,
    expected_payable_credit: float,
    expected_vat_gl_dr: float,
    expected_vat_gl_cr: float,
) -> CaseResult:
    try:
        _ensure_company(company)
        supplier = _ensure_supplier(company)
        item_code = _ensure_item(company)
        acc = _ensure_accounts(company)
        vat_account = _get_vat_account_purchase(company)

        axis = vat_axis_kind(mode=price_mode, kind="purchase")
        tpl = infer_mixed_template_name(company=company, kind="purchase", axis=axis)

        pi = _new_pi(
            company=company,
            supplier=supplier,
            item_code=item_code,
            payable=acc["payable"],
            expense=acc["expense"],
            price_mode=price_mode,
            taxes_and_charges=tpl,
            qty=qty,
            rate=rate,
        )

        pi.insert(ignore_permissions=True)
        pi.submit()

        # totals
        vat_amt = 0.0
        for t in (pi.taxes or []):
            if t.account_head == vat_account:
                vat_amt = flt(t.tax_amount)
                break

        if flt(vat_amt, 2) != flt(expected_vat, 2):
            return CaseResult(key=key, ok=False, name=pi.name, msg=f"VAT mismatch: got={vat_amt} expected={expected_vat}")

        if flt(pi.grand_total, 2) != flt(expected_grand, 2):
            return CaseResult(
                key=key, ok=False, name=pi.name, msg=f"Grand mismatch: got={pi.grand_total} expected={expected_grand}"
            )

        # GL checks
        gl = frappe.get_all(
            "GL Entry",
            filters={"voucher_type": "Purchase Invoice", "voucher_no": pi.name, "is_cancelled": 0},
            fields=["account", "debit", "credit"],
        )

        payable_credit = sum(flt(r.credit) for r in gl if r.account == acc["payable"])
        vat_dr = sum(flt(r.debit) for r in gl if r.account == vat_account)
        vat_cr = sum(flt(r.credit) for r in gl if r.account == vat_account)

        if flt(payable_credit, 2) != flt(expected_payable_credit, 2):
            return CaseResult(
                key=key,
                ok=False,
                name=pi.name,
                msg=f"Payable credit mismatch: got={payable_credit} expected={expected_payable_credit}",
            )

        if flt(vat_dr, 2) != flt(expected_vat_gl_dr, 2) or flt(vat_cr, 2) != flt(expected_vat_gl_cr, 2):
            return CaseResult(
                key=key,
                ok=False,
                name=pi.name,
                msg=f"VAT GL mismatch: Dr got={vat_dr} exp={expected_vat_gl_dr} | Cr got={vat_cr} exp={expected_vat_gl_cr}",
            )

        return CaseResult(
            key=key,
            ok=True,
            name=pi.name,
            msg=f"PASS | {pi.name} | Net={pi.net_total} | VAT={vat_amt} | Grand={pi.grand_total}",
            data={"payable_credit": payable_credit, "vat_dr": vat_dr, "vat_cr": vat_cr, "tpl": tpl},
        )

    except Exception as e:
        return CaseResult(key=key, ok=False, name=None, msg=f"FAIL -> {e.__class__.__name__}: {e}")


def run_pi_mixed_regression(company: str = "BlueAPi", rate: float = 1_000_000) -> Dict[str, Any]:
    """
    BH-EP01 v0.1 / PI MIXED REGRESSION (8 scenarios)
    """
    out: Dict[str, Any] = {"company": company, "ok": True, "cases": []}

    # Scenarios align with your existing EP01 set (keep deterministic)
    cases = [
        # EXCL
        ("PI-R01", "Exclusive", 4, rate, 90_000, 4_090_000, 4_090_000, 90_000, 0),
        ("PI-R08", "Exclusive", -4, rate, -90_000, -4_090_000, 0, 0, 90_000),
        ("PI-R02", "Exclusive", 5, rate, 180_000, 5_180_000, 5_180_000, 180_000, 0),
        ("PI-R03", "Exclusive", 3.9, rate, 81_000, 3_981_000, 3_981_000, 81_000, 0),
        ("PI-R04", "Exclusive", 4, rate, 90_000, 4_190_000, 4_190_000, 90_000, 0),
        # INCL (fixed grand)
        ("PI-R05", "Inclusive", 4, rate, 82_568.81, 4_000_000, 4_000_000, 82_568.81, 0),
        ("PI-R06", "Exclusive", 4.111111, rate, 99_999.99, 4_211_110.99, 4_211_111.0, 99_999.99, 0),
        ("PI-R07", "Exclusive", 3, rate, 0, 3_000_000, 3_000_000, 0, 0),
    ]

    for key, mode, qty, _rate, exp_vat, exp_grand, exp_pay_credit, exp_vat_dr, exp_vat_cr in cases:
        r = _run_one(
            key,
            company=company,
            price_mode=mode,
            qty=qty,
            rate=_rate,
            expected_vat=exp_vat,
            expected_grand=exp_grand,
            expected_payable_credit=exp_pay_credit,
            expected_vat_gl_dr=exp_vat_dr,
            expected_vat_gl_cr=exp_vat_cr,
        )
        out["cases"].append({"key": r.key, "ok": r.ok, "name": r.name, "msg": r.msg, "data": r.data})
        if not r.ok:
            out["ok"] = False
            # keep same behavior: stop early to preserve signal
            break

    return out
