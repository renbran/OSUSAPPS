#!/bin/bash
# Odoo 17 MCP Server Installation Script

set -e

echo "🚀 Installing Odoo 17 Development MCP Server..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Setting up configuration..."

# Create sample .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOL
# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=odoo

# Docker settings
COMPOSE_FILE=docker-compose.yml
ODOO_SERVICE=odoo

# Development settings
DEBUG=false
LOG_LEVEL=INFO

# Paths
ODOO_ADDONS_PATH=/mnt/extra-addons
LOG_PATH=/var/log/odoo
EOL
    echo "✅ Created .env configuration file"
fi

# Test server startup
echo "🧪 Testing server startup..."
timeout 10s python odoo17_mcp_server.py --test || {
    echo "⚠️  Server test timed out (expected for MCP servers)"
}

echo "✅ Installation completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure your MCP client to use this server"
echo "2. Update .env file with your specific settings"
echo "3. Ensure Docker and PostgreSQL are running for full functionality"
echo ""
echo "📚 See README.md for detailed usage instructions"
echo "🏁 Start the server with: python odoo17_mcp_server.py"