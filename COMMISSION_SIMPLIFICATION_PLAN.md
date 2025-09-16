# Commission Modules Simplification Plan

## Overview

This document outlines the plan to simplify and improve the two related commission modules: `commission_ax` and `commission_partner_statement`. The goal is to eliminate duplication, simplify installation, and make the modules easier to maintain and use.

## Current Structure Analysis

After analyzing both modules, we've identified the following issues:

### Duplicate Functionality

1. **Excel Report Generation**: Both modules implement their own Excel export functions
2. **PDF Report Generation**: Separate PDF report generation logic
3. **Period Selection**: Similar date range selection in both wizards
4. **Commission Calculation**: Overlapping commission calculation logic

### Complex Structure

1. **Mixed Data Models**: Commission data split between sale orders and separate commission statement models
2. **Dependency Issues**: Tight coupling between modules without clear separation of concerns
3. **Redundant Wizards**: Similar wizard implementations across modules

### Installation Issues

1. **Dependency Chains**: Complex dependencies make installation error-prone
2. **Inconsistent Data Models**: Mixed data models cause migration challenges

## Simplification Plan

### 1. Unified Core Model

Create a unified commission data model with:

```python
# In commission_ax/models/commission_base.py
class CommissionBase(models.AbstractModel):
    _name = 'commission.base'
    _description = 'Base Commission Model'
    
    partner_id = fields.Many2one('res.partner', string='Commission Agent')
    commission_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Commission Type", default='percent_untaxed_total')
    commission_rate = fields.Float(string="Commission Rate (%)")
    commission_amount = fields.Monetary(string="Commission Amount")
    
    # Common commission calculation methods
    def calculate_commission(self, base_amount):
        """Calculate commission based on type and rate"""
        self.ensure_one()
        if self.commission_type == 'fixed':
            return self.commission_amount
        elif self.commission_type == 'percent_unit_price':
            # Calculation for unit price
            return base_amount * (self.commission_rate / 100)
        elif self.commission_type == 'percent_untaxed_total':
            # Calculation for untaxed total
            return base_amount * (self.commission_rate / 100)
        return 0.0
```

### 2. Common Excel/PDF Utility Module

Create a utility module for report generation:

```python
# In commission_ax/utils/report_utils.py
class CommissionReportUtility:
    """Utility class for commission reporting functions"""
    
    @staticmethod
    def generate_excel_report(env, data, template_name='standard'):
        """Generate Excel report using standardized format"""
        # Standardized Excel generation logic
        pass
        
    @staticmethod
    def generate_pdf_report(env, data, template_name='standard'):
        """Generate PDF report using standardized format"""
        # Standardized PDF generation logic
        pass
```

### 3. Base Wizard Design

Create a base wizard that can be extended:

```python
# In commission_ax/wizards/commission_report_wizard_base.py
class CommissionReportWizardBase(models.TransientModel):
    _name = 'commission.report.wizard.base'
    _description = 'Base Commission Report Wizard'
    
    # Common fields for all commission reports
    period_start = fields.Date(string='Period Start')
    period_end = fields.Date(string='Period End')
    
    # Common period selection logic
    period_type = fields.Selection([
        ('custom', 'Custom Period'),
        ('current_month', 'Current Month'),
        ('last_month', 'Last Month'),
        # ... other period types
    ])
    
    # Common methods
    @api.onchange('period_type')
    def _onchange_period_type(self):
        """Update period dates based on selection"""
        # Standard period selection logic
        pass
```

### 4. Module Restructuring

#### commission_ax (Base Module)

- Core commission models
- Base report utilities
- Common wizard functionality
- Standard report templates

#### commission_partner_statement (Extension Module)

- Extends commission_ax for SCHOLARIX specific needs
- Uses the base models and utilities from commission_ax
- Adds only SCHOLARIX-specific functionality

### 5. New Dependency Structure

```text
commission_ax (Base Module)
  ↑
  ├── Standard dependencies (sale, purchase, account)
  │
commission_partner_statement (Extension)
  ↑
  ├── commission_ax
  └── SCHOLARIX-specific dependencies
```

### 6. Installation Simplification

1. Make commission_ax standalone and fully functional
2. Ensure commission_partner_statement cleanly extends without duplication
3. Provide clear error messages for any missing dependencies
4. Create migration scripts for existing data

## Implementation Steps

1. Extract common utilities to commission_ax/utils
2. Create the base abstract model in commission_ax
3. Update commission_ax to use the new common utilities
4. Refactor commission_partner_statement to extend rather than duplicate
5. Update manifests to reflect new structure
6. Create comprehensive documentation
7. Test installation and functionality

## Migration Considerations

- Create a data migration script for existing installations
- Provide a guide for upgrading from existing dual-module setup
- Consider backward compatibility for API changes

## Documentation

Comprehensive documentation will be created covering:

- Installation guide
- Module relationship explanation
- Customization guide
- API reference
