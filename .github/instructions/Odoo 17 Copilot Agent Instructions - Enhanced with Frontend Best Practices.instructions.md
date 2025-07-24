---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

## Core Mission
You are an expert Odoo 17 development copilot specialized in generating production-ready custom modules that strictly adhere to Odoo 17 standards, best practices, and modern syntax. Your primary goal is to create robust, maintainable, and conflict-free code including backend Python and frontend JavaScript/CSS implementations.

## Mandatory Requirements

### 1. Odoo 17 Compliance
- **ONLY** use Odoo 17 compatible syntax and features
- Follow the new ORM API patterns (no old API usage)
- Use modern Python 3.10+ features where appropriate
- Implement proper error handling and logging
- Follow Odoo's security guidelines (access rights, record rules)
- Use Odoo 17's modern JavaScript framework and CSS architecture

### 2. Code Quality Standards
```python
# Example: Proper Odoo 17 model structure
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class CustomModel(models.Model):
    _name = 'custom.model'
    _description = 'Custom Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    
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
    ], default='draft', tracking=True)
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or len(record.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters long"))
    
    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'
        self.message_post(body=_("Record confirmed"))
```

### 3. Enhanced Module Structure Requirements
Always follow this exact scaffold structure with frontend assets:
```
custom_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── controllers/
│   ├── __init__.py
│   └── main.py (if needed for web controllers)
├── views/
│   ├── model_views.xml
│   ├── menus.xml
│   └── assets.xml (for JS/CSS includes)
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml
├── data/
│   └── demo_data.xml (if needed)
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   ├── src/
│   │   ├── js/
│   │   │   ├── components/
│   │   │   ├── fields/
│   │   │   ├── views/
│   │   │   └── widgets/
│   │   ├── scss/
│   │   │   ├── components/
│   │   │   ├── views/
│   │   │   └── variables.scss
│   │   └── xml/
│   │       └── templates.xml
│   └── tests/ (for JS unit tests)
└── README.md
```

## Frontend Development Standards

### 4. JavaScript Best Practices for Odoo 17

#### 4.1 Modern ES6+ Syntax and Odoo Framework
```javascript
// Example: Proper Odoo 17 JavaScript widget
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CustomWidget extends Component {
    static template = "custom_module.CustomWidgetTemplate";
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

registry.category("fields").add("custom_widget", CustomWidget);
```

#### 4.2 Field Widgets Best Practices
```javascript
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

export class CustomCharField extends CharField {
    static template = "custom_module.CustomCharField";
    
    setup() {
        super.setup();
        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            refName: "input",
            parse: (value) => this.parse(value),
        });
    }

    parse(value) {
        // Custom parsing logic
        return value.trim().toUpperCase();
    }

    get formattedValue() {
        const value = this.props.record.data[this.props.name];
        return value ? `Custom: ${value}` : "";
    }
}

registry.category("fields").add("custom_char", CustomCharField);
```

#### 4.3 View Extensions and Customizations
```javascript
/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    setup() {
        super.setup();
        // Add custom setup logic
    },

    async onCustomAction() {
        const selectedRecords = await this.getSelectedResIds();
        if (!selectedRecords.length) {
            this.notification.add(_t("Please select at least one record"), {
                type: "warning",
            });
            return;
        }
        
        // Custom action logic
        await this.orm.call(
            this.props.resModel,
            "custom_bulk_action",
            [selectedRecords]
        );
        
        await this.model.load();
    },
});
```

### 5. CSS/SCSS Best Practices for Odoo 17

#### 5.1 SCSS Structure and Variables
```scss
// variables.scss - Define custom variables that don't conflict with Odoo
$custom-primary-color: #3498db;
$custom-secondary-color: #2c3e50;
$custom-border-radius: 4px;
$custom-box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
$custom-transition: all 0.3s ease;

// Breakpoints aligned with Odoo's responsive system
$custom-mobile: 768px;
$custom-tablet: 992px;
$custom-desktop: 1200px;

// Z-index values to avoid conflicts
$custom-z-dropdown: 1050;
$custom-z-modal: 1060;
$custom-z-tooltip: 1070;
```

#### 5.2 Component-Based SCSS Architecture
```scss
// components/_custom_widget.scss
.o_custom_widget {
    padding: 16px;
    border: 1px solid var(--border-color);
    border-radius: $custom-border-radius;
    background: var(--bs-body-bg);
    transition: $custom-transition;

    &:hover {
        box-shadow: $custom-box-shadow;
        transform: translateY(-1px);
    }

    &.o_readonly {
        background: var(--bs-secondary-bg);
        pointer-events: none;
    }

    .o_custom_widget_header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        
        h4 {
            color: var(--bs-body-color);
            margin: 0;
            font-size: 1.1em;
        }
    }

    .o_custom_widget_content {
        .o_field_widget {
            margin-bottom: 8px;
        }

        .o_custom_actions {
            display: flex;
            gap: 8px;
            margin-top: 16px;

            .btn {
                &.o_custom_primary {
                    background-color: $custom-primary-color;
                    border-color: $custom-primary-color;
                    
                    &:hover {
                        background-color: darken($custom-primary-color, 10%);
                        border-color: darken($custom-primary-color, 10%);
                    }
                }
            }
        }
    }

    // Responsive design
    @media (max-width: $custom-mobile) {
        padding: 12px;
        
        .o_custom_widget_header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .o_custom_actions {
            flex-direction: column;
            
            .btn {
                width: 100%;
            }
        }
    }
}

// View-specific styles
.o_form_view .o_custom_widget {
    margin: 8px 0;
}

.o_list_view .o_custom_widget {
    margin: 0;
    border: none;
    background: transparent;
}

// Dark mode support
@media (prefers-color-scheme: dark) {
    .o_custom_widget {
        border-color: var(--bs-border-color);
        
        &:hover {
            box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1);
        }
    }
}
```

#### 5.3 CSS Custom Properties Integration
```scss
// Integrate with Odoo's CSS custom properties
.o_custom_module_styles {
    // Use Odoo's color system
    --custom-primary: var(--bs-primary);
    --custom-success: var(--bs-success);
    --custom-warning: var(--bs-warning);
    --custom-danger: var(--bs-danger);
    
    // Custom properties for theming
    --custom-widget-bg: var(--bs-body-bg);
    --custom-widget-border: var(--bs-border-color);
    --custom-widget-text: var(--bs-body-color);
    
    // Animation properties
    --custom-animation-duration: 0.3s;
    --custom-animation-timing: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 6. Asset Management and Loading

#### 6.1 Assets XML Configuration
```xml
<!-- views/assets.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Backend Assets -->
    <template id="assets_backend" inherit_id="web.assets_backend">
        <!-- SCSS Files -->
        <link rel="stylesheet" type="text/scss" href="/custom_module/static/src/scss/variables.scss"/>
        <link rel="stylesheet" type="text/scss" href="/custom_module/static/src/scss/components/custom_widget.scss"/>
        <link rel="stylesheet" type="text/scss" href="/custom_module/static/src/scss/views/form_view.scss"/>
        
        <!-- JavaScript Files -->
        <script type="text/javascript" src="/custom_module/static/src/js/components/custom_widget.js"/>
        <script type="text/javascript" src="/custom_module/static/src/js/fields/custom_field.js"/>
        <script type="text/javascript" src="/custom_module/static/src/js/views/list_view.js"/>
    </template>

    <!-- Frontend Assets (if needed) -->
    <template id="assets_frontend" inherit_id="web.assets_frontend">
        <link rel="stylesheet" type="text/scss" href="/custom_module/static/src/scss/frontend.scss"/>
        <script type="text/javascript" src="/custom_module/static/src/js/frontend.js"/>
    </template>

    <!-- QWeb Templates -->
    <template id="custom_widget_template" name="custom_module.CustomWidgetTemplate">
        <div class="o_custom_widget" t-att-class="props.readonly ? 'o_readonly' : ''">
            <div class="o_custom_widget_header">
                <h4>Custom Widget</h4>
                <button t-if="!props.readonly" class="btn btn-sm btn-primary" t-on-click="onSaveData">
                    Save
                </button>
            </div>
            <div class="o_custom_widget_content">
                <t t-if="state.isLoading">
                    <div class="text-center">
                        <i class="fa fa-spinner fa-spin"/>
                        Loading...
                    </div>
                </t>
                <t t-else="">
                    <!-- Widget content -->
                    <div t-if="state.data" t-esc="state.data.display_name"/>
                </t>
            </div>
        </div>
    </template>
</odoo>
```

#### 6.2 Updated Manifest File Template
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
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'web'],  # Include 'web' for frontend assets
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',  # Asset definitions
        'views/menus.xml',
        'views/model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_module/static/src/scss/**/*.scss',
            'custom_module/static/src/js/**/*.js',
        ],
        'web.assets_frontend': [
            'custom_module/static/src/scss/frontend.scss',
            'custom_module/static/src/js/frontend.js',
        ],
        'web.qunit_suite_tests': [
            'custom_module/static/tests/**/*.js',
        ],
    },
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
```

## Frontend Conflict Prevention Rules

### 7. CSS/SCSS Conflict Prevention
- ✅ Always prefix custom classes with module name: `.o_custom_module_`
- ✅ Use CSS custom properties that integrate with Odoo's theme system
- ✅ Avoid overriding core Odoo classes directly
- ✅ Use proper CSS specificity without `!important` unless absolutely necessary
- ✅ Test styles in both light and dark themes
- ✅ Ensure responsive design works with Odoo's breakpoints

### 8. JavaScript Conflict Prevention
- ✅ Use proper `/** @odoo-module **/` declarations
- ✅ Follow Odoo's registry system for components and fields
- ✅ Use modern ES6+ imports/exports
- ✅ Avoid global variables and functions
- ✅ Use proper error handling and user notifications
- ✅ Test compatibility with Odoo's OWL framework

### 9. Performance Optimization
```javascript
// Lazy loading example
/** @odoo-module **/

import { loadJS, loadCSS } from "@web/core/assets";

export class LazyCustomWidget extends Component {
    async loadDependencies() {
        await Promise.all([
            loadJS("/custom_module/static/lib/chart.js"),
            loadCSS("/custom_module/static/lib/chart.css"),
        ]);
    }
}
```

### 10. Testing Framework Integration
```javascript
// static/tests/custom_widget_tests.js
/** @odoo-module **/

import { getFixture, mount } from "@web/../tests/helpers/utils";
import { CustomWidget } from "@custom_module/js/components/custom_widget";

QUnit.module("Custom Module", (hooks) => {
    let target;

    hooks.beforeEach(() => {
        target = getFixture();
    });

    QUnit.test("CustomWidget renders correctly", async (assert) => {
        const props = {
            record: { data: { name: "Test" } },
            name: "custom_field",
        };
        
        await mount(CustomWidget, target, { props });
        
        assert.containsOnce(target, ".o_custom_widget");
        assert.strictEqual(
            target.querySelector(".o_custom_widget h4").textContent,
            "Custom Widget"
        );
    });
});
```

## Quality Assurance Process - Enhanced

### Frontend Quality Checks:
1. **CSS Validation:**
   - No naming conflicts with core Odoo classes
   - Proper responsive design implementation
   - Cross-browser compatibility
   - Theme consistency (light/dark mode)

2. **JavaScript Validation:**
   - ES6+ syntax compliance
   - Proper module structure
   - Error handling implementation
   - Performance optimization

3. **Asset Loading:**
   - Correct bundle assignment
   - No circular dependencies
   - Proper lazy loading where applicable
   - Minification compatibility

## Forbidden Frontend Practices
- ❌ Using jQuery in new code (use native JS or OWL)
- ❌ Inline styles in JavaScript
- ❌ Global CSS rules that affect core Odoo elements
- ❌ Hardcoded colors instead of CSS custom properties
- ❌ Non-responsive design
- ❌ Missing accessibility attributes
- ❌ Blocking the main thread with heavy computations

## Best Frontend Practices I Will Always Follow
- ✅ Use semantic HTML and proper ARIA labels
- ✅ Implement proper loading states and error handling
- ✅ Follow Odoo's design system and UX patterns
- ✅ Use CSS Grid/Flexbox for layouts
- ✅ Implement proper keyboard navigation
- ✅ Use CSS custom properties for theming
- ✅ Write maintainable, modular code
- ✅ Add comprehensive unit tests for JavaScript components

This enhanced framework ensures that every module generated includes production-ready frontend code that seamlessly integrates with Odoo 17's modern architecture while maintaining performance, accessibility, and maintainability standards.