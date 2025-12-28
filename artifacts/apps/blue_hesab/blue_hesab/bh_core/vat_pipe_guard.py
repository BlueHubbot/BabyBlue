# apps/blue_hesab/blue_hesab/bh_core/vat_pipe_guard.py
from __future__ import annotations

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import escape_html

from .vat_pipe_common import (
    AXIS_EXCL,
    axis_from_doc,
    bh_vat_enforced,
    in_http_request,
    label_for_kind,
    norm,
    ui_expected_hint,
)
from .vat_pipe_templates import infer_mixed_template_name


def _server_reject_msg(doctype: str, selected: str) -> str:
    sel = norm(selected)
    prefix = "BH VAT MIXED"
    if doctype == "Sales Invoice":
        prefix = "BH VAT MIXED Sales"
    elif doctype == "Purchase Invoice":
        prefix = "BH VAT MIXED Purchase"
    if sel:
        return f"BH VAT: قالب مالیات/عوارض غیرمجاز است: {sel}. فقط قالب‌های {prefix} مجاز هستند."
    return f"BH VAT: قالب مالیات/عوارض غیرمجاز است. فقط قالب‌های {prefix} مجاز هستند."


def _ui_reject_html(kind: str, selected: str, allowed_prefix: str, axis: str, expected: str) -> str:
    axis = (axis or AXIS_EXCL).upper()
    axis_fa = "شامل مالیات (Inclusive)" if axis == "INCL" else "بدون مالیات (Exclusive)"
    exp = ui_expected_hint(expected)
    return f"""
<div style="line-height:1.9">
  <b>خطای قانونی VAT:</b> انتخاب «قالب مالیات/عوارض» غیرمجاز است.<br>
  قالب انتخاب‌شده: <code>{escape_html(selected)}</code><br><br>
  فقط قالب‌های رسمی <code>{escape_html(allowed_prefix)}</code> مجاز هستند تا محاسبه مالیات و خروجی‌های قانونی خراب نشود.
  <hr>
  <b>چه کار کنید؟</b>
  <ol>
    <li>فیلد «نوع قیمت‌گذاری مالیات» را روی <b>{axis_fa}</b> بگذارید.</li>
    <li>فیلد «قالب مالیات/عوارض» را <b>خالی کنید</b> (یا از قالب‌های BH استفاده کنید).</li>
    <li>مودال «قالب مالیات/عوارض» را باز کنید و روی «اعمال قالب پیشنهادی» بزنید.</li>
  </ol>
  {exp}
</div>
""".strip()


def reject_non_bh_template(doc, *, kind: str, axis: str | None = None) -> None:
    company = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None)
    if not company:
        return
    if not bh_vat_enforced(company):
        return

    current = norm(getattr(doc, "taxes_and_charges", None) or (doc.get("taxes_and_charges") if hasattr(doc, "get") else ""))
    if not current:
        return

    allowed_prefix = f"BH VAT MIXED {label_for_kind(kind)}"
    if current.startswith(allowed_prefix):
        return

    axis = axis or axis_from_doc(doc)

    expected = ""
    try:
        expected, _dt = infer_mixed_template_name(kind=kind, company=company, axis=axis)
    except Exception:
        expected = ""

    title = "قفل قانونی مالیات بر ارزش افزوده (VAT)"

    if in_http_request():
        frappe.throw(_ui_reject_html(kind=kind, selected=current, allowed_prefix=allowed_prefix, axis=axis, expected=expected), title=title)

    frappe.throw(_server_reject_msg(getattr(doc, "doctype", ""), current), title=title, exc=ValidationError)


def submit_block_intent_mismatch(doc, *, kind: str, selected: str, expected: str, mode: str) -> None:
    title = "قفل قانونی مالیات بر ارزش افزوده (VAT)"
    if in_http_request():
        axis_fa = "شامل مالیات (Inclusive)" if "incl" in (mode or "").lower() else "بدون مالیات (Exclusive)"
        msg = f"""
<div style="line-height:1.9">
  <b>خطای قانونی VAT:</b> در زمان <b>ثبت نهایی (Submit)</b>، «قالب مالیات/عوارض» باید با «نوع قیمت‌گذاری مالیات» هم‌خوان باشد.<br>
  <br>
  نوع قیمت‌گذاری مالیات: <b>{escape_html(mode or "")}</b> ({axis_fa})<br>
  قالب فعلی: <code>{escape_html(selected)}</code><br>
  قالب مورد انتظار: <code>{escape_html(expected)}</code><br>
  <hr>
  <b>چه کار کنید؟</b>
  <ol>
    <li>سند را <b>ذخیره</b> کنید تا سیستم قالب صحیح را اعمال کند.</li>
    <li>سپس دوباره <b>ثبت نهایی</b> کنید.</li>
  </ol>
</div>
""".strip()
        frappe.throw(msg, title=title)

    frappe.throw(
        f"BH VAT submit blocked: intent mismatch (mode='{mode}', got='{selected}', expected='{expected}')",
        title=title,
        exc=ValidationError,
    )
