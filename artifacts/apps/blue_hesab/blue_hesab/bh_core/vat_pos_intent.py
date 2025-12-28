from __future__ import annotations

def bh_before_validate_sales_invoice_pos_intent(doc, method=None):
    """
    Fix POS defaulting:
    - bh_vat_price_mode CF has default=Exclusive
    - For POS invoices using INCL mixed template, we must override default to Inclusive
      BEFORE the intent-lock runs, otherwise it mismatches and gets blocked.
    """
    try:
        if not doc or getattr(doc, "doctype", None) != "Sales Invoice":
            return

        if int(getattr(doc, "is_pos", 0) or 0) != 1:
            return

        tac = (getattr(doc, "taxes_and_charges", None) or "").strip()
        if not tac:
            return

        # Detect INCL/EXCL from template name (your naming is stable)
        want_incl = "(INCL)" in tac
        want_excl = "(EXCL)" in tac

        if not (want_incl or want_excl):
            return

        # Current mode (often defaulted to Exclusive by CF default)
        cur = getattr(doc, "bh_vat_price_mode", None)

        if want_incl and cur != "Inclusive":
            doc.bh_vat_price_mode = "Inclusive"
            if hasattr(doc, "bh_vat_inclusive_intent"):
                doc.bh_vat_inclusive_intent = 1

        if want_excl and cur != "Exclusive":
            doc.bh_vat_price_mode = "Exclusive"
            if hasattr(doc, "bh_vat_inclusive_intent"):
                doc.bh_vat_inclusive_intent = 0

    except Exception:
        # never block normal flow because of helper
        return
