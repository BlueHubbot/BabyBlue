server {
    listen 80;
    server_name $DOCS_DOMAIN;
    return 301 https://$DOCS_DOMAIN$request_uri;
}
server {
    listen 443 ssl;
    server_name $DOCS_DOMAIN;
    root $SRV_DOCS/main;
    location = / { return 302 /blueapi/; }
    location ^~ /_blue/ {
        alias $SRV_DOCS/main/_blue/;
    }
}
