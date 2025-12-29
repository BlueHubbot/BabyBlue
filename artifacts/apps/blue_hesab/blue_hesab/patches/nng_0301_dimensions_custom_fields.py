from __future__ import annotations

import frappe


def _ensure_cf(dt: str, fieldname: str, **kwargs) -> bool:
    frappe.reload_doc("core", "doctype", "custom_field")
    meta = frappe.get_meta(dt)
    if meta.has_field(fieldname):
        return False

    doc = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": dt,
        "fieldname": fieldname,
        **kwargs,
    })
    doc.insert(ignore_permissions=True)
    return True


def execute():
    # Ensure BH Tafsili doctype is available
    try:
        frappe.reload_doc("blue_hesab", "doctype", "bh_tafsili")
    except Exception:
        pass

    # Header fields (Sales/Purchase Invoice)
    for dt in ("Sales Invoice", "Purchase Invoice"):
        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after="company",
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

    # Row fields (Sales/Purchase Invoice Item)
    for dt in ("Sales Invoice Item", "Purchase Invoice Item"):
        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after="project" if frappe.get_meta(dt).has_field("project") else "item_code",
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

    # GL Entry stamping fields (voucher-level)
    dt = "GL Entry"
    _ensure_cf(
        dt,
        "bh_branch",
        label="شعبه (BH)",
        fieldtype="Link",
        options="Branch",
        insert_after="project" if frappe.get_meta(dt).has_field("project") else "voucher_no",
        reqd=0,
        read_only=1,
    )
    _ensure_cf(
        dt,
        "bh_tafsili_1",
        label="تفصیلی ۱ (BH)",
        fieldtype="Link",
        options="BH Tafsili",
        insert_after="bh_branch",
        reqd=0,
        read_only=1,
    )
    _ensure_cf(
        dt,
        "bh_tafsili_2",
        label="تفصیلی ۲ (BH)",
        fieldtype="Link",
        options="BH Tafsili",
        insert_after="bh_tafsili_1",
        reqd=0,
        read_only=1,
    )
