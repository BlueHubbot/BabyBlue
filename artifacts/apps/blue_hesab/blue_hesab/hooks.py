# -*- coding: utf-8 -*-
from __future__ import annotations

app_name = "blue_hesab"
app_title = "BlueHesab"
app_publisher = "Blue"
app_description = "BlueHesab (Iran compliance layer)"
app_email = "support@bluehesab.ir"
app_license = "MIT"


# -----------------------------------------------------------------------------
# DOC EVENTS (order matters)
# -----------------------------------------------------------------------------

_SI_BEFORE_VALIDATE = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_validate_sales_invoice",
    "blue_hesab.bh_core.vat_pipeline.before_validate_sales_invoice",
]
_SI_VALIDATE = "blue_hesab.bh_core.vat_pipeline.validate_sales_invoice"
_SI_BEFORE_SUBMIT = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_submit_sales_invoice",
    # VAT-11/13 guard (intent/inclusive mismatch, template flip, etc.)
    "blue_hesab.bh_core.vat_pipeline.before_submit_sales_invoice",
]
_SI_BEFORE_CANCEL = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_sales_invoice",
]

_PI_BEFORE_VALIDATE = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_validate_purchase_invoice",
    "blue_hesab.bh_core.vat_pipeline.before_validate_purchase_invoice",
]
_PI_VALIDATE = "blue_hesab.bh_core.vat_pipeline.validate_purchase_invoice"
_PI_BEFORE_SUBMIT = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_submit_purchase_invoice",
    "blue_hesab.bh_core.vat_pipe_intent_lock.vat11_lock_intent_guard",
    "blue_hesab.bh_core.vat_pipeline.before_submit_purchase_invoice",
]
_PI_BEFORE_CANCEL = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_purchase_invoice",
]

# Legal emit chain (Issue / Cancel / Amend)
_SI_LEGAL_ON_SUBMIT = "blue_hesab.bh_core.legal_hooks.on_submit_sales_invoice"
_SI_LEGAL_ON_CANCEL = "blue_hesab.bh_core.legal_hooks.on_cancel_sales_invoice"
_SI_LEGAL_ON_UPDATE_AFTER_SUBMIT = "blue_hesab.bh_core.legal_hooks.on_update_after_submit_sales_invoice"

_PI_LEGAL_ON_SUBMIT = "blue_hesab.bh_core.legal_hooks.on_submit_purchase_invoice"
_PI_LEGAL_ON_CANCEL = "blue_hesab.bh_core.legal_hooks.on_cancel_purchase_invoice"
_PI_LEGAL_ON_UPDATE_AFTER_SUBMIT = "blue_hesab.bh_core.legal_hooks.on_update_after_submit_purchase_invoice"

# Dimensions enforcement (phase DIM-02: JE + PE)
_JE_BEFORE_SUBMIT = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_submit_journal_entry",
    "blue_hesab.bh_core.dimensions_hook_adapter.enforce_journal_entry_dimensions",
]
_JE_BEFORE_CANCEL = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_journal_entry",
]

_PE_BEFORE_SUBMIT = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_submit_payment_entry",
    "blue_hesab.bh_core.dimensions_hook_adapter.enforce_payment_entry_dimensions",
]
_PE_BEFORE_CANCEL = [
    "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_payment_entry",
]

# Final guard: GL Entry must not be inserted without required dimensions.
_GL_ENTRY_VALIDATE = [
    "blue_hesab.bh_core.dim05_gl_gatekeeper.enforce_gl_entry_dimensions",
]

doc_events = {
    "Sales Invoice": {
        "before_validate": _SI_BEFORE_VALIDATE,
        "validate": _SI_VALIDATE,
        "before_submit": _SI_BEFORE_SUBMIT,
        "before_cancel": _SI_BEFORE_CANCEL,
        "on_submit": _SI_LEGAL_ON_SUBMIT,
        "on_cancel": _SI_LEGAL_ON_CANCEL,
        "on_update_after_submit": _SI_LEGAL_ON_UPDATE_AFTER_SUBMIT,
    },
    "Purchase Invoice": {
        "before_validate": _PI_BEFORE_VALIDATE,
        "validate": _PI_VALIDATE,
        "before_submit": _PI_BEFORE_SUBMIT,
        "before_cancel": _PI_BEFORE_CANCEL,
        "on_submit": _PI_LEGAL_ON_SUBMIT,
        "on_cancel": _PI_LEGAL_ON_CANCEL,
        "on_update_after_submit": _PI_LEGAL_ON_UPDATE_AFTER_SUBMIT,
    },
    "Journal Entry": {
        "before_submit": _JE_BEFORE_SUBMIT,
        "before_cancel": _JE_BEFORE_CANCEL,
    },
    "Payment Entry": {
        "before_submit": _PE_BEFORE_SUBMIT,
        "before_cancel": _PE_BEFORE_CANCEL,
    },
    "GL Entry": {
        "validate": _GL_ENTRY_VALIDATE,
    },
}
