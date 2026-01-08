from __future__ import annotations

from typing import Dict, Tuple, List, Any, Optional

import frappe
from blue_hesab.bh_core.company_legal import should_enforce_dimensions

_FIELDS = ("bh_branch", "bh_tafsili_1", "bh_tafsili_2")

def _field_exists(doc, fieldname: str) -> bool:
    """بررسی ایمن وجود فیلد روی Document/Meta بدون crash."""
    try:
        meta = getattr(doc, "meta", None)
        if meta:
            if hasattr(meta, "has_field") and meta.has_field(fieldname):
                return True
            if hasattr(meta, "get_field") and meta.get_field(fieldname):
                return True
    except Exception:
        pass

    try:
        if hasattr(doc, fieldname):
            return True
        if isinstance(doc, dict) and fieldname in doc:
            return True
    except Exception:
        pass

    return False


def _get_doc_value(doc, fieldname: str, default=None):
    """Safe getter for both dict-like and attribute-style docs."""
    try:
        if hasattr(doc, "get"):
            v = doc.get(fieldname)
            if v is not None:
                return v
        return getattr(doc, fieldname, default)
    except Exception:
        return default

def _s(x) -> str:
    return (x or "").strip()


def _f(x) -> float:
    try:
        return float(x or 0)
    except Exception:
        return 0.0


def _sig(account: str, debit: float, credit: float, cost_center: str) -> Tuple[str, float, float, str]:
    return (_s(account), round(_f(debit), 6), round(_f(credit), 6), _s(cost_center))


def _get_cache() -> Dict:
    try:
        cache = getattr(frappe.local, "_bh_gl_stamp_cache", None)
        if cache is None:
            cache = {}
            setattr(frappe.local, "_bh_gl_stamp_cache", cache)
        return cache
    except Exception:
        return {}


def _cache_get(key, default=None):
    c = _get_cache()
    return c.get(key, default)


def _cache_set(key, value):
    c = _get_cache()
    c[key] = value
    return value


def _get_voucher_child_tables(voucher_type: str) -> List[str]:
    ck = ("child_tables", voucher_type)
    hit = _cache_get(ck)
    if hit is not None:
        return hit

    out: List[str] = []
    try:
        meta = frappe.get_meta(voucher_type)
        table_dts: List[str] = []
        for df in meta.fields or []:
            if getattr(df, "fieldtype", None) == "Table" and getattr(df, "options", None):
                table_dts.append(df.options)

        for cdt in table_dts:
            try:
                cmeta = frappe.get_meta(cdt)
                if any(cmeta.has_field(f) for f in _FIELDS):
                    out.append(cdt)
            except Exception:
                continue
    except Exception:
        out = []

    return _cache_set(ck, out)


def _get_voucher_header_dims(voucher_type: str, voucher_no: str) -> Dict[str, str]:
    ck = ("hdr_dims", voucher_type, voucher_no)
    hit = _cache_get(ck)
    if hit is not None:
        return hit

    dims: Dict[str, str] = {}
    try:
        meta = frappe.get_meta(voucher_type)
        fields = [f for f in _FIELDS if meta.has_field(f)]
        if not fields:
            return _cache_set(ck, {})

        vals = frappe.db.get_value(voucher_type, voucher_no, fields, as_dict=True) or {}
        for f in fields:
            v = _s(vals.get(f))
            if v:
                dims[f] = v
    except Exception:
        dims = {}

    return _cache_set(ck, dims)


def _get_voucher_row_dims(voucher_type: str, voucher_no: str, voucher_detail_no: str) -> Dict[str, str]:
    ck = ("row_dims", voucher_type, voucher_no, voucher_detail_no)
    hit = _cache_get(ck)
    if hit is not None:
        return hit

    dims: Dict[str, str] = {}
    child_tables = _get_voucher_child_tables(voucher_type)
    if not child_tables:
        return _cache_set(ck, {})

    for cdt in child_tables:
        try:
            cmeta = frappe.get_meta(cdt)
            fields = [f for f in _FIELDS if cmeta.has_field(f)]
            if not fields:
                continue

            vals = frappe.db.get_value(
                cdt,
                voucher_detail_no,
                ["parent", "parenttype"] + fields,
                as_dict=True,
            )
            if not vals:
                continue
            if _s(vals.get("parent")) != voucher_no:
                continue
            if _s(vals.get("parenttype")) != voucher_type:
                continue

            for f in fields:
                v = _s(vals.get(f))
                if v:
                    dims[f] = v

            if dims:
                break
        except Exception:
            continue

    return _cache_set(ck, dims)


def _pop_local_rowmap(vt: str, vn: str, account: str, debit: float, credit: float, cost_center: str) -> Optional[Dict[str, Any]]:
    """
    Local rowmap (same request) created by vouchers (e.g., Journal Entry.before_submit).
    Structure:
      frappe.local._bh_gl_rowmap[(vt,vn)] = { (acc,dr,cr): [info1, info2, ...] }
    """
    try:
        rm = getattr(frappe.local, "_bh_gl_rowmap", None)
        if not rm:
            return None
        bucket = rm.get((vt, vn))
        if not bucket:
            return None
        key = _sig(account, debit, credit, cost_center)
        lst = bucket.get(key)
        if not lst:
            return None
        info = lst.pop(0)
        return info or None
    except Exception:
        return None


def stamp_gl_entry_from_voucher(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-04 Generalizer:
    Priority:
      1) voucher_detail_no -> pull dims from voucher child row (DB)
      2) local rowmap (same submit request) -> sets voucher_detail_no + dims (JE fix)
      3) voucher header dims (DB)
    Never overwrites existing bh_* on GL Entry.
    """
    try:
        company = _s(getattr(doc, "company", None))
        if not should_enforce_dimensions(company):
            return

        vt = _s(getattr(doc, "voucher_type", None))
        vn = _s(getattr(doc, "voucher_no", None))
        if not (vt and vn):
            return

        # decide if anything is needed
        need_vdn = not _s(getattr(doc, "voucher_detail_no", None))
        need_any_dim = any(not _s(getattr(doc, f, None)) for f in _FIELDS)
        if not (need_vdn or need_any_dim):
            return

        dims: Dict[str, str] = {}

        # 1) voucher_detail_no path
        vdn = _s(getattr(doc, "voucher_detail_no", None))
        if vdn:
            dims = _get_voucher_row_dims(vt, vn, vdn)

        # 2) local rowmap path (JE etc.)
        if not dims or need_vdn:
            info = _pop_local_rowmap(
                vt, vn,
                _s(getattr(doc, "account", None)),
                _f(getattr(doc, "debit", None)),
                _f(getattr(doc, "credit", None)),
                _s(getattr(doc, "cost_center", None)),
            )
            if info:
                if need_vdn and info.get("row_name"):
                    try:
                        setattr(doc, "voucher_detail_no", info["row_name"])
                        vdn = _s(info["row_name"])
                    except Exception:
                        pass
                for f in _FIELDS:
                    v = _s(info.get(f))
                    if v:
                        dims.setdefault(f, v)

        # 3) header dims fallback
        if any(not _s(getattr(doc, f, None)) for f in _FIELDS):
            hd = _get_voucher_header_dims(vt, vn)
            for f, v in (hd or {}).items():
                if _s(v):
                    dims.setdefault(f, _s(v))

        if not dims:
            return

        # apply (no overwrite)
        for f, v in dims.items():
            if v and not _s(getattr(doc, f, None)):
                setattr(doc, f, v)

    except Exception:
        return

def guard_gl_entry_dimensions(doc, method=None):
    """
    GL Entry hook (typically before_insert) to:
      1) Stamp BH dimensions onto GL Entry from voucher / voucher_detail_no
      2) Enforce required BH dimension fields (branch + tafsili_1)

    This is intentionally strict: every GL-posting document must carry dimensions.
    """
    # safety: only for GL Entry
    if getattr(doc, "doctype", None) and doc.doctype != "GL Entry":
        return

    company = _get_doc_value(doc, "company")

    # Feature flag (per-company)
    try:
        if not should_enforce_dimensions(company):
            return
    except Exception:
        # if settings lookup fails, do not crash accounting
        return

    # 1) Stamp from voucher (best-effort)
    try:
        stamp_gl_entry_from_voucher(doc, method=method)
    except Exception:
        # log but don't break on stamping itself; validation below will fail if still missing
        try:
            frappe.log_error(frappe.get_traceback(), "BH GL Stamp failed (gl_stamp.guard_gl_entry_dimensions)")
        except Exception:
            pass

    # 2) Validate required dimension fields
    required = ("bh_branch", "bh_tafsili_1")
    missing = []
    for f in required:
        if not _field_exists(doc, f):
            # if the field is not present on GL Entry meta, we cannot enforce it here
            continue
        v = getattr(doc, f, None)
        if v is None or (isinstance(v, str) and not v.strip()):
            missing.append(f)

    if missing:
        fa = {
            "bh_branch": "شعبه",
            "bh_tafsili_1": "تفصیلی ۱",
        }
        missing_fa = "، ".join(fa.get(x, x) for x in missing)
        vtype = getattr(doc, "voucher_type", None) or "؟"
        vno = getattr(doc, "voucher_no", None) or "؟"
        frappe.throw(
            f"تفکیک مالی ناقص است: {missing_fa}\n"
            f"سند مرجع: {vtype} / {vno}\n"
            "قبل از ثبت/ثبت نهایی، «شعبه» و «تفصیلی» را روی سند مرجع (یا سطر مربوط) تکمیل کنید.",
            title="تفکیک مالی الزامی است",
        )
