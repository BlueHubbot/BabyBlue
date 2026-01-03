# BlueHesab Iran Roadmap (Source of Truth)

**Non-negotiables (Hard Rules)**
- مرز قانونی = **Company** (VAT/TTMS/مودیان/بیمه/مالیات حقوق همه Per-Company)
- خروجی‌های قانونی: **versioned + reproducible + auditable** (schema_version + payload hash + generated_by/at) و **immutable after submit**
- Dimensions از روز اول روی هر سند GL (Branch/Cost Center/Project/تفصیلی شناور)
- UI کاملاً فارسی + تاریخ/نمایش جلالی، ولی Export/Data استاندارد (Gregorian)

**Current**
- Latest tag: BH-TEST-20251228.0343
- Date: 2026-01-03

## Phases A..I + Definition of Done (DoD)

### A) Legal Boundary & Audit Core
**DoD:** Company Legal Profile، جدول/مدل خروجی قانونی، schema_version، هش payload، قفل immutability، تست tamper، لاگ و trace id.

### B) Dimensions (Day-1 Enforcement)
**DoD:** طراحی ابعاد (Branch/CC/Project/تفصیلی)، policy enforcement روی همه GL docs، defaulting، validation، گزارش تفکیکی، تست‌ها.

### C) VAT Engine (Mixed + Intent + Period Lock)
**DoD:** Mixed VAT عملیاتی (SI/PI)، Intent↔Template guard، period lock، item_wise_tax_detail صحیح، GL صحیح، ریگرسیون CI.

### D) TTMS Exports
**DoD:** مدل TTMS per-Company، خروجی نسخه‌دار، mapping، export pipeline، ریگرسیون.

### E) Modian Payload/Integration
**DoD:** payload نسخه‌دار + امضا/کلید، صف/Retry، audit trail، تست cancel/amend/issue.

### F) Payroll Legal Outputs (Tax/Insurance)
**DoD:** خروجی‌های حقوق/بیمه نسخه‌دار، policy per-Company، قفل بعد از submit، تست‌ها.

### G) Treasury (Cheques/Bank/Settlements)
**DoD:** اسناد خزانه GL-safe + dimensions، خروجی‌های قانونی مرتبط، گزارش‌ها.

### H) Fixed Assets + Financial Statements
**DoD:** صورت‌های مالی قانونی per-Company، خروجی نسخه‌دار، کنترل دوره‌ها، تست‌ها.

### I) Hardening (GitOps/CI/Docs)
**DoD:** nightly sync، tagging برابر schema_version، ریگرسیون کامل، CHANGELOG منظم، مستندات تیم تحلیل/فنی.

➡️ نسخهٔ کامل/قابل‌اجرا: `roadmaps/BLUEHESAB_IRAN_ROADMAP.md`
