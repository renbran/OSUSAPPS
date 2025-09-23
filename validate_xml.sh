#!/bin/bash

echo "Validating XML syntax for quantity_percentage module..."

# Check account_move_views.xml
echo "Checking account_move_views.xml..."
if xmllint --noout quantity_percentage/views/account_move_views.xml 2>/dev/null; then
    echo "✓ account_move_views.xml is valid"
else
    echo "✗ account_move_views.xml has syntax errors"
    xmllint quantity_percentage/views/account_move_views.xml 2>&1
fi

# Check sale_order_views.xml  
echo "Checking sale_order_views.xml..."
if xmllint --noout quantity_percentage/views/sale_order_views.xml 2>/dev/null; then
    echo "✓ sale_order_views.xml is valid"
else
    echo "✗ sale_order_views.xml has syntax errors"
    xmllint quantity_percentage/views/sale_order_views.xml 2>&1
fi

echo "XML validation complete."