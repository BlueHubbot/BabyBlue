# BLUE_HESAB_MASTER — STATUS
Resume phrase: `Continue BLUE_HESAB_MASTER / STATUS`

## North Star (غیرقابل مذاکره)
- مرز قانونی = Company (VAT/TTMS/Modian/Payroll/Insurance/... همگی Per-Company)
- خروجی‌های قانونی: نسخه‌دار + قابل بازتولید + قابل ممیزی (schema_version, payload hash, generated_by/at) و Immutable بعد از Submit
- Dimensions از روز اول: هر سند GL-posting باید تفکیک‌پذیر و enforce شود
- UI/Errors/Labels کامل فارسی + Jalali UI (Export/Regulatory Gregorian)

## Current Build
- schema_version / generator_build: **BH-20260106.1**
- Site: baba.bluehesab.ir | Company: BlueAPi

---

## Daily Delta — 2026-01-06 (Runbook Full)
### Done today ✅
- RUNBOOK: اجرای suite کامل `bh_runbook_regress.sh all` با نتیجه OK
- DIM: smoke + DIM02 terminal checks + DIM04 audit GL + DIM04 JE stamp (linewise) → PASS
- VAT: lint v12 + intent v01/v08 + VAT-13 guard + period lock v01/v02 + MIXED PI/SI + CI wrappers → PASS
- LEGAL: LEGAL05 cycles + LEGAL suite 07+08+09 → PASS
- LEGAL: اجرای مستقیم regressهای LEGAL07/08/09 → 100% PASS

### Progress 🟡
- مستندسازی/گیت‌آپس: VERSION + STATUS_BOARD + release note هنوز آپدیت نشده‌اند

### Blocked ⛔
- ندارد

---

## Status Board
### DIMENSIONS
- ✅ DIM-01 — Core dimension policy/matrix + adapters پایه
- ✅ DIM-02 — Terminal checks suite (sanity/policy)
- ✅ DIM-04 — Audit GL + JE stamping (linewise)
- 🟡 DIM-05 — گسترش enforce/stamp به همه GL-posting DocTypeها + تست‌های ضد-ریگرس

### VAT
- ✅ VAT-10 — Production pipeline hardening (terminal OK)
- ✅ VAT-11 — Inclusive intent hardening (terminal OK)
- ✅ VAT-12 — Anti-regress intent/normal scenarios (intent v08 OK)
- ✅ VAT-13 — Guard regress (flip/submit-block/non-BH reject) OK
- ✅ VAT-16/17/18 — Terminal suites OK
- 🟡 VAT-19 — تثبیت نهایی “Template-driven intent” در UI/Templateها (اگر چیزی مانده باشد)

### LEGAL OUTPUTS
- ✅ LEGAL-05 — smoke sales/purchase cycle
- ✅ LEGAL-07 — amend/cancel/tamper blocked + audit meta OK
- ✅ LEGAL-08 — policy lock + skeleton TTMS/Modian OK
- ✅ LEGAL-09 — emit chain: issue/cancel/amend + PI issue/cancel OK
- 🟡 LEGAL-10 — TTMS export واقعی (ساخت payload واقعی + validate + فایل خروجی)
- 🟡 LEGAL-11 — Modian payload واقعی (ساخت payload واقعی + validate + امضا/هش)
- 🟡 LEGAL-12 — Period close/seal + constraints سراسری Per-Company

### RUNBOOK / CI / GITOPS
- 🟡 RUNBOOK-01 — تمیزکاری: حذف اجرای تکیِ redundant یا تضمین SKIP با RC=0 (برای CI بی‌حاشیه)
- 🟡 GITOPS-01 — آپدیت VERSION + STATUS_BOARD + releases/<TAG>.md و commit/tag

---

## Next session (پیشنهاد قطعی)
1) **GITOPS-01**: آپدیت 3 فایل (VERSION, STATUS_BOARD, release note) و یک Commit تمیز با عنوان build BH-20260106.1
2) **RUNBOOK-01**: یک‌دست‌سازی SKIPها (یا حذف redundant) تا CI هیچ RC=1 نبیند
3) شروع Sprint بعدی: **DIM-05 + LEGAL-10/11**
   - DIM-05: پوشش همه DocTypeهای GL-posting + تست audit
   - LEGAL-10/11: تبدیل skeleton به خروجی واقعی (payload واقعی + validate + hash/audit)

