from __future__ import annotations

import frappe
from frappe import _

# BLUE Outputs – DocType Print builders (auto-extracted from utils.py)
# Each function creates/updates a custom Jinja Print Format.

def create_blue_print_asset_movement_v1():
    """Create/Update BLUE_PRINT_ASSET_MOVEMENT_V1 for Asset Movement."""
    NAME = "BLUE_PRINT_ASSET_MOVEMENT_V1"
    DOCTYPE = "Asset Movement"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-idx        { width: 6%;  text-align: center; }
  .bapi-items-asset      { width: 20%; text-align: right; }
  .bapi-items-name       { width: 26%; text-align: right; }
  .bapi-items-from       { width: 18%; text-align: right; }
  .bapi-items-to         { width: 18%; text-align: right; }
  .bapi-items-ref        { width: 12%; text-align: left; }

  .bapi-remarks-block {
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">فرم جابجایی دارایی</div>
  <div class="bapi-subtitle">
    ثبت جابجایی دارایی‌ها بین محل‌ها / واحدها در سیستم بلوحساب / BlueHesab.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره فرم:</span>
          {{ doc.name }}
        </div>
        {% if doc.transaction_date %}
        <div>
          <span class="bapi-meta-label">تاریخ جابجایی:</span>
          {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.purpose %}
        <div>
          <span class="bapi-meta-label">هدف جابجایی:</span>
          {{ doc.purpose }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مبدأ</th>
      <th>مقصد</th>
    </tr>
    <tr>
      <td>
        {% if doc.source_location %}
          <div><strong>محل مبدأ:</strong> {{ doc.source_location }}</div>
        {% endif %}
        {% if doc.from_department %}
          <div><strong>واحد / دپارتمان مبدأ:</strong> {{ doc.from_department }}</div>
        {% endif %}
        {% if doc.from_employee %}
          <div><strong>مسئول تحویل‌دهنده:</strong> {{ doc.from_employee_name or doc.from_employee }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.target_location %}
          <div><strong>محل مقصد:</strong> {{ doc.target_location }}</div>
        {% endif %}
        {% if doc.to_department %}
          <div><strong>واحد / دپارتمان مقصد:</strong> {{ doc.to_department }}</div>
        {% endif %}
        {% if doc.to_employee %}
          <div><strong>مسئول تحویل‌گیرنده:</strong> {{ doc.to_employee_name or doc.to_employee }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-asset">کد دارایی</th>
        <th class="bapi-items-name">عنوان دارایی</th>
        <th class="bapi-items-from">محل / واحد قبلی</th>
        <th class="bapi-items-to">محل / واحد جدید</th>
        <th class="bapi-items-ref">سریال / مرجع</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.assets %}
        {% for row in doc.assets %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-asset">
            {{ row.asset or "" }}
          </td>
          <td class="bapi-items-name">
            {{ row.asset_name or row.asset or "" }}
          </td>
          <td class="bapi-items-from">
            {% if row.from_location %}
              {{ row.from_location }}
            {% elif row.source_location %}
              {{ row.source_location }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-items-to">
            {% if row.to_location %}
              {{ row.to_location }}
            {% elif row.target_location %}
              {{ row.target_location }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-items-ref">
            {% if row.serial_no %}
              {{ row.serial_no }}
            {% elif row.reference_name %}
              {{ row.reference_name }}
            {% else %}
              -
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#777;">
            هیچ قلمی برای جابجایی دارایی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات / شرایط تحویل:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>مسئول تحویل‌دهنده (مبدأ)</td>
      <td>مسئول تحویل‌گیرنده (مقصد)</td>
      <td>تأیید واحد دارایی‌ها / حسابداری</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_asset_repair_v1():
    """Create/Update BLUE_PRINT_ASSET_REPAIR_V1 for Asset Repair."""
    NAME = "BLUE_PRINT_ASSET_REPAIR_V1"
    DOCTYPE = "Asset Repair"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-type  { width: 10%; text-align: center; }
  .bapi-items-item  { width: 26%; text-align: right; }
  .bapi-items-qty   { width: 10%; text-align: center; }
  .bapi-items-rate  { width: 16%; text-align: left; }
  .bapi-items-amt   { width: 16%; text-align: left; }
  .bapi-items-note  { width: 16%; text-align: right; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 3px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">گزارش تعمیر دارایی</div>
  <div class="bapi-subtitle">
    جزئیات عملیات تعمیر و هزینه‌های مرتبط با دارایی در سیستم بلوحساب / BlueHesab.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره تعمیر:</span>
          {{ doc.name }}
        </div>
        {% if doc.completion_date %}
        <div>
          <span class="bapi-meta-label">تاریخ اتمام:</span>
          {{ doc.completion_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% elif doc.repair_date %}
        <div>
          <span class="bapi-meta-label">تاریخ تعمیر:</span>
          {{ doc.repair_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.asset %}
        <div>
          <span class="bapi-meta-label">کد دارایی:</span>
          {{ doc.asset }}
        </div>
        {% endif %}
        {% if doc.asset_name %}
        <div>
          <span class="bapi-meta-label">عنوان دارایی:</span>
          {{ doc.asset_name }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>اطلاعات تعمیر</th>
      <th>اطلاعات مالی</th>
    </tr>
    <tr>
      <td>
        {% if doc.service_person %}
          <div><strong>تکنسین / پیمانکار:</strong> {{ doc.service_person }}</div>
        {% endif %}
        {% if doc.repair_type %}
          <div><strong>نوع تعمیر:</strong> {{ doc.repair_type }}</div>
        {% endif %}
        {% if doc.downtime_hours %}
          <div><strong>مدت خواب دارایی (ساعت):</strong> {{ doc.downtime_hours }}</div>
        {% endif %}
        {% if doc.warranty_status %}
          <div><strong>وضعیت گارانتی:</strong> {{ doc.warranty_status }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.repair_cost %}
          <div>
            <strong>جمع هزینه تعمیر (ریال):</strong>
            {{ "{:,.0f}".format(doc.repair_cost or 0) }}
          </div>
        {% endif %}
        {% if doc.increase_in_value %}
          <div>
            <strong>افزایش ارزش دارایی (سرمایه‌ای):</strong>
            {{ "{:,.0f}".format(doc.increase_in_value or 0) }}
          </div>
        {% endif %}
        {% if doc.expense_amount %}
          <div>
            <strong>هزینه شناسایی‌شده (جاری):</strong>
            {{ "{:,.0f}".format(doc.expense_amount or 0) }}
          </div>
        {% endif %}
      </td>
    </tr>
  </table>

  {% set rows = doc.get("items") or doc.get("repair_items") or doc.get("stock_items") or [] %}

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-type">نوع</th>
        <th class="bapi-items-item">شرح قطعه / خدمت</th>
        <th class="bapi-items-qty">تعداد / ساعت</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">مبلغ (ریال)</th>
        <th class="bapi-items-note">توضیحات</th>
      </tr>
    </thead>
    <tbody>
      {% if rows %}
        {% for row in rows %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-type">
            {% if row.item_type %}
              {{ row.item_type }}
            {% elif row.is_service %}
              خدمت
            {% else %}
              قطعه
            {% endif %}
          </td>
          <td class="bapi-items-item">
            {{ row.item_name or row.description or row.item_code or "" }}
          </td>
          <td class="bapi-items-qty">
            {{ row.qty or row.hours or "" }}
          </td>
          <td class="bapi-items-rate">
            {{ "{:,.0f}".format(row.rate or 0) }}
          </td>
          <td class="bapi-items-amt">
            {{ "{:,.0f}".format(row.amount or row.base_amount or 0) }}
          </td>
          <td class="bapi-items-note">
            {% if row.note %}
              {{ row.note }}
            {% else %}
              &nbsp;
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ قلمی برای تعمیر / قطعات ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">جمع هزینه تعمیر:</td>
      <td class="bapi-summary-value">
        ریال {{ "{:,.0f}".format(doc.repair_cost or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-summary-label">جمع هزینه به حروف (تقریبی):</td>
      <td class="bapi-summary-value">
        {% set total_cost = doc.repair_cost or 0 %}
        {% if total_cost and total_cost > 0 %}
          {{ total_cost | money_to_words_fa("IRR") }}
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرح مشکل و اقدامات انجام‌شده:</div>
    <div class="bapi-remarks-box">
      {% if doc.problem_description %}
        <strong>مشکل گزارش‌شده:</strong> {{ doc.problem_description }}<br>
      {% endif %}
      {% if doc.work_done %}
        <strong>اقدامات انجام‌شده:</strong> {{ doc.work_done }}<br>
      {% endif %}
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        <strong>توضیحات تکمیلی:</strong> {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>درخواست‌کننده تعمیر</td>
      <td>تکنسین / پیمانکار</td>
      <td>تأیید واحد دارایی‌ها / مالی</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_asset_v1():
    """Create/Update BLUE_PRINT_ASSET_V1 for Asset."""
    NAME = "BLUE_PRINT_ASSET_V1"
    DOCTYPE = "Asset"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-summary-table {
    width: 100%;
    margin-top: 10px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 2px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">کارت دارایی ثابت</div>
  <div class="bapi-subtitle">
    مشخصات ثبت‌شده برای این دارایی در سیستم بلوحساب / BlueHesab.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">کد دارایی:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">عنوان دارایی:</span>
          {{ doc.asset_name or "" }}
        </div>
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>اطلاعات طبقه‌بندی</th>
      <th>اطلاعات خرید و ارزش</th>
    </tr>
    <tr>
      <td>
        {% if doc.asset_category %}
          <div><strong>گروه دارایی:</strong> {{ doc.asset_category }}</div>
        {% endif %}
        {% if doc.asset_location %}
          <div><strong>محل نگهداری:</strong> {{ doc.asset_location }}</div>
        {% elif doc.location %}
          <div><strong>محل نگهداری:</strong> {{ doc.location }}</div>
        {% endif %}
        {% if doc.department %}
          <div><strong>واحد / دپارتمان استفاده‌کننده:</strong> {{ doc.department }}</div>
        {% endif %}
        {% if doc.serial_no %}
          <div><strong>سریال / شناسه داخلی:</strong> {{ doc.serial_no }}</div>
        {% endif %}
        {% if doc.asset_tag %}
          <div><strong>برچسب دارایی:</strong> {{ doc.asset_tag }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.purchase_date %}
          <div>
            <strong>تاریخ خرید:</strong>
            {{ doc.purchase_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.purchase_invoice %}
          <div><strong>فاکتور خرید:</strong> {{ doc.purchase_invoice }}</div>
        {% endif %}
        {% if doc.gross_purchase_amount %}
          <div>
            <strong>بهای تمام‌شده (ریال):</strong>
            {{ "{:,.0f}".format(doc.gross_purchase_amount or 0) }}
          </div>
        {% endif %}
        {% if doc.opening_accumulated_depreciation %}
          <div>
            <strong>استهلاک انباشته اولیه:</strong>
            {{ "{:,.0f}".format(doc.opening_accumulated_depreciation or 0) }}
          </div>
        {% endif %}
        {% if doc.value_after_depreciation %}
          <div>
            <strong>ارزش دفتری فعلی:</strong>
            {{ "{:,.0f}".format(doc.value_after_depreciation or 0) }}
          </div>
        {% elif doc.book_value %}
          <div>
            <strong>ارزش دفتری فعلی:</strong>
            {{ "{:,.0f}".format(doc.book_value or 0) }}
          </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-info-table">
    <tr>
      <th>اطلاعات استهلاک</th>
      <th>سایر جزئیات</th>
    </tr>
    <tr>
      <td>
        {% if doc.depreciation_start_date %}
          <div>
            <strong>تاریخ شروع استهلاک:</strong>
            {{ doc.depreciation_start_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.total_number_of_depreciations %}
          <div>
            <strong>تعداد کل دوره‌های استهلاک:</strong>
            {{ doc.total_number_of_depreciations }}
          </div>
        {% endif %}
        {% if doc.expected_value %}
          <div>
            <strong>ارزش اسقاط (پایان عمر مفید):</strong>
            {{ "{:,.0f}".format(doc.expected_value or 0) }}
          </div>
        {% endif %}
      </td>
      <td>
        {% if doc.supplier %}
          <div><strong>تأمین‌کننده:</strong> {{ doc.supplier }}</div>
        {% endif %}
        {% if doc.asset_owner %}
          <div><strong>مالک دارایی:</strong> {{ doc.asset_owner }}</div>
        {% endif %}
        {% if doc.insurance_company %}
          <div><strong>شرکت بیمه:</strong> {{ doc.insurance_company }}</div>
        {% endif %}
        {% if doc.insurance_expiry_date %}
          <div>
            <strong>پایان بیمه:</strong>
            {{ doc.insurance_expiry_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">ارزش دفتری به حروف (تقریبی):</td>
      <td class="bapi-summary-value">
        {% set book_val = doc.value_after_depreciation or doc.book_value or 0 %}
        {% if book_val and book_val > 0 %}
          {{ book_val | money_to_words_fa("IRR") }}
          <br>(ریال {{ "{:,.0f}".format(book_val) }})
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات / وضعیت فیزیکی دارایی:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تهیه‌کننده / واحد دارایی‌ها</td>
      <td>مدیر واحد استفاده‌کننده</td>
      <td>تأیید مدیریت مالی</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_attendance_v1():
    """
    قالب چاپ «حضور و غیاب» برای DocType = Attendance
    - تاریخ‌ها: فقط جلالی (J1)
    - تمرکز روی یک روز / یک رکورد حضور
    """

    NAME = "BLUE_PRINT_ATTENDANCE_V1"
    DOCTYPE = "Attendance"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8.5pt;
    margin-right: 4px;
  }

  .bapi-status-present {
    background-color: #d4edda;
    color: #155724;
  }

  .bapi-status-absent {
    background-color: #f8d7da;
    color: #721c24;
  }

  .bapi-status-leave {
    background-color: #fff3cd;
    color: #856404;
  }

  .bapi-status-other {
    background-color: #e2e3e5;
    color: #383d41;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-row {
    margin-bottom: 4px;
  }

  .bapi-label {
    display: inline-block;
    min-width: 100px;
    font-weight: 600;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 30px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">برگ حضور و غیاب</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") if doc.posting_date else doc.attendance_date | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">تاریخ حضور:</span>
          {{ doc.attendance_date | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {% set st = doc.status or "" %}
          {% if st == "Present" %}
            <span class="bapi-status-pill bapi-status-present">حاضر</span>
          {% elif st == "Absent" %}
            <span class="bapi-status-pill bapi-status-absent">غایب</span>
          {% elif st in ["On Leave", "Half Day"] %}
            <span class="bapi-status-pill bapi-status-leave">{{ st }}</span>
          {% else %}
            <span class="bapi-status-pill bapi-status-other">{{ st }}</span>
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>مشخصات کارمند</th>
      <th>جزئیات حضور</th>
    </tr>
    <tr>
      <td>
        <div class="bapi-row">
          <span class="bapi-label">نام کارمند:</span>
          <span>{{ doc.employee_name or doc.employee }}</span>
        </div>
        <div class="bapi-row">
          <span class="bapi-label">کد کارمند:</span>
          <span>{{ doc.employee }}</span>
        </div>
        {% if doc.company %}
        <div class="bapi-row">
          <span class="bapi-label">شرکت:</span>
          <span>{{ doc.company }}</span>
        </div>
        {% endif %}
        {% if doc.department %}
        <div class="bapi-row">
          <span class="bapi-label">واحد سازمانی:</span>
          <span>{{ doc.department }}</span>
        </div>
        {% endif %}
      </td>
      <td>
        {% if doc.shift %}
        <div class="bapi-row">
          <span class="bapi-label">شیفت:</span>
          <span>{{ doc.shift }}</span>
        </div>
        {% endif %}
        {% if doc.working_hours %}
        <div class="bapi-row">
          <span class="bapi-label">ساعات کارکرد:</span>
          <span>{{ doc.working_hours }}</span>
        </div>
        {% endif %}
        {% if doc.late_entry %}
        <div class="bapi-row">
          <span class="bapi-label">ورود دیرهنگام:</span>
          <span>بله</span>
        </div>
        {% endif %}
        {% if doc.early_exit %}
        <div class="bapi-row">
          <span class="bapi-label">خروج زودهنگام:</span>
          <span>بله</span>
        </div>
        {% endif %}
        {% if doc.leave_type %}
        <div class="bapi-row">
          <span class="bapi-label">نوع مرخصی (در صورت غیبت):</span>
          <span>{{ doc.leave_type }}</span>
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء کارمند</td>
      <td>امضاء سرپرست</td>
      <td>امضاء واحد منابع انسانی</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_bom_v1():
    """Create/Update BLUE_PRINT_BOM_V1 for BOM."""
    NAME = "BLUE_PRINT_BOM_V1"
    DOCTYPE = "BOM"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-code  { width: 18%; }
  .bapi-items-desc  { width: 36%; }
  .bapi-items-qty   { width: 10%; text-align: center; }
  .bapi-items-uom   { width: 10%; text-align: center; }
  .bapi-items-rate  { width: 10%; text-align: left; }
  .bapi-items-amt   { width: 10%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">صورت مواد (BOM)</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ (doc.modified or doc.creation) | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">شماره BOM:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">کالای اصلی:</span>
          {{ doc.item_name or doc.item }}
        </div>
        <div>
          <span class="bapi-meta-label">مقدار تولید:</span>
          {{ doc.quantity }} {{ doc.uom or "" }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>اطلاعات BOM</th>
      <th>اطلاعات شرکت</th>
    </tr>
    <tr>
      <td>
        <div><strong>فعال:</strong> {{ "بله" if doc.is_active else "خیر" }}</div>
        <div><strong>BOM پیش‌فرض:</strong> {{ "بله" if doc.is_default else "خیر" }}</div>
        {% if doc.is_sub_assembly %}
          <div><strong>زیرمونتاژ:</strong> بله</div>
        {% endif %}
      </td>
      <td>
        <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا / جزء</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-rate">نرخ (ریال)</th>
        <th class="bapi-items-amt">مبلغ (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.get("items") or [] %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-code">{{ row.item_code }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name or row.item_code }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty }}</td>
        <td class="bapi-items-uom">{{ row.uom }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:50%;"></td>
      <td class="bapi-totals-label">هزینه مواد اولیه:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.raw_material_cost or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">هزینه عملیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.operating_cost or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">هزینه کل BOM:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_cost or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.description %}
        {{ doc.description }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تهیه‌کننده</td>
      <td>کنترل کیفیت</td>
      <td>تأیید مدیریت</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_delivery_note_v1():
    """Create/Update BLUE_PRINT_DELIVERY_NOTE_V1 for Delivery Note."""
    NAME = "BLUE_PRINT_DELIVERY_NOTE_V1"
    DOCTYPE = "Delivery Note"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-uom { width: 15%; text-align: center; }
  .bapi-items-warehouse { width: 25%; text-align: right; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">حواله خروج کالا</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">شماره حواله:</span>
          {{ doc.name }}
        </div>
        {% if doc.against_sales_invoice %}
        <div>
          <span class="bapi-meta-label">شماره فاکتور مرتبط:</span>
          {{ doc.against_sales_invoice }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات خریدار / گیرنده</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام فروشنده:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong> {{ doc.customer_name or doc.customer }}</div>
        {% if doc.shipping_address_display or doc.customer_address %}
          <div>
            <strong>آدرس:</strong>
            {{ doc.shipping_address_display or doc.address_display or doc.customer_address }}
          </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-warehouse">انبار / محل تحویل</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-uom">{{ row.stock_uom or row.uom }}</td>
        <td class="bapi-items-warehouse">{{ row.warehouse or doc.set_warehouse }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع تعداد اقلام:</td>
      <td class="bapi-totals-value">
        {{ doc.total_qty or 0 }}
      </td>
    </tr>
    {% if doc.total_net_weight %}
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع وزن خالص:</td>
      <td class="bapi-totals-value">
        {{ doc.total_net_weight }} {{ doc.weight_uom or "" }}
      </td>
    </tr>
    {% endif %}
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تحویل‌دهنده</td>
      <td>مسئول انبار</td>
      <td>گیرنده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_delivery_trip_v1():
    """Create/Update BLUE_PRINT_DELIVERY_TRIP_V1 for Delivery Trip."""
    NAME = "BLUE_PRINT_DELIVERY_TRIP_V1"
    DOCTYPE = "Delivery Trip"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-stops-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-stops-table th,
  .bapi-stops-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-stops-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-stop-idx      { width: 6%;  text-align: center; }
  .bapi-stop-customer { width: 22%; text-align: right; }
  .bapi-stop-address  { width: 32%; text-align: right; }
  .bapi-stop-docs     { width: 20%; text-align: right; }
  .bapi-stop-amount   { width: 10%; text-align: left; }
  .bapi-stop-status   { width: 10%; text-align: center; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 2px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% set trip_currency = doc.company_currency or "IRR" %}
{% set total_amount = 0 %}
{% set total_stops = 0 %}
{% if doc.delivery_stops %}
  {% set total_stops = doc.delivery_stops | length %}
  {% for row in doc.delivery_stops %}
    {% if row.grand_total %}
      {% set total_amount = total_amount + (row.grand_total or 0) %}
    {% endif %}
  {% endfor %}
{% endif %}

<div class="bapi-root">

  <div class="bapi-title">برنامه ارسال / Delivery Trip</div>
  <div class="bapi-subtitle">
    فهرست توقف‌ها و تحویل‌های مرتبط با این برنامه ارسال.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره برنامه ارسال:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">تاریخ برنامه:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.posting_time %}
        <div>
          <span class="bapi-meta-label">زمان برنامه:</span>
          {{ doc.posting_time }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات راننده / وسیله نقلیه</th>
      <th>اطلاعات تکمیلی مسیر</th>
    </tr>
    <tr>
      <td>
        {% if doc.driver %}
          <div><strong>راننده:</strong> {{ doc.driver }}</div>
        {% endif %}
        {% if doc.vehicle %}
          <div><strong>وسیله نقلیه:</strong> {{ doc.vehicle }}</div>
        {% elif doc.vehicle_no %}
          <div><strong>شماره خودرو:</strong> {{ doc.vehicle_no }}</div>
        {% endif %}
        {% if doc.lr_no %}
          <div><strong>شماره بارنامه:</strong> {{ doc.lr_no }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.from_location %}
          <div><strong>مبدأ:</strong> {{ doc.from_location }}</div>
        {% endif %}
        {% if doc.to_location %}
          <div><strong>مقصد کلی:</strong> {{ doc.to_location }}</div>
        {% endif %}
        {% if doc.purpose %}
          <div><strong>هدف سفر:</strong> {{ doc.purpose }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-stops-table">
    <thead>
      <tr>
        <th class="bapi-stop-idx">ردیف</th>
        <th class="bapi-stop-customer">مشتری / تحویل‌گیرنده</th>
        <th class="bapi-stop-address">آدرس / توضیحات</th>
        <th class="bapi-stop-docs">اسناد مرتبط</th>
        <th class="bapi-stop-amount">مبلغ تقریبی ({{ trip_currency }})</th>
        <th class="bapi-stop-status">وضعیت</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.delivery_stops %}
        {% for row in doc.delivery_stops %}
        <tr>
          <td class="bapi-stop-idx">{{ loop.index }}</td>
          <td class="bapi-stop-customer">
            {% if row.customer_name or row.customer %}
              {{ row.customer_name or row.customer }}
            {% elif row.customer_address %}
              {{ row.customer_address }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-stop-address">
            {% if row.address %}
              {{ row.address }}
            {% elif row.customer_address %}
              {{ row.customer_address }}
            {% elif row.contact_display %}
              {{ row.contact_display }}
            {% endif %}
          </td>
          <td class="bapi-stop-docs">
            {% if row.delivery_note %}
              <div>DN: {{ row.delivery_note }}</div>
            {% endif %}
            {% if row.sales_invoice %}
              <div>SI: {{ row.sales_invoice }}</div>
            {% endif %}
            {% if row.sales_order %}
              <div>SO: {{ row.sales_order }}</div>
            {% endif %}
          </td>
          <td class="bapi-stop-amount">
            {% if row.get_formatted %}
              {{ row.get_formatted("grand_total") or "" }}
            {% else %}
              {{ row.grand_total or "" }}
            {% endif %}
          </td>
          <td class="bapi-stop-status">
            {{ row.status or "" }}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#777;">
            هیچ توقفی برای این برنامه ارسال ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">تعداد توقف‌ها:</td>
      <td class="bapi-summary-value">{{ total_stops }}</td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-summary-label">جمع تقریبی مبالغ تحویل:</td>
      <td class="bapi-summary-value">
        {% if total_amount and total_amount > 0 %}
          {{ total_amount | money_to_words_fa(trip_currency) }}<br>
          ({{ "{:,.0f}".format(total_amount) }} {{ trip_currency }})
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">یادداشت‌ها و توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>آماده‌کننده برنامه ارسال</td>
      <td>راننده / تحویل‌دهنده</td>
      <td>تأیید واحد لجستیک / انبار</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_depreciation_schedule_v1():
    """Create/Update BLUE_PRINT_DEPRECIATION_SCHEDULE_V1 for Depreciation Schedule."""
    NAME = "BLUE_PRINT_DEPRECIATION_SCHEDULE_V1"
    DOCTYPE = "Depreciation Schedule"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-date  { width: 16%; text-align: center; }
  .bapi-items-amt   { width: 18%; text-align: left; }
  .bapi-items-acc   { width: 20%; text-align: left; }
  .bapi-items-book  { width: 20%; text-align: left; }
  .bapi-items-note  { width: 20%; text-align: right; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 3px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">برنامه استهلاک دارایی</div>
  <div class="bapi-subtitle">
    برنامه دوره‌ای استهلاک دارایی ثبت‌شده در سیستم بلوحساب / BlueHesab.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره برنامه:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.asset %}
        <div>
          <span class="bapi-meta-label">کد دارایی:</span>
          {{ doc.asset }}
        </div>
        {% endif %}
        {% if doc.asset_name %}
        <div>
          <span class="bapi-meta-label">عنوان دارایی:</span>
          {{ doc.asset_name }}
        </div>
        {% endif %}
        {% if doc.depreciation_start_date %}
        <div>
          <span class="bapi-meta-label">تاریخ شروع استهلاک:</span>
          {{ doc.depreciation_start_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>اطلاعات دارایی و استهلاک</th>
      <th>اطلاعات مالی</th>
    </tr>
    <tr>
      <td>
        {% if doc.finance_book %}
          <div><strong>دفتر مالی:</strong> {{ doc.finance_book }}</div>
        {% endif %}
        {% if doc.total_number_of_depreciations %}
          <div><strong>تعداد کل دوره‌های استهلاک:</strong> {{ doc.total_number_of_depreciations }}</div>
        {% endif %}
        {% if doc.frequency %}
          <div><strong>تناوب استهلاک:</strong> {{ doc.frequency }}</div>
        {% endif %}
        {% if doc.status %}
          <div><strong>وضعیت برنامه:</strong> {{ doc.status }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.gross_purchase_amount %}
          <div>
            <strong>بهای تمام‌شده (ریال):</strong>
            {{ "{:,.0f}".format(doc.gross_purchase_amount or 0) }}
          </div>
        {% endif %}
        {% if doc.opening_accumulated_depreciation %}
          <div>
            <strong>استهلاک انباشته اولیه:</strong>
            {{ "{:,.0f}".format(doc.opening_accumulated_depreciation or 0) }}
          </div>
        {% endif %}
        {% if doc.total_depreciation_amount %}
          <div>
            <strong>جمع مبلغ استهلاک این برنامه:</strong>
            {{ "{:,.0f}".format(doc.total_depreciation_amount or 0) }}
          </div>
        {% endif %}
        {% if doc.value_after_depreciation %}
          <div>
            <strong>ارزش دفتری پس از استهلاک:</strong>
            {{ "{:,.0f}".format(doc.value_after_depreciation or 0) }}
          </div>
        {% endif %}
      </td>
    </tr>
  </table>

  {% set rows = doc.get("depreciation_schedule") or doc.get("depreciation_schedule_details") or doc.get("schedule") or [] %}

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-date">تاریخ استهلاک</th>
        <th class="bapi-items-amt">مبلغ استهلاک (ریال)</th>
        <th class="bapi-items-acc">استهلاک انباشته (ریال)</th>
        <th class="bapi-items-book">ارزش دفتری پس از استهلاک</th>
        <th class="bapi-items-note">توضیحات</th>
      </tr>
    </thead>
    <tbody>
      {% if rows %}
        {% for row in rows %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-date">
            {% set d = row.schedule_date or row.depreciation_date %}
            {% if d %}
              {{ d | as_jdate("YYYY/MM/DD") }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-items-amt">
            {{ "{:,.0f}".format(row.depreciation_amount or row.amount or 0) }}
          </td>
          <td class="bapi-items-acc">
            {% set acc = row.accumulated_depreciation or row.total_depreciation or 0 %}
            {{ "{:,.0f}".format(acc) }}
          </td>
          <td class="bapi-items-book">
            {% set bv = row.depreciated_value or row.book_value or row.value_after_depreciation or 0 %}
            {{ "{:,.0f}".format(bv) }}
          </td>
          <td class="bapi-items-note">
            {% if row.journal_entry %}
              ثبت روزنامه: {{ row.journal_entry }}
            {% elif row.note %}
              {{ row.note }}
            {% else %}
              &nbsp;
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#777;">
            هیچ ردیفی برای برنامه استهلاک ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">جمع استهلاک برنامه:</td>
      <td class="bapi-summary-value">
        ریال {{ "{:,.0f}".format(doc.total_depreciation_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-summary-label">ارزش دفتری نهایی به حروف:</td>
      <td class="bapi-summary-value">
        {% set bv = doc.value_after_depreciation or 0 %}
        {% if bv and bv > 0 %}
          {{ bv | money_to_words_fa("IRR") }}
          <br>(ریال {{ "{:,.0f}".format(bv) }})
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>کارشناس دارایی‌ها</td>
      <td>مدیر مالی</td>
      <td>مدیرعامل / مقام مجاز</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_employee_advance_v1():
    """
    قالب چاپ «علی‌الحساب / مساعده حقوق» برای DocType = Employee Advance
    - تاریخ‌ها: فقط جلالی (J1)
    - باکس نارنجی: مبلغ علی‌الحساب (عدد + به حروف)
    """

    NAME = "BLUE_PRINT_EMPLOYEE_ADVANCE_V1"
    DOCTYPE = "Employee Advance"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8.5pt;
    margin-right: 4px;
  }

  .bapi-status-draft {
    background-color: #fff3cd;
    color: #856404;
  }

  .bapi-status-approved {
    background-color: #d4edda;
    color: #155724;
  }

  .bapi-status-paid {
    background-color: #cce5ff;
    color: #004085;
  }

  .bapi-status-cancelled {
    background-color: #f8d7da;
    color: #721c24;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-row {
    margin-bottom: 4px;
  }

  .bapi-label {
    display: inline-block;
    min-width: 110px;
    font-weight: 600;
  }

  .bapi-amount-box {
    margin-top: 12px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 45%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 55%;
    text-align: left;
  }

  .bapi-amount-box-words {
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-totals-table {
    width: 100%;
    margin-top: 10px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">فرم علی‌الحساب / مساعده حقوق</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {% set st = doc.status or "" %}
          {% if st == "Draft" %}
            <span class="bapi-status-pill bapi-status-draft">پیش‌نویس</span>
          {% elif st == "Unpaid" %}
            <span class="bapi-status-pill bapi-status-approved">تأیید شده</span>
          {% elif st == "Paid" %}
            <span class="bapi-status-pill bapi-status-paid">پرداخت شده</span>
          {% elif st == "Cancelled" %}
            <span class="bapi-status-pill bapi-status-cancelled">لغو شده</span>
          {% else %}
            <span class="bapi-status-pill">{{ st }}</span>
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>مشخصات کارمند</th>
      <th>مشخصات مالی</th>
    </tr>
    <tr>
      <td>
        <div class="bapi-row">
          <span class="bapi-label">نام کارمند:</span>
          <span>{{ doc.employee_name or doc.employee }}</span>
        </div>
        <div class="bapi-row">
          <span class="bapi-label">کد کارمند:</span>
          <span>{{ doc.employee }}</span>
        </div>
        {% if doc.department %}
        <div class="bapi-row">
          <span class="bapi-label">واحد سازمانی:</span>
          <span>{{ doc.department }}</span>
        </div>
        {% endif %}
        {% if doc.branch %}
        <div class="bapi-row">
          <span class="bapi-label">شعبه:</span>
          <span>{{ doc.branch }}</span>
        </div>
        {% endif %}
      </td>
      <td>
        {% set adv = doc.advance_amount or 0 %}
        {% set paid = doc.paid_amount or 0 %}
        {% set outstanding = doc.outstanding_amount or (adv - paid) %}
        {% if doc.mode_of_payment %}
        <div class="bapi-row">
          <span class="bapi-label">روش پرداخت:</span>
          <span>{{ doc.mode_of_payment }}</span>
        </div>
        {% endif %}
        {% if doc.repay_from_salary %}
        <div class="bapi-row">
          <span class="bapi-label">بازپرداخت از حقوق:</span>
          <span>بله</span>
        </div>
        {% endif %}
        {% if doc.payable_account %}
        <div class="bapi-row">
          <span class="bapi-label">حساب بستانکار:</span>
          <span>{{ doc.payable_account }}</span>
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ علی‌الحساب درخواستی:</div>
    <div class="bapi-amount-box-value">
      <div>ریال {{ "{:,.0f}".format(doc.advance_amount or 0) }}</div>
      <div class="bapi-amount-box-words">
        مبلغ به حروف:
        {{ (doc.advance_amount or 0) | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:50%;"></td>
      <td class="bapi-totals-label">مبلغ پرداخت‌شده تا کنون:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.paid_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label"><strong>مانده علی‌الحساب:</strong></td>
      <td class="bapi-totals-value">
        <strong>ریال {{ "{:,.0f}".format(outstanding or 0) }}</strong>
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرح و توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.purpose and doc.purpose.strip() %}
        {{ doc.purpose }}
      {% elif doc.remarks and doc.remarks.strip() %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء کارمند</td>
      <td>امضاء مدیر مستقیم</td>
      <td>امضاء واحد مالی / منابع انسانی</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_employee_v1():
    """
    قالب چاپ «پروفایل کارمند» برای DocType = Employee
    - تاریخ‌ها: فقط جلالی (J1)
    - تیتر: پروفایل کارمند
    - هدر: لوگو + کد کارمند + وضعیت
    - بلوک اطلاعات هویتی
    - اطلاعات استخدامی (شرکت، سمت، واحد، مدیر مستقیم)
    - اطلاعات تماس
    - آدرس‌ها
    - اطلاعات بانکی (در صورت وجود)
    - امضاءها
    """

    NAME = "BLUE_PRINT_EMPLOYEE_V1"
    DOCTYPE = "Employee"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8.5pt;
    margin-right: 4px;
  }

  .bapi-status-active {
    background-color: #d4edda;
    color: #155724;
  }

  .bapi-status-left {
    background-color: #f8d7da;
    color: #721c24;
  }

  .bapi-status-other {
    background-color: #fff3cd;
    color: #856404;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-main-grid {
    width: 100%;
    margin-bottom: 12px;
  }

  .bapi-main-grid td {
    vertical-align: top;
    padding: 4px 6px;
  }

  .bapi-photo-box {
    width: 30%;
    text-align: center;
  }

  .bapi-photo {
    max-width: 120px;
    max-height: 140px;
    border-radius: 4px;
    border: 1px solid #ddd;
    object-fit: cover;
  }

  .bapi-photo-placeholder {
    width: 120px;
    height: 140px;
    border-radius: 4px;
    border: 1px solid #ddd;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 9pt;
    color: #888;
  }

  .bapi-basic-box {
    width: 70%;
    border: 1px solid #dddddd;
    padding: 8px 10px;
    font-size: 10pt;
  }

  .bapi-row {
    margin-bottom: 4px;
  }

  .bapi-label {
    display: inline-block;
    min-width: 100px;
    font-weight: 600;
  }

  .bapi-section-title {
    font-weight: 600;
    margin: 10px 0 4px 0;
    font-size: 11pt;
  }

  .bapi-section-box {
    border: 1px solid #dddddd;
    padding: 8px 10px;
    font-size: 10pt;
    margin-bottom: 8px;
  }

  .bapi-address-box {
    border: 1px solid #dddddd;
    padding: 6px 8px;
    min-height: 40px;
    margin-bottom: 6px;
    font-size: 10pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <!-- تیتر اصلی -->
  <div class="bapi-title">پروفایل کارمند</div>

  <!-- هدر: لوگو + کد کارمند + وضعیت -->
  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">کد کارمند:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">نام کارمند:</span>
          {{ doc.employee_name or doc.employee }}
        </div>
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {% set st = doc.status or "" %}
          {% if st == "Active" %}
            <span class="bapi-status-pill bapi-status-active">مشغول به کار</span>
          {% elif st == "Left" %}
            <span class="bapi-status-pill bapi-status-left">ترک خدمت</span>
          {% else %}
            <span class="bapi-status-pill bapi-status-other">{{ st }}</span>
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <!-- عکس + اطلاعات پایه -->
  <table class="bapi-main-grid">
    <tr>
      <td class="bapi-photo-box">
        {% if doc.image %}
          <img src="{{ doc.image }}" class="bapi-photo">
        {% else %}
          <div class="bapi-photo-placeholder">بدون عکس</div>
        {% endif %}
      </td>
      <td>
        <div class="bapi-basic-box">
          <div class="bapi-row">
            <span class="bapi-label">شرکت:</span>
            <span>{{ doc.company or "" }}</span>
          </div>
          {% if doc.date_of_joining %}
          <div class="bapi-row">
            <span class="bapi-label">تاریخ شروع به کار:</span>
            <span>{{ doc.date_of_joining | as_jdate("YYYY/MM/DD") }}</span>
          </div>
          {% endif %}
          {% if doc.date_of_birth %}
          <div class="bapi-row">
            <span class="bapi-label">تاریخ تولد:</span>
            <span>{{ doc.date_of_birth | as_jdate("YYYY/MM/DD") }}</span>
          </div>
          {% endif %}
          {% if doc.gender %}
          <div class="bapi-row">
            <span class="bapi-label">جنسیت:</span>
            <span>{{ doc.gender }}</span>
          </div>
          {% endif %}
          {% if doc.blood_group %}
          <div class="bapi-row">
            <span class="bapi-label">گروه خونی:</span>
            <span>{{ doc.blood_group }}</span>
          </div>
          {% endif %}
          {% if doc.marital_status %}
          <div class="bapi-row">
            <span class="bapi-label">وضعیت تأهل:</span>
            <span>{{ doc.marital_status }}</span>
          </div>
          {% endif %}
        </div>
      </td>
    </tr>
  </table>

  <!-- اطلاعات استخدامی -->
  <div class="bapi-section-title">اطلاعات استخدامی</div>
  <div class="bapi-section-box">
    {% if doc.designation %}
    <div class="bapi-row">
      <span class="bapi-label">سمت:</span>
      <span>{{ doc.designation }}</span>
    </div>
    {% endif %}
    {% if doc.department %}
    <div class="bapi-row">
      <span class="bapi-label">واحد سازمانی:</span>
      <span>{{ doc.department }}</span>
    </div>
    {% endif %}
    {% if doc.branch %}
    <div class="bapi-row">
      <span class="bapi-label">شعبه:</span>
      <span>{{ doc.branch }}</span>
    </div>
    {% endif %}
    {% if doc.reports_to %}
    <div class="bapi-row">
      <span class="bapi-label">مدیر مستقیم:</span>
      <span>{{ doc.reports_to }}</span>
    </div>
    {% endif %}
    {% if doc.employment_type %}
    <div class="bapi-row">
      <span class="bapi-label">نوع استخدام:</span>
      <span>{{ doc.employment_type }}</span>
    </div>
    {% endif %}
    {% if doc.grade %}
    <div class="bapi-row">
      <span class="bapi-label">رده/گرید:</span>
      <span>{{ doc.grade }}</span>
    </div>
    {% endif %}
  </div>

  <!-- اطلاعات تماس -->
  <div class="bapi-section-title">اطلاعات تماس</div>
  <div class="bapi-section-box">
    {% if doc.cell_number %}
    <div class="bapi-row">
      <span class="bapi-label">موبایل:</span>
      <span>{{ doc.cell_number }}</span>
    </div>
    {% endif %}
    {% if doc.company_email %}
    <div class="bapi-row">
      <span class="bapi-label">ایمیل سازمانی:</span>
      <span>{{ doc.company_email }}</span>
    </div>
    {% endif %}
    {% if doc.personal_email %}
    <div class="bapi-row">
      <span class="bapi-label">ایمیل شخصی:</span>
      <span>{{ doc.personal_email }}</span>
    </div>
    {% endif %}
    {% if doc.phone %}
    <div class="bapi-row">
      <span class="bapi-label">تلفن ثابت:</span>
      <span>{{ doc.phone }}</span>
    </div>
    {% endif %}
  </div>

  <!-- آدرس‌ها -->
  <div class="bapi-section-title">آدرس‌ها</div>
  <div class="bapi-section-box">
    <div class="bapi-row"><strong>آدرس فعلی:</strong></div>
    <div class="bapi-address-box">
      {% if doc.current_address %}
        {{ doc.current_address }}
      {% endif %}
    </div>

    <div class="bapi-row"><strong>آدرس دائمی:</strong></div>
    <div class="bapi-address-box">
      {% if doc.permanent_address %}
        {{ doc.permanent_address }}
      {% endif %}
    </div>
  </div>

  <!-- اطلاعات بانکی (اختیاری) -->
  <div class="bapi-section-title">اطلاعات بانکی</div>
  <div class="bapi-section-box">
    {% if doc.bank_name %}
    <div class="bapi-row">
      <span class="bapi-label">بانک:</span>
      <span>{{ doc.bank_name }}</span>
    </div>
    {% endif %}
    {% if doc.bank_ac_no %}
    <div class="bapi-row">
      <span class="bapi-label">شماره حساب:</span>
      <span>{{ doc.bank_ac_no }}</span>
    </div>
    {% endif %}
    {% if doc.iban %}
    <div class="bapi-row">
      <span class="bapi-label">شماره شبا:</span>
      <span>{{ doc.iban }}</span>
    </div>
    {% endif %}
    {% if not (doc.bank_name or doc.bank_ac_no or doc.iban) %}
    <div class="bapi-row" style="color:#888;">
      اطلاعات بانکی برای این کارمند ثبت نشده است.
    </div>
    {% endif %}
  </div>

  <!-- امضاءها -->
  <table class="bapi-sign-table">
    <tr>
      <td>امضاء کارمند</td>
      <td>امضاء مدیر مستقیم</td>
      <td>امضاء واحد منابع انسانی</td>
    </tr>
  </table>

  <!-- فوتر -->
  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_expense_claim_v1():
    """
    قالب چاپ «فرم درخواست/گزارش هزینه» برای DocType = Expense Claim
    - تاریخ‌ها: فقط جلالی (J1)
    - هدر: لوگو + تاریخ ثبت + شماره سند + وضعیت
    - بلوک اطلاعات کارمند و شرکت
    - جدول ردیف‌های هزینه (تاریخ، شرح، نوع، ادعایی، تأییدشده)
    - جمع مبالغ و باکس نارنجی مبلغ نهایی قابل پرداخت (عدد + حروف)
    - توضیحات و امضاءها
    """

    NAME = "BLUE_PRINT_EXPENSE_CLAIM_V1"
    DOCTYPE = "Expense Claim"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8.5pt;
    margin-right: 4px;
  }

  .bapi-status-draft {
    background-color: #fff3cd;
    color: #856404;
  }

  .bapi-status-approved {
    background-color: #d4edda;
    color: #155724;
  }

  .bapi-status-rejected {
    background-color: #f8d7da;
    color: #721c24;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-row {
    margin-bottom: 4px;
  }

  .bapi-label {
    display: inline-block;
    min-width: 100px;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 4px 6px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-idx { width: 6%; text-align: center; }
  .bapi-date { width: 14%; text-align: center; }
  .bapi-desc { width: 35%; }
  .bapi-type { width: 15%; text-align: center; }
  .bapi-amt-claim { width: 15%; text-align: left; }
  .bapi-amt-sanc { width: 15%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 12px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 45%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 55%;
    text-align: left;
  }

  .bapi-amount-box-words {
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <!-- تیتر اصلی -->
  <div class="bapi-title">فرم درخواست / گزارش هزینه</div>

  <!-- هدر: لوگو + تاریخ + شماره + وضعیت -->
  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.approval_status or doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {% set st = doc.approval_status or doc.status or "" %}
          {% if st in ["Draft", "Submitted"] %}
            <span class="bapi-status-pill bapi-status-draft">{{ st }}</span>
          {% elif st in ["Approved", "Paid"] %}
            <span class="bapi-status-pill bapi-status-approved">{{ st }}</span>
          {% elif st in ["Rejected"] %}
            <span class="bapi-status-pill bapi-status-rejected">{{ st }}</span>
          {% else %}
            <span class="bapi-status-pill">{{ st }}</span>
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <!-- اطلاعات کارمند / هزینه -->
  <table class="bapi-info-table">
    <tr>
      <th>مشخصات کارمند</th>
      <th>مشخصات هزینه</th>
    </tr>
    <tr>
      <td>
        <div class="bapi-row">
          <span class="bapi-label">نام کارمند:</span>
          <span>{{ doc.employee_name or doc.employee }}</span>
        </div>
        <div class="bapi-row">
          <span class="bapi-label">کد کارمند:</span>
          <span>{{ doc.employee }}</span>
        </div>
        {% if doc.department %}
        <div class="bapi-row">
          <span class="bapi-label">واحد سازمانی:</span>
          <span>{{ doc.department }}</span>
        </div>
        {% endif %}
        {% if doc.branch %}
        <div class="bapi-row">
          <span class="bapi-label">شعبه:</span>
          <span>{{ doc.branch }}</span>
        </div>
        {% endif %}
      </td>
      <td>
        {% if doc.expense_approver %}
        <div class="bapi-row">
          <span class="bapi-label">تأییدکننده هزینه:</span>
          <span>{{ doc.expense_approver }}</span>
        </div>
        {% endif %}
        {% if doc.purpose %}
        <div class="bapi-row">
          <span class="bapi-label">هدف/شرح کلی:</span>
          <span>{{ doc.purpose }}</span>
        </div>
        {% endif %}
        {% if doc.project %}
        <div class="bapi-row">
          <span class="bapi-label">پروژه:</span>
          <span>{{ doc.project }}</span>
        </div>
        {% endif %}
        {% if doc.cost_center %}
        <div class="bapi-row">
          <span class="bapi-label">مرکز هزینه:</span>
          <span>{{ doc.cost_center }}</span>
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <!-- جدول ردیف‌های هزینه -->
  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-idx">ردیف</th>
        <th class="bapi-date">تاریخ هزینه</th>
        <th class="bapi-desc">شرح هزینه</th>
        <th class="bapi-type">نوع هزینه</th>
        <th class="bapi-amt-claim">مبلغ ادعایی ({{ doc.currency or "IRR" }})</th>
        <th class="bapi-amt-sanc">مبلغ تأیید شده ({{ doc.currency or "IRR" }})</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.expenses %}
        {% for row in doc.expenses %}
        <tr>
          <td class="bapi-idx">{{ loop.index }}</td>
          <td class="bapi-date">
            {% if row.expense_date %}
              {{ row.expense_date | as_jdate("YYYY/MM/DD") }}
            {% endif %}
          </td>
          <td class="bapi-desc">
            {{ row.description or row.expense_type }}
          </td>
          <td class="bapi-type">
            {{ row.expense_type }}
          </td>
          <td class="bapi-amt-claim">
            {{ row.get_formatted("amount") if row.get_formatted else ("{:,.0f}".format(row.amount or 0)) }}
          </td>
          <td class="bapi-amt-sanc">
            {% set sanc = row.sanctioned_amount or row.amount or 0 %}
            {{ "{:,.0f}".format(sanc) }}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#888;">
            هیچ ردیف هزینه‌ای ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  {% set total_claim = doc.total_claimed_amount or doc.total_amount or 0 %}
  {% set total_sanc = doc.total_sanctioned_amount or total_claim %}
  {% set payable = doc.payable_amount or total_sanc %}

  <!-- جمع‌ها -->
  <table class="bapi-totals-table">
    <tr>
      <td style="width:50%;"></td>
      <td class="bapi-totals-label">جمع مبالغ ادعایی:</td>
      <td class="bapi-totals-value">
        {{ "ریال {:,}".format(total_claim|int).replace(",", ",") if total_claim else "ریال 0" }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مبالغ تأیید شده:</td>
      <td class="bapi-totals-value">
        {{ "ریال {:,}".format(total_sanc|int).replace(",", ",") if total_sanc else "ریال 0" }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label"><strong>مبلغ نهایی قابل پرداخت:</strong></td>
      <td class="bapi-totals-value">
        <strong>{{ "ریال {:,}".format(payable|int).replace(",", ",") if payable else "ریال 0" }}</strong>
      </td>
    </tr>
  </table>

  <!-- باکس نارنجی: مبلغ نهایی + به حروف -->
  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی قابل پرداخت به کارمند:</div>
    <div class="bapi-amount-box-value">
      <div>
        {{ "ریال {:,}".format(payable|int).replace(",", ",") if payable else "ریال 0" }}
      </div>
      <div class="bapi-amount-box-words">
        مبلغ به حروف:
        {{ (payable or 0) | money_to_words_fa(doc.currency or "IRR") }}
      </div>
    </div>
  </div>

  <!-- توضیحات -->
  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remark and doc.remark.strip() %}
        {{ doc.remark }}
      {% endif %}
    </div>
  </div>

  <!-- امضاءها -->
  <table class="bapi-sign-table">
    <tr>
      <td>امضاء کارمند</td>
      <td>امضاء مدیر مستقیم</td>
      <td>امضاء واحد مالی</td>
    </tr>
  </table>

  <!-- فوتر -->
  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_installation_note_v1():
    """Create/Update BLUE_PRINT_INSTALLATION_NOTE_V1 for Installation Note."""
    NAME = "BLUE_PRINT_INSTALLATION_NOTE_V1"
    DOCTYPE = "Installation Note"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-idx    { width: 6%;  text-align: center; }
  .bapi-items-code   { width: 16%; text-align: right; }
  .bapi-items-desc   { width: 32%; text-align: right; }
  .bapi-items-serial { width: 18%; text-align: left; }
  .bapi-items-warehouse { width: 18%; text-align: right; }
  .bapi-items-qty    { width: 10%; text-align: center; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 2px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">گزارش نصب / Installation Note</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره گزارش نصب:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">تاریخ نصب:</span>
          {% if doc.installation_date %}
            {{ doc.installation_date | as_jdate("YYYY/MM/DD") }}
          {% elif doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.sales_invoice %}
        <div>
          <span class="bapi-meta-label">ارجاع فاکتور فروش:</span>
          {{ doc.sales_invoice }}
        </div>
        {% elif doc.delivery_note %}
        <div>
          <span class="bapi-meta-label">ارجاع حواله تحویل:</span>
          {{ doc.delivery_note }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات مشتری / محل نصب</th>
      <th>اطلاعات نصب</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام مشتری:</strong> {{ doc.customer_name or doc.customer }}</div>
        {% if doc.customer_address %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
        {% endif %}
        {% if doc.contact_person %}
          <div><strong>شخص تماس:</strong> {{ doc.contact_display or doc.contact_person }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.installer_name %}
          <div><strong>نصاب / تکنسین:</strong> {{ doc.installer_name }}</div>
        {% endif %}
        {% if doc.installation_location %}
          <div><strong>محل نصب:</strong> {{ doc.installation_location }}</div>
        {% endif %}
        {% if doc.warranty_expiry_date %}
          <div>
            <strong>پایان گارانتی:</strong>
            {{ doc.warranty_expiry_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.project %}
          <div><strong>پروژه مرتبط:</strong> {{ doc.project }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا / خدمت نصب‌شده</th>
        <th class="bapi-items-serial">سریال / شناسنامه</th>
        <th class="bapi-items-warehouse">انبار / محل نگهداری</th>
        <th class="bapi-items-qty">تعداد</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-code">
            {{ row.item_code or "" }}
          </td>
          <td class="bapi-items-desc">
            {{ row.item_name or "" }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-serial">
            {% if row.serial_no %}
              {{ row.serial_no }}
            {% elif row.asset %}
              دارایی: {{ row.asset }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-items-warehouse">
            {{ row.warehouse or row.target_warehouse or "" }}
          </td>
          <td class="bapi-items-qty">
            {{ row.qty or 1 }}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#777;">
            هیچ قلمی برای این گزارش نصب ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    {% set total_qty = 0 %}
    {% if doc.items %}
      {% for row in doc.items %}
        {% set total_qty = total_qty + (row.qty or 0) %}
      {% endfor %}
    {% endif %}
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">تعداد کل اقلام نصب‌شده:</td>
      <td class="bapi-summary-value">{{ total_qty }}</td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرح عملیات نصب / توضیحات تکمیلی:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>نصاب / تکنسین</td>
      <td>نماینده مشتری</td>
      <td>تأیید واحد فنی / خدمات پس از فروش</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_job_card_v1():
    """Create/Update BLUE_PRINT_JOB_CARD_V1 for Job Card."""
    NAME = "BLUE_PRINT_JOB_CARD_V1"
    DOCTYPE = "Job Card"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-from  { width: 20%; text-align: center; }
  .bapi-items-to    { width: 20%; text-align: center; }
  .bapi-items-qty   { width: 12%; text-align: center; }
  .bapi-items-time  { width: 12%; text-align: center; }
  .bapi-items-note  { width: 30%; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">کارت کار (Job Card)</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% else %}
            {{ doc.creation | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.posting_time %}
        <div>
          <span class="bapi-meta-label">ساعت ثبت:</span>
          {{ doc.posting_time }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره کارت کار:</span>
          {{ doc.name }}
        </div>
        {% if doc.work_order %}
        <div>
          <span class="bapi-meta-label">شماره دستور تولید:</span>
          {{ doc.work_order }}
        </div>
        {% endif %}
        {% if doc.for_operation or doc.operation %}
        <div>
          <span class="bapi-meta-label">عملیات:</span>
          {{ doc.for_operation or doc.operation }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>جزئیات تولید</th>
      <th>نیروی انسانی / ایستگاه کاری</th>
    </tr>
    <tr>
      <td>
        <div>
          <strong>کالای تولیدی:</strong>
          {{ doc.production_item or doc.item or "" }}
        </div>
        {% if doc.for_quantity %}
        <div>
          <strong>مقدار برنامه‌ریزی‌شده:</strong>
          {{ doc.for_quantity }}
        </div>
        {% endif %}
        {% if doc.total_completed_qty %}
        <div>
          <strong>مقدار تکمیل‌شده:</strong>
          {{ doc.total_completed_qty }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <strong>شرکت:</strong>
          {{ doc.company }}
        </div>
        {% endif %}
      </td>
      <td>
        {% if doc.employee or doc.employee_name %}
        <div>
          <strong>کاربر/اپراتور:</strong>
          {{ doc.employee_name or doc.employee }}
        </div>
        {% endif %}
        {% if doc.workstation %}
        <div>
          <strong>ایستگاه کاری:</strong>
          {{ doc.workstation }}
        </div>
        {% endif %}
        {% if doc.wip_warehouse %}
        <div>
          <strong>انبار در جریان ساخت:</strong>
          {{ doc.wip_warehouse }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-from">شروع</th>
        <th class="bapi-items-to">پایان</th>
        <th class="bapi-items-qty">مقدار تکمیل‌شده</th>
        <th class="bapi-items-time">زمان (دقیقه)</th>
        <th class="bapi-items-note">توضیحات</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.get("time_logs") or [] %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-from">
          {% if row.from_time %}
            {{ row.from_time | as_jdatetime("YYYY/MM/DD HH:mm") }}
          {% endif %}
        </td>
        <td class="bapi-items-to">
          {% if row.to_time %}
            {{ row.to_time | as_jdatetime("YYYY/MM/DD HH:mm") }}
          {% endif %}
        </td>
        <td class="bapi-items-qty">
          {{ row.completed_qty or "" }}
        </td>
        <td class="bapi-items-time">
          {{ row.time_in_mins or 0 }}
        </td>
        <td class="bapi-items-note">
          {% if row.remark %}
            {{ row.remark }}
          {% elif row.description %}
            {{ row.description }}
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:50%;"></td>
      {% if doc.total_completed_qty %}
      <td style="text-align:right; width:25%;">جمع مقدار تکمیل‌شده:</td>
      <td style="text-align:left; width:25%;">{{ doc.total_completed_qty }}</td>
      {% endif %}
    </tr>
    <tr>
      <td></td>
      {% if doc.total_time_in_mins %}
      <td style="text-align:right;">جمع زمان (دقیقه):</td>
      <td style="text-align:left;">{{ doc.total_time_in_mins }}</td>
      {% endif %}
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks %}
        {{ doc.remarks }}
      {% elif doc.description %}
        {{ doc.description }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>اپراتور / مجری</td>
      <td>سرپرست تولید</td>
      <td>کنترل کیفیت</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_journal_entry_v1():
    """Create/Update BLUE_PRINT_JOURNAL_ENTRY_V1 for Journal Entry."""
    NAME = "BLUE_PRINT_JOURNAL_ENTRY_V1"
    DOCTYPE = "Journal Entry"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-accounts-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-accounts-table th,
  .bapi-accounts-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-accounts-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-accounts-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-acc-idx     { width: 5%;  text-align: center; }
  .bapi-acc-name    { width: 26%; }
  .bapi-acc-party   { width: 17%; }
  .bapi-acc-debit   { width: 14%; text-align: left; }
  .bapi-acc-credit  { width: 14%; text-align: left; }
  .bapi-acc-cost    { width: 12%; text-align: center; }
  .bapi-acc-ref     { width: 12%; text-align: center; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 25%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 55%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 45%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }

  .bapi-warning {
    color: #c0392b;
    font-size: 9pt;
    margin-top: 4px;
  }
</style>

{% set main_amount = doc.total_debit or doc.total_credit or 0 %}
{% set main_currency = doc.company_currency or doc.currency or "IRR" %}

<div class="bapi-root">

  <div class="bapi-title">سند روزنامه / سند حسابداری</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ سند:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.voucher_type %}
        <div>
          <span class="bapi-meta-label">نوع سند:</span>
          {{ doc.voucher_type }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-accounts-table">
    <thead>
      <tr>
        <th class="bapi-acc-idx">ردیف</th>
        <th class="bapi-acc-name">حساب</th>
        <th class="bapi-acc-party">طرف حساب</th>
        <th class="bapi-acc-debit">بدهکار</th>
        <th class="bapi-acc-credit">بستانکار</th>
        <th class="bapi-acc-cost">مرکز هزینه</th>
        <th class="bapi-acc-ref">ارجاع</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.accounts %}
        {% for row in doc.accounts %}
        <tr>
          <td class="bapi-acc-idx">{{ loop.index }}</td>
          <td class="bapi-acc-name">
            {{ row.account }}
          </td>
          <td class="bapi-acc-party">
            {% if row.party_type and row.party %}
              {{ row.party_type }} - {{ row.party }}
            {% elif row.party %}
              {{ row.party }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-acc-debit">
            {% if row.debit %}
              {{ row.get_formatted("debit") }}
            {% endif %}
          </td>
          <td class="bapi-acc-credit">
            {% if row.credit %}
              {{ row.get_formatted("credit") }}
            {% endif %}
          </td>
          <td class="bapi-acc-cost">
            {{ row.cost_center or "-" }}
          </td>
          <td class="bapi-acc-ref">
            {% if row.reference_type and row.reference_name %}
              {{ row.reference_type }}<br>{{ row.reference_name }}
            {% else %}
              -
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ ردیفی در این سند ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-totals-label">جمع بدهکار:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("total_debit") }}</td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع بستانکار:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("total_credit") }}</td>
    </tr>
    {% if (doc.total_debit or 0) != (doc.total_credit or 0) %}
    <tr>
      <td></td>
      <td colspan="2" class="bapi-warning">
        هشدار: سند تراز نیست (جمع بدهکار و بستانکار برابر نیست).
      </td>
    </tr>
    {% endif %}
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ کل بدهکار این سند:</div>
    <div class="bapi-amount-box-value">
      <div>{{ "{:,.0f}".format(main_amount or 0) }} {{ main_currency }}</div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ main_amount | money_to_words_fa(main_currency) }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرح سند:</div>
    <div class="bapi-remarks-box">
      {% if doc.user_remark and doc.user_remark.strip() %}
        {{ doc.user_remark }}
      {% elif doc.remark and doc.remark.strip() %}
        {{ doc.remark }}
      {% elif doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تنظیم‌کننده</td>
      <td>بررسی و کنترل</td>
      <td>تأیید مدیریت / مدیر مالی</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_leave_application_v1():
    """
    قالب چاپ «فرم درخواست مرخصی» برای DocType = Leave Application
    - تاریخ‌ها: فقط جلالی (J1)
    - تیتر: فرم درخواست مرخصی
    - هدر: لوگو + تاریخ ثبت + شماره درخواست + وضعیت
    - بلوک اطلاعات کارمند
    - بلوک جزئیات مرخصی (نوع، بازه، تعداد روز)
    - توضیحات
    - سه جای امضاء (کارمند، مدیر، واحد منابع انسانی)
    """

    NAME = "BLUE_PRINT_LEAVE_APPLICATION_V1"
    DOCTYPE = "Leave Application"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8.5pt;
    margin-right: 4px;
  }

  .bapi-status-open {
    background-color: #fff3cd;
    color: #856404;
  }

  .bapi-status-approved {
    background-color: #d4edda;
    color: #155724;
  }

  .bapi-status-rejected {
    background-color: #f8d7da;
    color: #721c24;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-section-title {
    font-weight: 600;
    margin: 10px 0 4px 0;
    font-size: 11pt;
  }

  .bapi-leave-box {
    border: 1px solid #dddddd;
    padding: 8px 10px;
    font-size: 10pt;
  }

  .bapi-leave-row {
    margin-bottom: 4px;
  }

  .bapi-leave-label {
    display: inline-block;
    min-width: 90px;
    font-weight: 600;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <!-- تیتر اصلی -->
  <div class="bapi-title">فرم درخواست مرخصی</div>

  <!-- هدر: لوگو + تاریخ + شماره + وضعیت -->
  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
        </div>
        <div>
          <span class="bapi-meta-label">شماره درخواست:</span>
          {{ doc.name }}
        </div>
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {% set st = doc.status or "" %}
          {% if st == "Open" %}
            <span class="bapi-status-pill bapi-status-open">در انتظار تأیید</span>
          {% elif st == "Approved" %}
            <span class="bapi-status-pill bapi-status-approved">تأیید شده</span>
          {% elif st == "Rejected" %}
            <span class="bapi-status-pill bapi-status-rejected">رد شده</span>
          {% else %}
            <span class="bapi-status-pill">{{ st }}</span>
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <!-- اطلاعات کارمند / سازمان -->
  <table class="bapi-info-table">
    <tr>
      <th>مشخصات کارمند</th>
      <th>مشخصات سازمانی</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام کارمند:</strong> {{ doc.employee_name or doc.employee }}</div>
        <div><strong>کد کارمند:</strong> {{ doc.employee }}</div>
        {% if doc.company %}
          <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.department %}
          <div><strong>واحد سازمانی:</strong> {{ doc.department }}</div>
        {% endif %}
        {% if doc.designation %}
          <div><strong>سمت:</strong> {{ doc.designation }}</div>
        {% endif %}
        {% if doc.branch %}
          <div><strong>شعبه:</strong> {{ doc.branch }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <!-- جزئیات مرخصی -->
  <div class="bapi-section-title">جزئیات مرخصی</div>
  <div class="bapi-leave-box">
    <div class="bapi-leave-row">
      <span class="bapi-leave-label">نوع مرخصی:</span>
      <span>{{ doc.leave_type }}</span>
    </div>

    {% if doc.from_date and doc.to_date %}
    <div class="bapi-leave-row">
      <span class="bapi-leave-label">بازه مرخصی:</span>
      <span>
        از {{ doc.from_date | as_jdate("YYYY/MM/DD") }}
        تا {{ doc.to_date | as_jdate("YYYY/MM/DD") }}
      </span>
    </div>
    {% endif %}

    {% if doc.total_leave_days %}
    <div class="bapi-leave-row">
      <span class="bapi-leave-label">تعداد روز:</span>
      <span>{{ doc.total_leave_days }} روز</span>
    </div>
    {% endif %}

    {% if doc.half_day %}
    <div class="bapi-leave-row">
      <span class="bapi-leave-label">نوع روز:</span>
      <span>مرخصی نیم‌روز</span>
      {% if doc.half_day_date %}
        (تاریخ: {{ doc.half_day_date | as_jdate("YYYY/MM/DD") }})
      {% endif %}
    </div>
    {% endif %}

    {% if doc.leave_approver %}
    <div class="bapi-leave-row">
      <span class="bapi-leave-label">شخص تأییدکننده:</span>
      <span>{{ doc.leave_approver }}</span>
    </div>
    {% endif %}
  </div>

  <!-- توضیحات -->
  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات کارمند:</div>
    <div class="bapi-remarks-box">
      {% if doc.description and doc.description.strip() %}
        {{ doc.description }}
      {% endif %}
    </div>
  </div>

  <!-- امضاءها -->
  <table class="bapi-sign-table">
    <tr>
      <td>امضاء کارمند</td>
      <td>امضاء مدیر مستقیم</td>
      <td>امضاء واحد منابع انسانی</td>
    </tr>
  </table>

  <!-- فوتر -->
  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_material_request_v1():
    """Create/Update BLUE_PRINT_MATERIAL_REQUEST_V1 for Material Request."""
    NAME = "BLUE_PRINT_MATERIAL_REQUEST_V1"
    DOCTYPE = "Material Request"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 6%; text-align: center; }
  .bapi-items-code { width: 14%; text-align: center; }
  .bapi-items-desc { width: 34%; text-align: right; }
  .bapi-items-qty { width: 10%; text-align: center; }
  .bapi-items-uom { width: 8%; text-align: center; }
  .bapi-items-date { width: 14%; text-align: center; }
  .bapi-items-warehouse { width: 14%; text-align: center; }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">درخواست کالا / خدمات</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ درخواست:</span>
          {% if doc.transaction_date %}
            {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.schedule_date %}
        <div>
          <span class="bapi-meta-label">تاریخ مورد نیاز:</span>
          {{ doc.schedule_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره درخواست:</span>
          {{ doc.name }}
        </div>
        {% if doc.material_request_type %}
        <div>
          <span class="bapi-meta-label">نوع درخواست:</span>
          {{ doc.material_request_type }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات شرکت / سازمان</th>
      <th>مشخصات درخواست‌کننده</th>
    </tr>
    <tr>
      <td>
        <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% if doc.set_warehouse %}
          <div><strong>انبار مقصد پیش‌فرض:</strong> {{ doc.set_warehouse }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.requested_by %}
          <div><strong>درخواست‌کننده:</strong> {{ doc.requested_by }}</div>
        {% endif %}
        {% if doc.department %}
          <div><strong>دپارتمان:</strong> {{ doc.department }}</div>
        {% endif %}
        {% if doc.company and not doc.department %}
          <div><strong>واحد سازمانی:</strong> {{ doc.company }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-date">تاریخ مورد نیاز</th>
        <th class="bapi-items-warehouse">انبار مقصد</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-code">{{ row.item_code }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.description or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-qty">{{ row.qty or 0 }}</td>
          <td class="bapi-items-uom">{{ row.uom or "" }}</td>
          <td class="bapi-items-date">
            {% if row.schedule_date %}
              {{ row.schedule_date | as_jdate("YYYY/MM/DD") }}
            {% endif %}
          </td>
          <td class="bapi-items-warehouse">
            {{ row.warehouse or doc.set_warehouse or "" }}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ قلمی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>درخواست‌کننده</td>
      <td>تأیید مدیر واحد</td>
      <td>تأیید انبار / لجستیک</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_packing_slip_v1():
    """Create/Update BLUE_PRINT_PACKING_SLIP_V1 for Packing Slip."""
    NAME = "BLUE_PRINT_PACKING_SLIP_V1"
    DOCTYPE = "Packing Slip"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-code  { width: 16%; }
  .bapi-items-desc  { width: 34%; }
  .bapi-items-qty   { width: 10%; text-align: center; }
  .bapi-items-uom   { width: 8%;  text-align: center; }
  .bapi-items-ware  { width: 16%; text-align: right; }
  .bapi-items-weight{ width: 10%; text-align: center; }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">لیست بسته‌بندی (Packing Slip)</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% else %}
            {{ doc.creation | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره بسته‌بندی:</span>
          {{ doc.name }}
        </div>
        {% if doc.delivery_note %}
        <div>
          <span class="bapi-meta-label">حواله ارسال:</span>
          {{ doc.delivery_note }}
        </div>
        {% endif %}
        {% if doc.sales_invoice %}
        <div>
          <span class="bapi-meta-label">فاکتور فروش:</span>
          {{ doc.sales_invoice }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات گیرنده</th>
    </tr>
    <tr>
      <td>
        {% if doc.company %}
        <div><strong>نام شرکت:</strong> {{ doc.company }}</div>
        {% endif %}
        {% if doc.company_address_display %}
        <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام مشتری:</strong> {{ doc.customer_name or doc.customer or "" }}</div>
        {% if doc.customer_address_display %}
          <div><strong>آدرس:</strong> {{ doc.customer_address_display }}</div>
        {% elif doc.customer_address %}
          <div><strong>آدرس:</strong> {{ doc.customer_address }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-ware">انبار / موقعیت</th>
        <th class="bapi-items-weight">وزن خالص</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.get("items") or [] %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-code">{{ row.item_code }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name or row.item_code }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
          {% endif %}
          {% if row.batch_no %}
            <br><span style="font-size: 8pt; color:#666;">بچ: {{ row.batch_no }}</span>
          {% endif %}
          {% if row.serial_no %}
            <br><span style="font-size: 8pt; color:#666;">سریال: {{ row.serial_no }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty }}</td>
        <td class="bapi-items-uom">{{ row.uom }}</td>
        <td class="bapi-items-ware">{{ row.warehouse or "" }}</td>
        <td class="bapi-items-weight">
          {% if row.net_weight %}
            {{ row.net_weight }}
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات / شرایط حمل:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>بسته‌بندی</td>
      <td>کنترل کیفیت</td>
      <td>تحویل به حمل‌کننده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_payment_entry_v1():
    """Create/Update BLUE_PRINT_PAYMENT_ENTRY_V1 for Payment Entry."""
    NAME = "BLUE_PRINT_PAYMENT_ENTRY_V1"
    DOCTYPE = "Payment Entry"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-refs-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-refs-table th,
  .bapi-refs-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-refs-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-refs-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-refs-idx   { width: 6%;  text-align: center; }
  .bapi-refs-doctype { width: 18%; text-align: center; }
  .bapi-refs-name  { width: 18%; text-align: center; }
  .bapi-refs-date  { width: 14%; text-align: center; }
  .bapi-refs-total { width: 14%; text-align: left; }
  .bapi-refs-out   { width: 14%; text-align: left; }
  .bapi-refs-alloc { width: 16%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 25%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 55%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 45%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% if doc.payment_type == "Receive" %}
  {% set pay_title = "رسید دریافت وجه" %}
{% elif doc.payment_type == "Pay" %}
  {% set pay_title = "رسید پرداخت وجه" %}
{% elif doc.payment_type == "Internal Transfer" %}
  {% set pay_title = "انتقال داخلی وجه" %}
{% else %}
  {% set pay_title = "رسید مالی" %}
{% endif %}

{% set main_amount = doc.paid_amount or doc.received_amount or doc.base_paid_amount or doc.base_received_amount or 0 %}
{% set main_currency = doc.paid_from_account_currency or doc.paid_to_account_currency or doc.currency or "IRR" %}

<div class="bapi-root">

  <div class="bapi-title">{{ pay_title }}</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ سند:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.mode_of_payment %}
        <div>
          <span class="bapi-meta-label">روش پرداخت:</span>
          {{ doc.mode_of_payment }}
        </div>
        {% endif %}
        {% if doc.reference_no %}
        <div>
          <span class="bapi-meta-label">شماره مرجع / چک:</span>
          {{ doc.reference_no }}
          {% if doc.reference_date %}
            ({{ doc.reference_date | as_jdate("YYYY/MM/DD") }})
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات طرف حساب</th>
      <th>حساب‌ها</th>
    </tr>
    <tr>
      <td>
        {% if doc.party_type and doc.party %}
          <div><strong>نوع طرف:</strong> {{ doc.party_type }}</div>
          <div><strong>نام طرف:</strong> {{ doc.party_name or doc.party }}</div>
        {% elif doc.party %}
          <div><strong>طرف حساب:</strong> {{ doc.party }}</div>
        {% else %}
          <div><strong>طرف حساب:</strong> - </div>
        {% endif %}
        {% if doc.contact_person %}
          <div><strong>شخص تماس:</strong> {{ doc.contact_person }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.paid_from %}
          <div><strong>حساب مبدا:</strong> {{ doc.paid_from }}</div>
        {% endif %}
        {% if doc.paid_to %}
          <div><strong>حساب مقصد:</strong> {{ doc.paid_to }}</div>
        {% endif %}
        {% if doc.company %}
          <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-refs-table">
    <thead>
      <tr>
        <th class="bapi-refs-idx">ردیف</th>
        <th class="bapi-refs-doctype">نوع سند</th>
        <th class="bapi-refs-name">شماره سند</th>
        <th class="bapi-refs-date">تاریخ سررسید</th>
        <th class="bapi-refs-total">مبلغ کل</th>
        <th class="bapi-refs-out">مانده قبل</th>
        <th class="bapi-refs-alloc">مبلغ تخصیص</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.references %}
        {% for row in doc.references %}
        <tr>
          <td class="bapi-refs-idx">{{ loop.index }}</td>
          <td class="bapi-refs-doctype">{{ row.reference_doctype }}</td>
          <td class="bapi-refs-name">{{ row.reference_name }}</td>
          <td class="bapi-refs-date">
            {% if row.due_date %}
              {{ row.due_date | as_jdate("YYYY/MM/DD") }}
            {% endif %}
          </td>
          <td class="bapi-refs-total">
            {% if row.total_amount is not none %}
              {{ "{:,.0f}".format(row.total_amount or 0) }}
            {% endif %}
          </td>
          <td class="bapi-refs-out">
            {% if row.outstanding_amount is not none %}
              {{ "{:,.0f}".format(row.outstanding_amount or 0) }}
            {% endif %}
          </td>
          <td class="bapi-refs-alloc">
            {{ "{:,.0f}".format(row.allocated_amount or 0) }}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ سندی برای تسویه لینک نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-totals-label">جمع مبلغ پرداخت‌شده:</td>
      <td class="bapi-totals-value">
        {{ doc.get_formatted("paid_amount") or doc.get_formatted("received_amount") }}
      </td>
    </tr>
    {% if doc.difference_amount %}
    <tr>
      <td></td>
      <td class="bapi-totals-label">اختلاف (نقد/سایر):</td>
      <td class="bapi-totals-value">
        {{ doc.get_formatted("difference_amount") }}
      </td>
    </tr>
    {% endif %}
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">
      مبلغ نهایی این رسید:
    </div>
    <div class="bapi-amount-box-value">
      <div>
        {{ "{:,.0f}".format(main_amount or 0) }} {{ main_currency }}
      </div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ main_amount | money_to_words_fa(main_currency) }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تنظیم‌کننده / صندوق‌دار</td>
      <td>تأیید حسابداری</td>
      <td>امضاء دریافت‌کننده / پرداخت‌شونده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_payroll_entry_v1():
    """
    قالب چاپ خلاصه حقوق و دستمزد برای DocType = Payroll Entry
    - تاریخ‌ها: جلالی + میلادی (J2 / Dual)
    - هدر: لوگو + تاریخ ثبت + دوره حقوق + وضعیت
    - بلوک اطلاعات شرکت و مشخصات دوره
    - جدول لیست فیش‌ها (کارمند / واحد / خالص پرداختی)
    - باکس نارنجی: جمع خالص پرداختی (عدد + حروف)
    """

    NAME = "BLUE_PRINT_PAYROLL_ENTRY_V1"
    DOCTYPE = "Payroll Entry"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-meta-greg {
    font-size: 8pt;
    color: #666;
    margin-right: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-section-title {
    font-weight: 600;
    margin: 10px 0 4px 0;
    font-size: 11pt;
  }

  .bapi-salaryslip-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
  }

  .bapi-salaryslip-table th,
  .bapi-salaryslip-table td {
    border: 1px solid #dddddd;
    padding: 4px 6px;
  }

  .bapi-salaryslip-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-salaryslip-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-idx { width: 6%; text-align: center; }
  .bapi-emp-name { width: 26%; }
  .bapi-emp-id { width: 10%; text-align: center; }
  .bapi-emp-dept { width: 18%; }
  .bapi-emp-desg { width: 18%; }
  .bapi-net-pay { width: 22%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 12px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 45%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 55%;
    text-align: left;
  }

  .bapi-amount-box-words {
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <!-- تیتر اصلی -->
  <div class="bapi-title">خلاصه حقوق و دستمزد</div>

  <!-- هدر: لوگو + تاریخ + دوره + وضعیت -->
  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          <span class="bapi-meta-greg">
            ({{ doc.get_formatted("posting_date") }})
          </span>
        </div>

        {% if doc.start_date and doc.end_date %}
        <div>
          <span class="bapi-meta-label">دوره حقوق:</span>
          {{ doc.start_date | as_jdate("YYYY/MM/DD") }}
          تا
          {{ doc.end_date | as_jdate("YYYY/MM/DD") }}
          <span class="bapi-meta-greg">
            ({{ doc.get_formatted("start_date") }} تا {{ doc.get_formatted("end_date") }})
          </span>
        </div>
        {% endif %}

        {% if doc.payroll_frequency %}
        <div>
          <span class="bapi-meta-label">تناوب پرداخت:</span>
          {{ doc.payroll_frequency }}
        </div>
        {% endif %}

        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>

        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <!-- اطلاعات شرکت و آمار کلی -->
  <table class="bapi-info-table">
    <tr>
      <th>اطلاعات شرکت</th>
      <th>اطلاعات دوره و آمار</th>
    </tr>
    <tr>
      <td>
        <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% if doc.company and frappe.db %}
          {% set comp_abbr = frappe.db.get_value("Company", doc.company, "abbr") %}
          {% if comp_abbr %}
            <div><strong>کد شرکت:</strong> {{ comp_abbr }}</div>
          {% endif %}
        {% endif %}
      </td>
      <td>
        {% if doc.total_employees %}
          <div><strong>تعداد کارکنان در این دوره:</strong> {{ doc.total_employees }}</div>
        {% endif %}
        {% if doc.total_working_days %}
          <div><strong>جمع روزهای کارکرد:</strong> {{ doc.total_working_days }}</div>
        {% endif %}
        {% if doc.total_overtime_hours %}
          <div><strong>جمع اضافه‌کاری (ساعت):</strong> {{ doc.total_overtime_hours }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <!-- لیست فیش‌های حقوقی -->
  <div class="bapi-section-title">فهرست فیش‌های حقوقی در این دوره</div>

  <table class="bapi-salaryslip-table">
    <thead>
      <tr>
        <th class="bapi-idx">ردیف</th>
        <th class="bapi-emp-name">نام کارمند</th>
        <th class="bapi-emp-id">کد</th>
        <th class="bapi-emp-dept">واحد سازمانی</th>
        <th class="bapi-emp-desg">سمت</th>
        <th class="bapi-net-pay">خالص پرداختی (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.salary_slips %}
        {% set grand_net = 0 %}
        {% for row in doc.salary_slips %}
          {% set net_row = row.net_pay or row.base_net_pay or 0 %}
          {% set grand_net = grand_net + (net_row or 0) %}
          <tr>
            <td class="bapi-idx">{{ loop.index }}</td>
            <td class="bapi-emp-name">{{ row.employee_name or row.employee }}</td>
            <td class="bapi-emp-id">{{ row.employee }}</td>
            <td class="bapi-emp-dept">{{ row.department or "" }}</td>
            <td class="bapi-emp-desg">{{ row.designation or "" }}</td>
            <td class="bapi-net-pay">
              ریال {{ "{:,.0f}".format(net_row or 0) }}
            </td>
          </tr>
        {% endfor %}
      {% else %}
        {% set grand_net = doc.total_net_pay or doc.total_amount or 0 %}
        <tr>
          <td colspan="6" style="text-align:center; color:#888;">
            هیچ فیش حقوقی در این سند ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  {% set total_net = doc.total_net_pay or doc.total_amount or grand_net or 0 %}

  <!-- جمع‌ها -->
  <table class="bapi-totals-table">
    <tr>
      <td style="width:50%;"></td>
      <td class="bapi-totals-label">تعداد کارکنان:</td>
      <td class="bapi-totals-value">
        {{ doc.total_employees or (doc.salary_slips | length) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label"><strong>جمع خالص پرداختی:</strong></td>
      <td class="bapi-totals-value">
        <strong>ریال {{ "{:,.0f}".format(total_net or 0) }}</strong>
      </td>
    </tr>
  </table>

  <!-- باکس نارنجی: جمع خالص پرداختی + حروف -->
  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">جمع خالص پرداختی دوره:</div>
    <div class="bapi-amount-box-value">
      <div>ریال {{ "{:,.0f}".format(total_net or 0) }}</div>
      <div class="bapi-amount-box-words">
        مبلغ به حروف:
        {{ (total_net or 0) | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <!-- امضاءها -->
  <table class="bapi-sign-table">
    <tr>
      <td>امضاء تهیه‌کننده</td>
      <td>امضاء مدیر منابع انسانی</td>
      <td>امضاء مدیر مالی / مدیرعامل</td>
    </tr>
  </table>

  <!-- فوتر -->
  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_pick_list_v1():
    """Create/Update BLUE_PRINT_PICK_LIST_V1 for Pick List."""
    NAME = "BLUE_PRINT_PICK_LIST_V1"
    DOCTYPE = "Pick List"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 5%;  text-align: center; }
  .bapi-items-code  { width: 15%; }
  .bapi-items-desc  { width: 30%; }
  .bapi-items-qty   { width: 10%; text-align: center; }
  .bapi-items-picked{ width: 10%; text-align: center; }
  .bapi-items-uom   { width: 8%;  text-align: center; }
  .bapi-items-ware  { width: 12%; text-align: right; }
  .bapi-items-ref   { width: 10%; text-align: right; }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">لیست برداشت (Pick List)</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% else %}
            {{ doc.creation | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره لیست برداشت:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>اطلاعات انبار</th>
      <th>توضیحات</th>
    </tr>
    <tr>
      <td>
        {% if doc.parent_warehouse %}
        <div><strong>انبار اصلی:</strong> {{ doc.parent_warehouse }}</div>
        {% endif %}
        {% if doc.purpose %}
        <div><strong>هدف:</strong> {{ doc.purpose }}</div>
        {% endif %}
        {% if doc.group_by_warehouse %}
        <div><strong>گروه‌بندی براساس انبار:</strong> بله</div>
        {% endif %}
      </td>
      <td>
        {% if doc.note %}
          {{ doc.note }}
        {% elif doc.remarks %}
          {{ doc.remarks }}
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-qty">مقدار مورد نیاز</th>
        <th class="bapi-items-picked">مقدار برداشته‌شده</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-ware">انبار</th>
        <th class="bapi-items-ref">مرجع</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.get("locations") or doc.get("items") or [] %}
      {% set ref = row.sales_order or row.material_request or row.delivery_note %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-code">{{ row.item_code }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name or row.item_code }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
          {% endif %}
          {% if row.batch_no %}
            <br><span style="font-size: 8pt; color:#666;">بچ: {{ row.batch_no }}</span>
          {% endif %}
          {% if row.serial_no %}
            <br><span style="font-size: 8pt; color:#666;">سریال: {{ row.serial_no }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty or row.stock_qty or "" }}</td>
        <td class="bapi-items-picked">{{ row.picked_qty or "" }}</td>
        <td class="bapi-items-uom">{{ row.uom or "" }}</td>
        <td class="bapi-items-ware">{{ row.warehouse or "" }}</td>
        <td class="bapi-items-ref">{{ ref or "" }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">یادداشت اپراتور:</div>
    <div class="bapi-remarks-box">
      {% if doc.picker_remarks %}
        {{ doc.picker_remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>انباردار / پیکر</td>
      <td>کنترل سفارش</td>
      <td>مدیریت</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_pos_invoice_thermal_v1():
    """Create/Update BLUE_PRINT_POS_INVOICE_THERMAL_V1 for POS Invoice."""
    NAME = "BLUE_PRINT_POS_INVOICE_THERMAL_V1"
    DOCTYPE = "POS Invoice"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  @page {
    size: 80mm auto;
    margin: 4mm;
  }

  body {
    margin: 0;
    padding: 0;
  }

  .bpos-root {
    max-width: 80mm;
    margin: 0 auto;
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 9pt;
    color: #222;
  }

  .bpos-header {
    text-align: center;
    margin-bottom: 4px;
  }

  .bpos-logo {
    max-height: 40px;
    margin-bottom: 2px;
  }

  .bpos-title {
    font-size: 11pt;
    font-weight: 700;
    margin-bottom: 2px;
  }

  .bpos-subtitle {
    font-size: 8pt;
    color: #555;
  }

  .bpos-meta {
    margin-top: 4px;
    border-top: 1px dashed #999;
    border-bottom: 1px dashed #999;
    padding: 4px 0;
    font-size: 8.2pt;
  }

  .bpos-meta-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1px;
  }

  .bpos-meta-label {
    font-weight: 600;
    margin-left: 3px;
  }

  .bpos-cust {
    margin-top: 4px;
    font-size: 8.5pt;
  }

  .bpos-cust span {
    font-weight: 600;
  }

  .bpos-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 8.3pt;
  }

  .bpos-items-table th,
  .bpos-items-table td {
    padding: 3px 2px;
  }

  .bpos-items-table thead th {
    border-bottom: 1px dashed #999;
    text-align: center;
    font-weight: 600;
  }

  .bpos-items-idx   { width: 8%;  text-align: center; }
  .bpos-items-name  { width: 44%; text-align: right; }
  .bpos-items-qty   { width: 12%; text-align: center; }
  .bpos-items-rate  { width: 18%; text-align: left; }
  .bpos-items-amt   { width: 18%; text-align: left; }

  .bpos-items-table tbody tr td {
    border-bottom: 1px dotted #e0e0e0;
  }

  .bpos-totals {
    margin-top: 4px;
    border-top: 1px dashed #999;
    padding-top: 4px;
    font-size: 8.4pt;
  }

  .bpos-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1px;
  }

  .bpos-row-label {
    font-weight: 600;
  }

  .bpos-grand {
    margin-top: 4px;
    padding-top: 3px;
    border-top: 1px solid #000;
    font-weight: 700;
  }

  .bpos-grand .bpos-row-label {
    font-size: 9.5pt;
  }

  .bpos-payments {
    margin-top: 4px;
    border-top: 1px dashed #999;
    padding-top: 3px;
    font-size: 8.2pt;
  }

  .bpos-payments-title {
    font-weight: 600;
    margin-bottom: 2px;
  }

  .bpos-pay-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1px;
  }

  .bpos-note {
    margin-top: 4px;
    font-size: 7.8pt;
  }

  .bpos-footer {
    margin-top: 6px;
    border-top: 1px dashed #999;
    padding-top: 3px;
    text-align: center;
    font-size: 7.5pt;
  }

  .bpos-footer strong {
    display: block;
    margin-bottom: 2px;
  }
</style>

<div class="bpos-root">

  <div class="bpos-header">
    <img src="/files/blueapi-logo.png" class="bpos-logo">
    <div class="bpos-title">رسید فروش (POS)</div>
    <div class="bpos-subtitle">
      بلو ای‌پی‌آی / BlueAPI — سیستم فروش فروشگاهی
    </div>
  </div>

  <div class="bpos-meta">
    <div class="bpos-meta-row">
      <div>
        <span class="bpos-meta-label">فاکتور:</span>
        {{ doc.name }}
      </div>
      <div>
        <span class="bpos-meta-label">تاریخ:</span>
        {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
      </div>
    </div>
    <div class="bpos-meta-row">
      <div>
        <span class="bpos-meta-label">زمان:</span>
        {{ doc.posting_time or "" }}
      </div>
      {% if doc.pos_profile %}
      <div>
        <span class="bpos-meta-label">پروفایل POS:</span>
        {{ doc.pos_profile }}
      </div>
      {% endif %}
    </div>
  </div>

  <div class="bpos-cust">
    {% if doc.customer_name %}
      <div>
        <span>مشتری:</span> {{ doc.customer_name }}
      </div>
    {% elif doc.customer %}
      <div>
        <span>مشتری:</span> {{ doc.customer }}
      </div>
    {% endif %}
    {% if doc.customer_address %}
      <div>
        <span>آدرس:</span> {{ doc.address_display or doc.customer_address }}
      </div>
    {% endif %}
  </div>

  <table class="bpos-items-table">
    <thead>
      <tr>
        <th class="bpos-items-idx">#</th>
        <th class="bpos-items-name">شرح</th>
        <th class="bpos-items-qty">تعداد</th>
        <th class="bpos-items-rate">نرخ</th>
        <th class="bpos-items-amt">مبلغ</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bpos-items-idx">{{ loop.index }}</td>
        <td class="bpos-items-name">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 7pt; color:#666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bpos-items-qty">
          {{ row.qty | int }}
        </td>
        <td class="bpos-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bpos-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="bpos-totals">
    <div class="bpos-row">
      <div class="bpos-row-label">جمع اقلام:</div>
      <div>
        ریال {{ "{:,.0f}".format(doc.total or doc.net_total or 0) }}
      </div>
    </div>

    {% if doc.discount_amount %}
    <div class="bpos-row">
      <div class="bpos-row-label">تخفیف:</div>
      <div>
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </div>
    </div>
    {% endif %}

    {% if doc.total_taxes_and_charges %}
    <div class="bpos-row">
      <div class="bpos-row-label">مالیات و عوارض:</div>
      <div>
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </div>
    </div>
    {% endif %}

    <div class="bpos-row bpos-grand">
      <div class="bpos-row-label">مبلغ نهایی قابل پرداخت:</div>
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or doc.rounded_total or 0) }}
      </div>
    </div>

    {% if doc.change_amount %}
    <div class="bpos-row">
      <div class="bpos-row-label">مبلغ برگشتی به مشتری:</div>
      <div>
        ریال {{ "{:,.0f}".format(doc.change_amount or 0) }}
      </div>
    </div>
    {% endif %}
  </div>

  {% set pays = doc.get("payments") or [] %}
  {% if pays %}
  <div class="bpos-payments">
    <div class="bpos-payments-title">جزئیات پرداخت:</div>
    {% for p in pays %}
      <div class="bpos-pay-row">
        <div>{{ p.mode_of_payment }}</div>
        <div>ریال {{ "{:,.0f}".format(p.amount or 0) }}</div>
      </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
  <div class="bpos-note">
    {{ doc.remarks }}
  </div>
  {% endif %}

  <div class="bpos-footer">
    <strong>از خرید شما سپاسگزاریم</strong>
    بلو ای‌پی‌آی BlueAPI — سیستم فروش فروشگاهی<br>
    Telegram: @blueapi &nbsp;|&nbsp; Instagram: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_pos_invoice_v1():
    """Create/Update BLUE_PRINT_POS_INVOICE_V1 for POS Invoice."""
    NAME = "BLUE_PRINT_POS_INVOICE_V1"
    DOCTYPE = "POS Invoice"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  /* رسید حرارتی ۸ سانتی‌متری */
  .bpos-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 9pt;
    color: #222;
    width: 80mm;
    margin: 0 auto;
  }

  .bpos-header {
    text-align: center;
    margin-bottom: 6px;
  }

  .bpos-logo {
    max-height: 40px;
    margin-bottom: 4px;
  }

  .bpos-title {
    font-size: 12pt;
    font-weight: 700;
    margin-bottom: 2px;
  }

  .bpos-subtitle {
    font-size: 8pt;
    margin-bottom: 4px;
  }

  .bpos-separator {
    border-top: 1px dashed #999;
    margin: 4px 0;
  }

  .bpos-meta {
    font-size: 8pt;
    margin-bottom: 4px;
  }

  .bpos-meta-row {
    display: flex;
    justify-content: space-between;
  }

  .bpos-meta-label {
    font-weight: 600;
    margin-left: 2px;
  }

  .bpos-party {
    font-size: 8pt;
    margin-bottom: 4px;
  }

  .bpos-party div {
    margin-bottom: 1px;
  }

  .bpos-items-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
    margin-top: 2px;
  }

  .bpos-items-table th,
  .bpos-items-table td {
    padding: 2px 2px;
  }

  .bpos-items-table th {
    border-bottom: 1px solid #333;
    font-weight: 600;
    text-align: center;
  }

  .bpos-items-idx { width: 8%; text-align: center; }
  .bpos-items-desc { width: 52%; text-align: right; }
  .bpos-items-qty { width: 10%; text-align: center; }
  .bpos-items-rate { width: 15%; text-align: left; }
  .bpos-items-amt { width: 15%; text-align: left; }

  .bpos-items-table tbody tr:nth-child(odd) {
    background-color: #f7f7f7;
  }

  .bpos-totals {
    font-size: 8.5pt;
    margin-top: 4px;
  }

  .bpos-totals-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2px;
  }

  .bpos-totals-label {
    font-weight: 600;
  }

  .bpos-amount-box {
    margin-top: 4px;
    border: 1px solid #ff8c00;
    padding: 4px 4px;
    font-size: 9pt;
  }

  .bpos-amount-main {
    display: flex;
    justify-content: space-between;
    font-weight: 700;
    margin-bottom: 2px;
  }

  .bpos-amount-words {
    font-size: 8pt;
  }

  .bpos-footer {
    margin-top: 6px;
    font-size: 7.5pt;
    text-align: center;
  }

  .bpos-footer div {
    margin-bottom: 1px;
  }
</style>

<div class="bpos-root">

  <div class="bpos-header">
    <img src="/files/blueapi-logo.png" class="bpos-logo">
    <div class="bpos-title">رسید فروش (POS)</div>
    <div class="bpos-subtitle">بلو ای‌پی‌آی BlueAPI</div>
  </div>

  <div class="bpos-meta">
    <div class="bpos-meta-row">
      <div>
        <span class="bpos-meta-label">تاریخ:</span>
        {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
      </div>
      <div>
        <span class="bpos-meta-label">زمان:</span>
        {{ doc.posting_time }}
      </div>
    </div>
    <div class="bpos-meta-row">
      <div>
        <span class="bpos-meta-label">شماره رسید:</span>
        {{ doc.name }}
      </div>
      {% if doc.pos_profile %}
      <div>
        <span class="bpos-meta-label">پروفایل POS:</span>
        {{ doc.pos_profile }}
      </div>
      {% endif %}
    </div>
  </div>

  <div class="bpos-party">
    <div><strong>مشتری:</strong> {{ doc.customer_name or doc.customer }}</div>
    {% if doc.customer_address %}
      <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
    {% endif %}
  </div>

  <div class="bpos-separator"></div>

  <table class="bpos-items-table">
    <thead>
      <tr>
        <th class="bpos-items-idx">ردیف</th>
        <th class="bpos-items-desc">شرح</th>
        <th class="bpos-items-qty">تعداد</th>
        <th class="bpos-items-rate">نرخ</th>
        <th class="bpos-items-amt">مبلغ</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bpos-items-idx">{{ loop.index }}</td>
        <td class="bpos-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 7pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bpos-items-qty">{{ row.qty | int }}</td>
        <td class="bpos-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bpos-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="bpos-separator"></div>

  <div class="bpos-totals">
    <div class="bpos-totals-row">
      <div class="bpos-totals-label">جمع مبلغ اقلام:</div>
      <div>ریال {{ "{:,.0f}".format(doc.total or 0) }}</div>
    </div>
    <div class="bpos-totals-row">
      <div class="bpos-totals-label">تخفیف:</div>
      <div>ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}</div>
    </div>
    <div class="bpos-totals-row">
      <div class="bpos-totals-label">مالیات و عوارض:</div>
      <div>ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}</div>
    </div>
  </div>

  <div class="bpos-amount-box">
    <div class="bpos-amount-main">
      <span>مبلغ نهایی قابل پرداخت:</span>
      <span>ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}</span>
    </div>
    <div class="bpos-amount-words">
      مبلغ به حروف:
      {{ doc.grand_total | money_to_words_fa("IRR") }}
    </div>
  </div>

  <div class="bpos-totals" style="margin-top: 4px;">
    <div class="bpos-totals-row">
      <div class="bpos-totals-label">مبلغ دریافت‌شده:</div>
      <div>ریال {{ "{:,.0f}".format(doc.paid_amount or 0) }}</div>
    </div>
    <div class="bpos-totals-row">
      <div class="bpos-totals-label">مبلغ برگشتی به مشتری:</div>
      <div>ریال {{ "{:,.0f}".format(doc.change_amount or 0) }}</div>
    </div>
  </div>

  <div class="bpos-separator"></div>

  <div class="bpos-footer">
    <div>از خرید شما متشکریم</div>
    <div>بلو ای‌پی‌آی BlueAPI</div>
    <div>Telegram: @blueapi | Instagram: @blueapi | X: @blueapi</div>
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_production_plan_v1():
    """Create/Update BLUE_PRINT_PRODUCTION_PLAN_V1 for Production Plan."""
    NAME = "BLUE_PRINT_PRODUCTION_PLAN_V1"
    DOCTYPE = "Production Plan"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-code  { width: 20%; }
  .bapi-items-desc  { width: 34%; }
  .bapi-items-qty   { width: 12%; text-align: center; }
  .bapi-items-uom   { width: 10%; text-align: center; }
  .bapi-items-ware  { width: 18%; text-align: right; }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">برنامه تولید (Production Plan)</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ برنامه:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% else %}
            {{ doc.creation | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره برنامه تولید:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.planned_start_date %}
        <div>
          <span class="bapi-meta-label">تاریخ شروع برنامه:</span>
          {{ doc.planned_start_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        {% if doc.planned_end_date %}
        <div>
          <span class="bapi-meta-label">تاریخ پایان برنامه:</span>
          {{ doc.planned_end_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات برنامه تولید</th>
      <th>توضیحات کلی</th>
    </tr>
    <tr>
      <td>
        {% if doc.get("project") %}
        <div><strong>پروژه مرتبط:</strong> {{ doc.project }}</div>
        {% endif %}
        {% if doc.get("sales_order_based_on") %}
        <div><strong>مبنای سفارش فروش:</strong> {{ doc.sales_order_based_on }}</div>
        {% endif %}
        {% if doc.get("material_request_type") %}
        <div><strong>نوع درخواست تأمین:</strong> {{ doc.material_request_type }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.description %}
          {{ doc.description }}
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-qty">مقدار برنامه‌ریزی‌شده</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-ware">انبار / موقعیت</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.get("items") or [] %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-code">{{ row.item_code }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name or row.item_code }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.planned_qty or row.qty }}</td>
        <td class="bapi-items-uom">{{ row.uom }}</td>
        <td class="bapi-items-ware">
          {{ row.warehouse or row.source_warehouse or "" }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات تکمیلی:</div>
    <div class="bapi-remarks-box">
      {% if doc.more_info %}
        {{ doc.more_info }}
      {% elif doc.remarks %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>برنامه‌ریز تولید</td>
      <td>مدیر تولید</td>
      <td>انبار / لجستیک</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_project_task_v1():
    """Create/Update BLUE_PRINT_PROJECT_TASK_V1 for Task (Project Task)."""
    NAME = "BLUE_PRINT_PROJECT_TASK_V1"
    DOCTYPE = "Task"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-timesheet-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-timesheet-table th,
  .bapi-timesheet-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-timesheet-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-timesheet-idx   { width: 6%;  text-align: center; }
  .bapi-timesheet-date  { width: 16%; text-align: center; }
  .bapi-timesheet-hours { width: 12%; text-align: center; }
  .bapi-timesheet-user  { width: 20%; text-align: right; }
  .bapi-timesheet-desc  { width: 46%; text-align: right; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 3px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">گزارش تسک پروژه</div>
  <div class="bapi-subtitle">
    مشخصات تسک، زمان‌بندی، منابع صرف‌شده و توضیحات مربوط به تسک پروژه.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">کد تسک:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">عنوان تسک:</span>
          {{ doc.subject or doc.title or doc.name }}
        </div>
        {% if doc.project %}
        <div>
          <span class="bapi-meta-label">پروژه:</span>
          {{ doc.project }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
        {% if doc.priority %}
        <div>
          <span class="bapi-meta-label">اولویت:</span>
          {{ doc.priority }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>زمان‌بندی و پیشرفت</th>
      <th>مسئولیت و دسته‌بندی</th>
    </tr>
    <tr>
      <td>
        {% set sd = doc.exp_start_date or doc.expected_start_date or doc.start_date %}
        {% set ed = doc.exp_end_date or doc.expected_end_date or doc.end_date %}
        {% if sd %}
          <div>
            <strong>تاریخ شروع برنامه‌ریزی:</strong>
            {{ sd | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if ed %}
          <div>
            <strong>تاریخ پایان برنامه‌ریزی:</strong>
            {{ ed | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.actual_start_date %}
          <div>
            <strong>تاریخ شروع واقعی:</strong>
            {{ doc.actual_start_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.actual_end_date %}
          <div>
            <strong>تاریخ پایان واقعی:</strong>
            {{ doc.actual_end_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.progress is not none %}
          <div>
            <strong>درصد پیشرفت:</strong>
            {{ doc.progress }}%
          </div>
        {% endif %}
        {% if doc.task_weight %}
          <div>
            <strong>وزن تسک در پروژه:</strong>
            {{ doc.task_weight }}
          </div>
        {% endif %}
      </td>
      <td>
        {% if doc.department %}
          <div><strong>واحد سازمانی:</strong> {{ doc.department }}</div>
        {% endif %}
        {% if doc.owner %}
          <div><strong>ایجادکننده:</strong> {{ doc.owner }}</div>
        {% endif %}
        {% if doc.assigned_to %}
          <div><strong>مسئول اصلی:</strong> {{ doc.assigned_to }}</div>
        {% endif %}
        {% if doc.is_group %}
          <div><strong>نوع تسک:</strong> {{ "تسک گروهی" if doc.is_group else "تسک تکی" }}</div>
        {% endif %}
        {% if doc.is_template %}
          <div><strong>الگوی تسک:</strong> {{ "بله" if doc.is_template else "خیر" }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  {% set rows = doc.get("timesheets") or doc.get("time_logs") or [] %}

  <table class="bapi-timesheet-table">
    <thead>
      <tr>
        <th class="bapi-timesheet-idx">ردیف</th>
        <th class="bapi-timesheet-date">تاریخ کارکرد</th>
        <th class="bapi-timesheet-hours">ساعت کارکرد</th>
        <th class="bapi-timesheet-user">کاربر / کارشناس</th>
        <th class="bapi-timesheet-desc">شرح فعالیت</th>
      </tr>
    </thead>
    <tbody>
      {% if rows %}
        {% for row in rows %}
        <tr>
          <td class="bapi-timesheet-idx">{{ loop.index }}</td>
          <td class="bapi-timesheet-date">
            {% set d = row.from_time or row.to_time or row.date %}
            {% if d %}
              {{ d | as_jdate("YYYY/MM/DD") }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-timesheet-hours">
            {% if row.hours %}
              {{ row.hours }}
            {% elif row.hours_f %}
              {{ row.hours_f }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-timesheet-user">
            {{ row.employee or row.user or row.full_name or "" }}
          </td>
          <td class="bapi-timesheet-desc">
            {{ row.activity_type or row.description or "" }}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="5" style="text-align:center; color:#777;">
            هیچ رکورد زمان‌کاری برای این تسک ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">جمع ساعات کارکرد:</td>
      <td class="bapi-summary-value">
        {% if doc.total_hours %}
          {{ doc.total_hours }}
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرح تسک و یادداشت‌ها:</div>
    <div class="bapi-remarks-box">
      {% if doc.description %}
        {{ doc.description }}
      {% endif %}
      {% if doc.notes %}
        <br>{{ doc.notes }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>مسئول تسک</td>
      <td>مدیر پروژه</td>
      <td>مدیر واحد / کارفرما</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_project_v1():
    """Create/Update BLUE_PRINT_PROJECT_V1 for Project."""
    NAME = "BLUE_PRINT_PROJECT_V1"
    DOCTYPE = "Project"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-tasks-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-tasks-table th,
  .bapi-tasks-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-tasks-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-tasks-idx   { width: 6%;  text-align: center; }
  .bapi-tasks-subj  { width: 30%; text-align: right; }
  .bapi-tasks-stat  { width: 14%; text-align: center; }
  .bapi-tasks-prio  { width: 10%; text-align: center; }
  .bapi-tasks-start { width: 12%; text-align: center; }
  .bapi-tasks-end   { width: 12%; text-align: center; }
  .bapi-tasks-prog  { width: 16%; text-align: center; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 3px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 24px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">گزارش پروژه</div>
  <div class="bapi-subtitle">
    مشخصات کلی، وضعیت پیشرفت و خلاصه‌ی مالی پروژه در سیستم بلوحساب / BlueHesab.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">کد پروژه:</span>
          {{ doc.name }}
        </div>
        <div>
          <span class="bapi-meta-label">نام پروژه:</span>
          {{ doc.project_name or doc.name }}
        </div>
        {% if doc.customer %}
        <div>
          <span class="bapi-meta-label">مشتری / کارفرما:</span>
          {{ doc.customer }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
        {% if doc.priority %}
        <div>
          <span class="bapi-meta-label">اولویت:</span>
          {{ doc.priority }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>مشخصات برنامه‌ریزی و اجرا</th>
      <th>وضعیت مالی و پیشرفت</th>
    </tr>
    <tr>
      <td>
        {% if doc.expected_start_date %}
          <div>
            <strong>تاریخ شروع برنامه‌ریزی:</strong>
            {{ doc.expected_start_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.expected_end_date %}
          <div>
            <strong>تاریخ پایان برنامه‌ریزی:</strong>
            {{ doc.expected_end_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.actual_start_date %}
          <div>
            <strong>تاریخ شروع واقعی:</strong>
            {{ doc.actual_start_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.actual_end_date %}
          <div>
            <strong>تاریخ پایان واقعی:</strong>
            {{ doc.actual_end_date | as_jdate("YYYY/MM/DD") }}
          </div>
        {% endif %}
        {% if doc.project_type %}
          <div>
            <strong>نوع پروژه:</strong> {{ doc.project_type }}
          </div>
        {% endif %}
        {% if doc.project_manager %}
          <div>
            <strong>مدیر پروژه:</strong> {{ doc.project_manager }}
          </div>
        {% endif %}
      </td>
      <td>
        {% if doc.percent_complete is not none %}
          <div>
            <strong>درصد پیشرفت:</strong>
            {{ doc.percent_complete }}%
          </div>
        {% endif %}
        {% if doc.total_billing_amount %}
          <div>
            <strong>جمع صورت‌حساب‌ها (ریال):</strong>
            {{ "{:,.0f}".format(doc.total_billing_amount or 0) }}
          </div>
        {% endif %}
        {% if doc.total_costing_amount %}
          <div>
            <strong>جمع هزینه‌های پروژه (ریال):</strong>
            {{ "{:,.0f}".format(doc.total_costing_amount or 0) }}
          </div>
        {% endif %}
        {% if doc.gross_margin %}
          <div>
            <strong>حاشیه سود (ریال):</strong>
            {{ "{:,.0f}".format(doc.gross_margin or 0) }}
          </div>
        {% endif %}
        {% if doc.per_gross_margin %}
          <div>
            <strong>حاشیه سود (%):</strong>
            {{ doc.per_gross_margin }}%
          </div>
        {% endif %}
      </td>
    </tr>
  </table>

  {% set rows = doc.get("tasks") or [] %}

  <table class="bapi-tasks-table">
    <thead>
      <tr>
        <th class="bapi-tasks-idx">ردیف</th>
        <th class="bapi-tasks-subj">عنوان تسک / فعالیت</th>
        <th class="bapi-tasks-stat">وضعیت</th>
        <th class="bapi-tasks-prio">اولویت</th>
        <th class="bapi-tasks-start">تاریخ شروع</th>
        <th class="bapi-tasks-end">تاریخ پایان</th>
        <th class="bapi-tasks-prog">پیشرفت</th>
      </tr>
    </thead>
    <tbody>
      {% if rows %}
        {% for row in rows %}
        <tr>
          <td class="bapi-tasks-idx">{{ loop.index }}</td>
          <td class="bapi-tasks-subj">
            {{ row.subject or row.title or row.task or "" }}
          </td>
          <td class="bapi-tasks-stat">
            {{ row.status or "-" }}
          </td>
          <td class="bapi-tasks-prio">
            {{ row.priority or "-" }}
          </td>
          <td class="bapi-tasks-start">
            {% set sd = row.start_date or row.expected_start_date or row.exp_start_date %}
            {% if sd %}
              {{ sd | as_jdate("YYYY/MM/DD") }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-tasks-end">
            {% set ed = row.end_date or row.expected_end_date or row.exp_end_date %}
            {% if ed %}
              {{ ed | as_jdate("YYYY/MM/DD") }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-tasks-prog">
            {% if row.progress is not none %}
              {{ row.progress }}%
            {% elif row.task_weight %}
              وزن: {{ row.task_weight }}
            {% else %}
              -
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ تسکی برای این پروژه ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">جمع هزینه‌های پروژه:</td>
      <td class="bapi-summary-value">
        ریال {{ "{:,.0f}".format(doc.total_costing_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-summary-label">جمع هزینه به حروف:</td>
      <td class="bapi-summary-value">
        {% set cost = doc.total_costing_amount or 0 %}
        {% if cost and cost > 0 %}
          {{ cost | money_to_words_fa("IRR") }}
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرح کلی پروژه / یادداشت‌ها:</div>
    <div class="bapi-remarks-box">
      {% if doc.notes %}
        {{ doc.notes }}
      {% elif doc.description %}
        {{ doc.description }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>مدیر پروژه</td>
      <td>مدیر واحد / کارفرما</td>
      <td>مدیرعامل / مقام مجاز</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_purchase_invoice_v1():
    """Create/Update BLUE_PRINT_PURCHASE_INVOICE_V1 for Purchase Invoice."""
    NAME = "BLUE_PRINT_PURCHASE_INVOICE_V1"
    DOCTYPE = "Purchase Invoice"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-amount-words {
    margin-top: 6px;
    font-size: 9.5pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">فاکتور خرید</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% if doc.due_date %}
        <div>
          <span class="bapi-meta-label">تاریخ سررسید:</span>
          {{ doc.due_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره فاکتور:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات خریدار</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام فروشنده:</strong> {{ doc.supplier_name or doc.supplier }}</div>
        {% if doc.supplier_address_display or doc.supplier_address %}
          <div>
            <strong>آدرس:</strong>
            {{ doc.supplier_address_display or doc.supplier_address }}
          </div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">قیمت کل (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی قابل پرداخت:</div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}
      </div>
      <div style="margin-top: 4px; font-size: 9.5pt;">
        مبلغ به حروف:
        {{ doc.grand_total | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء خریدار</td>
      <td>امضاء حسابداری</td>
      <td>امضاء صادرکننده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_purchase_order_v1():
    """Create/Update BLUE_PRINT_PURCHASE_ORDER_V1 for Purchase Order."""
    NAME = "BLUE_PRINT_PURCHASE_ORDER_V1"
    DOCTYPE = "Purchase Order"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-amount-words {
    margin-top: 6px;
    font-size: 9.5pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">سفارش خرید</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% if doc.schedule_date %}
        <div>
          <span class="bapi-meta-label">تاریخ سررسید:</span>
          {{ doc.schedule_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره سفارش:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات خریدار</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام فروشنده:</strong> {{ doc.supplier_name or doc.supplier }}</div>
        {% if doc.supplier_address_display or doc.supplier_address %}
          <div>
            <strong>آدرس:</strong>
            {{ doc.supplier_address_display or doc.supplier_address }}
          </div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">قیمت کل (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی قابل پرداخت:</div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}
      </div>
      <div style="margin-top: 4px; font-size: 9.5pt;">
        مبلغ به حروف:
        {{ doc.grand_total | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء خریدار</td>
      <td>امضاء حسابداری</td>
      <td>امضاء صادرکننده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_purchase_receipt_v1():
    """Create/Update BLUE_PRINT_PURCHASE_RECEIPT_V1 for Purchase Receipt."""
    NAME = "BLUE_PRINT_PURCHASE_RECEIPT_V1"
    DOCTYPE = "Purchase Receipt"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #444;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx    { width: 6%;  text-align: center; }
  .bapi-items-code   { width: 14%; text-align: center; }
  .bapi-items-desc   { width: 30%; text-align: right; }
  .bapi-items-qty    { width: 8%;  text-align: center; }
  .bapi-items-uom    { width: 8%;  text-align: center; }
  .bapi-items-ware   { width: 18%; text-align: right; }
  .bapi-items-amount { width: 16%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
    font-weight: 400;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% set pr_currency = doc.currency or doc.company_currency or "IRR" %}
{% set pr_total = doc.grand_total or doc.base_grand_total
                  or doc.rounded_total or doc.base_rounded_total
                  or doc.net_total or doc.base_net_total or 0 %}
{% set pr_abs_total = pr_total %}
{% if pr_abs_total < 0 %}
  {% set pr_abs_total = 0 - pr_abs_total %}
{% endif %}

<div class="bapi-root">

  <div class="bapi-title">رسید خرید / Purchase Receipt</div>
  <div class="bapi-subtitle">
    این سند نشان‌دهنده‌ی دریافت کالا/خدمات در انبار یا محل تحویل است و مبنای ثبت موجودی می‌باشد.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ ثبت رسید:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.posting_time %}
        <div>
          <span class="bapi-meta-label">ساعت ثبت:</span>
          {{ doc.posting_time[:5] }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره رسید خرید:</span>
          {{ doc.name }}
        </div>
        {% if doc.supplier_delivery_note %}
        <div>
          <span class="bapi-meta-label">شماره برگه تحویل تأمین‌کننده:</span>
          {{ doc.supplier_delivery_note }}
        </div>
        {% endif %}
        {% if doc.purchase_order %}
        <div>
          <span class="bapi-meta-label">ارجاع به سفارش خرید:</span>
          {{ doc.purchase_order }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات تأمین‌کننده / فروشنده</th>
      <th>مشخصات خریدار / محل دریافت</th>
    </tr>
    <tr>
      <td>
        {% if doc.supplier %}
          <div><strong>نام تأمین‌کننده:</strong> {{ doc.supplier_name or doc.supplier }}</div>
        {% endif %}
        {% if doc.supplier_address or doc.address_display %}
          <div><strong>آدرس تأمین‌کننده:</strong> {{ doc.address_display or doc.supplier_address }}</div>
        {% endif %}
        {% if doc.supplier_tax_id %}
          <div><strong>شناسه/کد مالیاتی تأمین‌کننده:</strong> {{ doc.supplier_tax_id }}</div>
        {% endif %}
        {% if doc.contact_display %}
          <div><strong>اطلاعات تماس:</strong> {{ doc.contact_display }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.company %}
          <div><strong>شرکت خریدار:</strong> {{ doc.company }}</div>
        {% endif %}
        {% if doc.company_address_display %}
          <div><strong>آدرس شرکت:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
        {% if doc.set_warehouse %}
          <div><strong>انبار/محل دریافت:</strong> {{ doc.set_warehouse }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا / خدمت دریافتی</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-ware">انبار</th>
        <th class="bapi-items-amount">ارزش ({{ pr_currency }})</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-code">{{ row.item_code }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.description or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
            {% endif %}
            {% if row.batch_no %}
              <br><span style="font-size: 8pt; color:#555;">Batch: {{ row.batch_no }}</span>
            {% endif %}
            {% if row.serial_no %}
              <br><span style="font-size: 8pt; color:#555;">Serial: {{ row.serial_no }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-qty">{{ row.qty }}</td>
          <td class="bapi-items-uom">{{ row.uom or row.stock_uom or "" }}</td>
          <td class="bapi-items-ware">{{ row.warehouse or doc.set_warehouse or "" }}</td>
          <td class="bapi-items-amount">
            {% if row.get_formatted %}
              {{ row.get_formatted("amount") }}
            {% else %}
              {{ row.amount or 0 }}
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ قلمی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع ارزش اقلام:</td>
      <td class="bapi-totals-value">
        {% if doc.get_formatted %}
          {{ doc.get_formatted("total") or doc.get_formatted("net_total") }}
        {% else %}
          {{ doc.total or doc.net_total or 0 }}
        {% endif %}
      </td>
    </tr>
    {% if doc.total_taxes_and_charges %}
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات و عوارض:</td>
      <td class="bapi-totals-value">
        {% if doc.get_formatted %}
          {{ doc.get_formatted("total_taxes_and_charges") }}
        {% else %}
          {{ doc.total_taxes_and_charges or 0 }}
        {% endif %}
      </td>
    </tr>
    {% endif %}
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">ارزش کل رسید خرید (براساس سند):</div>
    <div class="bapi-amount-box-value">
      <div>
        {% if doc.get_formatted %}
          {{ doc.get_formatted("grand_total") or doc.get_formatted("net_total")
             or doc.get_formatted("rounded_total") }}
        {% else %}
          {{ pr_total }} {{ pr_currency }}
        {% endif %}
      </div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ pr_abs_total | money_to_words_fa(pr_currency) }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات و شرایط دریافت:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تحویل‌گیرنده در انبار</td>
      <td>مسئول کنترل کیفیت / فنی</td>
      <td>نماینده تأمین‌کننده (مهر و امضاء)</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_purchase_return_v1():
    """Create/Update BLUE_PRINT_PURCHASE_RETURN_V1 for Purchase Invoice (Return / Debit Note)."""
    NAME = "BLUE_PRINT_PURCHASE_RETURN_V1"
    DOCTYPE = "Purchase Invoice"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 4px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #b00020;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
    font-weight: 400;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% set pi_currency = doc.currency or doc.company_currency or "IRR" %}
{% set pi_total = doc.grand_total or doc.base_grand_total or 0 %}
{% set pi_abs_total = pi_total %}
{% if pi_abs_total < 0 %}
  {% set pi_abs_total = 0 - pi_abs_total %}
{% endif %}

<div class="bapi-root">

  <div class="bapi-title">برگشت از خرید / Purchase Return</div>
  <div class="bapi-subtitle">
    این سند به‌عنوان «یادداشت بدهکار / Debit Note» برای تأمین‌کننده ثبت شده است.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ سند برگشت:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.return_against %}
        <div>
          <span class="bapi-meta-label">ارجاع به فاکتور خرید اصلی:</span>
          {{ doc.return_against }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره سند برگشت:</span>
          {{ doc.name }}
        </div>
        {% if doc.supplier %}
        <div>
          <span class="bapi-meta-label">تأمین‌کننده:</span>
          {{ doc.supplier_name or doc.supplier }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات تأمین‌کننده</th>
      <th>مشخصات خریدار (شرکت)</th>
    </tr>
    <tr>
      <td>
        {% if doc.supplier %}
          <div><strong>نام تأمین‌کننده:</strong> {{ doc.supplier_name or doc.supplier }}</div>
        {% endif %}
        {% if doc.supplier_address %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.supplier_address }}</div>
        {% endif %}
        {% if doc.contact_display %}
          <div><strong>اطلاعات تماس:</strong> {{ doc.contact_display }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.company %}
          <div><strong>شرکت خریدار:</strong> {{ doc.company }}</div>
        {% endif %}
        {% if doc.company_address_display %}
          <div><strong>آدرس شرکت:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
        {% if doc.company_tax_id %}
          <div><strong>شناسه/کد مالیاتی:</strong> {{ doc.company_tax_id }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت برگشتی</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد ({{ pi_currency }})</th>
        <th class="bapi-items-amt">مبلغ برگشت ({{ pi_currency }})</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-qty">{{ row.qty }}</td>
          <td class="bapi-items-rate">{{ row.get_formatted("rate") }}</td>
          <td class="bapi-items-amt">{{ row.get_formatted("amount") }}</td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="5" style="text-align:center; color:#777;">
            هیچ قلمی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام برگشتی:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("total") }}</td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف برگشتی:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("discount_amount") }}</td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات تعدیلی:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("total_taxes_and_charges") }}</td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی برگشت / بدهکار صادرشده:</div>
    <div class="bapi-amount-box-value">
      <div>{{ doc.get_formatted("grand_total") }}</div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ pi_abs_total | money_to_words_fa(pi_currency) }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">علت برگشت و توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تنظیم‌کننده سند</td>
      <td>تأیید واحد تدارکات / خرید</td>
      <td>تأیید واحد مالی / حسابداری</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_quotation_v1():
    """Create/Update BLUE_PRINT_QUOTATION_V1 for Quotation (Sales Quotation)."""
    NAME = "BLUE_PRINT_QUOTATION_V1"
    DOCTYPE = "Quotation"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-amount-words {
    margin-top: 6px;
    font-size: 9.5pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">پیش‌فاکتور / پیشنهاد قیمت</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% if doc.valid_till %}
        <div>
          <span class="bapi-meta-label">تاریخ اعتبار تا:</span>
          {{ doc.valid_till | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره پیش‌فاکتور:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات خریدار</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام فروشنده:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong>
          {{ doc.customer_name or doc.customer or doc.party_name or doc.lead_name or doc.lead }}
        </div>
        {% if doc.customer_address %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">قیمت کل (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ کل پیش‌فاکتور:</div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}
      </div>
      <div style="margin-top: 4px; font-size: 9.5pt;">
        مبلغ به حروف:
        {{ doc.grand_total | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء خریدار</td>
      <td>امضاء حسابداری</td>
      <td>امضاء صادرکننده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_salary_slip_v1():
    """Create/Update BLUE_PRINT_SALARY_SLIP_V1 for Salary Slip."""
    NAME = "BLUE_PRINT_SALARY_SLIP_V1"
    DOCTYPE = "Salary Slip"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-emp-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-emp-table th,
  .bapi-emp-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-emp-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-ed-wrapper {
    width: 100%;
    margin-top: 8px;
    font-size: 10pt;
  }

  .bapi-ed-col {
    width: 50%;
    vertical-align: top;
  }

  .bapi-table-inner {
    width: 100%;
    border-collapse: collapse;
  }

  .bapi-table-inner th,
  .bapi-table-inner td {
    border: 1px solid #dddddd;
    padding: 4px 6px;
  }

  .bapi-table-inner th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-ed-idx { width: 10%; text-align: center; }
  .bapi-ed-comp { width: 55%; text-align: right; }
  .bapi-ed-amt { width: 35%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 25%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 55%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 45%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">فیش حقوقی</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">دوره حقوق:</span>
          {% if doc.start_date and doc.end_date %}
            از {{ doc.start_date | as_jdate("YYYY/MM/DD") }}
            تا {{ doc.end_date | as_jdate("YYYY/MM/DD") }}
          {% elif doc.start_date %}
            از {{ doc.start_date | as_jdate("YYYY/MM/DD") }}
          {% elif doc.end_date %}
            تا {{ doc.end_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">تاریخ صدور:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره فیش:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-emp-table">
    <tr>
      <th>مشخصات کارمند</th>
      <th>مشخصات سازمانی</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام کارمند:</strong> {{ doc.employee_name or doc.employee }}</div>
        {% if doc.employee %}
          <div><strong>کد کارمند:</strong> {{ doc.employee }}</div>
        {% endif %}
        {% if doc.designation %}
          <div><strong>سمت:</strong> {{ doc.designation }}</div>
        {% endif %}
        {% if doc.bank_name or doc.bank_ac_no %}
          <div>
            <strong>بانک / حساب:</strong>
            {{ doc.bank_name or "" }}{% if doc.bank_ac_no %} - {{ doc.bank_ac_no }}{% endif %}
          </div>
        {% endif %}
      </td>
      <td>
        <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% if doc.branch %}
          <div><strong>شعبه:</strong> {{ doc.branch }}</div>
        {% endif %}
        {% if doc.department %}
          <div><strong>دپارتمان:</strong> {{ doc.department }}</div>
        {% endif %}
        {% if doc.payroll_frequency %}
          <div><strong>تناوب پرداخت:</strong> {{ doc.payroll_frequency }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-ed-wrapper">
    <tr>
      <td class="bapi-ed-col">
        <table class="bapi-table-inner">
          <thead>
            <tr>
              <th colspan="3">مزایا (Earnings)</th>
            </tr>
            <tr>
              <th class="bapi-ed-idx">ردیف</th>
              <th class="bapi-ed-comp">عنوان</th>
              <th class="bapi-ed-amt">مبلغ (ریال)</th>
            </tr>
          </thead>
          <tbody>
            {% if doc.earnings %}
              {% for row in doc.earnings %}
              <tr>
                <td class="bapi-ed-idx">{{ loop.index }}</td>
                <td class="bapi-ed-comp">{{ row.salary_component }}</td>
                <td class="bapi-ed-amt">{{ "{:,.0f}".format(row.amount or 0) }}</td>
              </tr>
              {% endfor %}
            {% else %}
              <tr>
                <td colspan="3" style="text-align:center; color:#777;">بدون ردیف مزایا</td>
              </tr>
            {% endif %}
          </tbody>
        </table>
      </td>
      <td class="bapi-ed-col">
        <table class="bapi-table-inner">
          <thead>
            <tr>
              <th colspan="3">کسورات (Deductions)</th>
            </tr>
            <tr>
              <th class="bapi-ed-idx">ردیف</th>
              <th class="bapi-ed-comp">عنوان</th>
              <th class="bapi-ed-amt">مبلغ (ریال)</th>
            </tr>
          </thead>
          <tbody>
            {% if doc.deductions %}
              {% for row in doc.deductions %}
              <tr>
                <td class="bapi-ed-idx">{{ loop.index }}</td>
                <td class="bapi-ed-comp">{{ row.salary_component }}</td>
                <td class="bapi-ed-amt">{{ "{:,.0f}".format(row.amount or 0) }}</td>
              </tr>
              {% endfor %}
            {% else %}
              <tr>
                <td colspan="3" style="text-align:center; color:#777;">بدون ردیف کسورات</td>
              </tr>
            {% endif %}
          </tbody>
        </table>
      </td>
    </tr>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-totals-label">جمع مزایا (ناخالص):</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.gross_pay or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع کسورات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_deduction or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">حقوق خالص:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.net_pay or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">
      مبلغ خالص قابل پرداخت:
    </div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.net_pay or 0) }}
      </div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ (doc.net_pay or 0) | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>کارمند</td>
      <td>واحد منابع انسانی</td>
      <td>مدیر مالی / حسابداری</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_sales_invoice_v1():
    """Create/Update BLUE_PRINT_SALES_INVOICE_V1 for Sales Invoice."""
    NAME = "BLUE_PRINT_SALES_INVOICE_V1"
    DOCTYPE = "Sales Invoice"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-amount-words {
    margin-top: 6px;
    font-size: 9.5pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">فاکتور فروش</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% if doc.due_date %}
        <div>
          <span class="bapi-meta-label">تاریخ سررسید:</span>
          {{ doc.due_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره فاکتور:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات خریدار</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام فروشنده:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong> {{ doc.customer_name }}</div>
        {% if doc.customer_address %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">قیمت کل (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی قابل پرداخت:</div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}
      </div>
      <div style="margin-top: 4px; font-size: 9.5pt;">
        مبلغ به حروف:
        {{ doc.grand_total | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء خریدار</td>
      <td>امضاء حسابداری</td>
      <td>امضاء صادرکننده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_sales_order_v1():
    """Create/Update BLUE_PRINT_SALES_ORDER_V1 for Sales Order."""
    NAME = "BLUE_PRINT_SALES_ORDER_V1"
    DOCTYPE = "Sales Order"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-amount-words {
    margin-top: 6px;
    font-size: 9.5pt;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">سفارش فروش</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% if doc.delivery_date %}
        <div>
          <span class="bapi-meta-label">تاریخ تحویل:</span>
          {{ doc.delivery_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره سفارش:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات فروشنده</th>
      <th>مشخصات خریدار</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام فروشنده:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong> {{ doc.customer_name or doc.customer }}</div>
        {% if doc.customer_address %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">قیمت کل (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی قابل پرداخت:</div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}
      </div>
      <div style="margin-top: 4px; font-size: 9.5pt;">
        مبلغ به حروف:
        {{ doc.grand_total | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء خریدار</td>
      <td>امضاء حسابداری</td>
      <td>امضاء صادرکننده</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_sales_quotation_v1():
    """Create/Update BLUE_PRINT_SALES_QUOTATION_V1 for Quotation."""
    NAME = "BLUE_PRINT_SALES_QUOTATION_V1"
    DOCTYPE = "Quotation"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 8px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #444;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 6%;  text-align: center; }
  .bapi-items-code  { width: 14%; text-align: center; }
  .bapi-items-desc  { width: 40%; text-align: right; }
  .bapi-items-qty   { width: 10%; text-align: center; }
  .bapi-items-uom   { width: 8%;  text-align: center; }
  .bapi-items-rate  { width: 11%; text-align: left; }
  .bapi-items-amt   { width: 11%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
    font-weight: 400;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% set q_currency = doc.currency or doc.company_currency or "IRR" %}
{% set q_total = doc.grand_total or doc.base_grand_total or doc.total or 0 %}
{% set q_abs_total = q_total %}
{% if q_abs_total < 0 %}
  {% set q_abs_total = 0 - q_abs_total %}
{% endif %}

<div class="bapi-root">

  <div class="bapi-title">پیش‌فاکتور فروش / Sales Quotation</div>
  <div class="bapi-subtitle">
    این سند شامل شرایط قیمتی و تجاری پیشنهادی برای فروش کالا/خدمات به مشتری است.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ پیش‌فاکتور:</span>
          {% if doc.transaction_date %}
            {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.valid_till %}
        <div>
          <span class="bapi-meta-label">تاریخ اعتبار تا:</span>
          {{ doc.valid_till | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره پیش‌فاکتور:</span>
          {{ doc.name }}
        </div>
        {% if doc.sales_person %}
        <div>
          <span class="bapi-meta-label">کارشناس فروش:</span>
          {{ doc.sales_person }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات خریدار / مخاطب پیش‌فاکتور</th>
      <th>مشخصات فروشنده (شرکت)</th>
    </tr>
    <tr>
      <td>
        <div>
          <strong>نام خریدار:</strong>
          {{ doc.party_name or doc.customer_name or doc.customer or doc.lead or "" }}
        </div>
        {% if doc.customer_address or doc.address_display %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
        {% endif %}
        {% if doc.contact_display %}
          <div><strong>اطلاعات تماس:</strong> {{ doc.contact_display }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.company %}
          <div><strong>شرکت فروشنده:</strong> {{ doc.company }}</div>
        {% endif %}
        {% if doc.company_address_display %}
          <div><strong>آدرس شرکت:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
        {% if doc.company_tax_id %}
          <div><strong>شناسه/کد مالیاتی:</strong> {{ doc.company_tax_id }}</div>
        {% endif %}
        {% if doc.price_list %}
          <div><strong>لیست قیمت مورد استفاده:</strong> {{ doc.price_list }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا / خدمت پیشنهادی</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-rate">نرخ واحد ({{ q_currency }})</th>
        <th class="bapi-items-amt">مبلغ ({{ q_currency }})</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-code">{{ row.item_code }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.description or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-qty">{{ row.qty }}</td>
          <td class="bapi-items-uom">{{ row.uom or "" }}</td>
          <td class="bapi-items-rate">
            {% if row.get_formatted %}
              {{ row.get_formatted("rate") }}
            {% else %}
              {{ row.rate or 0 }}
            {% endif %}
          </td>
          <td class="bapi-items-amt">
            {% if row.get_formatted %}
              {{ row.get_formatted("amount") }}
            {% else %}
              {{ row.amount or 0 }}
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#777;">
            هیچ قلمی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        {% if doc.get_formatted %}
          {{ doc.get_formatted("total") }}
        {% else %}
          {{ doc.total or doc.base_total or 0 }}
        {% endif %}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        {% if doc.get_formatted %}
          {{ doc.get_formatted("discount_amount") }}
        {% else %}
          {{ doc.discount_amount or 0 }}
        {% endif %}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        {% if doc.get_formatted %}
          {{ doc.get_formatted("total_taxes_and_charges") }}
        {% else %}
          {{ doc.total_taxes_and_charges or 0 }}
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ کل پیش‌فاکتور:</div>
    <div class="bapi-amount-box-value">
      <div>
        {% if doc.get_formatted %}
          {{ doc.get_formatted("grand_total") }}
        {% else %}
          {{ q_total }} {{ q_currency }}
        {% endif %}
      </div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ q_abs_total | money_to_words_fa(q_currency) }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">شرایط تجاری و توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.terms and doc.terms.strip() %}
        {{ doc.terms }}
      {% elif doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>کارشناس فروش</td>
      <td>تأیید مدیریت فروش / فنی</td>
      <td>تأیید خریدار</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_sales_return_v1():
    """Create/Update BLUE_PRINT_SALES_RETURN_V1 for Sales Invoice (Return / Credit Note)."""
    NAME = "BLUE_PRINT_SALES_RETURN_V1"
    DOCTYPE = "Sales Invoice"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 4px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #b00020;
    margin-bottom: 10px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-amount-words {
    margin-top: 4px;
    font-size: 9.5pt;
    font-weight: 400;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% set si_currency = doc.currency or doc.company_currency or "IRR" %}
{% set si_total = doc.grand_total or doc.base_grand_total or 0 %}
{% set si_abs_total = si_total %}
{% if si_abs_total < 0 %}
  {% set si_abs_total = 0 - si_abs_total %}
{% endif %}

<div class="bapi-root">

  <div class="bapi-title">برگشت از فروش / Sales Return</div>
  <div class="bapi-subtitle">
    این سند به‌عنوان «یادداشت اعتباری / Credit Note» ثبت شده است.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ سند برگشت:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.return_against %}
        <div>
          <span class="bapi-meta-label">ارجاع به فاکتور اصلی:</span>
          {{ doc.return_against }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره سند برگشت:</span>
          {{ doc.name }}
        </div>
        {% if doc.customer %}
        <div>
          <span class="bapi-meta-label">مشتری:</span>
          {{ doc.customer_name or doc.customer }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات خریدار (مشتری)</th>
      <th>مشخصات فروشنده (شرکت)</th>
    </tr>
    <tr>
      <td>
        {% if doc.customer %}
          <div><strong>نام خریدار:</strong> {{ doc.customer_name or doc.customer }}</div>
        {% endif %}
        {% if doc.customer_address %}
          <div><strong>آدرس:</strong> {{ doc.address_display or doc.customer_address }}</div>
        {% endif %}
        {% if doc.contact_display %}
          <div><strong>اطلاعات تماس:</strong> {{ doc.contact_display }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.company %}
          <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% endif %}
        {% if doc.company_address_display %}
          <div><strong>آدرس شرکت:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
        {% if doc.company_tax_id %}
          <div><strong>شناسه/کد مالیاتی:</strong> {{ doc.company_tax_id }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت برگشتی</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد ({{ si_currency }})</th>
        <th class="bapi-items-amt">مبلغ برگشت ({{ si_currency }})</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-qty">{{ row.qty }}</td>
          <td class="bapi-items-rate">{{ row.get_formatted("rate") }}</td>
          <td class="bapi-items-amt">{{ row.get_formatted("amount") }}</td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="5" style="text-align:center; color:#777;">
            هیچ قلمی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام برگشتی:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("total") }}</td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف برگشتی:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("discount_amount") }}</td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات تعدیلی:</td>
      <td class="bapi-totals-value">{{ doc.get_formatted("total_taxes_and_charges") }}</td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ نهایی برگشت / اعتبار صادرشده:</div>
    <div class="bapi-amount-box-value">
      <div>{{ doc.get_formatted("grand_total") }}</div>
      <div class="bapi-amount-words">
        مبلغ به حروف:
        {{ si_abs_total | money_to_words_fa(si_currency) }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">علت برگشت و توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تنظیم‌کننده سند</td>
      <td>تأیید واحد فروش / مالی</td>
      <td>تأیید مشتری (در صورت نیاز)</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_stock_entry_v1():
    """Create/Update BLUE_PRINT_STOCK_ENTRY_V1 for Stock Entry."""
    NAME = "BLUE_PRINT_STOCK_ENTRY_V1"
    DOCTYPE = "Stock Entry"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 5%; text-align: center; }
  .bapi-items-code { width: 13%; text-align: center; }
  .bapi-items-desc { width: 27%; text-align: right; }
  .bapi-items-qty { width: 8%; text-align: center; }
  .bapi-items-uom { width: 7%; text-align: center; }
  .bapi-items-swh { width: 15%; text-align: center; }
  .bapi-items-twh { width: 15%; text-align: center; }
  .bapi-items-batch { width: 10%; text-align: center; }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

{% if doc.stock_entry_type %}
  {% set se_title = doc.stock_entry_type %}
{% else %}
  {% set se_title = "ثبت سند انبار" %}
{% endif %}

<div class="bapi-root">

  <div class="bapi-title">سند انبار ({{ se_title }})</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ سند:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.purpose %}
        <div>
          <span class="bapi-meta-label">هدف:</span>
          {{ doc.purpose }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات انبار / مبدا</th>
      <th>مشخصات انبار / مقصد</th>
    </tr>
    <tr>
      <td>
        {% if doc.from_warehouse %}
          <div><strong>انبار مبدا:</strong> {{ doc.from_warehouse }}</div>
        {% else %}
          <div><strong>انبار مبدا:</strong> - </div>
        {% endif %}
      </td>
      <td>
        {% if doc.to_warehouse %}
          <div><strong>انبار مقصد:</strong> {{ doc.to_warehouse }}</div>
        {% else %}
          <div><strong>انبار مقصد:</strong> - </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-uom">واحد</th>
        <th class="bapi-items-swh">انبار مبدا</th>
        <th class="bapi-items-twh">انبار مقصد</th>
        <th class="bapi-items-batch">بچ / سریال</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.items %}
        {% for row in doc.items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-code">{{ row.item_code }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.description or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-qty">{{ row.qty or 0 }}</td>
          <td class="bapi-items-uom">{{ row.uom or "" }}</td>
          <td class="bapi-items-swh">{{ row.s_warehouse or "" }}</td>
          <td class="bapi-items-twh">{{ row.t_warehouse or "" }}</td>
          <td class="bapi-items-batch">
            {% if row.batch_no %}
              {{ row.batch_no }}
            {% elif row.serial_no %}
              {{ row.serial_no }}
            {% else %}
              -
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="8" style="text-align:center; color:#777;">
            هیچ قلمی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>تحویل‌دهنده</td>
      <td>تحویل‌گیرنده</td>
      <td>مسئول انبار / حسابداری انبار</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_stock_reconciliation_v1():
    """Create/Update BLUE_PRINT_STOCK_RECONCILIATION_V1 for Stock Reconciliation."""
    NAME = "BLUE_PRINT_STOCK_RECONCILIATION_V1"
    DOCTYPE = "Stock Reconciliation"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx   { width: 5%;  text-align: center; }
  .bapi-items-code  { width: 15%; }
  .bapi-items-desc  { width: 25%; }
  .bapi-items-ware  { width: 20%; }
  .bapi-items-cur   { width: 10%; text-align: center; }
  .bapi-items-new   { width: 10%; text-align: center; }
  .bapi-items-diff  { width: 15%; text-align: left; }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">تعدیل موجودی (Stock Reconciliation)</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {% if doc.posting_date %}
            {{ doc.posting_date | as_jdate("YYYY/MM/DD") }}
          {% else %}
            {{ doc.creation | as_jdate("YYYY/MM/DD") }}
          {% endif %}
        </div>
        {% if doc.posting_time %}
        <div>
          <span class="bapi-meta-label">ساعت:</span>
          {{ doc.posting_time }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره سند:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.purpose %}
        <div>
          <span class="bapi-meta-label">هدف:</span>
          {{ doc.purpose }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>اطلاعات سند</th>
      <th>اطلاعات حسابداری</th>
    </tr>
    <tr>
      <td>
        {% if doc.warehouse %}
        <div><strong>انبار اصلی:</strong> {{ doc.warehouse }}</div>
        {% endif %}
        {% if doc.company %}
        <div><strong>شرکت:</strong> {{ doc.company }}</div>
        {% endif %}
      </td>
      <td>
        {% if doc.expense_account %}
        <div><strong>حساب هزینه / تعدیل:</strong> {{ doc.expense_account }}</div>
        {% endif %}
        {% if doc.cost_center %}
        <div><strong>مرکز هزینه:</strong> {{ doc.cost_center }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-ware">انبار</th>
        <th class="bapi-items-cur">موجودی فعلی</th>
        <th class="bapi-items-new">موجودی جدید</th>
        <th class="bapi-items-diff">تغییر مقدار / ارزش</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.get("items") or [] %}
      {% set cur_qty = row.current_qty or 0 %}
      {% set new_qty = row.qty or 0 %}
      {% set diff_qty = new_qty - cur_qty %}
      {% set cur_amount = row.current_amount or 0 %}
      {% set new_amount = row.amount or 0 %}
      {% set diff_amount = new_amount - cur_amount %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-code">{{ row.item_code }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name or row.item_code }}
          {% if row.batch_no %}
            <br><span style="font-size: 8pt; color:#666;">بچ: {{ row.batch_no }}</span>
          {% endif %}
          {% if row.serial_no %}
            <br><span style="font-size: 8pt; color:#666;">سریال: {{ row.serial_no }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-ware">{{ row.warehouse or "" }}</td>
        <td class="bapi-items-cur">{{ cur_qty }}</td>
        <td class="bapi-items-new">{{ new_qty }}</td>
        <td class="bapi-items-diff">
          {{ diff_qty }} واحد
          <br>
          ریال {{ "{:,.0f}".format(diff_amount) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>انباردار</td>
      <td>حسابداری</td>
      <td>مدیریت</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_supplier_quotation_v1():
    """Create/Update BLUE_PRINT_SUPPLIER_QUOTATION_V1 for Supplier Quotation."""
    NAME = "BLUE_PRINT_SUPPLIER_QUOTATION_V1"
    DOCTYPE = "Supplier Quotation"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 22pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-parties-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-parties-table th,
  .bapi-parties-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-parties-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-items-idx { width: 8%; text-align: center; }
  .bapi-items-desc { width: 40%; }
  .bapi-items-qty { width: 12%; text-align: center; }
  .bapi-items-rate { width: 20%; text-align: left; }
  .bapi-items-amt { width: 20%; text-align: left; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 14px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 25%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-amount-box {
    margin-top: 10px;
    border: 2px solid #ff8c00;
    padding: 6px 10px;
    display: table;
    width: 100%;
    font-size: 11pt;
    font-weight: 600;
  }

  .bapi-amount-box-label {
    display: table-cell;
    width: 60%;
  }

  .bapi-amount-box-value {
    display: table-cell;
    width: 40%;
    text-align: left;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 32px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">پیشنهاد قیمت تأمین‌کننده</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">تاریخ:</span>
          {{ doc.transaction_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% if doc.valid_till %}
        <div>
          <span class="bapi-meta-label">تاریخ اعتبار تا:</span>
          {{ doc.valid_till | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        <div>
          <span class="bapi-meta-label">شماره پیشنهاد:</span>
          {{ doc.name }}
        </div>
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-parties-table">
    <tr>
      <th>مشخصات تأمین‌کننده</th>
      <th>مشخصات خریدار</th>
    </tr>
    <tr>
      <td>
        <div><strong>نام تأمین‌کننده:</strong> {{ doc.supplier_name or doc.supplier }}</div>
        {% if doc.supplier_address_display or doc.supplier_address %}
          <div>
            <strong>آدرس:</strong>
            {{ doc.supplier_address_display or doc.supplier_address }}
          </div>
        {% endif %}
      </td>
      <td>
        <div><strong>نام خریدار:</strong> {{ doc.company }}</div>
        {% if doc.company_address_display %}
          <div><strong>آدرس:</strong> {{ doc.company_address_display }}</div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-desc">شرح کالا / خدمت</th>
        <th class="bapi-items-qty">تعداد</th>
        <th class="bapi-items-rate">نرخ واحد (ریال)</th>
        <th class="bapi-items-amt">قیمت کل (ریال)</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td class="bapi-items-idx">{{ loop.index }}</td>
        <td class="bapi-items-desc">
          {{ row.item_name }}
          {% if row.description and row.description != row.item_name %}
            <br><span style="font-size: 8pt; color: #666;">{{ row.description }}</span>
          {% endif %}
        </td>
        <td class="bapi-items-qty">{{ row.qty | int }}</td>
        <td class="bapi-items-rate">
          {{ "{:,.0f}".format(row.rate or 0) }}
        </td>
        <td class="bapi-items-amt">
          {{ "{:,.0f}".format(row.amount or 0) }}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="bapi-totals-table">
    <tr>
      <td style="width:55%;"></td>
      <td class="bapi-totals-label">جمع مبلغ اقلام:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع تخفیف:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.discount_amount or 0) }}
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="bapi-totals-label">جمع مالیات:</td>
      <td class="bapi-totals-value">
        ریال {{ "{:,.0f}".format(doc.total_taxes_and_charges or 0) }}
      </td>
    </tr>
  </table>

  <div class="bapi-amount-box">
    <div class="bapi-amount-box-label">مبلغ کل پیشنهاد:</div>
    <div class="bapi-amount-box-value">
      <div>
        ریال {{ "{:,.0f}".format(doc.grand_total or 0) }}
      </div>
      <div style="margin-top: 4px; font-size: 9.5pt;">
        مبلغ به حروف:
        {{ doc.grand_total | money_to_words_fa("IRR") }}
      </div>
    </div>
  </div>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>نماینده تأمین‌کننده</td>
      <td>نماینده خریدار</td>
      <td>تأیید مدیریت</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_timesheet_v1():
    """
    قالب چاپ «گزارش کارت ساعت / تایم‌شیت» برای DocType = Timesheet
    - تاریخ‌ها: فقط جلالی (J1)
    """

    NAME = "BLUE_PRINT_TIMESHEET_V1"
    DOCTYPE = "Timesheet"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 8px;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 50px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 15%;
  }

  .bapi-meta-cell {
    width: 50%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    padding-top: 6px;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8.5pt;
    margin-right: 4px;
  }

  .bapi-status-draft {
    background-color: #fff3cd;
    color: #856404;
  }

  .bapi-status-submitted {
    background-color: #d4edda;
    color: #155724;
  }

  .bapi-status-cancelled {
    background-color: #f8d7da;
    color: #721c24;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-row {
    margin-bottom: 4px;
  }

  .bapi-label {
    display: inline-block;
    min-width: 100px;
    font-weight: 600;
  }

  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 4px 6px;
  }

  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-items-table tbody tr:nth-child(odd) {
    background-color: #fcfcfc;
  }

  .bapi-idx { width: 5%; text-align: center; }
  .bapi-date { width: 14%; text-align: center; }
  .bapi-time { width: 18%; text-align: center; }
  .bapi-activity { width: 20%; }
  .bapi-project { width: 20%; }
  .bapi-hours { width: 11%; text-align: center; }
  .bapi-billable { width: 12%; text-align: center; }

  .bapi-totals-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-totals-table td {
    padding: 2px 4px;
  }

  .bapi-totals-label {
    text-align: right;
    width: 30%;
  }

  .bapi-totals-value {
    text-align: left;
    width: 20%;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 28px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 20px;
  }

  .bapi-footer-line {
    margin-top: 20px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer {
    margin-top: 6px;
    font-size: 8.5pt;
    text-align: center;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">گزارش تایم‌شیت</div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره تایم‌شیت:</span>
          {{ doc.name }}
        </div>
        {% if doc.employee %}
        <div>
          <span class="bapi-meta-label">کارمند:</span>
          {{ doc.employee_name or doc.employee }}
        </div>
        {% endif %}
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.start_date and doc.end_date %}
        <div>
          <span class="bapi-meta-label">بازه زمانی:</span>
          {{ doc.start_date | as_jdate("YYYY/MM/DD") }}
          تا
          {{ doc.end_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {% set st = doc.status or "" %}
          {% if st == "Draft" %}
            <span class="bapi-status-pill bapi-status-draft">پیش‌نویس</span>
          {% elif st == "Submitted" %}
            <span class="bapi-status-pill bapi-status-submitted">ثبت‌شده</span>
          {% elif st == "Cancelled" %}
            <span class="bapi-status-pill bapi-status-cancelled">لغو شده</span>
          {% else %}
            <span class="bapi-status-pill">{{ st }}</span>
          {% endif %}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th>اطلاعات کلی</th>
      <th>جمع ساعات</th>
    </tr>
    <tr>
      <td>
        {% if doc.project %}
        <div class="bapi-row">
          <span class="bapi-label">پروژه اصلی:</span>
          <span>{{ doc.project }}</span>
        </div>
        {% endif %}
        {% if doc.department %}
        <div class="bapi-row">
          <span class="bapi-label">واحد سازمانی:</span>
          <span>{{ doc.department }}</span>
        </div>
        {% endif %}
      </td>
      <td>
        {% if doc.total_hours %}
        <div class="bapi-row">
          <span class="bapi-label">جمع کل ساعات:</span>
          <span>{{ "{:,.2f}".format(doc.total_hours) }}</span>
        </div>
        {% endif %}
        {% if doc.total_billable_hours %}
        <div class="bapi-row">
          <span class="bapi-label">جمع ساعات قابل‌صورتحساب:</span>
          <span>{{ "{:,.2f}".format(doc.total_billable_hours) }}</span>
        </div>
        {% endif %}
        {% if doc.total_billed_hours %}
        <div class="bapi-row">
          <span class="bapi-label">جمع ساعات صورتحساب شده:</span>
          <span>{{ "{:,.2f}".format(doc.total_billed_hours) }}</span>
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-idx">ردیف</th>
        <th class="bapi-date">تاریخ</th>
        <th class="bapi-time">از / تا</th>
        <th class="bapi-activity">نوع فعالیت</th>
        <th class="bapi-project">پروژه / تسک</th>
        <th class="bapi-hours">ساعات</th>
        <th class="bapi-billable">وضعیت</th>
      </tr>
    </thead>
    <tbody>
      {% set logs = doc.time_logs or [] %}
      {% if logs %}
        {% for row in logs %}
        <tr>
          <td class="bapi-idx">{{ loop.index }}</td>
          <td class="bapi-date">
            {% if row.from_time %}
              {{ row.from_time | as_jdatetime("YYYY/MM/DD") }}
            {% endif %}
          </td>
          <td class="bapi-time">
            {% if row.from_time %}
              از {{ row.from_time | as_jdatetime("YYYY/MM/DD HH:mm") }}
            {% endif %}
            {% if row.to_time %}
              <br>تا {{ row.to_time | as_jdatetime("YYYY/MM/DD HH:mm") }}
            {% endif %}
          </td>
          <td class="bapi-activity">{{ row.activity_type or "" }}</td>
          <td class="bapi-project">
            {% if row.project %}پروژه: {{ row.project }}{% endif %}
            {% if row.task %}
              <br>تسک: {{ row.task }}
            {% endif %}
          </td>
          <td class="bapi-hours">
            {{ "{:,.2f}".format(row.hours or 0) }}
          </td>
          <td class="bapi-billable">
            {% if row.billable %}
              قابل‌صورتحساب
            {% else %}
              غیرقابل‌صورتحساب
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="7" style="text-align:center; color:#888;">
            هیچ ردیف زمانی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-sign-table">
    <tr>
      <td>امضاء کارمند</td>
      <td>امضاء سرپرست</td>
      <td>امضاء واحد پروژه / مشتری</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <div class="bapi-footer">
    BlueAPI | info@example.com | Telegram: @blueapi | Instagram: @blueapi | X: @blueapi
  </div>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")

def create_blue_print_work_order_v1():
    """Create/Update BLUE_PRINT_WORK_ORDER_V1 for Work Order."""
    NAME = "BLUE_PRINT_WORK_ORDER_V1"
    DOCTYPE = "Work Order"

    HTML = """
<style>
  @font-face {
    font-family: "Vazirmatn";
    src: url("/files/Vazirmatn[wght].woff2") format("woff2");
    font-weight: 100 900;
    font-style: normal;
    font-display: swap;
  }

  .bapi-root {
    direction: rtl;
    text-align: right;
    font-family: "Vazirmatn", Tahoma, sans-serif;
    font-size: 11pt;
    color: #222;
    padding: 24px 32px;
  }

  .bapi-title {
    text-align: center;
    font-size: 20pt;
    font-weight: 700;
    margin-bottom: 10px;
  }

  .bapi-subtitle {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-bottom: 12px;
  }

  .bapi-header-table {
    width: 100%;
    margin-bottom: 4px;
    direction: ltr;
  }

  .bapi-header-table td {
    vertical-align: top;
  }

  .bapi-logo-cell {
    width: 35%;
    text-align: left;
  }

  .bapi-logo {
    height: 60px;
  }

  .bapi-logo-caption {
    margin-top: 4px;
    font-size: 10pt;
  }

  .bapi-header-spacer {
    width: 20%;
  }

  .bapi-meta-cell {
    width: 45%;
    font-size: 9pt;
    line-height: 1.6;
    text-align: right;
    direction: rtl;
    vertical-align: middle;
  }

  .bapi-meta-label {
    font-weight: 600;
    margin-left: 4px;
  }

  .bapi-orange-line {
    margin: 8px 0 16px 0;
    border-top: 3px solid #ff8c00;
  }

  .bapi-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10pt;
  }

  .bapi-info-table th,
  .bapi-info-table td {
    border: 1px solid #dddddd;
    padding: 6px 8px;
  }

  .bapi-info-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-ops-table,
  .bapi-items-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6px;
    font-size: 9.5pt;
  }

  .bapi-ops-table th,
  .bapi-ops-table td,
  .bapi-items-table th,
  .bapi-items-table td {
    border: 1px solid #dddddd;
    padding: 5px 6px;
  }

  .bapi-ops-table th,
  .bapi-items-table th {
    background-color: #fafafa;
    text-align: center;
    font-weight: 600;
  }

  .bapi-ops-idx        { width: 6%;  text-align: center; }
  .bapi-ops-op         { width: 24%; text-align: right; }
  .bapi-ops-ws         { width: 20%; text-align: right; }
  .bapi-ops-time       { width: 20%; text-align: center; }
  .bapi-ops-qty        { width: 15%; text-align: center; }
  .bapi-ops-status     { width: 15%; text-align: center; }

  .bapi-items-idx      { width: 6%;  text-align: center; }
  .bapi-items-code     { width: 16%; text-align: center; }
  .bapi-items-desc     { width: 34%; text-align: right; }
  .bapi-items-warehouse{ width: 18%; text-align: center; }
  .bapi-items-qty      { width: 13%; text-align: center; }
  .bapi-items-uom      { width: 13%; text-align: center; }

  .bapi-summary-table {
    width: 100%;
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-summary-table td {
    padding: 2px 4px;
  }

  .bapi-summary-label {
    text-align: right;
    width: 30%;
  }

  .bapi-summary-value {
    text-align: left;
    width: 25%;
  }

  .bapi-remarks-block {
    margin-top: 12px;
    font-size: 10pt;
  }

  .bapi-remarks-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .bapi-remarks-box {
    border: 1px solid #dddddd;
    min-height: 40px;
    padding: 6px 8px;
  }

  .bapi-sign-table {
    width: 100%;
    margin-top: 26px;
    font-size: 9pt;
  }

  .bapi-sign-table td {
    text-align: center;
    padding-top: 24px;
  }

  .bapi-footer-line {
    margin-top: 18px;
    border-top: 1px solid rgba(255, 140, 0, 0.6);
  }

  .bapi-footer-table {
    width: 100%;
    margin-top: 6px;
    font-size: 8.5pt;
  }

  .bapi-footer-table td {
    vertical-align: top;
  }

  .bapi-footer-right {
    text-align: right;
    width: 50%;
    padding-right: 8px;
    font-size: 9pt;
  }

  .bapi-footer-left {
    text-align: left;
    width: 50%;
    padding-left: 8px;
  }
</style>

<div class="bapi-root">

  <div class="bapi-title">دستور کار تولید / Work Order</div>
  <div class="bapi-subtitle">
    این فرم جهت دستور تولید، پیگیری عملیات و کنترل مصرف/خروج مواد از انبار استفاده می‌شود.
  </div>

  <table class="bapi-header-table">
    <tr>
      <td class="bapi-logo-cell">
        <img src="/files/blueapi-logo.png" class="bapi-logo">
        <div class="bapi-logo-caption">بلو ای‌پی‌آی BlueAPI</div>
      </td>
      <td class="bapi-header-spacer"></td>
      <td class="bapi-meta-cell">
        <div>
          <span class="bapi-meta-label">شماره دستور کار:</span>
          {{ doc.name }}
        </div>
        {% if doc.company %}
        <div>
          <span class="bapi-meta-label">شرکت:</span>
          {{ doc.company }}
        </div>
        {% endif %}
        {% if doc.status %}
        <div>
          <span class="bapi-meta-label">وضعیت:</span>
          {{ doc.status }}
        </div>
        {% endif %}
        {% if doc.planned_start_date %}
        <div>
          <span class="bapi-meta-label">تاریخ شروع برنامه‌ریزی‌شده:</span>
          {{ doc.planned_start_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
        {% if doc.planned_end_date %}
        <div>
          <span class="bapi-meta-label">تاریخ پایان برنامه‌ریزی‌شده:</span>
          {{ doc.planned_end_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <div class="bapi-orange-line"></div>

  <table class="bapi-info-table">
    <tr>
      <th style="width: 40%;">اطلاعات محصول نهایی</th>
      <th style="width: 30%;">مقصد و سفارش مرجع</th>
      <th style="width: 30%;">انبارها و تنظیمات</th>
    </tr>
    <tr>
      <td>
        <div>
          <strong>محصول تولیدی:</strong>
          {{ doc.production_item }} - {{ doc.item_name or "" }}
        </div>
        <div>
          <strong>مقدار برنامه‌ریزی‌شده:</strong>
          {{ doc.qty or 0 }} {{ doc.stock_uom or "" }}
        </div>
        {% if doc.produced_qty %}
        <div>
          <strong>مقدار تولیدشده تاکنون:</strong>
          {{ doc.produced_qty }} {{ doc.stock_uom or "" }}
        </div>
        {% endif %}
      </td>
      <td>
        {% if doc.sales_order %}
        <div>
          <strong>سفارش فروش مرجع:</strong> {{ doc.sales_order }}
        </div>
        {% endif %}
        {% if doc.project %}
        <div>
          <strong>پروژه:</strong> {{ doc.project }}
        </div>
        {% endif %}
        {% if doc.expected_delivery_date %}
        <div>
          <strong>تاریخ تحویل مورد انتظار:</strong>
          {{ doc.expected_delivery_date | as_jdate("YYYY/MM/DD") }}
        </div>
        {% endif %}
      </td>
      <td>
        {% if doc.wip_warehouse %}
        <div>
          <strong>انبار در جریان ساخت (WIP):</strong> {{ doc.wip_warehouse }}
        </div>
        {% endif %}
        {% if doc.fg_warehouse %}
        <div>
          <strong>انبار محصول نهایی:</strong> {{ doc.fg_warehouse }}
        </div>
        {% endif %}
        {% if doc.from_warehouse %}
        <div>
          <strong>انبار تأمین مواد:</strong> {{ doc.from_warehouse }}
        </div>
        {% endif %}
      </td>
    </tr>
  </table>

  <h4 style="font-size: 11pt; margin-top: 12px; margin-bottom: 4px;">
    عملیات تولید
  </h4>

  <table class="bapi-ops-table">
    <thead>
      <tr>
        <th class="bapi-ops-idx">ردیف</th>
        <th class="bapi-ops-op">عملیات</th>
        <th class="bapi-ops-ws">ایستگاه کاری</th>
        <th class="bapi-ops-time">زمان برنامه‌ریزی‌شده</th>
        <th class="bapi-ops-qty">مقدار تکمیل‌شده</th>
        <th class="bapi-ops-status">وضعیت</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.operations %}
        {% for row in doc.operations %}
        <tr>
          <td class="bapi-ops-idx">{{ loop.index }}</td>
          <td class="bapi-ops-op">
            {{ row.operation or "" }}
            {% if row.description %}
              <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-ops-ws">{{ row.workstation or "" }}</td>
          <td class="bapi-ops-time">
            {% if row.planned_start_time %}
              شروع: {{ row.planned_start_time | as_jdatetime("YYYY/MM/DD HH:mm") }}<br>
            {% endif %}
            {% if row.planned_end_time %}
              پایان: {{ row.planned_end_time | as_jdatetime("YYYY/MM/DD HH:mm") }}<br>
            {% endif %}
            {% if row.time_in_mins %}
              ({{ row.time_in_mins }} دقیقه)
            {% endif %}
          </td>
          <td class="bapi-ops-qty">
            {% if row.completed_qty %}
              {{ row.completed_qty }} {{ doc.stock_uom or "" }}
            {% else %}
              -
            {% endif %}
          </td>
          <td class="bapi-ops-status">
            {% if row.status %}
              {{ row.status }}
            {% else %}
              -
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#777;">
            هیچ عملیات تولیدی ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <h4 style="font-size: 11pt; margin-top: 14px; margin-bottom: 4px;">
    مواد اولیه مورد نیاز
  </h4>

  <table class="bapi-items-table">
    <thead>
      <tr>
        <th class="bapi-items-idx">ردیف</th>
        <th class="bapi-items-code">کد کالا</th>
        <th class="bapi-items-desc">شرح کالا</th>
        <th class="bapi-items-warehouse">انبار</th>
        <th class="bapi-items-qty">مقدار موردنیاز / مصرف</th>
        <th class="bapi-items-uom">واحد</th>
      </tr>
    </thead>
    <tbody>
      {% if doc.required_items %}
        {% for row in doc.required_items %}
        <tr>
          <td class="bapi-items-idx">{{ loop.index }}</td>
          <td class="bapi-items-code">{{ row.item_code }}</td>
          <td class="bapi-items-desc">
            {{ row.item_name or row.description or row.item_code }}
            {% if row.description and row.description != row.item_name %}
              <br><span style="font-size: 8pt; color:#666;">{{ row.description }}</span>
            {% endif %}
          </td>
          <td class="bapi-items-warehouse">{{ row.source_warehouse or row.warehouse or "" }}</td>
          <td class="bapi-items-qty">
            موردنیاز: {{ row.required_qty or 0 }}
            {% if row.consumed_qty %}
              <br>مصرف‌شده: {{ row.consumed_qty }}
            {% endif %}
          </td>
          <td class="bapi-items-uom">{{ row.uom or "" }}</td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="6" style="text-align:center; color:#777;">
            هیچ ردیف مواد اولیه ثبت نشده است.
          </td>
        </tr>
      {% endif %}
    </tbody>
  </table>

  <table class="bapi-summary-table">
    <tr>
      <td style="width:45%;"></td>
      <td class="bapi-summary-label">جمع مقدار برنامه‌ریزی‌شده:</td>
      <td class="bapi-summary-value">
        {{ doc.qty or 0 }} {{ doc.stock_uom or "" }}
      </td>
    </tr>
    {% if doc.produced_qty %}
    <tr>
      <td></td>
      <td class="bapi-summary-label">جمع مقدار تولیدشده:</td>
      <td class="bapi-summary-value">
        {{ doc.produced_qty }} {{ doc.stock_uom or "" }}
      </td>
    </tr>
    {% endif %}
    {% if doc.material_transferred_for_manufacturing %}
    <tr>
      <td></td>
      <td class="bapi-summary-label">مواد منتقل‌شده برای تولید:</td>
      <td class="bapi-summary-value">
        {{ doc.material_transferred_for_manufacturing }} {{ doc.stock_uom or "" }}
      </td>
    </tr>
    {% endif %}
  </table>

  <div class="bapi-remarks-block">
    <div class="bapi-remarks-label">توضیحات و یادداشت‌ها:</div>
    <div class="bapi-remarks-box">
      {% if doc.remarks and doc.remarks.strip() and doc.remarks.strip() != "No Remarks" %}
        {{ doc.remarks }}
      {% endif %}
    </div>
  </div>

  <table class="bapi-sign-table">
    <tr>
      <td>کارشناس برنامه‌ریزی تولید</td>
      <td>سرپرست/مدیر تولید</td>
      <td>کنترل کیفیت / انبار</td>
    </tr>
  </table>

  <div class="bapi-footer-line"></div>
  <table class="bapi-footer-table">
    <tr>
      <td class="bapi-footer-right">
        <div><strong>بلو ای‌پی‌آی BlueAPI</strong></div>
        <div>تهران، خیابان مثال، پلاک ۱۳۳</div>
        <div>تلفن: 12345678-021</div>
      </td>
      <td class="bapi-footer-left">
        Telegram: @blueapi<br>
        Instagram: @blueapi<br>
        X: @blueapi
      </td>
    </tr>
  </table>

</div>
    """.strip()

    existing = frappe.db.exists("Print Format", NAME)
    if existing:
        pf = frappe.get_doc("Print Format", existing)
        pf.doc_type = DOCTYPE
        pf.print_format_type = "Jinja"
        pf.custom_format = 1
        pf.disabled = 0
        pf.html = HTML
        pf.save()
    else:
        pf = frappe.get_doc({
            "doctype": "Print Format",
            "name": NAME,
            "doc_type": DOCTYPE,
            "print_format_type": "Jinja",
            "custom_format": 1,
            "disabled": 0,
            "html": HTML,
        })
        pf.insert(ignore_permissions=True)

    frappe.db.commit()
    print("PRINT FORMAT:", pf.name, "created/updated.")
