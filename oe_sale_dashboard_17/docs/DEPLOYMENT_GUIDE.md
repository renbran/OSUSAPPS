# Odoo 17 Dashboard Module Deployment Guide

## Pre-Deployment Checklist

### 1. **Verify Dependencies**
```bash
# Check if required modules exist in your Odoo instance
python3 odoo-bin shell -d your_database_name
>>> env['ir.module.module'].search([('name', 'in', ['osus_invoice_report', 'le_sale_type'])])
```

### 2. **Update Manifest File**
```python
# __manifest__.py - Updated version
{
    'name': 'OSUS Executive Sales Dashboard',
    'version': '17.0.0.1.2',  # Increment version
    'category': 'Sales',
    'depends': ['web', 'sale_management'],  # Remove custom dependencies temporarily
    'external_dependencies': {
        'python': [],
    },
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js',
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
            'oe_sale_dashboard_17/static/src/scss/dashboard.scss',
        ],
    },
}
```

### 3. **Enhanced Error Handling**
```javascript
// Add to dashboard.js - Improved error handling
setup() {
    super.setup();
    
    // Wrap all async operations
    this._safeAsyncOperation = async (operation, errorMessage) => {
        try {
            return await operation();
        } catch (error) {
            console.error(`${errorMessage}:`, error);
            this.notification.add(_t(`${errorMessage}. Please contact administrator.`), { 
                type: 'danger' 
            });
            return null;
        }
    };
}

async _loadDashboardData() {
    return this._safeAsyncOperation(async () => {
        // Your existing dashboard loading logic
    }, "Failed to load dashboard data");
}
```

### 4. **Template Safety**
```xml
<!-- Ensure your template has proper structure -->
<templates>
    <t t-name="oe_sale_dashboard_17.yearly_sales_dashboard_template">
        <div class="o_oe_sale_dashboard_17_container">
            <!-- Loading state -->
            <div t-if="state.isLoading" class="loading-overlay">
                <div class="spinner"></div>
                <p>Loading dashboard...</p>
            </div>
            
            <!-- Main content -->
            <div t-else="">
                <!-- KPI Section -->
                <section id="kpi-section">
                    <div class="o_oe_sale_dashboard_17_container__kpi-grid"></div>
                </section>
                
                <!-- Charts Section -->
                <section id="charts-section">
                    <canvas id="revenueChart"></canvas>
                    <canvas id="trendChart"></canvas>
                </section>
                
                <!-- Data Tables -->
                <section id="quotations-section">
                    <!-- Quotations table -->
                </section>
            </div>
        </div>
    </t>
</templates>
```

### 5. **Field Validation Function**
```javascript
// Add to dashboard.js
async _validateRequiredFields() {
    const requiredFields = ['booking_date', 'sale_value', 'amount_total'];
    const missingFields = [];
    
    try {
        const modelFields = await this.orm.call("sale.order", "fields_get");
        
        requiredFields.forEach(field => {
            if (!modelFields[field]) {
                missingFields.push(field);
            }
        });
        
        if (missingFields.length > 0) {
            console.warn('Missing fields:', missingFields);
            this.notification.add(_t(`Missing required fields: ${missingFields.join(', ')}`), { 
                type: 'warning' 
            });
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Field validation error:', error);
        return false;
    }
}

// Call this in setup()
onMounted(async () => {
    const isValid = await this._validateRequiredFields();
    if (isValid) {
        await this._loadDashboardData();
    }
});
```

## Deployment Steps

### Step 1: Pre-deployment Testing
```bash
# Test module syntax
python3 -m py_compile __manifest__.py

# Check for JavaScript syntax errors
node -c static/src/js/dashboard.js
```

### Step 2: Gradual Deployment
```bash
# 1. Install in development mode first
python3 odoo-bin -d test_database -i oe_sale_dashboard_17 --dev=all

# 2. Check logs for errors
tail -f odoo.log | grep -i error

# 3. Test in browser console
# Look for JavaScript errors in browser developer tools
```

### Step 3: Database Migration Safety
```python
# Add to __init__.py if needed
def pre_init_hook(cr):
    """Check dependencies before installation"""
    cr.execute("SELECT name FROM ir_module_module WHERE name IN ('osus_invoice_report', 'le_sale_type') AND state = 'installed'")
    installed_deps = [row[0] for row in cr.fetchall()]
    
    if len(installed_deps) < 2:
        raise Exception(f"Required dependencies not installed: {installed_deps}")
```

### Step 4: Production Deployment
```bash
# 1. Update module
python3 odoo-bin -d production_db -u oe_sale_dashboard_17

# 2. Clear assets cache
python3 odoo-bin -d production_db --dev=all # temporarily for asset reload

# 3. Test all functionality
```

## Common Error Solutions

### Error: "Chart is not defined"
**Solution**: Ensure Chart.js loads before your dashboard script:
```xml
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
```

### Error: "Cannot read property of null"
**Solution**: Always check DOM elements exist:
```javascript
const element = document.querySelector('.my-element');
if (!element) return;
```

### Error: "Field 'booking_date' does not exist"
**Solution**: Add field existence checks and fallbacks:
```javascript
const domain = [];
if (await this._fieldExists('booking_date')) {
    domain.push(['booking_date', '>=', start_date]);
} else {
    domain.push(['date_order', '>=', start_date]);
}
```

### Error: "Template not found"
**Solution**: Check template name matches exactly:
```javascript
// In JavaScript
OeSaleDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";

// In XML
<t t-name="oe_sale_dashboard_17.yearly_sales_dashboard_template">
```

## Post-Deployment Monitoring

1. **Monitor Server Logs**: `tail -f odoo.log | grep -i dashboard`
2. **Check Browser Console**: Look for JavaScript errors
3. **Test All Features**: Date changes, chart interactions, data loading
4. **Performance Check**: Monitor database query performance
5. **User Feedback**: Collect feedback on usability and bugs

## Rollback Plan

If deployment fails:
```bash
# 1. Uninstall module
python3 odoo-bin -d database_name --uninstall oe_sale_dashboard_17

# 2. Restore from backup if needed
pg_restore -d database_name backup_file.dump

# 3. Fix issues and retry
```

## Additional CloudPepper Deployment Notes

### Chart.js CDN Fallback Configuration
Since we've recently fixed the JavaScript syntax errors related to Chart.js loading, make sure to include both the primary CDN and the fallback mechanism:

```python
# In __manifest__.py
'assets': {
    'web.assets_backend': [
        # Primary CDN loading for Chart.js
        'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js',
        # Module assets with fallbacks
        'oe_sale_dashboard_17/static/src/js/chart.fallback.js',  # Load this before dashboard.js
        'oe_sale_dashboard_17/static/src/js/dashboard.js',
        'oe_sale_dashboard_17/static/src/js/compatibility.js',
    ],
}
```

### Post-Fix Validation
After deploying the latest version with the syntax error fixes, run the following checks:

```bash
# Check for JavaScript errors in browser console
# Look for "SyntaxError: Missing catch or finally after try" - this should be resolved

# Verify all dashboard features are working
# - Chart rendering
# - Data loading
# - User interactions
```

### CloudPepper-Specific Configuration
For CloudPepper environments, ensure the following:

1. Clear the assets cache completely after deployment
2. Check server RAM usage during dashboard rendering
3. Monitor network traffic when loading Chart.js from CDN
4. Consider pre-loading critical assets for performance
