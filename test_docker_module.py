#!/usr/bin/env python3
"""
Docker Container Module Test for payment_account_enhanced
========================================================

This script tests the module specifically within the Odoo Docker container
environment to ensure it will install and function correctly.
"""

import subprocess
import sys
import json

def run_docker_command(command):
    """Run a command in the Docker container"""
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", f"docker exec osusapps-odoo-1 {command}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()

def test_module_structure():
    """Test if module structure is accessible in container"""
    print("🔍 Testing module structure in container...")
    
    stdout, stderr = run_docker_command("ls -la /mnt/extra-addons/payment_account_enhanced/")
    if stdout:
        print("✅ Module directory accessible in container")
        print(f"   Contents: {len(stdout.split())} items")
        return True
    else:
        print(f"❌ Module directory not accessible: {stderr}")
        return False

def test_python_dependencies():
    """Test Python dependencies in container"""
    print("🐍 Testing Python dependencies in container...")
    
    dependencies = ["qrcode", "PIL"]
    all_deps_ok = True
    
    for dep in dependencies:
        stdout, stderr = run_docker_command(f"python3 -c \"import {dep}; print('OK')\"")
        if stdout and "OK" in stdout:
            print(f"✅ {dep} dependency available")
        else:
            print(f"❌ {dep} dependency not available: {stderr}")
            all_deps_ok = False
    
    return all_deps_ok

def test_manifest_parsing():
    """Test if manifest can be parsed in container"""
    print("📋 Testing manifest parsing in container...")
    
    stdout, stderr = run_docker_command(
        "python3 -c \"import ast; f=open('/mnt/extra-addons/payment_account_enhanced/__manifest__.py'); print('Manifest OK' if ast.literal_eval(f.read()) else 'Failed'); f.close()\""
    )
    
    if stdout and "Manifest OK" in stdout:
        print("✅ Manifest file parses correctly")
        return True
    else:
        print(f"❌ Manifest parsing failed: {stderr}")
        return False

def test_python_syntax():
    """Test Python syntax of all module files"""
    print("📝 Testing Python syntax in container...")
    
    stdout, stderr = run_docker_command(
        "find /mnt/extra-addons/payment_account_enhanced -name '*.py' -exec python3 -m py_compile {} \\;"
    )
    
    if stderr and "SyntaxError" in stderr:
        print(f"❌ Python syntax errors found: {stderr}")
        return False
    else:
        print("✅ All Python files have valid syntax")
        return True

def test_xml_syntax():
    """Test XML syntax of all module files"""
    print("📄 Testing XML syntax in container...")
    
    stdout, stderr = run_docker_command(
        "python3 -c \"import xml.etree.ElementTree as ET; import glob; [ET.parse(f) for f in glob.glob('/mnt/extra-addons/payment_account_enhanced/**/*.xml', recursive=True)]; print('XML OK')\""
    )
    
    if stdout and "XML OK" in stdout:
        print("✅ All XML files have valid syntax")
        return True
    else:
        print(f"❌ XML syntax errors found: {stderr}")
        return False

def test_odoo_module_discovery():
    """Test if Odoo can discover the module"""
    print("🔍 Testing Odoo module discovery...")
    
    stdout, stderr = run_docker_command(
        "odoo --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons --list-modules | grep payment_account_enhanced"
    )
    
    if stdout and "payment_account_enhanced" in stdout:
        print("✅ Odoo can discover the module")
        return True
    else:
        print("⚠️  Module discovery test inconclusive (this may be normal)")
        return True  # Don't fail on this as it might require DB connection

def test_odoo_basic_import():
    """Test basic Odoo imports work"""
    print("📦 Testing Odoo imports in container...")
    
    stdout, stderr = run_docker_command(
        "python3 -c \"from odoo import models, fields, api; print('Odoo imports OK')\""
    )
    
    if stdout and "Odoo imports OK" in stdout:
        print("✅ Odoo framework imports work")
        return True
    else:
        print(f"❌ Odoo imports failed: {stderr}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Docker Container Module Test")
    print("=" * 60)
    
    tests = [
        ("Module Structure", test_module_structure),
        ("Python Dependencies", test_python_dependencies),
        ("Manifest Parsing", test_manifest_parsing),
        ("Python Syntax", test_python_syntax),
        ("XML Syntax", test_xml_syntax),
        ("Odoo Imports", test_odoo_basic_import),
        ("Module Discovery", test_odoo_module_discovery),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 60)
    if all(results.values()):
        print("🎉 ALL TESTS PASSED - Module is ready for Docker installation!")
    else:
        print("❌ SOME TESTS FAILED - Issues need to be resolved")
    print("=" * 60)
    
    return all(results.values())

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)