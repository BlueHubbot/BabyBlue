server {
  listen 80;
  server_name ${DOCS_DOMAIN};
  root ${DOCS_ROOT};
  index index.html;
  location / { try_files $uri $uri/ =404; }
  access_log /var/log/nginx/${DOCS_DOMAIN}.access.log;
  error_log  /var/log/nginx/${DOCS_DOMAIN}.error.log;
}
