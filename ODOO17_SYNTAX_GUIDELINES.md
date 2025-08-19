# Odoo 17 Development Guidelines - Deprecated Syntax Migration

## 🚨 **CRITICAL DEVELOPMENT NOTE**

**As of Odoo 17, several XML view attributes have been deprecated and MUST be replaced with modern syntax to ensure compatibility and avoid errors.**

## ❌ **Deprecated Syntax (Odoo 16 and Earlier)**

### 1. States Attribute
```xml
<!-- DEPRECATED - DON'T USE -->
<button name="action_confirm" states="draft,sent"/>
<field name="some_field" states="posted"/>
```

### 2. Attrs Dictionary
```xml
<!-- DEPRECATED - DON'T USE -->
<field name="field_name" attrs="{'invisible': [('state', '=', 'draft')]}"/>
<button name="button_name" attrs="{'readonly': [('state', '!=', 'posted')]}"/>
```

### 3. Modifiers Attribute
```xml
<!-- DEPRECATED - DON'T USE -->
<button name="action_name" modifiers="posted"/>
```

## ✅ **Modern Syntax (Odoo 17+)**

### 1. Invisible Domain Expression
```xml
<!-- CORRECT MODERN SYNTAX -->
<button name="action_confirm" invisible="state not in ['draft','sent']"/>
<field name="some_field" invisible="state != 'posted'"/>
```

### 2. Direct Field Attributes
```xml
<!-- CORRECT MODERN SYNTAX -->
<field name="field_name" invisible="state == 'draft'"/>
<button name="button_name" readonly="state != 'posted'"/>
<field name="amount" required="partner_id != False"/>
```

### 3. Complex Domain Expressions
```xml
<!-- CORRECT MODERN SYNTAX -->
<field name="field_name" invisible="state == 'draft' or amount <= 0"/>
<button name="action_name" readonly="state not in ['draft', 'sent'] and user_id == False"/>
```

## 🔄 **Migration Examples**

### Button States
```xml
<!-- OLD -->
<button name="action_confirm" states="draft,sent" class="btn-primary"/>

<!-- NEW -->
<button name="action_confirm" invisible="state not in ['draft','sent']" class="btn-primary"/>
```

### Field Visibility
```xml
<!-- OLD -->
<field name="delivery_date" attrs="{'invisible': [('state', '!=', 'confirmed')]}"/>

<!-- NEW -->
<field name="delivery_date" invisible="state != 'confirmed'"/>
```

### Field Requirements
```xml
<!-- OLD -->
<field name="partner_id" attrs="{'required': [('order_type', '=', 'sale')]}"/>

<!-- NEW -->
<field name="partner_id" required="order_type == 'sale'"/>
```

### Field Readonly
```xml
<!-- OLD -->
<field name="amount" attrs="{'readonly': [('state', 'in', ['posted', 'paid'])]}"/>

<!-- NEW -->
<field name="amount" readonly="state in ['posted', 'paid']"/>
```

## 🎯 **Domain Expression Operators**

| Condition | Modern Syntax |
|-----------|---------------|
| Equal | `field == 'value'` or `field == True` |
| Not Equal | `field != 'value'` or `field != False` |
| In List | `field in ['val1', 'val2']` |
| Not In List | `field not in ['val1', 'val2']` |
| Greater Than | `field > 100` |
| Less Than | `field < 50` |
| AND Logic | `field1 == 'value' and field2 > 0` |
| OR Logic | `field1 == 'draft' or field2 == False` |
| Complex | `(field1 == 'sale' and field2 > 0) or field3 != False` |

## 🔍 **How to Find Deprecated Syntax**

### Search Commands
```bash
# Find deprecated states usage
grep -r "states=" **/*.xml

# Find deprecated attrs usage  
grep -r "attrs=" **/*.xml

# Find deprecated modifiers usage
grep -r "modifiers=" **/*.xml
```

### VS Code Search
- **Search**: `states=|attrs=|modifiers=`
- **Files**: `**/*.xml`
- **Use Regex**: ✅

## 📋 **Pre-Development Checklist**

Before creating any new views or modifying existing ones:

- [ ] ✅ Use `invisible="domain_expression"` instead of `states=`
- [ ] ✅ Use `readonly="domain_expression"` instead of `attrs={'readonly': []}`
- [ ] ✅ Use `required="domain_expression"` instead of `attrs={'required': []}`
- [ ] ✅ Test domain expressions work correctly
- [ ] ✅ Verify no XML parsing errors in Odoo logs

## 🚀 **Benefits of Modern Syntax**

1. **Better Performance**: Domain expressions are more efficient
2. **Cleaner Code**: Less verbose than dictionary syntax
3. **Better Error Handling**: Clearer error messages
4. **Future Compatibility**: Aligns with Odoo's development direction
5. **No Deprecation Warnings**: Clean log files

## ⚠️ **Common Mistakes to Avoid**

### 1. Wrong Comparison Operators
```xml
<!-- WRONG -->
<field name="amount" invisible="amount = 0"/>  <!-- Single = -->

<!-- CORRECT -->
<field name="amount" invisible="amount == 0"/> <!-- Double == -->
```

### 2. Boolean Field Comparisons
```xml
<!-- WRONG -->
<field name="is_active" invisible="is_active == 'True'"/>

<!-- CORRECT -->
<field name="is_active" invisible="is_active == True"/>
<!-- OR -->
<field name="is_active" invisible="not is_active"/>
```

### 3. Many2one Field Checks
```xml
<!-- WRONG -->
<field name="partner_id" invisible="partner_id == None"/>

<!-- CORRECT -->
<field name="partner_id" invisible="partner_id == False"/>
<!-- OR -->
<field name="partner_id" invisible="not partner_id"/>
```

## 🔧 **Migration Script Template**

```python
# Quick find and replace patterns (use with caution, review each change)

# 1. Simple states to invisible
states="draft,sent" → invisible="state not in ['draft','sent']"

# 2. Simple attrs invisible
attrs="{'invisible': [('field', '=', 'value')]}" → invisible="field == 'value'"

# 3. Simple attrs readonly  
attrs="{'readonly': [('state', '!=', 'draft')]}" → readonly="state != 'draft'"
```

## 📝 **Testing Checklist**

After migration:

- [ ] No XML parsing errors in server logs
- [ ] Fields show/hide correctly based on conditions
- [ ] Buttons appear in correct states
- [ ] Form validation works as expected
- [ ] No JavaScript console errors
- [ ] All user workflows function properly

---

## 🎯 **ACTION ITEMS FOR ALL DEVELOPERS**

1. **Review** all existing XML views for deprecated syntax
2. **Update** any found deprecated attributes to modern syntax
3. **Test** thoroughly after migration
4. **Document** any complex domain logic
5. **Always use** modern syntax in new development

**Remember: This is not optional - deprecated syntax will cause errors in Odoo 17+**
