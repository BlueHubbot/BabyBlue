from __future__ import annotations

import frappe
from frappe import _


def _copy_field(dst, src, fieldname: str):
    if hasattr(src, fieldname) and hasattr(dst, fieldname):
        v = getattr(src, fieldname, None)
        if v is not None:
            setattr(dst, fieldname, v)


def _map_item_templates_by_item_code(original_doc):
    m = {}
    for it in (original_doc.get("items") or []):
        code = getattr(it, "item_code", None)
        tmpl = getattr(it, "item_tax_template", None)
        if not code:
            continue
        if code in m and (m[code] or "") != (tmpl or ""):
            frappe.throw(
                _("در سند مرجع، آیتم «{0}» با چند قالب مالیات متفاوت ثبت شده است. برگشت خودکار مبهم است.").format(code)
            )
        m[code] = tmpl
    return m


def _sync_return_item_templates(doc, original_doc):
    mapping = _map_item_templates_by_item_code(original_doc)
    for it in (doc.get("items") or []):
        code = getattr(it, "item_code", None)
        if not code:
            continue
        tmpl = mapping.get(code)
        if tmpl:
            it.item_tax_template = tmpl


def _assert_return_against(doc, doctype: str):
    if not getattr(doc, "is_return", 0):
        return None
    against = getattr(doc, "return_against", None)
    if not against:
        frappe.throw(_("برای «برگشت» باید «سند مرجع» مشخص شود (return_against)."))
    original = frappe.get_doc(doctype, against)

    if int(original.docstatus or 0) != 1:
        frappe.throw(_("سند مرجع باید ارسال/ثبت شده باشد (docstatus=1)."))
    if original.company != doc.company:
        frappe.throw(_("سند برگشت باید با همان شرکت سند مرجع باشد."))

    return original


def before_validate_sales_invoice(doc, method=None):
    original = _assert_return_against(doc, "Sales Invoice")
    if not original:
        return
    _copy_field(doc, original, "bh_vat_price_mode")
    _sync_return_item_templates(doc, original)


def before_validate_purchase_invoice(doc, method=None):
    original = _assert_return_against(doc, "Purchase Invoice")
    if not original:
        return
    _copy_field(doc, original, "bh_vat_price_mode")
    _sync_return_item_templates(doc, original)

# --- BlueHesab hook wrappers (bh_* naming) ---
def bh_before_validate_sales_invoice(doc, method=None):
    return before_validate_sales_invoice(doc, method)

def bh_before_validate_purchase_invoice(doc, method=None):
    return before_validate_purchase_invoice(doc, method)
