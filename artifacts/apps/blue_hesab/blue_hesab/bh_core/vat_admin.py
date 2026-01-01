from __future__ import annotations
import frappe
from frappe import _
import frappe
from frappe.utils import flt

def _ensure_company_abbr(company: str, fallback: str = "BA") -> str:
    abbr = frappe.db.get_value("Company", company, "abbr")
    if not abbr:
        frappe.db.set_value("Company", company, "abbr", fallback)
        frappe.db.commit()
        abbr = fallback
    return abbr

def _ensure_leaf_account(company: str, full_name: str, parent_full: str, account_type: str = "Tax") -> str:
    if frappe.db.exists("Account", full_name):
        is_group = int(frappe.db.get_value("Account", full_name, "is_group") or 0)
        if is_group == 1:
            frappe.throw(_("اکانت موجود است ولی Group است و قابل استفاده نیست: {0}").format(full_name))
        return full_name

    parent = frappe.get_doc("Account", parent_full)
    if int(parent.is_group or 0) != 1:
        frappe.throw(_("Parent باید Group باشد: {0}").format(parent_full))

    doc = frappe.get_doc({
        "doctype": "Account",
        "name": full_name,
        "account_name": full_name.rsplit(" - ", 1)[0],
        "company": company,
        "parent_account": parent_full,
        "is_group": 0,
        "root_type": parent.root_type,
        "report_type": parent.report_type,
        "account_currency": parent.account_currency,
        "account_type": account_type,
    })
    doc.insert(ignore_permissions=True, set_name=full_name)
    frappe.db.commit()
    return doc.name

def ensure_vat_settlement_accounts(
    company: str = "BlueAPi",
    payable_parent: str = "وظایف و مالیات - BA",
    receivable_parent: str = "حساب های دریافتنی - BA",
    payable_full: str = "مالیات بر ارزش افزوده پرداختنی - BA",
    receivable_full: str = "مالیات بر ارزش افزوده دریافتنی - BA",
) -> dict:
    # فقط برای جلوگیری از fail در جاهای دیگر (اگر abbr خالی باشد)
    _ensure_company_abbr(company, "BA")

    pay = _ensure_leaf_account(company, payable_full, payable_parent, "Tax")
    rec = _ensure_leaf_account(company, receivable_full, receivable_parent, "Tax")
    return {"payable": pay, "receivable": rec}


def debug_vat_accounts(company: str):
    """
    خروجی استاندارد برای دیباگ VAT accounts (per-company).
    هیچ Exception عمدی نمی‌زند؛ فقط وضعیت را گزارش می‌کند.
    """
    def acc_row(name: str):
        if not name:
            return {"name": name, "exists": False, "row": None}
        row = frappe.db.get_value(
            "Account",
            name,
            ["name", "company", "is_group", "parent_account", "root_type", "report_type", "account_type"],
            as_dict=True,
        )
        return {"name": name, "exists": bool(row), "row": row}

    # تلاش برای خواندن BH Settings (اگر فیلدها وجود داشته باشند)
    settings = {}
    try:
        meta = frappe.get_meta("BH Settings")
        for f in ["default_company", "default_sales_vat_account", "default_purchase_vat_account"]:
            if meta.has_field(f):
                settings[f] = frappe.db.get_single_value("BH Settings", f)
    except Exception:
        settings = {}

    # اکانت‌های تسویه (اگر ensure_vat_settlement_accounts در همین فایل هست)
    payable = None
    receivable = None
    try:
        res = ensure_vat_settlement_accounts(company=company)  # noqa: F821 (اگر همین فایل تعریفش کرده)
        payable = res.get("payable")
        receivable = res.get("receivable")
    except Exception:
        # اگر ensure_* نبود یا fail شد، حداقل چیزی نشکنه
        payable = f"مالیات بر ارزش افزوده پرداختنی - {frappe.db.get_value('Company', company, 'abbr') or ''}".strip()
        receivable = f"مالیات بر ارزش افزوده دریافتنی - {frappe.db.get_value('Company', company, 'abbr') or ''}".strip()

    out = {
        "company": company,
        "settings": settings,
        "accounts": {
            "sales_vat": acc_row(settings.get("default_sales_vat_account")),
            "purchase_vat": acc_row(settings.get("default_purchase_vat_account")),
            "payable": acc_row(payable),
            "receivable": acc_row(receivable),
        },
    }
    return out


def dump_journal_entry(name: str):
    """
    خروجی استاندارد برای بررسی JE (بالانس + ردیف‌ها).
    """
    je = frappe.get_doc("Journal Entry", name)
    rows = []
    for r in je.accounts:
        rows.append({
            "account": r.account,
            "debit": flt(r.debit),
            "credit": flt(r.credit),
            "party_type": r.party_type,
            "party": r.party,
            "cost_center": getattr(r, "cost_center", None),
            "project": getattr(r, "project", None),
        })
    return {
        "name": je.name,
        "company": je.company,
        "posting_date": je.posting_date,
        "total_debit": flt(je.total_debit),
        "total_credit": flt(je.total_credit),
        "diff": flt(je.total_debit - je.total_credit),
        "accounts": rows,
    }


def debug_vat_accounts(company: str):
    """Dump BH Settings + existence/leaf status of required VAT accounts."""
    s = frappe.get_single("BH Settings")

    res = {
        "company": company,
        "settings": {
            "default_company": s.default_company,
            "default_sales_vat_account": s.default_sales_vat_account,
            "default_purchase_vat_account": s.default_purchase_vat_account,
        },
        "accounts": {}
    }

    names = {
        "sales_vat": s.default_sales_vat_account,
        "purchase_vat": s.default_purchase_vat_account,
        "payable": f"مالیات بر ارزش افزوده پرداختنی - {frappe.db.get_value('Company', company, 'abbr') or 'XX'}",
        "receivable": f"مالیات بر ارزش افزوده دریافتنی - {frappe.db.get_value('Company', company, 'abbr') or 'XX'}",
    }

    for k, name in names.items():
        row = frappe.db.get_value(
            "Account",
            name,
            ["name", "company", "is_group", "parent_account", "root_type", "report_type", "account_type"],
            as_dict=True,
        )
        res["accounts"][k] = {
            "name": name,
            "exists": bool(row),
            "row": row,
        }

    return res


def audit_doc_event_handlers(doctype: str, event: str):
    """Checks that handlers listed in hooks are importable (prevents runtime crash)."""
    hooks = (frappe.get_hooks("doc_events") or {}).get(doctype, {})
    handlers = hooks.get(event) or []
    out = []
    for h in handlers:
        try:
            frappe.get_attr(h)
            out.append({"handler": h, "ok": True, "error": None})
        except Exception as e:
            out.append({"handler": h, "ok": False, "error": str(e)})
    return {"doctype": doctype, "event": event, "handlers": out}
