BabyBlue – Reproducible Frappe/ERPNext Deployment

Structure:
  scripts/00-05   -> bootstrap -> bench -> site -> nginx -> ssl -> postcheck
  templates/      -> nginx & site_config templates
  artifacts/data/ -> DB dump + public/private files + app tarballs
  apps.json       -> pinned apps and branches
  .env            -> deployment variables (copy from .env.example)

Source server (you already did this):
  - Backups and app tarballs are stored under artifacts/data and committed on branch repro-v1.

Target server (fresh VPS):

  1) Clone & prepare env
     apt-get update && apt-get install -y git
     git clone -b repro-v1 https://github.com/BlueHubbot/BabyBlue.git /tmp/BabyBlue
     cd /tmp/BabyBlue
     cp .env.example .env
     nano .env
       # set:
       #   SITE=your.new.domain
       #   DOCS_SITE=docs.your.new.domain (or empty)
       #   SSL_EMAIL=your@email
       #   DB_ROOT_PASS / DB_NAME / DB_USER / DB_PASS
       #   ADMIN_PASS / ENCRYPTION_KEY

  2) Run scripts in order (as root)
     bash scripts/00-bootstrap.sh
     bash scripts/01-setup-bench.sh
     bash scripts/02-provision-site.sh
     bash scripts/03-nginx-render.sh
     bash scripts/04-issue-certs.sh
     bash scripts/05-postcheck.sh

Result:
  - New server with Frappe + ERPNext + HRMS + cal_boot
  - Restored DB and files from artifacts/data
  - Nginx + HTTPS (Let’s Encrypt) on new SITE / DOCS_SITE
