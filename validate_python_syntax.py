#!/usr/bin/env python3
"""
Python syntax validation for partner_statement_followup module
"""

import ast
import os

def check_python_syntax(file_path):
    """Check Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the Python code
        ast.parse(content, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=== Python Syntax Validation ===\n")
    
    python_files = []
    
    # Collect all Python files
    for root, dirs, files in os.walk("partner_statement_followup"):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    
    for py_file in python_files:
        is_valid, error = check_python_syntax(py_file)
        if is_valid:
            print(f"✓ {py_file}")
        else:
            print(f"❌ {py_file}: {error}")
            errors.append(f"{py_file}: {error}")
    
    print("\n" + "="*50)
    if errors:
        print("❌ PYTHON VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("✅ PYTHON VALIDATION PASSED")
        print(f"All {len(python_files)} Python files have valid syntax.")
        return 0

if __name__ == "__main__":
    exit(main())
