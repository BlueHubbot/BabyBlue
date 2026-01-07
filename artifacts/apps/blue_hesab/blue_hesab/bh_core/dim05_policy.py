from __future__ import annotations

from typing import Optional, Sequence

import frappe

from blue_hesab.bh_core.company_legal import should_enforce_dimensions


def _s(v) -> str:
    return (v or "").strip()


def _req(doc, fieldname: str) -> str:
    v = _s(getattr(doc, fieldname, None))
    if not v:
        frappe.throw(f"فیلد «{fieldname}» برای ثبت سند الزامی است.", frappe.ValidationError)
    return v


def _ensure_dims(doc, required: Sequence[str]) -> None:
    for f in required:
        _req(doc, f)


def _propagate_header_dims(doc, childtable_field: str, fields: Sequence[str]) -> None:
    rows = list(getattr(doc, childtable_field, None) or [])
    if not rows:
        return

    hdr = {f: _s(getattr(doc, f, None)) for f in fields}
    for r in rows:
        for f in fields:
            if not _s(getattr(r, f, None)) and hdr.get(f):
                try:
                    setattr(r, f, hdr[f])
                except Exception:
                    pass


def _guard(doc) -> bool:
    try:
        company = _s(getattr(doc, "company", None))
        return bool(company and should_enforce_dimensions(company))
    except Exception:
        return False


def enforce_stock_entry_dimensions(doc, method: Optional[str] = None, *args, **kwargs) -> None:
    if not _guard(doc):
        return
    _ensure_dims(doc, ("bh_branch", "bh_tafsili_1"))
    _propagate_header_dims(doc, "items", ("bh_branch", "bh_tafsili_1", "bh_tafsili_2"))


def enforce_delivery_note_dimensions(doc, method: Optional[str] = None, *args, **kwargs) -> None:
    if not _guard(doc):
        return
    _ensure_dims(doc, ("bh_branch", "bh_tafsili_1"))
    _propagate_header_dims(doc, "items", ("bh_branch", "bh_tafsili_1", "bh_tafsili_2"))


def enforce_purchase_receipt_dimensions(doc, method: Optional[str] = None, *args, **kwargs) -> None:
    if not _guard(doc):
        return
    _ensure_dims(doc, ("bh_branch", "bh_tafsili_1"))
    _propagate_header_dims(doc, "items", ("bh_branch", "bh_tafsili_1", "bh_tafsili_2"))


def enforce_expense_claim_dimensions(doc, method: Optional[str] = None, *args, **kwargs) -> None:
    if not _guard(doc):
        return
    _ensure_dims(doc, ("bh_branch", "bh_tafsili_1"))
    _propagate_header_dims(doc, "expenses", ("bh_branch", "bh_tafsili_1", "bh_tafsili_2"))


def enforce_landed_cost_voucher_dimensions(doc, method: Optional[str] = None, *args, **kwargs) -> None:
    if not _guard(doc):
        return
    _ensure_dims(doc, ("bh_branch", "bh_tafsili_1"))
    _propagate_header_dims(doc, "items", ("bh_branch", "bh_tafsili_1", "bh_tafsili_2"))
