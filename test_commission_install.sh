#!/bin/bash

echo "🚀 Commission AX Installation Test Script"
echo "========================================"

cd "d:\RUNNING APPS\ready production\latest\OSUSAPPS"

# Stop any running containers
echo "📢 Stopping containers..."
docker-compose down

# Start fresh
echo "📢 Starting fresh containers..."
docker-compose up -d db

# Wait for database
echo "📢 Waiting for database to be ready..."
sleep 10

# Try to install commission_ax
echo "📢 Installing commission_ax module..."
docker-compose run --rm odoo odoo -d odoo -i commission_ax --stop-after-init --log-level=error --logfile=/tmp/commission_install.log

# Check exit code
exit_code=$?
echo "📢 Installation exit code: $exit_code"

# If successful, try to start Odoo with the module
if [ $exit_code -eq 0 ]; then
    echo "✅ Installation successful! Starting Odoo..."
    docker-compose up -d odoo
    echo "✅ Commission AX module is ready!"
else
    echo "❌ Installation failed. Exit code: $exit_code"
    echo "📋 Checking logs..."
    docker-compose run --rm odoo cat /tmp/commission_install.log || echo "No log file found"
fi