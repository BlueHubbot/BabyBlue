# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional, Iterable, Any, Dict, Tuple

import frappe
import os

from blue_hesab.bh_core.company_legal import should_enforce_dimensions


def _fieldname_by_label(meta, label: str) -> str | None:
    label = (label or "").strip()
    for df in (meta.fields or []):
        if (df.label or "").strip() == label and df.fieldname:
            return df.fieldname
    return None


def _pick_first_record(doctype: str, company: str | None = None) -> str | None:
    # Prefer enabled records if doctype has `disabled`
    filters = {}
    try:
        if frappe.db.has_column(doctype, "disabled"):
            filters["disabled"] = 0
    except Exception:
        pass

    # Prefer company-scoped masters if the doctype has `company`
    if company:
        try:
            if frappe.db.has_column(doctype, "company"):
                filters["company"] = company
        except Exception:
            pass

    name = frappe.db.get_value(doctype, filters, "name")
    if name:
        return name
    return frappe.db.get_value(doctype, {}, "name")


def bh_autofill_min_invoice_dims(doc, labels=("شعبه", "تفصیلی ۱")):
    """
    Used by smoke/regress scripts so they don't fail on DIM enforcement.
    Does NOT weaken enforcement; just fills required header dims if possible.
    """
    meta = doc.meta
    company = getattr(doc, "company", None)

    for label in labels:
        fieldname = _fieldname_by_label(meta, label)
        if not fieldname:
            continue

        if doc.get(fieldname):
            continue

        df = meta.get_field(fieldname)
        if not df:
            continue

        if df.fieldtype == "Link" and df.options:
            val = _pick_first_record(df.options, company=company)
            if val:
                doc.set(fieldname, val)

    return doc


def _bh_dim_require_project() -> bool:
    # default: OFF to avoid breaking existing VAT regressions; can be enabled per-process
    try:
        if bool(getattr(frappe.local, "bh_dim_require_project", False)):
            return True
    except Exception:
        pass

    try:
        v = os.environ.get("BH_DIM_REQUIRE_PROJECT", "")
        if str(v).strip().lower() in ("1", "true", "yes", "on"):
            return True
    except Exception:
        pass

    try:
        v = getattr(frappe, "conf", {}).get("bh_dim_require_project", "")
        if str(v).strip().lower() in ("1", "true", "yes", "on"):
            return True
    except Exception:
        pass

    return False

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
    Enforce mandatory BH dimensions on Sales/Purchase Invoice before submit/save.
    - Prevents crashes due to unbound require_* flags.
    - Keeps Project optional by default (unless policy overrides it).
    - Best-effort fills item-level bh_* from header if item has those fields.
    """
    company = (getattr(doc, "company", None) or "").strip()
    if not company:
        return

    # if you have a company switch/flag, keep it
    try:
        if not should_enforce_dimensions(company):
            return
    except Exception:
        # if should_enforce_dimensions is not available or fails, do NOT crash submit
        return

    # --- Defensive defaults (no UnboundLocalError)
    require_cost_center = True
    require_branch = True
    require_tafsili_1 = True
    require_project = False

    # Optional: override from a policy dict if you already have one
    # (If you don't, this block harmlessly does nothing.)
    try:
        # any existing function name you might have; wrapped to avoid hard dependency
        policy = None
        try:
            policy = get_dimensions_policy(company=company, doctype=getattr(doc, "doctype", ""))  # type: ignore
        except Exception:
            policy = None

        if isinstance(policy, dict):
            require_cost_center = bool(policy.get("require_cost_center", require_cost_center))
            require_branch = bool(policy.get("require_branch", require_branch))
            require_tafsili_1 = bool(policy.get("require_tafsili_1", require_tafsili_1))
            require_project = bool(policy.get("require_project", require_project))
    except Exception:
        pass

    hdr_branch = (getattr(doc, "bh_branch", None) or "").strip()
    hdr_t1 = (getattr(doc, "bh_tafsili_1", None) or "").strip()
    hdr_project = (getattr(doc, "project", None) or "").strip()

    missing = []

    if require_branch and not hdr_branch:
        missing.append("سربرگ: شعبه")

    if require_tafsili_1 and not hdr_t1:
        missing.append("سربرگ: تفصیلی ۱")

    if require_project and not hdr_project:
        missing.append("سربرگ: پروژه")

    # Default company cost center (best-effort autofill)
    default_cc = ""
    if require_cost_center:
        try:
            default_cc = (frappe.db.get_value("Company", company, "cost_center") or "").strip()
        except Exception:
            default_cc = ""

    items = getattr(doc, "items", None) or []
    for i, it in enumerate(items, start=1):
        if require_cost_center:
            cc = (getattr(it, "cost_center", None) or "").strip()
            if not cc:
                if default_cc:
                    try:
                        it.cost_center = default_cc
                    except Exception:
                        pass
                else:
                    missing.append(f"ردیف {i}: مرکز هزینه")

        # Best-effort: stamp item dims from header if those fields exist on item
        try:
            meta = getattr(it, "meta", None)
            if meta and getattr(meta, "has_field", None):
                if meta.has_field("bh_branch") and not (getattr(it, "bh_branch", "") or "").strip():
                    it.bh_branch = hdr_branch
                if meta.has_field("bh_tafsili_1") and not (getattr(it, "bh_tafsili_1", "") or "").strip():
                    it.bh_tafsili_1 = hdr_t1
                if meta.has_field("project") and not (getattr(it, "project", "") or "").strip() and hdr_project:
                    it.project = hdr_project
        except Exception:
            pass

    if missing:
        msg = "BH DIM: برای ثبت سند، ابعاد مالی اجباری هستند. موارد ناقص:\n- " + "\n- ".join(missing)
        raise_bh_vat_error(
            msg,
            context={"company": company, "doctype": getattr(doc, "doctype", ""), "name": getattr(doc, "name", "")},
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

# === Aliases for backward compatibility / audit hooks ===

def enforce_sales_invoice_dimensions(doc, method=None):
    """Alias → redirect to enforce_invoice_dimensions"""
    return enforce_invoice_dimensions(doc, method=method)

def enforce_purchase_invoice_dimensions(doc, method=None):
    """Alias → redirect to enforce_invoice_dimensions"""
    return enforce_invoice_dimensions(doc, method=method)

def enforce_journal_entry_dimensions(doc, method=None):
    """Alias → redirect to enforce_invoice_dimensions"""
    return enforce_invoice_dimensions(doc, method=method)
