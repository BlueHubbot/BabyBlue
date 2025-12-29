from __future__ import annotations

from typing import List, Optional, Tuple

import frappe
from frappe.exceptions import ValidationError

from blue_hesab.bh_core.company_legal import should_enforce_dimensions
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error


def _get_company(doc) -> Optional[str]:
    try:
        return (getattr(doc, "company", None) or doc.get("company") or "").strip()
    except Exception:
        return None


def enforce_invoice_dimensions(doc) -> None:
    company = _get_company(doc)
    if not should_enforce_dimensions(company):
        return

    # Header fallbacks
    hdr_branch = (getattr(doc, "bh_branch", None) or (doc.get("bh_branch") if hasattr(doc, "get") else None) or "").strip()
    hdr_t1 = (getattr(doc, "bh_tafsili_1", None) or (doc.get("bh_tafsili_1") if hasattr(doc, "get") else None) or "").strip()
    hdr_t2 = (getattr(doc, "bh_tafsili_2", None) or (doc.get("bh_tafsili_2") if hasattr(doc, "get") else None) or "").strip()

    missing: List[str] = []

    items = doc.get("items") or []
    for i, row in enumerate(items, start=1):
        # auto-fill from header when empty
        if hdr_branch and not (row.get("bh_branch") or "").strip():
            row.bh_branch = hdr_branch
        if hdr_t1 and not (row.get("bh_tafsili_1") or "").strip():
            row.bh_tafsili_1 = hdr_t1
        if hdr_t2 and not (row.get("bh_tafsili_2") or "").strip():
            row.bh_tafsili_2 = hdr_t2

        cc = (row.get("cost_center") or "").strip()
        pr = (row.get("project") or "").strip()
        br = (row.get("bh_branch") or "").strip()
        t1 = (row.get("bh_tafsili_1") or "").strip()
        t2 = (row.get("bh_tafsili_2") or "").strip()

        if not cc:
            missing.append(f"سطر {i}: Cost Center")
        if not pr:
            missing.append(f"سطر {i}: Project")
        if not br:
            missing.append(f"سطر {i}: Branch")
        if not t1:
            missing.append(f"سطر {i}: تفصیلی ۱")
        if not t2:
            missing.append(f"سطر {i}: تفصیلی ۲")

    if missing:
        msg = "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- " + "\n- ".join(missing)
        # Use BH VAT error wrapper to keep Persian UI + consistent logging
        raise_bh_vat_error(BH_VAT_E_GENERIC, msg, context={"company": company, "doctype": doc.doctype, "name": doc.name})


def apply_gl_dimensions_from_invoice(doc) -> None:
    """Best-effort: stamp voucher-level dimensions on GL Entries (does not split per-item)."""
    try:
        company = _get_company(doc) or ""
        if not should_enforce_dimensions(company):
            return
        voucher_type = doc.doctype
        voucher_no = doc.name

        br = (getattr(doc, "bh_branch", None) or "").strip()
        t1 = (getattr(doc, "bh_tafsili_1", None) or "").strip()
        t2 = (getattr(doc, "bh_tafsili_2", None) or "").strip()

        if not (br or t1 or t2):
            return

        frappe.db.sql(
            """
            UPDATE `tabGL Entry`
               SET bh_branch = COALESCE(NULLIF(bh_branch,''), %(br)s),
                   bh_tafsili_1 = COALESCE(NULLIF(bh_tafsili_1,''), %(t1)s),
                   bh_tafsili_2 = COALESCE(NULLIF(bh_tafsili_2,''), %(t2)s)
             WHERE voucher_type = %(vt)s AND voucher_no = %(vn)s
            """,
            {"br": br, "t1": t1, "t2": t2, "vt": voucher_type, "vn": voucher_no},
        )
    except Exception:
        # do not block submit; missing CFs etc will be caught elsewhere
        return
