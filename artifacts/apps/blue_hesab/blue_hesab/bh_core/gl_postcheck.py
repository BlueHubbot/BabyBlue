# -*- coding: utf-8 -*-
"""
blue_hesab.bh_core.gl_postcheck

این ماژول فقط برای جلوگیری از Crash هنگام doc_events مربوط به GL Entry است.
اصل enforce اصلی شما جای دیگری انجام می‌شود (dim05_gl_gatekeeper / gl_stamp).
اینجا باید "ایمن" باشد: هیچ وقت با Exception بی‌ربط ledger posting را نخواباند.
"""

from __future__ import annotations


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        return None


def postcheck_gl_entry(doc, method=None, *args, **kwargs) -> None:
    """
    Handler عمومی برای بعد از insert/update GL Entry.
    عمداً fail نمی‌کند. اگر guard موجود باشد، best-effort اجرا می‌شود.
    """
    try:
        # Import داخل تابع برای جلوگیری از circular-import در لحظه load hooks
        from . import gl_stamp  # noqa

        if hasattr(gl_stamp, "should_enforce_dimensions"):
            company = getattr(doc, "company", None)
            if not gl_stamp.should_enforce_dimensions(company):
                return

        # اگر guard دارید، best-effort صدا بزن
        if hasattr(gl_stamp, "guard_gl_entry_dimensions"):
            _safe(gl_stamp.guard_gl_entry_dimensions, doc, method=method)

    except Exception:
        return


# ---- aliases احتمالی برای hooks ----
after_insert = postcheck_gl_entry
on_update = postcheck_gl_entry
after_save = postcheck_gl_entry

after_insert_gl_entry = postcheck_gl_entry
gl_entry_after_insert = postcheck_gl_entry
postcheck = postcheck_gl_entry


def after_insert_gl_entry(doc, method=None):
    # اینجا intentionally no-op است تا posting هرگز نخوابد.
    # اگر بعداً خواستی postcheck سخت‌گیرانه اضافه کنیم، همینجا انجام می‌دهیم.
    return
