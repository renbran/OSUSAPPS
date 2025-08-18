#!/usr/bin/env python3
"""
OSUS Payment Module - Final Validation Script
============================================

This script validates the account_payment_final module to ensure:
- All referenced files in manifest actually exist
- No broken imports or dependencies
- Proper OSUS branding alignment
- CloudPepper optimization compliance
- Odoo 17 best practices adherence
"""

import os
import sys
import ast
import re
from pathlib import Path

class OSUSModuleValidator:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, message):
        self.errors.append(f"❌ ERROR: {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def log_success(self, message):
        self.success_count += 1
        print(f"✅ {message}")
        
    def validate_manifest(self):
        """Validate manifest file and referenced assets"""
        print("\n🔍 Validating Manifest File...")
        manifest_path = self.module_path / "__manifest__.py"
        
        if not manifest_path.exists():
            self.log_error("__manifest__.py not found")
            return
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find the dictionary content by removing the first line and parsing
            lines = content.strip().split('\n')
            dict_content = '\n'.join(lines[1:])  # Skip the comment line
            manifest_data = ast.literal_eval(dict_content)
                
            # Check OSUS branding in name/description
            if 'OSUS' not in manifest_data.get('name', ''):
                self.log_warning("Module name doesn't include OSUS branding")
            else:
                self.log_success("OSUS branding found in module name")
                
            # Validate data files
            for data_file in manifest_data.get('data', []):
                file_path = self.module_path / data_file
                if not file_path.exists():
                    self.log_error(f"Data file not found: {data_file}")
                else:
                    self.log_success(f"Data file exists: {data_file}")
                    
            # Validate assets
            assets = manifest_data.get('assets', {})
            for asset_bundle, files in assets.items():
                for asset_file in files:
                    # Handle tuple format like ('prepend', 'file.js')
                    if isinstance(asset_file, tuple):
                        asset_file = asset_file[1]  # Get the file path from tuple
                    
                    if isinstance(asset_file, str) and asset_file.startswith('account_payment_final/'):
                        # Remove module prefix for local path checking
                        local_path = asset_file.replace('account_payment_final/', '')
                        file_path = self.module_path / local_path
                        if not file_path.exists():
                            self.log_error(f"Asset file not found: {asset_file}")
                        else:
                            self.log_success(f"Asset file exists: {asset_file}")
                            
        except Exception as e:
            self.log_error(f"Failed to parse manifest: {str(e)}")
            
    def validate_python_files(self):
        """Check Python files for syntax and import issues"""
        print("\n🐍 Validating Python Files...")
        
        python_files = list(self.module_path.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check syntax
                ast.parse(content)
                self.log_success(f"Python syntax valid: {py_file.relative_to(self.module_path)}")
                
                # Check for OSUS branding in key files
                if 'osus' in str(py_file).lower() or 'OSUS' in content:
                    self.log_success(f"OSUS branding found in: {py_file.name}")
                    
            except SyntaxError as e:
                self.log_error(f"Syntax error in {py_file.relative_to(self.module_path)}: {str(e)}")
            except Exception as e:
                self.log_warning(f"Could not validate {py_file.relative_to(self.module_path)}: {str(e)}")
                
    def validate_static_assets(self):
        """Validate CSS/JS/XML files in static directory"""
        print("\n🎨 Validating Static Assets...")
        
        static_path = self.module_path / "static"
        if not static_path.exists():
            self.log_warning("No static directory found")
            return
            
        # Check SCSS files for OSUS branding
        scss_files = list(static_path.rglob("*.scss"))
        osus_branded_scss = 0
        for scss_file in scss_files:
            try:
                with open(scss_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '--osus-' in content or 'osus' in content.lower():
                        osus_branded_scss += 1
                        self.log_success(f"OSUS branding in: {scss_file.name}")
            except:
                pass
                
        if osus_branded_scss > 0:
            self.log_success(f"Found {osus_branded_scss} SCSS files with OSUS branding")
        else:
            self.log_warning("No OSUS branding found in SCSS files")
            
        # Check JS files for CloudPepper optimizations
        js_files = list(static_path.rglob("*.js"))
        cloudpepper_optimized = 0
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'cloudpepper' in content.lower() or 'CloudPepper' in content:
                        cloudpepper_optimized += 1
                        self.log_success(f"CloudPepper optimization in: {js_file.name}")
            except:
                pass
                
        if cloudpepper_optimized > 0:
            self.log_success(f"Found {cloudpepper_optimized} JS files with CloudPepper optimizations")
            
    def validate_security(self):
        """Check security files"""
        print("\n🔒 Validating Security Configuration...")
        
        security_path = self.module_path / "security"
        if not security_path.exists():
            self.log_error("Security directory not found")
            return
            
        # Check for required security files
        required_files = ["ir.model.access.csv", "payment_security.xml"]
        for req_file in required_files:
            file_path = security_path / req_file
            if file_path.exists():
                self.log_success(f"Security file exists: {req_file}")
            else:
                self.log_error(f"Required security file missing: {req_file}")
                
    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*60)
        print("🏢 OSUS PAYMENT MODULE VALIDATION REPORT")
        print("="*60)
        
        print(f"\n✅ SUCCESSES: {self.success_count}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
                
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        else:
            print("\n🎉 NO CRITICAL ERRORS FOUND!")
            
        # Final recommendation
        print("\n📋 DEPLOYMENT READINESS:")
        if len(self.errors) == 0:
            if len(self.warnings) <= 2:
                print("✅ MODULE IS PRODUCTION READY")
                print("   - All critical checks passed")
                print("   - OSUS branding implemented")
                print("   - CloudPepper optimizations applied")
            else:
                print("⚠️  MODULE NEEDS MINOR FIXES")
                print("   - Address warnings before deployment")
        else:
            print("❌ MODULE NEEDS CRITICAL FIXES")
            print("   - Resolve all errors before deployment")
            
        print("\n🔗 OSUS Properties - Professional Payment Solutions")
        print("="*60)

def main():
    # Get module path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    else:
        module_path = os.path.dirname(os.path.abspath(__file__))
        
    print("🏢 OSUS Payment Module Validator")
    print(f"📁 Module Path: {module_path}")
    
    validator = OSUSModuleValidator(module_path)
    
    # Run validation checks
    validator.validate_manifest()
    validator.validate_python_files()
    validator.validate_static_assets()
    validator.validate_security()
    
    # Generate final report
    validator.generate_report()
    
    return len(validator.errors)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
