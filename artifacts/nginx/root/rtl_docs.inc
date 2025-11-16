proxy_set_header Accept-Encoding "";
gunzip on;
sub_filter_once off;
sub_filter '</head>' '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="/rtl-docs.css?v=rtl1"><link rel="alternate" hreflang="fa" href="https://docs.bluenet.click/fa$request_uri"><link rel="canonical" href="https://docs.bluenet.click$request_uri"><meta property="og:locale" content="fa_IR"></head>';
sub_filter '<html ' '<html dir="rtl" lang="fa" ';
