#!/usr/bin/env python3
import ast
import glob
import os

def validate_manifest_in_context(filepath):
    """Validate manifest file in the context that Odoo would load it"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try parsing as Odoo would - as a dictionary literal
        try:
            result = ast.literal_eval(content)
            return True, None, result
        except (ValueError, SyntaxError) as e:
            return False, str(e), None
    except Exception as e:
        return False, f"File read error: {e}", None

def main():
    print("🔍 Scanning all manifest files for AST issues...")
    
    # Get all manifest files
    manifest_files = glob.glob('*/__manifest__.py')
    
    issues = []
    
    for manifest_file in sorted(manifest_files):
        is_valid, error, manifest_data = validate_manifest_in_context(manifest_file)
        
        if not is_valid:
            issues.append((manifest_file, error))
            
            # Check if this is a line 13 issue specifically
            if "line 13" in error.lower() or "malformed" in error.lower():
                print(f"🚨 CRITICAL ISSUE in {manifest_file}:")
                print(f"   Error: {error}")
                
                # Show context around the problematic area
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    print(f"   File context:")
                    for i, line in enumerate(lines):
                        line_num = i + 1
                        marker = ">>> " if line_num == 13 else "    "
                        print(f"   {marker}{line_num:2d}: {line.rstrip()}")
                        if line_num >= 20:  # Limit output
                            break
                except Exception as e:
                    print(f"   Could not read file context: {e}")
                print()
            else:
                print(f"❌ {manifest_file}: {error}")
        else:
            print(f"✅ {manifest_file}")
    
    print(f"\n📊 Summary:")
    print(f"   Total files: {len(manifest_files)}")
    print(f"   Issues found: {len(issues)}")
    
    if issues:
        print(f"\n🔥 Files with issues:")
        for filepath, error in issues:
            print(f"   - {filepath}: {error}")

if __name__ == "__main__":
    main()