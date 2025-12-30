# LEGAL Status Board (BlueHesab Legal Outputs)

> Master Spec: `README.md` (NNG-01..04 و GitOps/Tag Policy)

## Legend
✅ Done | 🟡 In Progress | ⛔ Blocked | ⏭ Next

## Current
- ✅ LEGAL-05 — Smoke: ISSUE → CANCEL → AMEND chain (Sales + Purchase)
- ✅ LEGAL-06.1 — Fix `reference_name` fieldtype + migrate
- ⏭ LEGAL-07 — Hardening v1 + close manipulation paths + new regressions

---

## LEGAL-07 — Hardening v1 (Definition + Acceptance)

### هدف
قفل‌کردن کامل مسیرهای دستکاری و رسمی‌کردن رفتار Cancel/Amend + افزودن تست‌های ضد-regress.

### Acceptance Criteria (بایدها)
1) **Immutability after submit**
   - هر گونه edit/delete/trash روی رکوردهای BH Legal Output بعد از submit ممنوع.
   - تنها مسیر مجاز: “Cancel/Amend flow” با تولید خروجی نسخه جدید + لینک به قبلی.

2) **Server-side tamper detection**
   - هر بار validate/submit: محاسبه و مقایسه `source_hash` و تشخیص mismatch.
   - خطا/پیام‌ها کاملاً فارسی + ثبت لاگ.

3) **Canonical chain rules**
   - Amend بدون Cancel باید fail شود.
   - Cancel دوباره: رفتار دقیق مشخص و تست‌شده (یا idempotent یا fail صریح).
   - Amend همیشه به آخرین CANCEL وصل شود (نه ISSUE).

4) **Regression Pack**
   - حداقل 3 تست: amend بدون cancel، cancel دوباره، دستکاری بعد submit.

### Deliverables
- کد hardening + guardها
- تست‌ها + لاگ خروجی
- آپدیت Daily Delta + Release note در Tag بعدی
