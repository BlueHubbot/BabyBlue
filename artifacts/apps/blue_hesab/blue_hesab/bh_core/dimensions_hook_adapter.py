from __future__ import annotations

# این فایل آداپتر رسمی هوک‌هاست؛
# هر چیزی که در hooks.py صدا زده می‌شود باید اینجا import/export شود.

from blue_hesab.bh_core.dimensions_policy import enforce_invoice_dimensions  # <-- مهم

# اگر قبلاً این فایل فقط apply_gl_dimensions_from_invoice داشت و نمی‌خوای از دست بره،
# همینجا نگهش دار (اگر وجود داشت).
try:
    from blue_hesab.bh_core.dimensions_policy import apply_gl_dimensions_from_invoice  # type: ignore
except Exception:
    apply_gl_dimensions_from_invoice = None  # pragma: no cover


__all__ = [
    "enforce_invoice_dimensions",
    "apply_gl_dimensions_from_invoice",
]
