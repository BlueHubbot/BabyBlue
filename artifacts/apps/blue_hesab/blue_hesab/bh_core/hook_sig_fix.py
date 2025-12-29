from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime
import py_compile
import frappe


def _as_list(v):
    if not v:
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
    doc_events = frappe.get_hooks("doc_events") or {}
    targets = []
    for dt in ("Sales Invoice", "Purchase Invoice"):
        handlers = _as_list((doc_events.get(dt) or {}).get("on_submit"))
        for h in handlers:
            try:
                fn = frappe.get_attr(h)
            except Exception:
                continue
            if callable(fn) and getattr(fn, "__name__", "") == "apply_gl_dimensions_from_invoice":
                cf = getattr(getattr(fn, "__code__", None), "co_filename", None)
                targets.append({"doctype": dt, "handler": h, "co_filename": cf})

    if not targets:
        frappe.throw("apply_gl_dimensions_from_invoice hook not found on Sales/Purchase Invoice on_submit")

    uniq_files = []
    seen = set()
    for t in targets:
        cf = t.get("co_filename") or ""
        if cf and cf not in seen:
            seen.add(cf)
            uniq_files.append(cf)

    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    pat = re.compile(r"(?m)^(?P<indent>\\s*)def\\s+apply_gl_dimensions_from_invoice\\s*\\((?P<args>[^)]*)\\)\\s*:")

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

            args = (m.group("args") or "").strip()
            # already ok?
            if re.search(r"(^|,)\\s*method\\s*(=|,|$)", args):
                skipped.append(str(p))
                continue

            parts = [a.strip() for a in args.split(",")] if args else []
            if not parts:
                new_args = "doc, method=None"
            else:
                # insert after first positional
                if parts[0] == "*":
                    parts.insert(1, "method=None")
                else:
                    parts.insert(1, "method=None")
                new_args = ", ".join([x for x in parts if x])

            new_def = f"{m.group(indent)}def apply_gl_dimensions_from_invoice({new_args}):"
            txt2 = pat.sub(new_def, txt, count=1)

            bk = p.with_name(p.name + f".bak.hook_sig_fix.{ts}")
            bk.write_text(txt, encoding="utf-8")
            p.write_text(txt2, encoding="utf-8")
            py_compile.compile(str(p), doraise=True)

            patched.append({"file": str(p), "backup": str(bk)})
        except Exception as e:
            errors.append({"file": cf, "error": str(e)})

    return {"targets": targets, "patched": patched, "skipped": skipped, "errors": errors}
