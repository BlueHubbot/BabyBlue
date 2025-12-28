from frappe import _

def get_data():
    return [
        {
            "label": _("Blue Hesab"),
            "icon": "octicon octicon-graph",
            "items": [
                {
                    "type": "doctype",
                    "name": "BH Settings",
                    "label": _("BH Settings")
                },
                {
                    "type": "doctype",
                    "name": "BH Period Lock",
                    "label": _("BH Period Lock")
                },
                {
                    "type": "doctype",
                    "name": "BH Account Mapping Profile",
                    "label": _("BH Account Mapping Profile")
                },
                {
                    "type": "doctype",
                    "name": "BH VAT Category",
                    "label": _("BH VAT Category")
                },
                {
                    "type": "doctype",
                    "name": "BH TTMS Document",
                    "label": _("BH TTMS Document")
                },
                {
                    "type": "doctype",
                    "name": "BH E-Invoice Document",
                    "label": _("BH E-Invoice Document")
                },
                {
                    "type": "doctype",
                    "name": "BH Modian Log",
                    "label": _("BH Modian Log")
                },
                {
                    "type": "doctype",
                    "name": "BH Insurance Export",
                    "label": _("BH Insurance Export")
                },
                {
                    "type": "doctype",
                    "name": "BH Payroll Tax Export",
                    "label": _("BH Payroll Tax Export")
                },
                {
                    "type": "doctype",
                    "name": "BH Financial Statement Profile",
                    "label": _("BH Financial Statement Profile")
                }
            ]
        }
    ]
