from __future__ import annotations

from typing import Iterable, List, Tuple

import frappe

from .company_legal import should_enforce_dimensions
from .exc import raise_bh_vat_error


REQ = ("bh_branch", "bh_tafsili_1")
OPT = ("bh_tafsili_2",)


def _has_field(doc, fieldname: str) -> bool:
    try:
        return bool(getattr(doc.meta, "has_field")(fieldname))
    except Exception:
        return False


def _get(doc, fieldname: str):
    try:
        return getattr(doc, fieldname, None)
    except Exception:
        return None


def _set(doc, fieldname: str, value) -> None:
    try:
        setattr(doc, fieldname, value)
    except Exception:
        pass


def _iter_child_rows(doc) -> Iterable[Tuple[str, object]]:
    """
    Yield (table_fieldname, row_doc) for every child row across all Table fields.
    """
    try:
        for df in (doc.meta.fields or []):
            if getattr(df, "fieldtype", None) == "Table":
                fn = getattr(df, "fieldname", None)
                if not fn:
                    continue
                rows = doc.get(fn) or []
                for r in rows:
                    yield fn, r
    except Exception:
        return


def _enforce_doc_dims(doc, *, label: str) -> None:
    company = (getattr(doc, "company", None) or "").strip()
    if not company:
        return

    try:
        if not should_enforce_dimensions(company):
            return
    except Exception:
        return

    missing: List[str] = []

    # Header required dims (if fields exist)
    header_vals = {}
    for f in REQ + OPT:
        if _has_field(doc, f):
            header_vals[f] = _get(doc, f)
    for f in REQ:
        if _has_field(doc, f) and not header_vals.get(f):
            missing.append(f"سرصفحه: {f}")

    # Propagate header -> rows (best effort)
    for _, row in _iter_child_rows(doc):
        for f in REQ + OPT:
            if _has_field(row, f) and not _get(row, f) and header_vals.get(f):
                _set(row, f, header_vals[f])

    # Row required dims (only if row has those fields)
    for _, row in _iter_child_rows(doc):
        idx = _get(row, "idx") or "?"
        for f in REQ:
            if _has_field(row, f) and not _get(row, f):
                missing.append(f"ردیف {idx}: {f}")

    if missing:
        msg = (
            f"BH DIM: برای ثبت سند «{label}» ابعاد مالی اجباری هستند.\n"
            "موارد ناقص:\n- " + "\n- ".join(missing)
        )
        raise_bh_vat_error(
            msg,
            context={"company": company, "doctype": getattr(doc, "doctype", ""), "name": getattr(doc, "name", "")},
        )


def enforce_stock_entry_dimensions(doc, method=None, *args, **kwargs) -> None:
    _enforce_doc_dims(doc, label="Stock Entry")


def enforce_stock_reconciliation_dimensions(doc, method=None, *args, **kwargs) -> None:
    _enforce_doc_dims(doc, label="Stock Reconciliation")


def enforce_delivery_note_dimensions(doc, method=None, *args, **kwargs) -> None:
    _enforce_doc_dims(doc, label="Delivery Note")


def enforce_purchase_receipt_dimensions(doc, method=None, *args, **kwargs) -> None:
    _enforce_doc_dims(doc, label="Purchase Receipt")


def enforce_pos_invoice_dimensions(doc, method=None, *args, **kwargs) -> None:
    _enforce_doc_dims(doc, label="POS Invoice")


def enforce_expense_claim_dimensions(doc, method=None, *args, **kwargs) -> None:
    _enforce_doc_dims(doc, label="Expense Claim")
