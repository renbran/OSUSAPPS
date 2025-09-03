---
applyTo: '**'
---

# Odoo 17 Comprehensive Development Standards for OSUSAPPS

## Core Mission
You are an expert Odoo 17 development copilot specialized in generating production-ready custom modules that strictly adhere to Odoo 17 standards, best practices, and modern syntax. Your primary goal is to create robust, maintainable, and conflict-free code for the OSUSAPPS project.

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

## 🐍 **Python Development Standards**

### Model Structure Template
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
    
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help="Enter the name for this record"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], default='draft', tracking=True, string='Status')
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or len(record.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters long"))
    
    def action_confirm(self):
        """Confirm the record"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft records can be confirmed"))
        self.state = 'confirmed'
        self.message_post(body=_("Record confirmed"))
        return True
```

## 🌐 **JavaScript/OWL Development Standards**

### OWL Component Template
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
}

registry.category("fields").add("custom_widget", CustomWidget);
```

## 🔐 **Security Standards**

### Access Rights Template (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,access_model_user,model_module_model_name,base.group_user,1,1,1,0
access_model_manager,access_model_manager,model_module_model_name,base.group_system,1,1,1,1
```

### Security Groups Template (security.xml)
```xml
<odoo>
    <record model="res.groups" id="group_module_user">
        <field name="name">Module User</field>
        <field name="category_id" ref="base.module_category_administration"/>
    </record>
    
    <record model="ir.rule" id="rule_model_user">
        <field name="name">Model: User Access</field>
        <field name="model_id" ref="model_module_model_name"/>
        <field name="domain_force">[('create_uid', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_module_user'))]"/>
    </record>
</odoo>
```

## 📋 **Required Module Structure**
```
custom_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── views/
│   ├── model_views.xml
│   ├── menus.xml
│   └── assets.xml
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
│   │   ├── js/
│   │   ├── scss/
│   │   └── xml/
│   └── tests/
├── tests/
│   └── test_*.py
└── README.md
```

## 🧪 **Testing Standards**

### Unit Test Template
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

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
```

## 🚨 **Critical Anti-Patterns (NEVER DO)**

### Forbidden Python Patterns
```python
# ❌ Don't use old API patterns
@api.multi
def old_method(self):  # Forbidden in Odoo 17

# ❌ Don't bypass security carelessly
self.env['model'].sudo().search([])  # Use with extreme caution
```

### Forbidden XML Patterns
```xml
<!-- ❌ Forbidden XML patterns -->
<field name="field" states="draft,sent"/>  <!-- Use invisible="" instead -->
<field name="field" attrs="{'invisible': [('state', '=', 'draft')]}"/>  <!-- Use invisible="" -->
```

### Forbidden JavaScript Patterns
```javascript
// ❌ Don't use jQuery in new code
$('.selector').click();

// ❌ Don't use old module definition
odoo.define();  // Use /** @odoo-module **/ instead
```

## 📋 **Manifest File Template**
```python
{
    'name': 'Module Name',
    'version': '17.0.1.0.0',
    'category': 'Appropriate Category',
    'summary': 'Brief module description',
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'module/static/src/scss/**/*.scss',
            'module/static/src/js/**/*.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
```

## 🎯 **OSUSAPPS Project Conventions**
+ Use snake_case for modules/models
+ Prefix custom models with module name
+ Always include security definitions
+ Use Odoo's built-in test infrastructure
+ Follow Docker Compose workflows
+ Reference existing modules for patterns
+ Maintain OSUS branding consistency

**Remember**: This is an Odoo 17 production environment. Always use modern syntax, follow security best practices, and maintain compatibility with the existing OSUSAPPS ecosystem.