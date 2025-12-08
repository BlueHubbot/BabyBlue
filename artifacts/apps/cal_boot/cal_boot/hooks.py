# hooks.py
from . import __version__ as app_version

app_name = "cal_boot"
app_title = "CAL Boot"
app_publisher = "BlueHesab"
app_description = "Global Jalali helpers (baseline)"
app_email = "desk@bluehesab.ir"
app_license = "MIT"

app_include_js = [
    "/assets/cal_boot/js/cal_lite_trap.js",
    "/assets/cal_boot/js/blue_jalali_picker.js",
    "/assets/cal_boot/js/blue_jalali_range.js",
    "/assets/cal_boot/js/cal_boot.js",
    "/assets/cal_boot/js/blue_overlay_dom_patches.js",
    "/assets/blueapi_help.js",
]

fixtures = [
    {"dt": "Translation", "filters": [["language", "=", "fa"]]}
]
