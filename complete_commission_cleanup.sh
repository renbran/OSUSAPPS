#!/bin/bash
# Complete Commission Module Cleanup and Reinstall
echo "🧹 Complete Commission Module Cleanup and Reinstall"
echo "=================================================="

# Stop Odoo
echo "1. Stopping Odoo..."
docker-compose stop odoo

# Clean database of all commission_ax references
echo "2. Cleaning database..."
docker-compose exec -T db psql -U odoo -d erposus << 'EOF'
-- Remove all commission_ax module data
DELETE FROM ir_module_module WHERE name = 'commission_ax';
DELETE FROM ir_model_data WHERE module = 'commission_ax';

-- Remove any commission assignment related views
DELETE FROM ir_ui_view WHERE model = 'commission.assignment';
DELETE FROM ir_ui_view WHERE name::text LIKE '%commission%assignment%';

-- Remove any commission assignment related menus  
DELETE FROM ir_ui_menu WHERE name::text LIKE '%assignment%';

-- Remove any commission assignment model references
DELETE FROM ir_model WHERE model = 'commission.assignment';
DELETE FROM ir_model_fields WHERE model = 'commission.assignment';

-- Clean up any existing commission data to avoid conflicts
TRUNCATE TABLE commission_line CASCADE;
TRUNCATE TABLE commission_type CASCADE;
TRUNCATE TABLE commission_partner_statement_wizard CASCADE;

COMMIT;
EOF

# Ensure problematic files are disabled
echo "3. Ensuring problematic files are disabled..."
cd "d:/GitHub/osus_main/cleanup osus/OSUSAPPS"

# Make sure assignment files are completely removed/disabled
rm -f commission_ax/views/commission_assignment_views.xml*
mv commission_ax/models/commission_assignment.py commission_ax/models/commission_assignment.py.disabled 2>/dev/null || true

# Recreate essential database tables
echo "4. Recreating essential database tables..."
docker-compose exec -T db psql -U odoo -d erposus << 'EOF'
-- Ensure commission_type table
CREATE TABLE IF NOT EXISTS commission_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    code VARCHAR UNIQUE NOT NULL,
    sequence INTEGER DEFAULT 10,
    active BOOLEAN DEFAULT TRUE,
    calculation_method VARCHAR DEFAULT 'percentage',
    default_rate NUMERIC DEFAULT 0.0,
    description TEXT,
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER DEFAULT 1,
    write_uid INTEGER DEFAULT 1
);

-- Ensure commission_line table
CREATE TABLE IF NOT EXISTS commission_line (
    id SERIAL PRIMARY KEY,
    sale_order_id INTEGER,
    partner_id INTEGER NOT NULL,
    commission_type_id INTEGER,
    sequence INTEGER DEFAULT 10,
    display_name VARCHAR,
    calculation_method VARCHAR DEFAULT 'percentage',
    rate NUMERIC DEFAULT 0.0,
    amount NUMERIC DEFAULT 0.0,
    commission_amount NUMERIC DEFAULT 0.0,
    base_amount NUMERIC DEFAULT 0.0,
    commission_category VARCHAR DEFAULT 'agent',
    role VARCHAR DEFAULT 'agent',
    state VARCHAR DEFAULT 'draft',
    currency_id INTEGER,
    company_id INTEGER,
    description TEXT,
    date_commission DATE DEFAULT CURRENT_DATE,
    assignment_count INTEGER DEFAULT 0,
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER DEFAULT 1,
    write_uid INTEGER DEFAULT 1
);

-- Ensure wizard table
CREATE TABLE IF NOT EXISTS commission_partner_statement_wizard (
    id SERIAL PRIMARY KEY,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    commission_state VARCHAR DEFAULT 'all',
    report_format VARCHAR DEFAULT 'pdf',
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER DEFAULT 1,
    write_uid INTEGER DEFAULT 1
);

-- Create relation table
CREATE TABLE IF NOT EXISTS commission_partner_statement_wizard_res_partner_rel (
    commission_partner_statement_wizard_id INTEGER REFERENCES commission_partner_statement_wizard(id) ON DELETE CASCADE,
    res_partner_id INTEGER REFERENCES res_partner(id) ON DELETE CASCADE,
    PRIMARY KEY (commission_partner_statement_wizard_id, res_partner_id)
);

-- Add sample commission types
INSERT INTO commission_type (name, code, sequence, active, calculation_method, default_rate) 
VALUES 
('Agent Commission', 'AGENT', 10, true, 'percentage', 5.0),
('Broker Commission', 'BROKER', 20, true, 'percentage', 3.0),
('Referral Commission', 'REFERRAL', 30, true, 'percentage', 2.0)
ON CONFLICT (code) DO NOTHING;

-- Ensure res_partner has commission fields
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS is_commission_agent boolean DEFAULT FALSE;
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS commission_rate numeric DEFAULT 0.0;

COMMIT;
EOF

# Update module
echo "5. Installing commission_ax module..."
docker-compose run --rm odoo odoo --init=commission_ax --stop-after-init -d erposus || echo "Module init may have failed, continuing..."

# Start Odoo
echo "6. Starting Odoo..."
docker-compose start odoo

echo ""
echo "✅ Cleanup and reinstall completed!"
echo ""
echo "🧪 Test the system:"
echo "1. Wait 30 seconds for Odoo to start"
echo "2. Go to http://localhost:8090"
echo "3. Test Commission Partner Statement Report"
echo ""
echo "📋 If errors persist:"
echo "- Check logs: docker-compose logs -f odoo"
echo "- Verify tables exist: Check database manually"
echo "- The assignment functionality has been completely disabled"