# 🧠 Copilot Instructions for OSUSAPPS (Odoo 17)

## Big Picture Architecture
- **Multi-module Odoo 17 system** for business management (finance, CRM, reporting, workflow, UI).
- **Each module** is self-contained: `models/`, `views/`, `security/`, `data/`, `static/`, `tests/`, etc.
- **Dockerized environment**: Odoo and Postgres containers, all modules mounted at `/mnt/extra-addons`.
- **CloudPepper hosting optimizations**: error suppression, asset loading order, emergency JS fixes.

## Developer Workflows
- **Start/stop**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac), or `docker-compose up -d` / `down`.
- **Update modules**: `docker-compose exec odoo odoo --update=all --stop-after-init` or single module with `--update=module_name`.
- **Run tests**: `docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i module_name`.
- **Debug JS**: Use `fix_dashboard_js.py` and check asset order in manifest.
- **Debug XML**: Use `--dev xml --stop-after-init` for XML validation.
- **Multi-company issues**: Domain fields referencing `company_id` need `groups="base.group_multi_company"` or alternative logic.
- **DB backup/restore**: See key commands below.

## Key Commands
- **Start environment**: `setup.bat` (Windows) or `setup.sh` (Linux/Mac), or `docker-compose up -d`
- **Stop environment**: via setup script or `docker-compose down`
- **Logs**: `docker-compose logs -f odoo`
- **DB backup**: `docker-compose exec db pg_dump -U odoo -d odoo > backup.sql`
- **DB restore**: `cat backup.sql | docker-compose exec -T db psql -U odoo -d odoo`
- **Module updates**: `docker-compose exec odoo odoo --update=all --stop-after-init`
- **Single module update**: `docker-compose exec odoo odoo --update=module_name --stop-after-init`
- **Enter Odoo shell**: `docker-compose exec odoo bash`
- **Run Odoo tests**: `docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i module_name`

## Project-Specific Conventions
- **Naming**: snake_case for modules/models; prefix models with module name.
- **Security**: Every module must define `ir.model.access.csv` and security XML; use role-based groups (see `account_payment_final/security/`).
- **State machines**: Use Selection fields and statusbar in form views (see `account_payment_approval/views/`).
- **Branding**: OSUS modules use strict color schemes and branded SCSS (`osus_branding.scss`).
- **CloudPepper**: JS assets include error suppression and emergency fixes; asset order matters for stability.
- **Multi-company**: Views with `company_id` domains require `groups="base.group_multi_company"` or alternative logic.

## Integration & Data Flows
- **REST API endpoints**: Controllers use `@http.route` with proper auth/CSRF (see `om_dynamic_report/controllers/`).
- **Report generation**: QWeb XML for PDFs, controllers for Excel/CSV.
- **Email notifications**: Workflow stages trigger emails (see `account_payment_final/data/email_templates.xml`).
- **QR code verification**: Payment modules use `qrcode` and `pillow` for secure voucher generation.
- **External dependencies**: All Python packages must be declared in both `__manifest__.py` and Dockerfile.

## Examples & Patterns
- **Module structure**: See `account_payment_approval/` and `account_payment_final/README.md`.
- **Workflow logic**: 4-stage approval in `account_payment_final/models/account_payment.py`.
- **Model inheritance**: Prefer `_inherit` for extension, `_inherits` for delegation.
- **State machines**: Use Selection fields with statusbar_visible in form views.
- **Configuration**: Store settings in `res.config.settings` and `ir.config_parameter`.
- **Error handling**: Use `ValidationError` for constraint errors, `UserError` for user-facing errors.
- **Testing**: Use `TransactionCase` in `tests/` (see `tk_sale_split_invoice/tests/test_sale_split_invoice.py`).
- **Asset config**: Manifest files must list JS/SCSS in correct order for CloudPepper.

## Common Issues & Fixes
- **Database errors**: If cron jobs fail, check `fix_cron_in_odoo.py` script.
- **Duplicate records**: Use the `fix_duplicate_partners.py` script as a reference for deduplication logic.
- **JavaScript errors**: Run `fix_dashboard_js.py` to analyze and fix common JS issues.
- **Permission issues**: Always check `ir.model.access.csv` entries if getting access errors.
- **Module dependencies**: Ensure all dependencies are properly declared in `__manifest__.py` before installing.
- **Multi-company issues**: Domain fields referencing `company_id` need `groups="base.group_multi_company"` or alternative logic.

## Tips for AI Agents
- Always use Docker Compose for running, testing, and debugging code.
- When adding a new module, follow the structure and manifest patterns of existing modules.
- For Odoo-specific logic, prefer Odoo ORM, API, and security mechanisms over custom code.
- Include proper security definitions for any new models and check for access rights.
- Use Odoo's built-in test infrastructure rather than separate test scripts.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
