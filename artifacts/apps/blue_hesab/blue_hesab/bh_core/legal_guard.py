from __future__ import annotations

from contextlib import contextmanager
import frappe


_FLAG = "bh_legal_output_write_allowed_v1"


def is_legal_output_write_allowed() -> bool:
    return bool(getattr(frappe.flags, _FLAG, False))


@contextmanager
def allow_legal_output_write():
    prev = getattr(frappe.flags, _FLAG, False)
    setattr(frappe.flags, _FLAG, True)
    try:
        yield
    finally:
        setattr(frappe.flags, _FLAG, prev)
