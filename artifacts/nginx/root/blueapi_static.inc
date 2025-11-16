# /etc/nginx/blueapi_static.inc
location = /blueapi_help.js     { alias /var/www/html/blueapi_help.js;     default_type application/javascript; add_header Cache-Control "no-store" always; access_log off; }
location = /blueapi_snippet.html { alias /var/www/html/blueapi_snippet.html; default_type text/html;              add_header Cache-Control "no-store" always; access_log off; }
