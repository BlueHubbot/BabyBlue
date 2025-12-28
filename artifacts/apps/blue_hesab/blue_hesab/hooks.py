# apps/blue_hesab/blue_hesab/hooks.py
# BlueHesab - Frappe hooks

app_name = "blue_hesab"
app_title = "BlueHesab"
app_publisher = "BlueAPi"
app_description = "BlueHesab Core"
app_email = "dev@blueapi"
app_license = "MIT"

# VAT pipeline (single source of truth)
#
# IMPORTANT:
# - Keep intent/mode enforcement ONLY in before_validate (vat_pipeline).
# - Keep tax calculations ONLY in validate (vat_hooks).
#   This prevents double-running the intent logic and preserves draft behaviour.

doc_events = {
    "Sales Invoice": {
        "before_validate": [
            "blue_hesab.bh_core.vat_pos_intent.bh_before_validate_sales_invoice_pos_intent",
            "blue_hesab.bh_core.vat_pipeline.bh_before_validate_sales_invoice",
        ],
        "validate": [
            "blue_hesab.bh_core.vat_pipeline.bh_validate_sales_invoice",
        ],
    },
    "Purchase Invoice": {
        "before_validate": [
            "blue_hesab.bh_core.vat_pipeline.bh_before_validate_purchase_invoice",
        ],
        "validate": [
            "blue_hesab.bh_core.vat_pipeline.bh_validate_purchase_invoice",
        ],
    },
}


# VAT-19 UI Guard (force-load on Desk; doctype_js sometimes not injected due to meta caching)
app_include_js = [
  "/assets/blue_hesab/js/vat_guard_ui.js?v=2470",
]

# optional: keep doctype_js too (harmless) + cache-bust
doctype_js = {
    "Sales Invoice": "public/js/vat_guard_ui.js?v=2470",
    "Purchase Invoice": "public/js/vat_guard_ui.js?v=2470",
}
