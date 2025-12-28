# apps/blue_hesab/blue_hesab/bh_core/vat_pipe_templates.py
from __future__ import annotations

from typing import Optional, Tuple

import frappe

from .vat_pipe_common import (
    AXIS_EXCL,
    AXIS_INCL,
    KIND_SALES,
    company_abbr,
    doctype_for_kind,
    label_for_kind,
    norm,
    axis_from_price_mode,
)


def infer_mixed_template_name(
    *,
    kind: str,
    company: str,
    axis: Optional[str] = None,
    mode: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Returns (template_name, template_doctype)
    Naming supports:
      - BH VAT MIXED Sales (EXCL) - BA
      - BH VAT MIXED Sales (EXCL)
      - (fallback older) BH VAT MIXED Sales - BA / BH VAT MIXED Sales
    """
    if not axis:
        axis = axis_from_price_mode(mode)

    axis = (norm(axis) or AXIS_EXCL).upper()
    if axis not in (AXIS_EXCL, AXIS_INCL):
        axis = AXIS_EXCL

    label = label_for_kind(kind)
    abbr = company_abbr(company)
    dt = doctype_for_kind(kind)

    candidates = []
    if abbr:
        candidates.append(f"BH VAT MIXED {label} ({axis}) - {abbr}")
    candidates.append(f"BH VAT MIXED {label} ({axis})")

    if abbr:
        candidates.append(f"BH VAT MIXED {label} - {abbr}")
    candidates.append(f"BH VAT MIXED {label}")

    for name in candidates:
        if frappe.db.exists(dt, name):
            return name, dt

    frappe.throw(
        "BH VAT: Mixed template not found.\n"
        f"kind={kind}, axis={axis}, company={company}\n"
        f"doctype={dt}\n"
        f"tried={', '.join(candidates)}"
    )
