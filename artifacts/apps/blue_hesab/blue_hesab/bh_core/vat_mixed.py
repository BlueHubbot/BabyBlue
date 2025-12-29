# blue_hesab/bh_core/vat_mixed.py
# VAT-10: low-level, idempotent normalization ONLY.
# - ensure VAT row exists + has correct account/rate/charge_type
# - sanitize taxes (esp. Purchase)
# - set item_tax_template on rows from Item.bh_item_tax_template / profile mapping
# NO intent inference, NO template selection, NO submit/guard logic.

from __future__ import annotations

from typing import Optional, Tuple

import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_TPL_NONSTR
from blue_hesab.bh_core.exc import raise_bh_vat_error
from blue_hesab.bh_core.vat_tpl_guard import guard_item_tax_template, BH_VAT_E_TPL_NONSTR
from frappe.utils import flt
from blue_hesab.bh_core.company_legal import get_vat_account_and_rate as _get_vat_acc_rate

from blue_hesab.bh_core import get_bh_settings


VAT_CHARGE_TYPE = "On Net Total"


def _company_from_doc(doc) -> Optional[str]:
    return getattr(doc, "company", None) or getattr(doc, "company_name", None)


def _get_company_abbr(company: str) -> str:
    try:
        return frappe.get_cached_value("Company", company, "abbr") or ""
    except Exception:
        return ""


def mixed_template_name(kind: str, company: str, axis: str) -> str:
    """Return the canonical BH MIXED template name for the given company.

    kind: 'sales' | 'purchase'
    axis: 'EXCL' | 'INCL'  (derived from bh_vat_price_mode by vat_pipeline)
    """
    abbr = _get_company_abbr(company)
    axis = (axis or "EXCL").upper()
    if axis not in ("EXCL", "INCL"):
        axis = "EXCL"
    if kind == "sales":
        return f"BH VAT MIXED Sales ({axis}) - {abbr}"
    if kind == "purchase":
        return f"BH VAT MIXED Purchase ({axis}) - {abbr}"
    raise ValueError(f"Unknown kind: {kind}")


def get_vat_account_and_rate(doc, *, kind: str) -> Tuple[Optional[str], float]:
    """Resolve VAT account + rate per-company (BH Company Legal Profile)."""
    company = getattr(doc, "company", None) or (doc.get("company") if hasattr(doc, "get") else None)
    return _get_vat_acc_rate(company, kind=kind)


def _iter_tax_rows(doc):
    return list(getattr(doc, "taxes", []) or [])


def _find_vat_rows(doc, vat_account: str):
    rows = []
    for r in _iter_tax_rows(doc):
        if (r.get("account_head") or "").strip() == (vat_account or "").strip():
            rows.append(r)
    return rows


def ensure_vat_row(doc, vat_account: str, vat_rate: float) -> Optional[object]:
    """Ensure a single VAT tax row exists (idempotent) and normalize its core fields.

    Does NOT touch included_in_print_rate / intent.
    """
    if not vat_account:
        return None

    rows = _find_vat_rows(doc, vat_account)

    if not rows:
        r = doc.append("taxes", {})
        r.account_head = vat_account
        rows = [r]

    # Keep first, drop duplicates with same VAT account
    keep = rows[0]
    if len(rows) > 1:
        for extra in rows[1:]:
            try:
                doc.taxes.remove(extra)
            except Exception:
                pass

    # Normalize required fields (do not infer intent)
    keep.account_head = vat_account
    keep.charge_type = VAT_CHARGE_TYPE
    keep.rate = flt(vat_rate or 0)

    # Purchase-specific niceties (safe if fields exist)
    if hasattr(keep, "add_deduct_tax"):
        keep.add_deduct_tax = keep.add_deduct_tax or "Add"
    if hasattr(keep, "category"):
        keep.category = keep.category or "Total"

    return keep


def sanitize_purchase_taxes(doc) -> None:
    """Purchase invoice taxes can contain rows that make VAT behave oddly.
    Keep this as a normalizer; do not change intent.
    """
    for row in _iter_tax_rows(doc):
        # ERPNext disallows inclusive for Actual; keep it explicit and safe
        if (row.get("charge_type") or "") == "Actual":
            if row.get("included_in_print_rate"):
                row.included_in_print_rate = 0


def set_items_tax_templates(doc) -> None:
    """Set item_tax_template per row from Item.bh_item_tax_template (or fallback via bh_vat_profile)."""
    from blue_hesab.bh_core.vat_item_autofill import resolve_item_tax_template

    company = getattr(doc, "company", None)
    for it in getattr(doc, "items", []) or []:
        item_code = it.get("item_code") or it.get("item") or None
        if not item_code:
            continue

        tpl = resolve_item_tax_template(item_code, company)
        tpl = guard_item_tax_template(
            tpl,
            context="vat_mixed:resolve_item_tax_template",
            extra={"company": getattr(doc, "company", None), "item_code": item_code},
        )
        if tpl:
            it.item_tax_template = tpl


def normalize_sales_invoice(doc) -> None:
    vat_account, vat_rate = get_vat_account_and_rate(doc, kind="sales")
    ensure_vat_row(doc, vat_account, vat_rate)
    set_items_tax_templates(doc)


def normalize_purchase_invoice(doc) -> None:
    vat_account, vat_rate = get_vat_account_and_rate(doc, kind="purchase")
    ensure_vat_row(doc, vat_account, vat_rate)
    sanitize_purchase_taxes(doc)
    set_items_tax_templates(doc)


# Backward-compatible hooks used by vat_pipeline (names kept intentionally)
def bh_before_validate_sales_invoice(doc, method=None):
    normalize_sales_invoice(doc)


def bh_before_validate_purchase_invoice(doc, method=None):
    normalize_purchase_invoice(doc)


# --- CI probe: ensures dict->string normalization never regresses ---
def _bh_ci_probe_tpl_assignment(company: str = "BlueAPi", item_code: str | None = None) -> str:
    """CI probe: ensure the resolver cannot leak non-str values into item_tax_template."""
    from blue_hesab.bh_core.vat_item_autofill import resolve_item_tax_template

    if not item_code:
        item_code = frappe.db.get_value("Item", {"bh_item_tax_template": ["!=", ""]}, "name")
        if not item_code:
            item_code = frappe.db.get_value("Item", {}, "name")

    tpl = resolve_item_tax_template(item_code, company)
    tpl = guard_item_tax_template(
        tpl,
        context="CI_PROBE:resolve_item_tax_template",
        extra={"company": company, "item_code": item_code},
    )
    if not tpl:
        raise_bh_vat_error(BH_VAT_E_TPL_NONSTR, f"CI_PROBE expected non-empty str, got: {repr(tpl)}")
    return tpl
