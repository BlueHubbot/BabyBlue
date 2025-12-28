BabyBlue – Reproducible Frappe/ERPNext Deployment

Structure:
  scripts/00-05   -> bootstrap -> bench -> site -> nginx -> ssl -> postcheck
  templates/      -> nginx & site_config templates
  artifacts/data/ -> DB dump + public/private files + app tarballs
  apps.json       -> pinned apps and branches
  .env            -> deployment variables (copy from .env.example)

Source server (you already did this):
  - Backups and app tarballs are stored under artifacts/data and committed on branch repro-v1.

Target server (fresh VPS):

  1) Clone & prepare env
     apt-get update && apt-get install -y git
     git clone -b repro-v1 https://github.com/BlueHubbot/BabyBlue.git /tmp/BabyBlue
     cd /tmp/BabyBlue
     cp .env.example .env
     nano .env
       # set:
       #   SITE=your.new.domain
       #   DOCS_SITE=docs.your.new.domain (or empty)
       #   SSL_EMAIL=your@email
       #   DB_ROOT_PASS / DB_NAME / DB_USER / DB_PASS
       #   ADMIN_PASS / ENCRYPTION_KEY

  2) Run scripts in order (as root)
     bash scripts/00-bootstrap.sh
     bash scripts/01-setup-bench.sh
     bash scripts/02-provision-site.sh
     bash scripts/03-nginx-render.sh
     bash scripts/04-issue-certs.sh
     bash scripts/05-postcheck.sh

Result:
  - New server with Frappe + ERPNext + HRMS + cal_boot
  - Restored DB and files from artifacts/data
  - Nginx + HTTPS (Let’s Encrypt) on new SITE / DOCS_SITE
BLUEHESAB — Iran Compliance Roadmap (Master Spec v2)

Last update: 2025-12-28
Target site: baba.bluehesab.ir
Repo: BlueHubbot/BabyBlue
Branches: repro-v1 (platform baseline) + nightly/baba (server sync)
Schema version (SoT): Git Tag (BH-YYYYMMDD.N)
Resume phrases:

Continue BabyBlue / STATUS

Continue BabyBlue / RELEASE-AUTO

0) Non-negotiables (اگر این‌ها سفت نباشد، محصول «قانونی» نیست)
0.1 مرز قانونی = Company (نه کاربر، نه شعبه)

تمام خروجی‌های قانونی Per-Company:

VAT / TTMS / سامانه مودیان / بیمه / مالیات حقوق / صورت‌های مالی رسمی

هر Company باید Legal Profile مستقل داشته باشد:

شناسه ملی، کد اقتصادی، شماره ثبت، کدپستی، نشانی رسمی، کد کارگاه، اطلاعات امضاکننده، حافظه مالیاتی، کلیدها/گواهی‌ها، سیاست‌های نسخه‌بندی، …

BH Settings فقط سوئیچ‌ها + پیش‌فرض‌ها؛ هیچ داده قانونی نباید آنجا باشد.

0.2 Versioned + Reproducible + Auditable برای «همه خروجی‌های قانونی»

برای هر خروجی (فایل/JSON/PDF/چاپ):

schema_version = Git Tag (مثل BH-20251228.1)

source_hash = هش ورودی‌ها (لیست اسناد + اعداد + نرخ‌ها + طرف حساب‌ها + تنظیمات موثر)

payload_hash = هش خروجی تولیدشده

generated_by / generated_at / generator_build (commit/tag)

Immutable بعد از Submit/ارسال: هر اصلاح = نسخه جدید + لینک به نسخه قبلی + دلیل تغییر

0.3 Dimensions از روز اول (برای هر سند GL-posting)

هر سندی که GL می‌زند باید اجباری:

Branch / Cost Center / Project

تفصیلی شناور واقعی Line-Level و مستقل از Customer/Supplier

Validation فارسی و سخت‌گیرانه (عدم رعایت = بلاک Submit)

0.4 UI فارسی + جلالی؛ خروجی داده‌ای استاندارد

UI و چاپ انسانی: جلالی (J1/J2) + برچسب‌های فارسی ۱۰۰٪

خروجی داده‌ای/قانونی: میلادی استاندارد (J3) + اعداد لاتین (برای آپلود سامانه‌ها)

1) وضعیت فعلی (Baseline شناخته‌شده)
1.1 GitOps / Nightly / Tagging

nightly/baba فعال و push می‌شود

Tag و VERSION و Release notes برقرار است (نمونه: BH-20251228.1)

workflow ساخت GitHub Release برای BH-* نصب شده

Roadmap داخل repro-v1 و nightly/baba نگهداری می‌شود

1.2 blue_hesab (اپ فعلی)

VAT pipeline/guard/intent/regress موجود و عملیاتی

DocTypeهای پایه در اپ وجود دارد (BH Settings, Period Lock, VAT Profile/Category, TTMS Document, E-Invoice Document, Modian Log, Insurance Export, Payroll Tax Export, Financial Statement Profile, …)

Gap بزرگ باقی‌مانده: Per-Company Legal Profile + استانداردسازی Audit Backbone + Immutability enforcement + Dimensions enforcement سراسری.

2) DNA محصول ایران (چیزی که بازار ایران بابتش پول می‌دهد)

اگر این‌ها را جدی نگیری، حتی با «قانونی بودن»، SMBها جذب نمی‌شوند:

2.1 سرعت و UX

ورود سریع (Search-first + keyboard-first)

کپی سند/فاکتور/پرداخت

ویزارد راه‌اندازی (Onboarding): سال مالی → شرکت → بانک/صندوق → کدینگ → VAT/Payroll policy

چاپ‌های آماده «همان چیزی که کاربر ایرانی انتظار دارد» (فاکتور رسمی، فیش حقوقی، دفترها)

2.2 خزانه‌داری واقعی (چک/مغایرت/تنخواه)

چرخه کامل چک (در جریان وصول/واگذاری/برگشت/وصول)

مغایرت بانکی (Import + Match + ثبت کارمزد)

تنخواه (سقف، تسویه، کنترل)

2.3 گزارش‌های مدیریتی کلاسیک

Aging بدهکاران/بستانکاران (DNA حیاتی)

گردش حساب اشخاص

فروش به تفکیک کالا/مشتری/بازاریاب/شعبه

سود روی فاکتور (Gross margin)

3) استاندارد داده/مدل (Core Data Contracts)
3.1 BH Company Legal Profile (الزامی)

ID: LEGAL-01
Per Company:

هویت: نام رسمی، نوع شخصیت، شناسه ملی، کد اقتصادی، شماره ثبت

آدرس: کدپستی ۱۰ رقمی، نشانی، تلفن/فکس

مالیات/مودیان: حافظه مالیاتی، کلیدها/گواهی‌ها، نسخه پروتکل، محیط تست/عملیاتی

بیمه: کد کارگاه، شعبه، اطلاعات کارفرما/امضا

سیاست‌ها: VAT policy، TTMS thresholds، Payroll policy year، …
Acceptance:

بدون Legal Profile → خروجی قانونی تولید نشود (بلاک)

همه DocTypeهای خروجی قانونی FK به Company + Legal Profile داشته باشند

3.2 Audit Fields (استاندارد مشترک)

ID: AUDIT-01
روی همه خروجی‌های قانونی و اسناد تولیدکننده:

schema_version

source_hash

payload_hash

generated_by

generated_at

generator_build

previous_version (اختیاری)

status (Draft/Generated/Sent/Accepted/Rejected/Cancelled)
Acceptance:

تولید خروجی بدون این فیلدها ممنوع

بعد از “Sent/Submitted” → تغییر رکورد ممنوع (Immutable)

3.3 Period Lock & Cut-off

ID: PERIOD-01

قفل دوره: مالی/مالیاتی/حقوق

Cut-off تاریخ برای گزارش‌های رسمی
Acceptance:

سند/خروجی خارج از دوره مجاز تولید نشود.

4) Financial Core — «در حد سپیدار/هلو و بالاتر»
4.1 Chart of Accounts — کدینگ ۴–۵ سطحی واقعی ایران

ID: FC-COA-01

ساختار

Group (۱–۲ رقم)

کل (۴ رقم)

معین (۶–۷ رقم)

تفصیلی شناور ۱ (اجباری)

تفصیلی شناور ۲ (اختیاری ولی توصیه‌شده)

قواعد

Account Number مستقل از نام

Posting Level: گروه/کل غیرقابل ثبت، معین قابل ثبت

Root Type: Asset/Liability/Equity/Income/Expense/COGS

Control Accounts (حساب‌های کنترلی): دریافتنی/پرداختنی/موجودی/مالیات/چک‌ها

تمپلیت چارت:

بازرگانی

خدماتی

تولیدی (فاز بعد)

نگاشت‌ها (Mapping)

ID: FC-MAP-01

Mapping حساب‌ها → ردیف‌های:

ترازنامه رسمی

سود و زیان رسمی

(فاز بعد) جریان وجوه نقد

(حداقل) نگاشت به ردیف‌های کلیدی اظهارنامه عملکرد

Acceptance:

گزارش رسمی فقط از روی Mapping تولید شود (نه جمع کور حساب‌ها)

تغییر چارت بعد از شروع سال مالی باید کنترل‌شده/نسخه‌دار باشد

4.2 Vouchers / Journal Entry

ID: FC-JE-01

انواع سند

عمومی

افتتاحیه

اختتامیه

بستن موقت

اصلاحی/معکوس

سندهای خودکار از ماژول‌ها (فروش/خرید/حقوق/استهلاک/انبار/خزانه)

کنترل‌ها

تراز Dr/Cr

ممنوعیت ثبت در دوره قفل

سند موقت/قطعی (Draft/Posted)

پیوست اجباری برای برخی انواع (قابل تنظیم)

شماره‌گذاری:

سالانه/ماهانه/سراسری

Prefix فارسی/لاتین

Per-Company (و در صورت نیاز Per-Branch)

Acceptance:

Submit بدون تراز و بدون ابعاد اجباری ممنوع

هر خط سند باید Dimensions کامل داشته باشد (طبق سیاست)

4.3 Closing / Opening

ID: FC-CLOSE-01

سند بستن حساب‌های موقت

انتقال به سود(زیان) انباشته

اختتامیه و افتتاحیه سال بعد

کنترل تغییرات پس از بستن (بلاک + نسخه اصلاحی)

4.4 گزارش‌های مالی کلاسیک (حداقل بازار ایران)

ID: FC-REP-01

دفتر روزنامه

دفتر کل

دفتر معین

دفتر تفصیلی

تراز آزمایشی ۲/۴/۶ ستونی

گردش حساب اشخاص/بانک/صندوق/تنخواه

Aging بدهکاران/بستانکاران (الزامی)

Acceptance:

UI جلالی و فارسی

Export اکسل/CSV با اعداد لاتین + تاریخ میلادی (برای ممیز/سامانه‌ها)

Drill-down تا سند و حتی ردیف

5) Treasury — خزانه‌داری (چک، تنخواه، مغایرت)
5.1 دریافت/پرداخت

ID: TR-01

Receipt / Payment Entry: نقد، کارت، حواله، واریز، …

لینک به: فاکتور/طرف حساب/سند حسابداری

صندوق/بانک/تنخواه چندگانه + سقف تنخواه + تسویه تنخواه

5.2 چک (چرخه کامل)

ID: TR-CHK-01

دریافتنی: InHand → Deposited → Cleared/Returned

پرداختنی: Issued → Paid/Cancelled

حساب واسط چک در جریان وصول

یادآوری سررسید + گزارش چک‌های سررسید شده

5.3 مغایرت بانکی

ID: TR-BR-01

Import گردش بانک

Match نیمه‌خودکار

ثبت کارمزد/اختلاف با سند خودکار

6) VAT — Mixed / Exclusive / Inclusive (ریسک قانونی)
6.1 ساختار حساب‌ها

ID: VAT-ACC-01

مالیات فروش

عوارض فروش (اگر تفکیک لازم است)

مالیات خرید

عوارض خرید

حساب‌های واسط تسویه (پرداختنی/دریافتنی)

6.2 Tax Category / Profile / Template

ID: VAT-CAT-01

مشمول ۹٪

معاف

صفر درصد

صادرات (۰٪)

(اختیاری) دسته‌های خاص

6.3 قواعد محاسبه

ID: VAT-RULE-01

مبنا: مبلغ بعد از تخفیف

Line-level

Snapshot نرخ در زمان صدور

ذخیره جزئیات محاسبه برای audit

6.4 گزارش VAT دوره‌ای + Reconciliation

ID: VAT-REP-01

فروش مشمول/معاف/صادرات

خرید مشمول/معاف

مالیات/عوارض فروش/خرید

خالص پرداختی/استردادی

Reconciliation با GL با لیست اختلاف‌ها

Acceptance:

هر اختلاف VAT report با GL باید قابل ردیابی به سند/ردیف باشد

تغییر Intent (EXCL/INCL) بعد از Submit ممنوع یا فقط با نسخه جدید

7) TTMS (ماده 169) — Generator + Validator + Audit
7.1 داده‌های لازم (Capture)

ID: TTMS-DATA-01
برای هر معامله:

نوع گزارش: فروش/خرید/قرارداد/حق‌الزحمه

نوع شخص: حقیقی/حقوقی

نوع شناسه: کد ملی/شناسه ملی/کد اقتصادی

شناسه + نام + کدپستی ۱۰ رقمی

شماره و تاریخ فاکتور

مبلغ ناخالص/تخفیف/خالص

مالیات/عوارض

وضعیت زیر حدنصاب (Flag + تجمیع)

7.2 Validator

ID: TTMS-VAL-01

طول/فرمت کدملی/شناسه ملی/کدپستی

تاریخ خارج از دوره

فاکتور بدون شماره

معاملات تکراری

زیر حدنصاب (تجمیعی/پرچم‌گذاری)

7.3 Generator/Export

ID: TTMS-EXP-01

خروجی Excel/CSV مطابق قالب قابل انتخاب (Schema-versioned)

فیلتر: فصل/سال/نوع گزارش

Attach فایل خروجی + لاگ تولید + hashها

Acceptance:

خروجی بدون Validator PASS تولید نشود

خروجی immutable بعد از Generate/Export رسمی

8) سامانه مودیان — زیرساخت داده + Payload Store + وضعیت ارسال
8.1 مدل داده

ID: MOD-DATA-01

نوع صورتحساب

نسخه/پروفایل

شناسه یکتا/شماره مالیاتی (در صورت دریافت)

اطلاعات فروشنده/خریدار کامل (Per-Company legal)

اقلام + مالیات/عوارض line-level

وضعیت ارسال: NotSent/Sent/Accepted/Rejected/NeedFix

Log درخواست/پاسخ/خطا

8.2 Payload Generator

ID: MOD-GEN-01

تولید JSON نسخه‌دار

ذخیره payload + payload_hash

تطبیق ۱۰۰٪ چاپ رسمی با payload

8.3 Integration (فاز بعد)

ID: MOD-INT-01

ارسال وب‌سرویس

retry policy + شمارنده

مدیریت کلید/گواهی Per-Company

مانیتورینگ وضعیت‌ها

Acceptance:

بدون Legal Profile و کلیدها، ارسال فعال نشود

بعد از Submit فاکتور رسمی، payload نوع/نسخه قفل شود

9) Payroll + بیمه + مالیات حقوق (خروجی «قابل ارسال»)
9.1 Payroll Policy (Per-Company, Per-Year)

ID: PAY-POL-01

معافیت‌ها، پلکان‌ها، ضرایب بیمه، قواعد مزایای مشمول/غیرمشمول

نسخه‌دار و audit-دار

9.2 موتور حقوق

ID: PAY-ENG-01

آیتم‌ها: پایه، مسکن، بن، اولاد، اضافه‌کاری، شب‌کاری، تعطیل‌کاری، مأموریت، کارانه، …

کسورات: بیمه سهم کارگر، مالیات حقوق، وام، …

اتصال به سند حسابداری هزینه حقوق با تفکیک مرکز هزینه/دپارتمان

9.3 بیمه تأمین اجتماعی (Export)

ID: PAY-INS-01

ریز لیست + خلاصه

فایل/اکسل نسخه‌دار

Attach + audit + hash

9.4 مالیات حقوق (Export)

ID: PAY-TAX-01

محاسبه پلکانی پارامتریک

خروجی اکسل/متن برای سامانه

گزارش ریز و خلاصه

10) Inventory / Sales / Purchase / POS (سبک بازار ایران + عمق ERP)
10.1 انبار و کارتکس

ID: INV-01

چندانباره

Moving Average + FIFO

کارتکس: کالا/انبار/طرف حساب/سند

رزرو/موجودی در راه/نقطه سفارش

سریال/بچ (اختیاری)

10.2 فروش

ID: SAL-01

پیش‌فاکتور، فاکتور عادی، رسمی، برگشت، حواله خروج

تخفیف ردیفی/کلی

VAT line-level (Mixed)

سقف اعتبار مشتری + هشدار سررسید

چاپ‌ها: A4 رسمی / A5 / رول POS

10.3 خرید

ID: PUR-01

سفارش خرید، رسید، فاکتور، برگشت

هزینه‌های جانبی + سرشکن روی اقلام (Landed Cost)

10.4 POS (فاز جدا)

ID: POS-01

شیفت، صندوق، گزارش صندوق

رول حرارتی

کنترل اختلاف صندوق

11) Fixed Assets — استهلاک قابل دفاع

ID: FA-01

ثبت دارایی + گروه/محل/مسئول/تاریخ‌ها/بهای تمام‌شده

استهلاک خط مستقیم (MVP) + نزولی (فاز بعد)

سند ماهانه استهلاک خودکار + ابعاد

نقل و انتقال/فروش/اسقاط + سود/زیان

دفتر دارایی + جدول استهلاک + ارزش دفتری

12) صورت‌های مالی رسمی + Notes (Template-driven)
12.1 صورت‌ها

ID: FS-01

ترازنامه با ستون سال جاری/سال قبل

سود و زیان عملکردی با ستون سال جاری/سال قبل

سود و زیان انباشته

جریان وجوه نقد (فاز دوم)

12.2 Notes

ID: FS-NOTE-01

حداقل Notes برای سرفصل‌های اصلی (قابل توسعه)

12.3 خروجی رسمی

ID: FS-OUT-01

PDF قابل امضا/مهر

Export اکسل/CSV برای تحلیل

13) Governance / Security / Permissions / Workflow
13.1 Role Model (حداقل)

ID: GOV-ROLE-01

CEO, CFO, Senior Accountant, Accountant, Sales, Warehouse, HR, Payroll, System Manager, Portal User

Scope دسترسی: Company/Branch/Cost Center

13.2 Workflowهای الزامی

ID: GOV-WF-01

PO: Draft → Unit Approve → CFO Approve

JE/Payment: Draft → Review → CFO Approve

Leave/Expense: Employee → Manager → HR/Finance

13.3 Security/Audit

ID: GOV-SEC-01

2FA برای System Manager و CFO

محدودیت IP برای صفحات حساس

Audit trail تقویت‌شده روی:

Users/Roles

Fiscal Year/Period Lock

Tax Templates/Policies

Legal Profile/Keys

14) Localization & UX — فارسی «واقعی» نه تزئینی

ID: L10N-01

همه لیبل/دکمه/پیغام خطا فارسی

جلالی سراسری در UI (CAL/blue_jdate)

انتخاب رقم فارسی/لاتین در UI (ترجیحاً)

خروجی داده‌ای: میلادی + لاتین

نام‌گذاری منو و گزارش‌ها مطابق اصطلاحات بازار ایران:

دفتر روزنامه، کل، معین، تفصیلی، تراز آزمایشی، کارتکس، …

15) GitOps / Release / Promotion Policy (اجرایی و بدون بحث)
15.1 Nightly Sync (server → repo)

منبع: /home/frappe/frappe-bench/apps/blue_hesab

مقصد: BabyBlue/artifacts/apps/blue_hesab (vendored)

برنچ: nightly/baba

Tag: BH-YYYYMMDD.N (schema_version)

15.2 Release Notes

هر Tag باید:

releases/<TAG>.md

GitHub Release از همین فایل ساخته شود.

15.3 Platform snapshot tags (repro-vX.Y)

repro-v3.5 = Golden snapshot پلتفرم (قابل نگه‌داری برای deploy تکرارپذیر)

تغییرات روزانه blue_hesab روی nightly/baba

وقتی یک نقطه پایدار شد:

Promotion کنترل‌شده به repro-v1

Tag جدید پلتفرم: repro-v3.6 (یا مشابه)

نظر قطعی: repro-v3.5 را دست نزن؛ «baseline قابل رجوع» است. همه تغییرات روزانه فقط روی nightly/baba تا زمان promotion.

16) QA / Regression Strategy (بدون تست، محصول حقوقی نیست)

ID: QA-01

مجموعه تست‌های رگرسیون برای:

VAT Mixed (sales/purchase) + intent/guard

TTMS validator + exporter

Payroll calc + insurance/tax exports

Period lock enforcement

Dimensions enforcement

“Golden dataset” کوچک برای CI (قابل ریستور)

هر Tag باید CI PASS داشته باشد

17) Phase Plan (Status Board IDs)
Phase A — Legal Boundary + Audit Backbone

LEGAL-01 ✅ (تعریف/پیاده‌سازی)

AUDIT-01 ✅ (استانداردسازی فیلدها)

IMMUT-01 ✅ (Immutable outputs)

Phase B — Dimensions Enforcement (Hard)

DIM-01 ✅ enforce برای همه GL-posting docها

Phase C — Financial Core hardening

FC-COA-01 ✅

FC-MAP-01 ✅

FC-REP-01 ✅

FC-CLOSE-01 ✅

Phase D — Treasury

TR-01, TR-CHK-01, TR-BR-01

Phase E — VAT production-grade

VAT-REP-01 + reconciliation سخت‌گیرانه

Phase F — TTMS

TTMS-VAL-01 + TTMS-EXP-01

Phase G — Modian payload store

MOD-DATA-01 + MOD-GEN-01

Phase H — Payroll exports

PAY-ENG-01 + PAY-INS-01 + PAY-TAX-01

Phase I — Inventory/Sales/Purchase/POS polish

INV-01, SAL-01, PUR-01, POS-01

Phase J — Financial Statements official layouts + notes

FS-01, FS-NOTE-01

18) Daily Workflow (برای ادامه بدون سردرگمی)
Start of session

Continue BabyBlue / STATUS

نگاه به آخرین Tag (BH-*)

مرور Daily Delta قبلی

انتخاب ۲–۳ آیتم ID برای بستن (نه بیشتر)

End of session (Daily Delta)

Done ✅ (IDها)

Progress 🟡 (IDها + ۱ خط وضعیت)

Blocked ⛔ (IDها + دلیل)

Next session (IDهای فردا)

Changelog entry (Unreleased + تاریخ‌دار)

Appendix A — Standard Output Object (برای همه خروجی‌های قانونی)

هر خروجی قانونی باید این را داشته باشد:

Meta:

schema_version, source_hash, payload_hash

generated_by, generated_at, generator_build

company, legal_profile

status + history

Attachments:

فایل خروجی + امضای فایل (hash)

Immutability:

بعد از “Sent/Submitted” فقط نسخه جدید
