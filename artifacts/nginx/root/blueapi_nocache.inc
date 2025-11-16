if ($request_uri ~* ^/assets/(frappe/service-worker\.js|desk/sw\.js|.*/service-worker\.js)$) { return 410; }
