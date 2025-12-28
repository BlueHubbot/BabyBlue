frappe.ui.form.on('Item', {
  setup(frm) {
    if (frm.fields_dict.bh_item_tax_template) {
      frm.set_df_property('bh_item_tax_template', 'label', 'قالب مالیات کالا (VAT)');
    }

    frm.set_query('bh_item_tax_template', function () {
      const company =
        frm.__bh_default_company ||
        frappe.defaults.get_user_default('Company') ||
        frappe.defaults.get_default('company');

      return {
        filters: {
          company: company,
          name: ['like', '%VAT%']   // فقط قالب‌های VAT، نه Iran Tax عمومی
        }
      };
    });
  },

  refresh(frm) {
    if (frm.__bh_loaded_once) return;
    frm.__bh_loaded_once = true;

    frappe.call({
      method: 'blue_hesab.bh_core.vat_item_autofill.get_default_item_tax_template',
      args: { profile: frm.doc.bh_vat_profile || null }
    }).then(r => {
      const m = r.message || {};
      frm.__bh_default_company = m.company || null;
      frm.refresh_field('bh_item_tax_template');
    });
  },

  bh_vat_profile(frm) {
    frappe.call({
      method: 'blue_hesab.bh_core.vat_item_autofill.get_default_item_tax_template',
      args: { profile: frm.doc.bh_vat_profile || null }
    }).then(r => {
      const m = r.message || {};
      if (m.template) frm.set_value('bh_item_tax_template', m.template);
    });
  }
});
