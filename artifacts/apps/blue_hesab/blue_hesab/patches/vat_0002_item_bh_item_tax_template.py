import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Item": [
            dict(
                fieldname="bh_item_tax_template",
                label="BH Item Tax Template",
                fieldtype="Link",
                options="Item Tax Template",
                insert_after="bh_vat_profile",
                no_copy=1,
                print_hide=1,
            )
        ]
    }

    create_custom_fields(fields, update=True)
    frappe.db.commit()
