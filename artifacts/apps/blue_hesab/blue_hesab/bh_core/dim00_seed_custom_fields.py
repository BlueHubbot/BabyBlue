from __future__ import annotations

import frappe


def _upsert_custom_field(cf: dict) -> str:
    """
    Upsert Custom Field by (dt, fieldname).
    Returns Custom Field name.
    """
    existing = frappe.db.get_value(
        "Custom Field",
        {"dt": cf["dt"], "fieldname": cf["fieldname"]},
        "name",
    )
    if existing:
        doc = frappe.get_doc("Custom Field", existing)
        # only update safe keys
        for k, v in cf.items():
            if k in ("dt", "fieldname"):
                continue
            doc.set(k, v)
        doc.save(ignore_permissions=True)
        return existing

    doc = frappe.get_doc({"doctype": "Custom Field", **cf})
    doc.insert(ignore_permissions=True)
    return doc.name


def run_cli() -> dict:
    """
    Creates JE/PE header dimension fields:
      - bh_branch (Link -> Branch) label: شعبه
      - bh_tafsili_1 (Link -> BH Tafsili) label: تفصیلی ۱
    Non-mandatory at field-level (policy enforces on submit).
    """
    created_or_updated = []

    targets = ["Journal Entry", "Payment Entry"]

    for dt in targets:
        created_or_updated.append(
            _upsert_custom_field(
                {
                    "dt": dt,
                    "fieldname": "bh_branch",
                    "label": "شعبه",
                    "fieldtype": "Link",
                    "options": "Branch",
                    "insert_after": "posting_date",
                    "reqd": 0,
                    "hidden": 0,
                    "read_only": 0,
                    "allow_on_submit": 0,
                    "read_only_depends_on": "eval:doc.docstatus==1",
                    "in_list_view": 0,
                    "module": "Blue Hesab",
                }
            )
        )

        created_or_updated.append(
            _upsert_custom_field(
                {
                    "dt": dt,
                    "fieldname": "bh_tafsili_1",
                    "label": "تفصیلی ۱",
                    "fieldtype": "Link",
                    "options": "BH Tafsili",
                    "insert_after": "bh_branch",
                    "reqd": 0,
                    "hidden": 0,
                    "read_only": 0,
                    "allow_on_submit": 0,
                    "read_only_depends_on": "eval:doc.docstatus==1",
                    "in_list_view": 0,
                    "module": "Blue Hesab",
                }
            )
        )

    frappe.clear_cache()
    frappe.db.commit()

    return {"ok": True, "updated": created_or_updated}
