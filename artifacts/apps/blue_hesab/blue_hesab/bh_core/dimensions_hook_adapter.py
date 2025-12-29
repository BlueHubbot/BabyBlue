from __future__ import annotations

# Adapter for Frappe hook signature: (doc, method=None)
# Calls the existing implementation regardless of whether it expects 1 or 2 args.

from typing import Any, Optional
import inspect

def apply_gl_dimensions_from_invoice(doc, method: Optional[str] = None) -> Any:
    from blue_hesab.bh_core import dimensions_policy  # local import (avoid import-time side effects)

    fn = getattr(dimensions_policy, "apply_gl_dimensions_from_invoice", None)
    if not fn:
        # If the implementation moved/renamed, do nothing (do not block submit)
        return None

    # Try best-effort calling with different signatures
    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        # If it accepts 2+ positional/kw, try (doc, method)
        if len(params) >= 2:
            try:
                return fn(doc, method=method)
            except TypeError:
                return fn(doc, method)
        # Otherwise only doc
        return fn(doc)
    except Exception:
        # Last resort
        try:
            return fn(doc)
        except TypeError:
            return fn(doc, method)
