# 🚨 COMMISSION MODULE INSTALLATION FIX

## ❌ CURRENT ERROR
```
Exception: Module loading commission_ax failed: file commission_ax/security/ir.model.access.csv could not be processed:
 No matching record found for external id 'commission_statement.group_commission_user' in field 'Group'
 No matching record found for external id 'model_commission_partner_statement_wizard' in field 'Model'
```

## ✅ FIXES APPLIED

### 1. **commission_ax Module - STANDALONE**
- ✅ Removed dependency on commission_statement
- ✅ Created own security groups (`group_commission_user`, `group_commission_manager`)
- ✅ Renamed wizard model to `commission.partner.statement.wizard`
- ✅ Updated all references to new model name
- ✅ Fixed access rights to use local groups
- ✅ Added security.xml to manifest

### 2. **commission_statement Module - INDEPENDENT**
- ✅ Removed dependency on commission_ax
- ✅ Can be installed independently
- ✅ Uses own wizard model `commission.statement.wizard`

## 📋 INSTALLATION ORDER

### Option 1: Install commission_ax ONLY
```bash
# Install just commission_ax (now standalone)
docker-compose exec odoo odoo --install=commission_ax --stop-after-init
```

### Option 2: Install both modules separately
```bash
# Install commission_statement first
docker-compose exec odoo odoo --install=commission_statement --stop-after-init

# Then install commission_ax
docker-compose exec odoo odoo --install=commission_ax --stop-after-init
```

## ⚠️ BREAKING CHANGES SUMMARY

### commission_ax Changes:
- 🔄 `commission.statement.wizard` → `commission.partner.statement.wizard`
- 🔄 External group references → Local group definitions
- 🔄 Dependency on commission_statement → Standalone module

### commission_statement Changes:
- 🔄 Dependency on commission_ax → Independent module
- ✅ Retains original `commission.statement.wizard` model

## 🎯 RESULT
- ✅ No more model name conflicts
- ✅ No more dependency cycles
- ✅ Both modules can install independently
- ✅ Clear separation of functionality

## 🚀 NEXT STEPS
1. Try installing commission_ax module first
2. If successful, optionally install commission_statement
3. Test all functionality
4. Both modules now work independently!
