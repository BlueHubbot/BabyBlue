# apps/blue_hesab/blue_hesab/bh_core/legal05_smoke.py
from __future__ import annotations

import frappe
from frappe.utils import now

def _bh_copy_doc(doc):
    # Frappe v15+
    try:
        from frappe import copy_doc as _copy_doc
        return _copy_doc(doc)
    except Exception:
        # fallback (اگر روی نسخه‌ای بود که frappe.copy_doc نداشت)
        from frappe.model.document import copy_doc as _copy_doc
        return _copy_doc(doc)


def _get_outputs(reference_doctype: str, reference_name: str, company: str, output_type: str):
    return frappe.get_all(
        "BH Legal Output",
        filters={
            "company": company,
            "output_type": output_type,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "docstatus": 1,
        },
        fields=[
            "name",
            "output_type",
            "correction_reason",
            "previous_output",
            "schema_version",
            "generator_build",
            "generated_at",
            "payload_hash",
            "source_hash",
            "modified",
        ],
        order_by="modified asc",
        limit_page_length=200,
    )


def validate_legal_chain(
    *,
    reference_doctype: str,
    reference_name: str,
    company: str,
    output_type: str = "VAT_INVOICE",
) -> dict:
    """
    Validate LEGAL-05 chain rules for a single reference doc.
    Does NOT modify anything. Read-only validation.
    """
    docstatus = frappe.db.get_value(reference_doctype, reference_name, "docstatus")
    amended_from = frappe.db.get_value(reference_doctype, reference_name, "amended_from")
    outs = _get_outputs(reference_doctype, reference_name, company, output_type)

    issues = [o for o in outs if not o.get("correction_reason")]
    cancels = [o for o in outs if (o.get("correction_reason") or "").upper() == "CANCEL"]
    amends = [o for o in outs if (o.get("correction_reason") or "").upper() == "AMEND"]

    errors: list[str] = []

    # ---- basic sanity ----
    if not outs:
        errors.append("هیچ BH Legal Output برای این سند پیدا نشد.")

    # ---- ISSUE rules ----
    if len(issues) > 1:
        errors.append(f"بیش از یک خروجی اولیه (ISSUE) وجود دارد: {[x['name'] for x in issues]}")
    if issues:
        if issues[0].get("previous_output"):
            errors.append("خروجی اولیه نباید previous_output داشته باشد.")

    # ---- CANCEL rules ----
    if len(cancels) > 1:
        errors.append(f"بیش از یک خروجی CANCEL وجود دارد: {[x['name'] for x in cancels]}")

    if cancels:
        if not issues:
            errors.append("CANCEL وجود دارد ولی ISSUE پیدا نشد.")
        else:
            expected_prev = issues[-1]["name"]
            if cancels[-1].get("previous_output") != expected_prev:
                errors.append(
                    f"previous_output در CANCEL غلط است. expected={expected_prev} got={cancels[-1].get('previous_output')}"
                )

    # ---- AMEND rules ----
    if amends and not amended_from:
        errors.append("AMEND ثبت شده ولی amended_from روی سند خالی است.")

    if amended_from:
        if len(amends) != 1:
            errors.append(f"برای سند اصلاحیه باید دقیقاً یک AMEND باشد. found={len(amends)}")

        # previous_output باید آخرین خروجی سند amended_from باشد
        prev_outs = _get_outputs(reference_doctype, amended_from, company, output_type)
        if not prev_outs:
            errors.append("سند amended_from هیچ خروجی قانونی ندارد.")
        else:
            expected_prev = prev_outs[-1]["name"]
            if amends:
                if amends[0].get("previous_output") != expected_prev:
                    errors.append(
                        f"previous_output در AMEND غلط است. expected={expected_prev} got={amends[0].get('previous_output')}"
                    )

    # ---- docstatus expectation (informative) ----
    notes: list[str] = []
    if int(docstatus or 0) == 2:
        if not cancels:
            notes.append("docstatus=2 است ولی CANCEL output برای این سند دیده نشد (ممکن است هنوز emit نشده باشد).")

    return {
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "company": company,
        "output_type": output_type,
        "docstatus": int(docstatus or 0),
        "amended_from": amended_from,
        "ok": len(errors) == 0,
        "errors": errors,
        "notes": notes,
        "outputs": outs,
    }


def smoke_legal05_sales_cycle(
    *,
    company: str = "BlueAPi",
    qty: float = 1,
    rate: float = 1000000,
    vat_price_mode: str = "Exclusive",
    mutate_amend: bool = True,
) -> dict:
    """
    Full cycle:
      1) create+submit Sales Invoice -> ISSUE output
      2) cancel it -> CANCEL output (previous_output=ISSUE)
      3) create amendment (amended_from=old) + submit -> AMEND output (previous_output=latest old output)
      4) validate chains and return full report
    """
    from frappe import copy_doc
    from blue_hesab.bh_core import smoke_invoices

    created = smoke_invoices.create_sales_invoice_and_submit(
        company=company,
        qty=qty,
        rate=rate,
        vat_price_mode=vat_price_mode,
    )
    si_name = created["sales_invoice"]

    cancelled = smoke_invoices.cancel_doc(doctype="Sales Invoice", name=si_name)

    old_doc = frappe.get_doc("Sales Invoice", si_name)
    new_doc = _bh_copy_doc(old_doc)
    new_doc.amended_from = si_name

    # بهتر است مقدار را کمی تغییر دهیم تا سناریو واقعی AMEND باشد
    if mutate_amend and getattr(new_doc, "items", None):
        try:
            new_doc.items[0].rate = float(new_doc.items[0].rate or 0) + 1000
        except Exception:
            pass

    # برای اینکه insert در دیتابیس conflict نخورد
    new_doc.posting_date = frappe.utils.nowdate()
    if hasattr(new_doc, "posting_time"):
        new_doc.posting_time = frappe.utils.nowtime()

    new_doc.insert(ignore_permissions=True)
    new_doc.submit()
    amend_name = new_doc.name

    # گزارش کامل
    v1 = validate_legal_chain(reference_doctype="Sales Invoice", reference_name=si_name, company=company)
    v2 = validate_legal_chain(reference_doctype="Sales Invoice", reference_name=amend_name, company=company)

    return {
        "ts": now(),
        "company": company,
        "sales_invoice_original": si_name,
        "sales_invoice_amend": amend_name,
        "created": created,
        "cancelled": cancelled,
        "validate_original": v1,
        "validate_amend": v2,
        "ok": bool(v1["ok"] and v2["ok"]),
    }


def smoke_legal05_purchase_cycle(
    *,
    company: str = "BlueAPi",
    qty: float = 1,
    rate: float = 1000000,
    vat_price_mode: str = "Exclusive",
    mutate_amend: bool = True,
) -> dict:
    """
    Same as sales_cycle but for Purchase Invoice.
    """
    from frappe import copy_doc
    from blue_hesab.bh_core import smoke_invoices

    created = smoke_invoices.create_purchase_invoice_and_submit(
        company=company,
        qty=qty,
        rate=rate,
        vat_price_mode=vat_price_mode,
    )
    pi_name = created["purchase_invoice"]

    cancelled = smoke_invoices.cancel_doc(doctype="Purchase Invoice", name=pi_name)

    old_doc = frappe.get_doc("Purchase Invoice", pi_name)
    new_doc = _bh_copy_doc(old_doc)
    new_doc.amended_from = pi_name

    if mutate_amend and getattr(new_doc, "items", None):
        try:
            new_doc.items[0].rate = float(new_doc.items[0].rate or 0) + 1000
        except Exception:
            pass

    new_doc.posting_date = frappe.utils.nowdate()
    if hasattr(new_doc, "posting_time"):
        new_doc.posting_time = frappe.utils.nowtime()

    new_doc.insert(ignore_permissions=True)
    new_doc.submit()
    amend_name = new_doc.name

    v1 = validate_legal_chain(reference_doctype="Purchase Invoice", reference_name=pi_name, company=company)
    v2 = validate_legal_chain(reference_doctype="Purchase Invoice", reference_name=amend_name, company=company)

    return {
        "ts": now(),
        "company": company,
        "purchase_invoice_original": pi_name,
        "purchase_invoice_amend": amend_name,
        "created": created,
        "cancelled": cancelled,
        "validate_original": v1,
        "validate_amend": v2,
        "ok": bool(v1["ok"] and v2["ok"]),
    }
