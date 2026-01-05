from __future__ import annotations

from typing import Optional

import frappe

from blue_hesab.bh_core.company_legal import should_enforce_dimensions
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error


def _get_company(doc) -> Optional[str]:
    try:
        v = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None) or ""
        v = (v or "").strip()
        return v or None
    except Exception:
        return None


def _get_str(obj, key: str) -> str:
    try:
        if hasattr(obj, "get"):
            v = obj.get(key)
        else:
            v = getattr(obj, key, None)
        return (v or "").strip()
    except Exception:
        return ""


def _raise_dim(msg: str) -> None:
    raise_bh_vat_error(BH_VAT_E_GENERIC, msg)


def enforce_journal_entry_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-02.A: Journal Entry
    - require cost_center per row (accounts)
    - keep it minimal & deterministic (no schema changes here)
    """
    company = _get_company(doc)
    if not company or not should_enforce_dimensions(company):
        return

    missing: list[str] = []

    # rows: Journal Entry Account
    try:
        rows = doc.get("accounts") or []
    except Exception:
        rows = getattr(doc, "accounts", None) or []

    idx = 0
    for r in (rows or []):
        idx += 1

        # skip empty rows
        debit = _get_str(r, "debit_in_account_currency") or _get_str(r, "debit")
        credit = _get_str(r, "credit_in_account_currency") or _get_str(r, "credit")
        if not debit and not credit:
            continue

        cc = _get_str(r, "cost_center")
        if not cc:
            missing.append(f"سطر {idx}: مرکز هزینه")

    if missing:
        msg = "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- " + "\n- ".join(missing)
        _raise_dim(msg)


def enforce_payment_entry_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-02.A: Payment Entry
    - require cost_center (if field exists)
    """
    company = _get_company(doc)
    if not company or not should_enforce_dimensions(company):
        return

    # only enforce if field exists on the DocType (safe across versions)
    try:
        if getattr(getattr(doc, "meta", None), "has_field", lambda _x: False)("cost_center"):
            cc = _get_str(doc, "cost_center")
            if not cc:
                _raise_dim("BH DIM: برای ثبت سند، «مرکز هزینه» اجباری است.")
    except Exception:
        # never crash submit because of meta issues; but we still want enforcement when possible
        cc = _get_str(doc, "cost_center")
        if not cc:
            _raise_dim("BH DIM: برای ثبت سند، «مرکز هزینه» اجباری است.")
