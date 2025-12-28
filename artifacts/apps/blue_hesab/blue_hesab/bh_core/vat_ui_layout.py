import frappe

from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
# VAT-11 UI placement rules (minimal, safe)
# Goal: ensure bh_vat_price_mode appears in the intended section (Taxes by default)
# and remains read-only after submit (handled by Custom Field props in vat_setup).


def _set_custom_field(dt: str, fieldname: str, changes: dict) -> dict:
    cf_name = frappe.db.get_value(
        "Custom Field", {"dt": dt, "fieldname": fieldname}, "name"
    )
    if not cf_name:
        return {"dt": dt, "fieldname": fieldname, "exists": False, "updated": False}

    cf = frappe.get_doc("Custom Field", cf_name)

    updated = False
    for k, v in changes.items():
        if getattr(cf, k, None) != v:
            setattr(cf, k, v)
            updated = True

    if updated:
        cf.save(ignore_permissions=True)

    return {"dt": dt, "fieldname": fieldname, "exists": True, "updated": updated}


def _has_field(dt: str, fieldname: str) -> bool:
    try:
        m = frappe.get_meta(dt)
        return bool(m.get_field(fieldname))
    except Exception:
        return False


@frappe.whitelist()
def apply_vat_ui_layout(target: str = "taxes") -> dict:
    """
    target:
      - "taxes": place right after taxes_and_charges
      - "accounting": place near receivable/payable accounts
    """

    target = (target or "taxes").strip().lower()
    if target not in ("taxes", "accounting"):
        target = "taxes"

    if target == "taxes":
        si_after = "taxes_and_charges"
        pi_after = "taxes_and_charges"
    else:
        si_after = "debit_to"
        pi_after = "credit_to"

    # Safety: if the chosen anchor does not exist (due to customization),
    # fallback to a stable accounting anchor, then finally a generic core field.
    if not _has_field("Sales Invoice", si_after):
        si_after = "debit_to" if _has_field("Sales Invoice", "debit_to") else "company"

    if not _has_field("Purchase Invoice", pi_after):
        pi_after = "credit_to" if _has_field("Purchase Invoice", "credit_to") else "company"

    changes = [
        # Sales Invoice placement
        ("Sales Invoice", "bh_vat_price_mode", {"insert_after": si_after}),
        # Purchase Invoice placement
        ("Purchase Invoice", "bh_vat_price_mode", {"insert_after": pi_after}),
    ]

    out = {"target": target, "changes": []}
    for dt, fn, payload in changes:
        out["changes"].append(_set_custom_field(dt, fn, payload))

    # cache refresh helps Desk layout immediately
    try:
        frappe.clear_cache()
    except Exception:
        pass

    return out
