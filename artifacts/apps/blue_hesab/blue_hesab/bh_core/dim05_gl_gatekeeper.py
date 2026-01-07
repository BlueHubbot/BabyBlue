from __future__ import annotations

import frappe

from .company_legal import should_enforce_dimensions
from .exc import raise_bh_vat_error

REQ = ("bh_branch", "bh_tafsili_1")


def guard_gl_entry_dimensions(doc, method=None, *args, **kwargs) -> None:
    """
    DIM-05 hard gate:
    Never allow a GL Entry to be inserted without required BH dimensions.
    Must run AFTER GL stamp.
    """
    company = (getattr(doc, "company", None) or "").strip()
    if not company:
        return

    try:
        if not should_enforce_dimensions(company):
            return
    except Exception:
        return

    missing = [f for f in REQ if not (getattr(doc, f, None) or "").strip()]
    if not missing:
        return

    vt = getattr(doc, "voucher_type", None)
    vn = getattr(doc, "voucher_no", None)
    acc = getattr(doc, "account", None)

    msg = (
        "BH DIM: اجازه ثبت سند حسابداری بدون ابعاد مالی وجود ندارد.\n"
        f"سند مرجع: {vt} / {vn}\n"
        f"حساب: {acc}\n"
        "ابعاد ناقص:\n- " + "\n- ".join(missing)
    )
    raise_bh_vat_error(
        msg,
        context={
            "company": company,
            "gl_entry": getattr(doc, "name", None),
            "voucher_type": vt,
            "voucher_no": vn,
            "account": acc,
        },
    )
