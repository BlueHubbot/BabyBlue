proxy_set_header Accept-Encoding "";
gunzip on;
sub_filter_once off;
sub_filter '</head>' '<script src="/assets/blueapi_help.js?v=$request_id"></script></head>';
sub_filter '</HEAD>' '<script src="/assets/blueapi_help.js?v=$request_id"></script></HEAD>';
add_header X-Blueapi-Inject "1" always;
