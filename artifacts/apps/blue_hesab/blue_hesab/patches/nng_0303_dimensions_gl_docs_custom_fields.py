from __future__ import annotations

import frappe


def _doctype_exists(dt: str) -> bool:
    try:
        return bool(frappe.db.exists("DocType", dt))
    except Exception:
        return False


def _best_insert_after(dt: str, candidates: tuple[str, ...]) -> str | None:
    try:
        meta = frappe.get_meta(dt)
        for c in candidates:
            if meta.has_field(c):
                return c
    except Exception:
        pass
    return None


def _ensure_cf(dt: str, fieldname: str, **kwargs) -> None:
    if not _doctype_exists(dt):
        return

    if frappe.db.exists("Custom Field", f"{dt}-{fieldname}"):
        return

    insert_after = kwargs.pop("insert_after", None)
    if not insert_after:
        insert_after = _best_insert_after(dt, ("company", "posting_date", "customer", "supplier", "item_code"))
    if not insert_after:
        insert_after = "company"

    doc = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": dt,
        "fieldname": fieldname,
        "insert_after": insert_after,
        **kwargs,
    })
    doc.insert(ignore_permissions=True)


def execute():
    """
    DIM-05:
    Add BH dimensions to common GL-posting doctypes (header + line doctypes)
    so GL Entry stamp can work everywhere, not فقط SI/PI/JE/PE.
    """

    # Header doctypes
    header_dts = (
        "Stock Entry",
        "Stock Reconciliation",
        "Delivery Note",
        "Purchase Receipt",
        "POS Invoice",
        "Expense Claim",
    )

    # Line doctypes (child tables whose row 'name' becomes voucher_detail_no in GL Entry)
    line_dts = (
        "Stock Entry Detail",
        "Stock Reconciliation Item",
        "Delivery Note Item",
        "Purchase Receipt Item",
        "POS Invoice Item",
        "Expense Claim Detail",
        "Payment Entry Reference",  # optional but useful
    )

    for dt in header_dts:
        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after=_best_insert_after(dt, ("company", "posting_date", "customer", "supplier")) or "company",
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

    for dt in line_dts:
        ins = _best_insert_after(dt, ("cost_center", "project", "item_code", "account", "expense_account")) or "item_code"
        _ensure_cf(
            dt,
            "bh_branch",
            label="شعبه",
            fieldtype="Link",
            options="Branch",
            insert_after=ins,
            reqd=0,
            no_copy=0,
            print_hide=1,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_1",
            label="تفصیلی ۱",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_branch",
            reqd=0,
            print_hide=1,
        )
        _ensure_cf(
            dt,
            "bh_tafsili_2",
            label="تفصیلی ۲",
            fieldtype="Link",
            options="BH Tafsili",
            insert_after="bh_tafsili_1",
            reqd=0,
            print_hide=1,
        )
