from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any, Dict, Optional

import frappe

from blue_hesab.bh_core import get_bh_settings


def _s(v) -> str:
    return (v or "").strip()


def _f(v) -> float:
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _iso(d) -> str:
    if not d:
        return ""
    if isinstance(d, (datetime, date)):
        return d.strftime("%Y-%m-%d")
    return _s(d)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _party_from_invoice(doc) -> Dict[str, Any]:
    if doc.doctype == "Sales Invoice":
        party_type = "Customer"
        party = _s(getattr(doc, "customer", None))
        party_name = _s(getattr(doc, "customer_name", None))
    elif doc.doctype == "Purchase Invoice":
        party_type = "Supplier"
        party = _s(getattr(doc, "supplier", None))
        party_name = _s(getattr(doc, "supplier_name", None))
    else:
        party_type, party, party_name = "", "", ""

    info: Dict[str, Any] = {
        "party_type": party_type,
        "party": party,
        "party_name": party_name,
        "national_id": "",
        "economic_code": "",
        "postal_code": "",
        "city": "",
        "province": "",
        "address": "",
    }

    if not party_type or not party:
        return info

    try:
        pdoc = frappe.get_doc(party_type, party)
        for fn in ("tax_id", "tax_id_number", "national_id", "company_registration", "registration_no", "vat_number"):
            if getattr(pdoc, fn, None):
                val = _s(getattr(pdoc, fn, None))
                if "national" in fn or fn in ("registration_no",):
                    info["national_id"] = info["national_id"] or val
                if "tax" in fn or "economic" in fn:
                    info["economic_code"] = info["economic_code"] or val
    except Exception:
        pass

    try:
        addr_name = frappe.db.get_value(
            "Dynamic Link",
            {"link_doctype": party_type, "link_name": party, "parenttype": "Address"},
            "parent",
        )
        if addr_name:
            addr = frappe.get_doc("Address", addr_name)
            info["postal_code"] = _s(getattr(addr, "pincode", None))
            info["city"] = _s(getattr(addr, "city", None))
            info["province"] = _s(getattr(addr, "state", None))
            info["address"] = _s(getattr(addr, "address_line1", None))
    except Exception:
        pass

    return info


def _vat_totals(doc) -> Dict[str, float]:
    s = get_bh_settings()
    vat_acc = _s(s.get("default_sales_vat_account")) if doc.doctype == "Sales Invoice" else _s(s.get("default_purchase_vat_account"))

    vat = 0.0
    for t in list(getattr(doc, "taxes", None) or []):
        if vat_acc and _s(getattr(t, "account_head", None)) == vat_acc:
            vat += _f(getattr(t, "tax_amount", None))

    net = _f(getattr(doc, "base_net_total", None)) or _f(getattr(doc, "net_total", None))
    grand = _f(getattr(doc, "base_grand_total", None)) or _f(getattr(doc, "grand_total", None))
    if grand == 0 and net:
        grand = net + vat

    return {"net_total": net, "vat_total": vat, "grand_total": grand}


def build_modian_payload_v1(
    doc,
    *,
    company: str,
    event_type: str,
    correction_reason: Optional[str],
    previous_output: Optional[str],
) -> Dict[str, Any]:
    s = get_bh_settings()
    if not int(s.get("enable_modian") or 0):
        frappe.throw("مودیان در تنظیمات BlueHesab غیرفعال است.", frappe.ValidationError)

    device_id = _s(s.get("modian_device_id"))
    profile_id = _s(s.get("modian_profile_id"))
    org_nid = _s(s.get("ttms_company_national_id"))
    org_ec = _s(s.get("ttms_company_economic_code"))

    if not device_id or not profile_id:
        frappe.throw("برای مودیان، فیلدهای «Device ID» و «Profile ID» در BH Settings الزامی هستند.", frappe.ValidationError)
    if not org_nid or not org_ec:
        frappe.throw("برای مودیان، فیلدهای «شناسه ملی شرکت» و «کد اقتصادی شرکت» الزامی هستند.", frappe.ValidationError)

    inv_date = _iso(getattr(doc, "posting_date", None) or getattr(doc, "transaction_date", None))
    party = _party_from_invoice(doc)
    totals = _vat_totals(doc)

    uid_seed = json.dumps(
        {
            "company": company,
            "doctype": doc.doctype,
            "name": doc.name,
            "event_type": event_type,
            "correction_reason": correction_reason,
            "previous_output": previous_output,
            "grand_total": totals["grand_total"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    invoice_uid = _sha(uid_seed)[:32]

    payload = {
        "format": "BH-MODIAN-EINV-V1",
        "device_id": device_id,
        "profile_id": profile_id,
        "invoice_uid": invoice_uid,
        "event": {"type": event_type, "correction_reason": correction_reason, "previous_output": previous_output},
        "seller": {"company": company, "national_id": org_nid, "economic_code": org_ec},
        "buyer": {
            "party_type": party.get("party_type"),
            "party": party.get("party"),
            "party_name": party.get("party_name"),
            "national_id": party.get("national_id"),
            "economic_code": party.get("economic_code"),
            "postal_code": party.get("postal_code"),
            "city": party.get("city"),
            "province": party.get("province"),
            "address": party.get("address"),
        },
        "invoice": {"doctype": doc.doctype, "name": doc.name, "date": inv_date, "currency": "IRR"},
        "totals": totals,
        "lines": [],
        "generated_by": _s(frappe.session.user),
        "generated_at": frappe.utils.now(),  # type: ignore[attr-defined]
    }

    for it in list(getattr(doc, "items", None) or []):
        qty = _f(getattr(it, "qty", None))
        rate = _f(getattr(it, "base_rate", None)) or _f(getattr(it, "rate", None))
        amt = _f(getattr(it, "base_amount", None)) or _f(getattr(it, "amount", None))
        tpl = _s(getattr(it, "item_tax_template", None))
        payload["lines"].append(
            {
                "item_code": _s(getattr(it, "item_code", None)),
                "item_name": _s(getattr(it, "item_name", None)),
                "qty": qty,
                "rate": rate,
                "amount": amt,
                "item_tax_template": tpl,
                "uom": _s(getattr(it, "uom", None)),
            }
        )

    einv = frappe.get_doc(
        {
            "doctype": "BH E-Invoice Document",
            "company": company,
            "status": "Generated",
            "modian_status": "Pending",
            "modian_invoice_uid": invoice_uid,
            "is_return": 1 if event_type == "cancel" else 0,
            "source_doctype": doc.doctype,
            "source_name": doc.name,
            "request_payload": json.dumps(payload, ensure_ascii=False, sort_keys=True),
            "total_amount": totals["grand_total"],
            "tax_amount": totals["vat_total"],
            "buyer_name": party.get("party_name"),
            "buyer_tax_id": party.get("economic_code") or party.get("national_id"),
            "issue_date": inv_date,
            "lines": [
                {
                    "item_code": ln.get("item_code"),
                    "item_name": ln.get("item_name"),
                    "qty": ln.get("qty"),
                    "rate": ln.get("rate"),
                    "amount": ln.get("amount"),
                    "tax_rate": 0.0,
                    "tax_amount": 0.0,
                    "total_amount": ln.get("amount"),
                    "extra_json": json.dumps({"item_tax_template": ln.get("item_tax_template")}, ensure_ascii=False, sort_keys=True),
                }
                for ln in payload["lines"]
            ],
        }
    )
    einv.insert(ignore_permissions=True)

    try:
        einv.submit()
    except Exception:
        pass

    return {**payload, "e_invoice_document": {"doctype": "BH E-Invoice Document", "name": einv.name, "status": einv.status, "modian_status": einv.modian_status, "docstatus": getattr(einv, "docstatus", 0)}}
