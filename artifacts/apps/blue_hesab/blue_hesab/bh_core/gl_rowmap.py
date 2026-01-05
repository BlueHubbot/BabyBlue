from __future__ import annotations

from typing import Dict, Tuple, Any, List

import frappe
from blue_hesab.bh_core.company_legal import should_enforce_dimensions

_FIELDS = ("bh_branch", "bh_tafsili_1", "bh_tafsili_2")


def _s(x) -> str:
    return (x or "").strip()


def _f(x) -> float:
    try:
        return float(x or 0)
    except Exception:
        return 0.0


def _sig(account: str, debit: float, credit: float, cost_center: str) -> Tuple[str, float, float, str]:
    return (_s(account), round(_f(debit), 6), round(_f(credit), 6), _s(cost_center))


def prepare_gl_rowmap_for_journal_entry(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-04 JE support:
    Build in-memory mapping for this submit request:
      (voucher_type, voucher_no) -> { (account,debit,credit) : [ {row_name, bh_*...}, ... ] }

    Must run BEFORE GL Entry inserts (we hook it on Journal Entry.before_submit).
    """
    try:
        company = _s(getattr(doc, "company", None))
        if not should_enforce_dimensions(company):
            return

        vt = _s(getattr(doc, "doctype", None))
        vn = _s(getattr(doc, "name", None))
        if not (vt and vn):
            return

        rows = list(getattr(doc, "accounts", None) or [])
        if not rows:
            return

        hdr = {f: _s(getattr(doc, f, None)) for f in _FIELDS}

        mapping: Dict[Tuple[str, float, float], List[Dict[str, Any]]] = {}

        for r in rows:
            acc = _s(getattr(r, "account", None))
            dr = _f(getattr(r, "debit", None) or getattr(r, "debit_in_account_currency", None))
            cr = _f(getattr(r, "credit", None) or getattr(r, "credit_in_account_currency", None))
            if not acc or (abs(dr) < 1e-9 and abs(cr) < 1e-9):
                continue

            info = {"row_name": getattr(r, "name", None)}

            # prefer row dims, fallback to header dims
            for f in _FIELDS:
                rv = _s(getattr(r, f, None)) or hdr.get(f, "")
                if rv:
                    info[f] = rv

            cc = _s(getattr(r, "cost_center", None))
            key = _sig(acc, dr, cr, cc)

            mapping.setdefault(key, []).append(info)

        if not mapping:
            return

        if not hasattr(frappe.local, "_bh_gl_rowmap"):
            setattr(frappe.local, "_bh_gl_rowmap", {})

        frappe.local._bh_gl_rowmap[(vt, vn)] = mapping  # type: ignore[attr-defined]

    except Exception:
        # never block submit
        return
