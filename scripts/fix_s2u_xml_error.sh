#!/bin/bash

# S2U Online Appointment XML Fix Script
# This script helps resolve the XML syntax error in s2u_online_appointment module

echo "🔍 Searching for s2u_online_appointment module..."

# Search for the module in common locations
SEARCH_PATHS=(
    "/mnt/extra-addons"
    "/var/odoo/addons"
    "/opt/odoo/addons" 
    "/usr/lib/python*/dist-packages/odoo/addons"
    "/var/odoo/properties/extra-addons"
)

MODULE_FOUND=""
for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "Checking: $path"
        FOUND=$(find "$path" -name "*s2u_online_appointment*" -type d 2>/dev/null | head -1)
        if [ -n "$FOUND" ]; then
            MODULE_FOUND="$FOUND"
            echo "✅ Found module at: $MODULE_FOUND"
            break
        fi
    fi
done

if [ -z "$MODULE_FOUND" ]; then
    echo "❌ Module not found in standard locations"
    echo "🔍 Searching entire filesystem (this may take a moment)..."
    MODULE_FOUND=$(find / -name "*s2u_online_appointment*" -type d 2>/dev/null | head -1)
fi

if [ -n "$MODULE_FOUND" ]; then
    XML_FILE="$MODULE_FOUND/data/default_data.xml"
    
    if [ -f "$XML_FILE" ]; then
        echo "📄 Found XML file: $XML_FILE"
        
        # Create backup
        cp "$XML_FILE" "$XML_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        echo "💾 Backup created"
        
        # Show lines around error (line 74)
        echo "🔍 Lines 70-80 of the XML file:"
        sed -n '70,80p' "$XML_FILE"
        
        echo ""
        echo "🛠️ Applying common XML fixes..."
        
        # Fix common XML entity issues
        sed -i 's/&\([^a-zA-Z0-9#]\)/\&amp;\1/g' "$XML_FILE"
        sed -i 's/&nbsp\([^;]\)/\&nbsp;\1/g' "$XML_FILE"
        sed -i 's/&copy\([^;]\)/\&copy;\1/g' "$XML_FILE"
        sed -i 's/&amp\([^;]\)/\&amp;\1/g' "$XML_FILE"
        
        echo "✅ Common XML fixes applied"
        
        # Validate XML syntax
        if command -v xmllint >/dev/null 2>&1; then
            echo "🔍 Validating XML syntax..."
            if xmllint --noout "$XML_FILE" 2>/dev/null; then
                echo "✅ XML syntax is now valid!"
            else
                echo "❌ XML still has syntax errors. Manual fix needed."
                echo "Error details:"
                xmllint --noout "$XML_FILE"
            fi
        else
            echo "⚠️ xmllint not available, cannot validate"
        fi
        
    else
        echo "❌ XML file not found: $XML_FILE"
    fi
else
    echo "❌ s2u_online_appointment module not found"
    echo ""
    echo "🛠️ Alternative solutions:"
    echo "1. The module might be in a git submodule or external repository"
    echo "2. Try removing the module from the addons_path"
    echo "3. Check if the module is required and find a working version"
fi

echo ""
echo "🔄 Next steps:"
echo "1. Restart Odoo container: docker-compose restart odoo"
echo "2. Try module installation again"
echo "3. Check Odoo logs: docker logs osusapps-odoo-1"