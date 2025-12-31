# -*- coding: utf-8 -*-
"""
Repository helpers for BH Legal Output.

These helpers MUST be stable because regress scripts import them directly.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import frappe


def find_last_output_for_ref(
    reference_doctype: str,
    reference_name: str,
    output_type: Optional[str] = None,
    correction_reason: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    filters: Dict[str, Any] = {
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
    }
    if output_type:
        filters["output_type"] = output_type
    if correction_reason is not None:
        # allow None vs string filtering explicitly
        filters["correction_reason"] = correction_reason

    rows = frappe.get_all(
        "BH Legal Output",
        filters=filters,
        fields=[
            "name",
            "company",
            "output_type",
            "reference_doctype",
            "reference_name",
            "schema_version",
            "generator_build",
            "docstatus",
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


def get_previous_output(
    reference_doctype: str,
    reference_name: str,
    output_type: str,
    correction_reason: str,
) -> Optional[str]:
    """
    For AMEND: previous_output must point to the last CANCEL output of the *original* document.
    For CANCEL: previous_output is optional (we keep None for now, regress doesn't require).
    """
    if (correction_reason or "").upper() == "AMEND":
        last_cancel = find_last_output_for_ref(reference_doctype, reference_name, output_type=output_type, correction_reason="CANCEL")
        return last_cancel["name"] if last_cancel else None
    return None


def get_outputs_for_ref(reference_doctype: str, reference_name: str) -> List[Dict[str, Any]]:
    return frappe.get_all(
        "BH Legal Output",
        filters={"reference_doctype": reference_doctype, "reference_name": reference_name},
        fields=["name", "output_type", "docstatus", "correction_reason", "previous_output", "creation"],
        order_by="creation desc",
    )
