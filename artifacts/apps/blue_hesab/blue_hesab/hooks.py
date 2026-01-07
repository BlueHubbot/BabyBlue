# -*- coding: utf-8 -*-
from __future__ import annotations

app_name = "blue_hesab"
app_title = "Blue Hesab"
app_publisher = "BlueHesab"
app_description = "Iran compliance layer for ERPNext (VAT/TTMS/Modian/Dimensions)"
app_email = "dev@bluehesab"
app_license = "MIT"

# -------------------------------------------------------------
# VAT hooks
# -------------------------------------------------------------

_SI_BEFORE_VALIDATE = "blue_hesab.bh_core.vat_mixed_sales.bh_before_validate_sales_invoice"
_PI_BEFORE_VALIDATE = "blue_hesab.bh_core.vat_mixed_purchase.bh_before_validate_purchase_invoice"

_SI_VALIDATE = "blue_hesab.bh_core.vat_hooks.apply_sales_invoice_vat"
_PI_VALIDATE = "blue_hesab.bh_core.vat_hooks.apply_purchase_invoice_vat"

# -------------------------------------------------------------
# DIM hooks
# -------------------------------------------------------------
_SI_DIM_BEFORE_SUBMIT = "blue_hesab.bh_core.dimensions_policy.enforce_sales_invoice_dimensions"
_PI_DIM_BEFORE_SUBMIT = "blue_hesab.bh_core.dimensions_policy.enforce_purchase_invoice_dimensions"

_JE_DIM_BEFORE_SUBMIT = "blue_hesab.bh_core.dimensions_policy.enforce_journal_entry_dimensions"
_PE_DIM_BEFORE_SUBMIT = "blue_hesab.bh_core.dimensions_policy.enforce_payment_entry_dimensions"
_DIM_ENFORCE_STOCK_ENTRY = "blue_hesab.bh_core.dim05_gl_docs.enforce_stock_entry_dimensions"
_DIM_ENFORCE_STOCK_RECON = "blue_hesab.bh_core.dim05_gl_docs.enforce_stock_reconciliation_dimensions"
_DIM_ENFORCE_DELIVERY_NOTE = "blue_hesab.bh_core.dim05_gl_docs.enforce_delivery_note_dimensions"
_DIM_ENFORCE_PURCHASE_RECEIPT = "blue_hesab.bh_core.dim05_gl_docs.enforce_purchase_receipt_dimensions"
_DIM_ENFORCE_POS_INVOICE = "blue_hesab.bh_core.dim05_gl_docs.enforce_pos_invoice_dimensions"
_DIM_ENFORCE_EXPENSE_CLAIM = "blue_hesab.bh_core.dim05_gl_docs.enforce_expense_claim_dimensions"

_GL_ENTRY_GUARD_DIMS = "blue_hesab.bh_core.dim05_gl_gatekeeper.guard_gl_entry_dimensions"

# -------------------------------------------------------------
# GL stamping & gatekeeper
# -------------------------------------------------------------
_GL_ENTRY_STAMP = "blue_hesab.bh_core.gl_stamp.stamp_gl_entry_from_voucher"
_GL_ENTRY_GATEKEEP = "blue_hesab.bh_core.dim05_gl_gatekeeper.enforce_gl_entry_dimensions"
_GL_ENTRY_AFTER = "blue_hesab.bh_core.gl_postcheck.after_insert_gl_entry"

doc_events = {
    # VAT pipeline
    "Sales Invoice": {"before_validate": [_SI_BEFORE_VALIDATE], "validate": [_SI_VALIDATE], "before_submit": [_SI_DIM_BEFORE_SUBMIT]},
    "Purchase Invoice": {"before_validate": [_PI_BEFORE_VALIDATE], "validate": [_PI_VALIDATE], "before_submit": [_PI_DIM_BEFORE_SUBMIT]},

    # Dimensions for JE/PE
    "Journal Entry": {"before_submit": [_JE_DIM_BEFORE_SUBMIT]},
    "Payment Entry": {"before_submit": [_PE_DIM_BEFORE_SUBMIT]},
    "Stock Entry": {"before_submit": _DIM_ENFORCE_STOCK_ENTRY},
    "Stock Reconciliation": {"before_submit": _DIM_ENFORCE_STOCK_RECON},
    "Delivery Note": {"before_submit": _DIM_ENFORCE_DELIVERY_NOTE},
    "Purchase Receipt": {"before_submit": _DIM_ENFORCE_PURCHASE_RECEIPT},
    "POS Invoice": {"before_submit": _DIM_ENFORCE_POS_INVOICE},
    "Expense Claim": {"before_submit": _DIM_ENFORCE_EXPENSE_CLAIM},

    # GL Entry (stamp + postcheck) — gatekeeper is appended below in try block
    "GL Entry": {"before_insert": [_GL_ENTRY_STAMP, _GL_ENTRY_GUARD_DIMS]},
}

# -------------------------------------------------------------
# LEGAL hooks (invoice-level chain/audit)
# -------------------------------------------------------------
try:
    from blue_hesab.bh_core.legal_hooks import on_sales_invoice_submit, on_sales_invoice_cancel, on_purchase_invoice_submit, on_purchase_invoice_cancel

    # attach to SI/PI submit/cancel (chain/audit)
    doc_events.setdefault("Sales Invoice", {})
    doc_events["Sales Invoice"].setdefault("on_submit", [])
    doc_events["Sales Invoice"].setdefault("on_cancel", [])
    if on_sales_invoice_submit not in doc_events["Sales Invoice"]["on_submit"]:
        doc_events["Sales Invoice"]["on_submit"].append("blue_hesab.bh_core.legal_hooks.on_sales_invoice_submit")
    if on_sales_invoice_cancel not in doc_events["Sales Invoice"]["on_cancel"]:
        doc_events["Sales Invoice"]["on_cancel"].append("blue_hesab.bh_core.legal_hooks.on_sales_invoice_cancel")

    doc_events.setdefault("Purchase Invoice", {})
    doc_events["Purchase Invoice"].setdefault("on_submit", [])
    doc_events["Purchase Invoice"].setdefault("on_cancel", [])
    if on_purchase_invoice_submit not in doc_events["Purchase Invoice"]["on_submit"]:
        doc_events["Purchase Invoice"]["on_submit"].append("blue_hesab.bh_core.legal_hooks.on_purchase_invoice_submit")
    if on_purchase_invoice_cancel not in doc_events["Purchase Invoice"]["on_cancel"]:
        doc_events["Purchase Invoice"]["on_cancel"].append("blue_hesab.bh_core.legal_hooks.on_purchase_invoice_cancel")
except Exception:
    pass

# -------------------------------------------------------------
# Normalize doc_events lists + add DIM-05 hooks safely
# -------------------------------------------------------------
try:
    def _as_list(v):
        if not v:
            return []
        if isinstance(v, (list, tuple)):
            return list(v)
        return [v]

    # Ensure SI/PI VAT hooks are lists
    for _dt in ("Sales Invoice", "Purchase Invoice"):
        _d = doc_events.get(_dt, {})
        for _k in ("before_validate", "validate", "before_submit", "on_submit", "on_cancel"):
            if _k in _d:
                _d[_k] = _as_list(_d.get(_k))

    # Ensure JE/PE before_submit are lists
    for _dt, _fn in (("Journal Entry", _JE_DIM_BEFORE_SUBMIT), ("Payment Entry", _PE_DIM_BEFORE_SUBMIT)):
        doc_events.setdefault(_dt, {})
        _d = doc_events[_dt]
        _d["before_submit"] = _as_list(_d.get("before_submit"))
        if _fn not in _d["before_submit"]:
            _d["before_submit"].append(_fn)

    # DIM-05: enforce header dimensions on additional GL-posting vouchers (before_submit)
    _DIM05_MAP = (
        ("Stock Entry", "blue_hesab.bh_core.dim05_policy.enforce_stock_entry_dimensions"),
        ("Delivery Note", "blue_hesab.bh_core.dim05_policy.enforce_delivery_note_dimensions"),
        ("Purchase Receipt", "blue_hesab.bh_core.dim05_policy.enforce_purchase_receipt_dimensions"),
        ("Expense Claim", "blue_hesab.bh_core.dim05_policy.enforce_expense_claim_dimensions"),
        ("Landed Cost Voucher", "blue_hesab.bh_core.dim05_policy.enforce_landed_cost_voucher_dimensions"),
    )
    for _dt, _fn in _DIM05_MAP:
        doc_events.setdefault(_dt, {})
        _d = doc_events[_dt]
        _d["before_submit"] = _as_list(_d.get("before_submit"))
        if _fn not in _d["before_submit"]:
            _d["before_submit"].append(_fn)

    # GL Entry: stamp + gatekeeper + after_insert
    doc_events.setdefault("GL Entry", {})
    _d = doc_events["GL Entry"]
    _d["before_insert"] = _as_list(_d.get("before_insert"))
    if _GL_ENTRY_STAMP not in _d["before_insert"]:
        _d["before_insert"].append(_GL_ENTRY_STAMP)
    if _GL_ENTRY_GATEKEEP not in _d["before_insert"]:
        _d["before_insert"].append(_GL_ENTRY_GATEKEEP)

    _d["after_insert"] = _as_list(_d.get("after_insert"))
    if _GL_ENTRY_AFTER not in _d["after_insert"]:
        _d["after_insert"].append(_GL_ENTRY_AFTER)

except Exception:
    pass
