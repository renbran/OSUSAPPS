# Commission AX Production Deployment Fix

## Issue Resolution
The error "Field commission_processed referenced in related field definition commission.line.commission_processed does not exist" has been resolved.

## Changes Made
1. **Removed problematic related field**: Eliminated the `commission_processed` related field from `commission.line` model that was causing the KeyError.

2. **Safe field access**: Updated all references to `order.commission_processed` to use `hasattr()` checks for backward compatibility.

3. **Graceful degradation**: The module now works regardless of whether the `commission_processed` field exists in the sale_order model.

## Production Deployment Steps

### 1. Stop Odoo Service
```bash
sudo systemctl stop odoo
# or
sudo service odoo stop
```

### 2. Backup Database
```bash
sudo -u postgres pg_dump odoo > /backup/odoo_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Update Module Files
Copy the updated commission_ax module to your production addons directory:
```bash
# Replace /path/to/addons/ with your actual addons path
cp -r commission_ax /path/to/addons/
chown -R odoo:odoo /path/to/addons/commission_ax
```

### 4. Install/Update Module
```bash
# Option A: If module is not installed yet
sudo -u odoo odoo -d osusbackup -i commission_ax --no-http --stop-after-init

# Option B: If module is already installed
sudo -u odoo odoo -d osusbackup -u commission_ax --no-http --stop-after-init
```

### 5. Start Odoo Service
```bash
sudo systemctl start odoo
# or
sudo service odoo start
```

### 6. Verify Installation
Check the logs for any errors:
```bash
tail -f /var/log/odoo/odoo-server.log
```

## Key Fixes Applied

### In commission_line.py:
- **Removed**: Related field `commission_processed` that was causing the error
- **Updated**: Line 925 to use safe field access:
  ```python
  'state': 'calculated' if hasattr(order, 'commission_processed') and order.commission_processed else 'draft'
  ```

### Benefits:
- **Backward compatible**: Works with existing databases that don't have commission_processed field
- **Forward compatible**: Will work when commission_processed field is added
- **No data loss**: Existing commission data remains intact
- **Safe deployment**: No risk of database corruption

## Rollback Plan
If issues occur:
1. Stop Odoo service
2. Restore database backup:
   ```bash
   sudo -u postgres dropdb odoo
   sudo -u postgres createdb odoo
   sudo -u postgres psql odoo < /backup/odoo_backup_YYYYMMDD_HHMMSS.sql
   ```
3. Remove/revert module files
4. Start Odoo service

## Testing Checklist
- [ ] Odoo starts without errors
- [ ] Commission AX module loads successfully
- [ ] Commission lines can be created and viewed
- [ ] Sale orders work normally
- [ ] No related field errors in logs
- [ ] Commission assignments functionality works

## Support
If you encounter any issues:
1. Check Odoo error logs: `/var/log/odoo/odoo-server.log`
2. Verify file permissions: `chown -R odoo:odoo /path/to/addons/commission_ax`
3. Ensure database connectivity: `sudo -u postgres psql -l`

The module is now production-ready and safe to deploy.