# Quick Deployment Checklist - Commission Type Model

## Files to Deploy

✅ **commission_ax/models/commission_type.py** - New model definition  
✅ **commission_ax/models/__init__.py** - Updated imports  
✅ **commission_ax/security/ir.model.access.csv** - Updated access rights  
✅ **commission_ax/data/commission_type_data.xml** - Default commission types  
✅ **commission_ax/views/commission_type_views.xml** - Management interface  
✅ **commission_ax/__manifest__.py** - Updated data files list  

## Deployment Commands

### For Staging Server (staging-erposus.com)

```bash
# 1. Deploy files to server
# 2. Update module
odoo --update=commission_ax --stop-after-init -d your_database

# 3. Restart Odoo service  
systemctl restart odoo

# 4. Verify model is available
odoo shell -d your_database
>>> env['commission.type'].search_count([])
# Should return: 4
```

### For Docker Development

```bash
# 1. Run update script
./update_commission_type.sh

# OR manually:
docker-compose exec odoo odoo --update=commission_ax --stop-after-init -d odoo
docker-compose restart odoo
```

## Expected Results

After successful deployment:

- ✅ **commission.type** model available in system
- ✅ **4 default commission types** created (External, Internal, Referral, Bonus)
- ✅ **commission_lines** module can reference commission.type without errors
- ✅ **RPC error resolved** - view parsing should work
- ✅ **Commission Types** menu available in Commission module

## Verification

```python
# In Odoo shell or through UI
commission_types = env['commission.type'].search([])
print(f"Found {len(commission_types)} commission types:")
for ct in commission_types:
    print(f"- {ct.name} ({ct.code})")
```

Expected output:
```
Found 4 commission types:
- External Commission (EXTERNAL)
- Internal Commission (INTERNAL)  
- Referral Commission (REFERRAL)
- Bonus Commission (BONUS)
```

## If Issues Persist

1. **Check database**: Ensure updating correct database
2. **Check logs**: Look for installation errors in odoo logs
3. **Clear cache**: Add `--dev=reload` flag to update command
4. **Reinstall**: Use `--init=commission_ax` instead of `--update`
5. **Dependencies**: Ensure commission_ax is listed as dependency in commission_lines