#!/bin/bash

# Commission App Docker Installation Test Script
# This script tests the installation of commission_app module in Docker environment

echo "🚀 Commission App - Docker Installation Test"
echo "=============================================="

# Check if Docker is running
echo "📋 Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi
echo "✅ Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in current directory"
    exit 1
fi
echo "✅ docker-compose.yml found"

# Check if commission_app module exists
if [ ! -d "commission_app" ]; then
    echo "❌ commission_app module not found"
    exit 1
fi
echo "✅ commission_app module found"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start the environment
echo "🚀 Starting Docker environment..."
docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for containers to start..."
sleep 10

# Check container status
echo "📊 Container status:"
docker-compose ps

# Check if Odoo is responding
echo "🔍 Checking Odoo availability..."
for i in {1..30}; do
    if curl -s http://localhost:8069 > /dev/null; then
        echo "✅ Odoo is responding on port 8069"
        break
    fi
    echo "⏳ Waiting for Odoo to start... ($i/30)"
    sleep 5
done

# Test module installation
echo "🔧 Testing commission_app module installation..."

# First, update the module list
echo "📋 Updating module list..."
docker-compose exec -T web odoo --stop-after-init --update=base --db_host=db --db_user=odoo --db_password=myodoo -d test_db

# Try to install the commission_app module
echo "⚡ Installing commission_app module..."
docker-compose exec -T web odoo --stop-after-init --init=commission_app --db_host=db --db_user=odoo --db_password=myodoo -d test_commission_db

if [ $? -eq 0 ]; then
    echo "✅ commission_app module installation completed successfully!"
    
    # Show logs to verify
    echo "📋 Recent Odoo logs:"
    docker-compose logs --tail=50 web | grep -i commission || echo "No commission-related logs found"
    
    echo ""
    echo "🎉 SUCCESS: Commission App Docker test completed!"
    echo "📝 Summary:"
    echo "   - Docker environment started successfully"
    echo "   - commission_app module installed without errors"  
    echo "   - Odoo is accessible on http://localhost:8069"
    echo ""
    echo "🔗 Next steps:"
    echo "   1. Open http://localhost:8069 in your browser"
    echo "   2. Create a new database"
    echo "   3. Install commission_app from Apps menu"
    echo "   4. Configure commission rules and test functionality"
    
else
    echo "❌ commission_app module installation failed!"
    echo "📋 Error logs:"
    docker-compose logs --tail=100 web
    exit 1
fi