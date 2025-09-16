# Commission Modules Deprecation Plan

This document outlines the plan for safely deprecating redundant functions across the `commission_ax` and `commission_partner_statement` modules while maintaining backward compatibility.

## Redundant Functions Identified

After thorough analysis, we've identified the following redundant functions that can be consolidated:

### 1. Excel Report Generation

**Duplicate Functions:**

- `_generate_xlsx` in `commission_ax/wizards/commission_report_wizard.py`
- `_generate_excel_report` in `commission_partner_statement/wizards/scholarix_commission_report_wizard.py`

**Deprecation Strategy:**

1. Create a unified utility function in `commission_ax/utils/excel_utils.py`
2. Update existing functions to use the unified utility with a deprecation warning
3. Maintain backward compatibility through function forwarding

**Implementation:**

```python
# New utility function
# commission_ax/utils/excel_utils.py
def generate_excel_report(data, format_options=None):
    """
    Unified Excel report generation function
    
    Args:
        data (dict): Report data to be included
        format_options (dict): Optional formatting parameters
        
    Returns:
        bytes: Excel file data
    """
    # Implementation of shared Excel generation logic
    return excel_data

# Deprecation of existing function in commission_ax
# commission_ax/wizards/commission_report_wizard.py
def _generate_xlsx(self, lines, company, currency):
    """
    @deprecated: Use commission_ax.utils.excel_utils.generate_excel_report instead.
    This function will be removed in version 18.0
    """
    import warnings
    warnings.warn(
        "The _generate_xlsx function is deprecated. Use commission_ax.utils.excel_utils.generate_excel_report instead.",
        DeprecationWarning, stacklevel=2
    )
    from odoo.addons.commission_ax.utils.excel_utils import generate_excel_report
    return generate_excel_report({
        'lines': lines,
        'company': company,
        'currency': currency
    })
```

### 2. Period Selection Logic

**Duplicate Functions:**

- Date range calculations in both wizard modules

**Deprecation Strategy:**

1. Extract common period selection logic to `commission_ax/utils/date_utils.py`
2. Update existing methods to use the common utility
3. Add deprecation warnings to the original methods

**Implementation:**

```python
# New date utility
# commission_ax/utils/date_utils.py
def get_date_range(period_type, base_date=None):
    """
    Get standardized date ranges based on period type
    
    Args:
        period_type (str): Type of period (current_month, last_month, etc.)
        base_date (datetime.date, optional): Reference date, defaults to today
        
    Returns:
        tuple: (start_date, end_date)
    """
    from datetime import datetime, date, timedelta
    from dateutil.relativedelta import relativedelta
    
    today = base_date or date.today()
    
    ranges = {
        'current_month': (
            today.replace(day=1),
            (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1))
        ),
        'last_month': (
            (today.replace(day=1) - relativedelta(months=1)),
            (today.replace(day=1) - timedelta(days=1))
        ),
        # Add other period types...
    }
    
    return ranges.get(period_type, (None, None))
```

### 3. Commission Calculation Logic

**Duplicate Functions:**

- Commission calculation in `sale_order.py` of both modules

**Deprecation Strategy:**

1. Create a base commission calculation model
2. Move core logic to the base model
3. Refactor existing functions to use the base logic

**Implementation:**

```python
# New base commission model
# commission_ax/models/commission_calculation.py
class CommissionCalculation(models.AbstractModel):
    _name = 'commission.calculation'
    _description = 'Commission Calculation Base'
    
    @api.model
    def calculate_commission(self, base_amount, commission_type, rate, fixed_amount=0.0):
        """
        Unified commission calculation function
        
        Args:
            base_amount (float): Base amount for calculation
            commission_type (str): Type of commission calculation
            rate (float): Commission rate (percentage)
            fixed_amount (float): Fixed amount for 'fixed' type
            
        Returns:
            float: Calculated commission amount
        """
        if commission_type == 'fixed':
            return fixed_amount
        elif commission_type == 'percent_unit_price':
            return base_amount * (rate / 100.0)
        elif commission_type == 'percent_untaxed_total':
            return base_amount * (rate / 100.0)
        return 0.0
```

## Implementation Schedule

1. **Phase 1: Create Unified Utilities**
   - Create utility modules for Excel/PDF generation
   - Create date utility functions
   - Create commission calculation base model

2. **Phase 2: Update commission_ax Module**
   - Update existing functions to use new utilities
   - Add deprecation warnings to old functions
   - Update documentation

3. **Phase 3: Update commission_partner_statement Module**
   - Update to use utilities from commission_ax
   - Remove duplicated code
   - Add compatibility layers as needed

4. **Phase 4: Testing and Documentation**
   - Test all functionality for backward compatibility
   - Update API documentation with migration guides
   - Create examples for using the new utilities

## Backward Compatibility Guarantees

1. All deprecated functions will continue to work in Odoo 17
2. Deprecation warnings will indicate the new approach
3. Full removal will only occur in Odoo 18
4. Data model changes will include migration scripts

## Deprecation Timeline

| Phase | Timing | Action |
|-------|--------|--------|
| 1 | Immediate | Add unified utilities and base models |
| 2 | +1 month | Add deprecation warnings to old functions |
| 3 | +3 months | Document migration path for custom modules |
| 4 | Odoo 18 | Remove deprecated functions |

## Testing Strategy

1. Unit tests for new utility functions
2. Integration tests with both old and new approaches
3. Backward compatibility tests with existing data
4. Performance comparison tests

## Communication Plan

1. Update module README files with deprecation notices
2. Add inline code comments and warnings
3. Create migration guides for developers
4. Document all changes in the changelog
