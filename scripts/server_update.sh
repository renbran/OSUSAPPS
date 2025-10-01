#!/bin/bash

# Quick Server Update Script for Commission Period Field Fix
# Run this on the server to apply the commission_period field name corrections

set -e

echo "🚀 Starting server update for Commission Period field fix..."

# Configuration
SERVER_PATH="/var/odoo/scholarixv17/extra-addons"
BACKUP_DIR="/tmp/odoo_backup_$(date +%Y%m%d_%H%M%S)"
TARGET_FILE="commission_app/views/commission_period_views.xml"

# Function to find the correct odoo directory
find_odoo_dir() {
    local found_dir
    for dir in "$SERVER_PATH"/osusapps* "$SERVER_PATH"/OSUSAPPS*; do
        if [ -d "$dir" ] && [ -f "$dir/$TARGET_FILE" ]; then
            echo "$dir"
            return 0
        fi
    done
    echo ""
    return 1
}

# Find the correct directory
ODOO_DIR=$(find_odoo_dir)
if [ -z "$ODOO_DIR" ]; then
    echo "❌ Error: Could not find OSUSAPPS directory with $TARGET_FILE"
    echo "Searched in: $SERVER_PATH"
    exit 1
fi

echo "📁 Found Odoo directory: $ODOO_DIR"
TARGET_PATH="$ODOO_DIR/$TARGET_FILE"

# Check if file exists
if [ ! -f "$TARGET_PATH" ]; then
    echo "❌ Error: $TARGET_PATH not found"
    exit 1
fi

# Create backup
echo "💾 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp "$TARGET_PATH" "$BACKUP_DIR/"
echo "✅ Backup created at: $BACKUP_DIR/$(basename $TARGET_FILE)"

# Check current status
echo "🔍 Checking current field names..."
date_from_count=$(grep -o "date_from" "$TARGET_PATH" | wc -l || true)
date_to_count=$(grep -o "date_to" "$TARGET_PATH" | wc -l || true)

echo "Current status:"
echo "  - date_from occurrences: $date_from_count"
echo "  - date_to occurrences: $date_to_count"

if [ "$date_from_count" -eq 0 ] && [ "$date_to_count" -eq 0 ]; then
    echo "✅ File is already correct! No changes needed."
    exit 0
fi

# Apply fixes
echo "🔧 Applying field name corrections..."
sed -i.bak 's/date_from/date_start/g' "$TARGET_PATH"
sed -i 's/date_to/date_end/g' "$TARGET_PATH"

# Verify fixes
echo "✅ Verifying corrections..."
date_start_count=$(grep -o "date_start" "$TARGET_PATH" | wc -l || true)
date_end_count=$(grep -o "date_end" "$TARGET_PATH" | wc -l || true)
remaining_from=$(grep -o "date_from" "$TARGET_PATH" | wc -l || true)
remaining_to=$(grep -o "date_to" "$TARGET_PATH" | wc -l || true)

echo "After fix:"
echo "  - date_start occurrences: $date_start_count"
echo "  - date_end occurrences: $date_end_count"
echo "  - remaining date_from: $remaining_from"
echo "  - remaining date_to: $remaining_to"

if [ "$remaining_from" -eq 0 ] && [ "$remaining_to" -eq 0 ]; then
    echo "✅ SUCCESS: All field names corrected!"
else
    echo "⚠️  WARNING: Some old field names may remain"
fi

# Restart instructions
echo ""
echo "🔄 NEXT STEPS:"
echo "1. Restart Odoo server:"
echo "   docker-compose restart odoo"
echo "   # or"
echo "   systemctl restart odoo"
echo ""
echo "2. Update the module in Odoo UI (if already installed)"
echo "3. Test commission_app module installation"
echo ""
echo "📋 Backup location: $BACKUP_DIR"
echo "✅ Server update complete!"