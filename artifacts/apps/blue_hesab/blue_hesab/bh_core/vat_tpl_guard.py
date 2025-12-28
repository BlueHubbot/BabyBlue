# apps/blue_hesab/blue_hesab/bh_core/vat_tpl_guard.py
from __future__ import annotations

from typing import Any, Optional, Dict

import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_TPL_NONSTR
from blue_hesab.bh_core.exc import raise_bh_vat_error
def normalize_item_tax_template(tpl: Any) -> Any:
    """
    Normalize Item Tax Template selector into a template name (str) or None.
    Returns original value if normalization is not possible (guard will catch).
    """
    if tpl is None:
        return None

    # common: template name
    if isinstance(tpl, str):
        v = tpl.strip()
        return v or None

    # common bug: dict leaking through
    if isinstance(tpl, dict):
        d: Dict[str, Any] = tpl
        for k in ("template", "name", "item_tax_template", "value"):
            v = d.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        # If dict carries known selector keys but none resolves to a template name,
        # treat as "no template" (prevents dict leak into ERPNext).
        if any(k in d for k in ("template", "name", "item_tax_template", "value")):
            return None
        return tpl  # unresolved (guard will raise)

    # sometimes a doc-like object with .name
    name = getattr(tpl, "name", None)
    if isinstance(name, str) and name.strip():
        return name.strip()

    return tpl

def guard_item_tax_template(tpl: Any, *, context: str, extra: Optional[dict] = None) -> Optional[str]:
    """
    Hard guard: after normalization, tpl must be str or None.
    Raises ValidationError with stable error code on violations.
    """
    extra = extra or {}
    normalized = normalize_item_tax_template(tpl)

    if normalized is None:
        return None

    if not isinstance(normalized, str):
        msg = (
            f"[{BH_VAT_E_TPL_NONSTR}] item_tax_template must be str|None\\n"
            f"context={context}\\n"
            f"type={type(normalized)}\\n"
            f"value={repr(normalized)}\\n"
            f"extra={repr(extra)}"
        )
        # log + raise (Production too)
        try:
            frappe.log_error(message=msg, title=BH_VAT_E_TPL_NONSTR)
        except Exception:
            pass
        raise_bh_vat_error(BH_VAT_E_TPL_NONSTR, msg)

    v = normalized.strip()
    if not v:
        return None
    return v
