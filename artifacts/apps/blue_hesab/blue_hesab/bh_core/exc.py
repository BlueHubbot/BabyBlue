# apps/blue_hesab/blue_hesab/bh_core/exc.py
from __future__ import annotations

from typing import Any, Mapping, Optional

import frappe


def raise_bh_vat_error(
    code: str,
    message: Any,
    *,
    context: Optional[Mapping[str, Any]] = None,
    log: bool = True,
    exc: Any = None,          # tolerate frappe.throw(exc=...)
    title: Any = None,        # tolerate frappe.throw(title=...)
    **_ignored: Any,          # tolerate other frappe.throw kwargs
):
    ctx = dict(context or {})
    full = f"[{code}] {str(message)}"

    if ctx and "context=" not in full:
        full = full + f"\ncontext={ctx!r}"

    if log:
        try:
            frappe.log_error(message=full, title=str(title or code))
        except Exception:
            pass

    ex = exc or frappe.ValidationError
    try:
        if isinstance(ex, type) and issubclass(ex, Exception):
            raise ex(full)
    except Exception:
        pass

    raise frappe.ValidationError(full)
