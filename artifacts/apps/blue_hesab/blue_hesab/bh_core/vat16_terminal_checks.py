# apps/blue_hesab/blue_hesab/bh_core/vat16_terminal_checks.py
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import frappe
from frappe.exceptions import ValidationError
from .vat_pipe_templates import infer_mixed_template_name
from blue_hesab.bh_core.dimensions_policy import bh_autofill_min_invoice_dims


# --- helpers --------------------------------------------------------------

def _sp_name(prefix: str = "bhvat16") -> str:
    h = getattr(frappe, "generate_hash", None)
    suffix = h(length=6) if callable(h) else str(int(time.time()))[-6:]
    raw = f"{prefix}_{int(time.time())}_{suffix}"
    return re.sub(r"[^0-9A-Za-z_]+", "_", raw)


def _rollback_to_savepoint(sp: str) -> None:
    try:
        frappe.db.rollback(save_point=sp)  # type: ignore[arg-type]
        return
    except TypeError:
        pass
    except Exception:
        pass

    try:
        frappe.db.sql(f"ROLLBACK TO SAVEPOINT `{sp}`")
        return
    except Exception:
        pass

    frappe.db.rollback()


def _as_float(x: Any) -> float:
    if x is None:
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return 0.0
        try:
            return float(s)
        except Exception:
            return 0.0
    return 0.0


def _close(a: float, b: float, tol: float = 0.01) -> bool:
    return abs(a - b) <= tol


def _extract_tax_amount(val: Any) -> float:
    """
    Robust parser for ERPNext item_wise_tax_detail value shapes across versions.
    Common shapes:
      - [rate, amount]
      - [amount] or [rate, amount, ...]
      - {"tax_amount": X, ...}
      - numeric
    """
    if val is None:
        return 0.0

    if isinstance(val, (int, float, str)):
        return _as_float(val)

    if isinstance(val, list):
        # try second element first (classic [rate, amount])
        if len(val) >= 2 and isinstance(val[1], (int, float, str)):
            return _as_float(val[1])
        # scan for last numeric
        for x in reversed(val):
            if isinstance(x, (int, float, str)):
                fx = _as_float(x)
                # prefer non-zero if any
                if fx != 0.0:
                    return fx
        return 0.0

    if isinstance(val, dict):
        for k in ("tax_amount", "amount", "tax", "tax_amount_after_discount_amount"):
            if k in val:
                return _as_float(val.get(k))
        # fallback: find any numeric leaf
        for v in val.values():
            if isinstance(v, (int, float, str)):
                fx = _as_float(v)
                if fx != 0.0:
                    return fx
        return 0.0

    return 0.0


def _parse_item_wise(s: str) -> Dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def _get_bh_settings() -> Any:
    return frappe.get_single("BH Settings")


def _find_item_tax_template(code: str, company_abbr: str) -> str:
    """
    Expected template names (your current naming):
      - VAT ۹٪ استاندارد (STD_9) - BA
      - VAT صفر درصد (ZERO) - BA
      - VAT معاف (EXEMPT) - BA
      - VAT صادرات ۰٪ (EXPORT_0) - BA
    """
    # search by markers first
    patterns = [
        f"%(STD_9)% - {company_abbr}",
        f"%(ZERO)% - {company_abbr}",
        f"%(EXEMPT)% - {company_abbr}",
        f"%(EXPORT_0)% - {company_abbr}",
    ]
    idx = {"STD_9": 0, "ZERO": 1, "EXEMPT": 2, "EXPORT_0": 3}.get(code)
    if idx is None:
        raise ValidationError(f"VAT-16: unknown code '{code}'")
    like = patterns[idx]

    name = frappe.db.get_value("Item Tax Template", {"name": ["like", like]}, "name")
    if not name:
        # fallback: without abbr
        like2 = like.replace(f" - {company_abbr}", "")
        name = frappe.db.get_value("Item Tax Template", {"name": ["like", like2]}, "name")

    if not name:
        raise ValidationError(f"VAT-16: Item Tax Template not found for {code} (like={like})")
    return str(name)


def _pick_item_for_template(template_name: str) -> str:
    # your custom field name:
    field = "bh_item_tax_template"
    if not frappe.db.has_column("Item", field):
        raise ValidationError("VAT-16: Missing custom field Item.bh_item_tax_template")

    item = frappe.db.get_value("Item", {field: template_name, "disabled": 0}, "name")
    if not item:
        raise ValidationError(f"VAT-16: No Item found with bh_item_tax_template='{template_name}'")
    return str(item)


def _ensure_customer(company: str) -> str:
    name = "مشتری تست VAT"
    if frappe.db.exists("Customer", name):
        return name
    doc = frappe.get_doc({"doctype": "Customer", "customer_name": name, "customer_type": "Company"})
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_supplier(company: str) -> str:
    name = "BH VAT REG Supplier"
    if frappe.db.exists("Supplier", name):
        return name
    doc = frappe.get_doc({"doctype": "Supplier", "supplier_name": name, "supplier_type": "Company"})
    doc.insert(ignore_permissions=True)
    return doc.name


def _find_leaf_account_like(company: str, contains: str, root_type: str) -> Optional[str]:
    # tries exact “... - BA” names first (your environment)
    name = frappe.db.get_value("Account", {"company": company, "name": ["like", f"%{contains}%"], "is_group": 0}, "name")
    if name:
        return str(name)
    # fallback by root_type
    name = frappe.db.get_value("Account", {"company": company, "root_type": root_type, "is_group": 0}, "name")
    return str(name) if name else None


@dataclass
class Vat16Case:
    label: str
    doctype: str
    mode: str  # "Exclusive"/"Inclusive"
    expected_std_tax: float


def _make_sales_invoice(
    company: str,
    mode: str,
    items: List[Tuple[str, float]],
    income_account: Optional[str],
    taxes_and_charges: Optional[str] = None,
) -> Any:
    from frappe.utils import nowdate

    customer = _ensure_customer(company)

    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.customer = customer
    si.posting_date = nowdate()
    si.due_date = nowdate()

    try:
        si.bh_vat_price_mode = mode
    except Exception:
        pass

    if str(mode).strip().lower().startswith("incl"):
        try:
            si.set("bh_vat_inclusive_intent", 1)
        except Exception:
            pass

    if not taxes_and_charges:
        tpl_name, _dt = infer_mixed_template_name(kind="sales", company=company, axis=None, mode=mode)
        taxes_and_charges = tpl_name

    if taxes_and_charges:
        si.taxes_and_charges = taxes_and_charges
        try:
            si.set_taxes_and_charges()
        except Exception:
            pass

    si.flags.ignore_mandatory = True

    for item_code, rate in items:
        row = {"item_code": item_code, "qty": 1, "rate": rate}
        if income_account:
            row["income_account"] = income_account
        si.append("items", row)

    bh_autofill_min_invoice_dims(si)

    # hard fill required DIMs if present on this site/schema
    try:
        if hasattr(si, "bh_branch") and not si.get("bh_branch"):
            si.set("bh_branch", _pick_required_link_value(si.doctype, "bh_branch", company))
        if hasattr(si, "bh_tafsili_1") and not si.get("bh_tafsili_1"):
            si.set("bh_tafsili_1", _pick_required_link_value(si.doctype, "bh_tafsili_1", company))
    except Exception:
        pass

    si.insert(ignore_permissions=True)
    si.submit()
    return si


def _make_purchase_invoice(
    company: str,
    mode: str,
    items: List[Tuple[str, float]],
    expense_account: Optional[str],
    taxes_and_charges: Optional[str] = None,
) -> Any:
    from frappe.utils import nowdate

    supplier = _ensure_supplier(company)

    pi = frappe.new_doc("Purchase Invoice")
    pi.company = company
    pi.supplier = supplier
    pi.posting_date = nowdate()
    pi.bill_date = nowdate()

    try:
        pi.bh_vat_price_mode = mode
    except Exception:
        pass

    if str(mode).strip().lower().startswith("incl"):
        try:
            pi.set("bh_vat_inclusive_intent", 1)
        except Exception:
            pass

    if not taxes_and_charges:
        tpl_name, _dt = infer_mixed_template_name(kind="purchase", company=company, axis=None, mode=mode)
        taxes_and_charges = tpl_name

    if taxes_and_charges:
        pi.taxes_and_charges = taxes_and_charges
        try:
            pi.set_taxes_and_charges()
        except Exception:
            pass

    pi.flags.ignore_mandatory = True

    for item_code, rate in items:
        row = {"item_code": item_code, "qty": 1, "rate": rate}
        if expense_account:
            row["expense_account"] = expense_account
        pi.append("items", row)

    bh_autofill_min_invoice_dims(pi)

    # hard fill required DIMs if present on this site/schema
    try:
        if hasattr(pi, "bh_branch") and not pi.get("bh_branch"):
            pi.set("bh_branch", _pick_required_link_value(pi.doctype, "bh_branch", company))
        if hasattr(pi, "bh_tafsili_1") and not pi.get("bh_tafsili_1"):
            pi.set("bh_tafsili_1", _pick_required_link_value(pi.doctype, "bh_tafsili_1", company))
    except Exception:
        pass

    pi.insert(ignore_permissions=True)
    pi.submit()
    return pi


def _vat_row_item_wise(doc, vat_account: str) -> Dict[str, Any]:
    taxes = doc.get("taxes") or []
    row = None
    for r in taxes:
        if (r.get("account_head") or "") == vat_account:
            row = r
            break
    if not row:
        raise ValidationError(f"VAT-16: VAT row not found on {doc.doctype} {doc.name} for account_head='{vat_account}'")

    detail = _parse_item_wise(row.get("item_wise_tax_detail") or "")
    if not detail:
        raise ValidationError(f"VAT-16: item_wise_tax_detail is empty on {doc.doctype} {doc.name}")

    return {"row": row, "detail": detail}


def _assert_item_wise(doc, vat_account: str, expected_by_item: Dict[str, float]) -> None:
    pack = _vat_row_item_wise(doc, vat_account)
    row = pack["row"]
    detail = pack["detail"]

    # map: try item_code first; if missing allow item_name fallback
    items = doc.get("items") or []
    missing_keys: List[str] = []

    total_from_detail = 0.0
    for it in items:
        code = it.get("item_code")
        name = it.get("item_name")
        key = code if code in detail else (name if name in detail else None)
        if not key:
            missing_keys.append(code or name or "?")
            continue

        tax_amt = _extract_tax_amount(detail.get(key))
        exp = expected_by_item.get(code, 0.0)
        if not _close(tax_amt, exp, tol=0.5):
            raise ValidationError(
                f"VAT-16: item tax mismatch on {doc.doctype} {doc.name}: item='{code}' got={tax_amt} expected={exp}"
            )
        total_from_detail += tax_amt

    if missing_keys:
        raise ValidationError(
            f"VAT-16: missing items in item_wise_tax_detail on {doc.doctype} {doc.name}: {', '.join(missing_keys)}"
        )

    row_tax_amount = _as_float(row.get("tax_amount"))
    if not _close(total_from_detail, row_tax_amount, tol=1.0):
        raise ValidationError(
            f"VAT-16: sum(detail) != tax_amount on {doc.doctype} {doc.name}: sum={total_from_detail} row_tax_amount={row_tax_amount}"
        )


# --- public runner ---------------------------------------------------------

@frappe.whitelist()
def run_cli(company: str = "BlueAPi") -> dict:
    """
    VAT-16:
      - Create SI/PI with MIXED items (STD_9 + ZERO + EXEMPT + EXPORT_0)
      - Verify item_wise_tax_detail contains all items
      - Verify per-item VAT amounts:
          EXCL: STD=90,000
          INCL: STD=82,568.81  (for gross=1,000,000)
          others=0
      - Verify sum(item_wise) == tax_amount
      - Run inside SAVEPOINT and rollback (no DB residue)
    """
    s = _get_bh_settings()
    if (s.default_company or "").strip() and (s.default_company or "").strip() != company:
        raise ValidationError(f"VAT-16: company must be BH Settings.default_company ({s.default_company})")

    abbr = frappe.db.get_value("Company", company, "abbr") or "BA"

    sales_vat_account = s.default_sales_vat_account
    purchase_vat_account = s.default_purchase_vat_account
    if not sales_vat_account or not purchase_vat_account:
        raise ValidationError("VAT-16: BH Settings VAT accounts are not set")

    # templates
    tpl_std = _find_item_tax_template("STD_9", abbr)
    tpl_zero = _find_item_tax_template("ZERO", abbr)
    tpl_exempt = _find_item_tax_template("EXEMPT", abbr)
    tpl_export = _find_item_tax_template("EXPORT_0", abbr)

    # pick items tied to templates
    item_std = _pick_item_for_template(tpl_std)
    item_zero = _pick_item_for_template(tpl_zero)
    item_exempt = _pick_item_for_template(tpl_exempt)
    item_export = _pick_item_for_template(tpl_export)

    # accounts (best effort)
    income_account = _find_leaf_account_like(company, "سرویس", "Income")
    expense_account = _find_leaf_account_like(company, "اختلال", "Expense")

    # Canonical numbers aligned with your existing CI patterns:
    # Make total (mostly) around 4,000,000 and ensure INCL extraction is stable.
    std_net_excl = 1_000_000.0              # EXCL: net base
    std_gross_incl = 1_000_000.0            # INCL: gross (tax included)
    expected_std_tax_excl = 90_000.0        # 9% of 1,000,000
    expected_std_tax_incl = round(std_gross_incl * 9.0 / 109.0, 2)  # 82,568.81

    amt_zero = 1_000_000.0
    amt_exempt = 1_000_000.0
    amt_export = 1_000_000.0

    cases = [
        Vat16Case("VAT16-SI-EXCL", "Sales Invoice", "Exclusive", expected_std_tax_excl),
        Vat16Case("VAT16-SI-INCL", "Sales Invoice", "Inclusive", expected_std_tax_incl),
        Vat16Case("VAT16-PI-EXCL", "Purchase Invoice", "Exclusive", expected_std_tax_excl),
        Vat16Case("VAT16-PI-INCL", "Purchase Invoice", "Inclusive", expected_std_tax_incl),
    ]

    sp = _sp_name()
    frappe.db.savepoint(sp)

    results: Dict[str, str] = {}
    ok = True

    try:
        for c in cases:
            try:
                if c.doctype == "Sales Invoice":
                    items = [
                        (item_std, std_net_excl if c.mode == "Exclusive" else std_gross_incl),
                        (item_zero, amt_zero),
                        (item_exempt, amt_exempt),
                        (item_export, amt_export),
                    ]
                    axis = "INCL" if c.mode == "Inclusive" else "EXCL"
                    tpl_name, _ = infer_mixed_template_name(kind="sales", company=company, axis=axis)
                    doc = _make_sales_invoice(company, c.mode, items, income_account, taxes_and_charges=tpl_name)
                    expected = {
                        item_std: c.expected_std_tax,
                        item_zero: 0.0,
                        item_exempt: 0.0,
                        item_export: 0.0,
                    }
                    _assert_item_wise(doc, sales_vat_account, expected)

                else:
                    items = [
                        (item_std, std_net_excl if c.mode == "Exclusive" else std_gross_incl),
                        (item_zero, amt_zero),
                        (item_exempt, amt_exempt),
                        (item_export, amt_export),
                    ]
                    axis = "INCL" if c.mode == "Inclusive" else "EXCL"
                    tpl_name, _ = infer_mixed_template_name(kind="purchase", company=company, axis=axis)
                    doc = _make_purchase_invoice(company, c.mode, items, expense_account, taxes_and_charges=tpl_name)

                    expected = {
                        item_std: c.expected_std_tax,
                        item_zero: 0.0,
                        item_exempt: 0.0,
                        item_export: 0.0,
                    }
                    _assert_item_wise(doc, purchase_vat_account, expected)

                results[c.label] = "PASS"

            except Exception as e:
                ok = False
                results[c.label] = f"FAIL - {e}"

    finally:
        _rollback_to_savepoint(sp)

    print("\n=== VAT-16 ITEM_WISE_TAX_DETAIL CHECKS ===")
    for k in sorted(results.keys()):
        print(f"{k}: {results[k]}")

    out = {**results, "ok": ok}
    if not ok:
        raise ValidationError(json.dumps(out, ensure_ascii=False))

    return out
