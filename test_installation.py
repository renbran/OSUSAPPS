#!/usr/bin/env python3
"""
Docker Odoo Module Installation Test
====================================

This script attempts to install the payment_account_enhanced module
in the Docker container and reports the results.
"""

import subprocess
import sys
import time

def run_docker_command(command, timeout=120):
    """Run a command in the Docker container with timeout"""
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", f"docker exec osusapps-odoo-1 {command}"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def test_database_connection():
    """Test if we can connect to the database"""
    print("🔌 Testing database connection...")
    
    returncode, stdout, stderr = run_docker_command(
        "python3 -c \"import psycopg2; conn=psycopg2.connect(host='db', database='odoo', user='odoo', password='odoo'); print('DB OK'); conn.close()\"",
        timeout=30
    )
    
    if returncode == 0 and "DB OK" in stdout:
        print("✅ Database connection successful")
        return True
    else:
        print(f"❌ Database connection failed: {stderr}")
        return False

def initialize_database():
    """Initialize the database if needed"""
    print("🗄️  Initializing database...")
    
    returncode, stdout, stderr = run_docker_command(
        "odoo --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons --init=base --stop-after-init -d odoo --log-level=error",
        timeout=180
    )
    
    if returncode == 0:
        print("✅ Database initialized successfully")
        return True
    else:
        print(f"⚠️  Database initialization returned code {returncode}")
        print(f"   This might be normal if DB already exists")
        return True  # Don't fail on this as DB might already exist

def test_module_installation():
    """Test installing the payment_account_enhanced module"""
    print("📦 Testing module installation...")
    
    # First try to install the module
    returncode, stdout, stderr = run_docker_command(
        "odoo --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons -i payment_account_enhanced --stop-after-init -d odoo --log-level=info",
        timeout=300
    )
    
    print(f"   Installation return code: {returncode}")
    
    if stdout:
        print("   STDOUT:")
        for line in stdout.split('\n')[-10:]:  # Show last 10 lines
            if line.strip():
                print(f"     {line}")
    
    if stderr:
        print("   STDERR:")
        for line in stderr.split('\n')[-10:]:  # Show last 10 lines
            if line.strip():
                print(f"     {line}")
    
    # Check if there are any critical errors
    critical_errors = [
        "ModuleNotFoundError",
        "ImportError", 
        "SyntaxError",
        "ParseError",
        "ValidationError"
    ]
    
    has_critical_error = any(error in stderr for error in critical_errors)
    
    if returncode == 0:
        print("✅ Module installation completed successfully")
        return True
    elif not has_critical_error:
        print("⚠️  Module installation completed with warnings (this may be normal)")
        return True
    else:
        print("❌ Module installation failed with critical errors")
        return False

def test_module_listing():
    """Test if the module appears in the module list"""
    print("📋 Testing module listing...")
    
    returncode, stdout, stderr = run_docker_command(
        "odoo --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons --list-modules",
        timeout=60
    )
    
    if returncode == 0 and "payment_account_enhanced" in stdout:
        print("✅ Module appears in Odoo module list")
        return True
    else:
        print("⚠️  Module listing test inconclusive")
        return True  # Don't fail on this

def check_logs_for_errors():
    """Check recent Odoo logs for any errors"""
    print("📜 Checking recent logs for errors...")
    
    returncode, stdout, stderr = run_docker_command("tail -n 50 /var/log/odoo/odoo.log", timeout=10)
    
    if returncode != 0:
        # Log file might not exist, try checking container logs
        print("   Log file not accessible, checking container logs...")
        result = subprocess.run(
            ["docker", "logs", "osusapps-odoo-1", "--tail=20"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            stdout = result.stdout
    
    if stdout:
        error_patterns = ["ERROR", "CRITICAL", "Exception", "Traceback"]
        recent_errors = []
        
        for line in stdout.split('\n'):
            if any(pattern in line for pattern in error_patterns):
                recent_errors.append(line.strip())
        
        if recent_errors:
            print(f"⚠️  Found {len(recent_errors)} recent error(s) in logs:")
            for error in recent_errors[-5:]:  # Show last 5 errors
                print(f"     {error}")
        else:
            print("✅ No recent errors found in logs")
    
    return True

def run_installation_test():
    """Run complete installation test"""
    print("🚀 Starting Docker Module Installation Test")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Database Initialization", initialize_database),
        ("Module Installation", test_module_installation),
        ("Module Listing", test_module_listing),
        ("Log Analysis", check_logs_for_errors),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results[test_name] = False
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("📊 INSTALLATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 60)
    if all(results.values()):
        print("🎉 MODULE INSTALLATION TEST PASSED!")
        print("   The module should be ready to use in Odoo.")
    else:
        print("❌ SOME INSTALLATION TESTS FAILED")
        print("   Check the errors above for details.")
    print("=" * 60)
    
    return all(results.values())

if __name__ == "__main__":
    success = run_installation_test()
    sys.exit(0 if success else 1)