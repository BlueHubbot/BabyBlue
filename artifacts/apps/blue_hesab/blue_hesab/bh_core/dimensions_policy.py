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


def _get_str(doc, key: str) -> str:
    try:
        v = getattr(doc, key, None)
        if v is None and hasattr(doc, "get"):
            v = doc.get(key)
        return (v or "").strip()
    except Exception:
        return ""


def enforce_invoice_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    P0.5: Block SUBMIT if mandatory financial dimensions are missing (SI/PI).
    IMPORTANT: Draft/Insert must NOT be blocked.
    Hook-safe signature: (doc, method, *args, **kwargs)
    """

    # Only enforce on submit path
    try:
        action = getattr(doc, "_action", None)
    except Exception:
        action = None

    if method not in ("before_submit", "on_submit"):
        # fallback: if called without method, only enforce during submit action
        if action != "submit":
            return

    # Idempotent in the same submit flow (only mark on success)
    if getattr(doc, "_bh_dim_enforced", False):
        return

    company = _get_company(doc)
    if not should_enforce_dimensions(company):
        return

    # ---- Header dims ----
    hdr_branch = _get_str(doc, "bh_branch")
    hdr_t1 = _get_str(doc, "bh_tafsili_1")
    hdr_t2 = _get_str(doc, "bh_tafsili_2")

    missing: list[str] = []

    if not hdr_branch:
        missing.append("سربرگ: شعبه")
    if not hdr_t1:
        missing.append("سربرگ: تفصیلی ۱")
    # bh_tafsili_2 فعلاً اختیاری است

    # ---- Detect if row-level bh_* fields exist (optional) ----
    row_has_bh_fields = False
    try:
        items_field = getattr(getattr(doc, "meta", None), "get_field", lambda _x: None)("items")
        child_dt = getattr(items_field, "options", None)
        if child_dt:
            m = frappe.get_meta(child_dt)
            row_has_bh_fields = bool(
                m.has_field("bh_branch") and m.has_field("bh_tafsili_1") and m.has_field("bh_tafsili_2")
            )
    except Exception:
        row_has_bh_fields = False

    # ---- Per-row core dims ----
    try:
        items = doc.get("items") or []
    except Exception:
        items = getattr(doc, "items", None) or []
    items = items or []

    for i, row in enumerate(items, start=1):
        try:
            cc = (row.get("cost_center") or "").strip()
        except Exception:
            cc = (getattr(row, "cost_center", None) or "").strip()

        try:
            pr = (row.get("project") or "").strip()
        except Exception:
            pr = (getattr(row, "project", None) or "").strip()

        if not cc:
            missing.append(f"سطر {i}: مرکز هزینه")
        if not pr:
            missing.append(f"سطر {i}: پروژه")

        # Optional: auto-fill row bh_* from header for consistency
        if row_has_bh_fields:
            try:
                if hdr_branch and not ((row.get("bh_branch") or "").strip() if hasattr(row, "get") else (getattr(row, "bh_branch", "") or "").strip()):
                    row.bh_branch = hdr_branch
                if hdr_t1 and not ((row.get("bh_tafsili_1") or "").strip() if hasattr(row, "get") else (getattr(row, "bh_tafsili_1", "") or "").strip()):
                    row.bh_tafsili_1 = hdr_t1
                if hdr_t2 and not ((row.get("bh_tafsili_2") or "").strip() if hasattr(row, "get") else (getattr(row, "bh_tafsili_2", "") or "").strip()):
                    row.bh_tafsili_2 = hdr_t2
            except Exception:
                pass

    if missing:
        msg = "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- " + "\n- ".join(missing)
        raise_bh_vat_error(
            BH_VAT_E_GENERIC,
            msg,
            context={"company": company, "doctype": getattr(doc, "doctype", None), "name": getattr(doc, "name", None)},
        )

    setattr(doc, "_bh_dim_enforced", True)


def apply_gl_dimensions_from_invoice(doc, method=None, *args, **kwargs) -> None:
    """
    Best-effort: stamp voucher-level dimensions on GL Entries (does not split per-item).
    Hook-safe signature: (doc, method, *args, **kwargs)
    """
    try:
        company = _get_company(doc) or ""
        if not should_enforce_dimensions(company):
            return

        voucher_type = getattr(doc, "doctype", None) or ""
        voucher_no = getattr(doc, "name", None) or ""
        if not (voucher_type and voucher_no):
            return

        br = _get_str(doc, "bh_branch")
        t1 = _get_str(doc, "bh_tafsili_1")
        t2 = _get_str(doc, "bh_tafsili_2")

        if not (br or t1 or t2):
            return

        # company exists on GL Entry in ERPNext; keep it for safety
        frappe.db.sql(
            """
            UPDATE `tabGL Entry`
               SET bh_branch   = COALESCE(NULLIF(bh_branch,''), %(br)s),
                   bh_tafsili_1 = COALESCE(NULLIF(bh_tafsili_1,''), %(t1)s),
                   bh_tafsili_2 = COALESCE(NULLIF(bh_tafsili_2,''), %(t2)s)
             WHERE voucher_type = %(vt)s
               AND voucher_no   = %(vn)s
               AND company      = %(company)s
            """,
            {"br": br, "t1": t1, "t2": t2, "vt": voucher_type, "vn": voucher_no, "company": company},
        )
    except Exception:
        # never block submit
        return
