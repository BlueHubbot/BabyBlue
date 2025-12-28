from __future__ import annotations

import frappe


def get_bh_settings(fields: list[str] | None = None):
    """Return BH Settings as Doc (default) or dict of selected fields."""
    s = frappe.get_single("BH Settings")
    if not fields:
        return s
    out = {}
    for f in fields:
        out[f] = s.get(f)
    return out


def is_iran_mode_enabled() -> bool:
    try:
        s = frappe.get_single("BH Settings")
        return bool(int(s.get("enable_iran_mode") or 0))
    except Exception:
        return False
