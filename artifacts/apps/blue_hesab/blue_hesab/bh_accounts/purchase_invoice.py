import frappe


def apply_default_vat(doc, method=None):
    """Auto-apply Iranian VAT on Purchase Invoice based on BH Settings."""
    if doc.doctype != "Purchase Invoice":
        return

    settings = frappe.get_single("BH Settings")

    if not getattr(settings, "enable_iran_mode", None):
        return

    if not getattr(settings, "enable_vat", None):
        return

    # اگر حساب یا نرخ تعریف نشده، کاری نکن
    account = getattr(settings, "default_purchase_vat_account", None)
    rate = getattr(settings, "default_purchase_vat_rate", None)

    if not account or not rate:
        return

    # اگر قبلاً VAT خطی اضافه شده، دوباره اضافه نکن
    existing_tax = None
    for row in doc.taxes or []:
        # بر اساس account_head و نوع مالیات چک می‌کنیم
        if row.account_head == account and abs(float(row.rate) - float(rate)) < 0.0001:
            existing_tax = row
            break

    if existing_tax:
        return

    # اگر جدول خالی است، index = 1
    idx = (doc.taxes[-1].idx + 1) if (doc.taxes and len(doc.taxes)) else 1

    tax = doc.append("taxes", {})
    tax.idx = idx
    tax.charge_type = "On Net Total"
    tax.account_head = account
    tax.description = "VAT خرید (خودکار BlueHesab)"
    tax.rate = float(rate)
    tax.included_in_print_rate = 0
    tax.cost_center = None
