# Commission Deals Report - Docker Testing Guide

## Overview

This document provides comprehensive testing instructions for the new Deals Commission Report functionality in the commission_ax module using Docker.

## Prerequisites

1. **Docker and Docker Compose** installed and running
2. **Git Bash** or Linux terminal (for Windows users)
3. **Available ports**: 8090 (Odoo), 5432 (PostgreSQL)

## Quick Test (Recommended)

### Step 1: Run Quick Test Script
```bash
cd "d:\GitHub\osus_main\cleanup osus\OSUSAPPS"
./quick_test_commission.sh
```

This script will:
- Start Docker containers
- Install the commission_ax module
- Test the new wizard model
- Start the Odoo web interface

### Step 2: Manual Testing in Odoo Web Interface

1. **Access Odoo**: http://localhost:8090
2. **Login**: admin/admin (default credentials)
3. **Navigate to**: Sales > Commission Reports > Comprehensive Deals Report
4. **Test the wizard**:
   - Set date range
   - Configure filters
   - Generate PDF and Excel reports

## Comprehensive Test

### Step 1: Module Validation
```bash
./validate_commission_module.sh
```

This validates:
- ✅ File structure completeness
- ✅ Manifest configuration
- ✅ Security access definitions
- ✅ Model imports

### Step 2: Full Docker Test
```bash
./test_commission_deals_report.sh
```

This performs:
- Container startup and health checks
- Module installation/upgrade
- Test data creation
- Wizard functionality testing
- Report generation testing

## Manual Testing Steps

### 1. Create Test Data

If you want to test with real data, create:

**Test Commission Partners:**
- Navigate to Contacts
- Create partners with supplier flag enabled
- Note their IDs for sale orders

**Test Sale Orders:**
- Navigate to Sales > Orders > Orders
- Create new sale orders with:
  - Customer information
  - Commission partners (Consultant, Manager, Director)
  - Commission rates and types
  - Project assignment (if available)

**Test Projects:**
- Navigate to Project (if module installed)
- Create test real estate projects
- Link to sale orders

### 2. Test Report Generation

**Access the Report:**
1. Sales > Commission Reports > Comprehensive Deals Report
2. Or use the action menu from any Sale Order

**Test Filters:**
- Date range filtering
- Partner-specific reports
- Project-specific reports
- Status filtering (eligible, processed, paid, pending)

**Test Options:**
- Include/exclude zero commissions
- Include/exclude draft orders
- Group by project
- Show payment details

**Test Output Formats:**
- PDF Report (professional formatted)
- Excel Export (detailed spreadsheet)

### 3. Verify Report Contents

The report should include:
- ✅ Deal/Order information
- ✅ Customer details
- ✅ Booking dates
- ✅ Project and unit information
- ✅ Commission partner details
- ✅ Eligible amounts
- ✅ Processed amounts
- ✅ Paid amounts
- ✅ Pending amounts
- ✅ Payment status

## Troubleshooting

### Common Issues

**1. Module Not Found**
```bash
# Reinstall the module
docker-compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -i commission_ax --stop-after-init
```

**2. Model Access Errors**
```bash
# Update module and security
docker-compose exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u commission_ax --stop-after-init
```

**3. Report Not Generating**
```bash
# Check logs
docker-compose logs odoo | grep -i error
```

**4. Menu Not Visible**
```bash
# Refresh browser and check user permissions
# Ensure user has Sales/User access rights
```

### Docker Issues

**Containers Not Starting:**
```bash
# Check Docker status
docker --version
docker-compose --version

# Start containers manually
docker-compose up -d db
sleep 10
docker-compose up -d odoo
```

**Port Conflicts:**
```bash
# Check if ports are in use
netstat -an | findstr :8090
netstat -an | findstr :5432

# Stop conflicting services or change ports in docker-compose.yml
```

### Module Issues

**Import Errors:**
- Check `wizards/__init__.py` includes the new wizard
- Check `__manifest__.py` includes all new files
- Check `security/ir.model.access.csv` has proper access rights

**XML Syntax Errors:**
- Validate XML files for syntax errors
- Check template references and IDs
- Ensure proper namespacing

## Expected Test Results

### Successful Installation
```
✅ Commission AX module status: installed
✅ Deals Commission Report Wizard model exists!
✅ Test wizard created successfully
```

### Report Generation
```
✅ Found X deals for report
✅ PDF Report action exists!
✅ Excel export working
```

### Web Interface
- Menu item visible under Sales > Commission Reports
- Wizard opens without errors
- Filters work correctly
- PDF and Excel generation successful

## Performance Testing

For performance testing with large datasets:

```bash
# Test with bulk data
docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo -c "
# Create 100 test sale orders
for i in range(100):
    # Create sale order with commission data
    pass
"
```

## Next Steps

After successful testing:

1. **Production Deployment**: Update production environment
2. **User Training**: Train users on new report functionality
3. **Data Migration**: Ensure existing commission data is compatible
4. **Performance Monitoring**: Monitor report generation performance
5. **User Feedback**: Collect feedback for improvements

## Support

For issues during testing:
1. Check container logs: `docker-compose logs`
2. Check Odoo logs: `docker-compose logs odoo`
3. Validate module structure: `./validate_commission_module.sh`
4. Review implementation files in commission_ax/

## Test Checklist

- [ ] Docker containers start successfully
- [ ] commission_ax module installs without errors
- [ ] Deals Commission Report Wizard model exists
- [ ] Menu item appears in Sales > Commission Reports
- [ ] Wizard opens and accepts input
- [ ] Filters work correctly
- [ ] PDF report generates successfully
- [ ] Excel export works
- [ ] Report contains all required data fields
- [ ] Performance is acceptable with test data
- [ ] No error messages in logs
