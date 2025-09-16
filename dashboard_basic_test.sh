#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting OE Sales Dashboard 17 Basic Test${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "odoo.*Up"; then
    echo -e "${YELLOW}Starting Docker containers...${NC}"
    docker-compose up -d
    echo -e "${YELLOW}Waiting for containers to start...${NC}"
    sleep 15
fi

# Check for module directory
if [ ! -d "oe_sale_dashboard_17" ]; then
    echo -e "${RED}Module directory not found. Please ensure oe_sale_dashboard_17 directory exists.${NC}"
    exit 1
fi

echo -e "${YELLOW}Checking module structure...${NC}"

# Check manifest
if [ ! -f "oe_sale_dashboard_17/__manifest__.py" ]; then
    echo -e "${RED}Manifest file not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Manifest file exists${NC}"

# Check models directory
if [ ! -d "oe_sale_dashboard_17/models" ] || [ ! -f "oe_sale_dashboard_17/models/__init__.py" ]; then
    echo -e "${RED}Models directory or __init__.py file missing.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Models directory and __init__.py exist${NC}"

# Check security directory
if [ ! -d "oe_sale_dashboard_17/security" ] || [ ! -f "oe_sale_dashboard_17/security/ir.model.access.csv" ]; then
    echo -e "${RED}Security directory or ir.model.access.csv file missing.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Security directory and access file exist${NC}"

# Check views directory
if [ ! -d "oe_sale_dashboard_17/views" ]; then
    echo -e "${RED}Views directory missing.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Views directory exists${NC}"

# List expected view files from manifest
echo -e "${YELLOW}Checking view files referenced in manifest...${NC}"
VIEW_FILES=$(grep -o "'views/[^']*'" oe_sale_dashboard_17/__manifest__.py | tr -d "'")

for file in $VIEW_FILES; do
    if [ ! -f "oe_sale_dashboard_17/$file" ]; then
        echo -e "${RED}✗ View file missing: $file${NC}"
    else
        echo -e "${GREEN}✓ View file exists: $file${NC}"
    fi
done

# Try to install the module
echo -e "${YELLOW}Attempting to install module...${NC}"
docker-compose exec odoo odoo -d odoo -i oe_sale_dashboard_17 --stop-after-init 2>&1 | tee /tmp/install_log.txt

if grep -qi "error\|exception\|traceback" /tmp/install_log.txt; then
    echo -e "${RED}Module installation failed. See errors above.${NC}"
    exit 1
else
    echo -e "${GREEN}Module installed successfully!${NC}"
fi

# Final result
echo -e "${GREEN}OE Sales Dashboard 17 basic test completed.${NC}"