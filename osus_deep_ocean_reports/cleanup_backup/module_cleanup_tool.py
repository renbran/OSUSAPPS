#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Deep Ocean Reports Module Cleanup Tool
===================================================

This script identifies and removes:
1. Test files and validation scripts
2. Duplicate files and backup versions
3. Unused documentation files
4. Temporary files and development artifacts
"""

import os
import shutil
import json
from pathlib import Path

def analyze_module_structure():
    """Analyze the current module structure and identify files for cleanup"""
    module_path = Path(".")
    
    # Files that are essential for the module to function
    essential_files = {
        # Core module files
        '__init__.py',
        '__manifest__.py',
        'README.md',
        
        # Model files
        'models/__init__.py',
        'models/deep_ocean_invoice.py',
        
        # View files
        'views/account_move_views.xml',
        'views/deep_ocean_menus.xml',
        
        # Report files
        'reports/deep_ocean_invoice_report.xml',
        'reports/deep_ocean_receipt_report.xml',
        'reports/report_templates.xml',
        
        # Data files
        'data/report_paperformat.xml',
        
        # Security files
        'security/ir.model.access.csv',
        
        # Static assets
        'static/description/index.html',
        'static/src/css/deep_ocean_reports.css',
        'static/src/js/deep_ocean_reports.js',
    }
    
    # Files to be removed (development artifacts)
    cleanup_files = []
    
    # Scan all files in the module
    for file_path in module_path.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(module_path)
            relative_path_str = str(relative_path).replace('\\', '/')
            
            # Skip essential files
            if relative_path_str in essential_files:
                continue
                
            # Categories of files to remove
            should_remove = False
            category = ""
            
            # 1. Documentation and fix files
            if (relative_path.suffix == '.md' and 
                relative_path.name not in ['README.md']):
                should_remove = True
                category = "Documentation/Fix files"
            
            # 2. Validation and diagnostic scripts
            elif (relative_path.suffix in ['.py', '.sh'] and 
                  'validate' in relative_path.name.lower() or
                  'diagnostic' in relative_path.name.lower() or
                  'final_validation' in relative_path.name.lower() or
                  'fix_' in relative_path.name.lower()):
                should_remove = True
                category = "Validation/Diagnostic scripts"
            
            # 3. Backup and temporary files
            elif (relative_path.suffix in ['.backup', '.bak', '.tmp', '.old'] or
                  '.backup' in relative_path.name or
                  '_backup' in relative_path.name):
                should_remove = True
                category = "Backup/Temporary files"
            
            # 4. Test files
            elif ('test' in relative_path.name.lower() and 
                  relative_path.suffix in ['.py', '.xml']):
                should_remove = True
                category = "Test files"
            
            if should_remove:
                cleanup_files.append({
                    'path': relative_path_str,
                    'full_path': str(file_path),
                    'category': category,
                    'size': file_path.stat().st_size
                })
    
    return essential_files, cleanup_files

def create_cleanup_report(essential_files, cleanup_files):
    """Create a detailed cleanup report"""
    
    report = f"""# 🧹 Deep Ocean Reports Module Cleanup Report

## 📊 Analysis Summary

**Essential Files**: {len(essential_files)} files
**Files for Cleanup**: {len(cleanup_files)} files
**Total Size to Remove**: {sum(f['size'] for f in cleanup_files):,} bytes

## 📁 Essential Files (Kept)
These files are required for the module to function properly:

"""
    
    # Group essential files by directory
    dirs = {}
    for file_path in sorted(essential_files):
        dir_name = str(Path(file_path).parent)
        if dir_name == '.':
            dir_name = 'Root'
        if dir_name not in dirs:
            dirs[dir_name] = []
        dirs[dir_name].append(Path(file_path).name)
    
    for dir_name, files in dirs.items():
        report += f"### {dir_name}/\n"
        for file in files:
            report += f"- ✅ `{file}`\n"
        report += "\n"
    
    # Group cleanup files by category
    categories = {}
    for file_info in cleanup_files:
        category = file_info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(file_info)
    
    report += "## 🗑️ Files to be Removed\n\n"
    
    for category, files in categories.items():
        report += f"### {category}\n"
        total_size = sum(f['size'] for f in files)
        report += f"**Count**: {len(files)} files | **Size**: {total_size:,} bytes\n\n"
        
        for file_info in sorted(files, key=lambda x: x['path']):
            size_kb = file_info['size'] / 1024
            report += f"- 🗑️ `{file_info['path']}` ({size_kb:.1f} KB)\n"
        report += "\n"
    
    report += """## 🔧 Cleanup Actions

The cleanup process will:

1. **Move files to backup** before deletion (safety measure)
2. **Remove development artifacts** that are not needed in production
3. **Keep only essential files** required for module functionality
4. **Maintain module structure** integrity

## ✅ Post-Cleanup Module Structure

After cleanup, the module will contain only:
- Core Odoo module files (__init__.py, __manifest__.py)
- Essential business logic (models, views, reports)
- Required assets (CSS, JS, images)
- Proper documentation (README.md only)

## 🚀 Benefits

- **Reduced module size** and faster loading
- **Cleaner codebase** without development artifacts  
- **Production-ready** module structure
- **Easier maintenance** with fewer files to manage
"""
    
    return report

def execute_cleanup(cleanup_files, dry_run=True):
    """Execute the cleanup by removing identified files"""
    
    if dry_run:
        print("🔍 DRY RUN - No files will actually be removed")
        print("=" * 60)
    
    backup_dir = Path("cleanup_backup")
    
    if not dry_run and cleanup_files:
        backup_dir.mkdir(exist_ok=True)
        print(f"📦 Created backup directory: {backup_dir}")
    
    removed_count = 0
    total_size = 0
    
    for file_info in cleanup_files:
        file_path = Path(file_info['full_path'])
        
        if file_path.exists():
            if not dry_run:
                # Create backup
                backup_path = backup_dir / file_info['path']
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                # Remove original file
                file_path.unlink()
                print(f"🗑️ Removed: {file_info['path']}")
            else:
                print(f"🔍 Would remove: {file_info['path']} ({file_info['category']})")
            
            removed_count += 1
            total_size += file_info['size']
    
    print(f"\n📊 Cleanup Summary:")
    print(f"Files processed: {removed_count}")
    print(f"Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    if not dry_run and removed_count > 0:
        print(f"🔒 Backup created in: {backup_dir}")

def main():
    """Main cleanup function"""
    print("🧹 Deep Ocean Reports Module Cleanup Tool")
    print("=" * 50)
    
    # Analyze module structure
    essential_files, cleanup_files = analyze_module_structure()
    
    # Create cleanup report
    report = create_cleanup_report(essential_files, cleanup_files)
    
    # Write report to file
    with open("CLEANUP_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"📋 Cleanup report generated: CLEANUP_REPORT.md")
    print(f"📊 Found {len(cleanup_files)} files for cleanup")
    
    # Show summary by category
    categories = {}
    for file_info in cleanup_files:
        category = file_info['category']
        if category not in categories:
            categories[category] = {'count': 0, 'size': 0}
        categories[category]['count'] += 1
        categories[category]['size'] += file_info['size']
    
    print("\n📁 Cleanup Summary by Category:")
    for category, stats in categories.items():
        print(f"  {category}: {stats['count']} files ({stats['size']:,} bytes)")
    
    # Execute dry run first
    print("\n🔍 Dry Run (Preview):")
    execute_cleanup(cleanup_files, dry_run=True)
    
    return len(cleanup_files), sum(f['size'] for f in cleanup_files)

if __name__ == "__main__":
    main()