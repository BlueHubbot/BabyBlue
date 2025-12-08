# -*- coding: utf-8 -*-
# blue_jdate/jdate_policy.py
#
# ماتریس سیاست‌های تقویم (JDate Policy Matrix)
# این فایل تعیین می‌کند هر خروجی چه قاعده‌ای دارد:
# J1 = Jalali only (فقط جلالی در UI/Print)
# J2 = Dual (جلالی + میلادی کنار هم)
# J3 = Gregorian only (دست‌نخورده، مخصوص Export/Regulatory)
# J4 = Frontend only (فقط CAL/JS، سرور Gregorian می‌ماند)


# -------------------------
# ثابت‌های کد قانون
# -------------------------
J1_JALALI_ONLY = "J1"
J2_DUAL = "J2"
J3_GREGORIAN_ONLY = "J3"
J4_FRONTEND_ONLY = "J4"


# -------------------------
# ستون‌های ماتریس
# -------------------------
# domain_code      : CORE_GLOBAL, INDUSTRY_HEALTHCARE, ...
# functional_area  : SALES, PURCHASE, HR, PAYROLL, STOCK, ...
# object_type      : DocType, Report, PortalPage, WebForm, ...
# object_name      : نام DocType/Report واقعی در ERPNext
# output_type      : نوع خروجی (DOC_PRINT, REPORT_PRINT, REPORT_EXPORT, ...)
# audience         : EXTERNAL, INTERNAL, OPERATIONAL, REGULATORY
# jdate_rule       : J1/J2/J3/J4
# blue_template_key: نام قالب Blue (اگر داریم)، مثلاً BLUE_PRINT_SALES_INVOICE_V1
# enabled          : 1 فعال، 0 غیر فعال


# -------------------------
# ماتریس هسته‌ی سراسری (CORE_GLOBAL)
# توجه: بعداً برای هر Industry می‌توانی ماتریس جدا اضافه کنی.
# -------------------------
POLICY_MATRIX_CORE_GLOBAL = [
    # --- SALES: سندهای فروش ---
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "SALES",
        "object_type": "DocType",
        "object_name": "Sales Invoice",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,                     # فاکتور رسمی → جلالی + میلادی
        "blue_template_key": "BLUE_PRINT_SALES_INVOICE_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "SALES",
        "object_type": "DocType",
        "object_name": "Sales Order",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,
        "blue_template_key": "BLUE_PRINT_SALES_ORDER_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "SALES",
        "object_type": "DocType",
        "object_name": "Quotation",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,
        "blue_template_key": "BLUE_PRINT_QUOTATION_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "SALES",
        "object_type": "DocType",
        "object_name": "Delivery Note",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J1_JALALI_ONLY,              # حواله برای بازار ایران → فقط جلالی کافی است
        "blue_template_key": "BLUE_PRINT_DELIVERY_NOTE_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "SALES",
        "object_type": "DocType",
        "object_name": "POS Invoice",
        "output_type": "DOC_PRINT",                # چاپ رول/برگ POS
        "audience": "EXTERNAL",
        "jdate_rule": J1_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_POS_INVOICE_V1",
        "enabled": 1,
    },

    # --- PURCHASE: سندهای خرید ---
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "PURCHASE",
        "object_type": "DocType",
        "object_name": "Purchase Invoice",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,
        "blue_template_key": "BLUE_PRINT_PURCHASE_INVOICE_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "PURCHASE",
        "object_type": "DocType",
        "object_name": "Purchase Order",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,
        "blue_template_key": "BLUE_PRINT_PURCHASE_ORDER_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "PURCHASE",
        "object_type": "DocType",
        "object_name": "Purchase Receipt",
        "output_type": "DOC_PRINT",
        "audience": "INTERNAL",                    # رسید انبار/رسید خرید → بیشتر داخلی
        "jdate_rule": J1_JALALI_ONLY,
        "blue_template_key": "BLUE_PRINT_PURCHASE_RECEIPT_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "PURCHASE",
        "object_type": "DocType",
        "object_name": "Supplier Quotation",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,
        "blue_template_key": "BLUE_PRINT_SUPPLIER_QUOTATION_V1",
        "enabled": 1,
    },

    # --- PAYMENTS / ACCOUNTS ---
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "ACCOUNTS",
        "object_type": "DocType",
        "object_name": "Payment Entry",
        "output_type": "DOC_PRINT",
        "audience": "EXTERNAL",
        "jdate_rule": J2_DUAL,                     # رسید پرداخت/دریافت → دو تاریخ
        "blue_template_key": "BLUE_PRINT_PAYMENT_ENTRY_V1",
        "enabled": 1,
    },

    # می‌توانی بعداً این‌ها را گسترش بدهی برای Statementها، Credit Note، Debit Note و...

    # --- HR / PAYROLL ---
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "PAYROLL",
        "object_type": "DocType",
        "object_name": "Salary Slip",
        "output_type": "DOC_PRINT",
        "audience": "INTERNAL",
        "jdate_rule": J2_DUAL,                     # کارمند: جلالی، حسابرسی: میلادی کوچک
        "blue_template_key": "BLUE_PRINT_SALARY_SLIP_V1",
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "PAYROLL",
        "object_type": "DocType",
        "object_name": "Payroll Entry",
        "output_type": "DOC_PRINT",
        "audience": "INTERNAL",
        "jdate_rule": J2_DUAL,
        "blue_template_key": "BLUE_PRINT_PAYROLL_ENTRY_V1",
        "enabled": 1,
    },

    # --- REPORTS: نمونه برای هسته‌ی مالی/انبار ---
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "ACCOUNTS",
        "object_type": "Report",
        "object_name": "General Ledger",
        "output_type": "REPORT_PRINT",             # چاپ PDF از گزارش GL
        "audience": "INTERNAL",
        "jdate_rule": J2_DUAL,                     # گزارش مالی داخلی → دو تاریخ
        "blue_template_key": None,
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "ACCOUNTS",
        "object_type": "Report",
        "object_name": "General Ledger",
        "output_type": "REPORT_EXPORT",            # Export به Excel/CSV
        "audience": "INTERNAL",
        "jdate_rule": J3_GREGORIAN_ONLY,           # داده خام، همیشه میلادی
        "blue_template_key": None,
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "STOCK",
        "object_type": "Report",
        "object_name": "Stock Ledger",
        "output_type": "REPORT_PRINT",
        "audience": "INTERNAL",
        "jdate_rule": J1_JALALI_ONLY,
        "blue_template_key": None,
        "enabled": 1,
    },
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "STOCK",
        "object_type": "Report",
        "object_name": "Stock Ledger",
        "output_type": "REPORT_EXPORT",
        "audience": "INTERNAL",
        "jdate_rule": J3_GREGORIAN_ONLY,           # داده برای Excel/BI → میلادی
        "blue_template_key": None,
        "enabled": 1,
    },

    # --- DASHBOARD / DESK (فقط Frontend) ---
    {
        "domain_code": "CORE_GLOBAL",
        "functional_area": "ACCOUNTS",
        "object_type": "Dashboard",
        "object_name": "Accounting Dashboard",
        "output_type": "DASHBOARD_VIEW",
        "audience": "INTERNAL",
        "jdate_rule": J4_FRONTEND_ONLY,            # فقط CAL/JS، سرور دست‌نخورده
        "blue_template_key": None,
        "enabled": 1,
    },

    # همین الگو را می‌توانی بعداً برای سایر Dashboardها/Charts طبق نیاز تکمیل کنی.
]


def _iter_all_rows():
    """در صورت اضافه شدن ماتریس‌های دامنه‌ای (مثلاً INDUSTRY_HEALTHCARE)،
    اینجا همه را yield کن."""
    for row in POLICY_MATRIX_CORE_GLOBAL:
        yield row
    # بعداً:
    # for row in POLICY_MATRIX_HEALTHCARE: yield row
    # for row in POLICY_MATRIX_EDUCATION: yield row
    # ...


def find_jdate_rule(
    domain_code: str,
    functional_area: str,
    object_type: str,
    object_name: str,
    output_type: str,
) -> dict | None:
    """جستجوی ردیف سیاست بر اساس کلیدهای اصلی.

    ترتیب اولویت:
    1) تطبیق کامل روی همه ستون‌ها
    2) اگر چیزی پیدا نشد، تلاش با CORE_GLOBAL به جای domain_code
    3) اگر باز هم نبود، None (یعنی: سیاست تعریف نشده → رفتار پیش‌فرض)
    """
    domain_code = (domain_code or "").upper() or "CORE_GLOBAL"
    functional_area = (functional_area or "").upper()
    object_type = (object_type or "").strip()
    object_name = (object_name or "").strip()
    output_type = (output_type or "").upper()

    # 1) تلاش برای تطبیق دقیق
    for row in _iter_all_rows():
        if not row.get("enabled"):
            continue
        if (
            row["domain_code"] == domain_code
            and row["functional_area"] == functional_area
            and row["object_type"] == object_type
            and row["object_name"] == object_name
            and row["output_type"] == output_type
        ):
            return row

    # 2) تلاش با CORE_GLOBAL اگر domain خاص بود
    if domain_code != "CORE_GLOBAL":
        for row in _iter_all_rows():
            if not row.get("enabled"):
                continue
            if (
                row["domain_code"] == "CORE_GLOBAL"
                and row["functional_area"] == functional_area
                and row["object_type"] == object_type
                and row["object_name"] == object_name
                and row["output_type"] == output_type
            ):
                return row

    # هیچ سیاستی تعریف نشده
    return None


def resolve_jdate_rule(
    domain_code: str,
    functional_area: str,
    object_type: str,
    object_name: str,
    output_type: str,
    default_rule: str | None = None,
) -> str | None:
    """فقط کد قانون JDate را برمی‌گرداند (J1/J2/J3/J4 یا default)."""
    row = find_jdate_rule(
        domain_code=domain_code,
        functional_area=functional_area,
        object_type=object_type,
        object_name=object_name,
        output_type=output_type,
    )
    if row:
        return row.get("jdate_rule")
    return default_rule
