BabyBlue – Reproducible Frappe/ERPNext Deployment

Structure:
  scripts/00-05   -> bootstrap -> bench -> site -> nginx -> ssl -> postcheck
  templates/      -> nginx & site_config templates
  artifacts/data/ -> DB dump + public/private files
  apps.json       -> pinned apps and branches
  .env            -> deployment variables (copy from .env.example)
