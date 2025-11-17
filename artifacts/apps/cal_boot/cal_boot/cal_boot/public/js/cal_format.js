// CAL::Desk Jalali V7 — Global format hooks for Date/Datetime (UI-only)
(() => {
  if (window.__CAL_FORMAT_V7) return; window.__CAL_FORMAT_V7 = 1;

  const isJalali = () => (localStorage.getItem("CAL_MODE") || "jalali") === "jalali";
  const havePD   = () => !!window.persianDate;

  const toDate = (v, withTime) => {
    if (!v) return null;
    if (typeof v === "string" && /^\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?$/.test(v)) {
      return new Date(v.replace(" ", "T"));
    }
    if (typeof v === "string") return new Date(v.replace(" ", "T"));
    if (v instanceof Date) return v;
    return null;
  };

  const fmtJ = (v, type) => {
    if (!havePD()) return v ?? "";
    const d = toDate(v, type === "Datetime");
    if (!d || Number.isNaN(+d)) return v ?? "";
    const pd = new window.persianDate(d);
    // نمایش کوتاه و پایدار؛ دادهٔ ذخیره‌شونده تغییر نمی‌کند
    return type === "Datetime" ? pd.format("YYYY/MM/DD HH:mm") : pd.format("YYYY/MM/DD");
  };

  // 1) Patch frappe.format_value
  if (window.frappe && typeof frappe.format_value === "function" && !frappe.__CAL_OV_FORMAT_VALUE) {
    const orig = frappe.format_value;
    frappe.format_value = function (value, df, opts, doc) {
      try {
        const ft = (df && df.fieldtype) || (opts && opts.fieldtype) || "";
        if (isJalali() && (ft === "Date" || ft === "Datetime")) return fmtJ(value, ft);
      } catch (e) { /* no-op */ }
      return orig.call(this, value, df, opts, doc);
    };
    frappe.__CAL_OV_FORMAT_VALUE = 1;
  }

  // 2) Patch frappe.format_date
  if (window.frappe && typeof frappe.format_date === "function" && !frappe.__CAL_OV_FORMAT_DATE) {
    const orig = frappe.format_date;
    frappe.format_date = function (date_str) {
      try { if (isJalali()) return fmtJ(date_str, "Date"); } catch (e) { /* no-op */ }
      return orig.apply(this, arguments);
    };
    frappe.__CAL_OV_FORMAT_DATE = 1;
  }

  // 3) Patch frappe.format (fallback در برخی مسیرها)
  if (window.frappe && typeof frappe.format === "function" && !frappe.__CAL_OV_FORMAT) {
    const orig = frappe.format;
    frappe.format = function (value, df, opts, doc) {
      try {
        const ft = (df && df.fieldtype) || "";
        if (isJalali() && (ft === "Date" || ft === "Datetime")) return fmtJ(value, ft);
      } catch (e) { /* no-op */ }
      return orig.call(this, value, df, opts, doc);
    };
    frappe.__CAL_OV_FORMAT = 1;
  }

  window.__CAL_FORMAT_ACTIVE = 1;
})();
