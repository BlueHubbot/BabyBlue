proxy_set_header Accept-Encoding "";
gunzip on;
sub_filter '</head>' '<script src="/_blue/boot.js?v=$request_id"></script></head>';
sub_filter '<HEAD>' '<script src="/_blue/boot.js?v=$request_id"></script></HEAD>';
sub_filter_types *;
sub_filter_once off;
