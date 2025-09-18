# Commission Type Model RPC Error - Resolution Guide

## Problem Summary

**Error**: `Model not found: commission.type`  
**Source**: External module `commission_lines` attempting to reference `commission.type` model  
**Impact**: Module installation/update failures, view rendering errors

## Root Cause Analysis

The external `commission_lines` module contains views and logic that reference a `commission.type` model, but this model was not defined in any installed module. This creates a dependency issue where:

1. `commission_lines` expects `commission.type` to exist
2. No module was providing this model
3. Odoo fails during module loading/view parsing

## Solution Implemented

### 1. Created Commission Type Model

**File**: `commission_ax/models/commission_type.py`

```python
class CommissionType(models.Model):
    _name = 'commission.type'
    _description = 'Commission Type'
    _order = 'sequence, name'
    
    sequence = fields.Integer(default=10, help="Display order")
    name = fields.Char(string='Commission Type Name', required=True)
    code = fields.Char(string='Code', required=True)
```

**Features**:
- Sequence-based ordering
- Required name and code fields
- Input validation and constraints
- Default commission types creation method
- Enhanced search functionality

### 2. Updated Module Structure

**Updated Files**:
- `commission_ax/models/__init__.py` - Added commission_type import
- `commission_ax/security/ir.model.access.csv` - Added access rights
- `commission_ax/__manifest__.py` - Added data and view files
- `commission_ax/data/commission_type_data.xml` - Default commission types
- `commission_ax/views/commission_type_views.xml` - Management interface

### 3. Security Configuration

```csv
# User Access (Read-only)
access_commission_type_user,commission.type.user,commission_ax.model_commission_type,commission_ax.group_commission_user,1,0,0,0

# Manager Access (Full)
access_commission_type_manager,commission.type.manager,commission_ax.model_commission_type,commission_ax.group_commission_manager,1,1,1,1
```

## Resolution Steps

### For Local Development

1. **Update Module**:
   ```bash
   cd /path/to/OSUSAPPS
   ./update_commission_type.sh
   ```

2. **Manual Update** (if script fails):
   ```bash
   docker-compose exec odoo odoo --update=commission_ax --stop-after-init -d odoo
   docker-compose restart odoo
   ```

### For Staging/Production Servers

1. **Deploy Updated Code**:
   - Ensure `commission_ax` module contains the new commission_type model
   - Verify all files are properly uploaded

2. **Update Module**:
   ```bash
   # Method 1: Through Odoo CLI
   odoo --update=commission_ax --stop-after-init -d your_database

   # Method 2: Through Odoo UI
   # Apps > commission_ax > Upgrade
   ```

3. **Restart Odoo Service**:
   ```bash
   systemctl restart odoo  # or your service manager
   ```

## Verification Steps

### 1. Check Model Registration

```python
# In Odoo shell
env['commission.type'].search_count([])
# Should return count of commission types (4 default types)
```

### 2. Verify Default Data

```python
# In Odoo shell
for ct in env['commission.type'].search([]):
    print(f"{ct.name} ({ct.code})")
    
# Expected output:
# External Commission (EXTERNAL)
# Internal Commission (INTERNAL)
# Referral Commission (REFERRAL)
# Bonus Commission (BONUS)
```

### 3. Test External Module

- Install or update `commission_lines` module
- Verify no RPC errors occur
- Check that commission type views render correctly

## Prevention Measures

### 1. Dependency Management

Add explicit dependency in external modules:

```python
# In commission_lines/__manifest__.py
'depends': [
    'base',
    'commission_ax',  # Ensure commission.type model is available
    # ... other dependencies
],
```

### 2. Model Availability Checks

```python
# In external module code
if 'commission.type' in self.env:
    commission_types = self.env['commission.type'].search([])
else:
    # Handle missing model gracefully
    commission_types = []
```

### 3. Installation Order

Ensure `commission_ax` is installed before `commission_lines`:
1. Install `commission_ax` first
2. Update apps list
3. Install `commission_lines`

## Troubleshooting

### Issue: Still Getting RPC Error After Update

**Possible Causes**:
1. Module not properly updated
2. Cache issues
3. Different database
4. Installation order problems

**Solutions**:
```bash
# Clear cache and force update
odoo --update=commission_ax --stop-after-init --dev=reload

# Check if model is in correct database
odoo shell -d your_database
>>> env['ir.model'].search([('model', '=', 'commission.type')])

# Reinstall module completely
odoo --init=commission_ax --stop-after-init
```

### Issue: Access Rights Problems

**Symptoms**: Users can't see commission types
**Solution**: Update access rights in `ir.model.access.csv`

### Issue: View Definition Errors

**Symptoms**: Views not rendering correctly
**Solution**: Check XML syntax in `commission_type_views.xml`

## Module Integration

The `commission.type` model is designed to integrate with:

- **commission_lines**: External commission line management
- **commission_ax**: Core commission functionality  
- **sale**: Sales order commission calculation
- **purchase**: Commission purchase order generation

## Summary

✅ **Created** comprehensive commission.type model  
✅ **Added** security access controls  
✅ **Provided** default commission types  
✅ **Created** management interface  
✅ **Updated** module dependencies  
✅ **Documented** resolution process  

The commission.type model is now available and should resolve all RPC errors related to missing commission type model references.