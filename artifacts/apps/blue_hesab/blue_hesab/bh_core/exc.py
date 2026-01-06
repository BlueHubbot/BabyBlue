# apps/blue_hesab/blue_hesab/bh_core/exc.py
from __future__ import annotations

from typing import Any, Mapping, Optional

import frappe


def raise_bh_vat_error(*args, **kwargs):
    """
    Backwards-compatible VAT error raiser.

    Supported call styles:
      - raise_bh_vat_error("message")                         -> code defaults
      - raise_bh_vat_error("BH-VAT-E-XXX", "message")
      - raise_bh_vat_error(code="BH-VAT-E-XXX", message="..")
      - raise_bh_vat_error(message="..")                      -> code defaults
    """
    import frappe
    from frappe import _
    from frappe.exceptions import ValidationError

    # Optional kwargs
    context = kwargs.pop("context", None)
    log = kwargs.pop("log", True)
    exc = kwargs.pop("exc", None)
    title = kwargs.pop("title", None)

    code = kwargs.pop("code", None)
    message = kwargs.pop("message", None)

    # Parse positional args
    if message is None:
        if len(args) == 0:
            raise TypeError("raise_bh_vat_error() missing required argument: 'message'")
        elif len(args) == 1:
            message = args[0]
        else:
            # assume (code, message, ...)
            code = code or args[0]
            message = args[1]

    # Default code if not provided
    if not code:
        code = "BH-VAT-E-GENERIC"

    # Normalize message to string
    if message is None:
        message = ""
    if not isinstance(message, str):
        try:
            message = str(message)
        except Exception:
            message = _("BH VAT: خطای نامشخص")

    # Compose final message (keep existing format expectation)
    final = f"[{code}] {message}"

    # Attach context if present
    if context:
        try:
            import json
            final += "\n" + json.dumps(context, ensure_ascii=False, default=str)
        except Exception:
            final += "\n" + str(context)

    # Optional server log
    if log:
        try:
            frappe.log_error(title=title or code, message=final)
        except Exception:
            pass

    # Raise validation error (preferred in ERPNext)
    if exc:
        raise ValidationError(final) from exc
    raise ValidationError(final)

