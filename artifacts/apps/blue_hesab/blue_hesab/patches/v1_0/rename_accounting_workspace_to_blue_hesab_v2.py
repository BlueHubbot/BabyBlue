import frappe

def execute():
    new_title = "بلو حساب"
    name_candidates = ["Accounting", "Accounts", "بلو حساب", "Blue Hesab"]
    label_candidates = ["Accounting", "Accounts", "حسابداری"]

    workspaces = frappe.get_all("Workspace", fields=["name", "label"])
    for ws in workspaces:
        if ws.name in name_candidates or (ws.label and ws.label in label_candidates):
            doc = frappe.get_doc("Workspace", ws.name)
            if hasattr(doc, "label"):
                doc.label = new_title
            if hasattr(doc, "title"):
                doc.title = new_title
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            break
