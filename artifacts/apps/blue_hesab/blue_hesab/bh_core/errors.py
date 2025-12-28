# apps/blue_hesab/blue_hesab/bh_core/errors.py
from __future__ import annotations

from typing import Final, Dict, List


# =========================
# VAT error codes (official)
# =========================

BH_VAT_E_TPL_NONSTR: Final[str] = "BH-VAT-E-TPL-NONSTR"
BH_VAT_E_TPL_NO_TEMPLATE: Final[str] = "BH-VAT-E-TPL-NO-TEMPLATE"
BH_VAT_E_GENERIC: Final[str] = "BH-VAT-E-GENERIC"

VAT_ERROR_REGISTRY: Final[Dict[str, str]] = {
    BH_VAT_E_TPL_NONSTR: "item_tax_template must be str|None after normalization",
    BH_VAT_E_TPL_NO_TEMPLATE: "no Item Tax Template exists in DB (CI setup issue)",
}


def list_vat_error_codes() -> List[str]:
    return sorted(VAT_ERROR_REGISTRY.keys())


def assert_vat_error_codes_sane() -> None:
    codes = list_vat_error_codes()

    # uniqueness
    if len(codes) != len(set(codes)):
        raise AssertionError("[BH-VAT-E-CODES-DUP] duplicate VAT error codes detected")

    # prefix policy (hard rule for reporting)
    bad = [c for c in codes if not c.startswith("BH-VAT-")]
    if bad:
        raise AssertionError(f"[BH-VAT-E-CODES-PREFIX] invalid prefix: {bad}")

    # non-empty descriptions
    for c in codes:
        d = VAT_ERROR_REGISTRY.get(c) or ""
        if not d.strip():
            raise AssertionError(f"[BH-VAT-E-CODES-DESC] missing description for {c}")
