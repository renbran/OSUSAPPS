#!/bin/bash
# Fix Missing Product Record - Shell Script
# ==========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_docker() {
    if ! docker ps > /dev/null 2>&1; then
        print_error "Docker is not running or not installed"
        echo "Please start Docker and try again"
        exit 1
    fi
}

show_menu() {
    print_header "Missing Product Record Fix Tool"
    
    echo "Choose an option:"
    echo
    echo "1. Generate Report Only (Safe - Read Only)"
    echo "2. Access Database Shell for Manual Fix"
    echo "3. Run Python Fix Script"
    echo "4. Use Odoo Database Cleanup Module"
    echo "5. Quick SQL Inspection"
    echo "6. Exit"
    echo
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1) generate_report ;;
        2) database_shell ;;
        3) python_fix ;;
        4) odoo_cleanup ;;
        5) sql_inspection ;;
        6) exit 0 ;;
        *) 
            print_error "Invalid choice!"
            exit 1
            ;;
    esac
}

generate_report() {
    print_header "Generating Report..."
    
    if [ -f "fix_missing_product_record.py" ]; then
        python3 fix_missing_product_record.py --fix-mode report
    else
        print_error "fix_missing_product_record.py not found!"
        print_warning "Please ensure the script is in the current directory"
        exit 1
    fi
}

database_shell() {
    print_header "Opening Database Shell"
    
    echo "You can run SQL queries to inspect and fix the issue."
    echo
    echo "Example queries:"
    echo "  -- Check if product exists"
    echo "  SELECT * FROM product_product WHERE id = 11;"
    echo
    echo "  -- Find references in sale order lines"
    echo "  SELECT * FROM sale_order_line WHERE product_id = 11;"
    echo
    echo "Type 'exit' or press Ctrl+D to close the shell"
    echo
    
    docker-compose exec db psql -U odoo -d odoo
}

python_fix() {
    print_header "Python Fix Script Options"
    
    print_warning "This will modify your database!"
    echo
    echo "1. Replace with another product (enter product ID)"
    echo "2. Remove orphaned references"
    echo "3. Cancel"
    echo
    read -p "Enter your choice (1-3): " fix_choice
    
    case $fix_choice in
        1)
            read -p "Enter replacement product ID: " replacement_id
            echo
            echo "Running replacement fix with product ID $replacement_id..."
            python3 fix_missing_product_record.py --fix-mode replace --replacement-id "$replacement_id"
            ;;
        2)
            print_warning "This will DELETE records!"
            echo
            read -p "Are you sure? Type 'YES' to confirm: " confirm
            if [ "$confirm" = "YES" ]; then
                python3 fix_missing_product_record.py --fix-mode remove
            else
                echo "Cancelled."
            fi
            ;;
        3)
            exit 0
            ;;
        *)
            print_error "Invalid choice!"
            exit 1
            ;;
    esac
}

odoo_cleanup() {
    print_header "Odoo Database Cleanup Module"
    
    echo "To use the Database Cleanup module:"
    echo
    echo "1. Open Odoo in your browser: http://localhost:8069"
    echo "2. Enable Developer Mode:"
    echo "   - Click your profile icon (top right)"
    echo "   - Click 'Developer Mode' at the bottom"
    echo "3. Go to: Settings > Technical > Database Structure > Database Cleanup"
    echo "4. Choose the cleanup option:"
    echo "   - 'Purge Data' to remove orphaned data references"
    echo "   - 'Purge Models' to clean up missing models"
    echo "5. Click 'Purge All' or select specific items"
    echo
    
    if command -v xdg-open > /dev/null; then
        read -p "Press Enter to open Odoo in your browser..."
        xdg-open http://localhost:8069
    elif command -v open > /dev/null; then
        read -p "Press Enter to open Odoo in your browser..."
        open http://localhost:8069
    else
        print_warning "Please open http://localhost:8069 in your browser"
    fi
}

sql_inspection() {
    print_header "Quick SQL Inspection"
    
    echo "Running SQL queries to check for product.product(11) references..."
    echo
    
    # Execute SQL queries
    docker-compose exec -T db psql -U odoo -d odoo <<'EOF'
-- Check if product exists
\echo '=== Product Status ==='
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM product_product WHERE id = 11) 
        THEN 'Product 11 EXISTS'
        ELSE 'Product 11 DOES NOT EXIST'
    END as status;

-- Find references in various tables
\echo ''
\echo '=== References in sale_order_line ==='
SELECT COUNT(*) as count FROM sale_order_line WHERE product_id = 11;

\echo ''
\echo '=== References in purchase_order_line ==='
SELECT COUNT(*) as count FROM purchase_order_line WHERE product_id = 11;

\echo ''
\echo '=== References in account_move_line ==='
SELECT COUNT(*) as count FROM account_move_line WHERE product_id = 11;

\echo ''
\echo '=== References in stock_move ==='
SELECT COUNT(*) as count FROM stock_move WHERE product_id = 11;

\echo ''
\echo '=== All available products (first 10) ==='
SELECT id, name, default_code 
FROM product_product 
WHERE active = true 
ORDER BY id 
LIMIT 10;
EOF
    
    print_success "Inspection complete!"
    echo
    echo "If you see references above, you need to fix them."
    echo "Run this script again and choose option 3 for fixes."
}

# Main execution
check_docker
show_menu
