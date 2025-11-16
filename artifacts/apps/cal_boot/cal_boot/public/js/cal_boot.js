/*!
 * CAL::BOOT — Unified Jalali UI Layer for ERPNext/Frappe
 * Version: 27.0 (clean)
 * - بایند کردن تاریخ شمسی روی Date / Datetime
 * - مودال دو-کلیکه برای DateRange
 */

(function () {
  "use strict";

  // ================== 1) وضعیت کلی و ابزارها ==================
  var CAL = (window.CAL = window.CAL || {});
  var MODE_KEY = "__cal_mode__";

  // حالت فعال (jalali / gregorian)
  CAL.getMode =
    CAL.getMode ||
    function () {
      try {
        return localStorage.getItem(MODE_KEY) || "gregorian";
      } catch (e) {
        return "gregorian";
      }
    };

  CAL.isJalali =
    CAL.isJalali ||
    function () {
      return CAL.getMode() === "jalali";
    };

  CAL.setMode =
    CAL.setMode ||
    function (m) {
      try {
        localStorage.setItem(MODE_KEY, m);
      } catch (e) {}
    };

  function pad(n) {
    return ("0" + n).slice(-2);
  }
  function toYMD(d) {
    return (
      d.getFullYear() +
      "-" +
      pad(d.getMonth() + 1) +
      "-" +
      pad(d.getDate())
    );
  }
  function toJalaliString(gDate) {
    // gDate: Date
    return new persianDate(gDate).format("YYYY/MM/DD");
  }

  // ================== 2) لود لایبرری‌ها ==================
  function addCss(href) {
    if (document.querySelector('link[href="' + href + '"]')) return;
    var l = document.createElement("link");
    l.rel = "stylesheet";
    l.href = href;
    document.head.appendChild(l);
  }

  function addJs(src) {
    return new Promise(function (resolve, reject) {
      if (document.querySelector('script[src="' + src + '"]')) {
        return resolve();
      }
      var s = document.createElement("script");
      s.src = src;
      s.onload = function () {
        resolve();
      };
      s.onerror = function (e) {
        reject(e);
      };
      document.head.appendChild(s);
    });
  }

  function addJsWithFallback(localUrl, cdnUrl) {
    return addJs(localUrl).catch(function (e) {
      console.warn("CAL: local JS failed, trying CDN.", e);
      return addJs(cdnUrl);
    });
  }

  var PD_LOCAL = "/files/persian-date.min.js";
  var PDP_LOCAL = "/files/persian-datepicker.min.js";
  var CSS_LOCAL = "/files/persian-datepicker.min.css";

  var PD_CDN =
    "https://unpkg.com/persian-date@1.1.0/dist/persian-date.min.js";
  var PDP_CDN =
    "https://unpkg.com/persian-datepicker@1.2.0/dist/js/persian-datepicker.min.js";
  var CSS_CDN =
    "https://unpkg.com/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css";

  function ensureLibs() {
    // اگه حالت جلالی نباشه لازم نیست چیزی لود کنیم
    if (!CAL.isJalali()) return Promise.resolve();

    // هم لوکال رو بزن، هم CDN رو اضافه کن که اگه استایل لوکال لود نشد، CDN باشه
    addCss(CSS_LOCAL);
    addCss(CSS_CDN);

    return addJsWithFallback(PD_LOCAL, PD_CDN)
      .then(function () {
        return addJsWithFallback(PDP_LOCAL, PDP_CDN);
      })
      .then(function () {
        window.__CAL_BOOT_READY__ = 1;
        console.log("CAL v27: Jalali libs loaded.");
      });
  }

  // ================== 3) فیلدهای Date / Datetime ==================
  function bindOne(input) {
    if (!CAL.isJalali()) return;
    if (input.__jalaliBound) return;
    if (!window.__CAL_BOOT_READY__) return;

    var jq = window.jQuery || window.$;
    if (!jq || !jq.fn || !jq.fn.pDatepicker) return;

    // از خود input بخون، نه از $
    var ft = input.getAttribute("data-fieldtype") || "";
    var isDatetime = ft === "Datetime";

    try {
      jq(input).pDatepicker({
        calendarType: "persian",
        calendar: { persian: { locale: "fa" } },
        initialValueType: "gregorian",
        format: isDatetime ? "YYYY/MM/DD HH:mm" : "YYYY/MM/DD",
        autoClose: true,
        timePicker: isDatetime ? { enabled: true } : { enabled: false },
        onSelect: function (unix) {
          try {
            // unix → persianDate → Date
            var g = new persianDate(unix).toDate();
            var gYMD = toYMD(g); // yyyy-mm-dd
            input.value = gYMD;

            // برای دیدن مقدار شمسی در placeholder
            input.setAttribute("placeholder", toJalaliString(g));

            // تریگر Frappe
            jq(input).trigger("change");
          } catch (e) {}
        },
      });

      input.__jalaliBound = true;
    } catch (e) {
      console.warn("CAL: bindOne failed", e);
    }
  }

  // ================== 4) مودال بازه تاریخ ==================
  function openCalRangeModal(inputElement, onSelectCallback) {
    var jq = window.jQuery || window.$;
    if (!jq || !jq.fn || !jq.fn.pDatepicker) return;

    // برای اینکه دو بار باز کنیم id یکتا بسازیم
    var modalId = "cal-range-modal-" + Date.now();

    var $modal = jq(
      '<div class="modal fade" id="' +
        modalId +
        '" tabindex="-1" role="dialog">' +
        '<div class="modal-dialog modal-sm" role="document">' +
        '<div class="modal-content">' +
        '<div class="modal-header">' +
        '<h5 class="modal-title">انتخاب بازه تاریخ</h5>' +
        '<button type="button" class="close" data-dismiss="modal">&times;</button>' +
        "</div>" +
        '<div class="modal-body">' +
        '<p class="text-center" id="' +
        modalId +
        '-status" style="font-weight:bold;">گام ۱: تاریخ شروع را انتخاب کنید</p>' +
        '<div id="' +
        modalId +
        '-container"></div>' +
        '<div style="margin-top: 10px; display: flex; justify-content: space-between;">' +
        '<span id="' +
        modalId +
        '-from">—</span>' +
        '<span id="' +
        modalId +
        '-to">—</span>' +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>"
    ).appendTo("body");

    var $status = jq("#" + modalId + "-status");
    var $from = jq("#" + modalId + "-from");
    var $to = jq("#" + modalId + "-to");

    var step = 1;
    var startDate = null;
    var endDate = null;

    jq("#" + modalId + "-container").pDatepicker({
      inline: true,
      calendarType: "persian",
      calendar: { persian: { locale: "fa" } },
      format: "YYYY/MM/DD",
      onSelect: function (unix) {
        var selectedJ = toJalaliString(new Date(unix));

        if (step === 1) {
          // انتخاب شروع
          startDate = unix;
          $from.text(selectedJ);
          $to.text("—");
          $status.text("گام ۲: تاریخ پایان را انتخاب کنید");
          step = 2;
        } else {
          // انتخاب پایان
          endDate = unix;

          // اگر برعکس انتخاب شد جابجا کن
          if (endDate < startDate) {
            var tmp = startDate;
            startDate = endDate;
            endDate = tmp;
          }

          var gFrom = toYMD(new Date(startDate));
          var gTo = toYMD(new Date(endDate));

          $from.text(toJalaliString(new Date(startDate)));
          $to.text(toJalaliString(new Date(endDate)));

          if (typeof onSelectCallback === "function") {
            onSelectCallback(gFrom, gTo);
          }

          jq("#" + modalId).modal("hide");
        }
      },
    });

    $modal.on("hidden.bs.modal", function () {
      $modal.remove();
    });

    jq("#" + modalId).modal("show");
  }

  // ================== 5) دزدیدن DateRange ==================
  function bindRangeHijack(input) {
    if (!CAL.isJalali()) return;
    if (input.__jalaliBound) return;
    if (!window.__CAL_BOOT_READY__) return;

    var jq = window.jQuery || window.$;
    if (!jq) return;

    var $input = jq(input);

    // اگه فلت‌پیکر بود، خرابش کن
    if ($input.data("flatpickr")) {
      try {
        $input.data("flatpickr").destroy();
      } catch (e) {}
    }

    $input.on("click focus", function (e) {
      e.preventDefault();
      e.stopImmediatePropagation();

      openCalRangeModal(input, function (gFrom, gTo) {
        var rangeString = gFrom + " to " + gTo;

        // تلاش ۱: اگه توی فیلتر گزارش بوده
        try {
          if (
            window.frappe &&
            frappe.ui &&
            frappe.ui.Filter &&
            typeof frappe.ui.Filter.get_filters === "function"
          ) {
            var filters = frappe.ui.Filter.get_filters() || [];
            var match = filters.find(function (f) {
              return f.input === input;
            });
            if (match && typeof match.set_value === "function") {
              console.log(
                "CAL: setting range on Filter control (List/Report)."
              );
              match.set_value([gFrom, gTo]);
              return;
            }
          }
        } catch (err) {
          console.warn(
            "CAL: filter API not available, falling back to direct input.",
            err && err.message
          );
        }

        // تلاش ۲: ست کردن مستقیم روی input (مثل داشبورد)
        input.value = rangeString;
        $input.trigger("change");

        // اگه داخل یه modal دیگه بود، ببند
        var parentModal = $input.closest(".modal");
        if (parentModal && parentModal.length) {
          parentModal.modal("hide");
        }
      });

      return false;
    });

    input.__jalaliBound = true;
  }

  // ================== 6) اسکنر ==================
  function scan(root) {
    if (!CAL.isJalali()) return;
    if (!window.__CAL_BOOT_READY__) return;

    var jq = window.jQuery || window.$;
    if (!jq) return;

    // Date / Datetime
    jq(
      'input[data-fieldtype="Date"], input[data-fieldtype="Datetime"]',
      root
    ).each(function () {
      bindOne(this);
    });

    // DateRange
    jq('input[data-fieldtype="DateRange"]', root).each(function () {
      bindRangeHijack(this);
    });
  }

  // ================== 7) مخفی کردن flatpickr ==================
  function disableFlatpickrIfJalali() {
    if (!CAL.isJalali()) return;
    if (document.getElementById("cal-disable-flatpickr")) return;
    var st = document.createElement("style");
    st.id = "cal-disable-flatpickr";
    st.textContent =
      "#wrapper body .flatpickr-calendar, body .flatpickr-calendar { display:none!important; }";
    document.head.appendChild(st);
    console.log("CAL: flatpickr hidden.");
  }

  // ================== 8) بوت اصلی ==================
  function boot() {
    ensureLibs().then(function () {
      disableFlatpickrIfJalali();
      scan(document);

      // برای محتواهای Ajax
      var mo = new MutationObserver(function (muts) {
        muts.forEach(function (m) {
          (m.addedNodes || []).forEach(function (n) {
            if (n && n.nodeType === 1) {
              scan(n);
            }
          });
        });
      });
      mo.observe(document.documentElement, {
        childList: true,
        subtree: true,
      });
    });
  }

  // ================== 9) هوک فرم (اختیاری) ==================
  function ensureBtn(frm) {
    // اگه بعداً خواستی دکمه تغییر تقویم بذاری اینجا بذار
  }

  // اگه داخل فرم هستیم
  if (window.cur_frm && window.frappe && window.frappe.ui && frappe.ui.form) {
    frappe.ui.form.on(cur_frm.doctype, {
      refresh: function (frm) {
        ensureBtn(frm);
        boot();
      },
      onload_post_render: function (frm) {
        ensureBtn(frm);
        boot();
      },
    });
  } else {
    // صفحه desk عادی
    document.addEventListener("DOMContentLoaded", boot);
  }
})();
