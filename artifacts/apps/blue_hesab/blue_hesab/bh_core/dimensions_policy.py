from __future__ import annotations

from typing import Optional, Iterable, Any, Dict, Tuple

import frappe

from blue_hesab.bh_core.company_legal import should_enforce_dimensions
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_company(doc) -> Optional[str]:
    try:
        v = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None) or ""
        v = (v or "").strip()
        return v or None
    except Exception:
        return None


def _get_str(doc, fieldname: str) -> str:
    try:
        v = getattr(doc, fieldname, None)
    except Exception:
        v = None
    if v is None and hasattr(doc, "get"):
        try:
            v = doc.get(fieldname)
        except Exception:
            v = None
    return (v or "").strip()


def _is_submit_path(doc, method: Optional[str]) -> bool:
    # Hook-safe: enforce ONLY on submit (never on draft/insert)
    if method in ("before_submit", "on_submit"):
        return True
    try:
        return getattr(doc, "_action", None) == "submit"
    except Exception:
        return False


def _iter_rows(doc, childfield: str) -> Iterable[Any]:
    try:
        v = getattr(doc, childfield, None)
    except Exception:
        v = None
    if v is None and hasattr(doc, "get"):
        try:
            v = doc.get(childfield)
        except Exception:
            v = None
    if not v:
        return []
    return v


def _row_get_str(row, fieldname: str) -> str:
    try:
        if hasattr(row, "get"):
            return (row.get(fieldname) or "").strip()
    except Exception:
        pass
    try:
        return (getattr(row, fieldname, "") or "").strip()
    except Exception:
        return ""


def _row_set(row, fieldname: str, value: str) -> None:
    try:
        if hasattr(row, "set"):
            row.set(fieldname, value)
            return
    except Exception:
        pass
    try:
        setattr(row, fieldname, value)
    except Exception:
        return


def _row_has_field(row, fieldname: str) -> bool:
    # We can't always access child meta; be defensive.
    try:
        if hasattr(row, "meta") and getattr(row, "meta", None) and row.meta.has_field(fieldname):  # type: ignore[attr-defined]
            return True
    except Exception:
        pass
    try:
        # fallback: attribute exists OR dict has key
        if hasattr(row, fieldname):
            return True
        if hasattr(row, "get") and row.get(fieldname, None) is not None:
            return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# DIM-01 (Invoices): enforce header + item dims on submit
# ---------------------------------------------------------------------------

def _bh_get_company_default_cost_center(company: str) -> str | None:
    # try common field names first
    cc = None
    for f in ("cost_center", "default_cost_center"):
        try:
            cc = frappe.db.get_value("Company", company, f)
        except Exception:
            cc = None
        if cc:
            return cc

    # fallback: first non-group cost center for company
    try:
        cc = frappe.db.get_value(
            "Cost Center",
            {"company": company, "is_group": 0, "disabled": 0},
            "name",
        )
    except Exception:
        cc = None
    return cc


def enforce_invoice_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    Minimal, production-safe enforcement for Sales/Purchase Invoice:
    - Header: bh_branch + bh_tafsili_1 are mandatory (block submit).
    - Items: cost_center is mandatory BUT we auto-fill from header/company if missing.
    - Project is NOT mandatory (for now).
    """
    company = (getattr(doc, "company", None) or "").strip() or None
    if not company:
        return

    if doc.doctype not in ("Sales Invoice", "Purchase Invoice"):
        return

    # اگر policy switch دارید، اینجا نگهش دار:
    try:
        if "should_enforce_dimensions" in globals() and not should_enforce_dimensions(company):
            return
    except Exception:
        pass

    missing = []

    hdr_branch = (getattr(doc, "bh_branch", None) or "").strip() or None
    hdr_t1 = (getattr(doc, "bh_tafsili_1", None) or "").strip() or None

    if not hdr_branch:
        missing.append("سربرگ: شعبه")
    if not hdr_t1:
        missing.append("سربرگ: تفصیلی ۱")

    # cost center autofill for items
    default_cc = (getattr(doc, "cost_center", None) or "").strip() or None
    if not default_cc:
        default_cc = _bh_get_company_default_cost_center(company)

    items = getattr(doc, "items", None) or []
    for i, it in enumerate(items, start=1):
        cc = (it.get("cost_center") or "").strip() if hasattr(it, "get") else (getattr(it, "cost_center", "") or "").strip()
        if not cc:
            if default_cc:
                try:
                    it.cost_center = default_cc
                except Exception:
                    try:
                        it["cost_center"] = default_cc
                    except Exception:
                        pass
            else:
                missing.append(f"ردیف {i}: مرکز هزینه")

        # best-effort: اگر روی آیتم فیلدهای ابعاد دارید، از سربرگ پرش کن
        try:
            if hasattr(it, "meta") and it.meta and it.meta.has_field("bh_branch") and not (it.get("bh_branch") or "").strip():
                it.bh_branch = hdr_branch
            if hasattr(it, "meta") and it.meta and it.meta.has_field("bh_tafsili_1") and not (it.get("bh_tafsili_1") or "").strip():
                it.bh_tafsili_1 = hdr_t1
        except Exception:
            pass

    if missing:
        msg = "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- " + "\n- ".join(missing)
        raise_bh_vat_error(
            msg,
            context={"company": company, "doctype": doc.doctype, "name": doc.name},
        )


# ---------------------------------------------------------------------------
# DIM-04 (Voucher-level GL stamp): keep invoice function for backward compat
# ---------------------------------------------------------------------------

def apply_gl_dimensions_from_voucher(doc, method=None, *args, **kwargs) -> None:
    """
    Best-effort: stamp voucher-level dimensions on GL Entries (does not split per-line).
    - Only fills GL Entry bh_* fields if currently empty.
    - Safe to call for any voucher_type, but requires voucher doctype to have fields.
    """
    try:
        company = _get_company(doc) or ""
        if not should_enforce_dimensions(company):
            return

        voucher_type = (getattr(doc, "doctype", None) or "").strip()
        voucher_no = (getattr(doc, "name", None) or "").strip()
        if not (voucher_type and voucher_no):
            return

        br = _get_str(doc, "bh_branch")
        t1 = _get_str(doc, "bh_tafsili_1")
        t2 = _get_str(doc, "bh_tafsili_2")

        if not (br or t1 or t2):
            return

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


def apply_gl_dimensions_from_invoice(doc, method=None, *args, **kwargs) -> None:
    """
    Stamp BH dimensions onto GL Entry rows for SI/PI after submit.
    - Header dims apply to all GL rows (at least).
    - If voucher_detail_no matches item row name, we can stamp row-wise too (optional best-effort).
    """

    company = _get_company(doc)
    if not company or not should_enforce_dimensions(company):
        return

    vt = getattr(doc, "doctype", None) or ""
    vn = getattr(doc, "name", None) or ""
    if vt not in ("Sales Invoice", "Purchase Invoice") or not vn:
        return

    hdr_branch = (getattr(doc, "bh_branch", None) or "").strip() or None
    hdr_t1 = (getattr(doc, "bh_tafsili_1", None) or "").strip() or None
    hdr_t2 = (getattr(doc, "bh_tafsili_2", None) or "").strip() or None

    # If nothing to stamp, skip (but normally enforce_invoice_dimensions prevents this)
    if not (hdr_branch or hdr_t1 or hdr_t2):
        return

    # 1) Best-effort row-wise stamp (if GL.voucher_detail_no == item_row.name)
    try:
        item_dt = "Sales Invoice Item" if vt == "Sales Invoice" else "Purchase Invoice Item"
        item_rows = frappe.get_all(
            item_dt,
            filters={"parent": vn, "parenttype": vt},
            fields=["name", "bh_branch", "bh_tafsili_1", "bh_tafsili_2"],
            limit_page_length=5000,
        ) or []

        for r in item_rows:
            vdn = (r.get("name") or "").strip()
            if not vdn:
                continue

            br = (r.get("bh_branch") or "").strip() or hdr_branch
            t1 = (r.get("bh_tafsili_1") or "").strip() or hdr_t1
            t2 = (r.get("bh_tafsili_2") or "").strip() or hdr_t2

            if not (br or t1 or t2):
                continue

            sets, params = [], []
            if br:
                sets.append("bh_branch=%s")
                params.append(br)
            if t1:
                sets.append("bh_tafsili_1=%s")
                params.append(t1)
            if t2:
                sets.append("bh_tafsili_2=%s")
                params.append(t2)

            frappe.db.sql(
                f"""
                UPDATE `tabGL Entry`
                   SET {", ".join(sets)}
                 WHERE company=%s
                   AND voucher_type=%s
                   AND voucher_no=%s
                   AND voucher_detail_no=%s
                """,
                params + [company, vt, vn, vdn],
            )
    except Exception:
        # row-wise is best-effort only
        pass

    # 2) Header fallback for anything still missing (do NOT overwrite existing)
    sets, params = [], []
    if hdr_branch:
        sets.append("bh_branch = CASE WHEN IFNULL(bh_branch,'')='' THEN %s ELSE bh_branch END")
        params.append(hdr_branch)
    if hdr_t1:
        sets.append("bh_tafsili_1 = CASE WHEN IFNULL(bh_tafsili_1,'')='' THEN %s ELSE bh_tafsili_1 END")
        params.append(hdr_t1)
    if hdr_t2:
        sets.append("bh_tafsili_2 = CASE WHEN IFNULL(bh_tafsili_2,'')='' THEN %s ELSE bh_tafsili_2 END")
        params.append(hdr_t2)

    frappe.db.sql(
        f"""
        UPDATE `tabGL Entry`
           SET {", ".join(sets)}
         WHERE company=%s
           AND voucher_type=%s
           AND voucher_no=%s
        """,
        params + [company, vt, vn],
    )


# ---------------------------------------------------------------------------
# DIM-02.A (JE/PE): enforce minimal Cost Center on submit
# ---------------------------------------------------------------------------

def enforce_journal_entry_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-02.B Journal Entry:
    - Only enforce on submit path.
    - Mandatory on each accounts row WITH amount:
        - cost_center
        - bh_branch
        - bh_tafsili_1
      (bh_tafsili_2 optional)
    - Propagation (no overwrite):
        - If header has bh_* and row is empty -> fill row from header
    """
    if not _is_submit_path(doc, method):
        return

    company = _get_company(doc)
    force = bool(kwargs.get("force"))
    if not force and not should_enforce_dimensions(company):
        return

    hdr_branch = _get_str(doc, "bh_branch")
    hdr_t1 = _get_str(doc, "bh_tafsili_1")
    hdr_t2 = _get_str(doc, "bh_tafsili_2")

    rows = list(_iter_rows(doc, "accounts"))
    if not rows:
        return

    missing: list[str] = []

    for i, r in enumerate(rows, start=1):
        # amount check
        try:
            debit = float((r.get("debit_in_account_currency") or r.get("debit") or 0) if hasattr(r, "get") else (getattr(r, "debit_in_account_currency", 0) or getattr(r, "debit", 0) or 0))
        except Exception:
            debit = 0.0
        try:
            credit = float((r.get("credit_in_account_currency") or r.get("credit") or 0) if hasattr(r, "get") else (getattr(r, "credit_in_account_currency", 0) or getattr(r, "credit", 0) or 0))
        except Exception:
            credit = 0.0

        if abs(debit) < 1e-9 and abs(credit) < 1e-9:
            continue

        acc = _row_get_str(r, "account") if _row_has_field(r, "account") else ""

        # cost_center mandatory
        if _row_has_field(r, "cost_center"):
            if not _row_get_str(r, "cost_center"):
                missing.append(f"ردیف {i}: مرکز هزینه (حساب: {acc or '—'})")

        # propagate header -> row (no overwrite)
        if _row_has_field(r, "bh_branch") and hdr_branch and not _row_get_str(r, "bh_branch"):
            _row_set(r, "bh_branch", hdr_branch)
        if _row_has_field(r, "bh_tafsili_1") and hdr_t1 and not _row_get_str(r, "bh_tafsili_1"):
            _row_set(r, "bh_tafsili_1", hdr_t1)
        if _row_has_field(r, "bh_tafsili_2") and hdr_t2 and not _row_get_str(r, "bh_tafsili_2"):
            _row_set(r, "bh_tafsili_2", hdr_t2)

        # enforce row bh_* (mandatory: branch + tafsili_1)
        if _row_has_field(r, "bh_branch") and not _row_get_str(r, "bh_branch"):
            missing.append(f"ردیف {i}: شعبه (حساب: {acc or '—'})")
        if _row_has_field(r, "bh_tafsili_1") and not _row_get_str(r, "bh_tafsili_1"):
            missing.append(f"ردیف {i}: تفصیلی ۱ (حساب: {acc or '—'})")

    if missing:
        msg = (
            "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- "
            + "\n- ".join(missing)
        )
        raise_bh_vat_error(
            BH_VAT_E_GENERIC,
            msg,
            context={"company": company, "doctype": getattr(doc, "doctype", None), "name": getattr(doc, "name", None)},
        )



def enforce_payment_entry_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-02.B Payment Entry:
    - Only enforce on submit path.
    - Mandatory (header):
        - cost_center (if field exists)
        - bh_branch
        - bh_tafsili_1
      (bh_tafsili_2 optional)
    - Deductions: if amount != 0 and row has bh_* -> fill from header (no overwrite), then enforce branch+tafsili_1.
    """
    if not _is_submit_path(doc, method):
        return

    company = _get_company(doc)
    force = bool(kwargs.get("force"))
    if not force and not should_enforce_dimensions(company):
        return

    hdr_cc = _get_str(doc, "cost_center")
    hdr_branch = _get_str(doc, "bh_branch")
    hdr_t1 = _get_str(doc, "bh_tafsili_1")
    hdr_t2 = _get_str(doc, "bh_tafsili_2")

    missing: list[str] = []

    # header cost_center
    try:
        has_cc_hdr = bool(getattr(getattr(doc, "meta", None), "has_field", lambda _x: False)("cost_center"))
    except Exception:
        has_cc_hdr = True
    if has_cc_hdr and not hdr_cc:
        missing.append("سربرگ: مرکز هزینه")

    # header branch/tafsili
    if not hdr_branch:
        missing.append("سربرگ: شعبه")
    if not hdr_t1:
        missing.append("سربرگ: تفصیلی ۱")

    # deductions (best-effort)
    for i, r in enumerate(_iter_rows(doc, "deductions"), start=1):
        # amount check
        amt = 0.0
        try:
            if hasattr(r, "get"):
                amt = float(r.get("amount") or 0)
            else:
                amt = float(getattr(r, "amount", 0) or 0)
        except Exception:
            amt = 0.0
        if abs(amt) < 1e-9:
            continue

        # propagate header -> row (no overwrite)
        if _row_has_field(r, "bh_branch") and hdr_branch and not _row_get_str(r, "bh_branch"):
            _row_set(r, "bh_branch", hdr_branch)
        if _row_has_field(r, "bh_tafsili_1") and hdr_t1 and not _row_get_str(r, "bh_tafsili_1"):
            _row_set(r, "bh_tafsili_1", hdr_t1)
        if _row_has_field(r, "bh_tafsili_2") and hdr_t2 and not _row_get_str(r, "bh_tafsili_2"):
            _row_set(r, "bh_tafsili_2", hdr_t2)

        # enforce if fields exist
        if _row_has_field(r, "bh_branch") and not _row_get_str(r, "bh_branch"):
            missing.append(f"کسورات ردیف {i}: شعبه")
        if _row_has_field(r, "bh_tafsili_1") and not _row_get_str(r, "bh_tafsili_1"):
            missing.append(f"کسورات ردیف {i}: تفصیلی ۱")

    if missing:
        msg = "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- " + "\n- ".join(missing)
        raise_bh_vat_error(
            BH_VAT_E_GENERIC,
            msg,
            context={"company": company, "doctype": getattr(doc, "doctype", None), "name": getattr(doc, "name", None)},
        )
