# Fix: Field is_extra_service Referenced Error

## Error Description
```
KeyError: 'Field is_extra_service referenced in related field definition contract.wizard.is_extra_service does not exist.'
```

## Root Cause
The `contract.wizard` model (TransientModel) is trying to reference `property_id.is_extra_service` before the `property.details` model has been fully loaded.

## Quick Fix Options

### Option 1: Reinstall rental_management (Recommended)
This forces a clean reload of all models in the correct order:

```bash
ssh root@139.84.163.11 << 'EOF'
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u rental_management --stop-after-init'
systemctl restart odoo
echo "✅ rental_management reinstalled!"
EOF
```

### Option 2: Upgrade All Modules
If multiple modules are having issues:

```bash
ssh root@139.84.163.11 << 'EOF'
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -u all --stop-after-init'
systemctl restart odoo
echo "✅ All modules upgraded!"
EOF
```

### Option 3: Uninstall and Reinstall rental_management
If the issue persists:

```bash
ssh root@139.84.163.11 << 'EOF'
# Stop Odoo
systemctl stop odoo

# Backup database first
sudo -u postgres pg_dump properties > /tmp/properties_backup_$(date +%Y%m%d_%H%M%S).sql

# Uninstall module
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties shell' << 'PYTHON'
env['ir.module.module'].search([('name', '=', 'rental_management')]).button_immediate_uninstall()
env.cr.commit()
exit()
PYTHON

# Clear cache
rm -rf /var/odoo/.local/share/Odoo/filestore/properties/sessions/*

# Reinstall module
su - odoo -c '/var/odoo/properties/src/odoo-bin -c /etc/odoo/odoo.conf -d properties -i rental_management --stop-after-init'

# Restart Odoo
systemctl start odoo
echo "✅ rental_management reinstalled from scratch!"
EOF
```

## Verification

Check the logs after restart:
```bash
ssh root@139.84.163.11 "tail -f /var/log/odoo/odoo-server.log | grep -E 'rental_management|is_extra_service|ERROR|WARNING'"
```

## What Happened?

1. You tried to update `commission_ax` module
2. Odoo's update process triggered a registry rebuild
3. During the rebuild, `rental_management` models were loaded
4. The `contract.wizard` TransientModel tried to set up its related field `is_extra_service` 
5. But the base field in `property.details.is_extra_service` wasn't accessible yet

## Prevention

This is a known Odoo issue with TransientModels and related fields. The safest approach:
- Always update modules individually: `-u module_name`
- Avoid `-u all` unless necessary
- Keep module dependencies explicit in `__manifest__.py`

## Next Steps After Fix

1. First, let's fix rental_management with Option 1
2. Then retry the commission_ax deployment
3. Update both modules if needed

---

**Need help?** Check `/var/log/odoo/odoo-server.log` for detailed errors.
