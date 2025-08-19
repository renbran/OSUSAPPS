# ============================================================
# Odoo 17 OSUSAPPS Payment Approval Mega-Prompt
# Production-Ready 4-Stage Workflow with CloudPepper Optimization
# Based on account_payment_final patterns and OSUS branding
# ============================================================

## Context & Environment
- **Base Module**: Extending existing `account_payment_final` (or creating new `account_payment_approval`)
- **Odoo Version**: 17.0 with modern ORM patterns and OWL framework
- **Hosting**: CloudPepper optimization required (error suppression, asset order)
- **Branding**: OSUS Properties (#722f37 primary, #b8860b secondary)
- **Multi-company**: Domain fields need `groups="base.group_multi_company"` or alternative logic

## High-Level Requirements

### 1. Enhanced 4-Stage Workflow
**Payments (outbound)**: `draft → under_review → for_approval → approved → posted`
**Receipts (inbound)**: `draft → under_review → approved → posted`

### 2. OSUS Security Groups (Role-Based)
```
account_payment_final.group_payment_user       # Basic access
account_payment_final.group_payment_reviewer   # Can review payments  
account_payment_final.group_payment_approver   # Can approve payments
account_payment_final.group_payment_authorizer # Can authorize payments
account_payment_final.group_payment_manager    # Full administrative access
```

### 3. QR Code Verification System
- Generate secure QR codes with payment data encoding
- Public verification portal: `/verify/<int:payment_id>/<string:token>`
- Professional OSUS-branded verification page

### 4. CloudPepper Production Features
- Emergency error handling and console optimization
- Asset loading order compatible with CloudPepper hosting
- Performance-optimized JavaScript with OWL framework

## Required Folder Structure (OSUS Standards)
```
account_payment_final/
├── __manifest__.py                           # CloudPepper asset order
├── models/
│   ├── __init__.py
│   ├── account_payment.py                    # Main workflow model
│   ├── payment_approval_history.py          # Audit trail
│   ├── payment_workflow_stage.py            # Stage definitions
│   └── res_config_settings.py               # OSUS configuration
├── controllers/
│   ├── __init__.py
│   ├── main.py                              # Dashboard endpoints
│   └── payment_verification.py              # QR verification
├── security/
│   ├── ir.model.access.csv                  # Role-based access
│   └── payment_security.xml                 # Groups & record rules
├── views/
│   ├── account_payment_views.xml            # Form with statusbar
│   ├── menus.xml                            # OSUS navigation
│   └── payment_verification_templates.xml   # QR templates
├── reports/
│   ├── payment_voucher_actions.xml          # Report actions
│   ├── payment_voucher_report.xml           # Report definition
│   └── payment_voucher_template.xml         # 4-signature layout
├── data/
│   ├── email_templates.xml                  # Workflow notifications
│   ├── payment_sequences.xml               # OSUS numbering
│   └── system_parameters.xml               # Default settings
├── static/src/
│   ├── js/
│   │   ├── emergency_error_fix.js           # CloudPepper compatibility
│   │   ├── payment_dashboard.js             # OWL components
│   │   └── components/                      # Widget components
│   ├── scss/
│   │   ├── osus_branding.scss              # OSUS colors & fonts
│   │   ├── professional_payment_ui.scss    # Enhanced styling
│   │   └── components/                      # Component styles
│   └── xml/
│       └── payment_templates.xml           # OWL templates
├── tests/
│   ├── test_payment_workflow.py            # Workflow testing
│   ├── test_payment_security.py            # Security testing
│   └── test_payment_models.py              # Model testing
└── migrations/
    └── 17.0.1.1.0/
        ├── pre-migrate.py                   # DB upgrades
        └── post-migrate.py                  # Data migration
```

## OSUS Coding Standards & Patterns

### 1. Python Model Structure
```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import qrcode
import io
import base64
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'OSUS Payment with Approval Workflow'
    
    # State workflow with proper naming
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted')
    ], default='draft', tracking=True)
    
    # Audit trail fields
    reviewer_id = fields.Many2one('res.users', string='Reviewer', tracking=True)
    reviewed_date = fields.Datetime(string='Review Date', tracking=True)
    
    # QR code system
    qr_code = fields.Binary(string='QR Code')
    qr_token = fields.Char(string='QR Token', size=64)
```

### 2. Security XML with Multi-Company Fix
```xml
<!-- Always include groups for company_id domains -->
<field name="journal_id" 
       domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]"
       groups="base.group_multi_company"/>
```

### 3. CloudPepper Asset Configuration
```python
# __manifest__.py - Asset loading order matters
'assets': {
    'web.assets_backend': [
        # Emergency fixes load FIRST for stability
        'account_payment_final/static/src/js/emergency_error_fix.js',
        'account_payment_final/static/src/js/cloudpepper_compatibility_patch.js',
        
        # OSUS branding
        'account_payment_final/static/src/scss/osus_branding.scss',
        'account_payment_final/static/src/scss/professional_payment_ui.scss',
        
        # Core functionality
        'account_payment_final/static/src/js/payment_dashboard.js',
        'account_payment_final/static/src/js/components/*.js',
    ],
},
```

### 4. OWL JavaScript Components (Odoo 17)
```javascript
/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class OSUSPaymentWidget extends Component {
    static template = "account_payment_final.PaymentWidget";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: false,
            paymentData: null
        });
        
        onMounted(this.loadPaymentData);
    }
}

registry.category("fields").add("osus_payment_widget", OSUSPaymentWidget);
```

## Step-by-Step Generation Tasks

### Phase 1: Core Infrastructure
1. **Update `__manifest__.py`**
   - Add OSUS branding and CloudPepper asset order
   - Dependencies: `['base', 'account', 'mail', 'web']`
   - External dependencies: `['qrcode', 'pillow']`

2. **Extend `account.payment` model**
   - Add workflow state fields with proper tracking
   - Add user assignment fields (reviewer_id, approver_id, etc.)
   - Add QR code generation with secure token
   - Override `action_post()` with workflow validation

3. **Create security framework**
   - Define 5 OSUS security groups with proper inheritance
   - Create record rules for each workflow stage
   - Ensure multi-company compatibility

### Phase 2: UI & Workflow
4. **Design form views**
   - Statusbar with dynamic button visibility
   - OSUS-branded styling with professional colors
   - Smart buttons for workflow actions
   - Fix multi-company domain issues

5. **Implement workflow methods**
   - `action_submit_for_review()`
   - `action_approve()`
   - `action_authorize()`
   - `action_reject()` with reason tracking

6. **Create email notifications**
   - Workflow stage change templates
   - OSUS-branded email styling
   - Activity creation for assigned users

### Phase 3: Reports & Verification
7. **Design 4-signature PDF report**
   - OSUS company header with logo
   - Professional payment voucher layout
   - 4 signature boxes (Review, Approve, Authorize, Post)
   - QR code integration for verification

8. **Build QR verification system**
   - Public controller with token validation
   - Professional verification page with OSUS branding
   - Security checks and audit logging

9. **CloudPepper optimization**
   - Emergency error handling for production
   - Console error suppression
   - Asset loading performance optimization

### Phase 4: Testing & Production
10. **Comprehensive test suite**
    - Workflow state transitions
    - Security group permissions
    - QR verification endpoints
    - Multi-company scenarios

11. **Migration scripts**
    - Database upgrade procedures
    - Data migration for existing payments
    - Backward compatibility checks

## Output Requirements

### Code Quality Standards
- **Python**: PEP 8 compliant, 80 columns, 4-space indents
- **XML**: Proper structure with OSUS naming conventions
- **JavaScript**: Modern ES6+ with OWL framework patterns
- **SCSS**: OSUS brand colors and responsive design

### Production Readiness Checklist
- [ ] All files syntax validated
- [ ] CloudPepper compatibility confirmed
- [ ] Multi-company domain fixes applied
- [ ] OSUS branding consistently implemented
- [ ] Security groups and record rules tested
- [ ] Email templates and notifications working
- [ ] QR verification system functional
- [ ] Asset loading order optimized
- [ ] Error handling and logging implemented
- [ ] Test coverage for core workflows

### Error Prevention Patterns
```python
# Multi-company domain fix
@api.depends('company_id')
def _compute_available_journals(self):
    # Safe domain without company_id reference in XML
    pass

# CloudPepper error handling
try:
    # RPC calls with error catching
    result = self.env['model.name'].method()
except Exception as e:
    _logger.warning("CloudPepper: %s", e)
    # Graceful fallback
```

## Final Instructions

1. **Generate in order**: manifest → models → security → views → reports → controllers → assets
2. **Use exact naming**: Follow OSUS conventions and existing `account_payment_final` patterns
3. **Include comments**: Document CloudPepper optimizations and OSUS-specific logic
4. **Test integration**: Ensure compatibility with existing modules
5. **Validate syntax**: All files must be production-ready without errors

**Return ONLY complete, production-ready code blocks for each file.**
**Use proper Odoo 17 syntax with OSUS branding and CloudPepper optimization.**
**Follow the exact folder structure and naming conventions specified above.**
