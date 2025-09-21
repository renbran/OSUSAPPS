# Sales Commission Module - Production Deployment Guide

## Prerequisites

- Odoo 17.0 or later
- PostgreSQL database
- Python 3.8+
- Required Odoo modules: `sale_management`, `account`

## Installation Steps

1. **Module Installation**
   ```bash
   # Copy module to Odoo addons directory
   cp -r sales_commission_users /path/to/odoo/addons/

   # Update module list
   odoo-bin -c /path/to/config.conf -d database_name -u all --stop-after-init

   # Install module
   odoo-bin -c /path/to/config.conf -d database_name -i sales_commission_users
   ```

2. **Database Considerations**
   - Create database indexes for performance:
     ```sql
     CREATE INDEX idx_commission_lines_sales_person ON commission_lines(sales_person_id);
     CREATE INDEX idx_commission_lines_date ON commission_lines(date);
     CREATE INDEX idx_sales_commission_type ON sales_commission(commission_type);
     ```

3. **Configuration Parameters**
   - Access Settings > Technical > Parameters > System Parameters
   - Configure the following parameters:
     - `sales_commission.max_percentage`: Maximum allowed commission percentage (default: 50.0)
     - `sales_commission.min_amount`: Minimum commission amount (default: 1.0)
     - `sales_commission.enable_logging`: Enable detailed logging (default: True)
     - `sales_commission.auto_invoice`: Auto-create invoices (default: False)

## Security Configuration

1. **User Groups**
   - Sales Managers: Full access to commission configuration and reporting
   - Sales Users: Read-only access to their own commission data

2. **Access Rights**
   - Commission configuration: Sales Manager only
   - Commission lines: Read-only for sales users, full access for managers
   - Reports: Both groups can generate reports

## Performance Optimization

1. **Database Tuning**
   - Enable database connection pooling
   - Configure appropriate `db_maxconn` in Odoo configuration
   - Set `max_cron_threads` based on server capacity

2. **Caching**
   - Configure Redis cache for session storage
   - Use CDN for static assets

3. **Logging Configuration**
   ```ini
   [logger_sales_commission]
   level = INFO
   handlers = h01
   qualname = odoo.addons.sales_commission_users
   ```

## Monitoring

1. **Key Metrics to Monitor**
   - Commission calculation errors
   - Invoice creation failures
   - Database query performance
   - Memory usage during bulk operations

2. **Log Files**
   - Monitor Odoo logs for commission-related errors
   - Set up log rotation for production environments

3. **Alerts**
   - Set up alerts for commission calculation failures
   - Monitor database deadlocks during order confirmation

## Backup Strategy

1. **Database Backups**
   - Daily full database backups
   - Transaction log backups every 15 minutes
   - Test backup restoration monthly

2. **Module Files**
   - Include custom module files in backup strategy
   - Version control all customizations

## Testing Procedures

1. **Pre-deployment Testing**
   - Test commission calculations with various scenarios
   - Verify invoice generation functionality
   - Test report generation with large datasets

2. **Post-deployment Verification**
   - Verify all commission types are working
   - Test user permissions
   - Validate report accuracy

## Troubleshooting

1. **Common Issues**
   - Commission not calculating: Check user permissions and commission configuration
   - Invoice creation fails: Verify accounting configuration and user access rights
   - Reports showing no data: Check date filters and commission line creation

2. **Performance Issues**
   - Enable database query logging
   - Monitor system resources during peak usage
   - Consider batch processing for large commission calculations

## Maintenance

1. **Regular Tasks**
   - Archive old commission data quarterly
   - Update commission percentages as needed
   - Review and clean up obsolete commission rules

2. **Updates**
   - Test module updates in staging environment first
   - Backup database before applying updates
   - Document any customizations for future reference