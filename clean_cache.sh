#!/bin/bash
# Auto Clean Cache Files - Odoo Project
# Run this script to automatically clean all Python cache files

echo "🧹 Cleaning Python cache files..."
echo "================================================"

# Find and remove __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✅ __pycache__ directories removed"

# Remove .pyc files
echo "Removing .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ .pyc files removed"

# Remove .pyo files
echo "Removing .pyo files..."
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "✅ .pyo files removed"

# Remove backup files
echo "Removing backup files..."
find . -type f -name "*~" -delete 2>/dev/null
find . -type f -name "*.bak" -delete 2>/dev/null
find . -type f -name "*.backup" -delete 2>/dev/null
echo "✅ Backup files removed"

# Verify
echo ""
echo "================================================"
echo "🔍 Verification:"
CACHE_COUNT=$(find . -name "*.pyc" -o -name "*.pyo" -o -name "__pycache__" 2>/dev/null | wc -l)
echo "Remaining cache files: $CACHE_COUNT (should be 0)"

if [ $CACHE_COUNT -eq 0 ]; then
    echo "✅ SUCCESS! All cache files removed."
else
    echo "⚠️  Some cache files still exist. Check permissions."
fi

echo "================================================"
echo "Done! Cache cleanup complete."
