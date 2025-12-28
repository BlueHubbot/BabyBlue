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


# BLUEHESAB — Iran Compliance Master Roadmap & PRD (MASTER)
Last update: 2025-12-28  
Target: baba.bluehesab.ir  
Repo: BlueHubbot/BabyBlue  
Branches: repro-v1 (platform baseline), nightly/baba (server sync)  
Schema source of truth: Git Tag (BH-YYYYMMDD.N)  
Doc scope: Financial Core + Tax/VAT/TTMS/Modian + Payroll/Insurance/Payroll Tax + Inventory/Sales/Purchase/POS + Fixed Assets + Official Statements + Governance

---

## 0) Non-negotiables (اگر این‌ها سفت نباشد، محصول “قانونی” نیست)

### 0.1 مرز قانونی = Company
- تمام خروجی‌های قانونی (VAT/TTMS/مودیان/بیمه/مالیات حقوق/صورت‌های رسمی) **Per-Company**.
- هر Company باید **Legal Profile مستقل** داشته باشد (اقتصادی/شناسه ملی/کدپستی/کارگاه/حافظه مالیاتی/کلیدها/…).
- BH Settings فقط سوئیچ/پیش‌فرض‌ها؛ «داده قانونی» در Legal Profile و Schema Packs ذخیره شود.

### 0.2 Versioned + Reproducible + Auditable (برای همه خروجی‌های قانونی)
برای هر خروجی (فایل/JSON/Excel/PDF):
- schema_version = Git Tag (BH-YYYYMMDD.N)
- schema_pack_id = شناسه بسته‌ی قالب/اسکیما (مثلاً MODIAN_vX_Y, TTMS_vZ, INSURANCE_vN)
- source_hash = هش ورودی‌ها (لیست اسناد + مقادیر + نرخ‌ها + طرف حساب‌ها + پارامترها)
- payload_hash = هش خروجی تولیدشده
- generated_by / generated_at / generator_build (commit/tag)
- Immutable بعد از Submit/ارسال/قفل (هر اصلاح = نسخه جدید با لینک به نسخه قبلی)

### 0.3 Dimensions از روز اول (برای هر سند GL-posting)
- Branch / Cost Center / Project اجباری (Policy قابل تنظیم، اما enforcement باید سخت باشد)
- تفصیلی شناور واقعی (Line-level) جدا از Customer/Supplier
- خروجی گزارش‌ها باید بتواند روی هر Dimension فیلتر/گروه‌بندی بدهد.

### 0.4 UI فارسی + جلالی، خروجی داده‌ای استاندارد
- UI و Print انسانی: فارسی + جلالی (J1/J2)
- خروجی داده‌ای/قانونی: میلادی استاندارد (J3) + اعداد لاتین (برای آپلود سامانه‌ها)

---

## 1) GitOps / Release Policy (اجرایی و غیرقابل مذاکره)

### 1.1 Nightly sync (server → repo)
- Source: bench/apps/blue_hesab
- Destination: BabyBlue/artifacts/apps/blue_hesab (vendored, بدون gitlink)
- Branch: nightly/baba
- VERSION file: artifacts/apps/blue_hesab/VERSION = BH-YYYYMMDD.N
- Release notes: releases/<TAG>.md
- Git Tag: BH-YYYYMMDD.N (schema_version)

### 1.2 Promotion model (خیلی مهم)
- nightly/baba = جریان تغییرات سرور (واقعی/روزانه)
- repro-v1 = baseline پایدار (برای استقرار/تکرارپذیری)
- Promotion به repro-v1 فقط وقتی انجام شود که:
  - regression suite PASS
  - خروجی‌های قانونی موردنظر “immutable + auditable” شده باشند
  - سپس Tag platform (مثل repro-v3.6) زده شود

### 1.3 Golden snapshot (مثل repro-v3.5)
- repro-v3.5 را نگه دار؛ آن “پلتفرم” است.
- BH-* Tagها “قانون/اسکیما/خروجی” هستند، نه پلتفرم.
- قاطی‌شان نکن. این تمایز بعداً نجاتت می‌دهد.

---

## 2) System Architecture (تقسیم‌کار درست)

### 2.1 Core Layers
- L0: Platform (Frappe/ERPNext/HRMS + cal_boot + blue_jdate)
- L1: BlueHesab Core (Accounting/Tax/Payroll/Inventory/FixedAssets)
- L2: Legal Outputs (VAT/TTMS/Modian/Insurance/PayrollTax/Official FS) = “Immutable Artifacts”
- L3: Integrations (API, export packs, later: submission)

### 2.2 “Schema Packs” (کلید موفقیت)
هر سامانه/قالب رسمی باید یک Schema Pack داشته باشد:
- pack_id, pack_version, authority, effective_from/to
- template file(s) + validation rules
- mapping definitions (field mapping)
- test vectors (نمونه ورودی/خروجی)
این Packها باید در repo ذخیره شوند تا خروجی‌ها reproducible شوند.

---

## 3) Data Model (DocTypes و فیلدهای حداقلی)

### 3.1 BH Company Legal Profile (NEW — mandatory)
Per Company:
- identity: national_id, economic_code, registration_no, postal_code(10), address, phone
- VAT: vat_registration_no (if applicable)
- TTMS: default_person_type, default_id_type
- Insurance: workshop_code, insurance_branch, employer_id
- Modian: tax_memory_id, certificate/public_key refs, issuer info
- policy: default_calendar_mode (UI), default_output_calendar (J3 for legal)
- audit: created_by/at, updated_by/at

### 3.2 Period & Locks
- BH Fiscal Year + BH Period (ماه/فصل)
- BH Period Lock:
  - lock_type: VAT_CLOSE / TTMS_CLOSE / PAYROLL_CLOSE / YEAR_CLOSE
  - locked_until
  - locked_by/at
  - rationale + attachment

### 3.3 Legal Output Base Fields (برای همه خروجی‌ها)
برای DocTypeهای خروجی:
- company
- period / from_date / to_date
- schema_version (BH tag)
- schema_pack_id
- source_hash
- payload_hash
- generated_by / generated_at / generator_build
- status: Draft/Generated/Sent/Accepted/Rejected/Cancelled
- immutable_after: Generated or Sent (policy)
- attachments: output file(s), logs

---

## 4) Financial Core — در حد سپیدار/راهکاران + بهتر

### FIN-01 Chart of Accounts (۴–۵ سطح واقعی ایرانی)
**Goal:** کدینگ استاندارد ایرانی + کنترل‌ها + Templateها  
Must have:
- Group (۱–۲ رقم) / کل (۴) / معین (۶–۷)
- تفصیلی شناور 1 و 2 (اختیاری ولی strongly recommended)
- Posting-level enforcement: گروه/کل non-posting، معین posting
- Rule engine برای طول/الگو + جلوگیری از کد تکراری/غلط
- Templates:
  - بازرگانی
  - خدماتی
  - (تولیدی فاز بعد)
- Mapping table:
  - حساب‌ها → ردیف‌های ترازنامه/سودوزیان/اظهارنامه عملکرد

Acceptance:
- ایجاد/ویرایش کد با طول غلط غیرممکن
- گزارش‌ها بر اساس Root Type درست گروه‌بندی شوند

### FIN-02 Vouchers / Journal (DNA نرم‌افزارهای ایرانی)
Must have:
- انواع سند: عمومی، افتتاحیه، اختتامیه، بستن موقت، اصلاحی/معکوس
- شماره‌گذاری قابل تنظیم: سالانه/ماهانه/سراسری + Prefix فارسی/لاتین
- Draft vs Posted (ثبت موقت/قطعی)
- پیوست اجباری برای برخی نوع سندها
- line-level dimensions + tafsili
- کنترل‌های سخت:
  - تراز Dr/Cr (تلورانس رُندینگ)
  - ممنوعیت دوره قفل‌شده
  - هشدار اختلاف تاریخ سند با دوره مالی

### FIN-03 Closing / Opening Automation
- بستن حساب‌های موقت → انتقال به سود(زیان) انباشته
- سند اختتامیه + افتتاحیه سال بعد
- Cut-off dates + قفل سال بعد از closing

### FIN-04 Core Reports (حداقل بازار ایران)
- دفتر روزنامه / کل / معین / تفصیلی
- تراز آزمایشی ۲/۴/۶ ستونی
- مانده اشخاص/بانک/صندوق/تنخواه
- Aging بدهکاران/بستانکاران (مهم و غیرقابل حذف)
- خروجی Excel با اعداد لاتین + تاریخ میلادی (اختیاری در export)

---

## 5) Treasury (خزانه‌داری) — عامل فروش واقعی در SMB ایران

### TRE-01 Receipt/Payment + Petty Cash
- صندوق/بانک/تنخواه چندگانه
- سقف تنخواه + تسویه تنخواه
- لینک به فاکتور/قرارداد/سند حسابداری

### TRE-02 Cheque Lifecycle (کامل)
States:
- دریافتنی: InHand → Deposited → Cleared / Returned
- پرداختنی: Issued → Paid / Cancelled
Fields:
- سررسید، بانک/شعبه، شماره صیادی(در صورت پیاده‌سازی)، تصویر چک
Accounting:
- حساب واسط چک در جریان وصول + اثر هر وضعیت

### TRE-03 Bank Reconciliation
- Import گردش بانک (CSV/Excel)
- تطبیق نیمه‌اتومات
- ثبت اختلافات (کارمزد/جرائم/بهره) با سند خودکار

---

## 6) VAT (MIXED) — Production-grade + Reconciliation
> VAT باید line-level باشد و snapshot نرخ/قواعد در زمان صدور را نگه دارد.

### VAT-01 Accounts & Templates
- حساب‌های مجزا (فروش/خرید) + حساب‌های واسط تسویه
- Tax Categories: STD_9 / ZERO / EXEMPT / EXPORT_0 (+ future)
- چاپ فاکتور رسمی: مالیات و عوارض جدا (اگر policy گفت)

### VAT-02 Calculation Rules (Line-level)
- محاسبه روی مبلغ بعد از تخفیف
- ذخیره جزئیات محاسبه برای audit (item-wise detail)
- Inclusive/Exclusive intent lock (UI + server validation)

### VAT-03 Period VAT Report + GL Reconciliation
- فروش: مشمول/معاف/صفر/صادرات
- خرید: مشمول/معاف
- VAT فروش/خرید + خالص پرداختی/استردادی
- Reconciliation:
  - اختلاف؟ دقیقاً کدام سند/ردیف

### VAT-04 Legal Output Artifact
- تولید خروجی VAT دوره‌ای به عنوان DocType immutable
- schema_pack_id = VAT_RETURN_vX
- attachment: فایل خروجی + گزارش reconcile

---

## 7) TTMS (ماده 169) — Generator + Validator + Audit
> TTMS در عمل قالب/نسخه‌های مختلف دارد؛ باید schema_pack نسخه‌مند داشته باشد. 

### TTMS-01 Data Capture (حداقل فیلدهای لازم)
Per transaction:
- نوع گزارش: خرید/فروش/قرارداد/حق‌الزحمه
- نوع شخص: حقیقی/حقوقی
- نوع شناسه: کدملی/شناسه ملی/کداقتصادی
- شناسه طرف + نام + کدپستی(۱۰ رقم) + شماره ثبت (در صورت نیاز)
- شماره/تاریخ فاکتور
- مبلغ ناخالص/تخفیف/خالص + مالیات/عوارض
- زیر حد نصاب: flag + aggregation policy

### TTMS-02 Validator (قبل از خروجی)
- کنترل طول/فرمت کدملی/شناسه ملی/کدپستی
- فاکتور بدون شماره/تاریخ
- تاریخ خارج از دوره
- زیرحدنصاب: تجمیع/پرچم‌گذاری طبق policy
- duplicate detection + fix suggestions

### TTMS-03 Generator (Excel/CSV)
- انتخاب دوره (فصل/سال)
- خروجی مطابق schema_pack_id (TTMS_vX)
- audit: generated_by/at/build + hash

### TTMS-04 Immutable Output DocType
- ذخیره خروجی به عنوان artifact
- امکان regenerate فقط با نسخه جدید (immutable rule)

---

## 8) Modian (E-Invoice) — Data Backbone + Payload Store + Status
> الزام قانونی/حاکمیتی روشن است و تغییرات نسخه‌ای دارد.   
> فعلاً “ارسال” می‌تواند فاز بعد باشد، اما backbone داده باید همین الان کامل باشد.

### MOD-01 Mandatory Data Model
Per Sales Invoice (official):
- نوع صورتحساب + نسخه
- اطلاعات فروشنده (از Legal Profile)
- اطلاعات خریدار (identity کامل)
- اقلام: کد/شرح/مقدار/واحد/مبلغ/تخفیف/مالیات/عوارض line-level
- identifiers: unique_tax_id (if provided), internal sequence, fiscal memory refs
- status: Not Sent / Sent / Accepted / Rejected + error payload

### MOD-02 Payload Generator (JSON)
- تولید JSON مطابق schema_pack_id = MODIAN_EINV_vX
- payload_hash ذخیره شود
- request/response log storage (حتی اگر ارسال manual باشد)

### MOD-03 Immutability & Locking
- بعد از Submit: نوع/نسخه صورتحساب و فیلدهای کلیدی قفل شوند
- اصلاح = سند اصلاحی/برگشت + نسخه جدید

---

## 9) Payroll + Insurance + Payroll Tax (قابل دفاع و قابل ارسال)

### PAY-01 Payroll Policy (Per Company, Per Year)
- جداول معافیت/پلکان مالیات حقوق نسخه‌مند
- ضرایب بیمه نسخه‌مند
- اجزای حقوق رایج: پایه/مسکن/بن/اولاد/اضافه‌کار/شب‌کار/تعطیل‌کار/مأموریت/کارانه/عیدی…
- کسورات: بیمه کارگر، مالیات، وام، بیمه تکمیلی، ...

### PAY-02 Accounting Link
- سند هزینه حقوق باید:
  - به تفکیک cost center/department
  - قابل reconcile با لیست حقوق باشد

### INS-01 Social Security List Exports
- تولید ریز لیست + خلاصه
- schema_pack_id = INSURANCE_LIST_vN (نسخه‌مند)
- خروجی‌ها باید با نرم‌افزار/فرمت‌های رسمی همخوان باشند. :contentReference[oaicite:6]{index=6}
- audit + hash + immutable

### TAXPAY-01 Payroll Tax Exports
- محاسبه پلکانی پارامتریک
- خروجی ماهانه + ریز هر فرد
- schema_pack_id = PAYROLL_TAX_vY

---

## 10) Inventory / Sales / Purchase / POS — سبک بازار ایران، ولی تمیز و ERP-grade

### INV-01 Stock & Kardex
- چند انبار
- Moving Average + FIFO
- کارتکس کالا (ورود/خروج/سند/طرف حساب)
- موجودی در راه + رزرو + نقطه سفارش
- سریال/بچ (optional)

### SAL-01 Sales Docs
- پیش‌فاکتور / فاکتور عادی / فاکتور رسمی / برگشت / حواله خروج
- تخفیف ردیفی و کلی
- VAT ردیفی (برای MIXED)
- کنترل سقف اعتبار + هشدار سررسید
- Print Formats:
  - A4 رسمی (الگوی ایرانی)
  - A5
  - رول POS

### PUR-01 Purchase Docs
- سفارش خرید / رسید / فاکتور خرید / برگشت
- هزینه‌های جانبی (حمل/بیمه/گمرک) + توزیع روی اقلام (Landed Cost)

---

## 11) Fixed Assets (دارایی ثابت) — قابل دفاع برای ممیز

### FA-01 Asset Register
- گروه/محل/مسئول/تاریخ خرید/بهره‌برداری/بهای تمام‌شده
- روش استهلاک: خط مستقیم (MVP) + نزولی (فاز بعد)
- عمر مفید/نرخ + policy نسخه‌مند

### FA-02 Depreciation Engine
- محاسبه ماهانه/سالانه
- سند استهلاک خودکار (با تفکیک مرکز هزینه/پروژه)
- عملیات: انتقال/فروش/اسقاط + سود/زیان

### FA-03 Reports
- دفتر دارایی
- جدول استهلاک
- ارزش دفتری پایان دوره

---

## 12) Official Financial Statements (Layout سازمان حسابرسی) + Notes
> خروجی “جنریک” کافی نیست؛ باید Template + Mapping + Lock داشته باشد. :contentReference[oaicite:7]{index=7}

### FS-01 Statements
- ترازنامه (سال جاری/قبل)
- سود و زیان عملکردی (سال جاری/قبل)
- سود و زیان انباشته
- جریان وجوه نقد (فاز ۲، ولی طراحی از ابتدا)

### FS-02 Notes (حداقل)
- موجودی‌ها، دارایی ثابت، وام‌ها، ذخایر، حقوق صاحبان سهام،
  رویدادهای بعد از تاریخ ترازنامه، اشخاص وابسته…

### FS-03 Mapping to Performance Tax Return
- نگاشت حساب‌ها → ردیف‌های اظهارنامه عملکرد (حداقل شرکت‌های رایج)

---

## 13) Governance / Security / Workflow / Audit

### GOV-01 Role Model (حداقل)
- CEO, CFO, Senior Accountant, Accountant, Sales, Storekeeper, HR, Payroll, SysMgr, SelfService
- Access کنترل‌شده بر اساس Company/Branch/CostCenter

### GOV-02 Workflows (نمونه‌های الزامی)
- PO: Draft → Review → Approve
- Journal/Payment: Draft → Review → Approval
- Leave/Expense: Employee → Manager → HR/Finance

### GOV-03 Audit & Security
- 2FA برای SysMgr و CFO
- IP restriction برای ماژول‌های حساس (optional)
- Audit Trail تقویت‌شده برای:
  - Role/Permission
  - CoA changes
  - Fiscal year/locks
  - Tax templates / schema packs

---

## 14) Execution Plan (فازها + Definition of Done)

### Phase A (Legal Boundary + Audit Backbone)
DoD:
- BH Company Legal Profile live
- همه خروجی‌های قانونی دارای audit fields + immutable enforcement
- schema_pack folder structure in repo

### Phase B (Dimensions Enforcement)
DoD:
- هر سند GL-posting بدون dimensions fail شود (پیام فارسی)
- گزارش‌ها dimension-aware

### Phase C (VAT Production-grade)
DoD:
- VAT Mixed end-to-end + period report + reconcile
- regression suite PASS + tag promotion-ready

### Phase D (TTMS)
DoD:
- Generator + Validator + immutable output docs
- export packs نسخه‌مند

### Phase E (Modian backbone)
DoD:
- data completeness + payload generator + status/logs
- آماده برای فاز ارسال

### Phase F (Payroll/Insurance/PayrollTax)
DoD:
- policy per-year per-company + exports نسخه‌مند + audit

### Phase G (Official FS)
DoD:
- templates locked + mapping stable + export artifacts

---

## 15) Daily Workflow (برای ادامه بدون سردرگمی)
Start:
- "Continue BabyBlue / STATUS"
- آخرین BH tag + آخرین nightly sync + وضعیت CI
End (Daily Delta):
- Done ✅ (IDها)
- Progress 🟡 (IDها + ۱ خط)
- Blocked ⛔ (دلیل)
- Next session (لیست فردا)
- Changelog entry

---


بعد از “Sent/Submitted” فقط نسخه جدید
