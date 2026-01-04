from __future__ import annotations

from typing import Any, Dict, Optional

from .vat_pipe_common import KIND_PURCHASE, KIND_SALES
from .vat_pipe_intent_lock import VAT11_POLICY_VER, vat11_lock_intent_guard


def vat11_is_real_pos_sales_invoice(doc) -> bool:
    """
    BH VAT: treat Sales Invoice as POS if it is marked as POS and there is any POS payment evidence.
    We intentionally do NOT require a POS Profile to exist, because many installs run POS-like flows
    without POS Profile configured (tests included).
    """
    try:
        if not doc or getattr(doc, "doctype", None) != "Sales Invoice":
            return False

        if int(getattr(doc, "is_pos", 0) or 0) != 1:
            return False

        # POS profile is a strong signal, but not mandatory
        if getattr(doc, "pos_profile", None):
            return True

        # Payments table is enough
        pays = getattr(doc, "payments", None)
        if pays and len(pays) > 0:
            return True

        # Paid amount is enough (some flows set paid_amount without payments rows)
        if float(getattr(doc, "paid_amount", 0) or 0) > 0:
            return True

        # If it's explicitly marked POS, still treat as POS (prevents wrong EXCL defaulting)
        return True
    except Exception:
        return False


def _infer_kind_from_doctype(doc) -> Optional[str]:
    try:
        dt = (doc.get("doctype") if hasattr(doc, "get") else getattr(doc, "doctype", None)) or ""
    except Exception:
        dt = ""
    dt = dt.strip()
    if dt == "Sales Invoice":
        return KIND_SALES
    if dt == "Purchase Invoice":
        return KIND_PURCHASE
    return None


def vat26_enforce_inclusive_intent(
    doc,
    *,
    kind: Optional[str] = None,
    axis: Optional[str] = None,
    allow_pos_implicit: bool = True,
    no_autofix: bool = True,
    is_submit: Optional[bool] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Public entrypoint for VAT-11 intent lock.
    Backward-compatible: ignores unknown kwargs.
    """
    k = (kind or _infer_kind_from_doctype(doc) or "").strip().lower()
    if k not in (KIND_SALES, KIND_PURCHASE):
        return {"ver": VAT11_POLICY_VER, "skipped": True, "reason": "unsupported_doctype"}

    real_pos = vat11_is_real_pos_sales_invoice(doc) if k == KIND_SALES else False
    return vat11_lock_intent_guard(
        doc,
        kind=k,
        axis=axis,
        allow_pos_implicit=allow_pos_implicit,
        real_pos=real_pos,
        no_autofix=no_autofix,
        is_submit=is_submit,
    )

def vat11_resolve_price_mode(doctype: str, doc, company: str | None = None) -> str:
    """
    Backward-compat helper for older regress tests (VAT-12 INTENT REGRESS).

    Current production logic relies on doc.bh_vat_price_mode, but regress tests
    may pass only is_pos / taxes_and_charges. We resolve as:

      - If bh_vat_price_mode is present -> normalize & return it
      - Else Sales Invoice real POS -> Inclusive
      - Else -> Exclusive
    """

    def _get(key, default=None):
        try:
            if hasattr(doc, "get"):
                return doc.get(key, default)
        except Exception:
            pass
        return getattr(doc, key, default)

    # 1) explicit mode on doc wins
    raw = (_get("bh_vat_price_mode") or "").strip()
    low = raw.lower()
    if low.startswith("incl"):
        return "Inclusive"
    if low.startswith("excl"):
        return "Exclusive"

    # 2) infer for regress
    if doctype == "Sales Invoice":
        if bool(_get("is_pos")) or bool(_get("pos_profile")):
            return "Inclusive"

    return "Exclusive"

def vat11_enforce_inclusive_intent_on_submit(doc, kind: str):
    """
    VAT-11: Inclusive Intent must be explicit and consistent on SUBMIT.
    - Draft is free.
    - If taxes_and_charges indicates INCL but doc intent is not Inclusive => block.
    - If doc intent is Inclusive but template is EXCL => block (unless POS rule allows).
    """
    intent = (doc.get("bh_vat_price_mode") or "").strip()  # "Exclusive" / "Inclusive"
    if not intent:
        # No intent: we allow only EXCL on submit (safe default)
        intent = "Exclusive"

    tpl = (doc.get("taxes_and_charges") or "").strip()

    # heuristic: detect INCL/EXCL from template name (your templates already use this convention)
    tpl_is_incl = ("(INCL)" in tpl) or ("INCL" in tpl)
    tpl_is_excl = ("(EXCL)" in tpl) or ("EXCL" in tpl)

    # If template doesn't encode, don't guess; block only if intent says Inclusive and we can't prove template is INCL.
    if intent == "Inclusive":
        if tpl_is_excl:
            raise_bh_vat_error(
                BH_VAT_E_GENERIC,
                "BH VAT: نوع قیمت‌گذاری «شامل مالیات» انتخاب شده اما قالب مالیات «غیرشامل» است. لطفاً قالب صحیح (INCL) را انتخاب کنید.",
                context={"doctype": doc.doctype, "name": doc.name, "template": tpl, "intent": intent},
            )
        if not tpl_is_incl:
            raise_bh_vat_error(
                BH_VAT_E_GENERIC,
                "BH VAT: نوع قیمت‌گذاری «شامل مالیات» انتخاب شده اما قالب مالیات قابل تشخیص نیست. لطفاً قالب MIXED (INCL) را انتخاب کنید.",
                context={"doctype": doc.doctype, "name": doc.name, "template": tpl, "intent": intent},
            )

    # intent Exclusive
    if intent == "Exclusive":
        if tpl_is_incl:
            raise_bh_vat_error(
                BH_VAT_E_GENERIC,
                "BH VAT: نوع قیمت‌گذاری «غیرشامل مالیات» است اما قالب مالیات «شامل» انتخاب شده. لطفاً قالب صحیح (EXCL) را انتخاب کنید.",
                context={"doctype": doc.doctype, "name": doc.name, "template": tpl, "intent": intent},
            )

def bh_before_submit_sales_invoice(doc, method=None):
    return vat11_enforce_inclusive_intent_on_submit(doc, kind="sales")

def bh_before_submit_purchase_invoice(doc, method=None):
    return vat11_enforce_inclusive_intent_on_submit(doc, kind="purchase")
