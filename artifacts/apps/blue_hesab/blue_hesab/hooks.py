# -*- coding: utf-8 -*-
# BlueHesab - Frappe hooks

app_name = "blue_hesab"
app_title = "BlueHesab"
app_publisher = "BlueAPi"
app_description = "BlueHesab Core"
app_email = "dev@blueapi"
app_license = "MIT"

# VAT pipeline (single source of truth)
# - intent/mode enforcement: before_validate (vat_pipeline)
# - calculations: validate (vat_pipeline/vat_hooks)

doc_events = {
  "Sales Invoice": {
    "before_validate": [
      "blue_hesab.bh_core.vat_pos_intent.bh_before_validate_sales_invoice_pos_intent",
      "blue_hesab.bh_core.vat_pipeline.bh_before_validate_sales_invoice",
    ],
    "validate": [
      "blue_hesab.bh_core.vat_pipeline.bh_validate_sales_invoice",
    ],

    # ✅ VAT-16: Period Lock + VAT final enforcement on submit
    "before_submit": [
      "blue_hesab.bh_core.vat_period_lock.bh_before_submit_sales_invoice",
      "blue_hesab.bh_core.vat_pipeline.bh_before_submit_sales_invoice",
    ],

    "on_submit": [
      "blue_hesab.bh_core.legal_hooks.on_submit_sales_invoice",
      "blue_hesab.bh_core.dimensions_hook_adapter.apply_gl_dimensions_from_invoice",
    ],

    # ✅ VAT-16: must run BEFORE legal side effects
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
      "blue_hesab.bh_core.vat_pipeline.bh_before_validate_purchase_invoice",
    ],
    "validate": [
      "blue_hesab.bh_core.vat_pipeline.bh_validate_purchase_invoice",
    ],

    # ✅ VAT-16: Period Lock + VAT final enforcement on submit
    "before_submit": [
      "blue_hesab.bh_core.vat_period_lock.bh_before_submit_purchase_invoice",
      "blue_hesab.bh_core.vat_pipeline.bh_before_submit_purchase_invoice",
    ],

    "on_submit": [
      "blue_hesab.bh_core.legal_hooks.on_submit_purchase_invoice",
      "blue_hesab.bh_core.dimensions_hook_adapter.apply_gl_dimensions_from_invoice",
    ],

    # ✅ VAT-16: must run BEFORE legal side effects
    "before_cancel": [
      "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_purchase_invoice",
      "blue_hesab.bh_core.legal_hooks.before_cancel_purchase_invoice",
    ],

    "on_cancel": [
      "blue_hesab.bh_core.legal_hooks.on_cancel_purchase_invoice",
    ],
  },

  "BH Legal Output": {
    "on_update_after_submit": "blue_hesab.bh_core.legal_immutability.on_update_after_submit",
    "on_cancel": "blue_hesab.bh_core.legal_immutability.on_cancel",
    "on_trash": "blue_hesab.bh_core.legal_immutability.on_trash",
  },

  # BH Legal Output immutability (NNG-02)
  "BH Legal Output": {
    "on_update_after_submit": "blue_hesab.bh_core.legal_immutability.on_update_after_submit",
    "on_cancel": "blue_hesab.bh_core.legal_immutability.on_cancel",
    "on_trash": "blue_hesab.bh_core.legal_immutability.on_trash",
  },
}

# VAT-19 UI Guard (force-load on Desk; doctype_js sometimes not injected due to meta caching)
app_include_js = [
  "/assets/blue_hesab/js/vat_guard_ui.js?v=2470",
]

doctype_js = {
  "Sales Invoice": "public/js/vat_guard_ui.js?v=2470",
  "Purchase Invoice": "public/js/vat_guard_ui.js?v=2470",
}