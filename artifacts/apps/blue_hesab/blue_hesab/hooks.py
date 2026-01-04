# -*- coding: utf-8 -*-
# BlueHesab - Frappe hooks

app_name = "blue_hesab"
app_title = "BlueHesab"
app_publisher = "BlueAPi"
app_description = "BlueHesab Core"
app_email = "dev@blueapi"
app_license = "MIT"

# -------------------------------------------------------------------
# VAT pipeline (single source of truth)
# - intent/mode enforcement: before_validate (vat_pipeline + intent lock)
# - calculations: validate (vat_pipeline/vat_hooks)
# - period lock MUST run first (hard stop) to prevent any downstream mutation
# -------------------------------------------------------------------

_DIM_ENFORCE = "blue_hesab.bh_core.dimensions_policy.enforce_invoice_dimensions"
_DIM_GL_STAMP = "blue_hesab.bh_core.dimensions_policy.apply_gl_dimensions_from_invoice"

doc_events = {
    "Sales Invoice": {
        "before_validate": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_validate_sales_invoice",
            "blue_hesab.bh_core.vat_returns.before_validate_sales_invoice",
            "blue_hesab.bh_core.vat_pos_intent.bh_before_validate_sales_invoice_pos_intent",
            "blue_hesab.bh_core.vat_pipeline.bh_before_validate_sales_invoice",
        ],
        "validate": [
            "blue_hesab.bh_core.vat_pipeline.bh_validate_sales_invoice",
        ],
        "before_submit": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_submit_sales_invoice",
            _DIM_ENFORCE,
            "blue_hesab.bh_core.vat_pipeline.bh_before_submit_sales_invoice",
        ],
        "on_submit": [
            "blue_hesab.bh_core.legal_hooks.on_submit_sales_invoice",
            _DIM_GL_STAMP,
        ],
        "before_cancel": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_sales_invoice",
            "blue_hesab.bh_core.legal_hooks.before_cancel_sales_invoice",
        ],
        "on_cancel": [
            "blue_hesab.bh_core.legal_hooks.on_cancel_sales_invoice",
        ],
    },

    "Purchase Invoice": {
        "before_validate": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_validate_purchase_invoice",
            "blue_hesab.bh_core.vat_returns.before_validate_purchase_invoice",
            "blue_hesab.bh_core.vat_pipeline.bh_before_validate_purchase_invoice",
        ],
        "validate": [
            "blue_hesab.bh_core.vat_pipeline.bh_validate_purchase_invoice",
        ],
        "before_submit": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_submit_purchase_invoice",
            _DIM_ENFORCE,
            "blue_hesab.bh_core.vat_pipeline.bh_before_submit_purchase_invoice",
        ],
        "on_submit": [
            "blue_hesab.bh_core.legal_hooks.on_submit_purchase_invoice",
            _DIM_GL_STAMP,
        ],
        "before_cancel": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_purchase_invoice",
            "blue_hesab.bh_core.legal_hooks.before_cancel_purchase_invoice",
        ],
        "on_cancel": [
            "blue_hesab.bh_core.legal_hooks.on_cancel_purchase_invoice",
        ],
    },

    # VAT-affecting docs outside SI/PI
    "Journal Entry": {
        "before_submit": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_submit_journal_entry",
        ],
        "before_cancel": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_journal_entry",
        ],
    },

    "Payment Entry": {
        "before_submit": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_submit_payment_entry",
        ],
        "before_cancel": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_payment_entry",
        ],
    },

    "BH Legal Output": {
        "on_update_after_submit": "blue_hesab.bh_core.legal_immutability.on_update_after_submit",
        "on_cancel": "blue_hesab.bh_core.legal_immutability.on_cancel",
        "on_trash": "blue_hesab.bh_core.legal_immutability.on_trash",
    },
}

# JS: فقط یک مسیر (برای جلوگیری از دوباره‌لود و دوباره‌ران شدن)
doctype_js = {
    "Sales Invoice": "public/js/vat_guard_ui.js?v=2470",
    "Purchase Invoice": "public/js/vat_guard_ui.js?v=2470",
}

# -------------------------------------------------------------------
# Safety: ensure DIM hooks exist exactly once (append-only, never break import)
# -------------------------------------------------------------------

def _as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, tuple):
        return list(v)
    return [v]

try:
    # Sales Invoice
    doc_events.setdefault("Sales Invoice", {})
    _si = doc_events["Sales Invoice"]
    _si["before_submit"] = _as_list(_si.get("before_submit"))
    if _DIM_ENFORCE not in _si["before_submit"]:
        _si["before_submit"].append(_DIM_ENFORCE)
    _si["on_submit"] = _as_list(_si.get("on_submit"))
    if _DIM_GL_STAMP not in _si["on_submit"]:
        _si["on_submit"].append(_DIM_GL_STAMP)

    # Purchase Invoice
    doc_events.setdefault("Purchase Invoice", {})
    _pi = doc_events["Purchase Invoice"]
    _pi["before_submit"] = _as_list(_pi.get("before_submit"))
    if _DIM_ENFORCE not in _pi["before_submit"]:
        _pi["before_submit"].append(_DIM_ENFORCE)
    _pi["on_submit"] = _as_list(_pi.get("on_submit"))
    if _DIM_GL_STAMP not in _pi["on_submit"]:
        _pi["on_submit"].append(_DIM_GL_STAMP)

except Exception:
    pass
