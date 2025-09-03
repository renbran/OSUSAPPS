
# 🧠 Copilot Instructions for OSUSAPPS - Odoo 17 Development Standards

## 🎯 Core Mission
You are an expert Odoo 17 development copilot specialized in generating production-ready custom modules that strictly adhere to Odoo 17 standards, best practices, and modern syntax. Your primary goal is to create robust, maintainable, and conflict-free code for the OSUSAPPS project.

## 📁 Project Architecture & Big Picture
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

## 🚨 MANDATORY Odoo 17 Compliance Rules

### ✅ **ALWAYS Use Modern Syntax (Odoo 17+)**
```xml
<!-- ✅ CORRECT: Modern domain expressions -->
<button name="action_confirm" invisible="state not in ['draft','sent']"/>
<field name="delivery_date" invisible="state != 'confirmed'"/>
<field name="partner_id" required="order_type == 'sale'"/>
<field name="amount" readonly="state in ['posted', 'paid']"/>
```

### ❌ **NEVER Use Deprecated Syntax (Odoo 16 and Earlier)**
```xml
<!-- ❌ FORBIDDEN: Will cause errors in Odoo 17 -->
<button name="action_confirm" states="draft,sent"/>
<field name="field_name" attrs="{'invisible': [('state', '=', 'draft')]}"/>
<button name="button_name" attrs="{'readonly': [('state', '!=', 'posted')]}"/>
```

### 📋 **Required Module Structure**
```
custom_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── controllers/           # For web routes
│   ├── __init__.py
│   └── main.py
├── views/
│   ├── model_views.xml
│   ├── menus.xml
│   └── assets.xml        # JS/CSS includes
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml
├── data/
│   └── demo_data.xml
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   ├── src/
│   │   ├── js/           # OWL components
│   │   ├── scss/         # Styles
│   │   └── xml/          # Templates
│   └── tests/            # JS unit tests
├── tests/               # Python tests
│   └── test_*.py
└── README.md
```

## 🐍 **Python Development Standards (Odoo 17)**

### ✅ **Model Structure Template**
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class CustomModel(models.Model):
    _name = 'module.custom_model'
    _description = 'Custom Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'
    
    # Required fields
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help="Enter the name for this record"
    )
    
    # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], default='draft', tracking=True, string='Status')
    
    # Relationships
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        ondelete='cascade',
        tracking=True
    )
    
    line_ids = fields.One2many(
        'module.custom_line',
        'parent_id',
        string='Lines'
    )
    
    # Computed fields
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True
    )
    
    # Constraints
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or len(record.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters long"))
    
    # Computed methods
    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.amount for line in record.line_ids)
    
    # Onchange methods
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Business logic here
            pass
    
    # Action methods
    def action_confirm(self):
        """Confirm the record"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft records can be confirmed"))
        self.state = 'confirmed'
        self.message_post(body=_("Record confirmed"))
        return True
    
    # Business methods
    def _get_default_values(self):
        """Get default values for the record"""
        return {
            'state': 'draft',
            'name': self.env['ir.sequence'].next_by_code('module.custom_model') or '/'
        }
```

### 🔒 **Security Best Practices**
```python
# Always check permissions
def sensitive_operation(self):
    self.check_access_rights('write')
    self.check_access_rule('write')
    
# Use proper sudo() usage
def system_operation(self):
    # Only use sudo() when absolutely necessary
    return self.sudo().write({'internal_field': value})

# Implement record rules in security.xml
```

### 📊 **Database Best Practices**
```python
# ✅ Efficient queries
records = self.env['model.name'].search([
    ('field', '=', value)
], limit=100)

# ✅ Batch operations
self.env['model.name'].search([]).write({'field': 'value'})

# ❌ Avoid loops for simple operations
for record in records:
    record.write({'field': 'value'})  # Inefficient
```

## 🌐 **Frontend Development Standards (JavaScript/OWL)**

### ✅ **OWL Component Template**
```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CustomWidget extends Component {
    static template = "module.CustomWidgetTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            isLoading: false,
            data: null,
        });
        
        onWillStart(this.loadData);
    }

    async loadData() {
        this.state.isLoading = true;
        try {
            const data = await this.orm.call(
                "custom.model",
                "get_custom_data",
                [this.props.record.resId]
            );
            this.state.data = data;
        } catch (error) {
            this.notification.add(
                _t("Failed to load data: %s", error.message),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    async onSaveData() {
        if (this.props.readonly) return;
        
        try {
            await this.orm.call(
                "custom.model",
                "save_custom_data",
                [this.props.record.resId, this.state.data]
            );
            this.notification.add(_t("Data saved successfully"), {
                type: "success",
            });
        } catch (error) {
            this.notification.add(
                _t("Save failed: %s", error.message),
                { type: "danger" }
            );
        }
    }
}

// Register component
registry.category("fields").add("custom_widget", CustomWidget);
```

### 🎨 **CSS/SCSS Best Practices**
```scss
// ✅ Use module-specific prefixes
.o_module_name_widget {
    padding: 16px;
    border: 1px solid var(--bs-border-color);
    border-radius: 4px;
    background: var(--bs-body-bg);

    &:hover {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .o_widget_header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    // Responsive design
    @media (max-width: 768px) {
        padding: 12px;
        
        .o_widget_header {
            flex-direction: column;
        }
    }
}

// ✅ Use CSS custom properties for theming
:root {
    --module-primary-color: #722f37;
    --module-secondary-color: #b8860b;
    --module-border-radius: 4px;
}
```

### 📱 **Asset Management**
```xml
<!-- views/assets.xml -->
<odoo>
    <template id="assets_backend" inherit_id="web.assets_backend">
        <!-- SCSS Files -->
        <link rel="stylesheet" type="text/scss" href="/module/static/src/scss/variables.scss"/>
        <link rel="stylesheet" type="text/scss" href="/module/static/src/scss/components.scss"/>
        
        <!-- JavaScript Files -->
        <script type="text/javascript" src="/module/static/src/js/components/widget.js"/>
        <script type="text/javascript" src="/module/static/src/js/fields/custom_field.js"/>
    </template>

    <!-- QWeb Templates -->
    <template id="custom_widget_template" name="module.CustomWidgetTemplate">
        <div class="o_module_name_widget" t-att-class="props.readonly ? 'o_readonly' : ''">
            <div class="o_widget_header">
                <h4>Custom Widget</h4>
                <button t-if="!props.readonly" class="btn btn-sm btn-primary" t-on-click="onSaveData">
                    Save
                </button>
            </div>
            <div class="o_widget_content">
                <t t-if="state.isLoading">
                    <div class="text-center">
                        <i class="fa fa-spinner fa-spin"/>
                        Loading...
                    </div>
                </t>
                <t t-else="">
                    <div t-if="state.data" t-esc="state.data.display_name"/>
                </t>
            </div>
        </div>
    </template>
</odoo>
```

## 📝 **XML View Development Standards**

### ✅ **Form View Template**
```xml
<record id="model_name_view_form" model="ir.ui.view">
    <field name="name">Model Name Form</field>
    <field name="model">module.model_name</field>
    <field name="arch" type="xml">
        <form string="Model Name">
            <!-- Header with statusbar -->
            <header>
                <button name="action_confirm" 
                        string="Confirm" 
                        type="object" 
                        class="btn-primary"
                        invisible="state != 'draft'"/>
                <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
            </header>
            
            <!-- Sheet layout -->
            <sheet>
                <div class="oe_title">
                    <label for="name" class="oe_edit_only"/>
                    <h1><field name="name" placeholder="Enter name..."/></h1>
                </div>
                
                <group>
                    <group>
                        <field name="partner_id"/>
                        <field name="date"/>
                    </group>
                    <group>
                        <field name="amount"/>
                        <field name="currency_id"/>
                    </group>
                </group>
                
                <!-- Notebook for tabs -->
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <tree editable="bottom">
                                <field name="name"/>
                                <field name="quantity"/>
                                <field name="price"/>
                                <field name="total"/>
                            </tree>
                        </field>
                    </page>
                    <page string="Notes" name="notes">
                        <field name="notes"/>
                    </page>
                </notebook>
            </sheet>
            
            <!-- Chatter -->
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### ✅ **List View Template**
```xml
<record id="model_name_view_tree" model="ir.ui.view">
    <field name="name">Model Name Tree</field>
    <field name="model">module.model_name</field>
    <field name="arch" type="xml">
        <tree string="Model Names" decoration-muted="state == 'draft'" decoration-success="state == 'done'">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="amount" sum="Total"/>
            <field name="state" widget="badge" decoration-warning="state == 'draft'" decoration-success="state == 'done'"/>
        </tree>
    </field>
</record>
```

## 🔐 **Security & Access Rights**

### ✅ **Access Rights (ir.model.access.csv)**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,access_model_user,model_module_model_name,base.group_user,1,1,1,0
access_model_manager,access_model_manager,model_module_model_name,base.group_system,1,1,1,1
```

### ✅ **Security Groups (security.xml)**
```xml
<odoo>
    <!-- Security Groups -->
    <record model="res.groups" id="group_module_user">
        <field name="name">Module User</field>
        <field name="category_id" ref="base.module_category_administration"/>
    </record>
    
    <record model="res.groups" id="group_module_manager">
        <field name="name">Module Manager</field>
        <field name="category_id" ref="base.module_category_administration"/>
        <field name="implied_ids" eval="[(4, ref('group_module_user'))]"/>
    </record>
    
    <!-- Record Rules -->
    <record model="ir.rule" id="rule_model_user">
        <field name="name">Model: User Access</field>
        <field name="model_id" ref="model_module_model_name"/>
        <field name="domain_force">[('create_uid', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_module_user'))]"/>
    </record>
</odoo>
```

## 🧪 **Testing Standards**

### ✅ **Unit Test Template**
```python
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError

class TestCustomModel(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Model = self.env['module.model_name']
        self.partner = self.env.ref('base.res_partner_1')
        
    def test_create_model(self):
        """Test model creation with valid data"""
        model = self.Model.create({
            'name': 'Test Model',
            'partner_id': self.partner.id,
        })
        self.assertEqual(model.state, 'draft')
        self.assertEqual(model.partner_id, self.partner)
        
    def test_model_constraints(self):
        """Test model constraints"""
        with self.assertRaises(ValidationError):
            self.Model.create({
                'name': 'AB',  # Too short
                'partner_id': self.partner.id,
            })
            
    def test_action_confirm(self):
        """Test confirm action"""
        model = self.Model.create({
            'name': 'Test Model',
            'partner_id': self.partner.id,
        })
        model.action_confirm()
        self.assertEqual(model.state, 'confirmed')
        
    def test_compute_methods(self):
        """Test computed fields"""
        model = self.Model.create({
            'name': 'Test Model',
            'partner_id': self.partner.id,
        })
        # Add test data and verify computations
        self.assertEqual(model.total_amount, 0.0)
```

## 🏗️ **Workflow & State Management**

### ✅ **State Machine Pattern**
```python
class WorkflowModel(models.Model):
    _name = 'module.workflow_model'
    _description = 'Workflow Model'
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)
    
    def action_submit(self):
        """Submit for approval"""
        if self.state != 'draft':
            raise UserError(_("Only draft records can be submitted"))
        self.state = 'submitted'
        self._notify_approvers()
        
    def action_approve(self):
        """Approve the record"""
        if self.state != 'submitted':
            raise UserError(_("Only submitted records can be approved"))
        self.state = 'approved'
        self._send_approval_notification()
        
    def action_reject(self):
        """Reject the record"""
        if self.state not in ['submitted', 'approved']:
            raise UserError(_("Only submitted or approved records can be rejected"))
        self.state = 'rejected'
        self._send_rejection_notification()
        
    def _notify_approvers(self):
        """Send notification to approvers"""
        template = self.env.ref('module.email_template_approval_request')
        for approver in self._get_approvers():
            template.send_mail(self.id, force_send=True, email_values={
                'email_to': approver.email
            })
```

## 📊 **Reports & QWeb Templates**

### ✅ **QWeb Report Template**
```xml
<template id="report_model_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <div class="page">
                <div class="oe_structure"/>
                
                <!-- Header -->
                <div class="row">
                    <div class="col-6">
                        <img t-if="company.logo" t-att-src="image_data_uri(company.logo)" 
                             alt="Logo" style="max-height: 45px;"/>
                    </div>
                    <div class="col-6 text-right">
                        <h3>
                            <span t-field="o.name"/>
                        </h3>
                    </div>
                </div>
                
                <!-- Content -->
                <div class="row mt32">
                    <div class="col-6">
                        <strong>Partner:</strong>
                        <div t-field="o.partner_id"/>
                    </div>
                    <div class="col-6">
                        <strong>Date:</strong>
                        <div t-field="o.date"/>
                    </div>
                </div>
                
                <!-- Table -->
                <table class="table table-sm o_main_table mt32">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th class="text-right">Quantity</th>
                            <th class="text-right">Price</th>
                            <th class="text-right">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr t-foreach="o.line_ids" t-as="line">
                            <td><span t-field="line.name"/></td>
                            <td class="text-right"><span t-field="line.quantity"/></td>
                            <td class="text-right"><span t-field="line.price"/></td>
                            <td class="text-right"><span t-field="line.total"/></td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="oe_structure"/>
            </div>
        </t>
    </t>
</template>
```

## 🏢 **OSUSAPPS Project-Specific Patterns**

### 🔧 **Developer Workflows**
+ **Start/Stop**: Use setup scripts or `docker-compose up -d` / `docker-compose down`.
+ **Logs**: `docker-compose logs -f odoo`
+ **DB backup/restore**: See project root scripts and `docker-compose` commands.
+ **Update all modules**: `docker-compose exec odoo odoo --update=all --stop-after-init`
+ **Update single module**: `docker-compose exec odoo odoo --update=module_name --stop-after-init`
+ **Run tests**: `docker-compose exec odoo odoo --test-enable --log-level=test --stop-after-init -d odoo -i module_name`
+ **Enter Odoo shell**: `docker-compose exec odoo bash`
+ **Module install**: Copy to repo, update app list in Odoo UI, then install from Apps menu.

### 🎯 **Project Conventions & Patterns**
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

### 🔗 **Integration & Cross-Component Patterns**
+ **Excel export**: Use `report_xlsx` if available, but degrade gracefully if not (see `account_statement/`).
+ **Multi-app integration**: Some modules (e.g. `account_statement/`) add features to both Contacts and Accounting apps.
+ **Security**: Multi-level permissions and record rules (see `payment_account_enhanced/security/`, `account_statement/security/`).
+ **REST API**: Some modules expose REST endpoints (see `payment_account_enhanced/controllers/main.py`, `custom_sales/api/`).
+ **Mobile/responsive**: Dashboards and reports are designed for mobile (see `custom_sales/`).
+ **Email notifications**: Use Odoo mail templates for workflow events (see `payment_account_enhanced/data/mail_template_data.xml`).
+ **QR code verification**: Use public and JSON endpoints for payment verification (see `payment_account_enhanced/controllers/main.py`).

## ⚠️ **Common Issues & Troubleshooting**
+ **DB errors**: If cron jobs fail, check `fix_cron_in_odoo.py`.
+ **Duplicate records**: See `fix_duplicate_partners.py` for deduplication logic.
+ **JS errors**: Run `fix_dashboard_js.py` for dashboard JS issues.
+ **Permission errors**: Check `ir.model.access.csv` and security groups.
+ **Module dependencies**: Ensure all dependencies are in `__manifest__.py` before install.
+ **Excel export**: If not available, check `xlsxwriter` and `report_xlsx` install.
+ **Voucher template errors**: See `PAYMENT_VOUCHER_FIX_SUMMARY.md` for common template issues and fixes.
+ **Approval workflow issues**: Check `payment_account_enhanced/models/payment_approval_history.py` for audit trail and debugging.

## 🚨 **Critical Anti-Patterns (NEVER DO)**

### ❌ **Forbidden Practices**
```python
# ❌ Don't use old API patterns
@api.multi
def old_method(self):  # Forbidden in Odoo 17

# ❌ Don't use deprecated decorators
@api.one
def another_old_method(self):  # Forbidden

# ❌ Don't bypass security
self.env['model'].sudo().search([])  # Use with extreme caution

# ❌ Don't hardcode IDs
record = self.env.ref('module.hardcoded_id')  # Use xmlids properly
```

```xml
<!-- ❌ Forbidden XML patterns -->
<field name="field" states="draft,sent"/>  <!-- Use invisible="" instead -->
<field name="field" attrs="{'invisible': [('state', '=', 'draft')]}"/>  <!-- Use invisible="" -->
```

```javascript
// ❌ Forbidden JavaScript patterns
$('.selector').click();  // Don't use jQuery in new code
odoo.define();  // Use /** @odoo-module **/ instead
```

### ✅ **Required Practices**
```python
# ✅ Modern Odoo 17 patterns
@api.depends('field')
def _compute_something(self):
    for record in self:
        record.computed_field = record.field * 2

# ✅ Proper error handling
try:
    result = self._risky_operation()
except Exception as e:
    _logger.error("Operation failed: %s", e)
    raise UserError(_("Operation failed. Please contact administrator."))

# ✅ Proper security checks
self.check_access_rights('write')
self.check_access_rule('write')
```

## 📋 **Manifest File Template**
```python
{
    'name': 'Module Name',
    'version': '17.0.1.0.0',
    'category': 'Appropriate Category',
    'summary': 'Brief module description',
    'description': """
        Detailed module description
        Key features and functionality
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/menus.xml',
        'views/model_views.xml',
        'reports/report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'module/static/src/scss/**/*.scss',
            'module/static/src/js/**/*.js',
        ],
        'web.assets_frontend': [
            'module/static/src/scss/frontend.scss',
            'module/static/src/js/frontend.js',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
```

## 🎯 **AI Agent Guidelines**
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

## 📚 **Additional Resources**
+ **Syntax Guidelines**: See `ODOO17_SYNTAX_GUIDELINES.md` for detailed migration examples
+ **VS Code Setup**: See `instruction for copilot.md` for development environment configuration
+ **Module Examples**: Reference `account_payment_final/`, `payment_account_enhanced/`, `custom_sales/`
+ **Usage Guide**: See `COPILOT_INSTRUCTIONS_GUIDE.md` for how these instructions work

**🚀 Remember**: This is an Odoo 17 production environment. Always use modern syntax, follow security best practices, and maintain compatibility with the existing OSUSAPPS ecosystem. When in doubt, reference the existing high-quality modules for proven patterns.

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
