#!/usr/bin/env python3
"""
Comprehensive Module Analysis for rental_management
Checks installability, structure, and provides improvement recommendations
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import re

class RentalModuleAnalyzer:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.stats = {}
        
    def analyze_manifest(self):
        """Analyze __manifest__.py for issues"""
        print("🔍 Analyzing Manifest File...")
        manifest_path = self.module_path / "__manifest__.py"
        
        if not manifest_path.exists():
            self.issues.append("CRITICAL: __manifest__.py not found")
            return False
            
        try:
            # Read manifest content
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check required fields
            required_fields = ['name', 'version', 'depends', 'data', 'installable']
            for field in required_fields:
                if f"'{field}'" not in content and f'"{field}"' not in content:
                    self.issues.append(f"Missing required field: {field}")
            
            # Check installable flag
            if 'installable' in content:
                if '"installable": True' in content or "'installable': True" in content:
                    print("  ✅ Module is marked as installable")
                else:
                    self.issues.append("Module is marked as not installable")
            
            # Check auto_install
            if 'auto_install' in content:
                if '"auto_install": True' in content or "'auto_install': True" in content:
                    self.warnings.append("Module has auto_install=True - may cause unexpected installations")
            
            # Extract data files for validation
            data_pattern = r'"data":\s*\[(.*?)\]'
            match = re.search(data_pattern, content, re.DOTALL)
            if match:
                data_content = match.group(1)
                data_files = re.findall(r'"([^"]+\.xml)"', data_content)
                self.stats['data_files'] = len(data_files)
                
                # Check if files exist
                missing_files = []
                for data_file in data_files:
                    file_path = self.module_path / data_file
                    if not file_path.exists():
                        missing_files.append(data_file)
                
                if missing_files:
                    self.issues.extend([f"Missing data file: {f}" for f in missing_files])
                else:
                    print(f"  ✅ All {len(data_files)} data files exist")
            
            return True
            
        except Exception as e:
            self.issues.append(f"Error reading manifest: {str(e)}")
            return False
    
    def analyze_structure(self):
        """Analyze module directory structure"""
        print("🏗️  Analyzing Module Structure...")
        
        required_dirs = ['models', 'views', 'security']
        recommended_dirs = ['static', 'data', 'wizard', 'tests', 'controllers']
        
        existing_dirs = [d.name for d in self.module_path.iterdir() if d.is_dir()]
        
        # Check required directories
        for req_dir in required_dirs:
            if req_dir not in existing_dirs:
                self.issues.append(f"Missing required directory: {req_dir}")
            else:
                print(f"  ✅ {req_dir}/ directory exists")
        
        # Check recommended directories
        for rec_dir in recommended_dirs:
            if rec_dir not in existing_dirs:
                self.suggestions.append(f"Consider adding {rec_dir}/ directory for better organization")
            else:
                print(f"  ✅ {rec_dir}/ directory exists")
        
        # Check for __init__.py files
        init_files = list(self.module_path.rglob("__init__.py"))
        self.stats['init_files'] = len(init_files)
        
        if not (self.module_path / "__init__.py").exists():
            self.issues.append("Missing root __init__.py file")
        
        return len(self.issues) == 0
    
    def analyze_security(self):
        """Analyze security configuration"""
        print("🔒 Analyzing Security Configuration...")
        
        security_dir = self.module_path / "security"
        if not security_dir.exists():
            self.issues.append("Security directory missing")
            return False
        
        # Check for access rights file
        access_file = security_dir / "ir.model.access.csv"
        if not access_file.exists():
            self.issues.append("Missing ir.model.access.csv")
        else:
            # Analyze access rights
            with open(access_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('id,')]
                self.stats['access_rules'] = len(lines)
                print(f"  ✅ Found {len(lines)} access rules")
        
        # Check for security groups
        groups_file = security_dir / "groups.xml"
        security_file = security_dir / "security.xml"
        
        if groups_file.exists():
            print("  ✅ Security groups file exists")
        if security_file.exists():
            print("  ✅ Security rules file exists")
        
        return True
    
    def analyze_models(self):
        """Analyze model definitions"""
        print("📊 Analyzing Models...")
        
        models_dir = self.module_path / "models"
        if not models_dir.exists():
            return False
        
        py_files = list(models_dir.glob("*.py"))
        model_count = 0
        
        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue
                
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Count models
            model_matches = re.findall(r'class\s+\w+\(models\.Model\):', content)
            model_count += len(model_matches)
            
            # Check for common issues
            if 'sudo()' in content:
                self.warnings.append(f"Model {py_file.name} contains sudo() calls - review security")
            
            if '_name =' in content and '_description =' not in content:
                self.suggestions.append(f"Model {py_file.name} missing _description field")
            
            if len(content.split('\n')) > 500:
                self.suggestions.append(f"Model {py_file.name} is large ({len(content.split('\n'))} lines) - consider splitting")
        
        self.stats['models'] = model_count
        self.stats['model_files'] = len(py_files) - 1  # Exclude __init__.py
        print(f"  ✅ Found {model_count} models in {len(py_files)-1} files")
        
        return True
    
    def analyze_views(self):
        """Analyze view definitions"""
        print("👁️  Analyzing Views...")
        
        views_dir = self.module_path / "views"
        if not views_dir.exists():
            return False
        
        xml_files = list(views_dir.glob("*.xml"))
        view_count = 0
        action_count = 0
        menu_count = 0
        
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                
                # Count different elements
                views = tree.findall('.//record[@model="ir.ui.view"]')
                actions = tree.findall('.//record[@model="ir.actions.act_window"]')
                menus = tree.findall('.//menuitem')
                
                view_count += len(views)
                action_count += len(actions)
                menu_count += len(menus)
                
                # Check for issues
                for view in views:
                    view_id = view.get('id')
                    if not view_id:
                        self.warnings.append(f"View without id in {xml_file.name}")
                
            except ET.ParseError as e:
                self.issues.append(f"XML parse error in {xml_file.name}: {str(e)}")
        
        self.stats['views'] = view_count
        self.stats['actions'] = action_count
        self.stats['menus'] = menu_count
        self.stats['view_files'] = len(xml_files)
        
        print(f"  ✅ Found {view_count} views, {action_count} actions, {menu_count} menus in {len(xml_files)} files")
        
        return True
    
    def analyze_dependencies(self):
        """Analyze module dependencies"""
        print("🔗 Analyzing Dependencies...")
        
        # Standard Odoo modules
        standard_modules = {
            'base', 'web', 'mail', 'contacts', 'account', 'sale', 'purchase',
            'stock', 'hr', 'crm', 'project', 'website', 'maintenance', 'fleet'
        }
        
        # Extract dependencies from manifest
        manifest_path = self.module_path / "__manifest__.py"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        deps_pattern = r'"depends":\s*\[(.*?)\]'
        match = re.search(deps_pattern, content, re.DOTALL)
        
        if match:
            deps_content = match.group(1)
            dependencies = re.findall(r'"([^"]+)"', deps_content)
            
            self.stats['dependencies'] = len(dependencies)
            
            # Check for non-standard dependencies
            non_standard = [dep for dep in dependencies if dep not in standard_modules]
            if non_standard:
                self.warnings.extend([f"Non-standard dependency: {dep}" for dep in non_standard])
            
            print(f"  ✅ Found {len(dependencies)} dependencies ({len(non_standard)} non-standard)")
        
        return True
    
    def analyze_tests(self):
        """Analyze test coverage"""
        print("🧪 Analyzing Tests...")
        
        tests_dir = self.module_path / "tests"
        if not tests_dir.exists():
            self.suggestions.append("Add tests/ directory for better quality assurance")
            return False
        
        test_files = list(tests_dir.glob("test_*.py"))
        self.stats['test_files'] = len(test_files)
        
        if len(test_files) == 0:
            self.warnings.append("No test files found in tests/ directory")
        else:
            print(f"  ✅ Found {len(test_files)} test files")
            
            # Analyze test quality
            total_test_methods = 0
            for test_file in test_files:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    test_methods = re.findall(r'def test_\w+', content)
                    total_test_methods += len(test_methods)
            
            self.stats['test_methods'] = total_test_methods
            print(f"  ✅ Found {total_test_methods} test methods")
        
        return True
    
    def check_integration_patterns(self):
        """Check for proper integration patterns"""
        print("🔄 Analyzing Integration Patterns...")
        
        # Check for proper inheritance patterns
        models_dir = self.module_path / "models"
        inheritance_count = 0
        
        if models_dir.exists():
            for py_file in models_dir.glob("*.py"):
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check for _inherit usage
                if '_inherit =' in content:
                    inheritance_count += 1
                    print(f"  ✅ Found model inheritance in {py_file.name}")
                
                # Check for proper API usage
                if '@api.' in content:
                    print(f"  ✅ Uses Odoo API decorators in {py_file.name}")
        
        self.stats['inherited_models'] = inheritance_count
        
        # Check for controller patterns
        controllers_dir = self.module_path / "controllers"
        if controllers_dir.exists():
            controller_files = list(controllers_dir.glob("*.py"))
            self.stats['controller_files'] = len(controller_files) - 1  # Exclude __init__.py
            if len(controller_files) > 1:
                print(f"  ✅ Found {len(controller_files)-1} controller files")
        
        return True
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE MODULE ANALYSIS REPORT")
        print("="*80)
        
        # Summary
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        total_suggestions = len(self.suggestions)
        
        if total_issues == 0:
            print("✅ MODULE IS INSTALLABLE")
        else:
            print("❌ MODULE HAS INSTALLATION ISSUES")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Issues: {total_issues}")
        print(f"  Warnings: {total_warnings}")
        print(f"  Suggestions: {total_suggestions}")
        
        # Statistics
        print(f"\n📈 STATISTICS:")
        for key, value in self.stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Issues
        if self.issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  ❌ {issue}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        # Suggestions
        if self.suggestions:
            print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
            for suggestion in self.suggestions:
                print(f"  💡 {suggestion}")
        
        return total_issues == 0

def main():
    module_path = "rental_management"
    
    if not os.path.exists(module_path):
        print(f"❌ Module path {module_path} not found")
        return False
    
    analyzer = RentalModuleAnalyzer(module_path)
    
    # Run all analyses
    analyzer.analyze_manifest()
    analyzer.analyze_structure()
    analyzer.analyze_security()
    analyzer.analyze_models()
    analyzer.analyze_views()
    analyzer.analyze_dependencies()
    analyzer.analyze_tests()
    analyzer.check_integration_patterns()
    
    # Generate report
    is_installable = analyzer.generate_report()
    
    return is_installable

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)