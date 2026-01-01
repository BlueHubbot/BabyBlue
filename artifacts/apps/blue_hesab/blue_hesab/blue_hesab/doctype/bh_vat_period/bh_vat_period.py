from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, datetime as dt_datetime
from frappe.utils import flt, nowdate
from frappe.model.naming import make_autoname
from frappe.utils import getdate

import frappe
from frappe.model.document import Document
from frappe import _


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_default(o):
    if isinstance(o, (dt_datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    return str(o)


def _json_dumps(obj: Any) -> str:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    )


@dataclass
class VatPeriodTotals:
    sales_count: int = 0
    sales_net_total: float = 0.0
    sales_vat_total: float = 0.0
    purchase_count: int = 0
    purchase_net_total: float = 0.0
    purchase_vat_total: float = 0.0

    @property
    def net(self) -> float:
        # + => payable, - => receivable
        return float(self.sales_vat_total) - float(self.purchase_vat_total)

    @property
    def net_payable(self) -> float:
        return max(0.0, self.net)

    @property
    def net_receivable(self) -> float:
        return max(0.0, -self.net)


def _get_company_currency(company: str) -> str:
    return (
        frappe.db.get_value("Company", company, "default_currency")
        or frappe.db.get_single_value("Global Defaults", "default_currency")
        or "IRR"
    )

def _default_settlement_accounts(company: str) -> tuple[str | None, str | None]:
    """Return (payable, receivable) settlement accounts if they already exist."""
    abbr = frappe.db.get_value("Company", company, "abbr") or ""
    if not abbr:
        return (None, None)

    payable = f"مالیات بر ارزش افزوده پرداختنی - {abbr}"
    receivable = f"مالیات بر ارزش افزوده دریافتنی - {abbr}"

    if not frappe.db.exists("Account", payable):
        payable = None
    if not frappe.db.exists("Account", receivable):
        receivable = None

    return (payable, receivable)


def _get_bh_settings():
    """Best-effort loader for BH Settings across app refactors."""
    # Newer layout: blue_hesab.bh_core.get_bh_settings
    for dotted in (
        "blue_hesab.bh_core.get_bh_settings",
        "blue_hesab.bh_core.bh_settings.get_bh_settings",
    ):
        try:
            fn = frappe.get_attr(dotted)
            return fn()
        except Exception:
            continue

    # Fallback: singleton DocType
    try:
        return frappe.get_single("BH Settings")
    except Exception:
        return None



def _default_vat_accounts(company: str) -> Tuple[Optional[str], Optional[str]]:
    s = _get_bh_settings()
    if not s:
        return (None, None)
    sales = getattr(s, "default_sales_vat_account", None)
    purchase = getattr(s, "default_purchase_vat_account", None)
    return (sales, purchase)


def _assert_leaf_account(account: str, label: str):
    if not account:
        frappe.throw(f"{label}: مقدار خالی است.")

    row = frappe.db.get_value(
        "Account",
        account,
        ["name", "is_group", "docstatus"],
        as_dict=True,
    )
    if not row:
        frappe.throw(f"{label}: حساب یافت نشد: {account}")

    if int(row.is_group or 0) == 1:
        frappe.throw(f"{label}: حساب باید Leaf باشد، ولی Group است: {account}")

    if int(row.docstatus or 0) == 2:
        frappe.throw(f"{label}: حساب Cancel شده و قابل استفاده نیست: {account}")



def _fetch_vat_docs(
    company: str,
    doctype: str,
    posting_date_from: str,
    posting_date_to: str,
    vat_account_head: str,
) -> List[Dict[str, Any]]:
    if doctype == "Sales Invoice":
        tax_tab = "tabSales Taxes and Charges"
        inv_tab = "tabSales Invoice"
        parenttype = "Sales Invoice"
    elif doctype == "Purchase Invoice":
        tax_tab = "tabPurchase Taxes and Charges"
        inv_tab = "tabPurchase Invoice"
        parenttype = "Purchase Invoice"
    else:
        raise ValueError("Unsupported doctype")

    rows = frappe.db.sql(
        f"""
        SELECT
            inv.name AS name,
            inv.posting_date AS posting_date,
            inv.net_total AS net_total,
            COALESCE(SUM(tax.tax_amount), 0) AS vat_amount
        FROM `{inv_tab}` inv
        LEFT JOIN `{tax_tab}` tax
          ON tax.parent = inv.name
         AND tax.parenttype = %s
         AND tax.docstatus < 2
         AND tax.account_head = %s
        WHERE inv.docstatus = 1
          AND inv.company = %s
          AND inv.posting_date >= %s
          AND inv.posting_date <= %s
        GROUP BY inv.name, inv.posting_date, inv.net_total
        ORDER BY inv.posting_date ASC, inv.name ASC
        """,
        (parenttype, vat_account_head, company, posting_date_from, posting_date_to),
        as_dict=True,
    ) or []
    return rows


def _calc_totals(company: str, start_date: str, end_date: str, sales_vat_account: str, purchase_vat_account: str):
    sales_docs = _fetch_vat_docs(company, "Sales Invoice", start_date, end_date, sales_vat_account)
    purchase_docs = _fetch_vat_docs(company, "Purchase Invoice", start_date, end_date, purchase_vat_account)

    tot = VatPeriodTotals()
    tot.sales_count = len(sales_docs)
    tot.sales_net_total = float(sum((d.get("net_total") or 0) for d in sales_docs))
    tot.sales_vat_total = float(sum((d.get("vat_amount") or 0) for d in sales_docs))

    tot.purchase_count = len(purchase_docs)
    tot.purchase_net_total = float(sum((d.get("net_total") or 0) for d in purchase_docs))
    tot.purchase_vat_total = float(sum((d.get("vat_amount") or 0) for d in purchase_docs))

    snapshot = {
        "company": company,
        "start_date": start_date,
        "end_date": end_date,
        "sales_vat_account": sales_vat_account,
        "purchase_vat_account": purchase_vat_account,
        "sales_docs": sales_docs,
        "purchase_docs": purchase_docs,
        "totals": {
            "sales_count": tot.sales_count,
            "sales_net_total": tot.sales_net_total,
            "sales_vat_total": tot.sales_vat_total,
            "purchase_count": tot.purchase_count,
            "purchase_net_total": tot.purchase_net_total,
            "purchase_vat_total": tot.purchase_vat_total,
            "net": tot.net,
            "net_payable": tot.net_payable,
            "net_receivable": tot.net_receivable,
        },
    }

    snap_json = _json_dumps(snapshot)
    source_hash = _sha256_hex(snap_json.encode("utf-8"))
    payload_hash = source_hash
    return tot, snapshot, source_hash, payload_hash


def _je_append_reverse_balance(je, account: str, balance_amount: float):
    """
    balance_amount = جمع VAT آن حساب طبق اسناد (ممکن است منفی هم شود).
    برای صفر کردن حساب، باید "معکوسِ balance" را ثبت کنیم.
    """
    amt = float(balance_amount or 0)
    if amt == 0:
        return
    # reverse posting
    if amt > 0:
        # reverse = Debit
        je.append("accounts", {"account": account, "debit_in_account_currency": amt, "credit_in_account_currency": 0})
    else:
        # reverse = Credit
        je.append("accounts", {"account": account, "debit_in_account_currency": 0, "credit_in_account_currency": -amt})


def _create_settlement_journal_entry(p):
    """
    Settlement JE that is ALWAYS balanced even if sales/purchase VAT totals are negative
    (returns/credit notes, reversals, etc.)

    Conventions:
    - sales_vat_total: positive => credit-balance VAT payable on sales
    - purchase_vat_total: positive => debit-balance VAT receivable on purchases
    """
    meta = frappe.get_meta("Journal Entry Account")
    prec = (meta.get_field("debit_in_account_currency").precision or 2)

    def money(x):
        return flt(x or 0, prec)

    sales = money(p.sales_vat_total)
    purchase = money(p.purchase_vat_total)

    # net > 0 => payable to tax org (credit payable_account)
    # net < 0 => receivable/refund (debit receivable_account)
    net = money(sales - purchase)

    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.company = p.company
    je.posting_date = p.period_end_date or nowdate()
    je.user_remark = (
        f"BH VAT Settlement | Period={p.name} | "
        f"{p.period_start_date}..{p.period_end_date}"
    )

    def add(account, debit=0, credit=0):
        debit = money(debit)
        credit = money(credit)
        if not debit and not credit:
            return
        r = je.append("accounts", {})
        r.account = account
        r.debit_in_account_currency = debit
        r.credit_in_account_currency = credit
        # base fields (same currency here)
        r.debit = debit
        r.credit = credit

    # Reverse SALES VAT account balance
    # sales>0 => debit to close credit balance
    # sales<0 => credit to close debit balance
    if sales > 0:
        add(p.sales_vat_account, debit=sales)
    elif sales < 0:
        add(p.sales_vat_account, credit=-sales)

    # Reverse PURCHASE VAT account balance
    # purchase>0 => credit to close debit balance
    # purchase<0 => debit to close credit balance
    if purchase > 0:
        add(p.purchase_vat_account, credit=purchase)
    elif purchase < 0:
        add(p.purchase_vat_account, debit=-purchase)

    # Net settlement
    if net > 0:
        add(p.payable_account, credit=net)
    elif net < 0:
        add(p.receivable_account, debit=-net)

    # Sanity: ensure balanced BEFORE submit
    total_debit = money(sum(money(x.debit_in_account_currency) for x in je.accounts))
    total_credit = money(sum(money(x.credit_in_account_currency) for x in je.accounts))
    diff = money(total_debit - total_credit)

    if diff != 0:
        # if it's tiny rounding, absorb it into last line; otherwise throw with debug
        tol = money(1 / (10 ** prec))
        if abs(diff) <= tol and je.accounts:
            if diff > 0:
                je.accounts[-1].credit_in_account_currency = money(je.accounts[-1].credit_in_account_currency + diff)
                je.accounts[-1].credit = je.accounts[-1].credit_in_account_currency
            else:
                je.accounts[-1].debit_in_account_currency = money(je.accounts[-1].debit_in_account_currency + (-diff))
                je.accounts[-1].debit = je.accounts[-1].debit_in_account_currency
        else:
            frappe.throw(
                "JE نامتوازن شد. این یعنی منبع VATها علامت‌دار/غیرمنتظره است. "
                f"sales={sales} purchase={purchase} net={net} "
                f"debit={total_debit} credit={total_credit} diff={diff}"
            )

    je.insert(ignore_permissions=True)
    je.submit()
    frappe.db.commit()
    return je.name



class BHVATPeriod(Document):
    def validate(self):
        if self.period_start_date and self.period_end_date:
            if self.period_start_date > self.period_end_date:
                frappe.throw("تاریخ شروع نمی‌تواند بزرگ‌تر از تاریخ پایان باشد.")

        # currency from Company
        self.currency = frappe.db.get_value("Company", self.company, "default_currency") or "IRR"

        # defaults from BH Settings (per-company)
        if not self.sales_vat_account or not self.purchase_vat_account:
            sales, purchase = _default_vat_accounts(self.company)
            self.sales_vat_account = self.sales_vat_account or sales
            self.purchase_vat_account = self.purchase_vat_account or purchase

        # defaults for settlement accounts if empty (created by vat_admin.ensure_vat_settlement_accounts)
        if not self.payable_account or not self.receivable_account:
            pay, rec = _default_settlement_accounts(self.company)
            self.payable_account = self.payable_account or pay
            self.receivable_account = self.receivable_account or rec

        # If still empty -> actionable error
        if not self.sales_vat_account or not self.purchase_vat_account:
            frappe.throw(
                "حساب‌های VAT فروش/خرید تنظیم نشده‌اند. "
                "یا در «BH Settings» مقادیر پیش‌فرض را ست کنید، "
                "یا هنگام ساخت دوره، این فیلدها را صریحاً پاس بدهید."
            )

        if not self.payable_account or not self.receivable_account:
            frappe.throw(
                "حساب‌های تسویه VAT (پرداختنی/دریافتنی) تنظیم نشده‌اند. "
                "ابتدا ensure_vat_settlement_accounts را اجرا کنید یا مقادیر را پاس بدهید."
            )

        # must be leaf accounts
        _assert_leaf_account(self.sales_vat_account, "حساب VAT فروش")
        _assert_leaf_account(self.purchase_vat_account, "حساب VAT خرید")
        _assert_leaf_account(self.payable_account, "حساب پرداختنی VAT")
        _assert_leaf_account(self.receivable_account, "حساب دریافتنی VAT")

        if not self.schema_version:
            self.schema_version = "VAT-PERIOD-V1"
        if not self.generator_build:
            self.generator_build = "BH-DEV"

        # draft => recompute live
        if int(self.docstatus or 0) == 0:
            self._recompute(strict=False)


    def on_submit(self):
        self._recompute(strict=True)

        je_name = _create_settlement_journal_entry(self)
        if je_name:
            self.db_set("settlement_journal_entry", je_name)

        self.db_set("status", "Closed")

    def on_cancel(self):
        if self.settlement_journal_entry:
            je_docstatus = frappe.db.get_value("Journal Entry", self.settlement_journal_entry, "docstatus")
            if int(je_docstatus or 0) == 1:
                frappe.throw(_("این دوره دارای سند تسویه ثبت‌شده است. ابتدا «سند تسویه» را لغو کنید، سپس دوره را لغو کنید."))
        self.db_set("status", "Cancelled")

    def _recompute(self, strict: bool):
        tot, snapshot, source_hash, payload_hash = _calc_totals(
            company=self.company,
            start_date=str(self.period_start_date),
            end_date=str(self.period_end_date),
            sales_vat_account=self.sales_vat_account,
            purchase_vat_account=self.purchase_vat_account,
        )

        self.sales_doc_count = tot.sales_count
        self.sales_net_total = tot.sales_net_total
        self.sales_vat_total = tot.sales_vat_total

        self.purchase_doc_count = tot.purchase_count
        self.purchase_net_total = tot.purchase_net_total
        self.purchase_vat_total = tot.purchase_vat_total

        self.net_payable = tot.net_payable
        self.net_receivable = tot.net_receivable

        self.snapshot_json = _json_dumps(snapshot)
        self.source_hash = source_hash
        self.payload_hash = payload_hash

        if strict:
            overlap = frappe.db.sql(
                """
                SELECT name FROM `tabBH VAT Period`
                WHERE docstatus = 1
                  AND company = %s
                  AND name != %s
                  AND period_start_date <= %s
                  AND period_end_date >= %s
                LIMIT 1
                """,
                (self.company, self.name or "", self.period_end_date, self.period_start_date),
            )
            if overlap:
                frappe.throw(_("این دوره با یک دوره بسته‌شده دیگر همپوشانی دارد: {0}").format(overlap[0][0]))


    def autoname(self):
        y = getdate(self.period_end_date or self.period_start_date).year
        abbr = frappe.db.get_value("Company", self.company, "abbr") or "XX"
        # مثال خروجی: BH-VATP-BA-2025-00001
        self.name = make_autoname(f"BH-VATP-{abbr}-{y}-.#####")