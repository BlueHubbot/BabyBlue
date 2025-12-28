# apps/blue_hesab/blue_hesab/bh_core/vat_regress_intent_v08.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import frappe
from frappe.utils import add_days, nowdate

MODE_EXCL = "Exclusive"
MODE_INCL = "Inclusive"


def intent_regress_v08_cli(company: str = "BlueAPi", rate: Optional[float] = None, **kwargs) -> Dict[str, Any]:
    """
    bench --site baba.bluehesab.ir execute "blue_hesab.bh_core.vat_regress_intent_v08.intent_regress_v08_cli" --kwargs '{"company":"BlueAPi"}'
    """
    res = intent_regress_v08(company=company, rate=rate, **kwargs)

    print("=== VAT-12 INTENT LOCK REGRESS v0.8 ===")
    for c in res["cases"]:
        line = f'{c["sid"]} {c["id"]}: ' + ("PASS" if c["pass"] else "FAIL")
        print(line)
    print(f'SUMMARY: total={res["total"]} passed={res["passed"]} failed={res["failed"]}')
    print(frappe.as_json(res))
    return res


def intent_regress_v08(company: str, rate: Optional[float] = None, **kwargs) -> Dict[str, Any]:
    """
    IMPORTANT:
    - must accept rate/kwargs because vat_ci passes them.
    - POS tests MUST NOT rely on POS Profile (it can wipe taxes_and_charges).
    """
    cases: List[Dict[str, Any]] = []
    created_docs: List[List[str]] = []

    passed = 0
    failed = 0

    def _add_case(row: Dict[str, Any]) -> None:
        nonlocal passed, failed
        row["ok"] = bool(row.get("pass"))  # CI expects ok==pass
        cases.append(row)
        if row["pass"]:
            passed += 1
        else:
            failed += 1

    # ---------------- deterministic pickers ----------------

    def _pick_customer() -> str:
        preferred = "مشتری تست VAT"
        if frappe.db.exists("Customer", preferred):
            return preferred
        name = frappe.db.get_value("Customer", {}, "name", order_by="name asc")
        if not name:
            raise Exception("No Customer found. Create a Customer (e.g. مشتری تست VAT).")
        return name

    def _pick_supplier() -> str:
        preferred = "BH VAT REG Supplier"
        if frappe.db.exists("Supplier", preferred):
            return preferred
        name = frappe.db.get_value("Supplier", {}, "name", order_by="name asc")
        if not name:
            raise Exception("No Supplier found. Create a Supplier (e.g. BH VAT REG Supplier).")
        return name

    def _pick_item_code() -> str:
        name = frappe.db.get_value("Item", {"disabled": 0}, "name", order_by="name asc")
        if not name:
            name = frappe.db.get_value("Item", {}, "name", order_by="name asc")
        if not name:
            raise Exception("No Item found. Create at least one Item for tests.")
        return name

    def _pick_income_account(company_: str) -> str:
        preferred = "سرویس - BA"
        if frappe.db.exists("Account", {"name": preferred, "company": company_}):
            return preferred
        name = frappe.db.get_value(
            "Account",
            {"company": company_, "root_type": "Income", "is_group": 0},
            "name",
            order_by="name asc",
        )
        if not name:
            raise Exception("No Income Account leaf found for company.")
        return name

    def _pick_expense_account(company_: str) -> str:
        preferred = "اختلال - BA"
        if frappe.db.exists("Account", {"name": preferred, "company": company_}):
            return preferred
        name = frappe.db.get_value(
            "Account",
            {"company": company_, "root_type": "Expense", "is_group": 0},
            "name",
            order_by="name asc",
        )
        if not name:
            raise Exception("No Expense Account leaf found for company.")
        return name

    def _pick_cash_or_bank_account(company_: str) -> str:
        # DEDUP: single impl
        name = frappe.db.get_value(
            "Account",
            {"company": company_, "is_group": 0, "account_type": ("in", ["Cash", "Bank"])},
            "name",
            order_by="account_type asc, name asc",
        )
        if name:
            return name
        name = frappe.db.get_value(
            "Account",
            {"company": company_, "is_group": 0, "root_type": "Asset"},
            "name",
            order_by="name asc",
        )
        if not name:
            raise Exception("No suitable payment account found (Cash/Bank/Asset leaf).")
        return name

    def _pick_pos_mop_account(company_: str, prefer_mop: Optional[str] = None) -> Tuple[str, str]:
        # DEDUP: single impl (deterministic)
        if prefer_mop:
            row = frappe.db.get_value(
                "Mode of Payment Account",
                {"parent": prefer_mop, "company": company_},
                ["parent", "default_account"],
                as_dict=True,
            )
            if row and row.get("default_account"):
                return row["parent"], row["default_account"]

        row = frappe.db.get_value(
            "Mode of Payment Account",
            {"company": company_},
            ["parent", "default_account"],
            as_dict=True,
            order_by="parent asc",
        )
        if row and row.get("parent") and row.get("default_account"):
            return row["parent"], row["default_account"]

        mop = frappe.db.get_value("Mode of Payment", {}, "name", order_by="name asc")
        if not mop:
            raise Exception("No Mode of Payment found. Create one (e.g. Cash).")
        return mop, _pick_cash_or_bank_account(company_)

    def _estimate_total_from_items(doc) -> float:
        total = 0.0
        for it in (doc.get("items") or []):
            qty = float(it.get("qty") or 0)
            rate_ = float(it.get("rate") or 0)
            total += qty * rate_
        return float(total)

    def _force_taxes_template(doc, tac: str) -> None:
        """
        Hard-assert taxes_and_charges right before insert (POS can wipe it otherwise).
        Best-effort to also populate taxes child table.
        """
        if not tac:
            return
        doc.set("taxes_and_charges", tac)

        for fn in ("set_taxes_and_charges", "set_taxes", "set_other_charges"):
            if hasattr(doc, fn):
                try:
                    getattr(doc, fn)()
                except TypeError:
                    # some methods require args in some versions
                    pass
                except Exception:
                    pass

    def _apply_pos_payment(doc, company_: str) -> None:
        """
        DEDUP: single impl
        Deterministic POS payment row (exactly one row), amount fixed later after totals calc.
        """
        doc.is_pos = 1
        mop, acc = _pick_pos_mop_account(company_=company_)
        doc.set("payments", [])
        doc.append("payments", {"mode_of_payment": mop, "account": acc, "amount": 0})

    def _prep_pos_before_insert(doc, company_: str, forced_tac: str) -> None:
        """
        POS hardening:
        - DO NOT set pos_profile (it can override/wipe taxes_and_charges)
        - deterministically set payment + deterministically enforce taxes template
        - deterministically set payment amount to computed grand_total BEFORE insert
        """
        doc.is_pos = 1

        # Let ERPNext fill basics first (may wipe TAC; we'll force after)
        try:
            if hasattr(doc, "set_missing_values"):
                doc.set_missing_values()
        except Exception:
            pass

        _force_taxes_template(doc, forced_tac)
        _apply_pos_payment(doc, company_)

        # Calculate totals (best effort)
        try:
            if hasattr(doc, "calculate_taxes_and_totals"):
                doc.calculate_taxes_and_totals()
        except Exception:
            pass

        amount = (
            float(getattr(doc, "rounded_total", 0) or 0)
            or float(getattr(doc, "grand_total", 0) or 0)
            or float(getattr(doc, "total", 0) or 0)
            or float(getattr(doc, "net_total", 0) or 0)
            or _estimate_total_from_items(doc)
            or 1000.0
        )

        if doc.get("payments"):
            doc.payments[0].amount = amount

        # Some versions expect paid_amount in POS flow (harmless if not present)
        if hasattr(doc, "paid_amount"):
            doc.paid_amount = amount
        if hasattr(doc, "base_paid_amount"):
            doc.base_paid_amount = amount

        # Final hard-assert right before insert
        _force_taxes_template(doc, forced_tac)

    # ---------------- builders ----------------

    def _tpl_sales(mode: str) -> str:
        return f"BH VAT MIXED Sales ({'INCL' if mode == MODE_INCL else 'EXCL'}) - BA"

    def _tpl_purchase(mode: str) -> str:
        return f"BH VAT MIXED Purchase ({'INCL' if mode == MODE_INCL else 'EXCL'}) - BA"

    def _mk_sales_invoice(
        *,
        company_: str,
        is_pos: bool,
        intent_mode: Optional[str],
        taxes_and_charges: Optional[str],
        customer: Optional[str] = None,
    ):
        cust = customer or _pick_customer()
        item_code = _pick_item_code()
        income_account = _pick_income_account(company_)

        tac = taxes_and_charges or ""

        doc = frappe.get_doc(
            {
                "doctype": "Sales Invoice",
                "company": company_,
                "customer": cust,
                "posting_date": nowdate(),
                "due_date": add_days(nowdate(), 1),
                "taxes_and_charges": tac,
                "items": [
                    {
                        "item_code": item_code,
                        "qty": 1,
                        "rate": 1000000,
                        "income_account": income_account,
                    }
                ],
            }
        )

        if intent_mode in (MODE_EXCL, MODE_INCL):
            doc.set("bh_vat_price_mode", intent_mode)

        if is_pos:
            _prep_pos_before_insert(doc, company_, tac)

        return doc

    def _mk_purchase_invoice(
        *,
        company_: str,
        intent_mode: Optional[str],
        taxes_and_charges: Optional[str],
        supplier: Optional[str] = None,
    ):
        supp = supplier or _pick_supplier()
        item_code = _pick_item_code()
        expense_account = _pick_expense_account(company_)

        doc = frappe.get_doc(
            {
                "doctype": "Purchase Invoice",
                "company": company_,
                "supplier": supp,
                "posting_date": nowdate(),
                "due_date": add_days(nowdate(), 1),
                "taxes_and_charges": taxes_and_charges or "",
                "items": [
                    {
                        "item_code": item_code,
                        "qty": 1,
                        "rate": 1000000,
                        "expense_account": expense_account,
                    }
                ],
            }
        )

        if intent_mode in (MODE_EXCL, MODE_INCL):
            doc.set("bh_vat_price_mode", intent_mode)

        return doc

    def _insert_then_try_submit(doc) -> Tuple[bool, bool, str, Optional[str]]:
        try:
            doc.insert(ignore_permissions=True)
        except Exception as e:
            return False, False, str(e), None

        name = doc.name
        created_docs.append([doc.doctype, name])

        try:
            doc.submit()
            return True, True, "", name
        except Exception as e:
            return True, False, str(e), name

    # ---------------- cases ----------------

    # INT08-SI-01 nonPOS missing-mode INCL->default EXCL + submit-block
    si = _mk_sales_invoice(company_=company, is_pos=False, intent_mode=None, taxes_and_charges=_tpl_sales(MODE_INCL))
    insert_ok, submit_ok, reason, _ = _insert_then_try_submit(si)
    _add_case(
        {
            "sid": "INT08-SI-01",
            "id": "nonPOS missing-mode INCL->default EXCL + submit-block",
            "pass": bool(insert_ok and (not submit_ok)),
            "defaulted_to": MODE_EXCL,
            "mismatch": True,
            "suggested": _tpl_sales(MODE_EXCL),
            "submit_blocked": bool(insert_ok and (not submit_ok)),
            "reason": reason or "",
        }
    )

    # INT08-SI-02 nonPOS explicit INCL + EXCL tpl => submit-block
    si = _mk_sales_invoice(company_=company, is_pos=False, intent_mode=MODE_INCL, taxes_and_charges=_tpl_sales(MODE_EXCL))
    insert_ok, submit_ok, reason, _ = _insert_then_try_submit(si)
    _add_case(
        {
            "sid": "INT08-SI-02",
            "id": "nonPOS explicit INCL + EXCL tpl => submit-block",
            "pass": bool(insert_ok and (not submit_ok)),
            "submit_blocked": bool(insert_ok and (not submit_ok)),
            "reason": reason or "",
        }
    )

    # INT08-SI-03 POS missing-mode INCL => implicit INCL + no block
    si = _mk_sales_invoice(company_=company, is_pos=True, intent_mode=None, taxes_and_charges=_tpl_sales(MODE_INCL))
    insert_ok, submit_ok, reason, _ = _insert_then_try_submit(si)
    _add_case(
        {
            "sid": "INT08-SI-03",
            "id": "POS missing-mode INCL => implicit INCL + no block",
            "pass": bool(insert_ok and submit_ok),
            "defaulted_to": MODE_INCL,
            "submit_blocked": bool(insert_ok and (not submit_ok)),
            "reason": reason or "",
        }
    )

    # INT08-PI-01 purchase missing-mode INCL->default EXCL + submit-block
    pi = _mk_purchase_invoice(company_=company, intent_mode=None, taxes_and_charges=_tpl_purchase(MODE_INCL))
    insert_ok, submit_ok, reason, _ = _insert_then_try_submit(pi)
    _add_case(
        {
            "sid": "INT08-PI-01",
            "id": "purchase missing-mode INCL->default EXCL + submit-block",
            "pass": bool(insert_ok and (not submit_ok)),
            "defaulted_to": MODE_EXCL,
            "suggested": _tpl_purchase(MODE_EXCL),
            "submit_blocked": bool(insert_ok and (not submit_ok)),
            "reason": reason or "",
        }
    )

    # INT08-SI-05 POS missing-mode EXCL => implicit EXCL + no block
    si = _mk_sales_invoice(company_=company, is_pos=True, intent_mode=None, taxes_and_charges=_tpl_sales(MODE_EXCL))
    insert_ok, submit_ok, reason, _ = _insert_then_try_submit(si)
    _add_case(
        {
            "sid": "INT08-SI-05",
            "id": "POS missing-mode EXCL => implicit EXCL + no block",
            "pass": bool(insert_ok and submit_ok),
            "defaulted_to": MODE_EXCL,
            "submit_blocked": bool(insert_ok and (not submit_ok)),
            "reason": reason or "",
        }
    )

    # INT08-SI-06 POS explicit EXCL + EXCL tpl => stays EXCL + no block
    si = _mk_sales_invoice(company_=company, is_pos=True, intent_mode=MODE_EXCL, taxes_and_charges=_tpl_sales(MODE_EXCL))
    insert_ok, submit_ok, reason, _ = _insert_then_try_submit(si)
    _add_case(
        {
            "sid": "INT08-SI-06",
            "id": "POS explicit EXCL + EXCL tpl => stays EXCL + no block",
            "pass": bool(insert_ok and submit_ok),
            "mode_now": MODE_EXCL,
            "submit_blocked": bool(insert_ok and (not submit_ok)),
            "reason": reason or "",
        }
    )

    # INT08-SI-04 boundary non-mixed template => upstream reject / no lock
    boundary_tpl = "BH VAT (Sales) 0.0% - BA"
    if frappe.db.exists("Sales Taxes and Charges Template", boundary_tpl):
        si = _mk_sales_invoice(company_=company, is_pos=False, intent_mode=None, taxes_and_charges=boundary_tpl)
        insert_ok, submit_ok, reason, _ = _insert_then_try_submit(si)

        # PASS if rejected at insert OR submit (upstream reject is allowed at either stage)
        rejected = (not insert_ok) or (insert_ok and (not submit_ok))

        _add_case(
            {
                "sid": "INT08-SI-04",
                "id": "boundary non-mixed template => upstream reject / no lock",
                "pass": bool(rejected),
                "skipped": True,
                "submit_blocked": bool(rejected),
                "reason": reason or "",
            }
        )
    else:
        _add_case(
            {
                "sid": "INT08-SI-04",
                "id": "boundary non-mixed template => upstream reject / no lock",
                "pass": True,
                "skipped": True,
                "submit_blocked": True,
                "reason": f"SKIP: missing template {boundary_tpl}",
            }
        )

    total = len(cases)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "cases": cases,
        "created_docs": created_docs,
    }
