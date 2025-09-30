# 🐳 Docker Testing Guide for OSUSAPPS Commission App

## 📊 Current Status
**Date**: October 1, 2025  
**Docker Status**: Not Available ❌  
**Module Status**: Ready for Testing ✅

## 🎯 Testing Strategy

### Phase 1: Docker Environment Setup

#### Option A: Start Docker Desktop (If Installed)
1. **Start Docker Desktop from Windows Start Menu**
   - Search for "Docker Desktop"
   - Click to start the application
   - Wait for Docker to fully initialize (green status)

2. **Verify Docker is Running**
   ```bash
   docker --version
   docker info
   docker ps
   ```

#### Option B: Install Docker Desktop (If Not Installed)
1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download Docker Desktop for Windows
   - Install with default settings

2. **Enable WSL 2 Integration** (recommended)
   - Docker Desktop → Settings → Resources → WSL Integration
   - Enable integration with default WSL distro

### Phase 2: Commission App Docker Testing

#### Test 1: Container Startup
```bash
cd "/d/RUNNING APPS/ready production/latest/OSUSAPPS"
docker compose up -d
```

**Expected Output:**
- PostgreSQL container starts
- Odoo 17 container starts  
- Both containers show "healthy" status

#### Test 2: Service Verification
```bash
# Check running containers
docker compose ps

# Monitor Odoo logs
docker compose logs -f web

# Check database connection
docker compose exec db psql -U odoo -d postgres -c "\l"
```

#### Test 3: Commission App Installation
1. **Access Odoo Web Interface**
   - URL: http://localhost:8069
   - Create database: commission_test
   - Admin password: admin

2. **Install Commission App Module**
   - Go to Apps menu
   - Update Apps List
   - Search for "Commission App"
   - Install the module

3. **Verify Module Components**
   - Check Commission menu appears
   - Navigate to Commission → Operations → Commission Allocations
   - Verify no RPC errors occur

### Phase 3: Comprehensive Testing

#### Test 4: Commission Workflow Testing
1. **Create Commission Rules**
   - Go to Commission → Configuration → Commission Rules
   - Create test rules for different categories

2. **Set Up Commission Partners**
   - Go to Commission → Operations → Commission Partners
   - Create test commission partners

3. **Test Sale Order Integration**
   - Create a sale order
   - Confirm the order
   - Verify commission allocations are created

#### Test 5: Performance Testing
```bash
# Monitor resource usage
docker stats

# Check container logs for errors
docker compose logs web | grep -i error
docker compose logs db | grep -i error
```

## 🔧 Troubleshooting Commands

### Container Issues
```bash
# Restart containers
docker compose restart

# Rebuild containers
docker compose down
docker compose up --build -d

# View container details
docker compose logs web
docker compose exec web bash
```

### Database Issues  
```bash
# Access PostgreSQL shell
docker compose exec db psql -U odoo -d postgres

# Check database size
docker compose exec db du -sh /var/lib/postgresql/data

# Reset database (if needed)
docker compose down -v
docker compose up -d
```

### Module Issues
```bash
# Update module via CLI
docker compose exec web odoo --update=commission_app --stop-after-init

# Install module via CLI  
docker compose exec web odoo -i commission_app --stop-after-init

# Check module status
docker compose exec web odoo --list-db
```

## 📋 Success Criteria

### ✅ Phase 1 Success
- [ ] Docker Desktop running
- [ ] `docker --version` works
- [ ] `docker compose --version` works

### ✅ Phase 2 Success  
- [ ] Both containers (web, db) running
- [ ] Odoo accessible at http://localhost:8069
- [ ] Database connection established

### ✅ Phase 3 Success
- [ ] Commission app module installs without errors
- [ ] All menu items accessible
- [ ] Commission workflows functional
- [ ] No RPC or server errors

## 🚀 Next Steps After Successful Testing

1. **Production Deployment Planning**
2. **Data Migration from commission_ax**  
3. **User Training and Documentation**
4. **Performance Optimization**

---

**Ready to begin testing once Docker is available!** 🎉