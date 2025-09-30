@echo off
REM Odoo 17 MCP Server Installation Script for Windows

echo 🚀 Installing Odoo 17 Development MCP Server...

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python not found. Please install Python 3.8+
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo 🔧 Setting up configuration...

REM Create sample .env file if it doesn't exist
if not exist .env (
    echo # Database settings > .env
    echo DB_HOST=localhost >> .env
    echo DB_PORT=5432 >> .env
    echo DB_USER=odoo >> .env
    echo DB_PASSWORD=odoo >> .env
    echo. >> .env
    echo # Docker settings >> .env
    echo COMPOSE_FILE=docker-compose.yml >> .env
    echo ODOO_SERVICE=odoo >> .env
    echo. >> .env
    echo # Development settings >> .env
    echo DEBUG=false >> .env
    echo LOG_LEVEL=INFO >> .env
    echo. >> .env
    echo # Paths >> .env
    echo ODOO_ADDONS_PATH=/mnt/extra-addons >> .env
    echo LOG_PATH=/var/log/odoo >> .env
    
    echo ✅ Created .env configuration file
)

REM Test server startup
echo 🧪 Testing server startup...
timeout /t 5 >nul
python odoo17_mcp_server.py --help >nul 2>&1

echo ✅ Installation completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Configure your MCP client to use this server
echo 2. Update .env file with your specific settings  
echo 3. Ensure Docker and PostgreSQL are running for full functionality
echo.
echo 📚 See README.md for detailed usage instructions
echo 🏁 Start the server with: python odoo17_mcp_server.py

pause