import frappe

from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
PROFILE_CODE_MAP = {
    'STD_9': 'STD_9', 'ZERO': 'ZERO', 'EXEMPT': 'EXEMPT', 'EXPORT_0': 'EXPORT_0',
    'استاندارد ۹٪': 'STD_9', 'صفر درصد': 'ZERO', 'معاف': 'EXEMPT', 'صادرات ۰٪': 'EXPORT_0',
}

def _company(doc):
    return (doc.get('company') or
            (frappe.db.get_single_value('BH Settings', 'default_company') if frappe.db.exists('DocType','BH Settings') else None) or
            frappe.db.get_value('Company', {}, 'name'))

def _bh_sales_vat():
    if not frappe.db.exists('DocType','BH Settings'):
        return (None, None)
    return (
        frappe.db.get_single_value('BH Settings','default_sales_vat_account'),
        frappe.db.get_single_value('BH Settings','default_sales_vat_rate') or 9.0
    )

def _ensure_tax_row(doc, vat_account, vat_rate):
    if not vat_account:
        return
    for t in (doc.get('taxes') or []):
        if t.get('account_head') == vat_account:
            # keep it aligned
            if t.get('charge_type') in (None, ''):
                t.charge_type = 'On Net Total'
            if t.get('rate') in (None, ''):
                t.rate = vat_rate
            return

    doc.append('taxes', {
        'charge_type': 'On Net Total',
        'account_head': vat_account,
        'description': 'مالیات بر ارزش افزوده (MIXED)',
        'rate': vat_rate,
        'included_in_print_rate': 0,
        'add_deduct_tax': 'Add',
    })

def _find_sales_item_tax_template(company, code, sales_vat_account):
    if not (company and code and sales_vat_account):
        return None

    itts = frappe.get_all(
        'Item Tax Template',
        filters={'company': company},
        fields=['name','title'],
        limit_page_length=1000
    )

    # must contain code AND has tax row pointing to sales VAT account
    for r in itts:
        hay = f"{r.get('name','')} {r.get('title','')}"
        if code not in hay:
            continue
        doc = frappe.get_doc('Item Tax Template', r['name'])
        for t in doc.taxes:
            if t.tax_type == sales_vat_account:
                return doc.name
    return None

def bh_before_validate_sales_invoice(doc, method=None):
    company = _company(doc)
    sales_vat_account, sales_vat_rate = _bh_sales_vat()
    if not sales_vat_account:
        return

    _ensure_tax_row(doc, sales_vat_account, sales_vat_rate)

    # cache templates by code
    cache = {}

    for it in (doc.get('items') or []):
        item_code = it.get('item_code')
        if not item_code:
            continue

        # resolve profile -> code
        profile = frappe.db.get_value('Item', item_code, 'bh_vat_profile')
        code = PROFILE_CODE_MAP.get(profile) or PROFILE_CODE_MAP.get(str(profile)) if profile else None
        if not code:
            # fallback: try from Item Tax Template saved on Item
            continue

        if code not in cache:
            cache[code] = _find_sales_item_tax_template(company, code, sales_vat_account)

        # set only if empty OR wrong (i.e. does not match sales VAT account)
        tmpl = cache.get(code)
        if tmpl:
            it.item_tax_template = tmpl

    # recalc
    if hasattr(doc, 'calculate_taxes_and_totals'):
        doc.calculate_taxes_and_totals()
