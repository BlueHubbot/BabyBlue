from __future__ import annotations

from typing import Any, Dict, Optional

import frappe
from frappe.exceptions import ValidationError

from .vat_pipe_common import (
    axis_from_template_name,
    bh_vat_enforced,
    infer_mixed_template_name,
    is_mixed_template,
    is_submit_action,
    normalize_axis,
    normalize_price_mode,
    ui_expected_hint,
    AXIS_EXCL,
    AXIS_INCL,
    KIND_PURCHASE,
    KIND_SALES,
    MODE_EXCL,
    MODE_INCL,
)

VAT11_POLICY_VER = "VAT-11.1"


def _get_company(doc) -> str:
    try:
        return (doc.get("company") if hasattr(doc, "get") else getattr(doc, "company", None)) or ""
    except Exception:
        return ""


def _get_mode(doc) -> str:
    try:
        return (doc.get("bh_vat_price_mode") if hasattr(doc, "get") else getattr(doc, "bh_vat_price_mode", None)) or ""
    except Exception:
        return ""


def _set_mode(doc, mode: str) -> None:
    if hasattr(doc, "set"):
        doc.set("bh_vat_price_mode", mode)
    else:
        setattr(doc, "bh_vat_price_mode", mode)

    # optional legacy mirror
    try:
        if hasattr(doc, "meta") and doc.meta.has_field("bh_vat_inclusive_intent"):
            doc.set("bh_vat_inclusive_intent", 1 if normalize_price_mode(mode) == MODE_INCL else 0)
    except Exception:
        pass


def _get_template(doc) -> str:
    try:
        return (doc.get("taxes_and_charges") if hasattr(doc, "get") else getattr(doc, "taxes_and_charges", None)) or ""
    except Exception:
        return ""


def _set_suggested(doc, suggested: str) -> None:
    try:
        if not hasattr(doc, "flags") or doc.flags is None:
            doc.flags = frappe._dict()
        doc.flags.bh_vat_suggested_taxes_and_charges = suggested
    except Exception:
        pass


def _build_mismatch_reason(expected: str) -> str:
    hint = ui_expected_hint(expected)
    return (
        "قفل قانونی VAT: نوع قیمت‌گذاری مالیات (Intent) با قالب مالیات (Taxes & Charges) هم‌خوان نیست.\n"
        f"{hint}\n"
        "در Draft فقط «پیشنهاد» ارائه می‌شود؛ اما هنگام Submit این سند مسدود می‌شود تا flip پنهان رخ ندهد."
    ).strip()


def vat11_lock_intent_guard(
    doc,
    *,
    kind: str,
    axis: Optional[str] = None,
    allow_pos_implicit: bool = True,
    real_pos: Optional[bool] = None,
    no_autofix: bool = True,
    is_submit: Optional[bool] = None,
) -> Dict[str, Any]:
    company = _get_company(doc)
    if not bh_vat_enforced(company):
        return {"ver": VAT11_POLICY_VER, "skipped": True, "reason": "out_of_scope"}

    k = (kind or "").strip().lower()
    if k not in (KIND_SALES, KIND_PURCHASE):
        return {"ver": VAT11_POLICY_VER, "skipped": True, "reason": "unknown_kind"}

    submit = bool(is_submit) if is_submit is not None else bool(is_submit_action(doc))

    # ---- resolve / default intent ----
    cur_mode_raw = _get_mode(doc)
    cur_mode = cur_mode_raw.strip()
    defaulted_to: Optional[str] = None

    if not cur_mode:
        is_pos = bool(real_pos) if (real_pos is not None) else False
        if k == KIND_SALES and allow_pos_implicit and is_pos:
            cur_mode = MODE_INCL
        else:
            cur_mode = MODE_EXCL
        defaulted_to = cur_mode
        _set_mode(doc, cur_mode)

    cur_mode = normalize_price_mode(cur_mode)

    # ---- template ----
    tpl = _get_template(doc)
    if not tpl:
        expected = infer_mixed_template_name(kind=k, company=company, mode=cur_mode)
        _set_suggested(doc, expected)
        if submit:
            msg = (
                "BH VAT: ثبت (Submit) مجاز نیست چون «قالب مالیات/عوارض» خالی است.\n"
                f"- {ui_expected_hint(expected)}\n"
                "برای ادامه: مودال «Taxes & Charges Template» را باز کنید و روی «اعمال قالب پیشنهادی» بزنید."
            ).strip()
            raise ValidationError(msg)
        return {
            "ver": VAT11_POLICY_VER,
            "defaulted_to": defaulted_to,
            "mismatch": True,
            "suggested": expected,
            "submit_blocked": False,
            "reason": "empty_template",
        }

    # non-mixed => this layer must not act (other guards may reject it)
    if not is_mixed_template(tpl, kind=k):
        return {"ver": VAT11_POLICY_VER, "skipped": True, "reason": "non_mixed_template", "template": tpl}

    tpl_axis = axis_from_template_name(tpl)
    eff_axis = normalize_axis(axis or tpl_axis)

    expected = infer_mixed_template_name(kind=k, company=company, axis=eff_axis, mode=cur_mode)

    mismatch = (tpl.strip() != expected.strip())
    if mismatch:
        _set_suggested(doc, expected)
        reason = _build_mismatch_reason(expected)
        if submit:
            raise ValidationError(reason)
        return {
            "ver": VAT11_POLICY_VER,
            "defaulted_to": defaulted_to,
            "mismatch": True,
            "suggested": expected,
            "submit_blocked": False,
            "reason": reason,
        }

    return {
        "ver": VAT11_POLICY_VER,
        "defaulted_to": defaulted_to,
        "mismatch": False,
        "suggested": expected,
        "submit_blocked": False,
        "reason": "",
    }
