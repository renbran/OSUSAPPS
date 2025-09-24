#!/bin/bash

echo "🔧 Git Merge Conflict Fix Verification"
echo "======================================"

# Check if the problematic file exists and is readable
FILE="commission_ax/models/__init__.py"

if [ -f "$FILE" ]; then
    echo "✅ File exists: $FILE"
else
    echo "❌ File not found: $FILE"
    exit 1
fi

# Check for remaining Git merge conflict markers
echo "🔍 Checking for Git merge conflict markers..."

if grep -q "^<<<<<<<\|^=======\|^>>>>>>>" "$FILE"; then
    echo "❌ Git merge conflict markers still present!"
    grep -n "^<<<<<<<\|^=======\|^>>>>>>>" "$FILE"
    exit 1
else
    echo "✅ No Git merge conflict markers found"
fi

# Check for the specific problematic line mentioned in the error
if grep -q ">>>>>>> 8cebde85c1c1855f70466431279857f91191bddc" "$FILE"; then
    echo "❌ Problematic Git hash line still present!"
    exit 1
else
    echo "✅ Problematic Git hash line removed"
fi

# Show the current file structure
echo ""
echo "📄 Current file structure:"
echo "Lines: $(wc -l < $FILE)"
echo "First 5 lines:"
head -5 "$FILE"
echo "..."
echo "Last 5 lines:"
tail -5 "$FILE"

echo ""
echo "🎯 Fix verification completed successfully!"
echo "The syntax error should now be resolved."
echo ""
echo "Next steps to test:"
echo "1. docker-compose up -d"
echo "2. docker-compose logs odoo"
echo "3. Check for successful database initialization"