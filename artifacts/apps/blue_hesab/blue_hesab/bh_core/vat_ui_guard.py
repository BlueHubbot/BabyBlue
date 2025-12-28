# apps/blue_hesab/blue_hesab/bh_core/vat_ui_guard.py
# VAT UI Guard (SAFE V2)
# - No client calls to vat_pipeline (no whitelist required)
# - Strict UI lock on taxes_and_charges: only BH VAT MIXED allowed
# - Auto-pick expected BH MIXED template via frappe.db.get_value (client) based on:
#   company + axis(INCL/EXCL) inferred from bh_vat_price_mode or current template.
# - Friendly Persian guidance

from __future__ import annotations

from typing import Any, Dict, Optional
import textwrap

import frappe


SCRIPT_NAME_SALES = "BH VAT UI Guard :: Sales Invoice"
SCRIPT_NAME_PURCHASE = "BH VAT UI Guard :: Purchase Invoice"

MARKER = "BH_VAT_UI_GUARD_V2_SAFE"


def _set_if_field(doc, fieldname: str, value: Any) -> None:
    try:
        if doc.meta.get_field(fieldname):
            doc.set(fieldname, value)
    except Exception:
        pass


def _pick_module_for_export() -> str:
    # Must match an existing "Module Def" or Client Script insert fails link validation
    candidates = [
        "Blue Hesab",
        "BlueHesab",
        "Accounts",
        "Selling",
        "Buying",
    ]
    for m in candidates:
        try:
            if frappe.db.exists("Module Def", m):
                return m
        except Exception:
            continue
    return "Accounts"


def _upsert_client_script(
    *,
    name: str,
    dt: str,
    view: str,
    script: str,
    enabled: int = 1,
    module: Optional[str] = None,
) -> Dict[str, Any]:
    module = module or _pick_module_for_export()

    if frappe.db.exists("Client Script", name):
        doc = frappe.get_doc("Client Script", name)
    else:
        doc = frappe.new_doc("Client Script")
        # Some setups have autoname=Prompt -> must force name
        doc.name = name

    # Common fieldnames across forks
    _set_if_field(doc, "dt", dt)
    _set_if_field(doc, "doctype", dt)
    _set_if_field(doc, "view", view)
    _set_if_field(doc, "enabled", int(enabled))
    _set_if_field(doc, "module", module)
    _set_if_field(doc, "script", script)

    # Some forks have script_type; harmless if missing
    _set_if_field(doc, "script_type", "Client")

    # Extra safety for mandatory in customized doctypes
    try:
        doc.flags.ignore_mandatory = True
    except Exception:
        pass

    doc.save(ignore_permissions=True)
    return {
        "name": doc.name,
        "dt": dt,
        "view": view,
        "enabled": int(getattr(doc, "enabled", enabled)),
        "module": module,
    }


_JS_TEMPLATE = textwrap.dedent(
    r"""
    // __MARKER__
    (() => {
      const MARKER = "__MARKER__";
      const BASE = "__BASE__";     // "BH VAT MIXED Sales" / "BH VAT MIXED Purchase"
      const DT = "__DT__";         // Sales Taxes... / Purchase Taxes...
      const TITLE = "قفل قانونی مالیات بر ارزش افزوده (VAT)";

      function norm(v) { return (v || "").toString().trim(); }

      function axisFromDoc(frm) {
        const pm = (frm.doc.bh_vat_price_mode || "").toString().toLowerCase().trim();
        if (pm.startsWith("incl")) return "INCL";
        if (pm.startsWith("excl")) return "EXCL";

        const tpl = norm(frm.doc.taxes_and_charges);
        if (tpl.includes("(INCL)")) return "INCL";
        if (tpl.includes("(EXCL)")) return "EXCL";

        return "EXCL";
      }

      function axisFa(axis) {
        return (axis === "INCL") ? "شامل مالیات (Inclusive)" : "بدون مالیات (Exclusive)";
      }

      function esc(s) {
        try { return frappe.utils.escape_html(s); }
        catch(e) { return (s || "").toString(); }
      }

      function isBhMixed(name) {
        const n = norm(name);
        return !!n && n.startsWith(BASE);
      }

      function hasAxis(name, axis) {
        const n = norm(name);
        if (!n) return true;
        return n.includes("(" + axis + ")");
      }

      function setQuery(frm) {
        // Even if we make field read-only, keep query sane (for power users / future changes)
        frm.set_query("taxes_and_charges", () => {
          const axis = axisFromDoc(frm);
          const filters = [];
          if (frm.doc.company) filters.push(["company", "=", frm.doc.company]);
          filters.push(["name", "like", `${BASE} (${axis})%`]);
          return { filters };
        });
      }

      async function inferExpected(frm) {
        const axis = axisFromDoc(frm);
        if (!frm.doc.company) return "";

        // SAFE: no custom python call; uses standard client get_value
        const filters = {
          company: frm.doc.company,
          name: ["like", `${BASE} (${axis})%`]
        };

        try {
          const r = await frappe.db.get_value(DT, filters, "name");
          const msg = r && r.message;
          const name = (msg && (msg.name || msg["name"])) || "";
          return name || "";
        } catch (e) {
          return "";
        }
      }

      function buildMsg(picked, expected, axis) {
        const pickedHtml = picked ? `<code>${esc(picked)}</code>` : "<i>(خالی)</i>";
        const expectedHtml = expected ? `<code>${esc(expected)}</code>` : "<i>(یافت نشد)</i>";

        return `
        <div style="line-height:1.95">
          <b>این فیلد «Taxes & Charges Template» قفل قانونی VAT است.</b><br>
          انتخاب فعلی شما: ${pickedHtml}<br><br>

          <b>چرا قفل است؟</b><br>
          چون در ایران، مالیات/عوارض باید مطابق قالب‌های استاندارد و قابل ردیابی محاسبه شود.
          انتخاب آزادِ Template باعث خطا در جمع مالیات، سند حسابداری، و خروجی‌های قانونی (اظهارنامه/مودیان) می‌شود.
          <hr>

          <b>چه کار کنید؟</b>
          <ol>
            <li>فیلد «نوع قیمت‌گذاری مالیات» را روی <b>${esc(axisFa(axis))}</b> تنظیم کنید.</li>
            <li>فاکتور را ذخیره کنید؛ سیستم قالب صحیح BH را خودکار اعمال می‌کند.</li>
            <li>اگر قالب خاص سازمانی لازم دارید، باید از مسیر تنظیمات BlueHesab به‌صورت کنترل‌شده تعریف شود (نه انتخاب آزاد داخل فاکتور).</li>
          </ol>

          <b>قالب صحیح پیشنهادی:</b> ${expectedHtml}
        </div>`;
      }

      let busy = false;

      async function enforce(frm, reason) {
        if (busy) return;
        busy = true;

        try {
          if (!frm || !frm.doc) return;
          if (!frm.doc.company) return;

          // hard UI lock
          try { frm.set_df_property("taxes_and_charges", "read_only", 1); } catch(e) {}
          try { frm.toggle_enable && frm.toggle_enable("taxes_and_charges", false); } catch(e) {}

          setQuery(frm);

          const axis = axisFromDoc(frm);
          const cur = norm(frm.doc.taxes_and_charges);

          const ok = (!cur) || (isBhMixed(cur) && hasAxis(cur, axis));

          if (!ok) {
            const expected = await inferExpected(frm);

            frappe.msgprint({
              title: TITLE,
              indicator: "red",
              message: buildMsg(cur, expected, axis)
            });

            // soft auto-revert in UI
            if (expected) {
              await frm.set_value("taxes_and_charges", expected);
            } else {
              await frm.set_value("taxes_and_charges", "");
            }
            return;
          }

          // if empty -> auto-fill
          if (!cur) {
            const expected = await inferExpected(frm);
            if (expected) await frm.set_value("taxes_and_charges", expected);
          }
        } finally {
          busy = false;
        }
      }

      frappe.ui.form.on("__DOCTYPE__", {
        onload(frm) { enforce(frm, "onload"); },
        refresh(frm) { enforce(frm, "refresh"); },
        company(frm) { enforce(frm, "company"); },
        bh_vat_price_mode(frm) { enforce(frm, "price_mode"); },
        taxes_and_charges(frm) { enforce(frm, "template"); },
        validate(frm) { enforce(frm, "validate"); }
      });
    })();
    """
).strip()


def _make_client_script(*, doctype: str, base: str, dt: str) -> str:
    s = _JS_TEMPLATE
    s = s.replace("__MARKER__", MARKER)
    s = s.replace("__BASE__", base)
    s = s.replace("__DT__", dt)
    s = s.replace("__DOCTYPE__", doctype)
    return s


@frappe.whitelist()
def install_vat_ui_guard() -> Dict[str, Any]:
    module = _pick_module_for_export()

    sales_script = _make_client_script(
        doctype="Sales Invoice",
        base="BH VAT MIXED Sales",
        dt="Sales Taxes and Charges Template",
    )
    purchase_script = _make_client_script(
        doctype="Purchase Invoice",
        base="BH VAT MIXED Purchase",
        dt="Purchase Taxes and Charges Template",
    )

    out: Dict[str, Any] = {"module": module}
    out["sales"] = _upsert_client_script(
        name=SCRIPT_NAME_SALES,
        dt="Sales Invoice",
        view="Form",
        script=sales_script,
        enabled=1,
        module=module,
    )
    out["purchase"] = _upsert_client_script(
        name=SCRIPT_NAME_PURCHASE,
        dt="Purchase Invoice",
        view="Form",
        script=purchase_script,
        enabled=1,
        module=module,
    )

    frappe.db.commit()
    return out


# bench helper (no whitelist needed)
def audit_vat_ui_guard() -> Dict[str, Any]:
    rows = []
    for n in (SCRIPT_NAME_SALES, SCRIPT_NAME_PURCHASE):
        s = frappe.db.get_value("Client Script", n, "script") or ""
        rows.append(
            {
                "name": n,
                "has_marker_v2": (MARKER in s),
                "uses_db_get_value": ("frappe.db.get_value" in s),
                "calls_vat_pipeline": ("vat_pipeline.debug_infer_mixed_template" in s),
                "len": len(s),
            }
        )
    return {"ok": True, "rows": rows}
