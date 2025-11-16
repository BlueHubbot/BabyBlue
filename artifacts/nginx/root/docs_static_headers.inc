location = /robots.txt {
  alias /var/www/docs/robots.txt;
  default_type text/plain;
  add_header Cache-Control "public, max-age=3600" always;
  access_log off; log_not_found off;
}
location = /sitemap-fa.xml {
  alias /var/www/docs/sitemap-fa.xml;
  default_type application/xml;
  add_header Cache-Control "public, max-age=3600" always;
  access_log off; log_not_found off;
}
