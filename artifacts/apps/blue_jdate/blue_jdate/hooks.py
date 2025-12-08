from . import __version__ as app_version

app_name = "blue_jdate"
app_title = "Blue JDate"
app_publisher = "Blue"
app_description = "Jalali helpers and print formats"
app_email = "support@example.com"
app_license = "MIT"

jinja = {
    "filters": [
        "blue_jdate.utils.as_jdate",
        "blue_jdate.utils.as_jdatetime",
        "blue_jdate.utils.money_to_words_fa",
    ],
    "methods": [
        # نسل قدیمی (اگر جایی استفاده شده باشد)
        "blue_jdate.utils.blue_date_j1",
        "blue_jdate.utils.blue_date_j2",

        # نسل جدید، مخصوص ماتریکس/policy
        "blue_jdate.utils.blue_policy_date_j1",
        "blue_jdate.utils.blue_policy_date_j2",
    ],
}
