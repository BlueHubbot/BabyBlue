from __future__ import annotations

import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
from frappe.utils import flt

from blue_hesab.bh_core import get_bh_settings


def _upsert_custom_field(dt: str, fieldname: str, **props):
    name = frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": fieldname}, "name")
    if name:
        cf = frappe.get_doc("Custom Field", name)
        changed = False
        for k, v in props.items():
            if cf.get(k) != v:
                cf.set(k, v)
                changed = True
        if changed:
            cf.save(ignore_permissions=True)
        return {"dt": dt, "fieldname": fieldname, "created": False, "updated": changed}

    cf = frappe.new_doc("Custom Field")
    cf.dt = dt
    cf.fieldname = fieldname
    for k, v in props.items():
        cf.set(k, v)
    cf.insert(ignore_permissions=True)
    return {"dt": dt, "fieldname": fieldname, "created": True, "updated": True}


def _upsert_translation(source: str, translated: str, lang: str = "fa"):
    name = frappe.db.get_value("Translation", {"language": lang, "source_text": source}, "name")
    if name:
        doc = frappe.get_doc("Translation", name)
        if (doc.translated_text or "") != translated:
            doc.translated_text = translated
            doc.save(ignore_permissions=True)
            return {"source": source, "updated": True}
        return {"source": source, "updated": False}

    doc = frappe.new_doc("Translation")
    doc.language = lang
    doc.source_text = source
    doc.translated_text = translated
    doc.insert(ignore_permissions=True)
    return {"source": source, "updated": True}


def ensure_vat_ui_fields():
    # Select values remain EN (stable logic), UI will be FA via label + translations
    label_fa = "نوع قیمت‌گذاری مالیات"
    desc_fa = "اگر «شامل مالیات» باشد، VAT داخل قیمت محاسبه می‌شود (INCL). در غیر اینصورت VAT خارج از قیمت است (EXCL)."

    common = dict(
        fieldtype="Select",
        label=label_fa,
        options="Exclusive\nInclusive",
        default="Exclusive",
        insert_after="taxes_and_charges",
        reqd=0,
        read_only=0,
        allow_on_submit=0,
        print_hide=0,
        in_list_view=0,
        in_standard_filter=0,
        description=desc_fa,
        read_only_depends_on="eval:doc.docstatus==1",
    )

    # VAT-26: explicit Inclusive Intent (prevents accidental Inclusive leak on normal invoices)
    intent_label_fa = "قصد قیمت شامل مالیات"
    intent_desc_fa = (
        "برای استفاده از «شامل مالیات (INCL)» در فاکتورهای عادی (غیر POS)، Intent صریح لازم است. "
        "این تیک فقط نقش «اجازه/Intent» دارد و جایگزین انتخاب قالب یا POS نیست."
    )

    intent_common = dict(
        fieldtype="Check",
        label=intent_label_fa,
        default=0,
        insert_after="bh_vat_price_mode",
        reqd=0,
        read_only=0,
        allow_on_submit=0,
        print_hide=1,
        in_list_view=0,
        in_standard_filter=0,
        description=intent_desc_fa,
        read_only_depends_on="eval:doc.docstatus==1",
    )

    out = []
    out.append(_upsert_custom_field("Sales Invoice", "bh_vat_price_mode", **common))
    out.append(_upsert_custom_field("Purchase Invoice", "bh_vat_price_mode", **common))

    out.append(_upsert_custom_field("Sales Invoice", "bh_vat_inclusive_intent", **intent_common))
    out.append(_upsert_custom_field("Purchase Invoice", "bh_vat_inclusive_intent", **intent_common))

    # Make sure options show FA too
    t = []
    t.append(_upsert_translation("Exclusive", "خارج از قیمت (بدون مالیات)", "fa"))
    t.append(_upsert_translation("Inclusive", "شامل مالیات", "fa"))
    # (Label is already FA, but keep this for safety if you ever switch label to EN)
    t.append(_upsert_translation("VAT Price Mode", "نوع قیمت‌گذاری مالیات", "fa"))

    return {"custom_fields": out, "translations": t}


def _company_and_abbr(company: str | None):
    if company:
        abbr = (frappe.get_cached_value("Company", company, "abbr") or "").strip()
        return company, abbr

    s = get_bh_settings()
    c = (s.get("default_company") or "").strip()
    if c and frappe.db.exists("Company", c):
        abbr = (frappe.get_cached_value("Company", c, "abbr") or "").strip()
        return c, abbr

    c = frappe.db.get_value("Company", {}, "name")
    if not c:
        raise Exception("No Company found.")
    abbr = (frappe.get_cached_value("Company", c, "abbr") or "").strip()
    return c, abbr


def _ensure_sales_template(company: str, abbr: str, included_in_print_rate: int):
    s = get_bh_settings()
    vat_account = getattr(s, "default_sales_vat_account", None)
    vat_rate = flt(getattr(s, "default_sales_vat_rate", 0) or 0)

    axis = "INCL" if int(included_in_print_rate or 0) else "EXCL"
    name = f"BH VAT MIXED Sales ({axis}) - {abbr}"

    exists = frappe.db.exists("Sales Taxes and Charges Template", name)

    if exists:
        tpl = frappe.get_doc("Sales Taxes and Charges Template", name)
        created = False
    else:
        tpl = frappe.new_doc("Sales Taxes and Charges Template")
        tpl.name = name
        created = True

    tpl.title = name
    tpl.company = company

    # Upsert: replace rows to avoid stale / silent drift
    tpl.set("taxes", [])
    tpl.append("taxes", {
        "charge_type": "On Net Total",
        "account_head": vat_account,
        "rate": vat_rate,
        "included_in_print_rate": 1 if int(included_in_print_rate or 0) else 0,
        "description": "BH VAT MIXED",
    })

    if created:
        tpl.insert(ignore_permissions=True)
    else:
        tpl.save(ignore_permissions=True)

    return {"name": name, "created": created}


def _ensure_purchase_template(company: str, abbr: str, included_in_print_rate: int):
    s = get_bh_settings()
    vat_account = getattr(s, "default_purchase_vat_account", None)
    vat_rate = flt(getattr(s, "default_purchase_vat_rate", 0) or 0)

    axis = "INCL" if int(included_in_print_rate or 0) else "EXCL"
    name = f"BH VAT MIXED Purchase ({axis}) - {abbr}"

    exists = frappe.db.exists("Purchase Taxes and Charges Template", name)

    if exists:
        tpl = frappe.get_doc("Purchase Taxes and Charges Template", name)
        created = False
    else:
        tpl = frappe.new_doc("Purchase Taxes and Charges Template")
        tpl.name = name
        created = True

    tpl.title = name
    tpl.company = company

    tpl.set("taxes", [])
    tpl.append("taxes", {
        "charge_type": "On Net Total",
        "account_head": vat_account,
        "rate": vat_rate,
        "included_in_print_rate": 1 if int(included_in_print_rate or 0) else 0,
        "description": "BH VAT MIXED",
        # purchase extras (safe)
        "add_deduct_tax": "Add",
        "category": "Total",
    })

    if created:
        tpl.insert(ignore_permissions=True)
    else:
        tpl.save(ignore_permissions=True)

    return {"name": name, "created": created}


def ensure_mixed_templates(company: str | None = None):
    company, abbr = _company_and_abbr(company)
    out = []
    out.append(_ensure_sales_template(company, abbr, 0))
    out.append(_ensure_sales_template(company, abbr, 1))
    out.append(_ensure_purchase_template(company, abbr, 0))
    out.append(_ensure_purchase_template(company, abbr, 1))
    return {"company": company, "abbr": abbr, "templates": out}


@frappe.whitelist()
def ensure_vat_ui_and_templates(company: str | None = None):
    a = ensure_vat_ui_fields()
    b = ensure_mixed_templates(company=company)
    frappe.clear_cache()
    return {"ok": True, "ui": a, "templates": b}
