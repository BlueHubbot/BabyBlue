"""
Compatibility proxy for VAT MIXED Purchase
All logic redirected to vat_mixed.bh_before_validate_purchase_invoice
"""

from .vat_mixed import bh_before_validate_purchase_invoice

__all__ = ["bh_before_validate_purchase_invoice"]
