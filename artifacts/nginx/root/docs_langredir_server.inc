set $is_fa $prefer_fa;
if ($is_fa) { if ($request_uri !~* "^/fa(/|$)") { return 302 https://docs.bluehesab.ir/fa$request_uri; } }
