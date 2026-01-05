from __future__ import annotations

import frappe


def _ensure_cf(dt: str, fieldname: str, **kwargs) -> bool:
    frappe.reload_doc("core", "doctype", "custom_field")
    meta = frappe.get_meta(dt)
    if meta.has_field(fieldname):
        return False

    doc = frappe.get_doc(
        {
            "doctype": "Custom Field",
            "dt": dt,
            "fieldname": fieldname,
            **kwargs,
        }
    )
    doc.insert(ignore_permissions=True)
    return True


def _safe_meta(dt: str):
    try:
        return frappe.get_meta(dt)
    except Exception:
        return None


def execute():
    # Ensure BH Tafsili doctype is available
    try:
        frappe.reload_doc("blue_hesab", "doctype", "bh_tafsili")
    except Exception:
        pass

    # --- Header fields: JE / PE ------------------------------------------------
    for dt in ("Journal Entry", "Payment Entry"):
        meta = _safe_meta(dt)
        if not meta:
            continue

        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after="company" if meta.has_field("company") else "posting_date",
            reqd=0,
            no_copy=0,
            print_hide=0,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_1",
            label="تفصیلی ۱",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_branch",
            reqd=0,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_2",
            label="تفصیلی ۲",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_tafsili_1",
            reqd=0,
        )

    # --- Row fields: Journal Entry Account ------------------------------------
    dt = "Journal Entry Account"
    meta = _safe_meta(dt)
    if meta:
        insert_after = "cost_center" if meta.has_field("cost_center") else ("account" if meta.has_field("account") else "idx")
        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after=insert_after,
            reqd=0,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_1",
            label="تفصیلی ۱",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_branch",
            reqd=0,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_2",
            label="تفصیلی ۲",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_tafsili_1",
            reqd=0,
        )

    # --- Row fields: Payment Entry Deduction (best-effort) --------------------
    dt = "Payment Entry Deduction"
    meta = _safe_meta(dt)
    if meta:
        insert_after = "cost_center" if meta.has_field("cost_center") else ("amount" if meta.has_field("amount") else "idx")
        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after=insert_after,
            reqd=0,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_1",
            label="تفصیلی ۱",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_branch",
            reqd=0,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_2",
            label="تفصیلی ۲",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_tafsili_1",
            reqd=0,
        )
