// apps/cal_boot/cal_boot/public/js/blue_jalali_range.js
// BlueJalaliRangePicker – انتخاب بازه‌ی جلالی روی یک تقویم، UI همسان BlueJalali (بدون hover رِنج)

(function (w, d) {
  "use strict";

  if (!w.console) {
    w.console = { log: function () {}, error: function () {}, warn: function () {} };
  }

  var DAY_MS = 24 * 60 * 60 * 1000;

  var MONTH_NAMES_FA = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
  ];

  var WEEKDAY_LABELS = ["ش", "ی", "د", "س", "چ", "پ", "ج"];

  // ---------- توابع کمکی تاریخ ----------

  function jalaliFromUnix(unix) {
    if (!w.persianDate) throw new Error("persianDate not loaded");
    var p = new w.persianDate(unix).toCalendar("persian").toLocale("en");
    var parts = p.format("YYYY-MM-DD").split("-");
    return {
      y: parseInt(parts[0], 10),
      m: parseInt(parts[1], 10),
      d: parseInt(parts[2], 10),
      formatted: parts.join("-")
    };
  }

  function gregorianFromUnix(unix) {
    if (!w.persianDate) throw new Error("persianDate not loaded");
    return new w.persianDate(unix)
      .toCalendar("gregorian")
      .toLocale("en")
      .format("YYYY-MM-DD");
  }

  function parseGregDate(str) {
    if (!str || !/^\d{4}-\d{2}-\d{2}$/.test(str)) return null;
    var p = str.split("-");
    var y = parseInt(p[0], 10);
    var m = parseInt(p[1], 10) - 1;
    var d0 = parseInt(p[2], 10);
    var dt = new Date(y, m, d0, 12, 0, 0, 0);
    var t = dt.getTime();
    return isFinite(t) ? t : null;
  }

  function jalaliMonthDays(y, m) {
    if (m <= 6) return 31;
    if (m <= 11) return 30;
    var r = y % 33;
    return (r === 1 || r === 5 || r === 9 || r === 13 || r === 17 ||
      r === 22 || r === 26 || r === 30) ? 30 : 29;
  }

  function jalaliToUnix(y, m, d) {
    if (!w.persianDate) throw new Error("persianDate not loaded");
    var day = Math.max(1, Math.min(d, jalaliMonthDays(y, m)));
    var p = new w.persianDate([y, m, day]).toLocale("en");
    var jsDate = p.toDate();
    return jsDate.getTime();
  }

  function makeEl(tag, className, text) {
    var el = d.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  }

  function startOfDay(unix) {
    var j = jalaliFromUnix(unix);
    return jalaliToUnix(j.y, j.m, j.d);
  }

  function clampRange(fromUnix, toUnix) {
    if (fromUnix != null && toUnix != null && toUnix < fromUnix) {
      var tmp = fromUnix;
      fromUnix = toUnix;
      toUnix = tmp;
    }
    return { fromUnix: fromUnix, toUnix: toUnix };
  }

  function sameJDate(u1, u2) {
    if (u1 == null || u2 == null) return false;
    var a = jalaliFromUnix(u1);
    var b = jalaliFromUnix(u2);
    return a.y === b.y && a.m === b.m && a.d === b.d;
  }

  // ---------- سازنده ----------

  function BlueJalaliRangePicker(opts) {
    this.opts = opts || {};
    this.root = null;
    this.titleEl = null;
    this.daysGridEl = null;

    this.anchor = null;
    this.isOpen = false;

    this.viewUnix = null;   // ماه در حال نمایش
    this.fromUnix = null;   // ابتدای بازه
    this.toUnix = null;     // انتهای بازه
    this.phase = "from";    // "from" یا "to"

    this._docHandler = null;
  }

  // ---------- ساخت DOM ----------

  BlueJalaliRangePicker.prototype._ensureDom = function () {
    if (this.root && d.body.contains(this.root)) return;

    var root = makeEl("div", "bjp-root");
    root.id = "blue-jalali-range-root";
    root.setAttribute("dir", "rtl");

    var header = makeEl("div", "bjp-nav");
    var prev = makeEl("button", "bjp-nav-action", "›");
    prev.type = "button";
    var title = makeEl("div", "bjp-title", "");
    var next = makeEl("button", "bjp-nav-action", "‹");
    next.type = "button";

    header.appendChild(prev);
    header.appendChild(title);
    header.appendChild(next);

    var content = makeEl("div", "bjp-content");

    var daysView = makeEl("div", "bjp-view bjp-days active");
    var weekRow = makeEl("div", "bjp-week-row");
    for (var i = 0; i < 7; i++) {
      weekRow.appendChild(makeEl("div", "bjp-weekday", WEEKDAY_LABELS[i]));
    }
    var daysGrid = makeEl("div", "bjp-grid");
    daysView.appendChild(weekRow);
    daysView.appendChild(daysGrid);

    content.appendChild(daysView);
    root.appendChild(header);
    root.appendChild(content);
    d.body.appendChild(root);

    this.root = root;
    this.titleEl = title;
    this.daysGridEl = daysGrid;

    var self = this;

    prev.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      self._shiftMonth(1);
    });

    next.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      self._shiftMonth(-1);
    });

    title.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      // در نسخه رنج کار خاصی روی title نمی‌کنیم
    });
  };

  // ---------- جابه‌جایی ماه ----------

  BlueJalaliRangePicker.prototype._shiftMonth = function (delta) {
    if (!this.viewUnix) {
      this.viewUnix = this.toUnix || this.fromUnix || Date.now();
    }
    var v = jalaliFromUnix(this.viewUnix);

    var y = v.y;
    var m = v.m;
    var d0 = v.d;

    m += delta;
    while (m < 1) { m += 12; y -= 1; }
    while (m > 12) { m -= 12; y += 1; }

    var maxDay = jalaliMonthDays(y, m);
    if (d0 > maxDay) d0 = maxDay;

    this.viewUnix = jalaliToUnix(y, m, d0);
    this._renderDays();
  };

  // ---------- open ----------

  BlueJalaliRangePicker.prototype.open = function (anchorEl, fromGreg, toGreg) {
    var self = this;
    if (!anchorEl) return;

    function reallyOpen() {
      try {
        jalaliFromUnix(Date.now());
      } catch (e) {
        console.error("[BlueJalaliRangePicker] persianDate not ready:", e);
        return;
      }

      // اطمینان از تزریق CSS BlueJalali (با ساخت یک نمونه موقت از تک‌تاریخ)
      if (w.BlueJalaliPicker && w.BlueJalaliPicker.prototype && w.BlueJalaliPicker.prototype._ensureDom) {
        try {
          new w.BlueJalaliPicker({})._ensureDom();
        } catch (e) {}
      }

      self._ensureDom();
      self.anchor = anchorEl;

      // اگر input از قبل مقدار دارد → به‌عنوان رنج اولیه در نظر بگیر
      var fromUnix = parseGregDate(fromGreg);
      var toUnix = parseGregDate(toGreg);

      if (fromUnix && toUnix) {
        var c0 = clampRange(fromUnix, toUnix);
        self.fromUnix = startOfDay(c0.fromUnix);
        self.toUnix = startOfDay(c0.toUnix);
        self.phase = "from";   // کلیک بعدی یعنی شروع رنج جدید
      } else {
        self.fromUnix = null;
        self.toUnix = null;
        self.phase = "from";
      }

      if (self.toUnix) {
        self.viewUnix = self.toUnix;
      } else if (self.fromUnix) {
        self.viewUnix = self.fromUnix;
      } else {
        self.viewUnix = Date.now();
      }

      self.root.style.visibility = "hidden";
      self.root.style.display = "block";

      self._renderDays();
      self._position();

      self.root.style.visibility = "visible";
      self.isOpen = true;

      if (self._docHandler) {
        d.removeEventListener("mousedown", self._docHandler, true);
      }
      self._docHandler = function (ev) {
        if (!self.isOpen) return;
        if (!self.root.contains(ev.target) && ev.target !== self.anchor) {
          self.close();
        }
      };
      d.addEventListener("mousedown", self._docHandler, true);
    }

    if (w.persianDate) {
      reallyOpen();
      return;
    }
    if (w.CAL && typeof w.CAL.ensureLibs === "function") {
      w.CAL.ensureLibs().then(reallyOpen).catch(function (err) {
        console.error("[BlueJalaliRangePicker] CAL.ensureLibs failed:", err);
      });
    }
  };

  // ---------- close ----------

  BlueJalaliRangePicker.prototype.close = function () {
    if (!this.isOpen) return;
    this.isOpen = false;
    if (this.root) this.root.style.display = "none";
    if (this._docHandler) {
      d.removeEventListener("mousedown", this._docHandler, true);
      this._docHandler = null;
    }
    this.anchor = null;
  };

  // ---------- رندر روزها ----------

  BlueJalaliRangePicker.prototype._renderDays = function () {
    if (!this.daysGridEl) return;

    if (!this.viewUnix) {
      this.viewUnix = this.toUnix || this.fromUnix || Date.now();
    }

    var viewJ = jalaliFromUnix(this.viewUnix);
    var todayJ = jalaliFromUnix(Date.now());

    this.titleEl.innerHTML =
      MONTH_NAMES_FA[viewJ.m - 1] + '<span>' + viewJ.y + "</span>";

    var firstUnix = this.viewUnix - (viewJ.d - 1) * DAY_MS;
    var gDay = new Date(firstUnix).getDay();
    var colIndex = (gDay + 1) % 7;
    var startUnix = firstUnix - colIndex * DAY_MS;

    while (this.daysGridEl.firstChild) {
      this.daysGridEl.removeChild(this.daysGridEl.firstChild);
    }

    var currentMonthDays = jalaliMonthDays(viewJ.y, viewJ.m);
    var lastDayOfMonthUnix = firstUnix + (currentMonthDays - 1) * DAY_MS;
    var lastDayIndex = Math.floor((lastDayOfMonthUnix - startUnix) / DAY_MS);
    var maxCells = lastDayIndex < 35 ? 35 : 42;

    var rangeFrom = this.fromUnix != null ? startOfDay(this.fromUnix) : null;
    var rangeTo = this.toUnix != null ? startOfDay(this.toUnix) : null;

    var self = this;

    for (var i = 0; i < maxCells; i++) {
      (function (cellUnix) {
        var j = jalaliFromUnix(cellUnix);
        var inMonth = j.m === viewJ.m && j.y === viewJ.y;

        var btn = makeEl("div", "bjp-cell bjp-day", String(j.d));

        if (!inMonth) {
          btn.classList.add("bjp-day-outside");
        }

        if (j.y === todayJ.y && j.m === todayJ.m && j.d === todayJ.d) {
          btn.classList.add("bjp-day-today");
        }

        var inRange = false;
        var isFrom = false;
        var isTo = false;

        if (rangeFrom != null && rangeTo != null) {
          var c = clampRange(rangeFrom, rangeTo);
          var dayStart = startOfDay(cellUnix);
          if (dayStart >= c.fromUnix && dayStart <= c.toUnix) {
            inRange = true;
          }
        }

        if (rangeFrom != null && sameJDate(cellUnix, rangeFrom)) {
          isFrom = true;
        }
        if (rangeTo != null && sameJDate(cellUnix, rangeTo)) {
          isTo = true;
        }

        if (inRange) btn.classList.add("bjp-in-range");
        if (isFrom) btn.classList.add("bjp-range-from");
        if (isTo) btn.classList.add("bjp-range-to");
        if (isFrom || isTo) btn.classList.add("bjp-selected");

        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          self._handleDayClick(cellUnix);
        });

        self.daysGridEl.appendChild(btn);
      })(startUnix + i * DAY_MS);
    }
  };

  // ---------- انتخاب روز (from/to) ----------

  BlueJalaliRangePicker.prototype._handleDayClick = function (cellUnix) {
    var day = startOfDay(cellUnix);

    if (this.phase === "from") {
      // کلیک اول: شروع بازه
      this.fromUnix = day;
      this.toUnix = null;
      this.phase = "to";
      this._renderDays();
      return;
    }

    if (this.phase === "to") {
      // کلیک دوم: پایان بازه (اگر قبل از from باشد، خودش جابه‌جا می‌شود)
      this.toUnix = day;
      this._finalizeRange();
      return;
    }

    // حالت‌های غیر عادی → شروع از اول
    this.fromUnix = day;
    this.toUnix = null;
    this.phase = "to";
    this._renderDays();
  };

  // ---------- نهایی‌کردن بازه و callback ----------

  BlueJalaliRangePicker.prototype._finalizeRange = function () {
    var c = clampRange(this.fromUnix, this.toUnix);
    this.fromUnix = startOfDay(c.fromUnix);
    this.toUnix = startOfDay(c.toUnix);

    var fromGreg = gregorianFromUnix(this.fromUnix);
    var toGreg = gregorianFromUnix(this.toUnix);
    var fromJ = jalaliFromUnix(this.fromUnix);
    var toJ = jalaliFromUnix(this.toUnix);

    this.phase = "from";   // برای دفعات بعدی

    if (typeof this.opts.onSelect === "function") {
      this.opts.onSelect({
        from_unix: this.fromUnix,
        to_unix: this.toUnix,
        from_greg: fromGreg,
        to_greg: toGreg,
        from_jalali: fromJ,
        to_jalali: toJ
      }, this);
    }

    this.close();
  };

  // ---------- موقعیت‌دهی کنار input ----------

  BlueJalaliRangePicker.prototype._position = function () {
    if (!this.root || !this.anchor) return;
    var rect = this.anchor.getBoundingClientRect();
    var pickerRect = this.root.getBoundingClientRect();

    var margin = 8;
    var scrollY =
      w.scrollY || d.documentElement.scrollTop || d.body.scrollTop || 0;
    var scrollX =
      w.scrollX || d.documentElement.scrollLeft || d.body.scrollLeft || 0;

    var top = rect.bottom + scrollY + margin;
    var left = rect.left + scrollX;

    var viewportWidth = d.documentElement.clientWidth || w.innerWidth || 0;
    if (left + pickerRect.width > viewportWidth - 8) {
      left = viewportWidth - pickerRect.width - 8;
    }
    if (left < 8) left = 8;

    this.root.style.top = top + "px";
    this.root.style.left = left + "px";
  };

  // ---------- export ----------

  w.BlueJalaliRangePicker = BlueJalaliRangePicker;
  console.log("[BlueJalaliRangePicker] loaded (no-hover)");
})(window, document);
