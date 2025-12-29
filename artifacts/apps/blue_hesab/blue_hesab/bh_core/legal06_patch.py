# -*- coding: utf-8 -*-
"""
LEGAL-06 Patch

Problem:
- اگر BH Legal Output.reference_name = Dynamic Link باشد، Frappe هنگام Cancel کردن Invoice
  به خاطر Dynamic Link، Cancel را Block می‌کند (LinkExistsError).

Fix:
- reference_name را از Dynamic Link به Data تبدیل می‌کنیم.
  (reference_doctype می‌تواند Link به DocType بماند.)

این پچ فقط DB meta را اصلاح می‌کند (DocField).
بعداً باید doctype json هم در repo sync شود (برای GitOps).
"""

from __future__ import annotations

import frappe


def apply(*, dry_run: bool = False) -> dict:
    fieldname = "reference_name"
    parent = "BH Legal Output"

    df_name = frappe.db.get_value("DocField", {"parent": parent, "fieldname": fieldname}, "name")
    if not df_name:
        frappe.throw(f"DocField {parent}.{fieldname} پیدا نشد.", frappe.ValidationError)

    df = frappe.get_doc("DocField", df_name)
    before = {"fieldtype": df.fieldtype, "options": df.options}

    changed = False
    if df.fieldtype != "Data":
        df.fieldtype = "Data"
        changed = True
    if df.options:
        df.options = ""
        changed = True

    if changed and not dry_run:
        df.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache(doctype=parent)

    return {
        "docfield": df_name,
        "before": before,
        "after": {"fieldtype": df.fieldtype, "options": df.options},
        "changed": changed,
        "dry_run": dry_run,
    }
