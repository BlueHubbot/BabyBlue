# apps/blue_hesab/blue_hesab/bh_core/vat_regress_si_v02.py
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

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


def _ensure_customer() -> str:
    cust = "مشتری تست VAT"
    if not frappe.db.exists("Customer", cust):
        c = frappe.get_doc({"doctype": "Customer", "customer_name": cust, "customer_type": "Individual"})
        c.insert(ignore_permissions=True)
    return cust


def _ensure_item() -> str:
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


def _ensure_accounts() -> Dict[str, str]:
    receivable = "بدهکاران - BA"
    income = "سرویس - BA"
    return {"receivable": receivable, "income": income}


def _get_vat_account_sales(company: str) -> str:
    return "مالیات بر ارزش افزوده فروش - BA"


def _new_si(
    company: str,
    customer: str,
    item_code: str,
    receivable: str,
    income: str,
    price_mode: str,
    taxes_and_charges: str,
    qty: float,
    rate: float,
) -> "frappe.model.document.Document":
    si = frappe.get_doc(
        {
            "doctype": "Sales Invoice",
            "company": company,
            "posting_date": _today(),
            "customer": customer,
            "debit_to": receivable,
            "bh_vat_price_mode": price_mode,
            "taxes_and_charges": taxes_and_charges,
            "items": [
                {
                    "item_code": item_code,
                    "qty": qty,
                    "rate": rate,
                    "income_account": income,
                }
            ],
        }
    )

    # VAT-26: اگر سند Inclusive است باید intent صریح داشته باشد
    if hasattr(si, "bh_vat_inclusive_intent") and getattr(si, "bh_vat_price_mode", None) == "Inclusive":
        si.bh_vat_inclusive_intent = 1

    return si


def _run_one(
    key: str,
    *,
    company: str,
    price_mode: str,
    qty: float,
    rate: float,
    expected_vat: float,
    expected_grand: float,
    expected_customer_dr: float,
    expected_customer_cr: float,
    expected_vat_gl_dr: float,
    expected_vat_gl_cr: float,
) -> CaseResult:
    try:
        _ensure_company(company)
        customer = _ensure_customer()
        item_code = _ensure_item()
        acc = _ensure_accounts()
        vat_account = _get_vat_account_sales(company)

        axis = vat_axis_kind(mode=price_mode, kind="sales")
        tpl = infer_mixed_template_name(company=company, kind="sales", axis=axis)

        si = _new_si(
            company=company,
            customer=customer,
            item_code=item_code,
            receivable=acc["receivable"],
            income=acc["income"],
            price_mode=price_mode,
            taxes_and_charges=tpl,
            qty=qty,
            rate=rate,
        )

        si.insert(ignore_permissions=True)
        si.submit()

        # taxes
        vat_amt = 0.0
        for t in (si.taxes or []):
            if t.account_head == vat_account:
                vat_amt = flt(t.tax_amount)
                break

        if flt(vat_amt, 2) != flt(expected_vat, 2):
            return CaseResult(key=key, ok=False, name=si.name, msg=f"VAT mismatch: got={vat_amt} expected={expected_vat}")

        if flt(si.grand_total, 2) != flt(expected_grand, 2):
            return CaseResult(
                key=key, ok=False, name=si.name, msg=f"Grand mismatch: got={si.grand_total} expected={expected_grand}"
            )

        gl = frappe.get_all(
            "GL Entry",
            filters={"voucher_type": "Sales Invoice", "voucher_no": si.name, "is_cancelled": 0},
            fields=["account", "debit", "credit"],
        )

        cust_dr = sum(flt(r.debit) for r in gl if r.account == acc["receivable"])
        cust_cr = sum(flt(r.credit) for r in gl if r.account == acc["receivable"])
        vat_dr = sum(flt(r.debit) for r in gl if r.account == vat_account)
        vat_cr = sum(flt(r.credit) for r in gl if r.account == vat_account)

        if flt(cust_dr, 2) != flt(expected_customer_dr, 2) or flt(cust_cr, 2) != flt(expected_customer_cr, 2):
            return CaseResult(
                key=key,
                ok=False,
                name=si.name,
                msg=f"Customer GL mismatch: Dr got={cust_dr} exp={expected_customer_dr} | Cr got={cust_cr} exp={expected_customer_cr}",
            )

        if flt(vat_dr, 2) != flt(expected_vat_gl_dr, 2) or flt(vat_cr, 2) != flt(expected_vat_gl_cr, 2):
            return CaseResult(
                key=key,
                ok=False,
                name=si.name,
                msg=f"VAT GL mismatch: Dr got={vat_dr} exp={expected_vat_gl_dr} | Cr got={vat_cr} exp={expected_vat_gl_cr}",
            )

        return CaseResult(
            key=key,
            ok=True,
            name=si.name,
            msg=f"PASS | {si.name} | Net={si.net_total} | VAT={vat_amt} | Grand={si.grand_total}",
            data={"cust_dr": cust_dr, "cust_cr": cust_cr, "vat_dr": vat_dr, "vat_cr": vat_cr, "tpl": tpl},
        )

    except Exception as e:
        return CaseResult(key=key, ok=False, name=None, msg=f"FAIL -> {e.__class__.__name__}: {e}")


def run_si_mixed_regression(company: str = "BlueAPi", rate: float = 1_000_000) -> Dict[str, Any]:
    """
    BH-EP01 v0.2 / SI MIXED REGRESSION (8 scenarios)
    """
    out: Dict[str, Any] = {"company": company, "ok": True, "cases": []}

    cases = [
        ("SI-R01", "Exclusive", 4, rate, 90_000, 4_090_000, 4_090_000, 0, 0, 90_000),
        ("SI-R08", "Exclusive", -4, rate, -90_000, -4_090_000, 0, 4_090_000, 90_000, 0),
        ("SI-R02", "Exclusive", 5, rate, 180_000, 5_180_000, 5_180_000, 0, 0, 180_000),
        ("SI-R03", "Exclusive", 3.9, rate, 81_000, 3_981_000, 3_981_000, 0, 0, 81_000),
        ("SI-R04", "Exclusive", 4, rate, 90_000, 4_190_000, 4_190_000, 0, 0, 90_000),
        # INCL (fixed grand)
        ("SI-R05", "Inclusive", 4, rate, 82_568.81, 4_000_000, 4_000_000, 0, 0, 82_568.81),
        ("SI-R06", "Exclusive", 4.111111, rate, 99_999.99, 4_211_110.99, 4_211_111.0, 0, 0, 99_999.99),
        ("SI-R07", "Exclusive", 3, rate, 0, 3_000_000, 3_000_000, 0, 0, 0),
    ]

    for key, mode, qty, _rate, exp_vat, exp_grand, exp_cust_dr, exp_cust_cr, exp_vat_dr, exp_vat_cr in cases:
        r = _run_one(
            key,
            company=company,
            price_mode=mode,
            qty=qty,
            rate=_rate,
            expected_vat=exp_vat,
            expected_grand=exp_grand,
            expected_customer_dr=exp_cust_dr,
            expected_customer_cr=exp_cust_cr,
            expected_vat_gl_dr=exp_vat_dr,
            expected_vat_gl_cr=exp_vat_cr,
        )
        out["cases"].append({"key": r.key, "ok": r.ok, "name": r.name, "msg": r.msg, "data": r.data})
        if not r.ok:
            out["ok"] = False
            break

    return out
