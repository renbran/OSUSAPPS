# Module Cleanup Plan - OSUSAPPS

## 📋 Cleanup Summary

**Date**: October 1, 2025  
**Status**: IN PROGRESS

## ✅ Completed Actions

### 1. Documentation Reorganization
- **Moved**: All `COMMISSION_*.md` files → `docs/commission_fixes/`
- **Moved**: All fix-related `.md` files → `docs/`
- **Created**: Organized documentation structure

### 2. Temporary File Cleanup
- **Removed**: `debug.log` (temporary debug file)
- **Moved**: All shell scripts (`.sh`) → `scripts/` directory

## 🎯 Recommended Actions

### 3. Commission Module Consolidation
**Analysis**:
- `commission_ax`: Legacy module (marked for replacement)
- `commission_app`: Modern replacement (production-ready)
- `commission_unified`: Experimental module (no external dependencies)
- `commission_lines`: Depends on commission_ax

**Recommendations**:
1. **SAFE TO REMOVE**: `commission_unified/` (experimental, no dependencies)
2. **EVALUATE**: Migration path from `commission_ax` to `commission_app`
3. **UPDATE**: `commission_lines` to depend on `commission_app` instead of `commission_ax`

### 4. Module Validation Needed
**Modules requiring manifest validation**:
- `enhanced_rest_api` (has external dependency: rest_api_odoo)
- `project_unit_management` (basic manifest structure)
- `smile_access_control` (deprecated "active" field)

## 🚨 Important Notes

1. **commission_ax** should not be removed until data migration to `commission_app` is complete
2. **commission_lines** needs dependency update before commission_ax removal
3. All modules should be tested after cleanup

## 📁 New Directory Structure

```
OSUSAPPS/
├── docs/
│   ├── commission_fixes/     # All commission-related documentation
│   └── [other fix docs]      # Other documentation files
├── scripts/                  # All shell scripts
└── [modules]/               # Clean module directories
```

## Next Steps

1. Remove experimental `commission_unified` module
2. Update `commission_lines` dependencies
3. Validate remaining modules
4. Test commission system after cleanup