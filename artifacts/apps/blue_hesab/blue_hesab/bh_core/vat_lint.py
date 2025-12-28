# apps/blue_hesab/blue_hesab/bh_core/vat_lint.py
# Lint checks to prevent regressions like "stubbed" VAT hooks or duplicate defs.

from __future__ import annotations

import inspect
import re
import frappe


from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
def _count_defs(source: str, fn_name: str) -> int:
    return len(re.findall(rf"^\s*def\s+{re.escape(fn_name)}\s*\(", source, flags=re.M))


def _non_comment_loc(source: str) -> int:
    n = 0
    for line in source.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        n += 1
    return n


def run_v12_lint() -> dict:
    errors: list[str] = []
    checks: dict = {}

    # ---- 1) ensure hooks are wired to vat_pipeline ----
    try:
        import blue_hesab.hooks as h  # type: ignore
        de = getattr(h, "doc_events", {}) or {}
        si = (de.get("Sales Invoice") or {})
        pi = (de.get("Purchase Invoice") or {})
        if (si.get("before_validate") or "") != "blue_hesab.bh_core.vat_pipeline.before_validate_sales_invoice":
            errors.append("hooks.py: Sales Invoice.before_validate must point to vat_pipeline.before_validate_sales_invoice")
        if (si.get("validate") or "") != "blue_hesab.bh_core.vat_pipeline.validate_sales_invoice":
            errors.append("hooks.py: Sales Invoice.validate must point to vat_pipeline.validate_sales_invoice")
        if (pi.get("before_validate") or "") != "blue_hesab.bh_core.vat_pipeline.before_validate_purchase_invoice":
            errors.append("hooks.py: Purchase Invoice.before_validate must point to vat_pipeline.before_validate_purchase_invoice")
        if (pi.get("validate") or "") != "blue_hesab.bh_core.vat_pipeline.validate_purchase_invoice":
            errors.append("hooks.py: Purchase Invoice.validate must point to vat_pipeline.validate_purchase_invoice")
        checks["hooks_doc_events_ok"] = (len(errors) == 0)
    except Exception as e:
        errors.append(f"hooks.py: cannot import/inspect doc_events: {e}")

    # ---- 2) vat_hooks must not be duplicated/stubbed ----
    try:
        import blue_hesab.bh_core.vat_hooks as vh  # type: ignore

        src = inspect.getsource(vh)
        for fn in ("apply_sales_invoice_vat", "apply_purchase_invoice_vat"):
            c = _count_defs(src, fn)
            checks[f"vat_hooks_def_count:{fn}"] = c
            if c != 1:
                errors.append(f"vat_hooks.py: {fn} must be defined exactly once (found {c})")

        # size checks (catch stubs)
        for fn in ("apply_sales_invoice_vat", "apply_purchase_invoice_vat"):
            f = getattr(vh, fn, None)
            if not callable(f):
                errors.append(f"vat_hooks.py: missing callable {fn}")
                continue
            s = inspect.getsource(f)
            loc = _non_comment_loc(s)
            checks[f"vat_hooks_loc:{fn}"] = loc
            if loc < 15:
                errors.append(f"vat_hooks.py: {fn} looks too small/stubbed (loc={loc})")

        # forbidden patterns
        forbidden = [
            "BH_PI_VAT_GUARD",
            "_BH_ORIG_APPLY_PI_VAT",
            "_BH_ORIG_APPLY_SI_VAT",
        ]
        for pat in forbidden:
            if pat in src:
                errors.append(f"vat_hooks.py: forbidden legacy marker present: {pat}")

    except Exception as e:
        errors.append(f"vat_hooks.py: cannot import/inspect: {e}")

    ok = not errors
    return {"ok": ok, "errors": errors, "checks": checks}
