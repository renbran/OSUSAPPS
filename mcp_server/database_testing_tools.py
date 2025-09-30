"""
Odoo 17 MCP Server - Database and Testing Tools

This module contains implementations for database management, testing tools,
and deployment utilities for Odoo 17 development.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import coverage

from mcp.types import CallToolResult, TextContent


class Odoo17DatabaseTools:
    """Database and testing tool implementations for Odoo 17 MCP server."""

    async def _db_backup(self, database: str, output_file: str = None, compress: bool = True) -> CallToolResult:
        """Create backup of Odoo PostgreSQL database."""
        
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"backup_{database}_{timestamp}.sql"
                if compress:
                    output_file += ".gz"
            
            # Build pg_dump command
            cmd = ['pg_dump']
            
            # Add connection parameters (assuming local connection)
            cmd.extend(['-h', 'localhost', '-U', 'odoo', '-d', database])
            
            # Add output options
            if compress:
                cmd.extend(['-Z', '9'])  # Maximum compression
            
            cmd.extend(['--no-owner', '--no-privileges', '--clean', '--if-exists'])
            
            if compress:
                cmd.extend(['|', 'gzip', '>', output_file])
                cmd_str = ' '.join(cmd)
                result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
            else:
                with open(output_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Backup failed: {result.stderr}")]
                )
            
            # Check file size
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            
            result_text = f"✅ Database backup completed successfully\\n\\n"
            result_text += f"📋 Backup Details:\\n"
            result_text += f"  • Database: {database}\\n"
            result_text += f"  • Output File: {output_file}\\n"
            result_text += f"  • File Size: {file_size:.2f} MB\\n"
            result_text += f"  • Compressed: {'Yes' if compress else 'No'}\\n"
            result_text += f"  • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
            
            result_text += "🚀 **Restore Command:**\\n"
            result_text += f"```bash\\n"
            if compress:
                result_text += f"gunzip -c {output_file} | psql -h localhost -U odoo -d new_database_name\\n"
            else:
                result_text += f"psql -h localhost -U odoo -d new_database_name < {output_file}\\n"
            result_text += "```"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error creating backup: {str(e)}")]
            )

    async def _db_restore(self, database: str, backup_file: str, drop_existing: bool = False) -> CallToolResult:
        """Restore Odoo PostgreSQL database from backup."""
        
        try:
            if not Path(backup_file).exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Backup file not found: {backup_file}")]
                )
            
            # Drop existing database if requested
            if drop_existing:
                drop_cmd = ['dropdb', '-h', 'localhost', '-U', 'odoo', '--if-exists', database]
                drop_result = subprocess.run(drop_cmd, capture_output=True, text=True)
                
                if drop_result.returncode != 0 and "does not exist" not in drop_result.stderr:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ Failed to drop database: {drop_result.stderr}")]
                    )
            
            # Create new database
            create_cmd = ['createdb', '-h', 'localhost', '-U', 'odoo', database]
            create_result = subprocess.run(create_cmd, capture_output=True, text=True)
            
            if create_result.returncode != 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Failed to create database: {create_result.stderr}")]
                )
            
            # Restore from backup
            is_compressed = backup_file.endswith('.gz')
            
            if is_compressed:
                cmd_str = f"gunzip -c {backup_file} | psql -h localhost -U odoo -d {database}"
                result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
            else:
                with open(backup_file, 'r') as f:
                    cmd = ['psql', '-h', 'localhost', '-U', 'odoo', '-d', database]
                    result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
            
            if result.returncode != 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Restore failed: {result.stderr}")]
                )
            
            # Get database size after restore
            size_query = """
                SELECT pg_size_pretty(pg_database_size(%s)) as size
            """
            
            try:
                conn = psycopg2.connect(host='localhost', user='odoo', database=database)
                cur = conn.cursor()
                cur.execute(size_query, (database,))
                db_size = cur.fetchone()[0]
                conn.close()
            except:
                db_size = "Unknown"
            
            result_text = f"✅ Database restored successfully\\n\\n"
            result_text += f"📋 Restore Details:\\n"
            result_text += f"  • Database: {database}\\n"
            result_text += f"  • Source File: {backup_file}\\n"
            result_text += f"  • Database Size: {db_size}\\n"
            result_text += f"  • Dropped Existing: {'Yes' if drop_existing else 'No'}\\n"
            result_text += f"  • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
            
            result_text += "🚀 **Next Steps:**\\n"
            result_text += f"1. Update Odoo modules: `docker-compose exec odoo odoo -u all -d {database}`\\n"
            result_text += f"2. Test database connectivity\\n"
            result_text += f"3. Verify data integrity"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error restoring database: {str(e)}")]
            )

    async def _db_query(self, database: str, query: str, format: str = "table") -> CallToolResult:
        """Execute SQL query on Odoo database."""
        
        try:
            # Security check - prevent dangerous operations
            dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
            query_upper = query.upper().strip()
            
            is_dangerous = any(query_upper.startswith(keyword) for keyword in dangerous_keywords)
            
            if is_dangerous:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Dangerous query detected. This tool only supports SELECT queries for safety.")]
                )
            
            # Connect to database
            conn = psycopg2.connect(
                host='localhost', 
                user='odoo', 
                database=database,
                cursor_factory=RealDictCursor
            )
            
            cur = conn.cursor()
            cur.execute(query)
            
            if query_upper.startswith('SELECT'):
                results = cur.fetchall()
                
                if not results:
                    return CallToolResult(
                        content=[TextContent(type="text", text="📋 Query executed successfully - No results returned")]
                    )
                
                # Format results based on requested format
                if format == "json":
                    result_text = f"📋 Query Results (JSON):\\n\\n"
                    result_text += "```json\\n"
                    result_text += json.dumps(results, indent=2, default=str)
                    result_text += "\\n```"
                    
                elif format == "csv":
                    result_text = f"📋 Query Results (CSV):\\n\\n"
                    result_text += "```csv\\n"
                    
                    if results:
                        # Get column names
                        columns = list(results[0].keys())
                        
                        # Write CSV
                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerow(columns)
                        
                        for row in results:
                            writer.writerow([row[col] for col in columns])
                        
                        result_text += output.getvalue()
                    
                    result_text += "```"
                    
                else:  # table format (default)
                    result_text = f"📋 Query Results ({len(results)} rows):\\n\\n"
                    
                    if results:
                        # Get column names
                        columns = list(results[0].keys())
                        
                        # Calculate column widths
                        col_widths = {}
                        for col in columns:
                            col_widths[col] = max(
                                len(str(col)),
                                max(len(str(row[col])) for row in results[:10])  # Check first 10 rows
                            )
                        
                        # Create table
                        result_text += "|"
                        for col in columns:
                            result_text += f" {col:<{col_widths[col]}} |"
                        result_text += "\\n"
                        
                        result_text += "|"
                        for col in columns:
                            result_text += "-" * (col_widths[col] + 2) + "|"
                        result_text += "\\n"
                        
                        # Add data rows (limit to first 50 for readability)
                        for i, row in enumerate(results[:50]):
                            result_text += "|"
                            for col in columns:
                                value = str(row[col])[:col_widths[col]]  # Truncate if too long
                                result_text += f" {value:<{col_widths[col]}} |"
                            result_text += "\\n"
                        
                        if len(results) > 50:
                            result_text += f"\\n... and {len(results) - 50} more rows"
            else:
                result_text = f"✅ Query executed successfully"
            
            conn.close()
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except psycopg2.Error as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Database error: {str(e)}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error executing query: {str(e)}")]
            )

    async def _run_odoo_tests(self, module: str, database: str = None, test_tags: List[str] = None, coverage: bool = False) -> CallToolResult:
        """Run Odoo module tests."""
        
        try:
            if database is None:
                database = "test_" + module
            
            # Build test command
            cmd = ['docker-compose', 'exec', '-T', 'odoo', 'odoo']
            
            # Add test parameters
            cmd.extend(['--test-enable', '--stop-after-init', '-d', database])
            
            # Add module to install/test
            cmd.extend(['-i', module])
            
            # Add test tags if specified
            if test_tags:
                cmd.extend(['--test-tags', ','.join(test_tags)])
            
            # Set log level for tests
            cmd.extend(['--log-level', 'test'])
            
            # Add coverage if requested
            if coverage:
                cmd = ['coverage', 'run'] + cmd[3:]  # Replace docker-compose exec part
            
            # Run tests
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            # Parse test output
            output_lines = result.stdout.split('\\n') + result.stderr.split('\\n')
            
            test_results = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'skipped': 0,
                'failures': [],
                'errors_list': []
            }
            
            # Simple parsing of test results
            for line in output_lines:
                if 'test' in line.lower() and ('ok' in line.lower() or 'fail' in line.lower()):
                    test_results['total'] += 1
                    if 'ok' in line.lower():
                        test_results['passed'] += 1
                    elif 'fail' in line.lower():
                        test_results['failed'] += 1
                        test_results['failures'].append(line.strip())
                    elif 'error' in line.lower():
                        test_results['errors'] += 1
                        test_results['errors_list'].append(line.strip())
            
            # Generate result
            result_text = f"🧪 Test Results for Module: {module}\\n\\n"
            
            if result.returncode == 0:
                result_text += "✅ Tests completed successfully\\n\\n"
            else:
                result_text += f"❌ Tests failed (exit code: {result.returncode})\\n\\n"
            
            result_text += f"📊 **Summary:**\\n"
            result_text += f"  • Total Tests: {test_results['total']}\\n"
            result_text += f"  • Passed: {test_results['passed']}\\n"
            result_text += f"  • Failed: {test_results['failed']}\\n"
            result_text += f"  • Errors: {test_results['errors']}\\n\\n"
            
            if test_results['failures']:
                result_text += "❌ **Failures:**\\n"
                for failure in test_results['failures'][:5]:  # Show first 5
                    result_text += f"  • {failure}\\n"
                if len(test_results['failures']) > 5:
                    result_text += f"  ... and {len(test_results['failures']) - 5} more\\n"
                result_text += "\\n"
            
            if test_results['errors_list']:
                result_text += "💥 **Errors:**\\n"
                for error in test_results['errors_list'][:5]:  # Show first 5
                    result_text += f"  • {error}\\n"
                if len(test_results['errors_list']) > 5:
                    result_text += f"  ... and {len(test_results['errors_list']) - 5} more\\n"
                result_text += "\\n"
            
            # Show full output if there are issues
            if result.returncode != 0:
                result_text += "📋 **Full Output:**\\n"
                result_text += "```\\n"
                result_text += result.stdout[-2000:]  # Last 2000 chars
                result_text += "\\n```\\n\\n"
            
            # Coverage report
            if coverage and result.returncode == 0:
                try:
                    cov_result = subprocess.run(['coverage', 'report', '--show-missing'], 
                                              capture_output=True, text=True)
                    if cov_result.returncode == 0:
                        result_text += "📈 **Coverage Report:**\\n"
                        result_text += "```\\n"
                        result_text += cov_result.stdout
                        result_text += "\\n```\\n"
                except:
                    result_text += "⚠️ Coverage report generation failed\\n"
            
            # Add recommendations
            result_text += "💡 **Recommendations:**\\n"
            result_text += f"- Run specific tests: `--test-tags tag1,tag2`\\n"
            result_text += f"- Enable coverage: `coverage run odoo --test-enable -i {module}`\\n"
            result_text += f"- Debug tests: `--log-level debug --test-enable`\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text=f"⏱️ Test execution timed out after 5 minutes")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error running tests: {str(e)}")]
            )

    async def _generate_test_data(self, module: str, model: str, count: int = 10) -> CallToolResult:
        """Generate test data for Odoo modules."""
        
        try:
            # Create Python script to generate test data
            script_content = f'''
import random
import string
from datetime import datetime, timedelta

# Connect to Odoo environment
env = self.env
model_obj = env['{model}']

# Sample data generators
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_email():
    return f"{{random_string(8)}}@example.com"

def random_phone():
    return f"+1-{''.join(random.choices(string.digits, k=10))}"

def random_date():
    base = datetime.now()
    return base - timedelta(days=random.randint(0, 365))

# Generate sample records
created_records = []
for i in range({count}):
    vals = {{
        'name': f"Test Record {{i+1}} {{random_string(5)}}",
    }}
    
    # Add common fields based on model type
    model_fields = model_obj._fields
    
    if 'email' in model_fields:
        vals['email'] = random_email()
    
    if 'phone' in model_fields:
        vals['phone'] = random_phone()
    
    if 'date' in model_fields:
        vals['date'] = random_date()
    
    if 'description' in model_fields:
        vals['description'] = f"Auto-generated test description {{random_string(20)}}"
    
    if 'active' in model_fields:
        vals['active'] = random.choice([True, False])
    
    if 'priority' in model_fields:
        vals['priority'] = random.choice(['0', '1', '2', '3'])
    
    try:
        record = model_obj.create(vals)
        created_records.append(record.id)
        print(f"Created record {{record.id}}: {{record.display_name}}")
    except Exception as e:
        print(f"Error creating record {{i+1}}: {{e}}")

print(f"Successfully created {{len(created_records)}} test records")
print(f"Record IDs: {{created_records}}")
'''
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Execute script in Odoo shell
                cmd = [
                    'docker-compose', 'exec', '-T', 'odoo', 
                    'odoo', 'shell', '-c', f'exec(open("{script_path}").read())'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    result_text = f"✅ Test data generation completed\\n\\n"
                    result_text += f"📋 **Details:**\\n"
                    result_text += f"  • Module: {module}\\n"
                    result_text += f"  • Model: {model}\\n"
                    result_text += f"  • Records Created: {count}\\n\\n"
                    
                    if result.stdout:
                        result_text += f"📤 **Output:**\\n"
                        result_text += f"```\\n{result.stdout}\\n```\\n\\n"
                    
                    result_text += f"🚀 **Next Steps:**\\n"
                    result_text += f"1. Check records in Odoo UI: Model '{model}'\\n"
                    result_text += f"2. Use data for testing module functionality\\n"
                    result_text += f"3. Clean up test data when no longer needed"
                    
                else:
                    result_text = f"❌ Test data generation failed\\n\\n"
                    result_text += f"**Error Output:**\\n```\\n{result.stderr}\\n```"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
            finally:
                # Clean up temporary file
                os.unlink(script_path)
                
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text=f"⏱️ Test data generation timed out")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error generating test data: {str(e)}")]
            )

    async def _deploy_module(self, module_path: str, target: str = "local", update_mode: str = "update") -> CallToolResult:
        """Deploy Odoo module to server."""
        
        try:
            module_path = Path(module_path)
            
            if not module_path.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Module path not found: {module_path}")]
                )
            
            module_name = module_path.name
            
            # Validate module structure before deployment
            manifest_file = module_path / "__manifest__.py"
            if not manifest_file.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ No __manifest__.py found in {module_path}")]
                )
            
            result_text = f"🚀 Deploying Module: {module_name}\\n\\n"
            result_text += f"📋 **Deployment Details:**\\n"
            result_text += f"  • Source: {module_path}\\n"
            result_text += f"  • Target: {target}\\n"
            result_text += f"  • Mode: {update_mode}\\n\\n"
            
            deployment_steps = []
            
            if target == "local":
                # Local Docker deployment
                
                # Step 1: Copy module to addons directory
                deployment_steps.append("📁 Copying module to addons directory...")
                
                # Step 2: Restart Odoo service
                deployment_steps.append("🔄 Restarting Odoo service...")
                cmd = ['docker-compose', 'restart', 'odoo']
                restart_result = subprocess.run(cmd, capture_output=True, text=True)
                
                if restart_result.returncode != 0:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ Failed to restart Odoo: {restart_result.stderr}")]
                    )
                
                # Step 3: Update/install module
                deployment_steps.append(f"📦 {update_mode.title()}ing module...")
                
                if update_mode == "install":
                    cmd = ['docker-compose', 'exec', '-T', 'odoo', 'odoo', '-i', module_name, '--stop-after-init']
                elif update_mode == "update":
                    cmd = ['docker-compose', 'exec', '-T', 'odoo', 'odoo', '-u', module_name, '--stop-after-init']
                elif update_mode == "upgrade":
                    cmd = ['docker-compose', 'exec', '-T', 'odoo', 'odoo', '-u', 'all', '--stop-after-init']
                
                install_result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if install_result.returncode != 0:
                    deployment_steps.append(f"❌ Module {update_mode} failed")
                    result_text += "\\n".join(deployment_steps) + "\\n\\n"
                    result_text += f"**Error Output:**\\n```\\n{install_result.stderr}\\n```"
                    return CallToolResult(
                        content=[TextContent(type="text", text=result_text)]
                    )
                else:
                    deployment_steps.append(f"✅ Module {update_mode} completed successfully")
                
                # Step 4: Start Odoo normally
                deployment_steps.append("▶️ Starting Odoo service...")
                start_cmd = ['docker-compose', 'up', '-d', 'odoo']
                start_result = subprocess.run(start_cmd, capture_output=True, text=True)
                
                if start_result.returncode == 0:
                    deployment_steps.append("✅ Odoo service started successfully")
                else:
                    deployment_steps.append("⚠️ Warning: Issue starting Odoo service")
                
            elif target == "staging":
                deployment_steps.append("🧪 Staging deployment not implemented yet")
                
            elif target == "production":
                deployment_steps.append("🏭 Production deployment requires manual verification")
                deployment_steps.append("⚠️ Please use proper CI/CD pipeline for production")
            
            # Add steps to result
            result_text += "📝 **Deployment Steps:**\\n"
            for step in deployment_steps:
                result_text += f"{step}\\n"
            result_text += "\\n"
            
            # Add post-deployment checks
            result_text += "✅ **Post-Deployment Checklist:**\\n"
            result_text += f"1. Verify module appears in Apps list\\n"
            result_text += f"2. Check module menus and views work correctly\\n"
            result_text += f"3. Test module functionality\\n"
            result_text += f"4. Review server logs for any errors\\n"
            result_text += f"5. Run module tests if available\\n\\n"
            
            result_text += "🔧 **Troubleshooting:**\\n"
            result_text += f"- Check logs: `docker-compose logs -f odoo`\\n"
            result_text += f"- Update apps list in Odoo UI\\n"
            result_text += f"- Verify module dependencies are installed\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text=f"⏱️ Deployment timed out")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error deploying module: {str(e)}")]
            )

    async def _generate_requirements(self, module_path: str) -> CallToolResult:
        """Generate requirements.txt for Odoo module dependencies."""
        
        try:
            module_path = Path(module_path)
            
            if not module_path.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Module path not found: {module_path}")]
                )
            
            # Find Python files in the module
            python_files = list(module_path.rglob('*.py'))
            
            # Common Odoo and Python imports to track
            import_tracking = {
                'requests': 'requests',
                'PIL': 'Pillow',
                'qrcode': 'qrcode[pil]',
                'reportlab': 'reportlab',
                'xlsxwriter': 'xlsxwriter',
                'openpyxl': 'openpyxl',
                'lxml': 'lxml',
                'psycopg2': 'psycopg2-binary',
                'cryptography': 'cryptography',
                'jwt': 'PyJWT',
                'dateutil': 'python-dateutil',
                'babel': 'Babel',
                'werkzeug': 'Werkzeug',
                'jinja2': 'Jinja2',
                'markupsafe': 'MarkupSafe',
                'passlib': 'passlib',
                'ldap3': 'ldap3',
                'paramiko': 'paramiko',
                'gevent': 'gevent',
                'greenlet': 'greenlet',
                'num2words': 'num2words',
                'ofxparse': 'ofxparse',
                'pyusb': 'pyusb',
                'serial': 'pyserial',
                'suds': 'suds-py3',
                'vobject': 'vobject',
                'xlrd': 'xlrd',
                'xlwt': 'xlwt'
            }
            
            found_imports = set()
            
            # Scan Python files for imports
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    lines = content.split('\\n')
                    for line in lines:
                        line = line.strip()
                        
                        # Check for import statements
                        if line.startswith(('import ', 'from ')):
                            for import_name, package_name in import_tracking.items():
                                if import_name in line:
                                    found_imports.add(package_name)
                                    
                except Exception as e:
                    # Skip files that can't be read
                    continue
            
            # Check manifest.py for external dependencies
            manifest_file = module_path / "__manifest__.py"
            external_deps = set()
            
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Execute manifest to get dictionary
                    namespace = {}
                    exec(content, namespace)
                    
                    # Find manifest dict
                    manifest = None
                    for key, value in namespace.items():
                        if isinstance(value, dict) and 'name' in value:
                            manifest = value
                            break
                    
                    if manifest and 'external_dependencies' in manifest:
                        ext_deps = manifest['external_dependencies']
                        if isinstance(ext_deps, dict) and 'python' in ext_deps:
                            for dep in ext_deps['python']:
                                external_deps.add(dep)
                                
                except Exception as e:
                    pass
            
            # Combine all dependencies
            all_deps = found_imports.union(external_deps)
            
            # Generate requirements.txt content
            requirements_content = "# Requirements for Odoo module: " + module_path.name + "\\n"
            requirements_content += "# Generated automatically - review and modify as needed\\n\\n"
            
            if all_deps:
                requirements_content += "# Python package dependencies\\n"
                for dep in sorted(all_deps):
                    requirements_content += f"{dep}\\n"
            else:
                requirements_content += "# No external dependencies detected\\n"
                
            requirements_content += "\\n# Common Odoo dependencies (uncomment if needed)\\n"
            requirements_content += "# psycopg2-binary>=2.8.6\\n"
            requirements_content += "# lxml>=4.6.0\\n"
            requirements_content += "# Pillow>=8.0.0\\n"
            requirements_content += "# reportlab>=3.5.0\\n"
            requirements_content += "# requests>=2.25.0\\n"
            
            # Write requirements.txt file
            requirements_file = module_path / "requirements.txt"
            requirements_file.write_text(requirements_content)
            
            # Generate result
            result_text = f"📦 Requirements Generated for Module: {module_path.name}\\n\\n"
            
            if all_deps:
                result_text += f"✅ **Found Dependencies ({len(all_deps)}):**\\n"
                for dep in sorted(all_deps):
                    result_text += f"  • {dep}\\n"
                result_text += "\\n"
            else:
                result_text += "ℹ️ **No external dependencies detected**\\n\\n"
            
            result_text += f"📁 **Output File:** {requirements_file}\\n\\n"
            
            result_text += "📋 **Requirements Content:**\\n"
            result_text += "```\\n"
            result_text += requirements_content
            result_text += "\\n```\\n\\n"
            
            result_text += "🚀 **Installation Commands:**\\n"
            result_text += f"```bash\\n"
            result_text += f"# Install in development environment\\n"
            result_text += f"pip install -r {requirements_file}\\n\\n"
            result_text += f"# Install in Docker container\\n"
            result_text += f"docker-compose exec odoo pip install -r /mnt/extra-addons/{module_path.name}/requirements.txt\\n"
            result_text += "```\\n\\n"
            
            result_text += "💡 **Notes:**\\n"
            result_text += "- Review and modify the generated requirements as needed\\n"
            result_text += "- Add version constraints for better dependency management\\n"
            result_text += "- Consider using virtual environments for development\\n"
            result_text += "- Update Dockerfile if using containerized deployment"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error generating requirements: {str(e)}")]
            )