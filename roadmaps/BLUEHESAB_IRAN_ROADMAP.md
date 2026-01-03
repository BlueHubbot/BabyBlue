# BLUEHESAB_IRAN_ROADMAP (Official)

این فایل «نقشه‌راه رسمی» تیم تحلیل/فنی است و در کنار ROADMAP.md نگه‌داری می‌شود.

## اصول غیرقابل مذاکره
1) Company مرز قانونی
2) خروجی‌های قانونی: versioned + reproducible + auditable + immutable after submit
3) Dimensions از روز اول روی هر GL Doc
4) UI کاملاً فارسی + تاریخ جلالی (نمایش)، ولی خروجی/داده Gregorian

## وضعیت فعلی (Snapshot)
- Latest tag: BH-TEST-20251228.0343
- Date: 2026-01-03

## Streamها و IDها (پیشنهاد استاندارد)
- VAT-xx: VAT Engine
- LEGAL-xx: Legal Output/Audit Core
- TTMS-xx: TTMS
- MOD-xx: Modian
- PAY-xx: Payroll Legal
- DIM-xx: Dimensions
- CI-xx: Regression/CI/GitOps

## Done (نمونه‌های تایید شده اخیر)
- VAT-12 Intent Regress v0.7: PASS (SI/PI)
- VAT-13 Guard Regress v0.2: PASS (flip intent/template submit-block)
- BH-EP01 v0.3 CI: PASS (Intent 7/7, Purchase 8/8, Sales 8/8)
- LEGAL07/08/09: PASS (issue/cancel/amend + tamper blocked)
- Period Lock v01/v02: PASS

## Next (پیشنهاد فردا)
- تثبیت «منبع حقیقت» (این ۳ فایل) و تبدیل STATUS.md/LEGAL_STATUS_BOARD.md به Pointer
- اضافه‌کردن step به nightly برای آپدیت خودکار STATUS_BOARD/CHANGELOG (اختیاری)
- شروع TTMS/MODIAN واقعی (فراتر از skeleton): mapping و payload schema versioning
