# Odoo 17 MCP Server - Enhanced Edition
## Complete Installation & Upgrade Guide

---

## 🚀 What's New in Enhanced Edition

### Major Enhancements

✅ **Configuration System**
- Full `.env` file support with validation
- Cross-platform compatibility (Windows/Linux/macOS)
- Secure credential management
- Hot-reload configuration

✅ **Async Operations**
- Non-blocking subprocess execution
- Proper async/await implementation
- Improved performance and responsiveness

✅ **Error Handling**
- Comprehensive exception hierarchy
- Retry logic with exponential backoff
- Detailed error context and suggestions
- Categorized errors by severity

✅ **Security Layer**
- Input validation for all operations
- SQL injection prevention
- Command injection prevention
- Path traversal protection
- Credential encryption

✅ **Performance Optimizations**
- Database connection pooling (async + sync)
- Query result caching
- Parallel operation support
- Resource management

✅ **Monitoring & Metrics**
- Tool usage tracking
- Performance analytics
- Error rate monitoring
- Exportable reports

✅ **New Advanced Tools** (15+)
- Dependency graph generator
- Code complexity analyzer
- Security vulnerability scanner
- Automated test generator
- Module comparison tool
- And 10+ more!

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8+ (3.10+ recommended)
- **PostgreSQL**: 12+ (for database operations)
- **Docker**: Latest (for container operations)
- **Git**: 2.30+ (for version control features)

### Operating Systems
- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+, Debian 11+, etc.)
- ✅ macOS 11+

---

## 🔧 Fresh Installation

### Step 1: Clone/Download the MCP Server

```bash
cd "D:\RUNNING APPS\ready production\latest\OSUSAPPS"
# Files should be in mcp_server directory
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```cmd
cd mcp_server
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd mcp_server
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install with optional performance enhancements
pip install -r requirements.txt ujson uvloop

# Verify installation
python -c "import mcp; print('MCP installed successfully')"
```

### Step 4: Configure Environment

```bash
# Copy example .env file
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS

# Edit .env file with your settings
notepad .env    # Windows
# nano .env     # Linux/macOS
```

**Essential Configuration:**
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=your_password_here

# Docker
COMPOSE_FILE=docker-compose.yml
USE_DOCKER_COMPOSE_V2=true

# Paths (adjust for your system)
BACKUP_PATH=./backups
```

### Step 5: Test Configuration

```bash
# Test configuration loading
python config.py

# You should see a configuration summary
```

### Step 6: Update MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop config):

**Windows** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "odoo17-dev-server": {
      "command": "python",
      "args": ["odoo17_mcp_server.py"],
      "cwd": "D:\\RUNNING APPS\\ready production\\latest\\OSUSAPPS\\mcp_server",
      "env": {
        "PYTHONPATH": "D:\\RUNNING APPS\\ready production\\latest\\OSUSAPPS\\mcp_server"
      }
    }
  }
}
```

**Linux/macOS** (`~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "odoo17-dev-server": {
      "command": "python3",
      "args": ["odoo17_mcp_server.py"],
      "cwd": "/path/to/mcp_server",
      "env": {
        "PYTHONPATH": "/path/to/mcp_server"
      }
    }
  }
}
```

### Step 7: Start the Server

```bash
python odoo17_mcp_server.py
```

You should see:
```
Starting Odoo 17 MCP Server...
Server initialized successfully
Available tools: scaffold_odoo_module, ...
```

---

## 🔄 Upgrading from Previous Version

### Step 1: Backup Current Installation

```bash
# Backup your configuration
copy .env .env.backup    # Windows
# cp .env .env.backup    # Linux/macOS

# Backup any custom modifications
copy custom_config.json custom_config.json.backup
```

### Step 2: Update Files

Replace all Python files with the new enhanced versions:
- `config.py` ⭐ NEW
- `async_utils.py` ⭐ NEW
- `exceptions.py` ⭐ NEW
- `security.py` ⭐ NEW
- `db_pool.py` ⭐ NEW
- `metrics.py` ⭐ NEW
- `advanced_tools.py` ⭐ NEW
- `requirements.txt` ✏️ UPDATED
- `odoo17_mcp_server.py` ✏️ UPDATED (will update next)
- All existing tool files

### Step 3: Install New Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate    # Windows
# source venv/bin/activate    # Linux/macOS

# Upgrade pip
python -m pip install --upgrade pip

# Install new dependencies
pip install -r requirements.txt --upgrade

# Install optional async database driver
pip install asyncpg

# Install security dependencies
pip install cryptography bcrypt
```

### Step 4: Create .env Configuration

```bash
# Copy example file
copy .env.example .env

# Migrate your old settings to new .env file
# Old settings from custom files should be moved to .env
```

### Step 5: Test Upgraded Installation

```bash
# Test all new modules
python -c "from config import get_config; print(get_config().print_summary())"
python -c "from async_utils import get_executor; print('Async utils OK')"
python -c "from security import get_security_manager; print('Security OK')"
python -c "from metrics import get_metrics_collector; print('Metrics OK')"
```

### Step 6: Restart MCP Server

```bash
# Restart the server to load new features
python odoo17_mcp_server.py
```

---

## ✅ Verification Checklist

After installation/upgrade, verify everything works:

- [ ] Configuration loads without errors
- [ ] All Python modules import successfully
- [ ] Database connection works (if configured)
- [ ] Docker commands execute (if Docker installed)
- [ ] MCP client can connect to server
- [ ] Sample tool execution works
- [ ] Metrics collection is active
- [ ] Security validation works

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
pip install mcp --upgrade
```

#### 2. AsyncPG Not Available

**Problem:** `asyncpg not available` warning

**Solution:**
```bash
pip install asyncpg
```

**Note:** Server will still work with psycopg2, but async features will be limited.

#### 3. Configuration Validation Fails

**Problem:** `Configuration validation failed: Invalid database port`

**Solution:**
- Check `.env` file for typos
- Ensure all values are in correct format
- Review error messages for specific issues

#### 4. Windows Path Issues

**Problem:** Paths with backslashes causing errors

**Solution:**
- Use forward slashes in .env: `C:/Users/...`
- Or escape backslashes: `C:\\Users\\...`
- Or use raw strings in Python: `r'C:\Users\...'`

#### 5. Docker Compose V2 Issues

**Problem:** `docker-compose: command not found`

**Solution:**
```env
# In .env file, switch to v1 if v2 not available
USE_DOCKER_COMPOSE_V2=false
```

Or install Docker Compose V2:
```bash
# Linux
sudo apt-get install docker-compose-plugin

# Or update Docker Desktop (Windows/macOS)
```

### Debug Mode

Enable detailed logging:

```env
# In .env file
LOG_LEVEL=DEBUG
LOG_FILE=mcp_server.log
```

Then check `mcp_server.log` for detailed information.

---

## 📊 Performance Tuning

### Database Connection Pool

```env
# Optimize for your workload
DB_MAX_CONNECTIONS=20  # More for high concurrency
PERF_CONNECTION_POOLING=true
```

### Caching

```env
PERF_ENABLE_CACHING=true
PERF_CACHE_TTL=600  # Increase for slower-changing data
PERF_MAX_CACHE_SIZE=2000
```

### Async Performance

```env
PERF_ASYNC_SUBPROCESS=true
PERF_MAX_CONCURRENT=10  # Adjust based on CPU cores
```

---

## 🔐 Security Configuration

### Production Security Settings

```env
# Enable all security features
SECURITY_INPUT_VALIDATION=true
SECURITY_COMMAND_WHITELIST=true
SECURITY_MAX_TIMEOUT=120

# Restrict allowed operations
SECURITY_MAX_QUERY_LENGTH=5000
```

### Credential Management

Never commit credentials to version control:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
echo "__pycache__/" >> .gitignore
```

---

## 📈 Monitoring

### View Metrics

```bash
# In Python console
from metrics import get_metrics_collector
collector = get_metrics_collector()
print(collector.get_performance_report())
```

### Export Metrics

```bash
# Export to JSON
collector.export_metrics('metrics_report.json')
```

---

## 🆘 Getting Help

### Documentation
- README.md - Overview and quick start
- MCP_SETUP_GUIDE.md - Original setup guide
- INSTALLATION.md - This file
- API_REFERENCE.md - Tool reference (coming soon)

### Support
- GitHub Issues: Report bugs and request features
- Email: support@osusapps.com

---

## 🎓 Next Steps

1. **Explore New Tools:** Try the advanced tools like dependency graph generator
2. **Monitor Performance:** Review metrics to optimize your workflow
3. **Customize:** Adjust `.env` settings for your specific needs
4. **Contribute:** Share improvements with the community

---

**Version:** Enhanced Edition v2.0
**Last Updated:** 2025-10-01
**Author:** OSUSAPPS Development Team

---

*For questions or issues, please create a GitHub issue or contact support.*
