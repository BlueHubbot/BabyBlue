from __future__ import annotations

import csv
import io
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


def _now() -> str:
    return frappe.utils.now()  # type: ignore[attr-defined]


def _get_vat_account(doc) -> Optional[str]:
    s = get_bh_settings()
    if doc.doctype == "Sales Invoice":
        return _s(s.get("default_sales_vat_account"))
    if doc.doctype == "Purchase Invoice":
        return _s(s.get("default_purchase_vat_account"))
    return None


def _get_vat_item_map(doc) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    vat_account = _get_vat_account(doc)

    taxes = list(getattr(doc, "taxes", None) or [])
    for t in taxes:
        acc = _s(getattr(t, "account_head", None))
        if vat_account and acc != vat_account:
            continue
        raw = getattr(t, "item_wise_tax_detail", None)
        if not raw:
            continue
        try:
            m = json.loads(raw) if isinstance(raw, str) else raw
            for k, v in (m or {}).items():
                if not isinstance(v, (list, tuple)) or len(v) < 2:
                    continue
                rate = _f(v[0])
                tax = _f(v[1])
                cur = out.setdefault(str(k), {"rate": 0.0, "tax": 0.0})
                cur["rate"] = max(cur["rate"], abs(rate))
                cur["tax"] += tax
        except Exception:
            continue
    return out


def _party_info_from_invoice(doc) -> Dict[str, Any]:
    if doc.doctype == "Sales Invoice":
        party_type = "Customer"
        party = _s(getattr(doc, "customer", None))
    elif doc.doctype == "Purchase Invoice":
        party_type = "Supplier"
        party = _s(getattr(doc, "supplier", None))
    else:
        party_type = ""
        party = ""

    info: Dict[str, Any] = {
        "party_type": party_type,
        "party": party,
        "party_name": _s(getattr(doc, "customer_name", None)) or _s(getattr(doc, "supplier_name", None)),
        "party_national_id": "",
        "party_economic_code": "",
        "party_postal_code": "",
        "party_city": "",
        "party_province": "",
    }

    if not party_type or not party:
        return info

    try:
        pdoc = frappe.get_doc(party_type, party)
        for fn in ("tax_id", "tax_id_number", "national_id", "company_registration", "registration_no", "vat_number"):
            if getattr(pdoc, fn, None):
                val = _s(getattr(pdoc, fn, None))
                if "national" in fn or fn in ("registration_no",):
                    info["party_national_id"] = info["party_national_id"] or val
                if "tax" in fn or "economic" in fn:
                    info["party_economic_code"] = info["party_economic_code"] or val
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
            info["party_postal_code"] = _s(getattr(addr, "pincode", None))
            info["party_city"] = _s(getattr(addr, "city", None))
            info["party_province"] = _s(getattr(addr, "state", None))
    except Exception:
        pass

    return info


def _compute_totals(doc, event_type: str) -> Dict[str, float]:
    item_tax = _get_vat_item_map(doc)
    taxable = 0.0
    exempt = 0.0
    vat = 0.0

    for it in list(getattr(doc, "items", None) or []):
        amt = _f(getattr(it, "base_amount", None)) or _f(getattr(it, "amount", None))
        tpl = _s(getattr(it, "item_tax_template", None))
        is_exempt = ("EXEMPT" in tpl.upper())
        if is_exempt:
            exempt += amt
        else:
            taxable += amt
            rowname = _s(getattr(it, "name", None))
            if rowname and rowname in item_tax:
                vat += _f(item_tax[rowname].get("tax"))

    total = taxable + exempt + vat

    if event_type == "cancel":
        taxable *= -1
        exempt *= -1
        vat *= -1
        total *= -1

    return {
        "taxable_base": taxable,
        "exempt_base": exempt,
        "vat_amount": vat,
        "duties_amount": 0.0,
        "total_amount": total,
    }


def _render_ttms_csv(ttms_doc) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "row_no",
            "row_type",
            "invoice_number",
            "invoice_date",
            "party_type",
            "party",
            "party_name",
            "party_national_id",
            "party_economic_code",
            "taxable_base",
            "exempt_base",
            "vat_amount",
            "duties_amount",
            "total_amount",
            "currency",
            "conversion_rate",
            "source_doctype",
            "source_name",
        ]
    )
    for i, ln in enumerate(ttms_doc.get("lines") or [], start=1):
        w.writerow(
            [
                i,
                ln.get("row_type"),
                ln.get("invoice_number"),
                ln.get("invoice_date"),
                ln.get("party_type"),
                ln.get("party"),
                ln.get("party_name"),
                ln.get("party_national_id"),
                ln.get("party_economic_code"),
                ln.get("taxable_base"),
                ln.get("exempt_base"),
                ln.get("vat_amount"),
                ln.get("duties_amount"),
                ln.get("total_amount"),
                ln.get("currency"),
                ln.get("conversion_rate"),
                ttms_doc.get("source_doctype"),
                ttms_doc.get("source_name"),
            ]
        )
    return buf.getvalue()


def build_ttms_export_payload_v1(
    doc,
    *,
    company: str,
    event_type: str,
    correction_reason: Optional[str],
    previous_output: Optional[str],
) -> Dict[str, Any]:
    s = get_bh_settings()
    if not int(s.get("enable_ttms") or 0):
        frappe.throw("TTMS در تنظیمات BlueHesab غیرفعال است.", frappe.ValidationError)

    seller_nid = _s(s.get("ttms_company_national_id"))
    seller_ec = _s(s.get("ttms_company_economic_code"))
    threshold = _f(s.get("ttms_threshold_amount"))

    if not seller_nid or not seller_ec:
        frappe.throw("فیلدهای «شناسه ملی شرکت (TTMS)» و «کد اقتصادی شرکت (TTMS)» در BH Settings الزامی هستند.", frappe.ValidationError)

    inv_no = _s(getattr(doc, "name", None))
    inv_date = _iso(getattr(doc, "posting_date", None) or getattr(doc, "transaction_date", None))

    party_info = _party_info_from_invoice(doc)
    totals = _compute_totals(doc, event_type)

    is_below_threshold = abs(totals["total_amount"]) <= threshold if threshold > 0 else False

    if not is_below_threshold and not (_s(party_info.get("party_national_id")) or _s(party_info.get("party_economic_code"))):
        frappe.throw("برای TTMS، شناسه/کد اقتصادی طرف مقابل الزامی است (بالای سقف مقرر).", frappe.ValidationError)

    row_type = "Sales" if doc.doctype == "Sales Invoice" else "Purchase" if doc.doctype == "Purchase Invoice" else "Sales"

    ttms = frappe.get_doc(
        {
            "doctype": "BH TTMS Document",
            "company": company,
            "status": "Generated",
            "period_type": "Invoice",
            "source_doctype": doc.doctype,
            "source_name": doc.name,
            "total_lines": 1,
            "total_amount": totals["total_amount"],
            "extra_json": json.dumps(
                {
                    "format_version": "BH-TTMS-INVOICE-V1",
                    "event_type": event_type,
                    "correction_reason": correction_reason,
                    "previous_output": previous_output,
                    "seller_national_id": seller_nid,
                    "seller_economic_code": seller_ec,
                    "threshold_amount": threshold,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            "lines": [
                {
                    "row_type": row_type,
                    "invoice_number": inv_no,
                    "invoice_date": inv_date,
                    "party_type": party_info.get("party_type"),
                    "party": party_info.get("party"),
                    "party_name": party_info.get("party_name"),
                    "party_national_id": party_info.get("party_national_id"),
                    "party_economic_code": party_info.get("party_economic_code"),
                    "party_postal_code": party_info.get("party_postal_code"),
                    "party_city": party_info.get("party_city"),
                    "party_province": party_info.get("party_province"),
                    "taxable_base": totals["taxable_base"],
                    "exempt_base": totals["exempt_base"],
                    "vat_amount": totals["vat_amount"],
                    "duties_amount": totals["duties_amount"],
                    "total_amount": totals["total_amount"],
                    "is_below_threshold": 1 if is_below_threshold else 0,
                    "currency": "IRR",
                    "conversion_rate": 1.0,
                    "extra_json": json.dumps(
                        {"event_type": event_type, "correction_reason": correction_reason, "previous_output": previous_output},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                }
            ],
        }
    )
    ttms.insert(ignore_permissions=True)

    csv_content = _render_ttms_csv(ttms)
    file_name = f"TTMS_{company}_{doc.doctype}_{doc.name}_{event_type}.csv".replace(" ", "_")
    fdoc = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": file_name,
            "content": csv_content,
            "is_private": 1,
            "attached_to_doctype": "BH TTMS Document",
            "attached_to_name": ttms.name,
            "attached_to_field": "export_file",
        }
    )
    fdoc.save(ignore_permissions=True)

    ttms.export_file = fdoc.file_url
    ttms.export_format = "CSV"
    ttms.export_generated_at = frappe.utils.now_datetime()  # type: ignore[attr-defined]
    ttms.status = "Exported"
    ttms.export_note = f"BH TTMS INVOICE V1 | event={event_type}"
    ttms.save(ignore_permissions=True)

    try:
        ttms.submit()
    except Exception:
        pass

    return {
        "format": "BH-TTMS-INVOICE-V1",
        "event": {"type": event_type, "correction_reason": correction_reason, "previous_output": previous_output},
        "seller": {"company": company, "national_id": seller_nid, "economic_code": seller_ec},
        "invoice": {"doctype": doc.doctype, "name": doc.name, "posting_date": inv_date},
        "totals": totals,
        "ttms_document": {"doctype": "BH TTMS Document", "name": ttms.name, "export_file": ttms.export_file, "status": ttms.status, "docstatus": getattr(ttms, "docstatus", 0)},
        "generated_at": _now(),
        "generated_by": _s(frappe.session.user),
    }
