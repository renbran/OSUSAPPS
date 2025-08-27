
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
+ **Odoo 17, Dockerized**: All development, testing, and deployment is via Docker Compose. Odoo runs in a container, with custom modules mounted at `/mnt/extra-addons`.
+ **Custom modules**: Each top-level folder (e.g. `account_payment_final/`, `payment_account_enhanced/`, `custom_sales/`, `account_statement/`) is a standard Odoo module with its own models, views, security, and tests. See module-level `README.md` for business context and features.
+ **Database**: Managed by a Postgres container. Use `docker-compose exec db ...` for DB operations.
+ **Setup scripts**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac) for common tasks (start, stop, logs, backup).
+ **Access**: Odoo UI at http://localhost:8069 (default admin: `admin`/`admin`).
+ **Major modules**:
+   - `account_payment_final/`: Enterprise-grade payment workflow, QR verification, multi-stage approval, OSUS branding.
+   - `payment_account_enhanced/`: Professional voucher templates, robust approval history, QR code security, advanced CSS theming.
+   - `custom_sales/`: Advanced sales dashboard, KPI widgets, Chart.js analytics, mobile/responsive design.
+   - `account_statement/`: Multi-app integration, PDF/Excel export, dual menu access, multi-level permissions.

## Developer Workflows
+ **Start/Stop**: Use setup scripts or `docker-compose up -d` / `docker-compose down`.
+ **Logs**: `docker-compose logs -f odoo`
+ **DB backup/restore**: See project root scripts and `docker-compose` commands.
+ **Update all modules**: `docker-compose exec odoo odoo --update=all --stop-after-init`
+ **Update single module**: `docker-compose exec odoo odoo --update=module_name --stop-after-init`
+ **Run tests**: `docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i module_name`
+ **Enter Odoo shell**: `docker-compose exec odoo bash`
+ **Module install**: Copy to repo, update app list in Odoo UI, then install from Apps menu.
+ **Testing**: Use Odoo's built-in test infrastructure (`TransactionCase` in `tests/`). Do not use ad-hoc scripts.
+ **Common test task**: See VS Code task `Odoo 17 Test: account_payment_final` for automated test runs.

## Project Conventions & Patterns
+ **Module structure**: Each module has `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `static/`, `reports/`, `wizards/`, and optionally `tests/`.
+ **Naming**: Use snake_case for modules/models. Prefix custom models with module name (e.g. `payment_account_enhanced.payment_qr_verification`).
+ **Security**: Always define `ir.model.access.csv` and `security.xml` for each module. See `payment_account_enhanced/security/` for multi-level group and record rule patterns.
+ **Testing**: Use Odoo's `TransactionCase` in `tests/` (see `tk_sale_split_invoice/tests/test_sale_split_invoice.py`).
+ **External dependencies**: Declare all Python packages in both `__manifest__.py` and Dockerfile. Example: `qrcode`, `Pillow` for QR features.
+ **Model extension**: Use `_inherit` for extension, `_inherits` for delegation. Example: `payment_account_enhanced/models/account_payment.py`.
+ **State machines**: Use Selection fields and statusbar in form views (see `account_payment_final/models/account_payment.py`).
+ **API endpoints**: Use `@http.route` with proper auth/CSRF (see `payment_account_enhanced/controllers/main.py`).
+ **Reports**: Use QWeb XML for PDF, controllers for Excel/CSV. See `payment_account_enhanced/reports/` for QWeb and CSS theming patterns.
+ **Config/settings**: Use `res.config.settings` and `ir.config_parameter` for settings (see `payment_account_enhanced/models/res_config_settings.py`).
+ **Error handling**: Use `ValidationError` for constraints, `UserError` for user-facing errors.
+ **Frontend**: Use Chart.js for dashboards (see `custom_sales/`).
+ **Report theming**: For report styling, see `report_font_enhancement/` (uses CSS variables, high-contrast, print optimizations).
+ **Voucher templates**: See `payment_account_enhanced/reports/payment_voucher_template_fixed.xml` and related CSS for production-ready, branded layouts.
+ **Audit trails**: Use `payment_account_enhanced/models/payment_approval_history.py` for comprehensive approval history.

## Integration & Cross-Component Patterns
+ **Excel export**: Use `report_xlsx` if available, but degrade gracefully if not (see `account_statement/`).
+ **Multi-app integration**: Some modules (e.g. `account_statement/`) add features to both Contacts and Accounting apps.
+ **Security**: Multi-level permissions and record rules (see `payment_account_enhanced/security/`, `account_statement/security/`).
+ **REST API**: Some modules expose REST endpoints (see `payment_account_enhanced/controllers/main.py`, `custom_sales/api/`).
+ **Mobile/responsive**: Dashboards and reports are designed for mobile (see `custom_sales/`).
+ **Email notifications**: Use Odoo mail templates for workflow events (see `payment_account_enhanced/data/mail_template_data.xml`).
+ **QR code verification**: Use public and JSON endpoints for payment verification (see `payment_account_enhanced/controllers/main.py`).

## Examples & References
+ **Module structure**: `payment_account_enhanced/`, `account_payment_final/`, `custom_sales/`, `account_statement/`
+ **API endpoint**: `payment_account_enhanced/controllers/main.py`, `custom_sales/api/`
+ **Form view**: `payment_account_enhanced/views/account_payment_views.xml`
+ **Testing**: `tk_sale_split_invoice/tests/test_sale_split_invoice.py`
+ **Report theming**: `report_font_enhancement/README.md`, `payment_account_enhanced/static/src/css/payment_voucher_style.css`
+ **Approval history**: `payment_account_enhanced/models/payment_approval_history.py`
+ **Mail templates**: `payment_account_enhanced/data/mail_template_data.xml`

## Common Issues & Troubleshooting
+ **DB errors**: If cron jobs fail, check `fix_cron_in_odoo.py`.
+ **Duplicate records**: See `fix_duplicate_partners.py` for deduplication logic.
+ **JS errors**: Run `fix_dashboard_js.py` for dashboard JS issues.
+ **Permission errors**: Check `ir.model.access.csv` and security groups.
+ **Module dependencies**: Ensure all dependencies are in `__manifest__.py` before install.
+ **Excel export**: If not available, check `xlsxwriter` and `report_xlsx` install.
+ **Voucher template errors**: See `PAYMENT_VOUCHER_FIX_SUMMARY.md` for common template issues and fixes.
+ **Approval workflow issues**: Check `payment_account_enhanced/models/payment_approval_history.py` for audit trail and debugging.

## Tips for AI Agents
+ Always use Docker Compose for all dev/test/debug.
+ When adding modules, follow structure and manifest patterns of existing modules.
+ Prefer Odoo ORM, API, and security mechanisms over custom code.
+ Always include security definitions for new models.
+ Use Odoo's built-in test infra, not ad-hoc scripts.
+ For reports, prefer QWeb XML and follow theming patterns in `report_font_enhancement/` and `payment_account_enhanced/static/src/css/payment_voucher_style.css`.
+ For voucher/report template fixes, see `PAYMENT_VOUCHER_FIX_SUMMARY.md` for production-ready patterns.
+ For approval workflow, ensure audit trail via `payment_approval_history.py`.
+ Reference module-level `README.md` for business logic and integration details.
+ If in doubt, mimic the structure and patterns of the most recently updated modules.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
