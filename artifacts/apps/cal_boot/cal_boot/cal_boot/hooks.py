# hooks.py
app_name = "cal_boot"
app_title = "CAL Boot"
app_publisher = "Sarmad"
app_description = "Global Jalali boot for Desk"
app_email = "sarmad.afzali@gmail.com"
license = "MIT"

# فایل‌هایی که توی دسک ERPNext لود می‌شن
app_include_js = [
    "/assets/cal_boot/js/cal_boot.js",
    "/assets/cal_boot/js/cal_format.js",
    "/assets/cal_boot/js/cal_charts.js",
    "/assets/blueapi_help.js",
    # پچ انتخاب بازه‌ٔ زمانی شمسی (از مسیر سایت)
    "/files/cal-date-range.js",
    # دقت کن: اینجا دیگه /blueapi_boot.js نداریم
]

# فیکسچر ترجمه‌های فارسی
fixtures = [
    {"dt": "Translation", "filters": [["language", "=", "fa"]]}
]
