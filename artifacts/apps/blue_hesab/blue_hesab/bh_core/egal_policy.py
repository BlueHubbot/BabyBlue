# apps/blue_hesab/blue_hesab/bh_core/legal_policy.py
from __future__ import annotations

import frappe


def _norm_reason(reason: str | None) -> str | None:
    r = (reason or "").strip().upper()
    return r or None


def get_latest_legal_output_name(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    exclude_reason: str | None = None,
) -> str | None:
    filters = {
        "company": company,
        "output_type": output_type,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "docstatus": 1,
    }
    if exclude_reason:
        filters["correction_reason"] = ["!=", exclude_reason]

    rows = frappe.get_all(
        "BH Legal Output",
        filters=filters,
        fields=["name", "modified"],
        order_by="modified desc",
        limit_page_length=1,
    )
    return rows[0]["name"] if rows else None


def enforce_legal_output_chain(
    *,
    company: str,
    output_type: str,
    reference_doctype: str,
    reference_name: str,
    correction_reason: str | None,
    previous_output: str | None,
    source_hash: str,
    payload_hash: str,
) -> tuple[str | None, str | None, str | None]:
    """
    Enforces LEGAL-05 chain rules and idempotency.
    Returns: (normalized_reason, normalized_previous_output, reuse_existing_name_or_None)
    """

    reason = _norm_reason(correction_reason)
    prev = (previous_output or "").strip() or None

    # ---- ISSUE (initial) ----
    if reason is None:
        if prev:
            frappe.throw("خروجی اولیه نباید previous_output داشته باشد.", frappe.ValidationError)

        # idempotent reuse: same hashes -> reuse existing ISSUE
        same = frappe.get_all(
            "BH Legal Output",
            filters={
                "company": company,
                "output_type": output_type,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "correction_reason": ["is", "not set"],
                "source_hash": source_hash,
                "payload_hash": payload_hash,
                "docstatus": 1,
            },
            fields=["name", "modified"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if same:
            return None, None, same[0]["name"]

        # prevent divergent duplicate ISSUE
        existing_issue = frappe.get_all(
            "BH Legal Output",
            filters={
                "company": company,
                "output_type": output_type,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "correction_reason": ["is", "not set"],
                "docstatus": 1,
            },
            fields=["name", "source_hash", "payload_hash", "modified"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if existing_issue:
            frappe.throw(
                "خروجی قانونی برای این سند قبلاً صادر شده و با دادهٔ جدید همخوانی ندارد. "
                "برای اصلاح باید از مسیر اصلاحیه (AMEND) استفاده شود.",
                frappe.ValidationError,
            )

        return None, None, None

    # ---- CANCEL ----
    if reason == "CANCEL":
        expected_prev = get_latest_legal_output_name(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=reference_name,
            exclude_reason="CANCEL",
        )
        if not expected_prev:
            frappe.throw("برای CANCEL باید یک خروجی قبلی وجود داشته باشد.", frappe.ValidationError)

        if not prev:
            prev = expected_prev
        elif prev != expected_prev:
            frappe.throw(
                f"previous_output نامعتبر است. مقدار مورد انتظار: {expected_prev}",
                frappe.ValidationError,
            )

        # idempotent reuse: same CANCEL already exists
        same = frappe.get_all(
            "BH Legal Output",
            filters={
                "company": company,
                "output_type": output_type,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "correction_reason": "CANCEL",
                "previous_output": prev,
                "source_hash": source_hash,
                "payload_hash": payload_hash,
                "docstatus": 1,
            },
            fields=["name", "modified"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if same:
            return "CANCEL", prev, same[0]["name"]

        # prevent multiple CANCELs with different content
        any_cancel = frappe.get_all(
            "BH Legal Output",
            filters={
                "company": company,
                "output_type": output_type,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "correction_reason": "CANCEL",
                "docstatus": 1,
            },
            fields=["name", "modified"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if any_cancel:
            frappe.throw("برای این سند قبلاً خروجی CANCEL ثبت شده است.", frappe.ValidationError)

        return "CANCEL", prev, None

    # ---- AMEND ----
    if reason == "AMEND":
        if not prev:
            frappe.throw("برای AMEND باید previous_output ست شود.", frappe.ValidationError)

        amended_from = frappe.db.get_value(reference_doctype, reference_name, "amended_from")
        if not amended_from:
            frappe.throw("برای خروجی اصلاحیه (AMEND)، سند باید amended_from داشته باشد.", frappe.ValidationError)

        expected_prev = get_latest_legal_output_name(
            company=company,
            output_type=output_type,
            reference_doctype=reference_doctype,
            reference_name=amended_from,
            exclude_reason=None,  # آخرین خروجی سند قبلی (معمولاً CANCEL) ملاک است
        )
        if not expected_prev:
            frappe.throw("روی سند amended_from هیچ خروجی قانونی پیدا نشد.", frappe.ValidationError)

        if prev != expected_prev:
            frappe.throw(
                f"previous_output برای AMEND نامعتبر است. مقدار مورد انتظار: {expected_prev}",
                frappe.ValidationError,
            )

        # idempotent reuse: same AMEND already exists for this new doc
        same = frappe.get_all(
            "BH Legal Output",
            filters={
                "company": company,
                "output_type": output_type,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "correction_reason": "AMEND",
                "previous_output": prev,
                "source_hash": source_hash,
                "payload_hash": payload_hash,
                "docstatus": 1,
            },
            fields=["name", "modified"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if same:
            return "AMEND", prev, same[0]["name"]

        # prevent multiple AMENDs on same new document
        any_out = frappe.get_all(
            "BH Legal Output",
            filters={
                "company": company,
                "output_type": output_type,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "docstatus": 1,
            },
            fields=["name", "correction_reason", "modified"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if any_out:
            frappe.throw("برای این سند قبلاً خروجی قانونی ثبت شده است.", frappe.ValidationError)

        return "AMEND", prev, None

    frappe.throw(f"correction_reason پشتیبانی نمی‌شود: {reason}", frappe.ValidationError)
    return reason, prev, None
