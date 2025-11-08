server {
    listen 80;
    server_name $SITE_DOMAIN;
    return 301 https://$SITE_DOMAIN$request_uri;
}
server {
    listen 443 ssl;
    server_name $SITE_DOMAIN;

    root $BENCH_PATH/sites;
    location /files/ {
        alias $BENCH_PATH/sites/$SITE_DOMAIN/public/files/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    location /socket.io {
        proxy_pass http://127.0.0.1:9000;
    }
}
