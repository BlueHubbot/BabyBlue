# -*- coding: utf-8 -*-
"""
BlueHesab Legal Output policy (minimal, regression-friendly).

Goals:
- Per-Company boundary
- Versioned outputs (schema_version) + generator_build marker
- Deterministic enablement list (VAT_INVOICE, TTMS_EXPORT, MODIAN_PAYLOAD)

This module is intentionally tiny and defensive (no guesswork, no "..." placeholders).
"""
from __future__ import annotations

from typing import Dict, List, Optional

# Stable identifiers (used in logs/regress)
LEGAL_SCHEMA_VERSION_DEFAULT = "LEGAL-V1"
LEGAL_GENERATOR_BUILD_DEFAULT = "BH-DEV"

# Output types (string constants)
OUT_VAT_INVOICE = "VAT_INVOICE"
OUT_TTMS_EXPORT = "TTMS_EXPORT"
OUT_MODIAN_PAYLOAD = "MODIAN_PAYLOAD"

ALL_OUTPUT_TYPES: List[str] = [OUT_VAT_INVOICE, OUT_TTMS_EXPORT, OUT_MODIAN_PAYLOAD]

# Correction reasons (string constants)
CORR_CANCEL = "CANCEL"
CORR_AMEND = "AMEND"


def normalize_output_type(value: str) -> str:
    v = (value or "").strip().upper()
    # keep canonical names
    for x in ALL_OUTPUT_TYPES:
        if v == x:
            return x
    # allow legacy lowercase etc
    mapping = {
        "VAT": OUT_VAT_INVOICE,
        "VAT_INVOICE": OUT_VAT_INVOICE,
        "TTMS": OUT_TTMS_EXPORT,
        "TTMS_EXPORT": OUT_TTMS_EXPORT,
        "MODIAN": OUT_MODIAN_PAYLOAD,
        "MODIAN_PAYLOAD": OUT_MODIAN_PAYLOAD,
    }
    return mapping.get(v, value)


def get_enabled_outputs(company: str, reference_doctype: str) -> List[str]:
    """
    Minimal policy: always enable all 3 outputs (regress expects this).
    In future, read from BH Settings / Company legal profile.
    """
    _ = company, reference_doctype
    return list(ALL_OUTPUT_TYPES)


def get_schema_version(company: str, reference_doctype: str) -> str:
    _ = company, reference_doctype
    return LEGAL_SCHEMA_VERSION_DEFAULT


def get_generator_build(company: str) -> str:
    _ = company
    return LEGAL_GENERATOR_BUILD_DEFAULT


def as_policy(company: str, reference_doctype: str) -> Dict[str, object]:
    return {
        "company": company,
        "reference_doctype": reference_doctype,
        "schema_version": get_schema_version(company, reference_doctype),
        "generator_build": get_generator_build(company),
        "enabled_outputs": get_enabled_outputs(company, reference_doctype),
    }
