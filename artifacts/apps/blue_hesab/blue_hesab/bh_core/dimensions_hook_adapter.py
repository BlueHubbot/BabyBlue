from __future__ import annotations

# آداپتر رسمی هوک‌ها:
# هر چیزی که در hooks.py صدا زده می‌شود باید از اینجا export شود.

from blue_hesab.bh_core.dimensions_policy import (
    enforce_invoice_dimensions,
    enforce_journal_entry_dimensions,
    enforce_payment_entry_dimensions,
)

# invoice-only (فعلاً JE/PE بهش وصل نمی‌کنیم)
try:
    from blue_hesab.bh_core.dimensions_policy import apply_gl_dimensions_from_invoice  # type: ignore
except Exception:
    apply_gl_dimensions_from_invoice = None  # pragma: no cover


__all__ = [
    "enforce_invoice_dimensions",
    "enforce_journal_entry_dimensions",
    "enforce_payment_entry_dimensions",
    "apply_gl_dimensions_from_invoice",
]
