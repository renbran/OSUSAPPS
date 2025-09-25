#!/bin/bash
# Quick Fix for Commission AX Database Schema Issue
# Run this when Docker Desktop is available

echo "🔧 Fixing commission_ax database schema..."

# Stop Odoo
docker-compose stop odoo

# Update commission_ax module to create missing database columns
docker-compose run --rm odoo odoo --update=commission_ax --stop-after-init -d erposus

# Start Odoo normally
docker-compose up -d odoo

echo "✅ Schema fix applied. Check logs for success."