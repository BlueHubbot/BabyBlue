import frappe
from frappe.model.rename_doc import rename_doc


def _has_persian(s: str) -> bool:
    if not s:
        return False
    return any("\u0600" <= ch <= "\u06FF" for ch in s)


def _get_fa_translation(src: str) -> str | None:
    if not src:
        return None
    tr = frappe.db.get_value(
        "Translation",
        {"language": "fa", "source_text": src},
        "translated_text",
    )
    if not tr:
        return None
    tr = (tr or "").strip()
    if not tr:
        return None
    return tr


# ------------------ Account ------------------


def patch_accounts() -> int:
    changed = 0

    rows = frappe.get_all(
        "Account",
        fields=["name", "account_name"],
        order_by="name",
    )

    for r in rows:
        src = (r.get("account_name") or "").strip()
        if not src:
            continue
        if _has_persian(src):
            continue

        dst = _get_fa_translation(src)
        if not dst or dst == src:
            continue

        frappe.db.set_value(
            "Account",
            r["name"],
            "account_name",
            dst,
            update_modified=False,
        )
        changed += 1

    return changed


# ------------------ UOM ------------------


def patch_uoms() -> tuple[int, int]:
    """
    اگر ترجمه‌ی فارسی آماده داشته باشیم:
      - نام UOM را با rename_doc فارسی می‌کند
      - اگر فیلد category وجود داشته باشد، دسته‌بندی را هم فارسی می‌کند
    """
    meta = frappe.get_meta("UOM")
    has_category_field = any(df.fieldname == "category" for df in meta.fields)

    fields = ["name"]
    if has_category_field:
        fields.append("category")

    rows = frappe.get_all(
        "UOM",
        fields=fields,
        order_by="name",
    )

    renamed = 0
    cat_changed = 0

    for r in rows:
        docname = (r.get("name") or "").strip()
        if not docname:
            continue

        # 1) rename نام UOM
        if not _has_persian(docname):
            new_name = _get_fa_translation(docname)
            if new_name and new_name != docname:
                if not frappe.db.exists("UOM", new_name):
                    rename_doc(
                        "UOM",
                        docname,
                        new_name,
                        ignore_permissions=True,
                        force=True,
                    )
                    renamed += 1
                    docname = new_name  # ادامه‌ی کار روی اسم جدید

        # 2) دسته‌بندی فقط اگر چنین فیلدی داریم
        if has_category_field:
            category = (r.get("category") or "").strip()
            if category and not _has_persian(category):
                new_cat = _get_fa_translation(category)
                if new_cat and new_cat != category:
                    frappe.db.set_value(
                        "UOM",
                        docname,
                        "category",
                        new_cat,
                        update_modified=False,
                    )
                    cat_changed += 1

    return renamed, cat_changed


# ------------------ entrypoint ------------------


def run():
    acc_changed = patch_accounts()
    uom_renamed, uom_cat_changed = patch_uoms()
    frappe.db.commit()
    print(
        f"PATCH_ACCOUNTS={acc_changed} "
        f"PATCH_UOMS_RENAME={uom_renamed} "
        f"PATCH_UOMS_CATEGORY={uom_cat_changed}"
    )
