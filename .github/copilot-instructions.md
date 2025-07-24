# 🧠 Copilot Instructions for odoo17_final

## Project Overview
- This repo is a Dockerized Odoo 17 environment with many custom modules for business management (finance, CRM, reporting, communication, UI, tools).
- Major modules are in top-level folders (e.g., `account_payment_approval/`, `osus_invoice_report/`, `dynamic_accounts_report/`). Each is a standard Odoo module with models, views, security, etc.
- The environment is designed for rapid local development, testing, and production deployment using Docker Compose.

## Architecture & Workflows
- **Odoo runs in a Docker container**. All development, testing, and debugging should be done via Docker Compose (`docker-compose.yml`).
- **Custom modules** are loaded from the repo root. Each module follows Odoo's best practices for structure and manifest.
- **Database** is managed via a separate Postgres container. Use `docker-compose exec db ...` for DB operations.
- **Setup scripts**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac) for common tasks (start, stop, logs, backup).
- **Access Odoo** at http://localhost:8069 (default admin: `admin`/`admin`).
- **Important note**: All custom modules are mounted at `/mnt/extra-addons` in the container.

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

## Project Conventions
- **Module structure**: Each module has `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `demo/`, `static/`, `tests/`, etc.
- **Naming**: Use snake_case for module and model names. Prefix custom models with the module name (e.g., `module_name.model_name`).
- **Security**: Always define `ir.model.access.csv` and `security.xml` for each module (see `account_payment_approval/security/` as an example).
- **Testing**: Create test classes inheriting from `TransactionCase` in `tests/` directory (see `tk_sale_split_invoice/tests/test_sale_split_invoice.py`).
- **External dependencies**: All Python packages must be declared in both `__manifest__.py` and Dockerfile.

## Common Patterns
- **Model inheritance**: Prefer `_inherit` for extension, `_inherits` for delegation. Example in `account_payment_approval/models/account_payment.py`.
- **State machines**: Use Selection fields with states and statusbar_visible in form views (`account_payment_approval` module).
- **API endpoints**: Create controllers using `@http.route` decorator with proper auth and CSRF settings (see `om_dynamic_report/controllers/`).
- **Report generation**: Use QWeb reports (XML templates) for PDF reports, or controllers for Excel/CSV exports.
- **Configuration**: Store settings in `res.config.settings` and `ir.config_parameter` (see `account_payment_approval/models/res_config_settings.py`).
- **Error handling**: Use `ValidationError` for constraint errors, `UserError` for user-facing errors.

## Common Issues & Fixes
- **Database errors**: If cron jobs fail, check `fix_cron_in_odoo.py` script.
- **Duplicate records**: Use the `fix_duplicate_partners.py` script as a reference for deduplication logic.
- **JavaScript errors**: Run `fix_dashboard_js.py` to analyze and fix common JS issues.
- **Permission issues**: Always check `ir.model.access.csv` entries if getting access errors.
- **Module dependencies**: Ensure all dependencies are properly declared in `__manifest__.py` before installing.

## Examples
- **Module structure**: `account_payment_approval/` shows proper module organization
- **API endpoint**: `om_dynamic_report/controllers/om_dynamic_report_controller.py` demonstrates REST API pattern
- **Form view**: `account_payment_approval/views/account_payment_views.xml` shows proper form view structure
- **Testing**: `tk_sale_split_invoice/tests/test_sale_split_invoice.py` demonstrates proper test setup

## Tips for AI Agents
- Always use Docker Compose for running, testing, and debugging code.
- When adding a new module, follow the structure and manifest patterns of existing modules.
- For Odoo-specific logic, prefer Odoo ORM, API, and security mechanisms over custom code.
- Include proper security definitions for any new models and check for access rights.
- Use Odoo's built-in test infrastructure rather than separate test scripts.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
