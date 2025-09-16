#!/usr/bin/env python3
import sys
import time
import requests
import json
import logging
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("dashboard_test_log.txt"),
        logging.StreamHandler()
    ]
)

class OdooTester:
    def __init__(self, host="localhost", port=8090, db="odoo", user="admin", password="admin"):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.uid = None
        self.errors = []
        self.warnings = []
        
    def login(self):
        """Log into Odoo and get user ID"""
        try:
            login_url = f"{self.url}/web/session/authenticate"
            payload = {
                "jsonrpc": "2.0",
                "params": {
                    "db": self.db,
                    "login": self.user,
                    "password": self.password,
                }
            }
            
            response = self.session.post(login_url, json=payload, timeout=30)
            result = response.json()
            
            if 'result' in result and result['result']:
                self.uid = result['result']['uid']
                logging.info(f"Successfully logged in as {self.user} (uid: {self.uid})")
                return True
            else:
                logging.error(f"Failed to login: {result.get('error', 'Unknown error')}")
                self.errors.append(f"Failed to login: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            logging.error(f"Error during login: {e}")
            self.errors.append(f"Error during login: {e}")
            return False
    
    def install_module(self):
        """Install the oe_sale_dashboard_17 module"""
        try:
            module_name = "oe_sale_dashboard_17"
            logging.info(f"Attempting to install module: {module_name}")
            
            # First check if module exists
            module_exists = self.call_kw('ir.module.module', 'search_count', 
                                       [[['name', '=', module_name]]])
            
            if not module_exists:
                logging.error(f"Module {module_name} not found in the system")
                self.errors.append(f"Module {module_name} not found in the system")
                return False
            
            # Check if it's already installed
            module_installed = self.call_kw('ir.module.module', 'search_count', 
                                          [[['name', '=', module_name], ['state', '=', 'installed']]])
            
            if module_installed:
                logging.info(f"Module {module_name} is already installed")
                return True
            
            # Get the module ID
            module_id = self.call_kw('ir.module.module', 'search', 
                                   [[['name', '=', module_name]]])
            
            if not module_id:
                logging.error(f"Could not find module ID for {module_name}")
                self.errors.append(f"Could not find module ID for {module_name}")
                return False
            
            # Install the module
            install_result = self.call_kw('ir.module.module', 'button_immediate_install', 
                                        [module_id])
            
            if install_result:
                logging.info(f"Successfully installed {module_name}")
                return True
            else:
                logging.error(f"Failed to install {module_name}")
                self.errors.append(f"Failed to install {module_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error during module installation: {e}")
            self.errors.append(f"Error during module installation: {e}")
            return False
    
    def call_kw(self, model, method, args=None, kwargs=None):
        """Call the ORM method on a model"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
            
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
                "context": {"lang": "en_US"},
            },
        }
        
        try:
            response = self.session.post(
                f"{self.url}/web/dataset/call_kw", json=payload, timeout=60
            )
            result = response.json()
            
            if "error" in result:
                error = result["error"]
                message = error.get("data", {}).get("message", error.get("message", "Unknown error"))
                logging.error(f"API Error: {message}")
                self.errors.append(f"API Error: {message}")
                return False
            
            return result.get("result")
        except Exception as e:
            logging.error(f"Error calling {model}.{method}: {e}")
            self.errors.append(f"Error calling {model}.{method}: {e}")
            return False

    def verify_models(self):
        """Verify that models exist in the system"""
        models_to_check = ['sales.dashboard', 'sales.dashboard.performer']
        results = {}
        
        for model in models_to_check:
            try:
                model_exists = self.call_kw('ir.model', 'search_count', 
                                           [[['model', '=', model]]])
                results[model] = bool(model_exists)
                
                if not model_exists:
                    logging.error(f"Model {model} does not exist")
                    self.errors.append(f"Model {model} does not exist")
                else:
                    logging.info(f"Model {model} exists")
                    
                    # Check fields
                    fields = self.call_kw('ir.model.fields', 'search_read', 
                                        [[['model', '=', model]]], {'fields': ['name', 'ttype']})
                    if fields:
                        logging.info(f"Fields for {model}: {len(fields)} fields found")
                    else:
                        logging.warning(f"No fields found for model {model}")
                        self.warnings.append(f"No fields found for model {model}")
                        
            except Exception as e:
                logging.error(f"Error verifying model {model}: {e}")
                self.errors.append(f"Error verifying model {model}: {e}")
                results[model] = False
                
        return results
    
    def check_asset_loading(self):
        """Check if JS and CSS assets can be loaded"""
        assets_to_check = [
            '/oe_sale_dashboard_17/static/src/js/dashboard_merged.js',
            '/oe_sale_dashboard_17/static/src/css/dashboard_merged.css',
            '/oe_sale_dashboard_17/static/src/js/chart.min.js'
        ]
        
        results = {}
        for asset in assets_to_check:
            try:
                url = f"{self.url}{asset}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    logging.info(f"Asset {asset} loaded successfully")
                    results[asset] = True
                else:
                    logging.error(f"Failed to load asset {asset}: Status code {response.status_code}")
                    self.errors.append(f"Failed to load asset {asset}: Status code {response.status_code}")
                    results[asset] = False
                    
            except Exception as e:
                logging.error(f"Error loading asset {asset}: {e}")
                self.errors.append(f"Error loading asset {asset}: {e}")
                results[asset] = False
                
        return results
    
    def check_menu_items(self):
        """Check if menu items are created properly"""
        try:
            # Find the Sales Analytics Hub menu item
            menu_items = self.call_kw('ir.ui.menu', 'search_read', 
                                    [[['name', 'ilike', 'Sales Analytics']]], 
                                    {'fields': ['name', 'complete_name']})
            
            if menu_items:
                logging.info(f"Found menu items: {menu_items}")
                return True
            else:
                logging.error("Could not find Sales Analytics menu items")
                self.errors.append("Could not find Sales Analytics menu items")
                return False
                
        except Exception as e:
            logging.error(f"Error checking menu items: {e}")
            self.errors.append(f"Error checking menu items: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return results"""
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "login_successful": False,
            "module_installation": False,
            "models": {},
            "assets": {},
            "menus": False,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        # Login
        login_success = self.login()
        test_results["login_successful"] = login_success
        
        if not login_success:
            return test_results
        
        # Install module
        install_success = self.install_module()
        test_results["module_installation"] = install_success
        
        if not install_success:
            return test_results
        
        # Give Odoo some time to process the installation
        logging.info("Waiting for module installation to complete...")
        time.sleep(5)
        
        # Verify models
        test_results["models"] = self.verify_models()
        
        # Check assets
        test_results["assets"] = self.check_asset_loading()
        
        # Check menu items
        test_results["menus"] = self.check_menu_items()
        
        # Save test results
        test_results["errors"] = self.errors
        test_results["warnings"] = self.warnings
        
        return test_results

def main():
    parser = argparse.ArgumentParser(description="Test Odoo Sales Dashboard Module")
    parser.add_argument("--host", default="localhost", help="Odoo host")
    parser.add_argument("--port", type=int, default=8090, help="Odoo port")
    parser.add_argument("--db", default="odoo", help="Odoo database name")
    parser.add_argument("--user", default="admin", help="Odoo username")
    parser.add_argument("--password", default="admin", help="Odoo password")
    
    args = parser.parse_args()
    
    tester = OdooTester(
        host=args.host,
        port=args.port,
        db=args.db,
        user=args.user,
        password=args.password
    )
    
    results = tester.run_all_tests()
    
    # Print summary
    print("\n========== TEST RESULTS ==========")
    print(f"Login successful: {results['login_successful']}")
    print(f"Module installation: {results['module_installation']}")
    
    print("\nModel verification:")
    for model, exists in results["models"].items():
        print(f"  - {model}: {'✓' if exists else '✗'}")
    
    print("\nAsset loading:")
    for asset, loaded in results["assets"].items():
        print(f"  - {asset}: {'✓' if loaded else '✗'}")
    
    print(f"\nMenu items created: {'✓' if results['menus'] else '✗'}")
    
    if results["errors"]:
        print("\nERRORS:")
        for error in results["errors"]:
            print(f"  - {error}")
    
    if results["warnings"]:
        print("\nWARNINGS:")
        for warning in results["warnings"]:
            print(f"  - {warning}")
    
    # Save results to file
    with open("dashboard_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Return exit code based on errors
    if results["errors"]:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())