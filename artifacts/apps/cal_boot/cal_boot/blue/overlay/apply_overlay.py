import json
import pathlib
import frappe

# --- Paths relative to this file ---
BASE = pathlib.Path(__file__).resolve().parent / "fixtures"
TR_PATH = BASE / "translations_fa.canon.json"
PS_PATH = BASE / "property_setter_naming_series_fa.json"

# الگوهای انگلیسی (substring) → ترجمه فارسی
LABEL_PATTERNS = {
    # Attendance
    "EARLY EXIT": "خروج زودهنگام (این ماه)",
    "LATE ENTRY": "ورود دیرهنگام (این ماه)",
    "TOTAL ABSENT": "کل غیبت‌ها (این ماه)",
    "TOTAL PRESENT": "کل حضورها (این ماه)",

    # Sales
    "ACTIVE CUSTOMERS": "مشتریان فعال",
    "ANNUAL SALES": "فروش سالانه",

    # CRM
    "OPEN OPPORTUNITY": "فرصت‌های باز",
    "WON OPPORTUNITY": "فرصت‌های برنده‌شده (ماه گذشته)",
    "NEW OPPORTUNITY": "فرصت‌های جدید (ماه گذشته)",
    "NEW LEAD": "سرنخ‌های جدید (ماه گذشته)",
    "NEW LEADS": "سرنخ‌های جدید (ماه گذشته)",

    # Manufacturing
    "MONTHLY QUALITY INSPECTION": "بازرسی کیفیت ماهانه",
    "ONGOING JOB CARD": "کارت‌های کار در حال انجام",
    "MONTHLY COMPLETED WORK ORDER": "سفارش‌های تولید تکمیل‌شده ماهانه",
    "MONTHLY TOTAL WORK ORDER": "مجموع سفارش‌های تولید ماهانه",

    # Human Resource
    "NEW HIRES": "استخدام‌های جدید (امسال)",
    "TOTAL EMPLOYEES": "کل کارکنان",

    # Expense Claims
    "REJECTED CLAIMS": "درخواست‌های ردشده (این ماه)",
    "APPROVED CLAIMS": "درخواست‌های تأییدشده (این ماه)",
    "EXPENSE CLAIMS": "درخواست‌های هزینه (این ماه)",

    # Recruitment
    "REJECTED JOB APPLICANTS": "متقاضیان شغل ردشده",
    "ACCEPTED JOB APPLICANTS": "متقاضیان شغل پذیرفته‌شده",
    "TOTAL APPLICANTS": "کل متقاضیان (این ماه)",
    "JOB OFFER ACCEPTANCE RATE": "نرخ پذیرش پیشنهاد شغلی",
    "APPLICANT-TO-HIRE PERCENTAGE": "درصد تبدیل متقاضی به استخدام",
    "JOB OFFERS": "پیشنهادهای شغلی (این ماه)",

    # Employee Lifecycle
    "TRANSFERS (THIS MONTH)": "انتقال‌ها (این ماه)",
    "PROMOTIONS (THIS MONTH)": "ارتقاها (این ماه)",
    "SEPARATIONS (THIS MONTH)": "قطع همکاری‌ها (این ماه)",
    "ONBOARDINGS (THIS MONTH)": "استخدام‌های جدید (این ماه)",
    "TRAININGS (THIS MONTH)": "آموزش‌ها (این ماه)",

    # Payroll
    "TOTAL OUTGOING SALARY": "کل حقوق پرداختی (ماه گذشته)",
    "TOTAL INCENTIVE GIVEN": "کل پاداش پرداختی (ماه گذشته)",
    "TOTAL SALARY STRUCTURE": "مجموع ساختارهای حقوق و دستمزد",
    "TOTAL DECLARATION SUBMITTED": "کل اظهارنامه‌های ثبت‌شده",

    # Workspace menu
    "EXPENSE CLAIMS": "درخواست‌های هزینه",
    "RECRUITMENT": "استخدام",
    "PAYROLL": "حقوق و دستمزد",
    "EMPLOYEE LIFECYCLE": "چرخه حیات کارمند",
    "ATTENDANCE": "حضور و غیاب",
    "PROJECT": "پروژه",
    "SELLING": "فروش",
    "STOCK": "انبار",
    "ACCOUNTS": "حسابداری",
    "BUYING": "خرید",
    "CRM": "مدیریت ارتباط با مشتری",
    "ASSET": "دارایی‌ها",
    "MANUFACTURING": "تولید",
}


def resolve_label(label: str) -> str | None:
    """از روی substring انگلیسی، ترجمه را برمی‌گرداند."""
    if not label:
        return None
    u = label.upper()
    for pat, fa in LABEL_PATTERNS.items():
        if pat in u:
            return fa
    return None


def upsert_translation(doc):
    lang = (doc.get("language") or "fa").strip()
    src = (doc.get("source_text") or "").strip()
    fa = (doc.get("translated_text") or "").strip()

    if not src or not fa:
        return False

    name = frappe.db.get_value(
        "Translation",
        {"language": lang, "source_text": src},
        "name",
    )

    if name:
        d = frappe.get_doc("Translation", name)
        old = (d.translated_text or "").strip()
        if old != fa:
            d.translated_text = fa
            d.save(ignore_permissions=True)
            return True
        return False

    frappe.get_doc({
        "doctype": "Translation",
        "language": lang,
        "source_text": src,
        "translated_text": fa,
    }).insert(ignore_permissions=True)
    return True


def upsert_prop_setter(doc):
    key = {
        "doc_type": doc.get("doc_type"),
        "field_name": doc.get("field_name"),
        "property": doc.get("property"),
        "doctype_or_field": doc.get("doctype_or_field") or "DocField",
    }
    if not all(key.values()):
        return False

    name = frappe.db.get_value("Property Setter", key, "name")
    if name:
        ps = frappe.get_doc("Property Setter", name)
        changed = False
        val = doc.get("value")
        ptype = doc.get("property_type")

        if val is not None and ps.value != val:
            ps.value = val
            changed = True
        if ptype and ps.property_type != ptype:
            ps.property_type = ptype
            changed = True

        if changed:
            ps.save(ignore_permissions=True)
        return changed

    ins = {
        "doctype": "Property Setter",
        **key,
        "value": doc.get("value"),
        "property_type": doc.get("property_type") or "Data",
    }
    frappe.get_doc(ins).insert(ignore_permissions=True)
    return True


def patch_labels():
    """
    بر اساس LABEL_PATTERNS، برچسب‌ها را در جاهای مختلف فارسی می‌کنیم:
    - Number Card.label
    - Dashboard Chart.chart_name
    - Workspace.label
    - Workspace Number Card.label
    - Workspace Chart.label
    - Workspace Shortcut.label
    - Workspace Link.label
    """
    nc_patched = 0
    ch_patched = 0
    ws_patched = 0
    wnc_patched = 0
    wch_patched = 0
    wsc_patched = 0
    wln_patched = 0

    # Number Card
    for row in frappe.get_all("Number Card", fields=["name", "label"]):
        label = (row.get("label") or "").strip()
        fa = resolve_label(label)
        if fa and label != fa:
            frappe.db.set_value("Number Card", row["name"], "label", fa, update_modified=False)
            nc_patched += 1

    # Dashboard Chart (با چک یکتا بودن chart_name)
    for row in frappe.get_all("Dashboard Chart", fields=["name", "chart_name"]):
        label = (row.get("chart_name") or "").strip()
        fa = resolve_label(label)
        if not fa or label == fa:
            continue

        others = frappe.get_all(
            "Dashboard Chart",
            filters={"chart_name": fa},
            pluck="name",
        )
        if any(n != row["name"] for n in others):
            continue

        frappe.db.set_value(
            "Dashboard Chart",
            row["name"],
            "chart_name",
            fa,
            update_modified=False,
        )
        ch_patched += 1

    # Workspace
    for row in frappe.get_all("Workspace", fields=["name", "label"]):
        label = (row.get("label") or "").strip()
        fa = resolve_label(label)
        if fa and label != fa:
            frappe.db.set_value("Workspace", row["name"], "label", fa, update_modified=False)
            ws_patched += 1

    # Workspace Number Card
    for row in frappe.get_all("Workspace Number Card", fields=["name", "label"]):
        label = (row.get("label") or "").strip()
        fa = resolve_label(label)
        if fa and label != fa:
            frappe.db.set_value("Workspace Number Card", row["name"], "label", fa, update_modified=False)
            wnc_patched += 1

    # Workspace Chart
    for row in frappe.get_all("Workspace Chart", fields=["name", "label"]):
        label = (row.get("label") or "").strip()
        fa = resolve_label(label)
        if fa and label != fa:
            frappe.db.set_value("Workspace Chart", row["name"], "label", fa, update_modified=False)
            wch_patched += 1

    # Workspace Shortcut
    for row in frappe.get_all("Workspace Shortcut", fields=["name", "label"]):
        label = (row.get("label") or "").strip()
        fa = resolve_label(label)
        if fa and label != fa:
            frappe.db.set_value("Workspace Shortcut", row["name"], "label", fa, update_modified=False)
            wsc_patched += 1

    # Workspace Link
    for row in frappe.get_all("Workspace Link", fields=["name", "label"]):
        label = (row.get("label") or "").strip()
        fa = resolve_label(label)
        if fa and label != fa:
            frappe.db.set_value("Workspace Link", row["name"], "label", fa, update_modified=False)
            wln_patched += 1

    return nc_patched, ch_patched, ws_patched, wnc_patched, wch_patched, wsc_patched, wln_patched


def run():
    """Entry point برای bench execute."""
    applied_tr = 0
    applied_ps = 0

    # --- ترجمه‌ها از فایل کانُن ---
    if TR_PATH.exists():
        with TR_PATH.open(encoding="utf-8") as f:
            docs = json.load(f)
        for d in docs:
            if d.get("doctype") and d.get("doctype") != "Translation":
                continue
            if upsert_translation(d):
                applied_tr += 1
    else:
        print(f"[WARN] Translation file not found: {TR_PATH}")

    # --- Property Setterها ---
    if PS_PATH.exists():
        with PS_PATH.open(encoding="utf-8") as f:
            docs = json.load(f)
        for d in docs:
            if d.get("doctype") and d.get("doctype") != "Property Setter":
                continue
            if upsert_prop_setter(d):
                applied_ps += 1
    else:
        print(f"[INFO] Property Setter file not found (skipped): {PS_PATH}")

    # --- پچ برچسب‌ها ---
    (
        nc_patched,
        ch_patched,
        ws_patched,
        wnc_patched,
        wch_patched,
        wsc_patched,
        wln_patched,
    ) = patch_labels()

    frappe.db.commit()
    print(
        f"APPLIED_TRANSLATIONS={applied_tr} "
        f"APPLIED_PROPERTY_SETTERS={applied_ps} "
        f"PATCHED_NUMBER_CARDS={nc_patched} "
        f"PATCHED_DASHBOARD_CHARTS={ch_patched} "
        f"PATCHED_WORKSPACES={ws_patched} "
        f"PATCHED_WORKSPACE_NUMBER_CARDS={wnc_patched} "
        f"PATCHED_WORKSPACE_CHARTS={wch_patched} "
        f"PATCHED_WORKSPACE_SHORTCUTS={wsc_patched} "
        f"PATCHED_WORKSPACE_LINKS={wln_patched}"
    )
