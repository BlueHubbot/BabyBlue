# BlueHesab — STATUS (nightly/baba)

> **Master Roadmap / Spec:** `README.md` (نقشه اصلی و Non-Negotiables و Policyها آنجاست)
> **Daily Logs:** `status/daily/`
> **Legal Board:** `roadmaps/LEGAL_STATUS_BOARD.md`
> **Releases (immutable per tag):** `releases/`

## Current Baseline
- Date (local): **2025-12-30**
- Repo: `BlueHubbot/BabyBlue`
- Branch: `nightly/baba`
- Current schema_version (tag): **BH-20251229.2**
- generator_build: **BH-20251229.2@453bd9b**

> Reminder: Schema Version = Git Tag (BH-YYYYMMDD.N) و Release Note الزامی است. (طبق README)

## Today (Latest Daily Delta)
- 📌 **Today log:** `status/daily/2025-12-30.md`

## Status Boards (Summary)

### LEGAL (Legal Outputs)
- ✅ LEGAL-05 Smoke PASS (Sales+Purchase chain: ISSUE → CANCEL → AMEND)
- ✅ LEGAL-06.1 PASS (Fix reference_name fieldtype + migrate OK)
- 🟡 LEGAL-07 NEXT: Hardening + “close manipulation paths” + new regressions

### VAT (high-level)
- ✅ VAT Core (Mixed + intent guard + base regress): PASS (BH-EP01 v0.3 per prior status)
- ✅ VAT Legal Output (Legal05 chain): PASS
- 🟡 VAT/Legal Hardening: در صف (هم‌راستا با LEGAL-07)

## Update Rule (Non-Negotiable)
- هر شب بعد از Nightly Sync + Tag:
  1) یک فایل روزانه در `status/daily/YYYY-MM-DD.md`
  2) آپدیت این فایل (`STATUS.md`) به آخرین روز
  3) Release note همان Tag داخل `releases/<TAG>.md` (immutable)
