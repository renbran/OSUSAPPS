# Missing Product Record Fix Guide

## Problem Description

**Error Message:**
```
Missing Record

Record does not exist or has been deleted.
(Record: product.product(11,), User: 288)
```

This error occurs when:
- A product record (ID: 11) has been deleted from the database
- Other records still reference this deleted product
- User 288 tries to access or perform operations involving this product

## Root Causes

1. **Direct Deletion**: Product was deleted without removing references
2. **Data Import Issues**: Incomplete data migration or sync
3. **Module Conflicts**: Modules trying to access products that don't exist
4. **Database Corruption**: Inconsistent state between related tables
5. **Manual SQL Operations**: Direct database modifications without ORM

## Impact

This error can affect:
- Sales Order Lines referencing the deleted product
- Purchase Order Lines
- Invoice/Bill Lines
- Stock Moves
- Commission calculations
- Product packages/bundles
- Subscription packages
- Maintenance records

## Solution Options

### Option 1: Generate Report (Recommended First Step)

**Purpose**: Identify all references to the missing product before making changes.

**Windows:**
```bash
FIX_MISSING_PRODUCT.bat
# Choose option 1
```

**Linux/Mac:**
```bash
chmod +x fix_missing_product.sh
./fix_missing_product.sh
# Choose option 1
```

**Python Direct:**
```bash
python fix_missing_product_record.py --product-id 11 --fix-mode report
```

**What it does:**
- ✓ Scans all tables for references to product.product(11)
- ✓ Generates detailed report
- ✓ Provides recommendations
- ✓ Read-only (safe to run)

---

### Option 2: Database Shell Inspection

**Purpose**: Manual inspection and surgical fixes using SQL.

**Access Database:**
```bash
docker-compose exec db psql -U odoo -d odoo
```

**Check if product exists:**
```sql
SELECT id, name, default_code, active 
FROM product_product 
WHERE id = 11;
```

**Find all references:**
```sql
-- Sale Order Lines
SELECT id, order_id, product_id, name 
FROM sale_order_line 
WHERE product_id = 11;

-- Purchase Order Lines
SELECT id, order_id, product_id, name 
FROM purchase_order_line 
WHERE product_id = 11;

-- Invoice Lines
SELECT id, move_id, product_id, name 
FROM account_move_line 
WHERE product_id = 11;

-- Stock Moves
SELECT id, product_id, name 
FROM stock_move 
WHERE product_id = 11;

-- Pack Products (Custom Sales Kit)
SELECT id, product_id, product_tmpl_id 
FROM pack_product 
WHERE product_id = 11;

-- Sales Commission
SELECT id, product_id, commission 
FROM product_based_sales_commission 
WHERE product_id = 11;
```

**Manual Fix Options:**

**A. Update references to valid product:**
```sql
-- First, find a valid replacement product
SELECT id, name, default_code 
FROM product_product 
WHERE active = true 
ORDER BY id 
LIMIT 10;

-- Replace in sale order lines (replace 1 with valid product ID)
UPDATE sale_order_line 
SET product_id = 1 
WHERE product_id = 11;

-- Repeat for other tables as needed
```

**B. Delete orphaned records:**
```sql
-- WARNING: This deletes records permanently!

-- Delete from sale order lines
DELETE FROM sale_order_line WHERE product_id = 11;

-- Delete from purchase order lines
DELETE FROM purchase_order_line WHERE product_id = 11;

-- Delete from stock moves
DELETE FROM stock_move WHERE product_id = 11;
```

---

### Option 3: Automated Python Fix

**Purpose**: Automated replacement or removal of references.

**A. Replace with Valid Product:**

1. Find a valid replacement product:
   ```bash
   docker-compose exec db psql -U odoo -d odoo -c "SELECT id, name FROM product_product WHERE active = true ORDER BY id LIMIT 10;"
   ```

2. Run replacement:
   ```bash
   python fix_missing_product_record.py \
     --product-id 11 \
     --fix-mode replace \
     --replacement-id 1
   ```

**B. Remove Orphaned References:**

⚠️ **WARNING**: This will DELETE records!

```bash
python fix_missing_product_record.py \
  --product-id 11 \
  --fix-mode remove
```

You'll be asked to confirm by typing `YES`.

---

### Option 4: Odoo Database Cleanup Module

**Purpose**: Use Odoo's built-in cleanup tools via GUI.

**Steps:**

1. **Enable Developer Mode:**
   - Open Odoo: http://localhost:8069
   - Click profile icon (top right)
   - Click "Developer Mode"

2. **Access Cleanup Tool:**
   - Go to: Settings → Technical → Database Structure → Database Cleanup

3. **Choose Cleanup Type:**
   - **Purge Data**: Remove orphaned data references
   - **Purge Models**: Clean up missing models
   - **Purge Columns**: Remove unused columns
   - **Purge Tables**: Remove unused tables

4. **Execute:**
   - Click "Analyze" to see what will be cleaned
   - Review the list
   - Click "Purge All" or select specific items

**Advantages:**
- ✓ Visual interface
- ✓ Safe preview before execution
- ✓ Comprehensive cleanup
- ✓ Handles many types of issues

---

### Option 5: Recreate the Product

**Purpose**: If the product should exist, recreate it.

**Steps:**

1. **Find product details from history:**
   ```sql
   SELECT * FROM product_template WHERE id IN (
     SELECT product_tmpl_id FROM product_product WHERE id = 11
   );
   ```

2. **Or create new product via Odoo UI:**
   - Go to: Inventory → Products → Products
   - Click "Create"
   - Set ID to 11 (if possible)
   - Fill in required fields
   - Save

3. **Or via SQL (advanced):**
   ```sql
   -- First, create product template
   INSERT INTO product_template (name, type, sale_ok, purchase_ok, active)
   VALUES ('Replacement Product', 'consu', true, true, true)
   RETURNING id;
   
   -- Then create product.product with specific ID
   -- Note: This requires careful sequence management
   ```

---

## Prevention Best Practices

### 1. Always Use ORM for Deletions
```python
# Good - uses ORM, handles relations
product.unlink()

# Bad - direct SQL, leaves orphans
cr.execute("DELETE FROM product_product WHERE id = 11")
```

### 2. Check References Before Deletion
```python
# Check if product is used anywhere
sale_lines = env['sale.order.line'].search([('product_id', '=', product.id)])
if sale_lines:
    raise UserError("Cannot delete product - used in sales orders")
```

### 3. Archive Instead of Delete
```python
# Archive (soft delete) instead of hard delete
product.write({'active': False})
```

### 4. Use Odoo's Dependency Management
```python
# In model definition
product_id = fields.Many2one(
    'product.product',
    ondelete='restrict'  # Prevents deletion if referenced
)
```

### 5. Regular Database Cleanup
- Schedule weekly cleanup using Database Cleanup module
- Monitor logs for orphaned record warnings
- Run integrity checks after major data operations

### 6. Backup Before Major Operations
```bash
# Backup database before bulk deletions
docker-compose exec db pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql
```

---

## Troubleshooting

### Issue: "User 288 not found"
```sql
-- Check if user exists
SELECT id, login, name FROM res_users WHERE id = 288;

-- Find actual user triggering the error
SELECT id, login, name FROM res_users WHERE active = true;
```

### Issue: "Table not found"
Some custom modules may have their own product reference tables. Check module documentation.

### Issue: "Permission denied"
Ensure you have admin access or database privileges.

### Issue: "Cannot connect to database"
```bash
# Check if Odoo container is running
docker-compose ps

# Check if database is accessible
docker-compose exec db psql -U odoo -d odoo -c "SELECT 1;"
```

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Generate report | `python fix_missing_product_record.py --fix-mode report` |
| Replace product | `python fix_missing_product_record.py --fix-mode replace --replacement-id 1` |
| Remove references | `python fix_missing_product_record.py --fix-mode remove` |
| Database shell | `docker-compose exec db psql -U odoo -d odoo` |
| Check product | `SELECT * FROM product_product WHERE id = 11;` |
| List products | `SELECT id, name FROM product_product WHERE active = true LIMIT 10;` |

---

## Files Created

1. **fix_missing_product_record.py** - Python script for automated fixes
2. **FIX_MISSING_PRODUCT.bat** - Windows batch script
3. **fix_missing_product.sh** - Linux/Mac shell script
4. **MISSING_PRODUCT_FIX_GUIDE.md** - This documentation

---

## Support

For additional help:
- Check module-specific README files
- Review Odoo logs: `docker-compose logs -f odoo`
- Enable debug logging in Odoo config
- Consult OCA database_cleanup module documentation

---

## Related Issues & Fixes

See also:
- `LANDLORD_ID_ERROR_FIX.md` - Similar issue with landlord records
- `SEQUENCE_FIELD_FIX.md` - Sequence-related errors
- `EXTERNAL_ID_FIX_SUMMARY.md` - External ID reference errors
- `database_cleanup/` module - Built-in cleanup tools

---

## Version History

- **v1.0.0** (2025-10-03): Initial version
  - Created comprehensive fix script
  - Added batch/shell wrappers
  - Generated documentation

---

**Last Updated**: October 3, 2025  
**Applies To**: Odoo 17 (OSUSAPPS)  
**Severity**: High (Blocks user operations)
