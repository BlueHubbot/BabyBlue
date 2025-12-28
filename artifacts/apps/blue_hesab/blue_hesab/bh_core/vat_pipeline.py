# apps/blue_hesab/blue_hesab/bh_core/vat_pipeline.py
# BlueHesab VAT Pipeline (prod-safe + backward compatible handler names)
# HARD MODE: Server Reject non-BH template (legal lock)
from __future__ import annotations

from typing import Optional, Tuple

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import escape_html


KIND_SALES = "sales"
KIND_PURCHASE = "purchase"

AXIS_EXCL = "EXCL"
AXIS_INCL = "INCL"

from .vat_intent import vat11_is_real_pos_sales_invoice

def _axis_from_doc(doc) -> str:
    pm = (doc.get("bh_vat_price_mode") or "").strip()
    if pm:
        return _axis_from_price_mode(pm)

    # VAT-11: only POS may implicitly be INCL
    if getattr(doc, "doctype", None) == "Sales Invoice" and vat11_is_real_pos_sales_invoice(doc):
        return AXIS_INCL

    return AXIS_EXCL

def _norm(s: Optional[str]) -> str:
    return (s or "").strip()


def _company_abbr(company: str) -> str:
    try:
        return frappe.db.get_value("Company", company, "abbr") or ""
    except Exception:
        return ""


def _label_for_kind(kind: str) -> str:
    return "Sales" if kind == KIND_SALES else "Purchase"


def _dt_for_kind(kind: str) -> str:
    return "Sales Taxes and Charges Template" if kind == KIND_SALES else "Purchase Taxes and Charges Template"


def _axis_from_price_mode(value: Optional[str]) -> str:
    v = _norm(value).lower()
    if not v:
        return AXIS_EXCL
    if v.startswith("incl"):
        return AXIS_INCL
    return AXIS_EXCL


def _axis_from_template_name(tpl: Optional[str]) -> Optional[str]:
    name = _norm(tpl)
    if not name:
        return None
    if "(INCL)" in name:
        return AXIS_INCL
    if "(EXCL)" in name:
        return AXIS_EXCL
    return None

def _ensure_price_mode(doc) -> str:
    """
    VAT-11: single source of truth for intent.
    - Normalize bh_vat_price_mode to 'Exclusive' / 'Inclusive'
    - If empty/invalid -> set to 'Exclusive'
    """
    raw = ""
    try:
        raw = (doc.get("bh_vat_price_mode") or "").strip()
    except Exception:
        try:
            raw = (getattr(doc, "bh_vat_price_mode", "") or "").strip()
        except Exception:
            raw = ""

    v = (raw or "").strip()
    lv = v.lower()

    if lv in ("inclusive", "incl", "in"):
        mode = "Inclusive"
    elif lv in ("exclusive", "excl", "ex", ""):
        mode = "Exclusive"
    else:
        # invalid -> force safe default
        mode = "Exclusive"

    # persist canonical value back to doc (prevents empties & accidental flips)
    try:
        doc.bh_vat_price_mode = mode
    except Exception:
        pass
    try:
        doc.set("bh_vat_price_mode", mode)
    except Exception:
        pass

    return mode

def _axis_from_doc(doc) -> str:
    """
    VAT-11: never infer axis from template name.
    Axis comes ONLY from bh_vat_price_mode (normalized & auto-set).
    """
    mode = _ensure_price_mode(doc)
    return AXIS_INCL if mode == "Inclusive" else AXIS_EXCL


def _is_bh_mixed_template(kind: str, tpl: Optional[str]) -> bool:
    t = _norm(tpl)
    if not t:
        return True
    label = _label_for_kind(kind)
    return t.startswith(f"BH VAT MIXED {label}")


def _should_override_template(current: str) -> bool:
    c = _norm(current)
    # only override if empty OR already one of our BH MIXED templates
    return (not c) or c.startswith("BH VAT MIXED")


def _safe_set_taxes_and_charges(doc) -> None:
    try:
        fn = getattr(doc, "set_taxes_and_charges", None)
        if callable(fn):
            fn()
    except Exception:
        pass


def _safe_recalc(doc) -> None:
    try:
        fn = getattr(doc, "calculate_taxes_and_totals", None)
        if callable(fn):
            fn()
    except Exception:
        pass


BH_VAT_SERVER_REJECT_V2 = 1


def _bh_vat_enforced(company: Optional[str] = None) -> bool:
    """
    Enforce only when BH Settings says Iran VAT is ON.
    If default_company is set, enforce only for that company.
    If settings are missing/unreadable, default to ENFORCE (safe).
    """
    try:
        s = frappe.get_single("BH Settings")
        if int(getattr(s, "enable_iran_mode", 0) or 0) != 1:
            return False
        if int(getattr(s, "enable_vat", 0) or 0) != 1:
            return False

        dc = (getattr(s, "default_company", None) or "").strip()
        if dc and company and company != dc:
            return False

        return True
    except Exception:
        return True


def _in_http_request() -> bool:
    # CLI/CI/bench execute => no request
    try:
        return bool(getattr(frappe, "request", None))
    except Exception:
        return False


def _bh_vat_server_reject_message(doctype: str, selected: Optional[str]) -> str:
    sel = _norm(selected)
    if doctype == "Sales Invoice":
        prefix = "BH VAT MIXED Sales"
    elif doctype == "Purchase Invoice":
        prefix = "BH VAT MIXED Purchase"
    else:
        prefix = "BH VAT MIXED"
    if sel:
        return f"BH VAT: قالب مالیات/عوارض غیرمجاز است: {sel}. فقط قالب‌های {prefix} مجاز هستند."
    return f"BH VAT: قالب مالیات/عوارض غیرمجاز است. فقط قالب‌های {prefix} مجاز هستند."


def _bh_vat_ui_html(kind: str, selected: str, allowed_prefix: str, axis: str, expected: str) -> str:
    axis = (axis or AXIS_EXCL).upper()
    axis_fa = "شامل مالیات (Inclusive)" if axis == AXIS_INCL else "بدون مالیات (Exclusive)"
    exp = f"<b>قالب صحیح پیشنهادی:</b> <code>{escape_html(expected)}</code>" if expected else ""
    return f"""
<div style="line-height:1.9">
  <b>خطای قانونی VAT:</b> انتخاب «قالب مالیات/عوارض» غیرمجاز است.<br>
  قالب انتخاب‌شده: <code>{escape_html(selected)}</code><br>
  <br>
  فقط قالب‌های رسمی <code>{escape_html(allowed_prefix)} ...</code> مجاز هستند تا محاسبه مالیات و خروجی‌های قانونی (اظهارنامه/مودیان/TTMS) خراب نشود.
  <hr>
  <b>چه کار کنید؟</b>
  <ol>
    <li>فیلد «نوع قیمت‌گذاری مالیات» را روی <b>{axis_fa}</b> بگذارید.</li>
    <li>فیلد «قالب مالیات/عوارض» را <b>خالی کنید</b> (یا از قالب‌های BH استفاده کنید).</li>
    <li>ذخیره کنید؛ سیستم قالب صحیح BH را اعمال می‌کند.</li>
  </ol>
  {exp}
</div>
""".strip()


def _infer_mixed_template_name(
    *,
    kind: str,
    company: str,
    axis: Optional[str] = None,
    mode: Optional[str] = None,  # legacy alias: "Inclusive"/"Exclusive"
) -> Tuple[str, str]:
    """
    Returns: (template_name, template_doctype)
    Delegates to vat_pipe_templates as the single source of truth.
    """
    from .vat_pipe_templates import infer_mixed_template_name
    return infer_mixed_template_name(kind=kind, company=company, axis=axis, mode=mode)


def _server_reject_non_bh_template(doc, *, kind: str, axis: Optional[str] = None) -> None:
    """
    Hard reject if user sets a non-BH VAT template.
    - Allowed: empty OR BH VAT MIXED <Sales/Purchase>...
    - Reason: legal/compliance; prevents silent wrong VAT reporting.
    """
    company = getattr(doc, "company", None) or doc.get("company")
    if not company:
        return
    if not _bh_vat_enforced(company):
        return

    current = _norm(getattr(doc, "taxes_and_charges", None) or doc.get("taxes_and_charges"))
    if not current:
        return

    label = _label_for_kind(kind)  # "Sales" / "Purchase"
    allowed_prefix = f"BH VAT MIXED {label}"

    if current.startswith(allowed_prefix):
        return

    if not axis:
        axis = _axis_from_doc(doc)

    expected = ""
    try:
        expected, _dt = _infer_mixed_template_name(kind=kind, company=company, axis=axis)
    except Exception:
        expected = ""

    title = "قفل قانونی مالیات بر ارزش افزوده (VAT)"

    # UI keeps the rich HTML (no change)
    if _in_http_request():
        msg = _bh_vat_ui_html(kind=kind, selected=current, allowed_prefix=allowed_prefix, axis=axis or AXIS_EXCL, expected=expected)
        frappe.throw(msg, title=title)

    # Server/CI gets short message
    frappe.throw(
        _bh_vat_server_reject_message(getattr(doc, "doctype", ""), current),
        title=title,
        exc=ValidationError,
    )


def _reject_if_non_bh_template(doc, *, kind: str, company: str, axis: str) -> None:
    current = _norm(getattr(doc, "taxes_and_charges", None) or doc.get("taxes_and_charges"))
    if not current:
        return
    if _is_bh_mixed_template(kind, current):
        return

    # keep consistent with server guard behaviour
    _server_reject_non_bh_template(doc, kind=kind, axis=axis)


def _set_official_template_if_needed(
    doc,
    *,
    kind: str,
    company: Optional[str] = None,
    axis: Optional[str] = None,
    mode: Optional[str] = None,  # legacy
    is_submit: bool = False,     # legacy
) -> None:
    """
    VAT-25: legacy helper kept for backward compatibility.
    Previously this function could auto-set taxes_and_charges (draft/submit).
    That behaviour is now DISABLED to prevent silent flips.
    """
    company = company or (getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None))
    if not company:
        return

    if not axis:
        axis = _axis_from_doc(doc)

    # still enforce legal lock for non-BH templates
    _server_reject_non_bh_template(doc, kind=kind, axis=axis)

    # no-op: do not mutate doc.taxes_and_charges here
    return

def _apply_mixed_layer(doc, *, kind: str) -> None:
    # must run in before_validate
    from blue_hesab.bh_core import vat_mixed

    if kind == KIND_SALES:
        vat_mixed.bh_before_validate_sales_invoice(doc, None)
    else:
        vat_mixed.bh_before_validate_purchase_invoice(doc, None)


def bh_before_validate_sales_invoice(doc, method=None):
    _bh_capture_pre_pipeline_snapshot(doc)

    company = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None)
    axis = _axis_from_doc(doc)

    # VAT-26: block INCL on non-POS unless explicit intent
    from .vat_intent import vat26_enforce_inclusive_intent
    vat26_enforce_inclusive_intent(doc, kind=KIND_SALES, axis=axis)


    # Legal lock: reject non-BH templates (draft safe: empty is allowed)
    _server_reject_non_bh_template(doc, kind=KIND_SALES, axis=axis)

    # VAT-25: NEVER auto-fill/auto-flip taxes_and_charges on draft/refresh.
    # Applying the expected template is an explicit UI action (modal button).
    _apply_mixed_layer(doc, kind=KIND_SALES)
    _safe_recalc(doc)

def bh_before_validate_purchase_invoice(doc, method=None):
    _bh_capture_pre_pipeline_snapshot(doc)

    company = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None)
    axis = _axis_from_doc(doc)

    # VAT-26: block INCL unless explicit intent
    from .vat_intent import vat26_enforce_inclusive_intent
    vat26_enforce_inclusive_intent(doc, kind=KIND_PURCHASE, axis=axis)


    _server_reject_non_bh_template(doc, kind=KIND_PURCHASE, axis=axis)

    # VAT-25: NEVER auto-fill/auto-flip taxes_and_charges on draft/refresh.
    _apply_mixed_layer(doc, kind=KIND_PURCHASE)
    _safe_recalc(doc)

def bh_validate_sales_invoice(doc, method=None):
    company = getattr(doc, "company", None) or doc.get("company")
    axis = _axis_from_doc(doc)
    if company:
        _reject_if_non_bh_template(doc, kind=KIND_SALES, company=company, axis=axis)

    from blue_hesab.bh_core import vat_hooks
    vat_hooks.apply_sales_invoice_vat(doc, method)


def bh_validate_purchase_invoice(doc, method=None):
    company = getattr(doc, "company", None) or doc.get("company")
    axis = _axis_from_doc(doc)
    if company:
        _reject_if_non_bh_template(doc, kind=KIND_PURCHASE, company=company, axis=axis)

    from blue_hesab.bh_core import vat_hooks
    vat_hooks.apply_purchase_invoice_vat(doc, method)


# -------------------------
# BACKWARD COMPATIBILITY (do NOT remove)
# -------------------------

def before_validate_sales_invoice(doc, method=None):
    return bh_before_validate_sales_invoice(doc, method)


def before_validate_purchase_invoice(doc, method=None):
    return bh_before_validate_purchase_invoice(doc, method)


def validate_sales_invoice(doc, method=None):
    return bh_validate_sales_invoice(doc, method)


def validate_purchase_invoice(doc, method=None):
    return bh_validate_purchase_invoice(doc, method)


def debug_infer_mixed_template(kind: str, company: str, axis: str = AXIS_EXCL) -> dict:
    name, dt = _infer_mixed_template_name(kind=kind, company=company, axis=axis)
    return {"kind": kind, "company": company, "axis": axis, "doctype": dt, "name": name}


# ---------------------------------------------------------------------------
# VAT-18: SUBMIT SAFE / POST-SUBMIT STABILITY
# - Do NOT auto-flip MIXED template during submit (keep mismatch)
# - Enforce template<->price_mode match on before_submit (hard block)
# ---------------------------------------------------------------------------

def _is_submit_action(doc, is_submit_flag: bool = False) -> bool:
    """Robust submit detection for doc_events hooks."""
    try:
        if is_submit_flag:
            return True

        action = (getattr(doc, "_action", None) or "").lower()
        if not action:
            try:
                action = (getattr(getattr(doc, "flags", None), "action", None) or "").lower()
            except Exception:
                action = ""
        if action == "submit":
            return True

        try:
            if bool(getattr(getattr(doc, "flags", None), "in_submit", False)):
                return True
        except Exception:
            pass
        try:
            if bool(getattr(getattr(frappe, "flags", None), "in_submit", False)):
                return True
        except Exception:
            pass

        ds = int(getattr(doc, "docstatus", 0) or 0)
        if ds == 1 and action not in ("update_after_submit", "cancel", "amend"):
            return True

        return False
    except Exception:
        return False


def _bh_capture_pre_pipeline_snapshot(doc) -> None:
    """Capture user intent BEFORE VAT pipeline auto-fixes taxes_and_charges.

    VAT-18 requires blocking INCL/EXCL mismatch on submit using the ORIGINAL
    user-selected taxes_and_charges (pre-flip).
    """
    try:
        flags = getattr(doc, "flags", None)
        if not flags:
            return

        tpl = ""
        try:
            tpl = (getattr(doc, "taxes_and_charges", None) or (doc.get("taxes_and_charges") if hasattr(doc, "get") else None) or "")
        except Exception:
            tpl = ""

        mode = ""
        try:
            mode = (getattr(doc, "bh_vat_price_mode", None) or (doc.get("bh_vat_price_mode") if hasattr(doc, "get") else None) or "")
        except Exception:
            mode = ""

        # overwrite every call (important for submit call path)
        flags._bh_vat_pre_pipeline_tpl = (tpl or "").strip()
        flags._bh_vat_pre_pipeline_mode = str(mode or "").strip()
    except Exception:
        return

def _enforce_mixed_tpl_matches_mode_on_submit(doc, kind: str) -> None:
    """
    VAT-25: On submit, enforce policy WITHOUT auto-flip/auto-fill.
    Rules when BH VAT is enforced:
      - taxes_and_charges MUST be set (not empty)
      - MUST be one of BH VAT MIXED templates for the (kind, axis)
      - Axis marker (INCL/EXCL) MUST match bh_vat_price_mode
    Fix is an explicit user action (VAT modal -> "اعمال قالب پیشنهادی").
    """
    company = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None)
    if not company:
        return
    if not _bh_vat_enforced(company):
        return

    axis = _axis_from_doc(doc)  # reads bh_vat_price_mode first (source of truth)

    # VAT-26: Inclusive requires explicit intent (or POS for Sales)
    from .vat_intent import vat26_enforce_inclusive_intent
    vat26_enforce_inclusive_intent(doc, kind=kind, axis=axis)

    tpl = (getattr(doc, "taxes_and_charges", None) or (doc.get("taxes_and_charges") if hasattr(doc, "get") else "") or "").strip()

    expected = ""
    try:
        expected, _dt = _infer_mixed_template_name(kind=kind, company=company, axis=axis, mode=None)
    except Exception:
        expected = ""

    if not tpl:
        msg = (
            "BH VAT: ثبت (Submit) مجاز نیست چون «قالب مالیات/عوارض» خالی است.\n"
            + (f"- قالب پیشنهادی: {expected}\n" if expected else "")
            + "برای ادامه: مودال «Taxes & Charges Template» را باز کنید و روی «اعمال قالب پیشنهادی» بزنید."
        )
        frappe.throw(msg, title="BH VAT", exc=ValidationError)

    # Reject any non-BH template (legal lock)
    _server_reject_non_bh_template(doc, kind=kind, axis=axis)

    # Enforce axis match for BH MIXED templates (no auto-flip)
    if _is_bh_mixed_template(kind, tpl):
        tpl_axis = _axis_from_template_name(tpl) or AXIS_EXCL
        if tpl_axis != axis:
            msg = (
                "BH VAT: عدم تطابق «نوع قیمت‌گذاری مالیات» با «قالب مالیات/عوارض» در زمان ثبت (Submit).\n"
                f"- bh_vat_price_mode (axis): {axis}\n"
                f"- taxes_and_charges: {tpl}\n"
                + (f"- قالب پیشنهادی: {expected}\n" if expected else "")
                + "برای ادامه: مودال «Taxes & Charges Template» را باز کنید و روی «اعمال قالب پیشنهادی» بزنید."
            )
            frappe.throw(msg, title="BH VAT", exc=ValidationError)

def bh_before_submit_sales_invoice(doc, method=None):
    _enforce_mixed_tpl_matches_mode_on_submit(doc, kind=KIND_SALES)


def bh_before_submit_purchase_invoice(doc, method=None):
    _enforce_mixed_tpl_matches_mode_on_submit(doc, kind=KIND_PURCHASE)


def before_submit_sales_invoice(doc, method=None):
    return bh_before_submit_sales_invoice(doc, method)


def before_submit_purchase_invoice(doc, method=None):
    return bh_before_submit_purchase_invoice(doc, method)

@frappe.whitelist()
def vat19_expected_mixed_template(kind: str, axis: str, company: str | None = None) -> dict:
    """
    UI helper for VAT-19:
    returns the official BH VAT MIXED template name for (kind, axis, company).
    kind: "sales" | "purchase"
    axis: "EXCL" | "INCL" (or "Exclusive"/"Inclusive")
    """
    k = (kind or "").strip().lower()
    if k not in ("sales", "purchase"):
        frappe.throw(f"Invalid kind: {kind}")

    ax = (axis or "").strip().upper()
    if ax in ("EXCLUSIVE", "EXCL"):
        ax = AXIS_EXCL
    elif ax in ("INCLUSIVE", "INCL"):
        ax = AXIS_INCL
    elif ax not in (AXIS_EXCL, AXIS_INCL):
        frappe.throw(f"Invalid axis: {axis}")

    if not company:
        try:
            company = getattr(get_bh_settings(), "default_company", None) or None
        except Exception:
            company = None
    if not company:
        company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_default("company")

    tpl_name, _dt = _infer_mixed_template_name(kind=("sales" if k == "sales" else "purchase"), company=company, axis=ax)
    return {"company": company, "axis": ax, "expected": tpl_name}