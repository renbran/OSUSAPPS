#!/bin/bash
# Final RPC Error Resolution Script
echo "🔧 Final RPC Error Resolution for Commission Module"
echo "=================================================="

# Stop Odoo to ensure clean update
echo "1. Stopping Odoo service..."
docker-compose stop odoo

# Create missing database structures
echo "2. Ensuring all database tables exist..."
docker-compose exec -T db psql -U odoo -d erposus << 'EOF'
-- Ensure res_partner has commission fields
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS is_commission_agent boolean DEFAULT FALSE;
ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS commission_rate numeric DEFAULT 0.0;

-- Ensure commission_type table exists
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
    create_uid INTEGER,
    write_uid INTEGER
);

-- Ensure commission_line table exists
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
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER,
    write_uid INTEGER
);

-- Ensure wizard table exists
CREATE TABLE IF NOT EXISTS commission_partner_statement_wizard (
    id SERIAL PRIMARY KEY,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    commission_state VARCHAR DEFAULT 'all',
    report_format VARCHAR DEFAULT 'pdf',
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER,
    write_uid INTEGER
);

-- Ensure Many2many relation table exists
CREATE TABLE IF NOT EXISTS commission_partner_statement_wizard_res_partner_rel (
    commission_partner_statement_wizard_id INTEGER REFERENCES commission_partner_statement_wizard(id) ON DELETE CASCADE,
    res_partner_id INTEGER REFERENCES res_partner(id) ON DELETE CASCADE,
    PRIMARY KEY (commission_partner_statement_wizard_id, res_partner_id)
);

-- Create sample data for testing
INSERT INTO commission_type (name, code, sequence, active, calculation_method, default_rate)
SELECT 'Agent Commission', 'AGENT', 10, true, 'percentage', 5.0
WHERE NOT EXISTS (SELECT 1 FROM commission_type WHERE code = 'AGENT');

INSERT INTO commission_type (name, code, sequence, active, calculation_method, default_rate)
SELECT 'Broker Commission', 'BROKER', 20, true, 'percentage', 3.0
WHERE NOT EXISTS (SELECT 1 FROM commission_type WHERE code = 'BROKER');

-- Update at least one partner to be a commission agent
UPDATE res_partner 
SET is_commission_agent = true, commission_rate = 5.0 
WHERE id = (
    SELECT id FROM res_partner 
    WHERE supplier_rank > 0 OR customer_rank > 0 
    ORDER BY id LIMIT 1
)
AND NOT EXISTS (SELECT 1 FROM res_partner WHERE is_commission_agent = true);

COMMIT;
EOF

# Final module update
echo "3. Updating commission_ax module..."
docker-compose run --rm odoo odoo --update=commission_ax --stop-after-init -d erposus

# Update base modules to ensure compatibility
echo "4. Updating base modules..."
docker-compose run --rm odoo odoo --update=base,web --stop-after-init -d erposus

# Start Odoo
echo "5. Starting Odoo service..."
docker-compose start odoo

echo ""
echo "✅ Final fix completed!"
echo ""
echo "🧪 Test Instructions:"
echo "1. Wait 30 seconds for Odoo to fully start"
echo "2. Navigate to: http://localhost:8090"
echo "3. Login and go to Commission Management"
echo "4. Test Partner Statement Report generation"
echo ""
echo "📊 Verification queries:"
echo "- Commission types: $(docker-compose exec -T db psql -U odoo -d erposus -t -c 'SELECT COUNT(*) FROM commission_type;' | tr -d ' ')"
echo "- Commission partners: $(docker-compose exec -T db psql -U odoo -d erposus -t -c 'SELECT COUNT(*) FROM res_partner WHERE is_commission_agent = true;' | tr -d ' ')"
echo ""
echo "🔍 If issues persist, check logs with: docker-compose logs -f odoo"