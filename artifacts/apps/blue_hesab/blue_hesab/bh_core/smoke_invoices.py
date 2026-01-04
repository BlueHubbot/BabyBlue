from __future__ import annotations

from typing import Any, Dict, Optional
from blue_hesab.bh_core.dim_testkit import apply_required_dims

import frappe
from frappe.utils import nowdate, nowtime


def _pick_one(doctype: str, filters: Optional[Dict[str, Any]] = None) -> str:
    filters = filters or {}
    rows = frappe.get_all(doctype, filters=filters, pluck="name", limit=1)
    if not rows:
        raise Exception(f"No {doctype} found for filters={filters}")
    return rows[0]


def _pick_company(company: Optional[str]) -> str:
    if company:
        return company
    try:
        c = frappe.defaults.get_user_default("Company")
        if c:
            return c
    except Exception:
        pass
    return _pick_one("Company")


def _pick_account(company: str, *, account_type: Optional[str] = None, root_type: Optional[str] = None) -> str:
    f: Dict[str, Any] = {"company": company, "is_group": 0}
    if account_type:
        f["account_type"] = account_type
    if root_type:
        f["root_type"] = root_type

    acc = frappe.db.get_value("Account", f, "name")
    if acc:
        return acc

    acc = frappe.db.get_value("Account", {"company": company, "is_group": 0}, "name")
    if acc:
        return acc

    raise Exception(f"No Account found for company={company}")


def _pick_cost_center(company: str) -> str:
    cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
    if cc:
        return cc
    cc = frappe.db.get_value("Cost Center", {"is_group": 0}, "name")
    if cc:
        return cc
    raise Exception("No Cost Center found")


def _pick_item() -> Dict[str, Any]:
    item = frappe.db.get_value("Item", {"disabled": 0, "is_stock_item": 0}, ["name", "is_stock_item"], as_dict=True)
    if item:
        return item
    item = frappe.db.get_value("Item", {"disabled": 0}, ["name", "is_stock_item"], as_dict=True)
    if item:
        return item
    raise Exception("No Item found")


def _pick_warehouse(company: str) -> Optional[str]:
    wh = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
    if wh:
        return wh
    return frappe.db.get_value("Warehouse", {"is_group": 0}, "name")


def _intent_value(mode: str) -> str:
    # Custom Field options are English in your setup: Exclusive / Inclusive
    mode = (mode or "Exclusive").strip().lower()
    return "Inclusive" if mode.startswith("inc") else "Exclusive"


def _pick_sales_taxes_template(company: str, mode: str) -> str:
    intent = _intent_value(mode)
    token = "(INCL)" if intent == "Inclusive" else "(EXCL)"
    rows = frappe.get_all(
        "Sales Taxes and Charges Template",
        filters={"company": company, "name": ["like", f"BH VAT MIXED Sales {token}%"]},
        pluck="name",
        order_by="name asc",
        limit=1,
    )
    if rows:
        return rows[0]
    rows = frappe.get_all(
        "Sales Taxes and Charges Template",
        filters={"company": company},
        pluck="name",
        order_by="modified desc",
        limit=1,
    )
    if rows:
        return rows[0]
    raise Exception(f"No Sales Taxes and Charges Template found for company={company}")


def _pick_purchase_taxes_template(company: str, mode: str) -> str:
    intent = _intent_value(mode)
    token = "(INCL)" if intent == "Inclusive" else "(EXCL)"
    rows = frappe.get_all(
        "Purchase Taxes and Charges Template",
        filters={"company": company, "name": ["like", f"BH VAT MIXED Purchase {token}%"]},
        pluck="name",
        order_by="name asc",
        limit=1,
    )
    if rows:
        return rows[0]
    rows = frappe.get_all(
        "Purchase Taxes and Charges Template",
        filters={"company": company},
        pluck="name",
        order_by="modified desc",
        limit=1,
    )
    if rows:
        return rows[0]
    raise Exception(f"No Purchase Taxes and Charges Template found for company={company}")


def create_sales_invoice_and_submit(
    *,
    company: Optional[str] = None,
    customer: Optional[str] = None,
    item_code: Optional[str] = None,
    qty: float = 1.0,
    rate: float = 100000.0,
    vat_price_mode: str = "Exclusive",
    taxes_and_charges: Optional[str] = None,
) -> Dict[str, Any]:
    company = _pick_company(company)
    customer = (
        customer
        or (_pick_one("Customer", {"disabled": 0}) if frappe.db.has_column("Customer", "disabled") else _pick_one("Customer"))
    )
    it = _pick_item()
    item_code = item_code or it["name"]

    receivable = _pick_account(company, account_type="Receivable")
    income = _pick_account(company, root_type="Income")
    cost_center = _pick_cost_center(company)

    intent = _intent_value(vat_price_mode)
    taxes_and_charges = taxes_and_charges or _pick_sales_taxes_template(company, intent)

    item_row: Dict[str, Any] = {
        "item_code": item_code,
        "qty": qty,
        "rate": rate,
        "income_account": income,
        "cost_center": cost_center,
    }
    if int(it.get("is_stock_item") or 0) == 1:
        wh = _pick_warehouse(company)
        if wh:
            item_row["warehouse"] = wh

    si = frappe.get_doc(
        {
            "doctype": "Sales Invoice",
            "company": company,
            "customer": customer,
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "set_posting_time": 1,
            "due_date": nowdate(),
            "debit_to": receivable,
            "taxes_and_charges": taxes_and_charges,
            "items": [item_row],
        }
    )

    # force Intent to match template (prevents vat11_lock_intent_guard)
    try:
        if si.meta.has_field("bh_vat_price_mode"):
            si.set("bh_vat_price_mode", intent)
    except Exception:
        pass
    from blue_hesab.bh_core.dim_testkit import apply_invoice_dimensions
    apply_invoice_dimensions(si, company=company)
    apply_required_dims(si, company=company)
    si.insert(ignore_permissions=True)

    si.submit()

    lo = frappe.db.get_value(
        "BH Legal Output",
        {"output_type": "VAT_INVOICE", "reference_doctype": "Sales Invoice", "reference_name": si.name},
        "name",
    )
    return {
        "sales_invoice": si.name,
        "company": company,
        "customer": customer,
        "bh_vat_price_mode": intent,
        "taxes_and_charges": taxes_and_charges,
        "legal_output": lo,
    }


def create_purchase_invoice_and_submit(
    *,
    company: Optional[str] = None,
    supplier: Optional[str] = None,
    item_code: Optional[str] = None,
    qty: float = 1.0,
    rate: float = 100000.0,
    vat_price_mode: str = "Exclusive",
    taxes_and_charges: Optional[str] = None,
) -> Dict[str, Any]:
    company = _pick_company(company)
    supplier = (
        supplier
        or (_pick_one("Supplier", {"disabled": 0}) if frappe.db.has_column("Supplier", "disabled") else _pick_one("Supplier"))
    )
    it = _pick_item()
    item_code = item_code or it["name"]

    payable = _pick_account(company, account_type="Payable")
    expense = _pick_account(company, root_type="Expense")
    cost_center = _pick_cost_center(company)

    intent = _intent_value(vat_price_mode)
    taxes_and_charges = taxes_and_charges or _pick_purchase_taxes_template(company, intent)

    item_row: Dict[str, Any] = {
        "item_code": item_code,
        "qty": qty,
        "rate": rate,
        "expense_account": expense,
        "cost_center": cost_center,
    }
    if int(it.get("is_stock_item") or 0) == 1:
        wh = _pick_warehouse(company)
        if wh:
            item_row["warehouse"] = wh

    pi = frappe.get_doc(
        {
            "doctype": "Purchase Invoice",
            "company": company,
            "supplier": supplier,
            "posting_date": nowdate(),
            "posting_time": nowtime(),
            "set_posting_time": 1,
            "credit_to": payable,
            "bill_no": f"SMOKE-{frappe.generate_hash(length=8)}",
            "bill_date": nowdate(),
            "taxes_and_charges": taxes_and_charges,
            "items": [item_row],
        }
    )

    try:
        if pi.meta.has_field("bh_vat_price_mode"):
            pi.set("bh_vat_price_mode", intent)
    except Exception:
        pass
    from blue_hesab.bh_core.dim_testkit import apply_invoice_dimensions
    apply_invoice_dimensions(pi, company=company)
    apply_required_dims(pi, company=company)
    pi.insert(ignore_permissions=True)
    pi.submit()

    lo = frappe.db.get_value(
        "BH Legal Output",
        {"output_type": "VAT_INVOICE", "reference_doctype": "Purchase Invoice", "reference_name": pi.name},
        "name",
    )
    return {
        "purchase_invoice": pi.name,
        "company": company,
        "supplier": supplier,
        "bh_vat_price_mode": intent,
        "taxes_and_charges": taxes_and_charges,
        "legal_output": lo,
    }


def cancel_doc(*, doctype: str, name: str) -> dict[str, Any]:
    """Cancel a submitted doc and return related BH Legal Output rows."""
    doc = frappe.get_doc(doctype, name)
    before = int(doc.docstatus or 0)
    doc.cancel()
    after = int(doc.docstatus or 0)
    outs = frappe.get_all(
        "BH Legal Output",
        filters={"reference_doctype": doctype, "reference_name": name},
        fields=["name","output_type","correction_reason","previous_output","schema_version","generator_build","modified"],
        order_by="modified desc",
        limit_page_length=50,
    )
    return {"doctype": doctype, "name": name, "before_docstatus": before, "after_docstatus": after, "legal_outputs": outs}
