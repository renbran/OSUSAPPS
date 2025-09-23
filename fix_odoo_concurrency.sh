#!/bin/bash

echo "🛠️  Odoo Database Concurrency Fix Script"
echo "========================================="

# Stop all Odoo processes to prevent concurrent access
echo "📢 Stopping Odoo processes..."
sudo pkill -f odoo
sudo systemctl stop odoo || echo "No systemd service found"

# Wait for processes to stop
echo "📢 Waiting for processes to stop..."
sleep 5

# Check database connections
echo "📢 Checking database connections..."
sudo -u postgres psql -c "SELECT pid, usename, application_name, state FROM pg_stat_activity WHERE datname = 'osusbackup';"

# Kill any remaining connections to the database
echo "📢 Terminating database connections..."
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'osusbackup' AND pid <> pg_backend_pid();"

# Reset module states
echo "📢 Resetting module states in database..."
sudo -u postgres psql osusbackup -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE state IN ('to install', 'to upgrade', 'to remove');"

# Clear any locks
echo "📢 Clearing database locks..."
sudo -u postgres psql osusbackup -c "SELECT pg_advisory_unlock_all();"

echo "✅ Database cleanup completed!"
echo "📢 You can now restart Odoo safely"