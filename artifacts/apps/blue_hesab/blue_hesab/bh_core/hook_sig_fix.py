from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime
import py_compile
import inspect

import frappe


def _as_list(v):
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return list(v)
    return [v]


def _map_pyc_to_py(p: Path) -> Path:
    if p.suffix != ".pyc":
        return p
    if p.parent.name == "__pycache__":
        base = p.name.split(".cpython-")[0]
        cand = p.parent.parent / (base + ".py")
        if cand.exists():
            return cand
    cand2 = Path(str(p)).with_suffix(".py")
    if cand2.exists():
        return cand2
    return p


def patch_apply_gl_dimensions_hook() -> dict:
    """
    Finds the hooked handler(s) that resolve to apply_gl_dimensions_from_invoice and
    forces signature to: (doc, method=None, *args, **kwargs)
    Only patches source files that are actually referenced by hooks.
    """

    doc_events = frappe.get_hooks("doc_events") or {}

    # Collect handler paths from Sales/Purchase Invoice on_submit
    handler_paths: list[str] = []
    for dt in ("Sales Invoice", "Purchase Invoice"):
        ev = (doc_events.get(dt) or {})
        handlers = _as_list(ev.get("on_submit"))
        for h in handlers:
            if isinstance(h, str) and "apply_gl_dimensions_from_invoice" in h:
                handler_paths.append(h)

    handler_paths = sorted(set(handler_paths))
    if not handler_paths:
        frappe.throw("apply_gl_dimensions_from_invoice handler not found in doc_events for Sales/Purchase Invoice on_submit")

    targets = []
    uniq_files: list[str] = []
    seen = set()

    for h in handler_paths:
        try:
            fn = frappe.get_attr(h)
            src = inspect.getsourcefile(fn) or getattr(getattr(fn, "__code__", None), "co_filename", None)
        except Exception as e:
            targets.append({"handler": h, "error": str(e), "file": None})
            continue

        targets.append({"handler": h, "file": src})

        if src and src not in seen:
            seen.add(src)
            uniq_files.append(src)

    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    # match the def line
    pat = re.compile(r"(?m)^(?P<indent>\s*)def\s+apply_gl_dimensions_from_invoice\s*\([^)]*\)\s*:")

    patched = []
    skipped = []
    errors = []

    for cf in uniq_files:
        try:
            p = _map_pyc_to_py(Path(cf))
            if not p.exists():
                errors.append({"file": cf, "error": f"source_not_found -> {str(p)}"})
                continue

            txt = p.read_text(encoding="utf-8", errors="replace")
            m = pat.search(txt)
            if not m:
                errors.append({"file": str(p), "error": "def_not_found"})
                continue

            new_def = f"{m.group('indent')}def apply_gl_dimensions_from_invoice(doc, method=None, *args, **kwargs):"
            txt2 = pat.sub(new_def, txt, count=1)

            if txt2 == txt:
                skipped.append(str(p))
                continue

            bk = p.with_name(p.name + f".bak.hook_sig_fix.{ts}")
            bk.write_text(txt, encoding="utf-8")
            p.write_text(txt2, encoding="utf-8")

            py_compile.compile(str(p), doraise=True)
            patched.append({"file": str(p), "backup": str(bk)})

        except Exception as e:
            errors.append({"file": cf, "error": str(e)})

    return {"targets": targets, "patched": patched, "skipped": skipped, "errors": errors}
