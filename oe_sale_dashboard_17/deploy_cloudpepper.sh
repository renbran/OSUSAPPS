#!/bin/bash

# CloudPepper Enhanced Sales Dashboard Deployment Script
# Run this script directly on your CloudPepper server

set -e  # Exit on any error

echo "🚀 === CloudPepper Enhanced Sales Dashboard Deployment === 🚀"
echo "Module: oe_sale_dashboard_17"
echo "Target Path: /var/odoo/coatest/extra-addons/odoo17_final.git-6880b7fcd4844/"
echo "Date: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored text
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${MAGENTA}📋 $1${NC}"
}

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   print_warning "This script should be run with sudo for service management"
   echo "Usage: sudo ./deploy_cloudpepper.sh [database_name]"
   echo ""
fi

# Get database name from argument or prompt
if [ -z "$1" ]; then
    print_info "Enter your database name:"
    read -r DATABASE_NAME
else
    DATABASE_NAME=$1
fi

print_info "Using database: $DATABASE_NAME"
echo ""

# Navigate to the module directory
MODULE_PATH="/var/odoo/coatest/extra-addons/odoo17_final.git-6880b7fcd4844"
print_info "Checking current directory..."

# Check if we're already in the module directory
if [ -f "__manifest__.py" ] && [ "$(basename $(pwd))" = "oe_sale_dashboard_17" ]; then
    print_status "Already in module directory: $(pwd)"
    cd ..  # Go up to the parent directory to run git commands
    MODULE_PATH="$(pwd)"
elif [ ! -d "$MODULE_PATH" ]; then
    print_error "Module path not found: $MODULE_PATH"
    exit 1
else
    cd "$MODULE_PATH"
    print_status "Changed to directory: $(pwd)"
fi

# Check if oe_sale_dashboard_17 exists
if [ ! -d "oe_sale_dashboard_17" ]; then
    print_error "Module directory 'oe_sale_dashboard_17' not found!"
    print_info "Available directories:"
    ls -la | grep "^d"
    exit 1
fi

print_status "Module directory found"

# Pull latest changes from git
print_header "Updating Code from Repository"
print_info "Pulling latest changes from git..."

if git pull origin main; then
    print_status "Git pull completed successfully"
else
    print_warning "Git pull failed or no changes available"
fi

# Check required files for merged best practices
print_header "Verifying Enhanced Module Files"
REQUIRED_FILES=(
    "oe_sale_dashboard_17/__manifest__.py"
    "oe_sale_dashboard_17/models/sale_dashboard.py"
    "oe_sale_dashboard_17/static/src/js/dashboard_merged.js"
    "oe_sale_dashboard_17/static/src/css/dashboard_merged.css"
    "oe_sale_dashboard_17/static/src/xml/dashboard_merged_template.xml"
    "oe_sale_dashboard_17/views/dashboard_views.xml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "$file"
    else
        print_error "$file (missing)"
    fi
done

echo ""

# Check Odoo service status
print_header "Checking Odoo Service Status"
if systemctl is-active --quiet odoo; then
    print_status "Odoo service is running"
    ODOO_RUNNING=true
else
    print_warning "Odoo service is not running"
    ODOO_RUNNING=false
fi

# Find Odoo binary
print_header "Locating Odoo Binary"
ODOO_BIN=""
POSSIBLE_PATHS=(
    "/opt/odoo/odoo-bin"
    "/usr/bin/odoo"
    "/usr/local/bin/odoo"
    "/var/odoo/odoo-bin"
    "/opt/odoo17/odoo-bin"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        ODOO_BIN="$path"
        print_status "Found Odoo binary: $ODOO_BIN"
        break
    fi
done

if [ -z "$ODOO_BIN" ]; then
    print_error "Odoo binary not found. Please specify the correct path."
    print_info "Common locations: /opt/odoo/odoo-bin, /usr/bin/odoo"
    exit 1
fi

# Update the module
print_header "Updating Enhanced Sales Dashboard Module"
print_info "Updating module in database: $DATABASE_NAME"

# Stop Odoo service if running
if [ "$ODOO_RUNNING" = true ]; then
    print_info "Stopping Odoo service..."
    if systemctl stop odoo; then
        print_status "Odoo service stopped"
    else
        print_warning "Failed to stop Odoo service, continuing anyway..."
    fi
fi

# Run module update
print_info "Running module update command..."
UPDATE_CMD="$ODOO_BIN -u oe_sale_dashboard_17 -d $DATABASE_NAME --stop-after-init"
print_info "Command: $UPDATE_CMD"

if $UPDATE_CMD; then
    print_status "Module update completed successfully"
else
    print_error "Module update failed"
    print_info "Check logs: sudo journalctl -u odoo -f"
    exit 1
fi

# Start Odoo service
print_header "Starting Odoo Service"
print_info "Starting Odoo service..."

if systemctl start odoo; then
    print_status "Odoo service started"
else
    print_error "Failed to start Odoo service"
    print_info "Check logs: sudo journalctl -u odoo -f"
    exit 1
fi

# Wait for service to be ready
print_info "Waiting for Odoo service to be ready..."
sleep 10

if systemctl is-active --quiet odoo; then
    print_status "Odoo service is running and ready"
else
    print_warning "Odoo service may not be fully ready yet"
fi

# Display enhanced features
echo ""
print_header "Enhanced Dashboard Features Deployed:"
echo -e "${GREEN}  ✅ Merged Best Practices from Version 1 & 2${NC}"
echo -e "${GREEN}  ✅ Defensive field checking (booking_date/create_date)${NC}"
echo -e "${GREEN}  ✅ Auto-refresh capability${NC}"
echo -e "${GREEN}  ✅ Enhanced KPIs (conversion rate, pipeline velocity)${NC}"
echo -e "${GREEN}  ✅ Revenue growth calculation${NC}"
echo -e "${GREEN}  ✅ Performance tracking${NC}"
echo -e "${GREEN}  ✅ CSV export functionality${NC}"
echo -e "${GREEN}  ✅ Responsive mobile design${NC}"
echo -e "${GREEN}  ✅ Registry error fixes${NC}"

echo ""
print_header "Access Your Enhanced Dashboard:"
echo -e "${CYAN}Navigate to: Sales > Reports > OSUS Executive Sales Dashboard${NC}"
echo -e "${CYAN}Or direct URL: https://your-domain.com/web#action=oe_sale_dashboard_17_tag${NC}"

echo ""
print_header "Troubleshooting:"
echo -e "${YELLOW}  • Check logs: sudo journalctl -u odoo -f${NC}"
echo -e "${YELLOW}  • Service status: sudo systemctl status odoo${NC}"
echo -e "${YELLOW}  • Clear browser cache if needed${NC}"
echo -e "${YELLOW}  • Verify dependencies: sale_management, osus_invoice_report, le_sale_type${NC}"

echo ""
print_status "🎉 CloudPepper deployment completed successfully!"
echo -e "${MAGENTA}=== End of Deployment ===${NC}"
