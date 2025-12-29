from __future__ import annotations

import frappe


def execute():
    if not frappe.db.exists("DocType", "BH Legal Output"):
        return

    df = frappe.db.get_value(
        "DocField",
        {"parent": "BH Legal Output", "fieldname": "reference_name"},
        ["name", "fieldtype", "options"],
        as_dict=True,
    )
    if not df:
        return

    # only mutate when it is exactly the problematic dynamic link
    if df.fieldtype == "Dynamic Link" and (df.options or "") == "reference_doctype":
        frappe.db.set_value("DocField", df.name, "fieldtype", "Data")
        frappe.db.set_value("DocField", df.name, "options", "")
        frappe.clear_cache(doctype="BH Legal Output")
