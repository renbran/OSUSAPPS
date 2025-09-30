# Odoo 17 Development MCP Server

A comprehensive Model Context Protocol (MCP) server designed specifically for Odoo 17 development workflows. This server provides a rich set of tools for module scaffolding, Docker operations, code quality checks, database management, testing, and deployment automation.

## 🚀 Features

### 📦 Module Management
- **Module Scaffolding**: Create complete Odoo 17 modules with proper structure, manifest, models, views, and security
- **Manifest Validation**: Validate `__manifest__.py` files for Odoo 17 compatibility
- **Structure Analysis**: Analyze module structure and provide improvement recommendations
- **Health Checks**: Comprehensive module health analysis including syntax, security, and performance

### 🐳 Docker Integration
- **Container Status**: Monitor Odoo Docker containers and services
- **Log Management**: Retrieve and analyze Docker container logs
- **Service Control**: Restart Odoo services and execute commands in containers
- **Shell Access**: Execute commands directly in Odoo Docker containers

### 🔍 Code Quality
- **Python Linting**: Run flake8 and pylint on Odoo modules with auto-fix capabilities
- **Code Formatting**: Format code using black and isort with Odoo-specific configurations
- **XML Validation**: Validate XML syntax in Odoo view and data files
- **Best Practices**: Check compliance with Odoo development standards

### 🗄️ Database Management
- **Backup & Restore**: Create and restore PostgreSQL database backups with compression
- **SQL Queries**: Execute safe SELECT queries with multiple output formats (table, JSON, CSV)
- **Database Analysis**: Analyze database structure and performance

### 🧪 Testing & Quality Assurance
- **Test Execution**: Run Odoo module tests with coverage analysis
- **Test Data Generation**: Generate realistic test data for Odoo models
- **Performance Monitoring**: Identify performance bottlenecks and optimization opportunities

### 🚀 Deployment & DevOps
- **Module Deployment**: Deploy modules to local, staging, and production environments
- **Requirements Generation**: Auto-generate requirements.txt from module dependencies
- **CI/CD Integration**: Tools compatible with GitHub Actions and other CI/CD systems

### 🛠️ Development Utilities
- **Odoo Shell**: Execute Python code in Odoo shell environment
- **Log Analysis**: Parse and analyze Odoo logs for errors and patterns
- **Development Workflow**: Streamlined tools for common development tasks

## 📋 Installation

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for Odoo development)
- PostgreSQL (for database operations)
- Git (for version control integration)

### Setup

1. **Clone or download the MCP server files:**
   ```bash
   mkdir odoo17_mcp_server
   cd odoo17_mcp_server
   # Copy all MCP server files here
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MCP client:**
   Add to your MCP client configuration:
   ```json
   {
     "mcpServers": {
       "odoo17-dev-server": {
         "command": "python",
         "args": ["odoo17_mcp_server.py"],
         "cwd": "./mcp_server"
       }
     }
   }
   ```

4. **Start the server:**
   ```bash
   python odoo17_mcp_server.py
   ```

## 🎯 Quick Start

### Creating a New Module

```python
# Use the scaffold_odoo_module tool
{
  "module_name": "my_custom_module",
  "module_title": "My Custom Module", 
  "description": "A comprehensive custom module for specific business needs",
  "author": "Your Name",
  "depends": ["base", "sale", "account"],
  "include_models": true,
  "include_views": true,
  "include_security": true,
  "include_reports": false,
  "include_controllers": true
}
```

### Health Check

```python
# Check module health
{
  "module_path": "/path/to/your/module"
}
```

### Docker Operations

```python
# Check Docker status
{}

# Get logs
{
  "service": "odoo",
  "lines": 100
}

# Restart service
{
  "service": "odoo"
}
```

### Code Quality

```python
# Lint code
{
  "path": "/path/to/module",
  "tool": "both",
  "fix": true
}

# Format code
{
  "path": "/path/to/module",
  "check_only": false
}
```

### Database Operations

```python
# Create backup
{
  "database": "your_db_name",
  "compress": true
}

# Execute query
{
  "database": "your_db_name", 
  "query": "SELECT name, state FROM res_users LIMIT 10",
  "format": "table"
}
```

### Testing

```python
# Run tests
{
  "module": "your_module_name",
  "database": "test_db",
  "coverage": true
}

# Generate test data
{
  "module": "your_module",
  "model": "your_module.record",
  "count": 50
}
```

## 🛠️ Available Tools

### Module Management
- `scaffold_odoo_module` - Create new Odoo 17 modules
- `validate_module_manifest` - Validate manifest files
- `analyze_module_structure` - Analyze module structure
- `check_module_health` - Comprehensive health check

### Docker Operations  
- `docker_odoo_status` - Check container status
- `docker_odoo_logs` - Get container logs
- `docker_odoo_restart` - Restart services
- `docker_odoo_shell` - Execute shell commands

### Code Quality
- `lint_python_code` - Python linting with flake8/pylint
- `format_python_code` - Code formatting with black/isort
- `validate_xml_syntax` - XML validation

### Database Management
- `db_backup` - Create database backups
- `db_restore` - Restore from backups
- `db_query` - Execute SQL queries

### Testing
- `run_odoo_tests` - Run module tests
- `generate_test_data` - Generate test data

### Deployment
- `deploy_module` - Deploy modules
- `generate_requirements` - Generate requirements.txt

### Utilities
- `odoo_shell` - Execute Python in Odoo shell
- `check_odoo_logs` - Analyze log files

## 📚 Configuration

### Environment Variables

Create a `.env` file for configuration:

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
DEBUG=true
LOG_LEVEL=INFO

# Paths
ODOO_ADDONS_PATH=/mnt/extra-addons
LOG_PATH=/var/log/odoo
```

### Docker Compose Integration

The server works with standard Odoo Docker Compose setups:

```yaml
version: '3.1'
services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=myodoo
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=myodoo
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata

volumes:
  odoo-web-data:
  odoo-db-data:
```

## 🏗️ Architecture

### Server Components

1. **Main Server** (`odoo17_mcp_server.py`): Core MCP server with tool registration
2. **Tool Implementations** (`tool_implementations.py`): Module scaffolding and basic tools
3. **Additional Tools** (`additional_tools.py`): Docker, validation, and code quality tools
4. **Database Tools** (`database_testing_tools.py`): Database and testing functionality
5. **Utility Tools** (`utility_tools.py`): Shell access and log analysis

### Tool Categories

```
📁 Odoo 17 MCP Server
├── 🏗️ Module Management
│   ├── Scaffolding & Generation
│   ├── Structure Analysis
│   ├── Health Checks
│   └── Validation
├── 🐳 Docker Integration  
│   ├── Container Management
│   ├── Service Control
│   ├── Log Retrieval
│   └── Shell Access
├── 🔍 Code Quality
│   ├── Python Linting
│   ├── Code Formatting
│   ├── XML Validation
│   └── Best Practices
├── 🗄️ Database Operations
│   ├── Backup & Restore
│   ├── Query Execution
│   └── Performance Analysis
├── 🧪 Testing & QA
│   ├── Test Execution
│   ├── Coverage Analysis
│   ├── Test Data Generation
│   └── Performance Testing
└── 🚀 Deployment & DevOps
    ├── Module Deployment
    ├── Requirements Management
    ├── CI/CD Integration
    └── Environment Management
```

## 🔧 Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tools/improvements
4. Test thoroughly
5. Submit a pull request

### Adding New Tools

```python
# In the appropriate tool file:
async def _my_new_tool(self, param1: str, param2: int = 10) -> CallToolResult:
    """Description of what the tool does."""
    try:
        # Tool implementation
        result = do_something(param1, param2)
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"✅ Success: {result}")]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"❌ Error: {str(e)}")]
        )

# In list_tools method, add:
Tool(
    name="my_new_tool",
    description="Description for MCP client",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "default": 10, "description": "Second parameter"}
        },
        "required": ["param1"]
    }
)

# In call_tool method, add:
elif tool_name == "my_new_tool":
    return await self.tool_class._my_new_tool(**args)
```

### Testing

```bash
# Run server tests
python -m pytest tests/ -v

# Test specific tool
python test_tools.py scaffold_odoo_module

# Integration tests
python integration_tests.py
```

## 📖 Examples

### Complete Development Workflow

```python
# 1. Create new module
scaffold_odoo_module({
    "module_name": "sales_enhancement",
    "module_title": "Sales Enhancement Module",
    "description": "Advanced sales functionality",
    "include_models": true,
    "include_views": true,
    "include_security": true
})

# 2. Check module health
check_module_health({
    "module_path": "./sales_enhancement"
})

# 3. Lint and format code
lint_python_code({
    "path": "./sales_enhancement",
    "tool": "both", 
    "fix": true
})

format_python_code({
    "path": "./sales_enhancement"
})

# 4. Validate structure
analyze_module_structure({
    "module_path": "./sales_enhancement"
})

# 5. Run tests
run_odoo_tests({
    "module": "sales_enhancement",
    "coverage": true
})

# 6. Deploy
deploy_module({
    "module_path": "./sales_enhancement",
    "target": "local",
    "update_mode": "install"
})
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Odoo Module CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      
      - name: Install MCP Server
        run: |
          pip install -r mcp_server/requirements.txt
      
      - name: Validate Modules
        run: |
          python mcp_server/odoo17_mcp_server.py validate_module_manifest ./my_module
          
      - name: Code Quality Check  
        run: |
          python mcp_server/odoo17_mcp_server.py lint_python_code ./my_module
          
      - name: Run Tests
        run: |
          python mcp_server/odoo17_mcp_server.py run_odoo_tests my_module
```

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**
   ```bash
   # Check Python version
   python --version  # Should be 3.8+
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Check MCP configuration
   cat mcp_config.json
   ```

2. **Docker operations fail**
   ```bash
   # Check Docker is running
   docker ps
   
   # Check Docker Compose file exists
   ls docker-compose.yml
   
   # Test Docker Compose
   docker-compose ps
   ```

3. **Database connection issues**
   ```bash
   # Check PostgreSQL is running
   docker-compose ps db
   
   # Test database connection
   docker-compose exec db psql -U odoo -d postgres -c "SELECT 1;"
   ```

4. **Module scaffolding fails**
   ```bash
   # Check output directory permissions
   ls -la ./
   
   # Check module name format (snake_case)
   # Ensure no special characters
   ```

### Debug Mode

Enable debug logging:
```python
# Set environment variable
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run server
python odoo17_mcp_server.py
```

### Log Analysis

```python
# Check recent errors
check_odoo_logs({
    "level": "ERROR",
    "lines": 200
})

# Get Docker logs
docker_odoo_logs({
    "service": "odoo",
    "lines": 100,
    "follow": false
})
```

## 📄 License

This MCP server is licensed under LGPL-3.0, consistent with Odoo's licensing.

## 🤝 Support

- **Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive tool documentation
- **Community**: Join the Odoo development community
- **Professional Support**: Available for custom implementations

## 🔄 Updates

This MCP server is actively maintained with:
- Regular updates for new Odoo 17 features
- Tool improvements and optimizations
- Bug fixes and security updates
- Community-requested features

---

**Built with ❤️ for the Odoo community by OSUSAPPS**

*Making Odoo development faster, safer, and more enjoyable!*