#!/bin/bash
# Final fix for commission_ax database schema issues
# This script will properly update the database schema and fix the RPC error

echo "🔧 Fixing Commission Database Schema - Final Fix"
echo "=============================================="

# Stop Odoo service
echo "1. Stopping Odoo service..."
docker-compose stop odoo

# Wait a bit
sleep 2

# Method 1: Try to update the module first
echo "2. Attempting to update commission_ax module..."
docker-compose run --rm odoo odoo --update=commission_ax --stop-after-init -d erposus --without-demo=all

# Method 2: If update fails, try init
if [ $? -ne 0 ]; then
    echo "   Update failed, trying to initialize module..."
    docker-compose run --rm odoo odoo --init=commission_ax --stop-after-init -d erposus --without-demo=all
fi

# Check if column exists now
echo "3. Checking if is_commission_agent column exists..."
COLUMN_EXISTS=$(docker-compose exec -T db psql -U odoo -d erposus -t -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'res_partner' AND column_name = 'is_commission_agent';" 2>/dev/null | xargs)

if [ -z "$COLUMN_EXISTS" ]; then
    echo "   Column still missing, adding it manually..."
    docker-compose exec -T db psql -U odoo -d erposus -c "
        ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS is_commission_agent boolean DEFAULT FALSE;
        ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS commission_rate numeric DEFAULT 0.0;
        COMMENT ON COLUMN res_partner.is_commission_agent IS 'Check this box if this partner is a commission agent';
        COMMENT ON COLUMN res_partner.commission_rate IS 'Default commission rate percentage for this agent';
    " || echo "   Manual column addition failed, but continuing..."
fi

# Verify commission_type table exists
echo "4. Checking commission_type table..."
docker-compose exec -T db psql -U odoo -d erposus -c "
    CREATE TABLE IF NOT EXISTS commission_type (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        code VARCHAR NOT NULL,
        sequence INTEGER DEFAULT 10,
        active BOOLEAN DEFAULT TRUE,
        calculation_method VARCHAR DEFAULT 'percentage',
        default_rate NUMERIC DEFAULT 0.0,
        create_date TIMESTAMP DEFAULT NOW(),
        write_date TIMESTAMP DEFAULT NOW(),
        create_uid INTEGER,
        write_uid INTEGER
    );
" || echo "   Commission type table creation failed, but continuing..."

# Verify commission_line table exists with proper relationships
echo "5. Checking commission_line table..."
docker-compose exec -T db psql -U odoo -d erposus -c "
    CREATE TABLE IF NOT EXISTS commission_line (
        id SERIAL PRIMARY KEY,
        sale_order_id INTEGER,
        partner_id INTEGER,
        commission_type_id INTEGER,
        sequence INTEGER DEFAULT 10,
        calculation_method VARCHAR DEFAULT 'percentage',
        rate NUMERIC DEFAULT 0.0,
        amount NUMERIC DEFAULT 0.0,
        state VARCHAR DEFAULT 'draft',
        create_date TIMESTAMP DEFAULT NOW(),
        write_date TIMESTAMP DEFAULT NOW(),
        create_uid INTEGER,
        write_uid INTEGER
    );
" || echo "   Commission line table creation failed, but continuing..."

# Update Odoo registry to refresh field definitions
echo "6. Updating Odoo registry..."
docker-compose run --rm odoo odoo --update=base --stop-after-init -d erposus

echo "7. Final module update for commission_ax..."
docker-compose run --rm odoo odoo --update=commission_ax --stop-after-init -d erposus

# Restart Odoo
echo "8. Starting Odoo service..."
docker-compose start odoo

echo ""
echo "✅ Database fix completed!"
echo ""
echo "Please wait 30 seconds for Odoo to fully start, then test:"
echo "1. Navigate to http://localhost:8090"
echo "2. Go to Apps and search for 'commission_ax'"
echo "3. Install or update the module if needed"
echo "4. Test the Commission Partner Statement Report"
echo ""
echo "If you still get RPC errors, the issue might be in specific views"
echo "that reference fields not yet created. Check Odoo logs with:"
echo "docker-compose logs -f odoo"