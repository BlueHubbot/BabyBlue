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
_GL_ENTRY_STAMP = "blue_hesab.bh_core.gl_stamp.stamp_gl_entry_from_voucher"
_GL_ROWMAP_JE = "blue_hesab.bh_core.gl_rowmap.prepare_gl_rowmap_for_journal_entry"
_DIM_ENFORCE_JE = "blue_hesab.bh_core.dimensions_policy.enforce_journal_entry_dimensions"
_DIM_ENFORCE_PE = "blue_hesab.bh_core.dimensions_policy.enforce_payment_entry_dimensions"

doc_events = {
    "Sales Invoice": {
        "before_validate": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_validate_sales_invoice",
            "blue_hesab.bh_core.vat_returns.before_validate_sales_invoice",
            "blue_hesab.bh_core.vat_pipeline.bh_before_validate_sales_invoice",
        ],
        "validate": [
            "blue_hesab.bh_core.vat_pipeline.bh_validate_sales_invoice",
        ],
        "before_submit": [
            "blue_hesab.bh_core.vat_period_lock.bh_before_submit_sales_invoice",
            "blue_hesab.bh_core.vat_pipeline.bh_before_submit_sales_invoice",
            "blue_hesab.bh_core.dimensions_policy.enforce_invoice_dimensions",
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

    "GL Entry": {
        "before_insert": _GL_ENTRY_STAMP,
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
# Safety:
# - Invoice GL stamp فقط برای SI/PI (invoice-only)
# - DIM enforce برای SI/PI داخل VAT pipeline است (do NOT inject _DIM_ENFORCE)
# - JE/PE DIM enforce اینجا (DIM-02.A)
# -------------------------------------------------------------------

_DIM_JE_ENFORCE = "blue_hesab.bh_core.dimensions_hook_adapter.enforce_journal_entry_dimensions"
_DIM_PE_ENFORCE = "blue_hesab.bh_core.dimensions_hook_adapter.enforce_payment_entry_dimensions"


def _as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, tuple):
        return list(v)
    return [v]


try:
    # invoice-only GL stamp (SI/PI فقط)
    for _dt in ("Sales Invoice", "Purchase Invoice"):
        doc_events.setdefault(_dt, {})
        _d = doc_events[_dt]
        _d["on_submit"] = _as_list(_d.get("on_submit"))
        if _DIM_GL_STAMP not in _d["on_submit"]:
            _d["on_submit"].append(_DIM_GL_STAMP)

    # JE/PE: enforce at submit-time
    for _dt, _fn in (("Journal Entry", _DIM_JE_ENFORCE), ("Payment Entry", _DIM_PE_ENFORCE)):
        doc_events.setdefault(_dt, {})
        _d = doc_events[_dt]
        _d["before_submit"] = _as_list(_d.get("before_submit"))
        if _fn not in _d["before_submit"]:
            _d["before_submit"].append(_fn)
    # GL Entry: stamp from any voucher (DIM-04)
    doc_events.setdefault("GL Entry", {})
    _d = doc_events["GL Entry"]
    _d["before_insert"] = _as_list(_d.get("before_insert"))
    if _GL_ENTRY_STAMP not in _d["before_insert"]:
        _d["before_insert"].append(_GL_ENTRY_STAMP)
    # JE: build local rowmap for GL line-aware stamp (DIM-04)
    doc_events.setdefault("Journal Entry", {})
    _d = doc_events["Journal Entry"]
    _d["before_submit"] = _as_list(_d.get("before_submit"))
    if _GL_ROWMAP_JE not in _d["before_submit"]:
        _d["before_submit"].append(_GL_ROWMAP_JE)
    # JE: enforce dims on submit (DIM-02.B)
    doc_events.setdefault("Journal Entry", {})
    _d = doc_events["Journal Entry"]
    _d["before_submit"] = _as_list(_d.get("before_submit"))
    if _DIM_ENFORCE_JE not in _d["before_submit"]:
        _d["before_submit"].insert(0, _DIM_ENFORCE_JE)  # enforce first
    # PE: enforce dims on submit (DIM-02.B)
    doc_events.setdefault("Payment Entry", {})
    _d = doc_events["Payment Entry"]
    _d["before_submit"] = _as_list(_d.get("before_submit"))
    if _DIM_ENFORCE_PE not in _d["before_submit"]:
        _d["before_submit"].insert(0, _DIM_ENFORCE_PE)

except Exception:
    pass
