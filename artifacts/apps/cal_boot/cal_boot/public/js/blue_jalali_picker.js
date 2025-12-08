// apps/cal_boot/cal_boot/public/js/blue_jalali_picker.js
// BlueJalaliPicker – تقویم جلالی تک‌تاریخ، اعداد لاتین، استایل نزدیک به Litepicker
// این فایل الان استایل مشترک برای تک‌تاریخ و رنج را هم آماده می‌کند.

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

    function makeEl(tag, className, text) {
        var el = d.createElement(tag);
        if (className) el.className = className;
        if (text != null) el.textContent = text;
        return el;
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

    // ---------- CSS مشترک تک‌تاریخ و رنج ----------

    function injectStylesOnce() {
        var id = "blue-jalali-picker-stable-style";
        if (d.getElementById(id)) return;

        var css = `
/* کادر اصلی پاپ‌آپ تقویم (برای هر دو: تک‌تاریخ و رنج) */
#blue-jalali-picker-root,
#blue-jalali-range-root {
  position: absolute;
  z-index: 9999;
  display: none;
  width: 252px;
  background: #ffffff;
  border: 1px solid #dddee0ff;
  border-radius: 16px;
  box-shadow:
    0 18px 40px rgba(15, 23, 42, 0.14),
    0 6px 18px rgba(15, 23, 42, 0.12);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  color: #111827;
  padding: 0;
  user-select: none;
}
#blue-jalali-picker-root *,
#blue-jalali-range-root * {
  box-sizing: border-box;
}

/* سربرگ تقویم */
#blue-jalali-picker-root .bjp-nav,
#blue-jalali-range-root .bjp-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 9px 6px 10px;
  border-bottom: 1px solid #f3f4f6;
  min-height: 38px;
}

/* دکمه‌های فلش */
#blue-jalali-picker-root .bjp-nav-action,
#blue-jalali-range-root .bjp-nav-action {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #51535aff;
  padding: 0;
  font-size: 25px;
}
#blue-jalali-picker-root .bjp-nav-action:hover,
#blue-jalali-range-root .bjp-nav-action:hover {
  background: #f3f4f6;
  color: #111827;
}

/* عنوان ماه/سال */
#blue-jalali-picker-root .bjp-title,
#blue-jalali-range-root .bjp-title {
  flex: 1;
  text-align: center;
  font-weight: 600;
  font-size: 15px;
  color: #111827;
  cursor: pointer;
  border-radius: 6px;
  padding: 4px 8px;
  margin: 0 6px;
  white-space: nowrap;
}
#blue-jalali-picker-root .bjp-title:hover,
#blue-jalali-range-root .bjp-title:hover {
  background: #f3f4f6;
}
#blue-jalali-picker-root .bjp-title span,
#blue-jalali-range-root .bjp-title span {
  color: #666c79ff;
  font-weight: 500;
  font-size: 14px;
  margin-right: 4px;
}

/* محتوای اصلی */
#blue-jalali-picker-root .bjp-content,
#blue-jalali-range-root .bjp-content {
  padding: 8px 10px;
}

/* ردیف نام روزها */
#blue-jalali-picker-root .bjp-week-row,
#blue-jalali-range-root .bjp-week-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 5px;
}
#blue-jalali-picker-root .bjp-weekday,
#blue-jalali-range-root .bjp-weekday {
  text-align: center;
  font-size: 12px;
  color: #6b7280;
  font-weight: 550;
  height: 24px;
  line-height: 24px;
}

/* گرید روزها */
#blue-jalali-picker-root .bjp-grid,
#blue-jalali-range-root .bjp-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

/* سلول پایه */
#blue-jalali-picker-root .bjp-cell,
#blue-jalali-range-root .bjp-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 0;
  background: transparent;
  transition: all 0.15s ease;
  border-radius: 7px;
  font-weight: 550;
  font-size: 14px;
  color: #0f1522ff;
}

/* سلول روز */
#blue-jalali-picker-root .bjp-day,
#blue-jalali-range-root .bjp-day {
  width: 32px;
  height: 28px;
}

/* Hover روی سلول‌ها */
#blue-jalali-picker-root .bjp-day:hover,
#blue-jalali-picker-root .bjp-month:hover,
#blue-jalali-picker-root .bjp-year:hover,
#blue-jalali-range-root .bjp-day:hover,
#blue-jalali-range-root .bjp-month:hover,
#blue-jalali-range-root .bjp-year:hover {
  background: #f3f4f6;
}

/* روزهای خارج از ماه جاری */
#blue-jalali-picker-root .bjp-day-outside,
#blue-jalali-range-root .bjp-day-outside {
  color: #d1d5db;
  font-weight: 400;
}

/* انتخاب‌شده (برای تک‌تاریخ و همچنین ابتدای/انتهای رنج) */
#blue-jalali-picker-root .bjp-selected,
#blue-jalali-range-root .bjp-selected {
  background: #111827 !important;
  color: #ffffff !important;
}

/* امروز (وقتی انتخاب نشده) */
#blue-jalali-picker-root .bjp-day-today:not(.bjp-selected),
#blue-jalali-range-root .bjp-day-today:not(.bjp-selected) {
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.75);
}

/* گرید ماه‌ها و سال‌ها (فعلاً بیشتر برای تک‌تاریخ استفاده می‌شود) */
#blue-jalali-picker-root .bjp-months-grid,
#blue-jalali-picker-root .bjp-years-grid,
#blue-jalali-range-root .bjp-months-grid,
#blue-jalali-range-root .bjp-years-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  padding: 4px 0;
}
#blue-jalali-picker-root .bjp-month,
#blue-jalali-picker-root .bjp-year,
#blue-jalali-range-root .bjp-month,
#blue-jalali-range-root .bjp-year {
  height: 36px;
  font-size: 13px;
  color: #374151;
  border-radius: 6px;
}
#blue-jalali-picker-root .bjp-year-outside,
#blue-jalali-range-root .bjp-year-outside {
  color: #d1d5db;
}

/* Viewها */
#blue-jalali-picker-root .bjp-view,
#blue-jalali-range-root .bjp-view {
  display: none;
}
#blue-jalali-picker-root .bjp-view.active,
#blue-jalali-range-root .bjp-view.active {
  display: block;
}

/* فوتر (فقط برای تک‌تاریخ استفاده می‌کنیم؛ رنج فوتر ندارد) */
#blue-jalali-picker-root .bjp-footer {
  border-top: 1px solid #f3f4f6;
  padding: 7px 11px;
  text-align: center;
}
#blue-jalali-picker-root .bjp-btn-today {
  display: block;
  width: 100%;
  border: none;
  background: transparent;
  font-size: 13px;
  font-weight: 550;
  color: #6b7280;
  cursor: pointer;
  padding: 6px 0;
  border-radius: 6px;
  transition: all 0.15s ease;
}
#blue-jalali-picker-root .bjp-btn-today:hover {
  background: #f3f4f6;
  color: #111827;
}

/* استایل اضافه برای حالت رنج (هایلایت بین from/to) */
#blue-jalali-picker-root .bjp-in-range,
#blue-jalali-range-root .bjp-in-range {
  background: #e5e7eb;
}
#blue-jalali-picker-root .bjp-range-from,
#blue-jalali-picker-root .bjp-range-to,
#blue-jalali-range-root .bjp-range-from,
#blue-jalali-range-root .bjp-range-to {
  background: #111827;
  color: #ffffff;
}
        `.trim();

        var style = d.createElement("style");
        style.id = id;
        style.type = "text/css";
        style.appendChild(d.createTextNode(css));
        d.head.appendChild(style);
    }

    // ---------- BlueJalaliPicker (تک‌تاریخ) ----------

    function BlueJalaliPicker(opts) {
        injectStylesOnce();
        this.opts = opts || {};
        this.root = null;
        this.titleEl = null;

        this.daysView = null;
        this.monthsView = null;
        this.yearsView = null;

        this.daysGridEl = null;
        this.monthsGridEl = null;
        this.yearsGridEl = null;

        this.anchorInput = null;
        this.viewUnix = null;
        this.selectedUnix = null;
        this.isOpen = false;
        this.viewMode = "day";
        this._docClickHandler = null;
    }

    BlueJalaliPicker.prototype._ensureDom = function () {
        if (this.root && d.body.contains(this.root)) return;

        var root = makeEl("div", "bjp-root");
        root.id = "blue-jalali-picker-root";
        root.setAttribute("dir", "rtl");

        var header = makeEl("div", "bjp-nav");

        var prev = makeEl("button", "bjp-nav-action", "›"); // به‌صورت ظاهری راست/چپ تنظیم شده
        prev.type = "button";
        var title = makeEl("div", "bjp-title", "");
        var next = makeEl("button", "bjp-nav-action", "‹");
        next.type = "button";

        header.appendChild(prev);
        header.appendChild(title);
        header.appendChild(next);

        var content = makeEl("div", "bjp-content");

        var daysView = makeEl("div", "bjp-view bjp-days");
        var weekRow = makeEl("div", "bjp-week-row");
        for (var i = 0; i < 7; i++) {
            weekRow.appendChild(makeEl("div", "bjp-weekday", WEEKDAY_LABELS[i]));
        }
        var daysGrid = makeEl("div", "bjp-grid");
        daysView.appendChild(weekRow);
        daysView.appendChild(daysGrid);

        var monthsView = makeEl("div", "bjp-view bjp-months");
        var monthsGrid = makeEl("div", "bjp-months-grid");
        monthsView.appendChild(monthsGrid);

        var yearsView = makeEl("div", "bjp-view bjp-years");
        var yearsGrid = makeEl("div", "bjp-years-grid");
        yearsView.appendChild(yearsGrid);

        content.appendChild(daysView);
        content.appendChild(monthsView);
        content.appendChild(yearsView);

        var footer = makeEl("div", "bjp-footer");
        var todayBtn = makeEl("button", "bjp-btn-today", "امروز");
        todayBtn.type = "button";
        footer.appendChild(todayBtn);

        root.appendChild(header);
        root.appendChild(content);
        root.appendChild(footer);
        d.body.appendChild(root);

        this.root = root;
        this.titleEl = title;
        this.daysView = daysView;
        this.monthsView = monthsView;
        this.yearsView = yearsView;
        this.daysGridEl = daysGrid;
        this.monthsGridEl = monthsGrid;
        this.yearsGridEl = yearsGrid;

        var self = this;

        prev.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            self._shiftView(1);
        });

        next.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            self._shiftView(-1);
        });

        title.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (self.viewMode === "day") {
                self.viewMode = "month";
            } else if (self.viewMode === "month") {
                self.viewMode = "year";
            }
            self._render();
        });

        todayBtn.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            self._select(Date.now());
        });
    };

    BlueJalaliPicker.prototype._shiftView = function (delta) {
        if (!this.viewUnix) this.viewUnix = this.selectedUnix || Date.now();
        var viewJ = jalaliFromUnix(this.viewUnix);

        var y = viewJ.y;
        var m = viewJ.m;
        var d0 = viewJ.d;

        if (this.viewMode === "day") {
            m += delta;
            while (m < 1) { m += 12; y -= 1; }
            while (m > 12) { m -= 12; y += 1; }
        } else if (this.viewMode === "month") {
            y += delta;
        } else if (this.viewMode === "year") {
            y += delta * 12;
        }

        var maxDay = jalaliMonthDays(y, m);
        if (d0 > maxDay) d0 = maxDay;

        this.viewUnix = jalaliToUnix(y, m, d0);
        this._render();
    };

    BlueJalaliPicker.prototype.open = function (inputEl, initialGregStr) {
        var self = this;
        if (!inputEl) return;

        function reallyOpen() {
            try {
                jalaliFromUnix(Date.now());
            } catch (e) {
                console.error("[BlueJalaliPicker] persianDate not ready:", e);
                return;
            }

            self._ensureDom();
            self.anchorInput = inputEl;

            var raw =
                (initialGregStr && initialGregStr.trim()) ||
                (inputEl.value && String(inputEl.value).trim()) ||
                "";
            var selUnix = parseGregDate(raw) || Date.now();

            self.selectedUnix = selUnix;
            self.viewUnix = selUnix;
            self.viewMode = "day";

            self.root.style.visibility = "hidden";
            self.root.style.display = "block";

            self._render();
            self._position();

            self.root.style.visibility = "visible";
            self.isOpen = true;

            if (self._docClickHandler) {
                d.removeEventListener("mousedown", self._docClickHandler, true);
            }
            self._docClickHandler = function (ev) {
                if (!self.isOpen) return;
                if (!self.root.contains(ev.target) && ev.target !== self.anchorInput) {
                    self.close();
                }
            };
            d.addEventListener("mousedown", self._docClickHandler, true);
        }

        if (w.persianDate) {
            reallyOpen();
            return;
        }
        if (w.CAL && typeof w.CAL.ensureLibs === "function") {
            w.CAL.ensureLibs().then(reallyOpen).catch(function (err) {
                console.error("[BlueJalaliPicker] CAL.ensureLibs failed:", err);
            });
        }
    };

    BlueJalaliPicker.prototype.close = function () {
        if (!this.isOpen) return;
        this.isOpen = false;
        if (this.root) this.root.style.display = "none";
        if (this._docClickHandler) {
            d.removeEventListener("mousedown", this._docClickHandler, true);
            this._docClickHandler = null;
        }
        this.anchorInput = null;
    };

    BlueJalaliPicker.prototype._render = function () {
        if (!this.root || !this.daysView || !this.monthsView || !this.yearsView) return;

        this.daysView.classList.remove("active");
        this.monthsView.classList.remove("active");
        this.yearsView.classList.remove("active");

        if (this.viewMode === "day") {
            this.daysView.classList.add("active");
            this._renderDays();
        } else if (this.viewMode === "month") {
            this.monthsView.classList.add("active");
            this._renderMonths();
        } else if (this.viewMode === "year") {
            this.yearsView.classList.add("active");
            this._renderYears();
        }
    };

    BlueJalaliPicker.prototype._renderDays = function () {
        if (!this.selectedUnix) this.selectedUnix = Date.now();
        if (!this.viewUnix) this.viewUnix = this.selectedUnix;

        var viewJ = jalaliFromUnix(this.viewUnix);
        var selectedJ = jalaliFromUnix(this.selectedUnix);
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

        var self = this;
        var currentMonthDays = jalaliMonthDays(viewJ.y, viewJ.m);
        var lastDayOfMonthUnix = firstUnix + (currentMonthDays - 1) * DAY_MS;
        var lastDayIndex = Math.floor((lastDayOfMonthUnix - startUnix) / DAY_MS);
        var maxCells = lastDayIndex < 35 ? 35 : 42;

        for (var i = 0; i < maxCells; i++) {
            (function (cellUnix) {
                var j = jalaliFromUnix(cellUnix);
                var inMonth = j.m === viewJ.m && j.y === viewJ.y;

                var btn = makeEl("div", "bjp-cell bjp-day", String(j.d));

                if (!inMonth) {
                    btn.classList.add("bjp-day-outside");
                }

                if (
                    j.y === selectedJ.y &&
                    j.m === selectedJ.m &&
                    j.d === selectedJ.d
                ) {
                    btn.classList.add("bjp-selected");
                }

                if (
                    j.y === todayJ.y &&
                    j.m === todayJ.m &&
                    j.d === todayJ.d
                ) {
                    btn.classList.add("bjp-day-today");
                }

                btn.addEventListener("click", function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    self._select(cellUnix);
                });

                self.daysGridEl.appendChild(btn);
            })(startUnix + i * DAY_MS);
        }
    };

    BlueJalaliPicker.prototype._renderMonths = function () {
        var viewJ = jalaliFromUnix(this.viewUnix);
        var selectedJ = jalaliFromUnix(this.selectedUnix);

        this.titleEl.textContent = viewJ.y;

        while (this.monthsGridEl.firstChild) {
            this.monthsGridEl.removeChild(this.monthsGridEl.firstChild);
        }

        var self = this;
        for (var m = 1; m <= 12; m++) {
            (function (monthNum) {
                var btn = makeEl(
                    "div",
                    "bjp-cell bjp-month",
                    MONTH_NAMES_FA[monthNum - 1]
                );
                btn.setAttribute("data-month", monthNum);

                if (monthNum === selectedJ.m && viewJ.y === selectedJ.y) {
                    btn.classList.add("bjp-selected");
                }

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    self.viewUnix = jalaliToUnix(
                        viewJ.y,
                        monthNum,
                        viewJ.d
                    );
                    self.viewMode = "day";
                    self._render();
                });

                self.monthsGridEl.appendChild(btn);
            })(m);
        }
    };

    BlueJalaliPicker.prototype._renderYears = function () {
        var viewJ = jalaliFromUnix(this.viewUnix);
        var selectedJ = jalaliFromUnix(this.selectedUnix);

        var startYear = Math.floor(viewJ.y / 10) * 10 - 1;
        var endYear = startYear + 11;

        this.titleEl.textContent = startYear + " - " + endYear;

        while (this.yearsGridEl.firstChild) {
            this.yearsGridEl.removeChild(this.yearsGridEl.firstChild);
        }

        var self = this;
        for (var y = startYear; y <= endYear; y++) {
            (function (yearNum) {
                var btn = makeEl("div", "bjp-cell bjp-year", String(yearNum));

                if (yearNum < startYear + 1 || yearNum > endYear - 1) {
                    btn.classList.add("bjp-year-outside");
                }
                if (yearNum === selectedJ.y) {
                    btn.classList.add("bjp-selected");
                }

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    self.viewUnix = jalaliToUnix(
                        yearNum,
                        viewJ.m,
                        viewJ.d
                    );
                    self.viewMode = "month";
                    self._render();
                });

                self.yearsGridEl.appendChild(btn);
            })(y);
        }
    };

    BlueJalaliPicker.prototype._position = function () {
        if (!this.root || !this.anchorInput) return;
        var rect = this.anchorInput.getBoundingClientRect();
        var pickerRect = this.root.getBoundingClientRect();

        var margin = 8;
        var scrollY =
            w.scrollY || d.documentElement.scrollTop || d.body.scrollTop || 0;
        var scrollX =
            w.scrollX || d.documentElement.scrollLeft || d.body.scrollLeft || 0;

        var top = rect.bottom + scrollY + margin;
        var left = rect.left + scrollX;

        var viewportWidth =
            d.documentElement.clientWidth || w.innerWidth || 0;
        if (left + pickerRect.width > viewportWidth - 8) {
            left = viewportWidth - pickerRect.width - 8;
        }
        if (left < 8) left = 8;

        this.root.style.top = top + "px";
        this.root.style.left = left + "px";
    };

    BlueJalaliPicker.prototype._select = function (unix) {
        this.selectedUnix = unix;
        var gregStr = gregorianFromUnix(unix);
        var j = jalaliFromUnix(unix);

        if (this.anchorInput) {
            this.anchorInput.value = gregStr;
            try {
                this.anchorInput.dispatchEvent(
                    new Event("change", { bubbles: true })
                );
            } catch (e) {
                var evt = d.createEvent("HTMLEvents");
                evt.initEvent("change", true, false);
                this.anchorInput.dispatchEvent(evt);
            }
        }

        if (typeof this.opts.onSelect === "function") {
            this.opts.onSelect(
                { unix: unix, gregorian: gregStr, jalali: j },
                this
            );
        }

        this.close();
    };

    w.BlueJalaliPicker = BlueJalaliPicker;
    console.log("[BlueJalaliPicker] stable version loaded");

})(window, document);
