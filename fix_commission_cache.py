#!/usr/bin/env python3
"""
Fix commission module caching issues by force reinstalling
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"Exit Code: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main execution"""
    os.chdir(r"d:\GitHub\osus_main\cleanup osus\OSUSAPPS")
    
    commands = [
        ("docker-compose down", "Stopping Docker containers"),
        ("docker-compose up -d", "Starting Docker containers"),
        ("docker-compose exec odoo odoo --uninstall=commission_ax --stop-after-init", "Uninstalling commission_ax module"),
        ("docker-compose exec odoo odoo --update=all --stop-after-init", "Updating all modules"),
        ("docker-compose exec odoo odoo --install=commission_ax --stop-after-init", "Installing commission_ax module"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"FAILED: {desc}")
            sys.exit(1)
            
    print("\n" + "="*60)
    print("SUCCESS: Commission module reinstallation completed!")
    print("="*60)

if __name__ == "__main__":
    main()
