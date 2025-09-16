# -*- coding: utf-8 -*-
"""
OE Sales Dashboard 17 Module Tester
===================================

This script performs comprehensive testing of the oe_sale_dashboard_17 Odoo module,
validating its structure, models, relationships, and dependencies.

Usage:
    Run this script within the Odoo container.
    docker-compose exec odoo python3 /mnt/extra-addons/oe_sale_dashboard_17/tests/test_module.py

Requirements:
    - Running Odoo container
    - Module installed in database
"""

import sys
import os
import logging
import json
from datetime import datetime

# Add Odoo paths to sys.path
odoo_path = "/usr/lib/python3/dist-packages"
if odoo_path not in sys.path:
    sys.path.insert(0, odoo_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('oe_sale_dashboard_test.log')
    ]
)
logger = logging.getLogger('module_tester')

try:
    import odoo
    from odoo.tools import config
    from odoo.exceptions import ValidationError
except ImportError:
    logger.error("Failed to import Odoo. Make sure this script is run within an Odoo container.")
    sys.exit(1)

class ModuleTester:
    """Test Odoo modules systematically and report issues."""
    
    def __init__(self, module_name, db_name="odoo"):
        self.module_name = module_name
        self.db_name = db_name
        self.issues = []
        self.warnings = []
        self.env = None
        self.module = None

    def setup_odoo(self):
        """Configure Odoo environment for testing."""
        logger.info(f"Setting up Odoo environment for {self.db_name}")
        config['db_name'] = self.db_name
        
        # Initialize Odoo environment
        odoo.cli.server.report_configuration()
        
        try:
            registry = odoo.modules.registry.Registry.new(self.db_name)
            with registry.cursor() as cr:
                self.env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                logger.info("Odoo environment successfully initialized")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize Odoo environment: {str(e)}")
            self.issues.append(f"Database connection error: {str(e)}")
            return False

    def test_module_installation(self):
        """Check if module is properly installed."""
        logger.info(f"Testing if {self.module_name} is installed")
        
        if not self.env:
            logger.error("Environment not initialized")
            return False
            
        IrModule = self.env['ir.module.module']
        self.module = IrModule.search([('name', '=', self.module_name)], limit=1)
        
        if not self.module:
            self.issues.append(f"Module {self.module_name} not found in installed modules")
            logger.error(f"Module {self.module_name} not found")
            return False
            
        if self.module.state != 'installed':
            self.issues.append(f"Module {self.module_name} is not installed (state: {self.module.state})")
            logger.error(f"Module {self.module_name} is not installed (state: {self.module.state})")
            return False
            
        logger.info(f"Module {self.module_name} is properly installed")
        return True

    def test_model_definitions(self):
        """Test if all models in the module are properly defined."""
        logger.info("Testing model definitions")
        
        if not self.env or not self.module:
            logger.error("Environment or module not initialized")
            return False
            
        IrModel = self.env['ir.model']
        models = IrModel.search([('modules', 'like', self.module_name)])
        
        logger.info(f"Found {len(models)} models defined in {self.module_name}")
        
        if not models:
            self.warnings.append("No models defined in this module")
            logger.warning("No models defined in this module")
            
        for model in models:
            logger.info(f"Testing model: {model.model}")
            
            # Check if model class exists in registry
            if model.model not in self.env:
                self.issues.append(f"Model {model.model} exists in ir.model but not in registry")
                continue
                
            # Test required fields
            model_obj = self.env[model.model]
            missing_required = []
            
            for field_name, field in model_obj._fields.items():
                if field.required and not field.related and not field.compute and not field.default:
                    try:
                        # Create a record without this field to see if it's truly required
                        test_data = {f: 'Test' if f != field_name else False for f in model_obj._fields 
                                    if model_obj._fields[f].type == 'char' and model_obj._fields[f].required}
                        if test_data:  # Only test if we have required char fields to test with
                            model_obj.create(test_data)
                            missing_required.append(field_name)
                    except ValidationError:
                        # This is expected for truly required fields
                        pass
                    except Exception as e:
                        logger.warning(f"Error testing required field {field_name}: {str(e)}")
            
            if missing_required:
                self.issues.append(f"Model {model.model} has fields marked as required but without enforcement: {', '.join(missing_required)}")
        
        return True

    def test_security_definitions(self):
        """Test security access rules for module models."""
        logger.info("Testing security definitions")
        
        if not self.env or not self.module:
            logger.error("Environment or module not initialized")
            return False
            
        IrModel = self.env['ir.model']
        IrModelAccess = self.env['ir.model.access']
        
        models = IrModel.search([('modules', 'like', self.module_name)])
        
        for model in models:
            logger.info(f"Testing security for model: {model.model}")
            
            # Check for access rules
            access_rules = IrModelAccess.search([('model_id', '=', model.id)])
            
            if not access_rules:
                self.issues.append(f"No access rules defined for model: {model.model}")
                continue
                
            # Check for common security groups
            has_user_access = False
            has_manager_access = False
            
            for rule in access_rules:
                if rule.group_id and 'user' in rule.group_id.name.lower():
                    has_user_access = True
                if rule.group_id and 'manager' in rule.group_id.name.lower():
                    has_manager_access = True
            
            if not has_user_access:
                self.warnings.append(f"No user-level access rules for model: {model.model}")
                
            if not has_manager_access:
                self.warnings.append(f"No manager-level access rules for model: {model.model}")
        
        return True

    def test_view_definitions(self):
        """Test view definitions for module models."""
        logger.info("Testing view definitions")
        
        if not self.env or not self.module:
            logger.error("Environment or module not initialized")
            return False
            
        IrModel = self.env['ir.model']
        IrUiView = self.env['ir.ui.view']
        
        models = IrModel.search([('modules', 'like', self.module_name)])
        
        for model in models:
            model_name = model.model
            logger.info(f"Testing views for model: {model_name}")
            
            # Check for form, tree, search views
            form_views = IrUiView.search([('model', '=', model_name), ('type', '=', 'form')])
            tree_views = IrUiView.search([('model', '=', model_name), ('type', '=', 'tree')])
            search_views = IrUiView.search([('model', '=', model_name), ('type', '=', 'search')])
            
            if not form_views:
                self.warnings.append(f"No form view defined for model: {model_name}")
            else:
                logger.info(f"Found {len(form_views)} form view(s) for {model_name}")
                
            if not tree_views:
                self.warnings.append(f"No tree view defined for model: {model_name}")
            else:
                logger.info(f"Found {len(tree_views)} tree view(s) for {model_name}")
                
            if not search_views:
                self.warnings.append(f"No search view defined for model: {model_name}")
            else:
                logger.info(f"Found {len(search_views)} search view(s) for {model_name}")
                
            # Check for XML validity
            for view in list(form_views) + list(tree_views) + list(search_views):
                if not view._check_xml():
                    self.issues.append(f"Invalid XML in view {view.name} (ID: {view.id})")
        
        return True

    def test_menu_items(self):
        """Test menu items for module."""
        logger.info("Testing menu items")
        
        if not self.env or not self.module:
            logger.error("Environment or module not initialized")
            return False
            
        IrUiMenu = self.env['ir.ui.menu']
        
        # Check for menu items from this module
        menus = IrUiMenu.search([('web_icon', '!=', False), ('name', 'ilike', '%dashboard%'), ('name', 'ilike', '%sale%')])
        if not menus:
            menus = IrUiMenu.search([('name', 'ilike', '%dashboard%'), ('name', 'ilike', '%sale%')])
            
        if not menus:
            self.warnings.append("No dashboard menu items found")
            logger.warning("No dashboard menu items found")
        else:
            logger.info(f"Found {len(menus)} dashboard menu items")
            
        return True

    def test_assets(self):
        """Test asset bundles for the module."""
        logger.info("Testing asset bundles")
        
        if not self.env or not self.module:
            logger.error("Environment or module not initialized")
            return False
            
        IrAsset = self.env['ir.asset']
        
        # Check for assets from this module
        assets = IrAsset.search([('path', 'like', self.module_name)])
        
        if not assets:
            self.warnings.append("No assets defined for this module")
            logger.warning("No assets defined for this module")
        else:
            logger.info(f"Found {len(assets)} asset definitions")
            
            # Check if the JS and CSS files actually exist
            module_path = os.path.join('/mnt/extra-addons', self.module_name)
            
            for asset in assets:
                path = asset.path.replace(self.module_name + '/', '')
                file_path = os.path.join(module_path, path)
                
                if not os.path.exists(file_path) and not asset.path.startswith(('http://', 'https://')):
                    self.issues.append(f"Asset file not found: {asset.path}")
        
        return True

    def run_tests(self):
        """Run all tests and return a report."""
        logger.info(f"Starting tests for module {self.module_name}")
        
        start_time = datetime.now()
        success = self.setup_odoo()
        
        if not success:
            logger.error("Failed to set up Odoo environment. Cannot continue testing.")
            return self.generate_report(start_time)
            
        tests = [
            self.test_module_installation,
            self.test_model_definitions,
            self.test_security_definitions,
            self.test_view_definitions,
            self.test_menu_items,
            self.test_assets
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Error in test {test.__name__}: {str(e)}")
                self.issues.append(f"Test error in {test.__name__}: {str(e)}")
        
        return self.generate_report(start_time)

    def generate_report(self, start_time):
        """Generate a report of the test results."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        report = {
            "module": self.module_name,
            "test_date": end_time.isoformat(),
            "duration": duration,
            "issues": self.issues,
            "warnings": self.warnings,
            "issues_count": len(self.issues),
            "warnings_count": len(self.warnings),
            "status": "SUCCESS" if not self.issues else "FAILURE"
        }
        
        # Print summary to console
        logger.info("=" * 80)
        logger.info(f"TEST REPORT FOR MODULE: {self.module_name}")
        logger.info("=" * 80)
        logger.info(f"Status: {report['status']}")
        logger.info(f"Issues: {report['issues_count']}")
        logger.info(f"Warnings: {report['warnings_count']}")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        if self.issues:
            logger.info("\nISSUES:")
            for i, issue in enumerate(self.issues, 1):
                logger.info(f"{i}. {issue}")
                
        if self.warnings:
            logger.info("\nWARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                logger.info(f"{i}. {warning}")
        
        # Save report to JSON file
        with open(f"{self.module_name}_test_report.json", 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"\nDetailed report saved to: {self.module_name}_test_report.json")
        
        return report

if __name__ == "__main__":
    module_name = "oe_sale_dashboard_17"
    tester = ModuleTester(module_name)
    tester.run_tests()