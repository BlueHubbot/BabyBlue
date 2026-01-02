# -*- coding: utf-8 -*-
import frappe
from frappe.exceptions import ValidationError

def _as_list(x):
    if not x:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

def _doc_event_handlers(doctype: str, event: str):
    doc_events = frappe.get_hooks("doc_events") or {}
    mapping = doc_events.get(doctype) or {}
    return _as_list(mapping.get(event))

def _check_first(doctype: str, event: str, expected_first: str):
    hs = _doc_event_handlers(doctype, event)
    if not hs:
        return False, f"NO_HANDLERS: {doctype}.{event}"
    if hs[0] != expected_first:
        return False, f"ORDER_MISMATCH: got='{hs[0]}' expected='{expected_first}' handlers={hs}"
    return True, None

class _Dummy:
    def __init__(self, **kw):
        self.__dict__.update(kw)
    def get(self, k, default=None):
        return getattr(self, k, default)

def run_v02(company="BlueAPi"):
    out = {"company": company, "total": 0, "passed": 0, "failed": 0, "results": []}

    def push(name, ok, err=None):
        out["total"] += 1
        out["passed"] += 1 if ok else 0
        out["failed"] += 0 if ok else 1
        out["results"].append({"name": name, "pass": bool(ok), "error": err})

    # 1) Hook order: Payment Entry must be guarded
    ok, err = _check_first(
        "Payment Entry", "before_submit",
        "blue_hesab.bh_core.vat_period_lock.bh_before_submit_payment_entry"
    )
    push("LOCK-ORDER-PE-before_submit", ok, err)

    ok, err = _check_first(
        "Payment Entry", "before_cancel",
        "blue_hesab.bh_core.vat_period_lock.bh_before_cancel_payment_entry"
    )
    push("LOCK-ORDER-PE-before_cancel", ok, err)

    # 2) Functional: VAT-touching Payment Entry must be blocked (manual VAT is forbidden)
    try:
        from blue_hesab.bh_core.vat_period_lock import bh_before_submit_payment_entry
        from blue_hesab.bh_core.bh_settings import get_bh_settings  # if you have it
        s = get_bh_settings(company=company)

        # force-touch VAT account
        d = _Dummy(
            company=company,
            posting_date="2025-12-15",
            paid_from=s.default_sales_vat_account,   # touches VAT
            paid_to="Bank - BA",
            deductions=[],
        )
        try:
            bh_before_submit_payment_entry(d, "before_submit")
            push("LOCK-PE-vat-block", False, "EXPECTED_BLOCK_BUT_PASSED")
        except ValidationError:
            push("LOCK-PE-vat-block", True, None)
    except Exception as e:
        push("LOCK-PE-vat-block", False, f"EXCEPTION: {e}")

    return out
