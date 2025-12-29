from __future__ import annotations

def bh_before_cancel_invoice(doc, method=None):
    """
    BH Legal Output is an immutable audit log and MUST NOT block cancel of the source doc.
    We explicitly whitelist it during cancel.
    """
    ignore = getattr(doc, "ignore_linked_doctypes", None)

    if ignore is None:
        ignore_list = []
    elif isinstance(ignore, (list, tuple, set)):
        ignore_list = list(ignore)
    else:
        ignore_list = [str(ignore)]

    if "BH Legal Output" not in ignore_list:
        ignore_list.append("BH Legal Output")

    doc.ignore_linked_doctypes = ignore_list

    # belt & suspenders (harmless)
    doc.flags.ignore_links = True
