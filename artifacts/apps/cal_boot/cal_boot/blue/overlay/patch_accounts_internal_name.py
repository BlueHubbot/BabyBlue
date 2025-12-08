import frappe
from frappe.model.rename_doc import rename_doc


def has_persian(s: str) -> bool:
    if not s:
        return False
    return any("\u0600" <= ch <= "\u06FF" for ch in s)


def get_fa_translation(src: str) -> str | None:
    """بر اساس Translation(language=fa) ترجمه‌ی غیرخالی را برمی‌گرداند."""
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


def patch_account_internal_names() -> int:
    changed = 0

    rows = frappe.get_all(
        "Account",
        fields=["name"],
        order_by="name",
    )

    for r in rows:
        old_name = (r.get("name") or "").strip()
        if not old_name:
            continue

        # اگر نام فعلی فارسی است، بی‌خیال
        if has_persian(old_name):
            continue

        base = old_name
        suffix = ""

        # الگوی معمول ERPNext: "Xxx Yyy - ABD"
        if " - " in old_name:
            base, suffix = old_name.rsplit(" - ", 1)

        base = base.strip()
        suffix = suffix.strip()

        if not base:
            continue

        new_base = get_fa_translation(base)
        if not new_base or new_base == base:
            # ترجمه‌ای در کانن/DB نداریم
            continue

        if suffix:
            new_name = f"{new_base} - {suffix}"
        else:
            new_name = new_base

        if new_name == old_name:
            continue

        # اگر حسابی با این نام جدید هست، ریسک merge نمی‌کنیم
        if frappe.db.exists("Account", new_name):
            continue

        rename_doc(
            "Account",
            old_name,
            new_name,
            ignore_permissions=True,
            force=True,
        )
        changed += 1

    return changed


def run():
    n = patch_account_internal_names()
    frappe.db.commit()
    print(f"PATCH_ACCOUNT_INTERNAL_NAMES={n}")
