// apps/cal_boot/cal_boot/public/js/cal_lite_trap.js
(function () {
  "use strict";

  var w = window;
  var d = document;

  var CAL = w.CAL = w.CAL || {};
  var LIBS_KEY = "__CAL_LIBS_LOADED__";

  function alreadyLoaded() {
    return (
      w[LIBS_KEY] ||
      (w.persianDate &&
        w.jQuery &&
        (w.jQuery.fn.persianDatepicker || w.jQuery.fn.pDatepicker))
    );
  }

  function loadCss(href) {
    return new Promise(function (resolve, reject) {
      if (!href) return resolve();
      if (d.querySelector('link[data-cal-href="' + href + '"]')) {
        return resolve();
      }
      var link = d.createElement("link");
      link.rel = "stylesheet";
      link.type = "text/css";
      link.href = href;
      link.setAttribute("data-cal-href", href);
      link.onload = function () { resolve(); };
      link.onerror = function () { console.error("[CAL] CSS load failed:", href); resolve(); };
      d.head.appendChild(link);
    });
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (!src) return resolve();
      if (d.querySelector('script[data-cal-src="' + src + '"]')) {
        return resolve();
      }
      var s = d.createElement("script");
      s.src = src;
      s.async = false;
      s.setAttribute("data-cal-src", src);
      s.onload = function () { resolve(); };
      s.onerror = function () { console.error("[CAL] JS load failed:", src); resolve(); };
      d.head.appendChild(s);
    });
  }

  CAL.ensureLibs = function ensureLibs() {
    if (alreadyLoaded()) {
      w[LIBS_KEY] = true;
      return Promise.resolve();
    }

    // مسیر فایل‌هایی که خودت در /files گذاشتی
    var base = "/files";

    var cssHref = base + "/persian-datepicker.min.css";
    var jsDate = base + "/persian-date.min.js";
    var jsPicker = base + "/persian-datepicker.min.js";

    return loadCss(cssHref)
      .then(function () { return loadScript(jsDate); })
      .then(function () { return loadScript(jsPicker); })
      .then(function () {
        if (!alreadyLoaded()) {
          console.error("[CAL] persian-date / persian-datepicker not available after load.");
        } else {
          w[LIBS_KEY] = true;
        }
      });
  };

  w.__CAL_LITE_TRAP_V13 = 1;
})();
