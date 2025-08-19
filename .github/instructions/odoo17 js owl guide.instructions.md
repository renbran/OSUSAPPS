---
applyTo: '**'
---

# Odoo 17 Owl Components Development Guide for Copilot

## Overview
When developing Owl components for Odoo 17 portal and website integration, follow this comprehensive guide to ensure proper implementation and best practices.

## Core Implementation Steps

### 1. Component Structure Requirements

**Template File Location**: `/your_module/static/src/portal_component/your_component.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="your_module.YourComponent">
        <!-- Component content here -->
    </t>
</templates>
```

**JavaScript File Location**: `/your_module/static/src/portal_component/your_component.js`
```javascript
/** @odoo-module */
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry"

export class YourComponent extends Component {
    static template = "your_module.YourComponent";
    static props = {};
    // Add component logic here
}

registry.category("public_components").add("your_module.YourComponent", YourComponent);
```

### 2. Manifest Configuration

**Assets Bundle**: Always add to `web.assets_frontend` in `__manifest__.py`:
```python
{
    'assets': {
        'web.assets_frontend': [
            'your_module/static/src/portal_component/**/*',
        ],
    },
    'data': [
        'views/templates.xml',
    ]
}
```

### 3. Template Integration

**XML Template Usage**: Add to portal/website pages via inheritance:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="your_module.portal_extension" inherit_id="portal.portal_my_home">
        <xpath expr="//target_element" position="before|after|inside">
            <owl-component name="your_module.YourComponent" />
        </xpath>
    </template>
</odoo>
```

## Development Guidelines

### When to Use Owl Components
- **Portal pages** where SEO is not critical
- **Interactive features** requiring real-time user interaction
- **Dynamic content** that needs to update without page reload
- **User-specific interfaces** behind authentication

### When NOT to Use Owl Components
- **Public-facing content** that needs SEO optimization
- **Static content** that doesn't require interactivity
- **Above-the-fold content** that could cause layout shift
- **Simple forms** that can be handled server-side

### Best Practices

1. **Layout Considerations**:
   - Reserve fixed space for components using CSS
   - Position interactive components below static content
   - Avoid placing near other interactive elements

2. **Performance Optimization**:
   - Keep components lightweight
   - Use lazy loading when appropriate
   - Minimize initial render impact

3. **SEO Considerations**:
   - Use server-side rendering for indexable content
   - Reserve Owl for truly interactive features
   - Consider progressive enhancement approach

## Code Patterns to Follow

### Component Registration Pattern
```javascript
// Always register in public_components category
registry.category("public_components").add("module_name.ComponentName", ComponentClass);
```

### Template Naming Convention
```javascript
// Template name should match: module_name.ComponentName
static template = "your_module.YourComponent";
```

### File Organization
```
your_module/
├── static/src/portal_component/
│   ├── component_name.xml
│   └── component_name.js
└── views/
    └── templates.xml
```

## Common Issues to Avoid

1. **Missing Registry Registration**: Always add component to `public_components` registry
2. **Incorrect Bundle**: Use `web.assets_frontend`, not `web.assets_backend`
3. **Template Name Mismatch**: Ensure template name matches class reference
4. **Layout Shift**: Plan component placement to minimize content movement
5. **SEO Impact**: Don't use for content that needs search engine indexing

## Integration Checklist

- [ ] Component files created in correct directory structure
- [ ] Template properly defined with correct naming
- [ ] JavaScript class extends Component and registered
- [ ] Assets added to `web.assets_frontend` bundle
- [ ] Template XML file added to manifest data section
- [ ] `<owl-component>` tag added to target page
- [ ] Layout shift considerations addressed
- [ ] SEO impact evaluated

## Remember
Owl components in portal/website are client-side rendered, so use them strategically for interactive features while keeping SEO and user experience implications in mind.