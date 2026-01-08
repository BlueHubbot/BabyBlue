


# apps/blue_hesab/blue_hesab/bh_core/dim05_gl_gatekeeper.py
from __future__ import annotations

"""
DIM-05 gatekeeper for GL Entry.
This module exists because multiple suites (LEGAL08/09, DIM04, VAT CI)
expect a stable API:
    - enforce_gl_entry_dimensions(doc, method=None)

Implementation delegates to the existing GL stamping/guard logic
to keep behavior consistent.
"""

import frappe

from .company_legal import should_enforce_dimensions
from .exc import raise_bh_vat_error

REQ = ("bh_branch", "bh_tafsili_1")
from typing import Any

import frappe


def enforce_gl_entry_dimensions(doc: Any, method: str | None = None) -> None:
    """
    Hook-compatible function expected by regress suites.
    It should:
      1) Try to stamp GL dims from voucher context (when possible)
      2) Enforce required dimension presence (guard)

    Safe to call in validate/after_insert.
    """
    # Import locally to avoid circular import at boot.
    from . import gl_stamp

    # If doc is already inserted, we can attempt stamping using voucher context.
    # (stamp_gl_entry_from_voucher internally handles missing context safely.)
    try:
        if getattr(doc, "name", None):
            gl_stamp.stamp_gl_entry_from_voucher(doc, method=method)
    except Exception:
        # stamping is best-effort; enforcement will still run
        pass

    # Always enforce/guard
    gl_stamp.guard_gl_entry_dimensions(doc, method=method)


# Backward/compat alias (some places may reference guard name)
guard_gl_entry_dimensions = enforce_gl_entry_dimensions
# Backward-compat aliases (older hooks/tests might call these)
# Backward-compat: some hooks still call dim05_gl_gatekeeper.gatekeeper
gatekeeper = enforce_gl_entry_dimensions

def gatekeeper(gl_entry, method=None):
    # hooks.py expects dim05_gl_gatekeeper.gatekeeper
    return enforce_gl_entry_dimensions(gl_entry, method=method)
