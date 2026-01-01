from __future__ import annotations
import json
import frappe

def _dump(obj):
    print(json.dumps(obj, ensure_ascii=False))
    return obj

def _ensure_accounts(company: str):
    from blue_hesab.bh_core import vat_admin
    fn = getattr(vat_admin, "ensure_vat_settlement_accounts")
    try:
        return fn(company=company)
    except TypeError:
        return fn()

def debug_vat_settlement_accounts(company: str = "BlueAPi"):
    acc = _ensure_accounts(company)
    payable = acc.get("payable")
    receivable = acc.get("receivable")

    def info(name: str | None):
        if not name:
            return {"name": None, "exists": False}
        row = frappe.db.get_value(
            "Account",
            name,
            ["name","company","is_group","parent_account","root_type","report_type","account_type"],
            as_dict=True,
        )
        return {"name": name, "exists": bool(row), "row": row}

    out = {
        "company": company,
        "payable": info(payable),
        "receivable": info(receivable),
    }
    frappe.db.commit()
    return _dump(out)

def create_vat_period(company: str = "BlueAPi", start: str = "2025-12-01", end: str = "2025-12-31", submit: int = 1):
    acc = _ensure_accounts(company)

    # اگر قبلاً ساخته شده، همان را برگردان
    existing = frappe.db.get_value(
        "BH VAT Period",
        {"company": company, "period_start_date": start, "period_end_date": end, "docstatus": ["!=", 2]},
        "name",
    )
    if existing:
        p = frappe.get_doc("BH VAT Period", existing)
    else:
        p = frappe.new_doc("BH VAT Period")
        p.company = company
        p.period_start_date = start
        p.period_end_date = end

        # مهم: payable/receivable را از خروجی ensure بگیر (نه تایپ دستی)
        p.payable_account = acc.get("payable")
        p.receivable_account = acc.get("receivable")

        # sales/purchase اگر خالی باشند، validate خود DocType از BH Settings پر می‌کند (به شرط اینکه آنجا تنظیم شده باشد)
        p.insert(ignore_permissions=True)

    if int(submit) and int(p.docstatus or 0) == 0:
        p.submit()

    frappe.db.commit()
    p.reload()

    out = {
        "name": p.name,
        "docstatus": p.docstatus,
        "status": p.get("status"),
        "settlement_journal_entry": p.get("settlement_journal_entry"),
        "hashes": {"source": p.get("source_hash"), "payload": p.get("payload_hash")},
        "totals": {
            "sales_vat_total": p.get("sales_vat_total"),
            "purchase_vat_total": p.get("purchase_vat_total"),
            "net_payable": p.get("net_payable"),
            "net_receivable": p.get("net_receivable"),
        },
    }
    return _dump(out)
