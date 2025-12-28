import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
from frappe.utils import today, flt

def _company():
    if frappe.db.exists('DocType','BH Settings'):
        c = frappe.db.get_single_value('BH Settings','default_company')
        if c and frappe.db.exists('Company', c):
            return c
    c = frappe.db.get_value('Company', {}, 'name')
    if not c:
        raise Exception('No Company found.')
    return c

def _sales_vat_account():
    if not frappe.db.exists('DocType','BH Settings'):
        return None
    return frappe.db.get_single_value('BH Settings','default_sales_vat_account')

def _pick_income(company):
    acc = frappe.db.get_value('Account', {'company': company, 'root_type': 'Income', 'is_group': 0}, 'name')
    if acc:
        return acc
    acc = frappe.db.get_value('Account', {'company': company, 'is_group': 0}, 'name')
    if not acc:
        raise Exception('No leaf account found.')
    return acc

def _pick_customer():
    c = frappe.db.get_value('Customer', {}, 'name')
    if c:
        return c
    # minimal create
    cg = frappe.db.get_value('Customer Group', {}, 'name') or 'All Customer Groups'
    tr = frappe.db.get_value('Territory', {}, 'name') or 'All Territories'
    doc = frappe.new_doc('Customer')
    doc.customer_name = 'مشتری تست VAT'
    doc.customer_group = cg
    doc.territory = tr
    doc.save(ignore_permissions=True)
    return doc.name

def _require_items():
    items = ['BH-VAT-STD_9-TEST','BH-VAT-ZERO-TEST','BH-VAT-EXEMPT-TEST','BH-VAT-EXPORT_0-TEST']
    miss = [i for i in items if not frappe.db.exists('Item', i)]
    if miss:
        raise Exception('Missing test items: ' + ', '.join(miss))
    return items

def _gl(company, voucher_no):
    rows = frappe.get_all(
        'GL Entry',
        filters={'company': company, 'voucher_type': 'Sales Invoice', 'voucher_no': voucher_no},
        fields=['account','debit','credit','party_type','party'],
        limit_page_length=2000
    )
    agg = {}
    for r in rows:
        a = r['account']
        agg.setdefault(a, {'dr':0.0,'cr':0.0})
        agg[a]['dr'] += flt(r['debit'])
        agg[a]['cr'] += flt(r['credit'])
    return agg

@frappe.whitelist()
def run_base(rate=1000000):
    company = _company()
    vat_acc = _sales_vat_account()
    if not vat_acc:
        raise Exception('BH Settings.default_sales_vat_account is not set.')

    income = _pick_income(company)
    customer = _pick_customer()
    items = _require_items()

    si = frappe.new_doc('Sales Invoice')
    si.company = company
    si.customer = customer
    si.posting_date = today()
    si.set_posting_time = 1

    for code in items:
        si.append('items', {
            'item_code': code,
            'qty': 1,
            'rate': flt(rate),
            'income_account': income,
        })

    si.save(ignore_permissions=True)  # triggers before_validate (sets MIXED VAT row + sales item_tax_template)
    si.submit()

    # totals expectation: VAT only on STD_9 => 90k when rate=1,000,000
    exp_vat = flt(rate) * 0.09
    got_vat = flt(si.total_taxes_and_charges)

    gl = _gl(company, si.name)
    vat_line = gl.get(vat_acc, {'dr':0.0,'cr':0.0})

    print('\n=== SALES MIXED SMOKE (v0.2 / WI-01) ===')
    print('SI:', si.name)
    print('Net:', si.net_total, 'VAT:', got_vat, 'Grand:', si.grand_total)
    print('VAT Account:', vat_acc, 'GL Dr:', vat_line['dr'], 'GL Cr:', vat_line['cr'])

    ok = abs(got_vat - exp_vat) < 0.02 and vat_line['cr'] > 0
    if not ok:
        raise Exception('FAIL: VAT or GL does not match expectation.')
    print('PASS')
    return {'si': si.name, 'net': si.net_total, 'vat': got_vat, 'grand': si.grand_total, 'vat_gl_cr': vat_line['cr']}
