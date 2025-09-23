#!/bin/bash

# Custom Calendar Invitations Module Test Script
echo "🧪 Testing Custom Calendar Invitations Module Installation"
echo "=" × 60

# Check module structure
echo "📁 Checking module structure..."
MODULE_PATH="custom_calendar_invitations"

if [ -d "$MODULE_PATH" ]; then
    echo "✅ Module directory exists"
else
    echo "❌ Module directory not found"
    exit 1
fi

# Check required files
FILES=(
    "__manifest__.py"
    "__init__.py"
    "models/__init__.py"
    "models/calendar_event.py"
    "data/calendar_templates.xml"
    "security/ir.model.access.csv"
    "README.md"
)

echo "📋 Checking required files..."
for file in "${FILES[@]}"; do
    if [ -f "$MODULE_PATH/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

# Check manifest syntax
echo "🔍 Validating manifest syntax..."
if python3 -c "exec(open('$MODULE_PATH/__manifest__.py').read())" 2>/dev/null; then
    echo "✅ Manifest syntax valid"
else
    echo "❌ Manifest syntax error"
fi

# Check XML syntax  
echo "🔍 Validating XML syntax..."
if command -v xmllint >/dev/null 2>&1; then
    if xmllint --noout "$MODULE_PATH/data/calendar_templates.xml" 2>/dev/null; then
        echo "✅ XML syntax valid"
    else
        echo "❌ XML syntax error"
    fi
else
    echo "⚠️  xmllint not available, skipping XML validation"
fi

# Test Odoo installation (if docker is available)
echo "🐳 Testing Odoo installation..."
if command -v docker-compose >/dev/null 2>&1; then
    if docker-compose ps odoo >/dev/null 2>&1; then
        echo "🚀 Testing module installation..."
        docker-compose exec -T odoo odoo -i custom_calendar_invitations --test-enable --stop-after-init -d odoo --log-level=info
    else
        echo "⚠️  Odoo container not running"
    fi
else
    echo "⚠️  Docker not available"
fi

echo "🎯 Test completed!"