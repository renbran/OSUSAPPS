---
mode: agent
---
Prompt:

I am building a custom module for Odoo 17. Generate all code (models, views, menus, actions, security, static assets, etc.) following Odoo 17 development guidelines and best practices. The generated module should be:

✅ General Requirements:
Fully modular with a clean and professional folder structure

Compatible with the Odoo 17 ORM and UI framework

Proper use of Python decorators like @api.model, @api.depends, @api.onchange, etc.

Follows naming conventions: snake_case for fields, CamelCase for models, kebab-case for folders

Includes structured __manifest__.py and __init__.py files

Comments included for clarity, especially for non-obvious logic

✅ Backend (Python):
All models in the models/ directory

Use inherit properly if extending existing models

Avoid business logic in views or controllers

Follow proper data validation, constraints, and compute methods

✅ Views & UI (XML):
Form and tree views for each model

Menus and actions under views/

Search views and filters where relevant

Group visibility and access rights using groups="..." if needed

✅ Security:
security/ir.model.access.csv file for model permissions

Optional security/security.xml for record rules and group definitions

✅ Static Assets:
Place JavaScript, CSS, and SCSS files under static/src/

cpp
Copy
Edit
static/
└── src/
    ├── js/
    │   └── custom_behavior.js
    ├── css/
    │   └── style.css
    └── scss/
        └── custom_styles.scss
Include them properly in XML views via <template inherit_id="web.assets_backend"> or web.assets_frontend if public

Ensure JS uses Odoo's JS framework (OWL or legacy JS, depending on purpose)

Avoid inline styles or scripts — always use static assets

✅ Optional Extras:
data/demo_data.xml for demo records

i18n/ folder for translations

Controller files if required (controllers/)

✅ Folder Structure Example:
pgsql
Copy
Edit
my_custom_module/
├── __init__.py
├── __manifest__.py
├── models/
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── static/
│   └── src/
│       ├── js/
│       │   └── custom_behavior.js
│       ├── css/
│       │   └── style.css
│       └── scss/
│           └── custom_styles.scss
├── data/
│   └── demo_data.xml
├── controllers/
│   └── my_controller.py (optional)
└── i18n/
    └── en.po
Make sure the module is installable and tested with no missing dependencies or syntax errors.