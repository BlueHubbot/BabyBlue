# -*- coding: utf-8 -*-
"""
BH Legal Output repository helpers.

Regress suites depend on these symbols (keep stable):
- find_last_output_for_ref
- get_previous_output
- get_latest_output_for_ref
"""

from __future__ import annotations

from typing import Optional, Dict, Any

import frappe


_DOCTYPE = "BH Legal Output"


def get_latest_output_for_ref(
    *,
    company: str,
    reference_doctype: str,
    reference_name: str,
    output_type: str,
    correction_reason: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    filters: Dict[str, Any] = {
        "company": company,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "output_type": output_type,
    }

    # IMPORTANT:
    # - correction_reason=None means "issue" outputs (NULL/empty), not "any"
    if correction_reason is None:
        filters["correction_reason"] = ["in", ["", None]]
    else:
        filters["correction_reason"] = correction_reason

    rows = frappe.get_all(
        _DOCTYPE,
        filters=filters,
        fields=[
            "name",
            "docstatus",
            "output_type",
            "schema_version",
            "generator_build",
            "previous_output",
            "correction_reason",
            "payload_hash",
            "source_hash",
            "creation",
        ],
        order_by="creation desc",
        limit=1,
    )
    return rows[0] if rows else None


def find_last_output_for_ref(
    company: str,
    reference_doctype: str | None = None,
    reference_name: str | None = None,
    output_type: str | None = None,
    correction_reason: str | None = None,
    *,
    # Backward-compat / callers sometimes use these:
    ref_doctype: str | None = None,
    ref_name: str | None = None,
):
    """
    Return last BH Legal Output.name for a given ref + output_type (+ optional correction_reason).

    Backward compatible:
      - accepts ref_doctype/ref_name as aliases for reference_doctype/reference_name
    """
    # alias support
    reference_doctype = reference_doctype or ref_doctype
    reference_name = reference_name or ref_name

    if not company or not reference_doctype or not reference_name or not output_type:
        return None

    row = get_latest_output_for_ref(
        company=company,
        reference_doctype=reference_doctype,
        reference_name=reference_name,
        output_type=output_type,
        correction_reason=correction_reason,
    )
    return row["name"] if row else None



def get_previous_output(output_name: str) -> Optional[str]:
    if not output_name:
        return None
    return frappe.db.get_value(_DOCTYPE, output_name, "previous_output")  # type: ignore


def get_output_doc(output_name: str):
    return frappe.get_doc(_DOCTYPE, output_name)
