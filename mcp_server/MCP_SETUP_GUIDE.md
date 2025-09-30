# 🚀 MCP Server Setup & Usage Guide

## What is MCP (Model Context Protocol)?

MCP is a standardized protocol that allows AI assistants (like Claude, ChatGPT, etc.) to interact with external tools and services. Our Odoo 17 MCP Server provides 21 specialized development tools that can be used directly through your AI assistant.

## 🔧 Installation & Setup

### Step 1: Install the MCP Server

**For Windows:**
```bash
cd "d:\RUNNING APPS\ready production\latest\OSUSAPPS\mcp_server"
.\install.bat
```

**For Linux/Mac:**
```bash
cd "/path/to/OSUSAPPS/mcp_server"
chmod +x install.sh
./install.sh
```

**Manual Installation:**
```bash
# Navigate to MCP server directory
cd mcp_server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Your MCP Client

The MCP server needs to be configured in your MCP client (like Claude Desktop, etc.).

#### For Claude Desktop:

1. **Find your Claude Desktop config file:**
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/claude/claude_desktop_config.json`

2. **Add the MCP server configuration:**
```json
{
  "mcpServers": {
    "odoo17-dev-server": {
      "command": "python",
      "args": ["odoo17_mcp_server.py"],
      "cwd": "d:\\RUNNING APPS\\ready production\\latest\\OSUSAPPS\\mcp_server",
      "env": {
        "PYTHONPATH": "d:\\RUNNING APPS\\ready production\\latest\\OSUSAPPS\\mcp_server"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

#### For other MCP clients:

Follow your client's documentation to add an MCP server with:
- **Command:** `python odoo17_mcp_server.py`
- **Working Directory:** Your mcp_server folder path
- **Environment:** Set PYTHONPATH to the mcp_server directory

## 📋 How to Use MCP Tools

### Method 1: Direct AI Assistant Commands

Once configured, you can ask your AI assistant to use the tools directly:

```
"Create a new Odoo module called 'sales_enhancement' with models and views"

"Check the health of my custom_sales module"

"Run tests for the commission_unified module with coverage"

"Check Docker container status for Odoo"

"Lint and format the code in my account_statement module"
```

### Method 2: Specific Tool Requests

You can request specific tools by name:

```
"Use the scaffold_odoo_module tool to create a module named 'inventory_tracker'"

"Run the docker_odoo_logs tool to get the last 100 lines"

"Execute the db_backup tool for my development database"
```

## 🛠️ Available Tools Quick Reference

### 📦 Module Management
- **scaffold_odoo_module** - Create complete Odoo modules
- **validate_module_manifest** - Validate __manifest__.py files  
- **analyze_module_structure** - Analyze module architecture
- **check_module_health** - Comprehensive module health check

### 🐳 Docker Operations
- **docker_odoo_status** - Check container status
- **docker_odoo_logs** - Get container logs
- **docker_odoo_restart** - Restart Odoo services
- **docker_odoo_shell** - Execute shell commands

### 🔍 Code Quality  
- **lint_python_code** - Run flake8/pylint with fixes
- **format_python_code** - Format with black/isort
- **validate_xml_syntax** - Validate XML files

### 🗄️ Database Management
- **db_backup** - Create PostgreSQL backups
- **db_restore** - Restore databases
- **db_query** - Execute safe SQL queries

### 🧪 Testing & QA
- **run_odoo_tests** - Run module tests with coverage
- **generate_test_data** - Create test data
- **analyze_performance** - Performance analysis
- **check_security** - Security validation

### 🚀 Deployment & Utilities
- **deploy_module** - Deploy to environments
- **generate_requirements** - Create requirements.txt
- **odoo_shell** - Execute Python in Odoo shell
- **check_odoo_logs** - Analyze Odoo logs

## 💡 Common Usage Patterns

### 1. New Module Development Workflow
```
1. "Create a new module for customer feedback management"
   → Uses scaffold_odoo_module

2. "Check the health of the new module"
   → Uses check_module_health

3. "Lint and format the generated code"
   → Uses lint_python_code & format_python_code

4. "Run tests for the module"
   → Uses run_odoo_tests
```

### 2. Docker Environment Management
```
1. "Check if Odoo containers are running"
   → Uses docker_odoo_status

2. "Show me the latest Odoo logs"
   → Uses docker_odoo_logs

3. "Restart the Odoo service"
   → Uses docker_odoo_restart
```

### 3. Database Operations
```
1. "Create a backup of my development database"
   → Uses db_backup

2. "Show me the last 10 users created"
   → Uses db_query

3. "Generate test data for my new module"
   → Uses generate_test_data
```

## 🔧 Configuration Options

### Environment Variables (.env file)
```bash
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
```

### MCP Server Configuration (mcp_config.json)
```json
{
  "name": "odoo17-development-server",
  "version": "1.0.0",
  "description": "Comprehensive MCP server for Odoo 17 development",
  "tools_enabled": true,
  "max_concurrent_tools": 5,
  "timeout_seconds": 300,
  "debug_mode": false
}
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. MCP Server Not Starting
```bash
# Check Python version (requires 3.8+)
python --version

# Check if all dependencies are installed
pip list | grep mcp

# Try running the server manually
python odoo17_mcp_server.py --test
```

#### 2. Tools Not Appearing in AI Assistant
- Restart your MCP client (Claude Desktop, etc.)
- Check the configuration file path and syntax
- Verify the working directory path is correct
- Check server logs for errors

#### 3. Docker Operations Failing
```bash
# Verify Docker is running
docker ps

# Check if docker-compose.yml exists
ls docker-compose.yml

# Test Docker Compose
docker-compose ps
```

#### 4. Database Connection Issues
```bash
# Check PostgreSQL container
docker-compose ps db

# Test database connection
docker-compose exec db psql -U odoo -d postgres -c "SELECT 1;"
```

### Debug Mode

Enable debug logging in `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

Check server logs:
```bash
# View real-time logs
tail -f debug.log

# Check for specific errors
grep ERROR debug.log
```

## 📝 Example Conversations

### Creating a Complete Module
**You:** "I need to create a customer loyalty module with points tracking"

**AI Assistant:** *Uses scaffold_odoo_module to create the module with models for loyalty points, views for management, and security rules*

### Code Quality Check
**You:** "Check and improve the code quality of my commission_unified module"

**AI Assistant:** *Uses lint_python_code and format_python_code to analyze and fix code issues*

### Testing & Deployment
**You:** "Run comprehensive tests on my modules and deploy to staging"

**AI Assistant:** *Uses run_odoo_tests for testing and deploy_module for staging deployment*

## 🔄 Updates & Maintenance

### Updating the MCP Server
```bash
# Navigate to mcp_server directory
cd mcp_server

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart your MCP client
```

### Adding Custom Tools
You can extend the server by adding new tools to the appropriate tool file:

1. Add your tool function to the relevant tool file
2. Register it in `odoo17_mcp_server.py`
3. Update the documentation
4. Restart the server

## 📞 Support & Help

- **Documentation:** See README.md for detailed tool documentation
- **Examples:** Check the examples/ directory (if available)
- **Issues:** Report problems with specific error messages
- **Community:** Join Odoo development forums for general questions

## 🎯 Best Practices

1. **Always specify module paths clearly** when asking for operations
2. **Use descriptive module names** for better organization
3. **Run health checks** before deploying modules
4. **Create backups** before major database operations
5. **Test modules thoroughly** before production deployment
6. **Keep your MCP server updated** for latest features

---

**🎉 You're now ready to use the MCP server for accelerated Odoo 17 development!**

The AI assistant can now help you with module creation, code quality, testing, deployment, and much more using these 21 powerful development tools.