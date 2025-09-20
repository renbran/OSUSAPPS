#!/usr/bin/env python3
import ast
import os
import glob

def check_manifest(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the AST
        try:
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except ValueError as e:
            if "malformed node" in str(e):
                return False, f"Malformed AST node: {e}"
            return False, f"ValueError: {e}"
    except Exception as e:
        return False, f"File error: {e}"

def main():
    manifest_files = glob.glob('*/__manifest__.py', recursive=True)
    
    print(f"Checking {len(manifest_files)} manifest files...\n")
    
    errors_found = []
    line_13_errors = []
    
    for manifest in sorted(manifest_files):
        is_valid, error_msg = check_manifest(manifest)
        if not is_valid:
            errors_found.append((manifest, error_msg))
            if "Line 13" in error_msg or "malformed node" in error_msg:
                line_13_errors.append((manifest, error_msg))
                print(f"⚠️  LINE 13 ERROR: {manifest}")
                print(f"   {error_msg}")
                
                # Show context around line 13
                try:
                    with open(manifest, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    if len(lines) >= 13:
                        print(f"   Context around line 13:")
                        for i in range(max(0, 10), min(len(lines), 16)):
                            marker = ">>> " if i == 12 else "    "
                            print(f"   {marker}{i+1:2d}: {lines[i].rstrip()}")
                except:
                    pass
                print()
            else:
                print(f"❌ {manifest}: {error_msg}")
        else:
            print(f"✅ {manifest}")
    
    print(f"\nSummary:")
    print(f"Total files checked: {len(manifest_files)}")
    print(f"Files with errors: {len(errors_found)}")
    print(f"Files with line 13/malformed errors: {len(line_13_errors)}")
    
    if line_13_errors:
        print(f"\n⚠️  CRITICAL: Found {len(line_13_errors)} file(s) with line 13/malformed errors:")
        for manifest, error in line_13_errors:
            print(f"   - {manifest}: {error}")

if __name__ == "__main__":
    main()