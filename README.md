BLUEHESAB — Iran Compliance Master Spec (V1)

Last update: 2025-12-28
Target: baba.bluehesab.ir
Repo: BlueHubbot/BabyBlue
Branches: repro-v1 (platform baseline) + nightly/baba (server sync)
Schema Version (Source of Truth): Git Tag = BH-YYYYMMDD.N

0) Non-Negotiables (خط قرمز)
NNG-01 — مرز قانونی = Company

هر خروجی قانونی/حاکمیتی (VAT/TTMS/مودیان/بیمه/مالیات حقوق/صورت‌های مالی رسمی) فقط Per-Company.

داده‌ی قانونی هر شرکت باید در BH Company Legal Profile ذخیره شود، نه BH Settings.

هیچ Report/Export قانونی نباید از چند Company تجمیع کند (حتی اگر کاربر دسترسی داشته باشد).

NNG-02 — Versioned + Reproducible + Auditable برای تمام خروجی‌های قانونی

برای هر خروجی (فایل/JSON/چاپ/ارسال):

schema_version = همان Tag (BH-YYYYMMDD.N)

source_hash = هش ورودی‌ها (لیست اسناد + مقادیر کلیدی + نرخ‌ها + تنظیمات موثر)

payload_hash = هش خروجی تولیدشده

generated_by, generated_at, generator_build (commit/tag)

Immutable بعد از Submit/Send
اصلاح = تولید نسخه جدید + لینک به نسخه قبلی + ثبت دلیل اصلاح

NNG-03 — Dimensions از روز اول برای هر سند GL-Posting

هر سندی که GL Entry می‌سازد باید:

Branch / Cost Center / Project را داشته باشد (سیاست: Mandatory)

“تفصیلی شناور واقعی” جدا از Customer/Supplier
یعنی هر سطر سند بتواند یک/دو تفصیلی مستقل داشته باشد.

NNG-04 — UI فارسی + جلالی، خروجی داده‌ای استاندارد

UI و Print انسانی: فارسی + جلالی (J1/J2)

خروجی داده‌ای/قانونی (CSV/Excel/JSON): میلادی استاندارد (J3) + اعداد لاتین

1) GitOps / Release / Tag Policy (اجرایی)
GIT-01 — Nightly Sync

source: frappe-bench/apps/blue_hesab

destination: BabyBlue/artifacts/apps/blue_hesab (vendored، بدون gitlink)

branch: nightly/baba

GIT-02 — Tagging = Schema Version

هر Nightly موفق → Tag جدید BH-YYYYMMDD.N

فایل artifacts/apps/blue_hesab/VERSION باید دقیقاً همان Tag را نگه دارد.

GIT-03 — Release Notes الزام

هر Tag باید فایل داشته باشد: releases/<TAG>.md

GitHub Release باید body را از همین فایل بسازد.

GIT-04 — Platform Snapshot جدا از App Tag

repro-v3.5 و بعدی‌ها = Snapshot پلتفرم/استقرار

BH-* = نسخه‌ی قانونی/اسکیما/خروجی‌های BlueHesab

وقتی BH به نقطه پایدار رسید → merge کنترل‌شده به repro-v1 و بعد Tag پلتفرم (مثل repro-v3.6)

2) Financial Core — هسته حسابداری مالی (در حد سپیدار/راهکاران و بالاتر)
FIN-COA — کدینگ ۴–۵ سطحی ایرانی

الزام‌ها

Group (۱–۲ رقم)

کل (۴ رقم)

معین (۶–۷ رقم)

تفصیلی شناور ۱ (اجباری در اسناد)

تفصیلی شناور ۲ (اختیاری ولی بازار ایران شدیداً دوست دارد)

کنترل‌های ریز (واقعاً مهم)

FIN-COA-01: Rule Engine برای طول/الگو (اجازه ساخت حساب با الگوی غلط = ممنوع)

FIN-COA-02: Root Type دقیق: Asset/Liability/Equity/Income/Expense/COGS

FIN-COA-03: Posting Level (گروه/کل غیرقابل ثبت، معین قابل ثبت)

FIN-COA-04: Account Number مستقل از نام (مرتب‌سازی و گزارش رسمی)

FIN-COA-05: Template آماده COA برای:

بازرگانی

خدماتی

تولیدی (فاز بعد)

FIN-COA-06: Mapping رسمی COA ↔ ردیف‌های صورت‌های مالی (Balance Sheet/P&L/Cash Flow) + ردیف‌های اظهارنامه عملکرد

FIN-VCH — اسناد حسابداری (Vouchers)

انواع سند

سند عمومی

افتتاحیه / اختتامیه

بستن حساب‌های موقت (سود و زیان)

اصلاحی / برگشت / معکوس (Reversing)

اسناد خودکار از ماژول‌ها (فروش/خرید/حقوق/استهلاک/انبار/خزانه)

کنترل‌ها

FIN-VCH-01: تراز بودن Dr/Cr + تلورانس رُندینگ تعریف‌شده

FIN-VCH-02: ممنوعیت ثبت در دوره قفل‌شده

FIN-VCH-03: ممنوعیت تغییر سند پس از “ثبت قطعی”

FIN-VCH-04: Draft vs Posted (ثبت موقت/قطعی مثل نرم‌افزارهای ایرانی)

FIN-VCH-05: پیوست سند (PDF فاکتور/قرارداد) + Policy الزام پیوست برای برخی انواع

FIN-VCH-06: شماره‌گذاری قابل تنظیم:

سالانه/ماهانه/سراسری

Prefix فارسی/لاتین (مثل س-۱۴۰۴-۰۰۰۱۲۳)

سری جدا برای هر Company (و در صورت نیاز Branch)

FIN-FY — سال مالی / دوره‌ها / بستن حساب‌ها

FIN-FY-01: تعریف Fiscal Year + Periods (ماهانه/فصلی)

FIN-FY-02: Cut-off date برای گزارش‌های قانونی

FIN-FY-03: بستن خودکار حساب‌های موقت → انتقال به سود/زیان انباشته

FIN-FY-04: تولید افتتاحیه سال بعد از اختتامیه (با کنترل عدم تغییر پس از بستن)

FIN-RPT — گزارش‌های کلاسیک بازار ایران

دفتر روزنامه (فیلتر: دوره/نوع سند/کاربر)

دفتر کل / معین / تفصیلی

تراز آزمایشی ۲ ستونی / ۴ ستونی / ۶ ستونی

گزارش مانده حساب‌ها: اشخاص/بانک‌ها/صندوق‌ها/تنخواه

Aging بدهکاران/بستانکاران (DNA بازار ایران)

صورت‌حساب طرف حساب (Statement) با گردش و مانده

3) Treasury — خزانه‌داری (عامل اصلی پذیرش SMB در ایران)
TRE-PAY — دریافت/پرداخت

رسید دریافت / حواله پرداخت (نقد/کارت/انتقال/چک)

لینک به: طرف حساب، فاکتور، قرارداد، سند حسابداری

صندوق/بانک/تنخواه چندگانه

سقف تنخواه + تسویه تنخواه

TRE-CHK — چک (چرخه کامل)

وضعیت‌ها

دریافتنی: InHand → Deposited → Cleared / Returned

پرداختنی: Issued → Paid / Cancelled

ریزهای ضروری

بانک/شعبه/سریال/تاریخ سررسید

(اختیاری فاز بعد) صیادی

تصویر چک + پیوست

یادآوری سررسید

اثر حسابداری هر وضعیت (حساب واسط “چک در جریان وصول”)

TRE-BR — مغایرت بانکی

Import گردش بانک (CSV/Excel)

تطبیق نیمه‌اتومات (مبلغ/تاریخ/شرح)

ثبت اختلافات (کارمزد/جرائم/بهره) با سند خودکار

4) Tax & Compliance — VAT / TTMS / Modian (ریسک قانونی اصلی)
TAX-VAT — VAT (ارزش افزوده) — مدل MIXED

ساختار حساب‌ها

VAT فروش / VAT خرید (ترجیحاً جدا از عوارض اگر نیاز چاپ/گزارش دارید)

حساب‌های واسط تسویه: پرداختنی/دریافتنی

قواعد

TAX-VAT-01: محاسبه بر مبنای مبلغ بعد از تخفیف

TAX-VAT-02: Line-level (ردیف به ردیف) + ذخیره جزئیات محاسبه برای Audit

TAX-VAT-03: Snapshot نرخ در زمان صدور (تغییر نرخ سال بعد نباید گذشته را تغییر دهد)

TAX-VAT-04: فاکتور MIXED (مشمول/معاف/صفر/صادرات در یک فاکتور) با reconciliation دقیق به GL

گزارش دوره‌ای VAT

فروش مشمول/معاف/صفر/صادرات

خرید مشمول/معاف

VAT فروش و VAT خرید

خالص پرداختی/استردادی

Reconciliation با GL + گزارش اختلاف “کدام سند/کدام ردیف”

خروجی قانونی نسخه‌دار

VAT Period Export → ثبت در BH Legal Output با schema_version/source_hash/payload_hash

TAX-TTMS — معاملات فصلی (169)

Scope خروجی

فروش / خرید / قراردادها / حق‌الزحمه‌ها

Validator قبل از خروجی

کنترل کدملی/شناسه ملی/کداقتصادی/کدپستی (طول/فرمت)

زیر حدنصاب (تجمیعی/پرچم‌گذاری) + سیاست قابل تنظیم

تکراری‌ها، تاریخ خارج از دوره، فاکتور بدون شماره

Audit و Versioning

فایل خروجی Attach شود

schema_version/source_hash/payload_hash

لاگ: چه کسی/چه زمانی خروجی گرفته

TAX-MODIAN — سامانه مودیان / صورتحساب الکترونیکی

فاز ۱ (الزامی): زیرساخت داده + Payload Store + Status

نگهداری فیلدهای اجباری روی فاکتور فروش رسمی (Per-Company)

تولید Payload (JSON) مطابق نسخه مشخصات فنی (versioned)

ذخیره request/response/errors + retry counters

Lock نوع/نسخه صورتحساب بعد از Submit

فاز ۲: Integration

ارسال وب‌سرویس + مدیریت وضعیت (ارسال شده/تایید/رد/نیازمند اصلاح)

تطبیق ۱۰۰٪ چاپ رسمی با Payload ارسالی (برای بازرسی)

5) Payroll / Insurance / Payroll Tax — خروجی باید “قابل ارسال” باشد
PAY-ENG — موتور حقوق (پارامتریک Per-Year)

آیتم‌ها: پایه/مسکن/بن/اولاد/اضافه‌کاری/شب‌کاری/تعطیل‌کاری/ماموریت/کارانه/عیدی/مزایای غیرنقدی…

کسورات: بیمه سهم کارگر/مالیات حقوق/وام/بیمه تکمیلی/…

Policy per-Company per-Year (بخشنامه‌ها تغییر می‌کنند)

اتصال هزینه حقوق به سند حسابداری با تفکیک Cost Center/Branch

PAY-INS — لیست بیمه تامین اجتماعی (Export نسخه‌دار)

ریز لیست + خلاصه

خروجی Text/Excel مطابق نسخه‌های رایج (versioned schema)

Audit + hash + لاگ تولید

PAY-TAX — مالیات حقوق

موتور پلکانی + معافیت‌ها (پارامتریک)

خروجی اکسل/متن قابل استفاده برای سامانه

گزارش ریز هر فرد + خلاصه کارفرما

6) Sales / Purchase / Inventory / POS — سبک بازار ایران با عمق ERP
INV-STK — انبار و کارتکس

چندانباره

روش قیمت‌گذاری: Moving Average + FIFO

کارتکس: ورود/خروج به تفکیک کالا/انبار/طرف حساب/سند

موجودی در راه / رزرو / نقطه سفارش

(اختیاری) سریال/Batch

SAL-DOC — فروش

پیش‌فاکتور / فاکتور عادی / فاکتور رسمی / برگشت / حواله خروج

تخفیف ردیفی و کلی

VAT ردیفی (برای MIXED)

کنترل سقف اعتبار مشتری + هشدار سررسید

Print قالب‌های: A4 رسمی / A5 / رول POS

PUR-DOC — خرید

سفارش خرید / رسید انبار / فاکتور خرید / برگشت

هزینه‌های جانبی (حمل/بیمه/گمرک) + سرشکن روی اقلام (بهای تمام‌شده واقعی)

POS-OPS — POS عملیاتی

شیفت صندوق (Open/Close)

جمع‌بندی روزانه (Z Report)

روش‌های پرداخت ترکیبی

چاپ رول + شماره‌گذاری جداگانه

7) Fixed Assets — دارایی ثابت و استهلاک (قابل دفاع برای ممیز)
FA-REG — ثبت دارایی

گروه/محل استقرار/مسئول/تاریخ خرید و بهره‌برداری/بهای تمام‌شده

روش استهلاک: خط مستقیم (MVP) + نزولی (فاز بعد)

عمر مفید/نرخ

FA-DEP — استهلاک

محاسبه ماهانه/سالانه

ثبت خودکار سند استهلاک (با تفکیک Cost Center/Project)

انتقال/فروش/اسقاط + سود/زیان فروش

FA-RPT — گزارش‌ها

دفتر دارایی

جدول استهلاک

ارزش دفتری پایان دوره

8) Official Financial Statements — صورت‌های مالی رسمی + Notes

خروجی‌های اصلی: وضعیت مالی (ترازنامه)، سود و زیان، جریان وجوه نقد، تغییرات حقوق مالکانه

این‌ها باید Template + Mapping + Lock داشته باشند (نه گزارش جنریک)

Notes حداقل برای سرفصل‌های اصلی (موجودی‌ها/دارایی ثابت/وام‌ها/ذخایر/اشخاص وابسته/رویدادهای بعد از تاریخ ترازنامه/…)

(نمونه‌های منتشرشده‌ی صورت‌های مالی و یادداشت‌ها معمولاً همین ساختار را دارند: صورت‌ها + یادداشت‌های توضیحی مفصل.) 
شُماران سیستم
+1

9) Security / Roles / Workflow / Audit
SEC-ROLE — Role Model

حداقل Roleها:

CEO, CFO, حسابدار ارشد، حسابدار، فروش، انباردار، HR، حقوق و دستمزد، System Manager محدود، Portal User

کنترل‌ها:

محدودیت دسترسی به Company/Branch/Cost Center

محدودیت مشاهده اسناد حساس (حقوق)

محدودیت ثبت/تغییر در دوره‌های قفل‌شده

SEC-WF — Workflowهای الزامی

PO: Draft → تایید کارشناس → تایید مدیر واحد → تایید مالی

JE/Payment: Draft → Review ارشد → Approval CFO

Leave/Expense: کارمند → مدیر مستقیم → HR/مالی

SEC-AUD — Audit Trail تقویت‌شده

تغییرات روی: COA, Fiscal Year, Tax Rules, Legal Profiles, خروجی‌های قانونی

لاگ دقیق: چه کسی/کی/چه تغییری/از کجا

10) Localization & UX — چیزهایی که باعث “حس ایرانی” می‌شود

تقویم جلالی سراسری (Desk + Print) + export میلادی

زبان و اصطلاحات: دفتر روزنامه/کل/معین/تفصیلی/تراز آزمایشی/کارتکس/…

Wizard راه‌اندازی شبیه نرم‌افزارهای ایرانی:

تعریف شرکت + Legal Profile

تعریف سال مالی و دوره‌ها

انتخاب COA Template

بانک‌ها/صندوق‌ها/تنخواه

VAT/Tax/Payroll policy سال

11) Anti-Patterns (چیزهایی که نباید انجام شود)

نگهداری داده قانونی در BH Settings (باید Legal Profile باشد)

خروجی قانونی بدون schema_version/source_hash/payload_hash

اجازه‌ی ویرایش خروجی بعد از Submit/Send

Dimensions اختیاری برای اسناد GL-Posting (باید Mandatory باشد)

اتکا به Customer/Supplier به‌عنوان تفصیلی (تفصیلی شناور باید مستقل باشد)

12) Roadmap اجرایی (فازبندی)
Phase A — Legal Boundary + Output Audit Backbone

Deliverables:

BH Company Legal Profile (Per-Company)

BH Legal Output (Generic) + Audit Fields + Immutable rules

Adapter برای VAT/TTMS/Modian/Insurance/PayrollTax

Phase B — Dimensions Enforcement (Hard)

Deliverables:

تعریف Dimensions استاندارد + اجبار روی تمام GL-Posting docs

پیام‌های خطا فارسی و دقیق

Phase C — VAT Production-Grade + Period Reconciliation

Deliverables:

Snapshot نرخ/قواعد

VAT Period Output نسخه‌دار + GL reconciliation دقیق

Phase D — TTMS Generator + Validator + Export schema versions

Deliverables:

TTMS خروجی نسخه‌دار + validator کامل + audit

Phase E — Modian Data Backbone + Payload Store + Status

Deliverables:

Payload generator نسخه‌دار + request/response store + locking rules

Phase F — Payroll/Insurance/PayrollTax Exports نسخه‌دار

Deliverables:

policy per-company/year + exports + audit

13) Acceptance Tests (تعریف Done واقعی)

هر خروجی قانونی: record در BH Legal Output + hashها + immutable

VAT/TTMS/Modian/Insurance/PayrollTax: قابلیت تولید دوباره همان خروجی با همان schema_version و همان source_hash

هر سند GL-Posting بدون Dimensions → block با خطای فارسی

گزارش‌های اصلی: Journal/Ledger/TrialBalance/AR-AP Aging در UI جلالی + خروجی داده‌ای میلادی
