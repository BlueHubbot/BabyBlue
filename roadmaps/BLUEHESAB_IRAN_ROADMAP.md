# BLUEHESAB — Iran Compliance Roadmap (Master)
Last update: 2025-12-28  
Target site: baba.bluehesab.ir  
Repo: BlueHubbot/BabyBlue  
Branches: repro-v1 (platform baseline), nightly/baba (server sync)  
Schema version source of truth: Git Tag (BH-YYYYMMDD.N)

---

## 0) Non-negotiables (اگر این‌ها سفت نباشد، محصول «قانونی» نیست)
### 0.1 مرز قانونی = Company
- هر خروجی قانونی (VAT/TTMS/مودیان/بیمه/مالیات حقوق/صورت‌های رسمی) **Per-Company**.
- هر Company باید **Legal Profile مستقل** داشته باشد (اقتصادی/شناسه ملی/کدپستی/کارگاه/حافظه مالیاتی/کلیدها/…).
- BH Settings فقط سوئیچ‌ها و پیش‌فرض‌ها؛ داده‌های قانونی نباید آنجا باشد.

### 0.2 Versioned + Reproducible + Auditable (برای همه خروجی‌های قانونی)
برای هر خروجی:
- schema_version = Git Tag (BH-YYYYMMDD.N)
- source_hash = هش ورودی‌ها (اسناد/مبالغ/نرخ‌ها/طرف حساب‌ها/…)
- payload_hash = هش خروجی
- generated_by / generated_at / generator_build
- Immutable بعد از Submit/ارسال (هر اصلاح = نسخه جدید با لینک به نسخه قبلی)

### 0.3 Dimensions از روز اول (برای هر سند GL-posting)
- Branch / Cost Center / Project
- تفصیلی شناور واقعی جدا از Customer/Supplier (سطر-به-سطر)

### 0.4 UI فارسی + جلالی، خروجی داده‌ای استاندارد
- UI و Print انسانی: جلالی (J1/J2)
- خروجی داده‌ای/قانونی: میلادی استاندارد (J3) + اعداد لاتین

---

## 1) GitOps / Tagging Policy (اجرایی)
### 1.1 Nightly sync (server → repo)
- منبع: /home/frappe/frappe-bench/apps/blue_hesab
- مقصد: BabyBlue/artifacts/apps/blue_hesab (vendored, بدون .git)
- برنچ: nightly/baba
- Tag: BH-YYYYMMDD.N (schema_version)

### 1.2 Release Notes
- هر Tag باید فایل داشته باشد:
  - releases/<TAG>.md
- GitHub Release باید از روی همین فایل ساخته شود.

### 1.3 Platform snapshot (repro tags)
- repro-v3.5 یک «Golden snapshot» برای استقرار تکرارپذیر است.
- تغییرات روزانه blue_hesab روی nightly/baba می‌آید.
- وقتی یک نقطه پایدار رسیدیم: merge کنترل‌شده به repro-v1 و Tag جدید مثل repro-v3.6.

---

## 2) Current State (as of BH-20251228.1)
✅ blue_hesab vendored داخل BabyBlue  
✅ nightly/baba + tagging + release notes + VERSION file  
✅ VAT Mixed pipeline + guard/intent/regress (طبق وضعیت فعلی سرور)

---

## 3) Roadmap — فازها (خلاصه اجرایی)
### Phase A — Legal Boundary & Output Audit Backbone
- افزودن DocType: BH Company Legal Profile (Per Company)
- استانداردسازی فیلدهای audit در تمام خروجی‌ها:
  schema_version, source_hash, payload_hash, generated_by/at/build
- Enforcement: immutable after submit/send

### Phase B — Dimensions Enforcement (Hard)
- تعریف/اجبار Branch/Cost Center/Project برای تمام GL-posting docها
- تفصیلی شناور واقعی (line-level) + validation فارسی

### Phase C — VAT Production-grade (Mixed) + Period Report
- Snapshot نرخ در زمان صدور
- VAT period report + reconciliation با GL
- تثبیت UX قالب‌ها (EXCL/INCL) با guard کامل

### Phase D — TTMS (169) Generator + Validator + Audit
- generator دوره‌ای (فصل/سال)
- validator (شناسه‌ها/کدپستی/حدنصاب/تکراری/خارج از دوره)
- خروجی نسخه‌دار + attach + audit

### Phase E — Modian (E-Invoice) Data + Payload Store + Status
- نگهداری داده اجباری
- تولید JSON نسخه مشخصات فنی
- request/response/errors + retry counters
- قفل شدن نسخه/نوع صورتحساب بعد submit

### Phase F — Payroll / Insurance / Payroll Tax (Exportable)
- policy per-company per-year
- خروجی نسخه‌دار + audit + hash
- اتصال به سند حسابداری با تفکیک cost center

---

## 4) Daily Workflow (برای ادامه بدون سردرگمی)
### Start of session
- "Continue BabyBlue / STATUS"
- بررسی آخرین Tag: BH-*
- بررسی diff سرور → repo (اگر لازم)

### End of session (Daily Delta)
- Done (✅ با IDها)
- Progress (🟡 با ۱ خط وضعیت)
- Blocked (⛔ با دلیل)
- Next session (لیست کار فردا)
- Changelog entry

