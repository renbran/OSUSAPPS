# 🚀 ODOO MODULE PREFIX QUICK REFERENCE

## ✅ WHEN TO USE MODULE PREFIX

### Rule: Use prefix when referencing EXTERNAL modules

```xml
<!-- ✅ CORRECT: Referencing another module -->
<menuitem id="my_custom_menu" 
          parent="sale.sale_menu_root" 
          action="account.action_invoice"/>

<field name="partner_id" ref="base.res_partner_1"/>

<record id="my_action" model="ir.actions.act_window">
    <field name="view_id" ref="stock.view_picking_form"/>
</record>
```

### Examples by Module
| Your Module | Referencing | Use Prefix | Example |
|-------------|-------------|------------|---------|
| `custom_sales` | `sale` module | ✅ YES | `sale.sale_menu_root` |
| `commission_ax` | `account` module | ✅ YES | `account.action_invoice` |
| `custom_reports` | `base` module | ✅ YES | `base.res_partner_1` |

---

## ❌ WHEN NOT TO USE MODULE PREFIX

### Rule: Do NOT use prefix for INTERNAL references

```xml
<!-- ✅ CORRECT: Referencing same module -->
<menuitem id="menu_sub_item" 
          parent="menu_root" 
          action="action_main_view"/>

<field name="type_id" ref="commission_type_1"/>

<record id="action_view" model="ir.actions.act_window">
    <field name="view_id" ref="view_form"/>
</record>
```

### Examples by Module
| Your Module | Referencing | Use Prefix | Example |
|-------------|-------------|------------|---------|
| `commission_ax` | `commission_ax` menu | ❌ NO | `menu_commission_root` |
| `commission_ax` | `commission_ax` action | ❌ NO | `action_commission_type` |
| `commission_ax` | `commission_ax` record | ❌ NO | `commission_type_1` |

---

## 🔍 COMMON MISTAKES

### Mistake 1: Using Module Prefix for Same Module

```xml
<!-- ❌ WRONG -->
<menuitem id="menu_item" 
          parent="commission_ax.menu_root" 
          action="commission_ax.action_view"/>

<!-- ✅ CORRECT -->
<menuitem id="menu_item" 
          parent="menu_root" 
          action="action_view"/>
```

**Error**: `ValueError: External ID not found: commission_ax.menu_root`

---

### Mistake 2: Missing Module Prefix for External Reference

```xml
<!-- ❌ WRONG -->
<menuitem id="menu_item" 
          parent="sale_menu_root" 
          action="action_invoice"/>

<!-- ✅ CORRECT -->
<menuitem id="menu_item" 
          parent="sale.sale_menu_root" 
          action="account.action_invoice"/>
```

**Error**: `ValueError: External ID not found: sale_menu_root`

---

## 🛠️ TROUBLESHOOTING GUIDE

### Error: "External ID not found"

**Step 1**: Identify the missing XML ID
```
ValueError: External ID not found in the system: commission_ax.commission_menu_reports
                                                   ^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^
                                                   Module    XML ID
```

**Step 2**: Search for the XML ID definition
```bash
grep -r "id=\"commission_menu_reports\"" .
```

**Step 3**: Check if it's in the same module
- ✅ **Same module**: Remove the prefix
- ❌ **Different module**: Keep the prefix

**Step 4**: Verify the fix
```xml
<!-- If found in same module (commission_ax) -->
<menuitem parent="commission_menu_reports"/>  <!-- Remove prefix -->

<!-- If found in different module (sale) -->
<menuitem parent="sale.sale_menu_root"/>  <!-- Keep prefix -->
```

---

## 📝 VERIFICATION COMMANDS

### Find Incorrect Internal References
```bash
# Search for module_name prefix in same module
grep -r "parent=\"commission_ax\." commission_ax/views/
grep -r "action=\"commission_ax\." commission_ax/views/
grep -r "ref=\"commission_ax\." commission_ax/views/
```

### Find Missing External References
```bash
# Search for external references without prefix
grep -r "parent=\"sale_menu" .  # Should be "sale.sale_menu"
grep -r "parent=\"account_menu" .  # Should be "account.account_menu"
```

### Check Module Loading
```bash
docker-compose logs web | grep -E "(ParseError|External ID not found)"
```

---

## 📋 FIX CHECKLIST

When you encounter "External ID not found" error:

- [ ] Note the full XML ID from error (e.g., `commission_ax.commission_menu_reports`)
- [ ] Search for XML ID definition: `grep -r "id=\"commission_menu_reports\"" .`
- [ ] Identify which module defines it
- [ ] Compare with module where it's referenced
- [ ] **If same module**: Remove prefix
- [ ] **If different module**: Keep prefix
- [ ] Restart Docker: `docker-compose down && docker-compose up -d`
- [ ] Verify no errors: `docker-compose logs web | grep ERROR`

---

## 🎯 MODULE PREFIX DECISION TREE

```
Is the XML ID in the same module as your current file?
│
├─ YES → Do NOT use module prefix
│         Example: parent="menu_root"
│
└─ NO → Is it in a different module?
         │
         └─ YES → USE module prefix
                   Example: parent="sale.sale_menu_root"
```

---

## 💡 BEST PRACTICES

### 1. Consistent Naming
- Use descriptive XML IDs: `menu_commission_reports` (not `menu1`)
- Follow Odoo naming conventions: `action_`, `view_`, `menu_`

### 2. Module Organization
- Group related XML IDs in same file
- Keep menu definitions in dedicated file (e.g., `commission_menu.xml`)

### 3. Testing
- Always test module installation after changes
- Use Docker for isolated testing environment
- Check logs for ParseError or ValueError

### 4. Documentation
- Document external dependencies in module README
- Comment complex menu structures
- Keep track of cross-module references

---

## 🔗 RELATED ERRORS

### ParseError
- Usually caused by XML syntax errors or missing references
- Check line number in error message
- Verify XML tags are properly closed

### ValueError: External ID not found
- Caused by incorrect module prefix usage
- Follow decision tree above
- Verify module is installed and XML ID exists

### KeyError in cache lookup
- Related to External ID not found
- Same fix: correct module prefix usage
- Clear cache if needed: `docker-compose down -v`

---

**Quick Reference Version**: 1.0  
**Last Updated**: October 2, 2025  
**Related Docs**: `COMMISSION_AX_MENU_FIX_FINAL.md`