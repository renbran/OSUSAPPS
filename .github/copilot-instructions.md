
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
- **Odoo 17, Dockerized**: All dev/test/deploy is via Docker Compose. Odoo runs in a container, with custom modules mounted at `/mnt/extra-addons`.
- **Custom modules**: Each top-level folder (e.g. `account_payment_approval/`, `custom_sales/`, `oe_sale_dashboard_17/`) is a standard Odoo module with its own models, views, security, and tests.
- **Database**: Managed by a Postgres container. Use `docker-compose exec db ...` for DB ops.
- **Setup scripts**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac) for common tasks (start, stop, logs, backup).
- **Access**: Odoo UI at http://localhost:8069 (default admin: `admin`/`admin`).

## Developer Workflows
- **Start/Stop**: Use setup scripts or `docker-compose up -d` / `docker-compose down`.
- **Logs**: `docker-compose logs -f odoo`
- **DB backup/restore**: See project root scripts and `docker-compose` commands.
- **Update all modules**: `docker-compose exec odoo odoo --update=all --stop-after-init`
- **Update single module**: `docker-compose exec odoo odoo --update=module_name --stop-after-init`
- **Run tests**: `docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i module_name`
- **Enter Odoo shell**: `docker-compose exec odoo bash`
- **Module install**: Copy to repo, update app list in Odoo UI, then install from Apps menu.

## Project Conventions & Patterns
- **Module structure**: Each module has `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `demo/`, `static/`, `tests/`.
- **Naming**: Use snake_case for modules/models. Prefix custom models with module name (e.g. `custom_sales.kpi_config`).
- **Security**: Always define `ir.model.access.csv` and `security.xml` for each module. See `account_payment_approval/security/` for reference.
- **Testing**: Use `TransactionCase` in `tests/` (see `tk_sale_split_invoice/tests/test_sale_split_invoice.py`).
- **External dependencies**: Declare all Python packages in both `__manifest__.py` and Dockerfile.
- **Model extension**: Use `_inherit` for extension, `_inherits` for delegation. Example: `account_payment_approval/models/account_payment.py`.
- **State machines**: Use Selection fields and statusbar in form views (see `account_payment_approval`).
- **API endpoints**: Use `@http.route` with proper auth/CSRF (see `om_dynamic_report/controllers/`).
- **Reports**: Use QWeb XML for PDF, controllers for Excel/CSV. See `payment_account_enhanced/reports/` for QWeb patterns.
- **Config/settings**: Use `res.config.settings` and `ir.config_parameter` for settings (see `account_payment_approval/models/res_config_settings.py`).
- **Error handling**: Use `ValidationError` for constraints, `UserError` for user-facing errors.
- **Frontend**: Use Chart.js for dashboards (see `custom_sales/`, `oe_sale_dashboard_17/`).
- **Report theming**: For report styling, see `report_font_enhancement/` (uses CSS variables, high-contrast, print optimizations).

## Integration & Cross-Component Patterns
- **Excel export**: Use `report_xlsx` if available, but degrade gracefully if not (see `account_statement/`).
- **Multi-app integration**: Some modules (e.g. `account_statement/`) add features to both Contacts and Accounting apps.
- **Security**: Multi-level permissions and record rules (see `account_statement/security/`).
- **REST API**: Some modules expose REST endpoints (see `custom_sales/api/`).
- **Mobile/responsive**: Dashboards and reports are designed for mobile (see `custom_sales/`).

## Examples & References
- **Module structure**: `account_payment_approval/`, `custom_sales/`, `account_statement/`
- **API endpoint**: `om_dynamic_report/controllers/om_dynamic_report_controller.py`, `custom_sales/api/`
- **Form view**: `account_payment_approval/views/account_payment_views.xml`
- **Testing**: `tk_sale_split_invoice/tests/test_sale_split_invoice.py`
- **Report theming**: `report_font_enhancement/README.md`

## Common Issues & Troubleshooting
- **DB errors**: If cron jobs fail, check `fix_cron_in_odoo.py`.
- **Duplicate records**: See `fix_duplicate_partners.py` for deduplication logic.
- **JS errors**: Run `fix_dashboard_js.py` for dashboard JS issues.
- **Permission errors**: Check `ir.model.access.csv` and security groups.
- **Module dependencies**: Ensure all dependencies are in `__manifest__.py` before install.
- **Excel export**: If not available, check `xlsxwriter` and `report_xlsx` install.

## Tips for AI Agents
- Always use Docker Compose for all dev/test/debug.
- When adding modules, follow structure and manifest patterns of existing modules.
- Prefer Odoo ORM, API, and security mechanisms over custom code.
- Always include security definitions for new models.
- Use Odoo's built-in test infra, not ad-hoc scripts.
- For reports, prefer QWeb XML and follow theming patterns in `report_font_enhancement/`.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
