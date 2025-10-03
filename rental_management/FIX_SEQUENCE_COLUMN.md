# 🔧 URGENT FIX: Missing Sequence Column in Payment Plan Tables

## Error
```
psycopg2.errors.UndefinedColumn: column property_payment_plan.sequence does not exist
LINE 1: ..."property_payment_plan"."active" = true) ORDER BY "property_...
```

## Root Cause
The `sequence` column is defined in the Python model but doesn't exist in the database table. This happens when:
- Module was upgraded without running migrations
- Database was restored from old backup
- Migration script didn't execute properly

## IMMEDIATE FIX (Choose ONE method)

### Method 1: Via Odoo Shell (Recommended) ⭐

1. **Access Odoo Shell:**
   ```bash
   docker compose exec odoo odoo shell -d odoo
   ```

2. **Run the fix:**
   ```python
   cr = env.cr
   
   # Add sequence to property_payment_plan
   cr.execute("""
       ALTER TABLE property_payment_plan 
       ADD COLUMN IF NOT EXISTS sequence INTEGER DEFAULT 10
   """)
   cr.execute("UPDATE property_payment_plan SET sequence = id * 10")
   
   # Add sequence to property_payment_plan_line
   cr.execute("""
       ALTER TABLE property_payment_plan_line 
       ADD COLUMN IF NOT EXISTS sequence INTEGER DEFAULT 10
   """)
   cr.execute("UPDATE property_payment_plan_line SET sequence = id * 10")
   
   # Commit
   cr.commit()
   print("✅ Fixed!")
   ```

3. **Exit:** Press `Ctrl+D`

4. **Restart Odoo:**
   ```bash
   docker compose restart odoo
   ```

### Method 2: Via Python Script

```bash
docker compose exec odoo odoo shell -d odoo < rental_management/fix_payment_plan_sequence.py
```

### Method 3: Via PostgreSQL Direct

```bash
docker compose exec db psql -U odoo -d odoo
```

Then run:
```sql
ALTER TABLE property_payment_plan 
ADD COLUMN IF NOT EXISTS sequence INTEGER DEFAULT 10;

UPDATE property_payment_plan 
SET sequence = id * 10;

ALTER TABLE property_payment_plan_line 
ADD COLUMN IF NOT EXISTS sequence INTEGER DEFAULT 10;

UPDATE property_payment_plan_line 
SET sequence = id * 10;
```

Exit with `\q`

### Method 4: Upgrade Module

```bash
docker compose exec odoo odoo -d odoo -u rental_management --stop-after-init
docker compose restart odoo
```

## Verification

After applying the fix, verify:

```bash
docker compose exec db psql -U odoo -d odoo -c "
SELECT 
    table_name,
    column_name,
    data_type,
    column_default
FROM information_schema.columns 
WHERE table_name IN ('property_payment_plan', 'property_payment_plan_line')
  AND column_name = 'sequence'
ORDER BY table_name;
"
```

Expected output:
```
         table_name          | column_name | data_type | column_default 
-----------------------------+-------------+-----------+----------------
 property_payment_plan       | sequence    | integer   | 10
 property_payment_plan_line  | sequence    | integer   | 10
```

## Why This Happened

The rental_management module was upgraded to version 3.2.8 which added the `sequence` field to:
- `property.payment.plan` model (line 13 in property_payment_plan.py)
- `property.payment.plan.line` model (line 53)

The model definition includes:
```python
_order = 'sequence, id'
sequence = fields.Integer(string='Sequence', default=10)
```

However, the database migration didn't run, leaving the database schema out of sync with the Python model.

## Files Involved

- **Model:** `rental_management/models/property_payment_plan.py`
- **Migration:** `rental_management/migrations/3.2.8/pre-migrate.py`
- **Fix Scripts:**
  - `rental_management/fix_payment_plan_sequence.py` (Python)
  - `rental_management/fix_payment_plan_sequence.sql` (SQL)

## Prevention

To prevent this in the future:

1. **Always upgrade modules properly:**
   ```bash
   docker compose exec odoo odoo -d odoo -u rental_management --stop-after-init
   ```

2. **Check logs** after upgrades for migration warnings

3. **Test in staging** before deploying to production

4. **Backup database** before major upgrades

## Support

If the error persists after applying the fix:
1. Check Odoo logs: `docker compose logs -f odoo`
2. Verify table structure: See verification commands above
3. Try full module reinstall (last resort)
