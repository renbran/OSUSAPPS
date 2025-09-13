#!/usr/bin/env python3
"""
Simple script to test module installation without external dependencies
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_module_structure():
    """Check if the module has all required files for installation"""
    logger.info("🔍 Checking module structure for Odoo installation...")
    
    module_path = "payment_account_enhanced"
    
    # Required files for a basic Odoo module
    required_files = [
        "__manifest__.py",
        "__init__.py",
        "models/__init__.py",
        "models/account_payment.py",
        "views/account_payment_views.xml",
        "views/menus.xml",
        "security/ir.model.access.csv",
        "security/security.xml"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = f"{module_path}/{file_path}"
        if os.path.exists(full_path):
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    # Report results
    logger.info("📋 MODULE STRUCTURE CHECK")
    logger.info("=" * 50)
    logger.info("✅ Found %d required files:", len(existing_files))
    for file_path in existing_files:
        logger.info("  ✓ %s", file_path)
    
    if missing_files:
        logger.error("❌ Missing %d required files:", len(missing_files))
        for file_path in missing_files:
            logger.error("  ✗ %s", file_path)
        return False
    
    logger.info("🎉 All required files present!")
    return True

def check_syntax():
    """Basic syntax check for Python files"""
    logger.info("🐍 Checking Python syntax...")
    
    python_files = [
        "payment_account_enhanced/__init__.py",
        "payment_account_enhanced/__manifest__.py",
        "payment_account_enhanced/models/__init__.py",
        "payment_account_enhanced/models/account_payment.py"
    ]
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                logger.info("  ✓ %s - syntax OK", file_path)
            except SyntaxError as e:
                logger.error("  ✗ %s - syntax error: %s", file_path, e)
                return False
    
    logger.info("✅ All Python files have valid syntax")
    return True

def main():
    """Main validation function"""
    logger.info("🚀 Starting module installation readiness check...")
    logger.info("=" * 60)
    
    # Check module structure
    if not check_module_structure():
        logger.error("❌ Module structure check failed")
        return False
    
    # Check syntax
    if not check_syntax():
        logger.error("❌ Syntax check failed")
        return False
    
    logger.info("=" * 60)
    logger.info("🎉 MODULE IS READY FOR INSTALLATION!")
    logger.info("✅ All structure checks passed")
    logger.info("✅ All syntax checks passed")
    logger.info("🔧 You can proceed with Odoo module installation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)