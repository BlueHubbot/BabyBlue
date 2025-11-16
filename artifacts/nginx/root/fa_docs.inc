location = /fa { return 301 /fa/; }
location ^~ /fa/ {
  alias /var/www/html/fa/;
  index index.html;
  try_files $uri $uri/ =404;
  add_header Content-Language "fa" always;
  add_header Vary "Accept-Language" always;
  add_header X-FA-Loc "hit" always;
}
