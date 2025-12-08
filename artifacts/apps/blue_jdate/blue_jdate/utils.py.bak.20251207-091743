from __future__ import annotations
from . import jdate_policy  # blue_jdate/jdate_policy.py
from markupsafe import Markup, escape
import datetime
from typing import Any, Optional
import frappe
from frappe.utils import get_datetime
import jdatetime
# =========================
#  JALALI DATE FILTERS
# =========================
def _to_user_datetime(value: Any) -> Optional[datetime.datetime]:
    """Convert str/date/datetime to datetime safely."""
    if not value:
        return None

    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        value = datetime.datetime(value.year, value.month, value.day, 0, 0, 0)

    try:
        return get_datetime(value)
    except Exception:
        return None
def _format_jdate(jdate: jdatetime.date, fmt: str) -> str:
    fmt = fmt or "YYYY-MM-DD"

    if "%" in fmt:
        return jdate.strftime(fmt)

    if fmt == "YYYY-MM-DD":
        return f"{jdate.year:04d}-{jdate.month:02d}-{jdate.day:02d}"
    if fmt == "YYYY/MM/DD":
        return f"{jdate.year:04d}/{jdate.month:02d}/{jdate.day:02d}"
    if fmt == "YYYY-MM":
        return f"{jdate.year:04d}-{jdate.month:02d}"
    if fmt == "YYYY/MM":
        return f"{jdate.year:04d}/{jdate.month:02d}"

    return f"{jdate.year:04d}-{jdate.month:02d}-{jdate.day:02d}"
def as_jdate(value: Any, fmt: str = "YYYY-MM-DD") -> str:
    """Jinja filter: convert date to Jalali (date only)."""
    dt = _to_user_datetime(value)
    if not dt:
        return ""

    jdate = jdatetime.date.fromgregorian(date=dt.date())
    return _format_jdate(jdate, fmt)
def as_jdatetime(value: Any, fmt: str = "YYYY-MM-DD HH:mm") -> str:
    """Jinja filter: convert datetime to Jalali date+time."""
    dt = _to_user_datetime(value)
    if not dt:
        return ""

    jdt = jdatetime.datetime.fromgregorian(
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=dt.hour,
        minute=dt.minute,
        second=dt.second,
        microsecond=dt.microsecond,
    )

    if "%" in fmt:
        return jdt.strftime(fmt)

    if "H" not in fmt and "h" not in fmt:
        return _format_jdate(jdt.date(), fmt)

    if fmt == "YYYY-MM-DD HH:mm":
        return (
            f"{jdt.year:04d}-{jdt.month:02d}-{jdt.day:02d} "
            f"{jdt.hour:02d}:{jdt.minute:02d}"
        )

    if fmt == "YYYY/MM/DD HH:mm":
        return (
            f"{jdt.year:04d}/{jdt.month:02d}/{jdt.day:02d} "
            f"{jdt.hour:02d}:{jdt.minute:02d}"
        )

    return (
        f"{jdt.year:04d}-{jdt.month:02d}-{jdt.day:02d} "
        f"{jdt.hour:02d}:{jdt.minute:02d}"
    )
def blue_date_j1(value: Any, fmt: str = "YYYY/MM/DD") -> str:
    """
    Pattern J1: فقط جلالی (DB میلادی می‌ماند، خروجی جلالی).
    استفاده در جینجا:
      {{ blue_date_j1(doc.posting_date, "YYYY/MM/DD") }}
    """
    return as_jdate(value, fmt)
def blue_date_j2(value: Any, fmt: str = "YYYY/MM/DD") -> str:
    """
    Pattern J2: Dual – جلالی + میلادی کوچک/ثانویه در HTML استاندارد.

    خروجی نمونه:
      <span class="b-jdate-main">۱۴۰۴/۰۹/۱۱</span>
      <span class="b-jdate-sub">(2025-12-02)</span>
    """
    j = as_jdate(value, fmt)
    if not j:
        return ""

    from frappe.utils import formatdate
    from markupsafe import Markup, escape

    try:
        g = formatdate(value)
    except Exception:
        return j

    html = (
        f'<span class="b-jdate-main">{escape(j)}</span>'
        f'<span class="b-jdate-sub">({escape(g)})</span>'
    )
    return Markup(html)
def blue_policy_date_j1(value: Any, fmt: str = "YYYY/MM/DD") -> str:
    """
    Policy J1 (جدید): فقط جلالی، ولی به‌صورت wrapper مستقل برای ماتریکس.
    قالب‌های قدیمی می‌توانند همچنان از as_jdate یا blue_date_j1 استفاده کنند.
    """
    return blue_date_j1(value, fmt)
def blue_policy_date_j2(value: Any, fmt: str = "YYYY/MM/DD") -> str:
    """
    Policy J2 (جدید): جلالی اصلی + میلادی کوچک، مخصوص قالب‌هایی که
    طبق ماتریکس JDATE_POLICY تنظیم می‌کنی.
    """
    return blue_date_j2(value, fmt)
def jinja_filters():
    return {
        "as_jdate": as_jdate,
        "as_jdatetime": as_jdatetime,
        "money_to_words_fa": money_to_words_fa,
    }
def jinja_methods():
    return {}
# =========================
#  NUMBER → PERSIAN WORDS
# =========================
_FA_ONES = {
    0: "صفر",
    1: "یک",
    2: "دو",
    3: "سه",
    4: "چهار",
    5: "پنج",
    6: "شش",
    7: "هفت",
    8: "هشت",
    9: "نه",
}

_FA_TEENS = {
    10: "ده",
    11: "یازده",
    12: "دوازده",
    13: "سیزده",
    14: "چهارده",
    15: "پانزده",
    16: "شانزده",
    17: "هفده",
    18: "هجده",
    19: "نوزده",
}

_FA_TENS = {
    2: "بیست",
    3: "سی",
    4: "چهل",
    5: "پنجاه",
    6: "شصت",
    7: "هفتاد",
    8: "هشتاد",
    9: "نود",
}

_FA_HUNDREDS = {
    1: "صد",
    2: "دویست",
    3: "سیصد",
    4: "چهارصد",
    5: "پانصد",
    6: "ششصد",
    7: "هفتصد",
    8: "هشتصد",
    9: "نهصد",
}

_FA_SCALES = [
    (10**12, "تریلیون"),
    (10**9, "میلیارد"),
    (10**6, "میلیون"),
    (10**3, "هزار"),
    (1, ""),
]
def _fa_three_digits(n: int) -> str:
    n = n % 1000
    parts: list[str] = []

    h = n // 100
    r = n % 100

    if h:
        parts.append(_FA_HUNDREDS[h])

    if r:
        if r < 10:
            parts.append(_FA_ONES[r])
        elif 10 <= r < 20:
            parts.append(_FA_TEENS[r])
        else:
            t = r // 10
            u = n % 10
            if t:
                parts.append(_FA_TENS[t])
            if u:
                parts.append(_FA_ONES[u])

    return " و ".join(parts)
def number_to_words_fa(value: Any) -> str:
    if value is None or value == "":
        return ""

    try:
        n = int(float(value))
    except Exception:
        return ""

    if n == 0:
        return _FA_ONES[0]

    negative = n < 0
    n = abs(n)

    parts: list[str] = []

    for scale_value, scale_name in _FA_SCALES:
        if n == 0:
            break
        q, n = divmod(n, scale_value)
        if not q:
            continue
        words = _fa_three_digits(q)
        if scale_name:
            parts.append(f"{words} {scale_name}")
        else:
            parts.append(words)

    text = " و ".join(parts)
    if negative:
        text = "منفی " + text
    return text
def money_to_words_fa(value: Any, currency: str | None = None) -> str:
    """Jinja filter: مبلغ به حروف فارسی + واحد پول (بدون «فقط»)."""
    words = number_to_words_fa(value)
    if not words:
        return ""

    cur = (currency or "").upper().strip()
    if cur in {"IRR", "RIAL"}:
        unit = "ریال"
    elif cur in {"IRT", "TOMAN", "TOMANS"}:
        unit = "تومان"
    elif cur:
        unit = cur
    else:
        unit = "ریال"

    return f"{words} {unit}"
# =========================
#  MAIN PRINT FORMAT
# =========================

# BLUE Outputs – DocType Print builders moved to blue_outputs/prints_docs.py
from .blue_outputs.prints_docs import (
    create_blue_print_asset_movement_v1,
    create_blue_print_asset_repair_v1,
    create_blue_print_asset_v1,
    create_blue_print_attendance_v1,
    create_blue_print_bom_v1,
    create_blue_print_delivery_note_v1,
    create_blue_print_delivery_trip_v1,
    create_blue_print_depreciation_schedule_v1,
    create_blue_print_employee_advance_v1,
    create_blue_print_employee_v1,
    create_blue_print_expense_claim_v1,
    create_blue_print_installation_note_v1,
    create_blue_print_job_card_v1,
    create_blue_print_journal_entry_v1,
    create_blue_print_leave_application_v1,
    create_blue_print_material_request_v1,
    create_blue_print_packing_slip_v1,
    create_blue_print_payment_entry_v1,
    create_blue_print_payroll_entry_v1,
    create_blue_print_pick_list_v1,
    create_blue_print_pos_invoice_thermal_v1,
    create_blue_print_pos_invoice_v1,
    create_blue_print_production_plan_v1,
    create_blue_print_project_task_v1,
    create_blue_print_project_v1,
    create_blue_print_purchase_invoice_v1,
    create_blue_print_purchase_order_v1,
    create_blue_print_purchase_receipt_v1,
    create_blue_print_purchase_return_v1,
    create_blue_print_quotation_v1,
    create_blue_print_salary_slip_v1,
    create_blue_print_sales_invoice_v1,
    create_blue_print_sales_order_v1,
    create_blue_print_sales_quotation_v1,
    create_blue_print_sales_return_v1,
    create_blue_print_stock_entry_v1,
    create_blue_print_stock_reconciliation_v1,
    create_blue_print_supplier_quotation_v1,
    create_blue_print_timesheet_v1,
    create_blue_print_work_order_v1,
)

# =====================================================================
#  JDATE POLICY / MATRIX (DOMAINS & AREAS)
# =====================================================================

# --- Business / Industry domains (۹ دامین صنعتی + هسته عمومی) ---

DOMAIN_CORE_GLOBAL = "CORE_GLOBAL"                   # چیزهایی که در همهٔ صنایع مشترک است

DOMAIN_INDUSTRY_MANUFACTURING = "INDUSTRY_MANUFACTURING"
DOMAIN_INDUSTRY_DISTRIBUTION = "INDUSTRY_DISTRIBUTION"
DOMAIN_INDUSTRY_RETAIL = "INDUSTRY_RETAIL"
DOMAIN_INDUSTRY_SERVICES = "INDUSTRY_SERVICES"

DOMAIN_INDUSTRY_EDUCATION = "INDUSTRY_EDUCATION"
DOMAIN_INDUSTRY_HEALTHCARE = "INDUSTRY_HEALTHCARE"
DOMAIN_INDUSTRY_AGRICULTURE = "INDUSTRY_AGRICULTURE"
DOMAIN_INDUSTRY_HOSPITALITY = "INDUSTRY_HOSPITALITY"
DOMAIN_INDUSTRY_NON_PROFIT = "INDUSTRY_NON_PROFIT"
# --- Domain codes (Business / Industry) ---

DOMAIN_CORE_GLOBAL = "CORE_GLOBAL"
DOMAIN_INDUSTRY_MANUFACTURING = "INDUSTRY_MANUFACTURING"
DOMAIN_INDUSTRY_HEALTHCARE = "INDUSTRY_HEALTHCARE"
DOMAIN_INDUSTRY_EDUCATION = "INDUSTRY_EDUCATION"
DOMAIN_INDUSTRY_RETAIL = "INDUSTRY_RETAIL"
DOMAIN_INDUSTRY_SERVICES = "INDUSTRY_SERVICES"
DOMAIN_INDUSTRY_HOSPITALITY = "INDUSTRY_HOSPITALITY"  # هتل / رستوران / کافه
# سایر دامین‌ها را بعداً در صورت نیاز اضافه می‌کنیم


# --- Functional domains (ماژول‌ها / حوزه‌های کارکردی) ---

# مالی / حسابداری
AREA_ACCOUNTS = "ACCOUNTS"              # Accounts / Finance: GL, TB, P&L, VAT, ...

# فروش
AREA_SALES = "SALES"                    # Quotation, Sales Order, Sales Invoice, POS (backend)

# خرید
AREA_PURCHASE = "PURCHASE"              # Supplier، PO، Purchase Invoice، ...

# انبار / موجودی
AREA_STOCK = "STOCK"                    # Stock Entry, Stock Ledger, Material Request, ...

# پروژه‌ها
AREA_PROJECTS = "PROJECTS"              # Project, Task, Timesheet, Gantt, ...

# اجرا و تولید
AREA_MANUFACTURING_EXECUTION = "MANUFACTURING_EXECUTION"  # BOM, Work Order, Job Card, Production Plan, ...

# CRM / فروش سازمانی
AREA_CRM = "CRM"                        # Lead, Opportunity, Pipeline, ...

# پشتیبانی / هِلپ‌دِسک
AREA_SUPPORT = "SUPPORT"                # Issue, Ticket, SLA, ...

# HR / منابع انسانی
AREA_HR = "HR"                          # Employee, Attendance, Leave, ...

# Payroll
AREA_PAYROLL = "PAYROLL"                # Payroll Entry, Salary Slip, ...

# دارایی‌ها
AREA_ASSETS = "ASSETS"                  # Asset, Depreciation, Asset Movement, ...

# مدیریت کیفیت
AREA_QUALITY = "QUALITY"                # Quality Inspection, NCR, COA, ...

# اشتراک‌ها
AREA_SUBSCRIPTIONS = "SUBSCRIPTIONS"    # Subscription, Recurring Invoice, ...

# Healthcare (HIS)
AREA_HEALTHCARE = "HEALTHCARE"          # Patient, Encounter, Lab Test, Inpatient, ...

# Education (SIS/LMS)
AREA_EDUCATION = "EDUCATION"            # Student, Program, Enrollment, Assessment, ...

# Website / CMS / Blog / Wiki
AREA_WEBSITE = "WEBSITE"                # Web Page, Blog, Wiki, Help

# E-commerce / Shopping Cart
AREA_ECOMMERCE = "ECOMMERCE"            # Product, Cart, Checkout, Online Orders

# POS / Retail Front
AREA_POS = "POS"                        # POS Invoice, POS Profile, حرارتی، ...

# Fleet / Field Service
AREA_FLEET = "FLEET"                    # Fleet, Vehicle, Trip, Field Service

# Real Estate / Property Management
AREA_REAL_ESTATE = "REAL_ESTATE"       # Property, Lease, Rent, Contract

# ناحیهٔ عمومی / مشترک
AREA_GENERAL = "GENERAL"                # Dashboard, Desk, generic stuff (CAL Boot, ...)


# --- Object types ---

OBJ_DOCTYPE = "DocType"
OBJ_REPORT = "Report"
OBJ_PORTAL_PAGE = "PortalPage"
OBJ_WEB_FORM = "WebForm"


# --- Output types (نوع خروجی) ---

OUT_DOC_PRINT = "DOC_PRINT"              # Print Format روی DocType
OUT_REPORT_PRINT = "REPORT_PRINT"        # قالب چاپ گزارش
OUT_REPORT_EXPORT = "REPORT_EXPORT"      # Export گزارش (XLSX/CSV/JSON)
OUT_EMAIL_TEMPLATE = "EMAIL_TEMPLATE"    # DocType Email Template
OUT_NOTIFICATION = "NOTIFICATION"        # DocType Notification
OUT_PORTAL_PAGE = "PORTAL_PAGE"          # Portal View
OUT_WEB_FORM = "WEB_FORM"                # Web Form
OUT_POS_THERMAL = "POS_THERMAL"          # چاپ حرارتی POS
OUT_LABEL_PRINT = "LABEL_PRINT"          # لیبل / بارکد
OUT_CHEQUE_PRINT = "CHEQUE_PRINT"        # چاپ چک
OUT_REGULATORY_EXPORT = "REGULATORY_EXPORT"  # خروجی خام برای دولت/سیستم‌ها
OUT_REGULATORY_PRINT = "REGULATORY_PRINT"    # فرم چاپی قانونی
OUT_DASHBOARD_VIEW = "DASHBOARD_VIEW"
OUT_CHART_VIEW = "CHART_VIEW"
OUT_CALENDAR_VIEW = "CALENDAR_VIEW"
OUT_GANTT_VIEW = "GANTT_VIEW"
OUT_KANBAN_VIEW = "KANBAN_VIEW"
OUT_AUTO_EMAIL_REPORT = "AUTO_EMAIL_REPORT"


# --- Audience (مخاطب خروجی) ---

AUD_EXTERNAL = "EXTERNAL"       # مشتری، تأمین‌کننده، کارمند به‌عنوان مخاطب بیرونی
AUD_INTERNAL = "INTERNAL"       # مدیران، مالی، داخلی
AUD_OPERATIONAL = "OPERATIONAL" # عملیات روزمره (انبار، تولید، ...)
AUD_REGULATORY = "REGULATORY"   # مراجع قانونی / مالیاتی / سامانه‌های رسمی


# --- JDate rules ---

JDATE_JALALI_ONLY = "J1"        # فقط جلالی روی خروجی (DB میلادی)
JDATE_DUAL = "J2"               # جلالی + میلادی کوچک/ثانویه
JDATE_GREGORIAN_ONLY = "J3"     # فقط میلادی، بدون دست‌کاری
JDATE_FRONTEND_ONLY = "J4"      # فقط UI/JS (CAL)، سرور جینجا دست‌نخورده


# --- Core policy matrix (هسته GLOBAL) ---
# هر ردیف: یک سند / خروجی خاص و قانون JDate آن + کلید قالب Blue (اگر داریم)

JDATE_POLICY_MATRIX = [
    # -----------------
    # SALES / PURCHASE
    # -----------------

    # Sales Invoice (فاکتور فروش رسمی) – Blue Template موجود
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Invoice",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,  # جلالی + میلادی کوچک
        "blue_template_key": "BLUE_PRINT_SALES_INVOICE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Invoice",
        "output_type": OUT_REPORT_EXPORT,  # Export جدول Invoiceها
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Sales Order
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Order",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_SALES_ORDER_V1",
        "enabled": True,
    },

    # Quotation
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Quotation",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_QUOTATION_V1",
        "enabled": True,
    },

    # Delivery Note
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Delivery Note",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # می‌تواند J2 هم شود، فعلاً فقط جلالی
        "blue_template_key": "BLUE_PRINT_DELIVERY_NOTE_V1",
        "enabled": True,
    },

    # Purchase Invoice
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PURCHASE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Purchase Invoice",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_PURCHASE_INVOICE_V1",
        "enabled": True,
    },

    # Purchase Order
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PURCHASE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Purchase Order",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_PURCHASE_ORDER_V1",
        "enabled": True,
    },

    # Supplier Quotation
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PURCHASE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Supplier Quotation",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_SUPPLIER_QUOTATION_V1",
        "enabled": True,
    },

    # -----------------
    # ACCOUNTS / FINANCIAL REPORTS
    # -----------------

    # General Ledger
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "General Ledger",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,  # چاپ GL: جلالی + میلادی کوچک
        "blue_template_key": "BLUE_REPORT_GL_V1",  # بعداً اگر خواستی برایش قالب بسازیم
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "General Ledger",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,  # Export برای Excel/BI → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Trial Balance
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Trial Balance",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_TRIAL_BALANCE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Trial Balance",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Balance Sheet
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Balance Sheet",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_BALANCE_SHEET_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Balance Sheet",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Profit and Loss Statement
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Profit and Loss Statement",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_PL_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Profit and Loss Statement",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
        # -----------------
    # ACCOUNTS / REGISTERS & AR/AP
    # -----------------

    # Sales Register
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Sales Register",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,  # چاپ رجیستر فروش: جلالی + میلادی کوچک
        "blue_template_key": "BLUE_REPORT_SALES_REGISTER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Sales Register",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,  # Export برای Excel/BI → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Purchase Register
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Purchase Register",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_PURCHASE_REGISTER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Purchase Register",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Accounts Receivable Summary
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Receivable Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_AR_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Receivable Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Accounts Payable Summary
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Payable Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_AP_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Payable Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # INDUSTRY: EDUCATION (SIS / LMS)
    # -----------------

    # Student (پرینت پروفایل دانش‌آموز / دانشجو) – استفاده داخلی
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Student",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # تاریخ‌ها فقط جلالی در پروفایل
        "blue_template_key": "BLUE_PRINT_EDU_STUDENT_V1",
        "enabled": True,
    },

    # Student Applicant (فرم ثبت‌نام / پذیرش) – مخاطب خارجی
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Student Applicant",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,  # جلالی اصلی + میلادی کوچک
        "blue_template_key": "BLUE_PRINT_EDU_APPLICANT_V1",
        "enabled": True,
    },

    # Program Enrollment (فرم ثبت‌نام در برنامه/رشته) – معمولاً به دانشجو هم داده می‌شود
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Program Enrollment",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,  # دانشجو / ولی دانش‌آموز
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_EDU_ENROLLMENT_V1",
        "enabled": True,
    },

    # Fees (فاکتور شهریه / قبض پرداخت) – سند مالی آموزشی
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Fees",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,  # شبیه Sales Invoice، اما برای Education
        "blue_template_key": "BLUE_PRINT_EDU_FEES_V1",
        "enabled": True,
    },

    # Student Report Generation (کارنامه / ریزنمرات) – گزارش رسمی برای دانش‌آموز
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Student Report Generation",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,  # کارنامه: جلالی اصلی + میلادی کوچک برای ارجاع
        "blue_template_key": "BLUE_PRINT_EDU_REPORT_CARD_V1",
        "enabled": True,
    },

    # Student Attendance (گزارش حضور و غیاب برای استفاده داخلی مدرسه)
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Student Attendance",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_EDU_ATTENDANCE_V1",
        "enabled": True,
    },
    # -----------------
    # INDUSTRY: HEALTHCARE (HIS)
    # -----------------

    # Patient – پرونده بیمار (اگر چاپ شود، معمولاً برای خود بیمار یا پرونده کاغذی)
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Patient",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,              # بیمار / همراه بیمار
        "jdate_rule": JDATE_DUAL,              # جلالی + میلادی کوچک
        "blue_template_key": "BLUE_PRINT_HC_PATIENT_V1",
        "enabled": True,
    },

    # Patient Appointment – نوبت‌دهی (برگه‌ی وقت ویزیت)
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Patient Appointment",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,              # به دست بیمار می‌رسد
        "jdate_rule": JDATE_JALALI_ONLY,       # تاریخ نوبت برای بیمار → فقط جلالی
        "blue_template_key": "BLUE_PRINT_HC_APPOINTMENT_V1",
        "enabled": True,
    },

    # Patient Encounter – برگه ویزیت / شرح حال
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Patient Encounter",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,              # هم برای بیمار، هم پرونده‌ی داخلی
        "jdate_rule": JDATE_DUAL,              # جلالی اصلی + میلادی کوچک
        "blue_template_key": "BLUE_PRINT_HC_ENCOUNTER_V1",
        "enabled": True,
    },

    # Lab Test – نتیجه آزمایش
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Lab Test",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,              # تحویل به بیمار / پزشک
        "jdate_rule": JDATE_DUAL,              # تاریخ نمونه‌گیری / گزارش → J2
        "blue_template_key": "BLUE_PRINT_HC_LABTEST_V1",
        "enabled": True,
    },

    # Inpatient Record – پرونده بستری (عمدتاً مصرف داخلی بیمارستان)
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Inpatient Record",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,       # برای پرسنل داخلی → فقط جلالی
        "blue_template_key": "BLUE_PRINT_HC_INPATIENT_V1",
        "enabled": True,
    },

    # Healthcare Invoice – قبض/فاکتور درمانی (اگر از DocType جداگانه استفاده شود)
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Healthcare Invoice",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,              # مطابق سیاست فاکتورهای مالی
        "blue_template_key": "BLUE_PRINT_HC_INVOICE_V1",
        "enabled": True,
    },
    # -----------------
    # INDUSTRY: EDUCATION - REPORTS (Attendance / Fees)
    # -----------------

    # Student Attendance Sheet – برگه حضور و غیاب برای معلم/مدرسه
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Student Attendance Sheet",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                 # استفاده‌ی داخلی مدرسه
        "jdate_rule": JDATE_JALALI_ONLY,          # فقط جلالی روی چاپ
        "blue_template_key": "BLUE_REPORT_EDU_ATTENDANCE_SHEET_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Student Attendance Sheet",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,       # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Student Attendance Summary – خلاصه‌ی حضور و غیاب (اگر روی سایتت این Report هست)
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Student Attendance Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_EDU_ATTENDANCE_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Student Attendance Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Fees Collection – گزارش وصول شهریه
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Fees Collection",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                 # مالی/اداری مدرسه
        "jdate_rule": JDATE_DUAL,                 # مالی → جلالی + میلادی کوچک
        "blue_template_key": "BLUE_REPORT_EDU_FEES_COLLECTION_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Fees Collection",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,       # Export برای Excel/BI → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Fees Outstanding / Fees Pending – گزارش معوقات شهریه
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Fees Outstanding",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,                 # مالی + حساس → Dual
        "blue_template_key": "BLUE_REPORT_EDU_FEES_OUTSTANDING_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Fees Outstanding",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Program-wise Student Summary – خلاصه دانشجو/دانش‌آموز بر اساس Program
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Program-wise Student Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # بیشتر عملیاتی/آموزشی است
        "blue_template_key": "BLUE_REPORT_EDU_PROGRAM_STUDENT_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_EDUCATION,
        "functional_area": AREA_EDUCATION,
        "object_type": OBJ_REPORT,
        "object_name": "Program-wise Student Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # INDUSTRY: HEALTHCARE - REPORTS (OPD / IPD SUMMARY)
    # -----------------

    # OPD Summary – خلاصه بیماران سرپایی (Outpatient)
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_REPORT,
        "object_name": "OPD Summary",                 # اگر روی سایتت اسم دیگری است، همین را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                     # مدیریت/پرسنل درمانی
        "jdate_rule": JDATE_JALALI_ONLY,              # چاپ داخلی → فقط جلالی
        "blue_template_key": "BLUE_REPORT_HC_OPD_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_REPORT,
        "object_name": "OPD Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,           # Export برای Excel/BI → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # IPD Summary – خلاصه بیماران بستری (Inpatient)
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_REPORT,
        "object_name": "IPD Summary",                 # اگر Report واقعی اسم دیگری دارد، این را عوض کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                     # بیشتر مصرف مدیریتی/عملیاتی
        "jdate_rule": JDATE_JALALI_ONLY,              # چاپ داخلی → جلالی
        "blue_template_key": "BLUE_REPORT_HC_IPD_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_HEALTHCARE,
        "functional_area": AREA_HEALTHCARE,
        "object_type": OBJ_REPORT,
        "object_name": "IPD Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,           # Export → میلادی خالص
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # INDUSTRY: MANUFACTURING – DOC PRINTS
    # -----------------

    # Work Order – دستور کار تولید (کاملاً عملیاتی / داخلی)
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Work Order",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_OPERATIONAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # برای اپراتور و تولید → فقط جلالی
        "blue_template_key": "BLUE_PRINT_MFG_WORK_ORDER_V1",
        "enabled": True,
    },

    # Job Card – کارت کار برای اپراتور
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Job Card",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_OPERATIONAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_MFG_JOB_CARD_V1",
        "enabled": True,
    },

    # Bill of Materials (BOM) – لیست مواد
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "BOM",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,  # مهندسی / برنامه‌ریزی تولید
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_MFG_BOM_V1",
        "enabled": True,
    },

    # Production Plan – برنامه تولید (مصرف داخلی مدیریتی/برنامه‌ریزی)
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Production Plan",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # می‌توانست J2 هم باشد؛ فعلاً J1
        "blue_template_key": "BLUE_PRINT_MFG_PRODUCTION_PLAN_V1",
        "enabled": True,
    },

    # -----------------
    # INDUSTRY: MANUFACTURING – REPORTS
    # -----------------

    # Production Analytics – تحلیل تولید
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_REPORT,
        "object_name": "Production Analytics",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # گزارش مدیریتی داخلی → جلالی
        "blue_template_key": "BLUE_REPORT_MFG_PRODUCTION_ANALYTICS_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_REPORT,
        "object_name": "Production Analytics",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,  # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Work Order Summary – خلاصه وضعیت Work Orderها
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_REPORT,
        "object_name": "Work Order Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_MFG_WORK_ORDER_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_REPORT,
        "object_name": "Work Order Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # BOM Stock Report – موجودی مواد طبق BOM (اگر روی سیستم‌ات فعال است)
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_REPORT,
        "object_name": "BOM Stock Report",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_MFG_BOM_STOCK_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_MANUFACTURING,
        "functional_area": AREA_MANUFACTURING_EXECUTION,
        "object_type": OBJ_REPORT,
        "object_name": "BOM Stock Report",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / STOCK & INVENTORY – DOC PRINTS
    # -----------------

    # Material Request – درخواست مواد/کالا (انبار / تولید)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Material Request",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_OPERATIONAL,              # انبار / تولید
        "jdate_rule": JDATE_JALALI_ONLY,          # فقط جلالی کافی است
        "blue_template_key": "BLUE_PRINT_MATERIAL_REQUEST_V1",
        "enabled": True,
    },

    # Stock Entry – ورود/خروج/انتقال موجودی
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Stock Entry",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_OPERATIONAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_STOCK_ENTRY_V1",
        "enabled": True,
    },

    # Stock Reconciliation – انبارگردانی / اصلاح موجودی
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Stock Reconciliation",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_STOCK_RECONCILIATION_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / STOCK & INVENTORY – REPORTS
    # -----------------

    # Stock Ledger – کاردکس کالا
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Ledger",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # چاپ داخلی → جلالی
        "blue_template_key": "BLUE_REPORT_STOCK_LEDGER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Ledger",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,       # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Stock Balance – موجودی کالا
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Balance",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_STOCK_BALANCE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Balance",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Stock Ageing – گزارش سررسید / خواب موجودی
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Ageing",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_STOCK_AGEING_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Ageing",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / CRM – DOC PRINTS
    # -----------------

    # Lead – سرنخ فروش (پرینت داخلی برای تیم فروش)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Lead",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,              # فقط تیم فروش
        "jdate_rule": JDATE_JALALI_ONLY,       # جلالی کافی است
        "blue_template_key": "BLUE_PRINT_LEAD_V1",
        "enabled": True,
    },

    # Opportunity – فرصت فروش (پیشنهاد داخلی/جلسه‌ای)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Opportunity",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_OPPORTUNITY_V1",
        "enabled": True,
    },

    # Contact – چاپ کارت/پروفایل مخاطب (معمولاً داخلی)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Contact",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_CONTACT_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / CRM – REPORTS
    # -----------------

    # Lead Details / Lead Summary – گزارش سرنخ‌ها
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_REPORT,
        "object_name": "Lead Details",         # اگر روی سیستم‌ات اسم دیگری است، همین را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,       # چاپ داخلی → جلالی
        "blue_template_key": "BLUE_REPORT_LEAD_DETAILS_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_REPORT,
        "object_name": "Lead Details",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,    # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Opportunity Summary – خلاصه فرصت‌ها / Pipeline
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_REPORT,
        "object_name": "Opportunity Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_OPPORTUNITY_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_CRM,
        "object_type": OBJ_REPORT,
        "object_name": "Opportunity Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / SUPPORT – DOC PRINTS
    # -----------------

    # Issue – تیکت پشتیبانی (برگه تیکت قابل ارسال برای مشتری)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Issue",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,              # ممکن است برای مشتری هم چاپ/ارسال شود
        "jdate_rule": JDATE_DUAL,              # جلالی + میلادی کوچک
        "blue_template_key": "BLUE_PRINT_ISSUE_V1",
        "enabled": True,
    },

    # Service Level Agreement – SLA (اگر چاپ شود، بیشتر داخلی/قراردادی است)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Service Level Agreement",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,              # عموماً داخلی/قراردادی
        "jdate_rule": JDATE_DUAL,              # می‌تواند جلالی + میلادی کوچک باشد
        "blue_template_key": "BLUE_PRINT_SLA_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / SUPPORT – REPORTS
    # -----------------

    # Issue Summary – خلاصه تیکت‌ها (بار اصلی روی تاریخ ایجاد/بستن)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_REPORT,
        "object_name": "Issue Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,       # برای تیم پشتیبانی → جلالی
        "blue_template_key": "BLUE_REPORT_ISSUE_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_REPORT,
        "object_name": "Issue Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,    # Export → میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Support Analytics – گزارش تحلیلی پشتیبانی (اگر روی سیستم‌ات فعال است)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_REPORT,
        "object_name": "Support Analytics",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_SUPPORT_ANALYTICS_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_REPORT,
        "object_name": "Support Analytics",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / ASSETS – DOC PRINTS
    # -----------------

    # Asset – برگهٔ مشخصات دارایی (پرونده دارایی)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ASSETS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Asset",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,              # مالی / حسابداری / دارایی
        "jdate_rule": JDATE_DUAL,              # هم برای مدیر داخلی، هم حسابرس → Dual
        "blue_template_key": "BLUE_PRINT_ASSET_V1",
        "enabled": True,
    },

    # Asset Movement – حواله جابجایی دارایی
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ASSETS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Asset Movement",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_OPERATIONAL,           # انبار / دارایی / واحد استفاده‌کننده
        "jdate_rule": JDATE_JALALI_ONLY,       # عملیات داخلی → فقط جلالی
        "blue_template_key": "BLUE_PRINT_ASSET_MOVEMENT_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / ASSETS – REPORTS
    # -----------------

    # Fixed Asset Register – دفتر دارایی‌ها
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ASSETS,
        "object_type": OBJ_REPORT,
        "object_name": "Fixed Asset Register",    # اگر نامش فرق دارد، همین را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                 # داخلی + حسابرس
        "jdate_rule": JDATE_DUAL,                 # Dual: جلالی + میلادی کوچک
        "blue_template_key": "BLUE_REPORT_FIXED_ASSET_REGISTER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ASSETS,
        "object_type": OBJ_REPORT,
        "object_name": "Fixed Asset Register",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,       # Export برای Excel/BI → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Asset Depreciation Schedule – برنامه استهلاک
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ASSETS,
        "object_type": OBJ_REPORT,
        "object_name": "Asset Depreciation Schedule",  # یا اسم واقعی Report روی سایت تو
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                 # مالی / حسابرس
        "jdate_rule": JDATE_DUAL,                 # Dual برای گزارش استهلاک
        "blue_template_key": "BLUE_REPORT_ASSET_DEPRECIATION_SCHEDULE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ASSETS,
        "object_type": OBJ_REPORT,
        "object_name": "Asset Depreciation Schedule",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,       # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / SUBSCRIPTIONS – DOC PRINTS
    # -----------------

    # Subscription – قرارداد/اشتراک خدمات (سند اصلی اشتراک)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Subscription",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,                  # مشتری اشتراک
        "jdate_rule": JDATE_DUAL,                  # جلالی + میلادی کوچک (قراردادی/مالی)
        "blue_template_key": "BLUE_PRINT_SUBSCRIPTION_V1",
        "enabled": True,
    },

    # Subscription Plan – اگر بخواهی پلن را به‌صورت برگه معرفی چاپ کنی (بیشتر مارکتینگ)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Subscription Plan",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,                  # می‌تواند به مشتری نمایش داده شود
        "jdate_rule": JDATE_JALALI_ONLY,           # معرفی پلن → جلالی کافی است
        "blue_template_key": "BLUE_PRINT_SUBSCRIPTION_PLAN_V1",
        "enabled": True,
    },

    # (فاکتورهای تکرارشوندهٔ Subscription عملاً همان Sales Invoice هستند
    # و قبلاً تحت AREA_SALES / Sales Invoice پوشش داده شده‌اند.)

    # -----------------
    # CORE_GLOBAL / SUBSCRIPTIONS – REPORTS
    # -----------------

    # Subscription-wise Revenue – درآمد بر اساس اشتراک
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_REPORT,
        "object_name": "Subscription-wise Revenue",   # اگر اسم واقعی فرق دارد، این را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,                    # مالی / مدیریت
        "jdate_rule": JDATE_DUAL,                    # مالی → Dual
        "blue_template_key": "BLUE_REPORT_SUBSCRIPTION_REVENUE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_REPORT,
        "object_name": "Subscription-wise Revenue",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,          # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Subscription Summary – خلاصه وضعیت اشتراک‌ها (Active/Expired/Trial و ...)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_REPORT,
        "object_name": "Subscription Summary",       # اگر Report اسم دیگری دارد، این را عوض کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,             # بیشتر عملیاتی/مدیریتی داخلی
        "blue_template_key": "BLUE_REPORT_SUBSCRIPTION_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_REPORT,
        "object_name": "Subscription Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,          # Export → میلادی
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / PROJECTS – DOC PRINTS
    # -----------------

    # Project – برگه اطلاعات پروژه (داخلی)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Project",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,              # مدیر پروژه، تیم داخلی
        "jdate_rule": JDATE_JALALI_ONLY,       # فقط جلالی روی چاپ
        "blue_template_key": "BLUE_PRINT_PROJECT_V1",
        "enabled": True,
    },

    # Task – برگه تسک (اگر بخواهی برای جلسات/برنامه‌ریزی چاپ کنی)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Task",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_TASK_V1",
        "enabled": True,
    },

    # (Timesheet قبلاً به‌عنوان DOC_PRINT تحت AREA_PROJECTS اضافه شده؛ دوباره تعریف نکن.)

    # -----------------
    # CORE_GLOBAL / PROJECTS – REPORTS
    # -----------------

    # Project Summary – خلاصه وضعیت پروژه‌ها
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_REPORT,
        "object_name": "Project Summary",      # اگر روی سایتت اسم دیگری است، همین را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,       # چاپ داخلی → جلالی
        "blue_template_key": "BLUE_REPORT_PROJECT_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_REPORT,
        "object_name": "Project Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,    # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Task Summary – خلاصه تسک‌ها (مثلاً بر اساس Status / Project)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_REPORT,
        "object_name": "Task Summary",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_REPORT_TASK_SUMMARY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_REPORT,
        "object_name": "Task Summary",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / WEBSITE & PORTAL – PORTAL PAGES
    # -----------------
    # Customer Portal: Sales Invoice
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Sales Invoice",        # نمایش فاکتور در پرتال مشتری
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,       # UI پرتال → فقط جلالی
        "blue_template_key": "BLUE_PORTAL_SALES_INVOICE_V1",
        "enabled": True,
    },

    # Customer Portal: Sales Order
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Sales Order",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PORTAL_SALES_ORDER_V1",
        "enabled": True,
    },

    # Customer Portal: Quotation
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Quotation",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PORTAL_QUOTATION_V1",
        "enabled": True,
    },

    # Customer Portal: Delivery Note
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Delivery Note",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PORTAL_DELIVERY_NOTE_V1",
        "enabled": True,
    },

    # Support Portal: Issue (تیکت پشتیبانی در پرتال)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Issue",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PORTAL_ISSUE_V1",
        "enabled": True,
    },

    # Employee Portal: Salary Slip (پرتال کارمند)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PAYROLL,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Salary Slip",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,              # کارمند از دید سیستم
        "jdate_rule": JDATE_JALALI_ONLY,       # فیش روی پرتال → فقط جلالی
        "blue_template_key": "BLUE_PORTAL_SALARY_SLIP_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / WEBSITE & PORTAL – WEB FORMS
    # -----------------

    # Web Form: Job Applicant (فرم استخدام)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_WEB_FORM,
        "object_name": "Job Applicant",
        "output_type": OUT_WEB_FORM,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,       # مهلت ارسال و تاریخ‌ها → جلالی
        "blue_template_key": "BLUE_WEBFORM_JOB_APPLICANT_V1",
        "enabled": True,
    },

    # Web Form: Contact (فرم تماس)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_WEB_FORM,
        "object_name": "Contact",
        "output_type": OUT_WEB_FORM,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_WEBFORM_CONTACT_V1",
        "enabled": True,
    },

    # Web Form: Support (اگر فرم پشتیبانی وب داری)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_WEB_FORM,
        "object_name": "Support",
        "output_type": OUT_WEB_FORM,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_WEBFORM_SUPPORT_V1",
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / EMAIL TEMPLATES (DocType-level)
    # -----------------
    # Email Template برای ارسال فاکتور فروش به مشتری
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,              # قالب ایمیل مربوط به Sales Invoice
        "object_name": "Sales Invoice",
        "output_type": OUT_EMAIL_TEMPLATE,
        "audience": AUD_EXTERNAL,               # مشتری
        "jdate_rule": JDATE_DUAL,               # تاریخ‌ها در متن ایمیل → جلالی + میلادی کوچک
        "blue_template_key": "BLUE_EMAIL_SALES_INVOICE_V1",
        "enabled": True,
    },

    # Email Template برای ارسال سفارش فروش به مشتری
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Order",
        "output_type": OUT_EMAIL_TEMPLATE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_EMAIL_SALES_ORDER_V1",
        "enabled": True,
    },

    # Email Template برای ارسال پیش‌فاکتور (Quotation) به مشتری
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Quotation",
        "output_type": OUT_EMAIL_TEMPLATE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_EMAIL_QUOTATION_V1",
        "enabled": True,
    },

    # Email Template برای ارسال فاکتور خرید به تأمین‌کننده (در صورت استفاده)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PURCHASE,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Purchase Order",
        "output_type": OUT_EMAIL_TEMPLATE,
        "audience": AUD_EXTERNAL,               # تأمین‌کننده
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_EMAIL_PURCHASE_ORDER_V1",
        "enabled": True,
    },

    # Email Template برای HR: اطلاع‌رسانی مرخصی به کارمند
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Leave Application",
        "output_type": OUT_EMAIL_TEMPLATE,
        "audience": AUD_EXTERNAL,               # از دید سیستم، کارمند یک مخاطب بیرونی است
        "jdate_rule": JDATE_JALALI_ONLY,        # HR داخلی → فقط جلالی
        "blue_template_key": "BLUE_EMAIL_LEAVE_APPLICATION_V1",
        "enabled": True,
    },

    # Email Template برای ارسال تیکت پشتیبانی به مشتری
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Issue",
        "output_type": OUT_EMAIL_TEMPLATE,
        "audience": AUD_EXTERNAL,               # مشتری/کاربر نهایی
        "jdate_rule": JDATE_DUAL,               # زمان ایجاد/بستن تیکت → Dual
        "blue_template_key": "BLUE_EMAIL_ISSUE_V1",
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / NOTIFICATIONS (Workflow / Doc Notifications)
    # -----------------
    # Notification روی Sales Invoice (مثلاً Payment Reminder)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Invoice",
        "output_type": OUT_NOTIFICATION,
        "audience": AUD_EXTERNAL,               # اعلان به مشتری
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_NOTIF_SALES_INVOICE_V1",
        "enabled": True,
    },

    # Notification داخلی روی Leave Application (مثلاً برای Manager / HR)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Leave Application",
        "output_type": OUT_NOTIFICATION,
        "audience": AUD_INTERNAL,               # مدیر / HR
        "jdate_rule": JDATE_JALALI_ONLY,        # اعلان داخلی → فقط جلالی
        "blue_template_key": "BLUE_NOTIF_LEAVE_APPLICATION_V1",
        "enabled": True,
    },

    # Notification روی Issue (مثلاً وقتی تیکت Closed شد)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SUPPORT,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Issue",
        "output_type": OUT_NOTIFICATION,
        "audience": AUD_EXTERNAL,               # برای مشتری
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_NOTIF_ISSUE_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / AUTO EMAIL REPORTS
    # -----------------

    # Auto Email Report: General Ledger
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "General Ledger",
        "output_type": OUT_AUTO_EMAIL_REPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,               # بدنه HTML ایمیل → Dual
        "blue_template_key": "BLUE_AUTOEMAIL_GL_V1",
        "enabled": True,
    },

    # Auto Email Report: Trial Balance
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Trial Balance",
        "output_type": OUT_AUTO_EMAIL_REPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_AUTOEMAIL_TRIAL_BALANCE_V1",
        "enabled": True,
    },

    # Auto Email Report: Profit and Loss Statement
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Profit and Loss Statement",
        "output_type": OUT_AUTO_EMAIL_REPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_AUTOEMAIL_PL_V1",
        "enabled": True,
    },

    # Auto Email Report: Stock Ledger
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_STOCK,
        "object_type": OBJ_REPORT,
        "object_name": "Stock Ledger",
        "output_type": OUT_AUTO_EMAIL_REPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,        # گزارش عملیاتی انبار → در بدنه فقط جلالی
        "blue_template_key": "BLUE_AUTOEMAIL_STOCK_LEDGER_V1",
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / ACCOUNTS – DOC PRINTS
    # -----------------

    # Journal Entry – سند روزنامه
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Journal Entry",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,                 # مالی / حسابداری
        "jdate_rule": JDATE_DUAL,                 # جلالی اصلی + میلادی کوچک
        "blue_template_key": "BLUE_PRINT_JOURNAL_ENTRY_V1",
        "enabled": True,
    },

    # Payment Entry – سند دریافت/پرداخت
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Payment Entry",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,                 # مالی / خزانه
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_PAYMENT_ENTRY_V1",
        "enabled": True,
    },

    # Payment Request – درخواست پرداخت (ممکن است برای مشتری/تأمین‌کننده ارسال شود)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Payment Request",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,                 # طرف حساب بیرونی
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_PAYMENT_REQUEST_V1",
        "enabled": True,
    },

    # Bank Reconciliation – آشتی بانکی (DocType)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Bank Reconciliation",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,                 # حسابداری / خزانه
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_BANK_RECONCILIATION_V1",
        "enabled": True,
    },

    # -----------------
    # CORE_GLOBAL / ACCOUNTS – STATEMENTS (Customer / Supplier)
    # -----------------

    # Customer Statement – صورتحساب مشتری
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Customer Statement",       # اگر اسم دیگری است، همین را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_EXTERNAL,                  # برای مشتری
        "jdate_rule": JDATE_DUAL,                  # جلالی + میلادی کوچک
        "blue_template_key": "BLUE_REPORT_CUSTOMER_STATEMENT_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Customer Statement",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,        # فایل داده → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Supplier Statement – صورتحساب تأمین‌کننده
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Supplier Statement",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_EXTERNAL,                  # برای تأمین‌کننده
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_SUPPLIER_STATEMENT_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Supplier Statement",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / ACCOUNTS – CORE FINANCIAL REPORTS
    # -----------------

    # General Ledger
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "General Ledger",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,                  # برای مدیر مالی/حسابرس → Dual
        "blue_template_key": "BLUE_REPORT_GENERAL_LEDGER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "General Ledger",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,        # Export → میلادی خالص
        "blue_template_key": None,
        "enabled": True,
    },

    # Trial Balance
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Trial Balance",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_TRIAL_BALANCE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Trial Balance",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Profit and Loss Statement
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Profit and Loss Statement",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_PROFIT_AND_LOSS_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Profit and Loss Statement",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Balance Sheet
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Balance Sheet",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_BALANCE_SHEET_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Balance Sheet",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Cash Flow Statement
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Cash Flow",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_CASH_FLOW_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Cash Flow",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Accounts Receivable / Accounts Payable
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Receivable",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_ACCOUNTS_RECEIVABLE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Receivable",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Payable",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_ACCOUNTS_PAYABLE_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Payable",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # AR / AP Ageing
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Receivable Ageing",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_AR_AGEING_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Receivable Ageing",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Payable Ageing",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_AP_AGEING_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Accounts Payable Ageing",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # -----------------
    # CORE_GLOBAL / REGULATORY & TAX
    # -----------------

    # VAT / Tax Return – گزارش قانونی مالیات بر ارزش افزوده (فرم رسمی)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "VAT Return",               # اگر اسم دیگری است، اصلاح کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,        # فرم قانونی → پیش‌فرض فقط میلادی
        "blue_template_key": "BLUE_REPORT_VAT_RETURN_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "VAT Return",
        "output_type": OUT_REGULATORY_EXPORT,      # خروجی JSON/CSV/XML رسمی
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,        # خط قرمز: داده خام همیشه میلادی
        "blue_template_key": None,
        "enabled": True,
    },

    # Tax Detail / Tax Summary – گزارش جزئیات مالیات
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Tax Detail",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,        # پیش‌فرض: قانونی → میلادی
        "blue_template_key": "BLUE_REPORT_TAX_DETAIL_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Tax Detail",
        "output_type": OUT_REGULATORY_EXPORT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Sales Register – اگر خروجی رسمی برای سازمان مالیات استفاده شود
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Sales Register",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": "BLUE_REPORT_SALES_REGISTER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Sales Register",
        "output_type": OUT_REGULATORY_EXPORT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },

    # Purchase Register – معادل برای خریدها
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Purchase Register",
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": "BLUE_REPORT_PURCHASE_REGISTER_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_ACCOUNTS,
        "object_type": OBJ_REPORT,
        "object_name": "Purchase Register",
        "output_type": OUT_REGULATORY_EXPORT,
        "audience": AUD_REGULATORY,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # =================================================================
    # INDUSTRY_RETAIL – Retail / Shops / Supermarkets
    # =================================================================

    # Retail Sales Invoice – فاکتور فروش خرده‌فروشی
    {
        "domain_code": DOMAIN_INDUSTRY_RETAIL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Invoice",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,  # مثل هسته، اما برای Retail صریح
        "blue_template_key": "BLUE_PRINT_SALES_INVOICE_RETAIL_V1",
        "enabled": True,
    },

    # Retail POS Invoice – پرینت A4 از POS (اگر استفاده کنی)
    {
        "domain_code": DOMAIN_INDUSTRY_RETAIL,
        "functional_area": AREA_POS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "POS Invoice",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # رسید فروشگاهی → فقط جلالی
        "blue_template_key": "BLUE_PRINT_POS_INVOICE_RETAIL_V1",
        "enabled": True,
    },

    # Retail POS Thermal Receipt – رول حرارتی
    {
        "domain_code": DOMAIN_INDUSTRY_RETAIL,
        "functional_area": AREA_POS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "POS Invoice",
        "output_type": OUT_POS_THERMAL,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_POS_THERMAL_RETAIL_V1",
        "enabled": True,
    },

    # Retail Daily Sales Summary – گزارش فروش روزانه فروشگاه
    {
        "domain_code": DOMAIN_INDUSTRY_RETAIL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_REPORT,
        "object_name": "Sales Analytics",  # اگر اسم گزارش چیز دیگری است، این را عوض کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,   # برای مدیر فروشگاه → جلالی
        "blue_template_key": "BLUE_REPORT_RETAIL_SALES_ANALYTICS_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_RETAIL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_REPORT,
        "object_name": "Sales Analytics",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,  # Export → فقط میلادی
        "blue_template_key": None,
        "enabled": True,
    },
    # =================================================================
    # INDUSTRY_SERVICES – Service Companies / Agencies / IT / Consulting
    # =================================================================

    # Service Project – برگه پروژه قابل ارسال به مشتری
    {
        "domain_code": DOMAIN_INDUSTRY_SERVICES,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Project",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,  # برای مشتری هم ارسال می‌شود
        "jdate_rule": JDATE_DUAL,  # Dual برای تطبیق حقوقی/مالی
        "blue_template_key": "BLUE_PRINT_PROJECT_SERVICES_V1",
        "enabled": True,
    },

    # Service Timesheet – تایم‌شیت برای مشتری (برخلاف CORE که داخلی بود)
    {
        "domain_code": DOMAIN_INDUSTRY_SERVICES,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Timesheet",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,  # در این دامین، Dual چون پیوست فاکتور می‌شود
        "blue_template_key": "BLUE_PRINT_TIMESHEET_SERVICES_V1",
        "enabled": True,
    },

    # Service Subscription / Contract – قرارداد خدمات دوره‌ای
    {
        "domain_code": DOMAIN_INDUSTRY_SERVICES,
        "functional_area": AREA_SUBSCRIPTIONS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Subscription",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_SUBSCRIPTION_SERVICES_V1",
        "enabled": True,
    },

    # Project Profitability – گزارش سودآوری پروژه
    {
        "domain_code": DOMAIN_INDUSTRY_SERVICES,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_REPORT,
        "object_name": "Project Profitability",  # اگر Report اسم دیگری دارد، این را تنظیم کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_REPORT_PROJECT_PROFITABILITY_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_SERVICES,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_REPORT,
        "object_name": "Project Profitability",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # =================================================================
    # INDUSTRY_HOSPITALITY – Hotels / Restaurants / Cafes
    # =================================================================

    # Guest Invoice – فاکتور مهمان (Sales Invoice در هتل/رستوران)
    {
        "domain_code": DOMAIN_INDUSTRY_HOSPITALITY,
        "functional_area": AREA_SALES,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Sales Invoice",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,  # مهمان/مشتری
        "jdate_rule": JDATE_DUAL,  # فاکتور رسمی → Dual
        "blue_template_key": "BLUE_PRINT_SALES_INVOICE_HOSPITALITY_V1",
        "enabled": True,
    },

    # Restaurant POS Invoice – رسید رستوران روی رول
    {
        "domain_code": DOMAIN_INDUSTRY_HOSPITALITY,
        "functional_area": AREA_POS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "POS Invoice",
        "output_type": OUT_POS_THERMAL,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,   # روی میز مهمان → فقط جلالی
        "blue_template_key": "BLUE_PRINT_POS_THERMAL_HOSPITALITY_V1",
        "enabled": True,
    },

    # Room Booking / Reservation – رزرو اتاق/میز (نام DocType را با واقعی عوض کن)
    {
        "domain_code": DOMAIN_INDUSTRY_HOSPITALITY,
        "functional_area": AREA_GENERAL,   # می‌توانی بعداً AREA_PROJECTS یا چیز دیگر بگذاری
        "object_type": OBJ_DOCTYPE,
        "object_name": "Reservation",      # TODO: اسم DocType واقعی Hospitality را اینجا بگذار
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_DUAL,          # تاریخ ورود/خروج/رزرو → Dual
        "blue_template_key": "BLUE_PRINT_RESERVATION_HOSPITALITY_V1",
        "enabled": True,
    },

    # Daily Hospitality Sales – گزارش فروش/اشغال روزانه
    {
        "domain_code": DOMAIN_INDUSTRY_HOSPITALITY,
        "functional_area": AREA_SALES,
        "object_type": OBJ_REPORT,
        "object_name": "Hospitality Daily Sales",  # نام گزارش واقعی را جایگزین کن
        "output_type": OUT_REPORT_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,    # برای مدیر شیفت/هتل → جلالی
        "blue_template_key": "BLUE_REPORT_HOSPITALITY_DAILY_SALES_V1",
        "enabled": True,
    },
    {
        "domain_code": DOMAIN_INDUSTRY_HOSPITALITY,
        "functional_area": AREA_SALES,
        "object_type": OBJ_REPORT,
        "object_name": "Hospitality Daily Sales",
        "output_type": OUT_REPORT_EXPORT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_GREGORIAN_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
    # =================================================================
    # CORE_GLOBAL / WEBSITE & E-COMMERCE – FRONTEND UI PAGES
    # =================================================================
    # Product Detail Page – صفحه محصول (Website Item)
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Website Item",   # صفحه جزئیات محصول
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,  # UI فارسی → فقط شمسی
        "blue_template_key": "BLUE_WEB_PRODUCT_PAGE_V1",
        "enabled": True,
    },

    # Product Listing / Category – لیست محصولات
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Product Listing",  # لیست/شبکه محصولات
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_WEB_PRODUCT_LISTING_V1",
        "enabled": True,
    },

    # Shopping Cart – سبد خرید
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Shopping Cart",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # تاریخ تحویل تخمینی و ... → شمسی
        "blue_template_key": "BLUE_WEB_CART_V1",
        "enabled": True,
    },

    # Checkout Page – صفحه نهایی‌سازی خرید
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Checkout",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # UI فقط جلالی
        "blue_template_key": "BLUE_WEB_CHECKOUT_V1",
        "enabled": True,
    },

    # Order Confirmation Page – صفحه تأیید سفارش بعد از پرداخت
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Order Confirmation",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_WEB_ORDER_CONFIRMATION_V1",
        "enabled": True,
    },

    # My Orders – صفحه لیست سفارشات کاربر در وب
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_SALES,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "My Orders",   # صفحه "سفارشات من"
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # تاریخ سفارش/تحویل در UI → جلالی
        "blue_template_key": "BLUE_PORTAL_MY_ORDERS_V1",
        "enabled": True,
    },

    # Blog Post – صفحه مقاله/بلاگ
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Blog Post",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # تاریخ انتشار برای کاربر فارسی → شمسی
        "blue_template_key": "BLUE_WEB_BLOG_POST_V1",
        "enabled": True,
    },

    # Event Page – صفحه رویداد در وب‌سایت
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_PORTAL_PAGE,
        "object_name": "Event",
        "output_type": OUT_PORTAL_PAGE,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # تاریخ/ساعت رویداد در UI → جلالی
        "blue_template_key": "BLUE_WEB_EVENT_V1",
        "enabled": True,
    },

    # Event Registration Web Form – فرم ثبت‌نام رویداد
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_WEBSITE,
        "object_type": OBJ_WEB_FORM,
        "object_name": "Event Registration",
        "output_type": OUT_WEB_FORM,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,          # مهلت، تاریخ رویداد در فرم → جلالی
        "blue_template_key": "BLUE_WEBFORM_EVENT_REGISTRATION_V1",
        "enabled": True,
    },
    # -----------------
    # POS
    # -----------------
    # POS Invoice - رسید فروشگاهی / حرارتی
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_POS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "POS Invoice",
        "output_type": OUT_POS_THERMAL,
        "audience": AUD_EXTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_POS_INVOICE_V1",
        "enabled": True,
    },
    # -----------------
    # HR / PAYROLL
    # -----------------
    # Salary Slip
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PAYROLL,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Salary Slip",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,  # فیش حقوق: جلالی اصلی + میلادی کوچک اگر خواستی
        "blue_template_key": "BLUE_PRINT_SALARY_SLIP_V1",
        "enabled": True,
    },

    # Payroll Entry
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PAYROLL,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Payroll Entry",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_DUAL,
        "blue_template_key": "BLUE_PRINT_PAYROLL_ENTRY_V1",
        "enabled": True,
    },

    # Leave Application
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Leave Application",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_LEAVE_APPLICATION_V1",
        "enabled": True,
    },

    # Employee Profile
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Employee",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_EMPLOYEE_V1",
        "enabled": True,
    },

    # Expense Claim
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Expense Claim",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_EXPENSE_CLAIM_V1",
        "enabled": True,
    },

    # Attendance
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_HR,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Attendance",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_ATTENDANCE_V1",
        "enabled": True,
    },

    # Timesheet
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PROJECTS,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Timesheet",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_TIMESHEET_V1",
        "enabled": True,
    },

    # Employee Advance
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_PAYROLL,
        "object_type": OBJ_DOCTYPE,
        "object_name": "Employee Advance",
        "output_type": OUT_DOC_PRINT,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_EMPLOYEE_ADVANCE_V1",
        "enabled": True,
    },

    # -----------------
    # Desk / Frontend-only views (CAL Boot)
    # -----------------

    # Dashboard / Charts / Calendar / Gantt / Kanban → همیشه J4
    {
        "domain_code": DOMAIN_CORE_GLOBAL,
        "functional_area": AREA_GENERAL,
        "object_type": OBJ_REPORT,
        "object_name": "*DESK*",
        "output_type": OUT_DASHBOARD_VIEW,
        "audience": AUD_INTERNAL,
        "jdate_rule": JDATE_FRONTEND_ONLY,
        "blue_template_key": None,
        "enabled": True,
    },
]
def find_jdate_policy(
    domain_code: str,
    functional_area: str,
    object_type: str,
    object_name: str,
    output_type: str,
    audience: str | None = None,
):
    """
    جستجوی ساده در ماتریس JDATE_POLICY_MATRIX.
    - اولویت: دامین دقیق > CORE_GLOBAL
    - امتیازدهی: domain + area + audience برای انتخاب بهترین ردیف
    - خروجی: dict کامل ردیف (یا None اگر پیدا نشد)
    """

    best_row = None
    best_score = -1

    for row in JDATE_POLICY_MATRIX:
        if not row.get("enabled", True):
            continue

        if row["object_type"] != object_type:
            continue

        # نام سند/ریپورت: تطبیق کامل؛ می‌توانی بعداً wildcard اضافه کنی
        if row["object_name"] != object_name:
            continue

        if row["output_type"] != output_type:
            continue

        score = 0

        # Domain: exact > CORE_GLOBAL
        if row["domain_code"] == domain_code:
            score += 4
        elif row["domain_code"] == DOMAIN_CORE_GLOBAL:
            score += 1
        else:
            continue  # دامین نامرتبط

        # Functional area
        if row["functional_area"] == functional_area:
            score += 2

        # Audience
        if audience and row.get("audience") == audience:
            score += 1

        if score > best_score:
            best_score = score
            best_row = row

    return best_row

def get_jdate_policy(
    domain_code: str,
    functional_area: str,
    object_type: str,
    object_name: str,
    output_type: str,
    audience: str | None = None,
) -> dict[str, Any] | None:
    """
    Wrapper ساده روی find_jdate_policy برای استفادهٔ عمومی (داخل اپ‌ها / API / تست).

    خروجی نمونه:
    {
        "jdate_rule": "J2",
        "blue_template_key": "BLUE_PRINT_SALES_INVOICE_V1",
        "domain_code": "...",
        "functional_area": "...",
        ...
    }
    یا None اگر Policy پیدا نشود.
    """
    row = find_jdate_policy(
        domain_code=domain_code,
        functional_area=functional_area,
        object_type=object_type,
        object_name=object_name,
        output_type=output_type,
        audience=audience,
    )

    if not row:
        return None

    # یک کپی برگردانیم تا جای دیگر دستکاری‌اش نکنند
    return dict(row)
@frappe.whitelist()
def debug_jdate_policy(
    domain_code: str,
    functional_area: str,
    object_type: str,
    object_name: str,
    output_type: str,
    audience: str | None = None,
):
    """
    تست Policy از طریق API/Bench.

    مثال Bench:
      bench --site baba.bluehesab.ir execute blue_jdate.utils.debug_jdate_policy \
        --kwargs '{"domain_code": "CORE_GLOBAL", "functional_area": "SALES", "object_type": "DocType", "object_name": "Sales Invoice", "output_type": "DOC_PRINT", "audience": "EXTERNAL"}'
    """
    policy = get_jdate_policy(
        domain_code=domain_code,
        functional_area=functional_area,
        object_type=object_type,
        object_name=object_name,
        output_type=output_type,
        audience=audience,
    )
    return policy or {}