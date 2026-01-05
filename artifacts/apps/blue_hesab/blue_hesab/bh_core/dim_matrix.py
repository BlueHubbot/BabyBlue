from __future__ import annotations

"""
DIM-01 (Design/Matrix) — v0.1

این فایل فقط «طراحی» است (runtime impact ندارد).
هدف: یک منبع حقیقت برای لیست GL-Docs و قواعد Dimensionها.

قاعده:
- Company مرز قانونی است.
- هر سند GL-posting باید حداقل Branch/Cost Center/Project و ابعاد سفارشی را پشتیبانی/اجباری کند.
- enforce واقعی در DIM-02..DIM-04 می‌آید.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class DimRule:
    doctype: str
    header_required: Tuple[str, ...] = ()
    row_required: Tuple[str, ...] = ()
    header_optional: Tuple[str, ...] = ()
    row_optional: Tuple[str, ...] = ()
    enforce_at: Tuple[str, ...] = ("before_submit",)
    child_doctype: Optional[str] = None
    child_fieldname: Optional[str] = None


# v0.1 skeleton — جلسه بعد کاملش می‌کنیم (لیست قطعی GL docs + سطح الزام header/row)
DIM_MATRIX_V01 = {
    # P0.5 موجود
    "Sales Invoice": DimRule(
        doctype="Sales Invoice",
        header_required=("company",),
        header_optional=("branch", "cost_center", "project"),
        enforce_at=("before_submit",),
    ),
    "Purchase Invoice": DimRule(
        doctype="Purchase Invoice",
        header_required=("company",),
        header_optional=("branch", "cost_center", "project"),
        enforce_at=("before_submit",),
    ),

    # DIM-02 (Accounting docs) — شروع enforce واقعی
    "Journal Entry": DimRule(
        doctype="Journal Entry",
        header_required=("company",),
        row_required=("cost_center",),
        header_optional=("branch", "project"),
        child_doctype="Journal Entry Account",
        child_fieldname="accounts",
        enforce_at=("before_submit",),
    ),
    "Payment Entry": DimRule(
        doctype="Payment Entry",
        header_required=("company",),
        header_optional=("branch", "cost_center", "project"),
        enforce_at=("before_submit",),
    ),
}


def get_dim_rule(doctype: str) -> Optional[DimRule]:
    return DIM_MATRIX_V01.get((doctype or "").strip())
