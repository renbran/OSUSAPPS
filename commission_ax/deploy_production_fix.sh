#!/bin/bash
# Production Deployment Script for Commission AX Fix
# This script addresses the commission_processed field issue

echo "=== Commission AX Production Deployment Fix ==="
echo "Date: $(date)"
echo "Fixing: Field commission_processed referenced in related field definition"
echo ""

# Variables (update these for your environment)
ODOO_USER="odoo"
ODOO_DB="osusbackup"
ADDONS_PATH="/var/odoo/osusbackup/custom-addons"
ODOO_BIN="/var/odoo/osusbackup/src/odoo/odoo-bin"
LOG_FILE="/var/log/odoo/deployment_$(date +%Y%m%d_%H%M%S).log"

echo "1. Creating backup..."
sudo -u postgres pg_dump $ODOO_DB > "/backup/${ODOO_DB}_backup_$(date +%Y%m%d_%H%M%S).sql"
if [ $? -eq 0 ]; then
    echo "✓ Database backup created successfully"
else
    echo "✗ Database backup failed"
    exit 1
fi

echo ""
echo "2. Stopping Odoo service..."
sudo systemctl stop odoo
echo "✓ Odoo service stopped"

echo ""
echo "3. Cleaning Python cache files..."
find "$ADDONS_PATH/commission_ax" -name "*.pyc" -delete
find "$ADDONS_PATH/commission_ax" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✓ Python cache cleaned"

echo ""
echo "4. Setting correct permissions..."
chown -R $ODOO_USER:$ODOO_USER "$ADDONS_PATH/commission_ax"
chmod -R 755 "$ADDONS_PATH/commission_ax"
echo "✓ Permissions set"

echo ""
echo "5. Testing module syntax..."
sudo -u $ODOO_USER python3 -c "
import sys
sys.path.insert(0, '$ADDONS_PATH')
try:
    # Test basic imports
    from commission_ax.models import commission_line
    print('✓ commission_line import successful')
    from commission_ax.models import sale_order
    print('✓ sale_order import successful')
    print('✓ Module syntax check passed')
except Exception as e:
    print(f'✗ Module syntax error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "✗ Module syntax check failed"
    exit 1
fi

echo ""
echo "6. Installing/updating module..."
sudo -u $ODOO_USER $ODOO_BIN -d $ODOO_DB -u commission_ax --no-http --stop-after-init --logfile=$LOG_FILE

if [ $? -eq 0 ]; then
    echo "✓ Module updated successfully"
else
    echo "✗ Module update failed. Check log: $LOG_FILE"
    echo "Recent log entries:"
    tail -20 $LOG_FILE
    exit 1
fi

echo ""
echo "7. Verifying installation..."
sudo -u $ODOO_USER python3 -c "
import odoo
from odoo import registry
from odoo.api import Environment

try:
    with registry('$ODOO_DB').cursor() as cr:
        env = Environment(cr, 1, {})
        # Check if commission_ax module is installed
        module = env['ir.module.module'].search([('name', '=', 'commission_ax')])
        if module and module.state == 'installed':
            print('✓ commission_ax module is installed')
            
            # Check if commission.line model exists
            if 'commission.line' in env.registry:
                print('✓ commission.line model exists')
                
                # Test creating a commission line (dry run)
                commission_line = env['commission.line']
                print('✓ commission.line model is accessible')
            else:
                print('✗ commission.line model not found')
                exit(1)
        else:
            print('✗ commission_ax module not installed')
            exit(1)
except Exception as e:
    print(f'✗ Verification failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "✗ Module verification failed"
    exit 1
fi

echo ""
echo "8. Starting Odoo service..."
sudo systemctl start odoo
sleep 5

# Wait for Odoo to start
echo "Waiting for Odoo to start..."
for i in {1..30}; do
    if systemctl is-active --quiet odoo; then
        echo "✓ Odoo service started successfully"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        echo "✗ Odoo service failed to start within 60 seconds"
        exit 1
    fi
done

echo ""
echo "9. Final verification..."
sleep 10
if systemctl is-active --quiet odoo; then
    echo "✓ Odoo is running"
    echo "✓ Check logs: tail -f /var/log/odoo/odoo-server.log"
else
    echo "✗ Odoo is not running"
    exit 1
fi

echo ""
echo "=== Deployment Summary ==="
echo "✓ Database backup created"
echo "✓ Python cache cleaned" 
echo "✓ Module syntax verified"
echo "✓ commission_ax module updated"
echo "✓ Installation verified"
echo "✓ Odoo service restarted"
echo ""
echo "🎉 Commission AX deployment completed successfully!"
echo "Log file: $LOG_FILE"
echo ""
echo "Next steps:"
echo "1. Monitor logs: tail -f /var/log/odoo/odoo-server.log"
echo "2. Test commission functionality in the web interface"
echo "3. Verify no 'commission_processed' related field errors"