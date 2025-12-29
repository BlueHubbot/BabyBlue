# apps/blue_hesab/blue_hesab/bh_core/legal_policy.py
# -*- coding: utf-8 -*-
"""
LEGAL-06 — Correction outputs policy + enforced chain rules

این فایل فقط Policy/Query است (بدون ساخت Doc).

قواعد فعلی برای output_type=VAT_INVOICE:
- ISSUE: correction_reason=None (روی submit سند اصلی)
- CANCEL: correction_reason="CANCEL" (روی before_cancel سند اصلی) و previous_output باید آخرین خروجی غیرکنسلی باشد.
- AMEND: correction_reason="AMEND" (روی submit سند اصلاحیه) و previous_output باید CANCEL سند amended_from باشد.

Idempotency:
- اگر خروجی هم‌نوع قبلاً وجود داشته و source_hash/payload_hash برابر باشد → همان output reuse می‌شود.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import frappe


CORR_CANCEL = "CANCEL"
CORR_AMEND = "AMEND"


def _norm_reason(reason: Optional[str]) -> Optional[str]:
    if not reason:
        return None
    r = str(reason).strip().upper()
    return r or None


def _ref_meta(reference_doctype: str, reference_name: str) -> Dict[str, Any]:
    """docstatus + amended_from را بدون get_doc سنگین می‌گیریم."""
    row = frappe.db.get_value(
        reference_doctype,
        reference_name,
        ["docstatus", "amended_from"],
        as_dict=True,
    )
    if not row:
        frappe.throw(
            f"سند مرجع پیدا نشد: {reference_doctype} / {reference_name}",
            frappe.DoesNotExistError,
        )
    return {"docstatus": int(row.get("docstatus") or 0), "amended_from": row.get("amended_from")}


def get_outputs_for_ref(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    fields: Optional[List[str]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    fields = fields or [
        "name",
        "company",
        "output_type",
        "correction_reason",
        "previous_output",
        "schema_version",
        "generator_build",
        "generated_at",
        "payload_hash",
        "source_hash",
        "modified",
    ]
    return frappe.get_all(
        "BH Legal Output",
        filters={
            "company": company,
            "output_type": output_type,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
        },
        fields=fields,
        order_by="modified desc",
        limit_page_length=limit,
    )


def get_latest_legal_output(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    only_reason: Optional[str] = None,
    fields: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    filters: Dict[str, Any] = {
        "company": company,
        "output_type": output_type,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
    }
    if only_reason is not None:
        filters["correction_reason"] = only_reason

    rows = frappe.get_all(
        "BH Legal Output",
        filters=filters,
        fields=fields
        or [
            "name",
            "correction_reason",
            "previous_output",
            "payload_hash",
            "source_hash",
            "modified",
        ],
        order_by="modified desc",
        limit_page_length=1,
    )
    return rows[0] if rows else None


def get_latest_non_cancel_output(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
) -> Optional[Dict[str, Any]]:
    """
    آخرین خروجی غیر-CANCEL.
    این را در Python فیلتر می‌کنیم تا مشکل NULL در query != نخوریم.
    """
    rows = get_outputs_for_ref(
        company=company,
        output_type=output_type,
        reference_doctype=reference_doctype,
        reference_name=reference_name,
        fields=["name", "correction_reason", "previous_output", "payload_hash", "source_hash", "modified"],
        limit=20,
    )
    for r in rows:
        if _norm_reason(r.get("correction_reason")) != CORR_CANCEL:
            return r
    return None


def get_latest_legal_output_name(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    only_reason: Optional[str] = None,
) -> Optional[str]:
    row = get_latest_legal_output(
        company=company,
        output_type=output_type,
        reference_doctype=reference_doctype,
        reference_name=reference_name,
        only_reason=only_reason,
        fields=["name"],
    )
    return row["name"] if row else None


def _reuse_if_same_hash(
    latest: Optional[Dict[str, Any]],
    *,
    source_hash: str,
    payload_hash: str,
) -> Optional[str]:
    if not latest:
        return None
    if (latest.get("source_hash") == source_hash) and (latest.get("payload_hash") == payload_hash):
        return str(latest.get("name"))
    return None


def enforce_legal_output_chain(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    correction_reason: Optional[str],
    previous_output: Optional[str],
    source_hash: str,
    payload_hash: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    خروجی:
      (normalized_reason, normalized_previous_output, reuse_name)
    """
    reason = _norm_reason(correction_reason)
    meta = _ref_meta(reference_doctype, reference_name)
    docstatus = meta["docstatus"]
    amended_from = meta["amended_from"]

    # ISSUE
    if reason is None:
        if amended_from:
            frappe.throw("این سند اصلاحیه است؛ خروجی آن باید AMEND باشد (نه ISSUE).", frappe.ValidationError)
        if docstatus != 1:
            frappe.throw("خروجی ISSUE فقط برای سند Submitted مجاز است.", frappe.ValidationError)

        latest_any = get_latest_legal_output(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
        )
        reuse = _reuse_if_same_hash(latest_any, source_hash=source_hash, payload_hash=payload_hash)
        if reuse:
            return None, None, reuse

        if latest_any:
            frappe.throw(
                "برای این سند قبلاً خروجی قانونی صادر شده است. برای تغییر باید مسیر اصلاحیه (AMEND) طی شود.",
                frappe.ValidationError,
            )
        return None, None, None

    # CANCEL
    if reason == CORR_CANCEL:
        latest_non_cancel = get_latest_non_cancel_output(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
        )
        if not latest_non_cancel:
            frappe.throw("کنسلی بدون «صدور خروجی اولیه» مجاز نیست.", frappe.ValidationError)

        expected_prev = str(latest_non_cancel["name"])
        if previous_output and previous_output != expected_prev:
            frappe.throw("previous_output کنسلی باید دقیقاً آخرین خروجی غیرکنسلی همین سند باشد.", frappe.ValidationError)

        latest_cancel = get_latest_legal_output(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
            only_reason=CORR_CANCEL,
        )
        reuse = _reuse_if_same_hash(latest_cancel, source_hash=source_hash, payload_hash=payload_hash)
        if reuse:
            return CORR_CANCEL, expected_prev, reuse

        if latest_cancel:
            return CORR_CANCEL, expected_prev, str(latest_cancel["name"])

        return CORR_CANCEL, expected_prev, None

    # AMEND
    if reason == CORR_AMEND:
        if not amended_from:
            frappe.throw("AMEND فقط وقتی مجاز است که سند amended_from داشته باشد.", frappe.ValidationError)
        if docstatus != 1:
            frappe.throw("خروجی AMEND فقط برای سند Submitted مجاز است.", frappe.ValidationError)

        cancel_of_origin = get_latest_legal_output_name(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=amended_from,
            only_reason=CORR_CANCEL,
        )
        if not cancel_of_origin:
            frappe.throw("برای اصلاحیه، ابتدا باید سند اصلی Cancel شود و خروجی CANCEL صادر گردد.", frappe.ValidationError)

        if previous_output and previous_output != cancel_of_origin:
            frappe.throw("previous_output اصلاحیه باید خروجی CANCEL سند amended_from باشد.", frappe.ValidationError)

        latest_any = get_latest_legal_output(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
        )
        reuse = _reuse_if_same_hash(latest_any, source_hash=source_hash, payload_hash=payload_hash)
        if reuse:
            return CORR_AMEND, cancel_of_origin, reuse

        if latest_any:
            frappe.throw("برای این اصلاحیه قبلاً خروجی قانونی ثبت شده است.", frappe.ValidationError)

        return CORR_AMEND, cancel_of_origin, None

    frappe.throw(f"correction_reason نامعتبر است: {reason}", frappe.ValidationError)
