# 🧠 Copilot Instructions for OSUSAPPS (Odoo 17)

## Architecture & Major Components
- **Odoo 17, Dockerized**: All dev, test, and deployment via Docker Compose. Custom modules are mounted at `/mnt/extra-addons`.
- **Modules**: Each top-level folder (e.g. `account_payment_final/`, `custom_sales/`, `account_statement/`) is a standard Odoo module with its own models, views, security, and tests. See each module's `README.md` for business context and features.
- **Database**: Managed by a Postgres container. Use `docker-compose exec db ...` for DB operations.

## Developer Workflows
- **Start/Stop**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac), or `docker-compose up -d` / `docker-compose down`.
- **Logs**: `docker-compose logs -f odoo`
- **Update modules**: `docker-compose exec odoo odoo --update=all --stop-after-init` or `--update=module_name`
- **Run tests**: `docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i module_name`
- **Common test task**: See VS Code task `Odoo 17 Test: account_payment_final`
- **Module install**: Copy to repo, update app list in Odoo UI, install from Apps menu.

## Project Conventions & Patterns
- **Module structure**: Always include `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `static/`, `reports/`, `wizards/`, and optionally `tests/`.
- **Naming**: Use snake_case for modules/models. Prefix custom models with module name (e.g. `payment_account_enhanced.payment_qr_verification`).
- **Security**: Always define `ir.model.access.csv` and `security.xml` for each module.
- **Testing**: Use Odoo's `TransactionCase` in `tests/`.
- **External dependencies**: Declare all Python packages in both `__manifest__.py` and Dockerfile (e.g. `qrcode`, `Pillow`).
- **Model extension**: Use `_inherit` for extension, `_inherits` for delegation.
- **State machines**: Use Selection fields and statusbar in form views.
- **API endpoints**: Use `@http.route` with proper auth/CSRF.
- **Reports**: Use QWeb XML for PDF, controllers for Excel/CSV. See `report_font_enhancement/` for CSS theming.
- **Config/settings**: Use `res.config.settings` and `ir.config_parameter`.
- **Error handling**: Use `ValidationError` for constraints, `UserError` for user-facing errors.
- **Frontend**: Use Chart.js for dashboards (`custom_sales/`), OWL for widgets.
- **Report theming**: See `report_font_enhancement/README.md` and `payment_account_enhanced/static/src/css/payment_voucher_style.css`.
- **Audit trails**: Use `payment_account_enhanced/models/payment_approval_history.py`.

## Integration & Cross-Component Patterns
- **Excel export**: Use `report_xlsx` if available, degrade gracefully if not.
- **Multi-app integration**: Some modules add features to both Contacts and Accounting apps.
- **Security**: Multi-level permissions and record rules.
- **REST API**: Some modules expose endpoints (see `payment_account_enhanced/controllers/main.py`).
- **Mobile/responsive**: Dashboards and reports are designed for mobile.
- **Email notifications**: Use Odoo mail templates for workflow events.
- **QR code verification**: Use public and JSON endpoints for payment verification.

## Common Issues & Troubleshooting
- **DB errors**: See `fix_cron_in_odoo.py`.
- **Duplicate records**: See `fix_duplicate_partners.py`.
- **JS errors**: See `fix_dashboard_js.py`.
- **Excel export**: Check `xlsxwriter` and `report_xlsx` install.
- **Voucher template errors**: See `PAYMENT_VOUCHER_FIX_SUMMARY.md`.
- **Approval workflow issues**: See `payment_approval_history.py`.

## Tips for AI Agents
- Always use Docker Compose for dev/test/debug.
- Mimic the structure and patterns of the most recently updated modules.
- Prefer Odoo ORM, API, and security mechanisms over custom code.
- Always include security definitions for new models.
- Use Odoo's built-in test infra, not ad-hoc scripts.
- Reference module-level `README.md` for business logic and integration details.

---

## Workspace Shortcut Commands

### Spec Workflow Commands
| Shortcut         | Command         | Description                        |
|------------------|----------------|------------------------------------|
| Ctrl+Alt+Spec    | Start Spec Workflow | Begin new feature spec process     |
| Ctrl+Alt+Req     | Create Requirements | Generate EARS requirements doc     |
| Ctrl+Alt+Des     | Create Design   | Generate design document with diagrams |
| Ctrl+Alt+Val     | Validate Spec   | Check spec compliance              |
| Ctrl+Alt+EARS    | Convert to EARS | Transform text to EARS format      |

### Odoo Development Commands
| Shortcut         | Command         | Description                        |
|------------------|----------------|------------------------------------|
| Ctrl+Alt+M       | Create Model    | Generate Odoo model with security  |
| Ctrl+Alt+V       | Create Views    | Generate XML views                 |
| Ctrl+Alt+S       | Create Security | Generate access rights             |
| Ctrl+Alt+Mod     | Complete Module | Generate full module from spec     |

### Code Quality Commands
| Shortcut         | Command         | Description                        |
|------------------|----------------|------------------------------------|
| Ctrl+Shift+I     | Explain Code    | AI explanation of selected code    |
| Ctrl+Shift+R     | Review Code     | Comprehensive code review          |
| Ctrl+Shift+T     | Generate Tests  | Create unit/integration tests      |
| Ctrl+Shift+D     | Generate Docs   | Create documentation               |

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
