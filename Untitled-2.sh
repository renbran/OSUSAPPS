#!/bin/bash
# Odoo 17 Database Migration Script: ERPOSUS to OSUSPROPERTIES
# With Complete Chart of Accounts Mapping
# Date: 2025-09-07
# Corrected with --no-http for all shell connections

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration Variables
SOURCE_DB="erposus"
TARGET_DB="osusproperties"
BACKUP_DIR="/var/odoo/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MIGRATION_LOG="/var/odoo/migration_${TIMESTAMP}.log"

# Create backup directory if it doesn't exist
sudo mkdir -p ${BACKUP_DIR}
sudo chown odoo:odoo ${BACKUP_DIR}

# Function to log messages
log_message() {
    echo -e "${2}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a ${MIGRATION_LOG}
}

# Step 1: Pre-Migration Checks
log_message "Starting Migration Process from ERPOSUS to OSUSPROPERTIES" "${GREEN}"

# Check PostgreSQL service
log_message "Checking PostgreSQL service..." "${YELLOW}"
sudo systemctl status postgresql --no-pager | head -5

# Step 2: Stop Odoo Services
log_message "Stopping Odoo services..." "${YELLOW}"
sudo systemctl stop odoo-erposus 2>/dev/null || true
sudo systemctl stop odoo-osusproperties 2>/dev/null || true

# Step 3: Create Backups
log_message "Creating backup of source database (erposus)..." "${YELLOW}"
sudo -u postgres pg_dump -Fc -f ${BACKUP_DIR}/erposus_${TIMESTAMP}.dump ${SOURCE_DB}

log_message "Creating backup of target database (osusproperties) if exists..." "${YELLOW}"
sudo -u postgres pg_dump -Fc -f ${BACKUP_DIR}/osusproperties_backup_${TIMESTAMP}.dump ${TARGET_DB} 2>/dev/null || true

# Step 4: Drop and Recreate Target Database
log_message "Preparing target database..." "${YELLOW}"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${TARGET_DB};"
sudo -u postgres psql -c "CREATE DATABASE ${TARGET_DB} WITH OWNER odoo ENCODING 'UTF8';"

# Step 5: Restore Source to Target
log_message "Restoring erposus data to osusproperties database..." "${YELLOW}"
sudo -u postgres pg_restore -d ${TARGET_DB} ${BACKUP_DIR}/erposus_${TIMESTAMP}.dump

# Step 6: Execute Account Mapping Migration Script
log_message "Executing Chart of Accounts migration mapping..." "${GREEN}"

sudo -u postgres psql -d ${TARGET_DB} << 'EOF'
-- Chart of Accounts Migration Script
-- ERPOSUS to OSUSPROPERTIES Account Mapping

BEGIN;

-- Create migration log table
CREATE TABLE IF NOT EXISTS account_migration_log (
    id SERIAL PRIMARY KEY,
    old_code VARCHAR(50),
    old_name VARCHAR(200),
    new_code VARCHAR(50),
    new_name VARCHAR(200),
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount NUMERIC(15,2)
);

-- Backup existing account.account table
CREATE TABLE account_account_backup_migration AS SELECT * FROM account_account;

-- Update Revenue Accounts
UPDATE account_account SET 
    code = '40100',
    name = 'Revenue - Primary Sales'
WHERE code IN ('1006', '1005');

UPDATE account_account SET 
    code = '40300',
    name = 'Revenue - Exclusive Sales'
WHERE code IN ('1001', '1002', '1003', '1004');

UPDATE account_account SET 
    code = '40200',
    name = 'Revenue - Secondary Sales'
WHERE code = '1007';

-- Update Cost of Sales Accounts
UPDATE account_account SET 
    code = '50100',
    name = 'Cost of Sales - Primary'
WHERE code IN ('2006', '2005');

UPDATE account_account SET 
    code = '50200',
    name = 'Cost of Sales - Secondary'
WHERE code = '2007';

UPDATE account_account SET 
    code = '50310',
    name = 'Cost of Sales - Exclusive External'
WHERE code IN ('2001', '2002');

UPDATE account_account SET 
    code = '50320',
    name = 'Cost of Sales - Exclusive Internal'
WHERE code IN ('2003', '2004');

-- Update Commission Accounts
UPDATE account_account SET 
    code = '51000',
    name = 'Internal Commission - RM/SM/CXO'
WHERE code = '2008';

UPDATE account_account SET 
    code = '51100',
    name = 'External Commission - Kickbacks'
WHERE code = '2009';

UPDATE account_account SET 
    code = '51200',
    name = 'Sales Discounts'
WHERE code = '2010';

-- Update Asset Accounts
UPDATE account_account SET 
    code = '10100',
    name = 'ADCB Bank Account'
WHERE code = '4003';

UPDATE account_account SET 
    code = '10200',
    name = 'ENBD Bank Account'
WHERE code IN ('4004', '4005');

UPDATE account_account SET 
    code = '10300',
    name = 'Alaan Prepaid Card'
WHERE code IN ('4006', '4007');

UPDATE account_account SET 
    code = '11000',
    name = 'Accounts Receivable'
WHERE code = '4020';

UPDATE account_account SET 
    code = '12000',
    name = 'LMD Receivables'
WHERE code = '4041';

UPDATE account_account SET 
    code = '13000',
    name = 'Loans and Advances'
WHERE code IN ('4040', '4043', '4044');

-- Update Prepaid Expenses
UPDATE account_account SET 
    code = '14000',
    name = 'Prepaid Expenses'
WHERE code IN ('4021', '4022', '4023', '4024', '4026', '4027', '4029');

UPDATE account_account SET 
    code = '140005',
    name = 'Prepaid Parking Expenses'
WHERE code = '4025';

UPDATE account_account SET 
    code = '140008',
    name = 'Prepaid Visa Expenses'
WHERE code = '4028';

-- Update Fixed Assets
UPDATE account_account SET 
    code = '15000',
    name = 'Work in Progress - Fixed Assets'
WHERE code IN ('4504', '4506');

UPDATE account_account SET 
    code = '16000',
    name = 'Office Equipment'
WHERE code = '4509';

UPDATE account_account SET 
    code = '17000',
    name = 'Leasehold Improvements'
WHERE code = '4511';

-- Update Liability Accounts
UPDATE account_account SET 
    code = '21000',
    name = 'Accounts Payable'
WHERE code = '5001';

UPDATE account_account SET 
    code = '22000',
    name = 'Accrued Salaries & Benefits'
WHERE code = '5004';

UPDATE account_account SET 
    code = '23000',
    name = 'LMD Control Account'
WHERE code = '5101';

UPDATE account_account SET 
    code = '24000',
    name = 'Due to Related Parties'
WHERE code IN ('5100', '5102');

UPDATE account_account SET 
    code = '25000',
    name = 'Tax Payable'
WHERE code IN ('251000', '5006');

UPDATE account_account SET 
    code = '26000',
    name = 'Agent Commission Provision'
WHERE code IN ('5007', '5010');

UPDATE account_account SET 
    code = '27000',
    name = 'Accrued Expenses'
WHERE code IN ('5002', '5003', '5005');

UPDATE account_account SET 
    code = '28000',
    name = 'Provision for Gratuity'
WHERE code = '5500';

-- Update Equity Accounts
UPDATE account_account SET 
    code = '30100',
    name = 'Share Capital - Partners'
WHERE code IN ('6001', '6002');

UPDATE account_account SET 
    code = '320001',
    name = 'Mr. Hamad - Current Account'
WHERE code = '6003';

-- Update Operating Expense Accounts
UPDATE account_account SET 
    code = '400003',
    name = 'Basic Salary'
WHERE code = '3021';

UPDATE account_account SET 
    code = '400008',
    name = 'End Of Service Indemnity'
WHERE code = '3024';

UPDATE account_account SET 
    code = '400009',
    name = 'Medical Insurance'
WHERE code = '3025';

UPDATE account_account SET 
    code = '400012',
    name = 'Staff Other Allowances'
WHERE code IN ('3026', '3027');

UPDATE account_account SET 
    code = '400014',
    name = 'Visa Expenses'
WHERE code = '3014';

UPDATE account_account SET 
    code = '400016',
    name = 'Office Rent'
WHERE code = '3019';

UPDATE account_account SET 
    code = '400018',
    name = 'Water & Electricity'
WHERE code = '3030';

UPDATE account_account SET 
    code = '400020',
    name = 'Telephone'
WHERE code = '3020';

UPDATE account_account SET 
    code = '400026',
    name = 'Meals'
WHERE code = '3002';

UPDATE account_account SET 
    code = '400032',
    name = 'Trade License Fees'
WHERE code = '3004';

UPDATE account_account SET 
    code = '400034',
    name = 'Other - Advertising Expenses'
WHERE code = '3005';

UPDATE account_account SET 
    code = '400041',
    name = 'Training'
WHERE code = '3028';

UPDATE account_account SET 
    code = '400042',
    name = 'Maintenance'
WHERE code = '3031';

UPDATE account_account SET 
    code = '400050',
    name = 'Others - Office Various Expenses'
WHERE code IN ('3013', '3016', '3017', '3018', '3029');

UPDATE account_account SET 
    code = '400051',
    name = 'Other Bank Charges'
WHERE code = '3015';

UPDATE account_account SET 
    code = '400057',
    name = 'Other Non Operating Expenses'
WHERE code = '3003';

UPDATE account_account SET 
    code = '400067',
    name = 'Consultancy Fees'
WHERE code = '3023';

-- Update account move lines with new account codes
UPDATE account_move_line aml
SET account_id = aa_new.id
FROM account_account aa_old, account_account aa_new
WHERE aml.account_id = aa_old.id
AND aa_old.code IN ('1006', '1005')
AND aa_new.code = '40100';

-- Log the migration
INSERT INTO account_migration_log (old_code, old_name, new_code, new_name)
SELECT 
    aab.code as old_code,
    aab.name as old_name,
    aa.code as new_code,
    aa.name as new_name
FROM account_account aa
JOIN account_account_backup_migration aab ON aa.id = aab.id
WHERE aa.code != aab.code;

COMMIT;

-- Verify migration
SELECT 
    'Migration Summary' as report,
    COUNT(DISTINCT id) as accounts_migrated,
    COUNT(DISTINCT code) as unique_codes
FROM account_migration_log;
EOF

# Step 7: Update Filestore
log_message "Updating filestore..." "${YELLOW}"
if [ -d "/var/odoo/erposus/.local/share/Odoo/filestore/${SOURCE_DB}" ]; then
    sudo rm -rf /var/odoo/osusproperties/.local/share/Odoo/filestore/${TARGET_DB}
    sudo cp -r /var/odoo/erposus/.local/share/Odoo/filestore/${SOURCE_DB} \
              /var/odoo/osusproperties/.local/share/Odoo/filestore/${TARGET_DB}
    sudo chown -R odoo:odoo /var/odoo/osusproperties/.local/share/Odoo/filestore/${TARGET_DB}
fi

# Step 8: Update Odoo Configuration
log_message "Updating Odoo configuration..." "${YELLOW}"
sudo sed -i "s/db_name = ${SOURCE_DB}/db_name = ${TARGET_DB}/g" /var/odoo/osusproperties/odoo.conf

# Step 9: Update All Modules in Target Instance
log_message "Updating all modules in target instance..." "${GREEN}"
cd /var/odoo/osusproperties && \
sudo -u odoo timeout 600 venv/bin/python3 src/odoo-bin \
    -c odoo.conf \
    -d ${TARGET_DB} \
    --no-http \
    --stop-after-init \
    --update all \
    --logfile ${MIGRATION_LOG} 2>&1

# Step 10: Rebuild Assets (CORRECTED WITH --no-http)
log_message "Rebuilding assets..." "${YELLOW}"
cd /var/odoo/osusproperties && \
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d ${TARGET_DB} --no-http << 'PYTHON_EOF'
env['ir.asset'].search([]).unlink()
env.cr.commit()
PYTHON_EOF

# Step 11: Clear Cache
log_message "Clearing cache..." "${YELLOW}"
sudo -u postgres psql -d ${TARGET_DB} -c "DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view' AND res_field = 'arch_db';"

# Step 12: Verify Migration
log_message "Verifying migration..." "${GREEN}"
sudo -u postgres psql -d ${TARGET_DB} -c "
SELECT 
    'Account Migration Summary' as report,
    COUNT(*) as total_accounts,
    COUNT(DISTINCT code) as unique_codes,
    MIN(code) as first_code,
    MAX(code) as last_code
FROM account_account
WHERE active = true;"

# Step 13: Start Services (CORRECTED)
log_message "Starting Odoo services..." "${GREEN}"
sudo systemctl start odoo-osusproperties 2>/dev/null || \
    (cd /var/odoo/osusproperties && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http &)

# Step 14: Final Report
log_message "Migration completed successfully!" "${GREEN}"
log_message "Backup files created:" "${YELLOW}"
log_message "  - Source: ${BACKUP_DIR}/erposus_${TIMESTAMP}.dump" "${NC}"
log_message "  - Target: ${BACKUP_DIR}/osusproperties_backup_${TIMESTAMP}.dump" "${NC}"
log_message "Migration log: ${MIGRATION_LOG}" "${YELLOW}"
log_message "Please verify the migration at: http://your-server:8069" "${GREEN}"

# Display migration statistics
sudo -u postgres psql -d ${TARGET_DB} -c "
SELECT 
    'Migration Statistics' as report,
    (SELECT COUNT(*) FROM account_account WHERE code LIKE '4%') as revenue_accounts,
    (SELECT COUNT(*) FROM account_account WHERE code LIKE '5%') as cost_accounts,
    (SELECT COUNT(*) FROM account_move) as total_journal_entries,
    (SELECT COUNT(*) FROM account_move_line) as total_journal_items;"