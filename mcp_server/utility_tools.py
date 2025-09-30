"""
Odoo 17 MCP Server - Utility Tools

This module contains utility implementations for Odoo shell execution,
log analysis, and other helper functions for Odoo 17 development.
"""

import asyncio
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from mcp.types import CallToolResult, TextContent


class Odoo17UtilityTools:
    """Utility tool implementations for Odoo 17 MCP server."""

    async def _odoo_shell(self, code: str, database: str) -> CallToolResult:
        """Execute Python code in Odoo shell environment."""
        
        try:
            # Create temporary script file
            script_content = f'''
# Odoo Shell Execution Script
# Database: {database}
# Timestamp: {datetime.now()}

# Your code:
{code}
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Execute in Odoo shell
                cmd = [
                    'docker-compose', 'exec', '-T', 'odoo', 
                    'odoo', 'shell', '-d', database, '--shell-interface', 'ipython'
                ]
                
                # Pass code via stdin
                process = subprocess.Popen(
                    cmd, 
                    stdin=subprocess.PIPE, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                
                stdout, stderr = process.communicate(input=code, timeout=60)
                
                result_text = f"🐍 Odoo Shell Execution Results\\n\\n"
                result_text += f"📋 **Details:**\\n"
                result_text += f"  • Database: {database}\\n"
                result_text += f"  • Exit Code: {process.returncode}\\n"
                result_text += f"  • Execution Time: {datetime.now()}\\n\\n"
                
                result_text += f"📝 **Code Executed:**\\n"
                result_text += f"```python\\n{code}\\n```\\n\\n"
                
                if process.returncode == 0:
                    result_text += f"✅ **Execution Successful**\\n\\n"
                    if stdout.strip():
                        result_text += f"📤 **Output:**\\n"
                        result_text += f"```\\n{stdout}\\n```\\n\\n"
                else:
                    result_text += f"❌ **Execution Failed**\\n\\n"
                    if stderr.strip():
                        result_text += f"💥 **Error:**\\n"
                        result_text += f"```\\n{stderr}\\n```\\n\\n"
                    if stdout.strip():
                        result_text += f"📤 **Output:**\\n"
                        result_text += f"```\\n{stdout}\\n```\\n\\n"
                
                result_text += f"💡 **Tips:**\\n"
                result_text += f"- Use `env['model.name']` to access models\\n"
                result_text += f"- Use `env.user` to get current user\\n"
                result_text += f"- Use `env.cr.commit()` to commit changes\\n"
                result_text += f"- Use `print()` to output results\\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
            finally:
                # Clean up temporary file
                os.unlink(script_path)
                
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text=f"⏱️ Odoo shell execution timed out after 60 seconds")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error executing Odoo shell: {str(e)}")]
            )

    async def _check_odoo_logs(self, log_file: str = "/var/log/odoo/odoo.log", 
                              level: str = "ERROR", lines: int = 100) -> CallToolResult:
        """Analyze Odoo log files for errors and warnings."""
        
        try:
            # If using Docker, get logs from container
            if not Path(log_file).exists():
                # Try to get logs from Docker container
                cmd = ['docker-compose', 'logs', '--tail', str(lines), 'odoo']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ Could not access logs: {result.stderr}")]
                    )
                
                log_content = result.stdout
            else:
                # Read from log file
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    log_content = ''.join(all_lines[-lines:])  # Get last N lines
            
            # Parse log entries
            log_entries = {
                'ERROR': [],
                'WARNING': [],
                'INFO': [],
                'DEBUG': [],
                'CRITICAL': []
            }
            
            # Regular expressions for log parsing
            log_pattern = re.compile(
                r'(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}),\\d{3}\\s+(\\d+)\\s+(\\w+)\\s+([^:]+):\\s*(.*)'
            )
            
            lines_analyzed = log_content.split('\\n')
            
            for line in lines_analyzed:
                match = log_pattern.match(line.strip())
                if match:
                    timestamp, pid, log_level, module, message = match.groups()
                    
                    if log_level in log_entries:
                        log_entries[log_level].append({
                            'timestamp': timestamp,
                            'pid': pid,
                            'module': module,
                            'message': message.strip()
                        })
            
            # Filter by requested level
            level_priority = {
                'DEBUG': 0,
                'INFO': 1,
                'WARNING': 2,
                'ERROR': 3,
                'CRITICAL': 4
            }
            
            min_priority = level_priority.get(level, 2)
            filtered_entries = []
            
            for log_level, entries in log_entries.items():
                if level_priority.get(log_level, 0) >= min_priority:
                    filtered_entries.extend([(log_level, entry) for entry in entries])
            
            # Sort by timestamp
            filtered_entries.sort(key=lambda x: x[1]['timestamp'], reverse=True)
            
            # Generate result
            result_text = f"📋 Odoo Log Analysis Results\\n\\n"
            result_text += f"🔍 **Analysis Details:**\\n"
            result_text += f"  • Log Source: {'Docker Container' if not Path(log_file).exists() else log_file}\\n"
            result_text += f"  • Lines Analyzed: {len(lines_analyzed)}\\n"
            result_text += f"  • Minimum Level: {level}\\n"
            result_text += f"  • Entries Found: {len(filtered_entries)}\\n\\n"
            
            # Summary by level
            result_text += f"📊 **Summary by Level:**\\n"
            for log_level, entries in log_entries.items():
                count = len(entries)
                if count > 0:
                    emoji = {
                        'CRITICAL': '🔴',
                        'ERROR': '❌', 
                        'WARNING': '⚠️',
                        'INFO': 'ℹ️',
                        'DEBUG': '🔍'
                    }.get(log_level, '📝')
                    result_text += f"  {emoji} {log_level}: {count}\\n"
            result_text += "\\n"
            
            # Show recent entries
            if filtered_entries:
                result_text += f"🕒 **Recent Entries (Last 20):**\\n\\n"
                
                for log_level, entry in filtered_entries[:20]:
                    emoji = {
                        'CRITICAL': '🔴',
                        'ERROR': '❌', 
                        'WARNING': '⚠️',
                        'INFO': 'ℹ️',
                        'DEBUG': '🔍'
                    }.get(log_level, '📝')
                    
                    result_text += f"{emoji} **{log_level}** | {entry['timestamp']} | {entry['module']}\\n"
                    result_text += f"   {entry['message'][:200]}{'...' if len(entry['message']) > 200 else ''}\\n\\n"
            
            # Error pattern analysis
            if log_entries['ERROR'] or log_entries['CRITICAL']:
                error_patterns = {}
                all_errors = log_entries['ERROR'] + log_entries['CRITICAL']
                
                for error in all_errors:
                    # Extract error type
                    message = error['message']
                    if ':' in message:
                        error_type = message.split(':')[0]
                        error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                
                if error_patterns:
                    result_text += f"🔍 **Common Error Patterns:**\\n"
                    for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
                        result_text += f"  • {pattern}: {count} occurrences\\n"
                    result_text += "\\n"
            
            # Recommendations
            result_text += f"💡 **Recommendations:**\\n"
            
            if log_entries['CRITICAL']:
                result_text += f"🔴 **CRITICAL**: {len(log_entries['CRITICAL'])} critical errors need immediate attention\\n"
            
            if log_entries['ERROR']:
                result_text += f"❌ **ERRORS**: {len(log_entries['ERROR'])} errors should be investigated\\n"
            
            if log_entries['WARNING']:
                result_text += f"⚠️ **WARNINGS**: {len(log_entries['WARNING'])} warnings may indicate potential issues\\n"
            
            result_text += f"- Monitor logs regularly for recurring issues\\n"
            result_text += f"- Set up log rotation to prevent disk space issues\\n"
            result_text += f"- Use log aggregation tools for better analysis\\n"
            result_text += f"- Configure log levels appropriately for production\\n"
            
            # Quick commands
            result_text += f"\\n🚀 **Quick Commands:**\\n"
            result_text += f"```bash\\n"
            result_text += f"# Follow logs in real-time\\n"
            result_text += f"docker-compose logs -f odoo\\n\\n"
            result_text += f"# Filter by error level\\n"
            result_text += f"docker-compose logs odoo | grep ERROR\\n\\n"
            result_text += f"# Save logs to file\\n"
            result_text += f"docker-compose logs odoo > odoo_logs.txt\\n"
            result_text += f"```"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error analyzing logs: {str(e)}")]
            )

    async def _check_module_health(self, module_path: str) -> CallToolResult:
        """Comprehensive health check for Odoo module."""
        
        try:
            module_path = Path(module_path)
            
            if not module_path.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Module path not found: {module_path}")]
                )
            
            health_report = {
                'structure': {'score': 0, 'max_score': 0, 'issues': []},
                'syntax': {'errors': [], 'warnings': []},
                'dependencies': {'missing': [], 'circular': []},
                'security': {'issues': [], 'suggestions': []},
                'performance': {'issues': [], 'suggestions': []},
                'best_practices': {'violations': [], 'recommendations': []}
            }
            
            # 1. Structure Check
            required_files = ['__init__.py', '__manifest__.py']
            recommended_dirs = ['models', 'views', 'security']
            
            for file in required_files:
                if (module_path / file).exists():
                    health_report['structure']['score'] += 1
                else:
                    health_report['structure']['issues'].append(f"Missing required file: {file}")
                health_report['structure']['max_score'] += 1
            
            for dir in recommended_dirs:
                if (module_path / dir).exists():
                    health_report['structure']['score'] += 1
                else:
                    health_report['structure']['issues'].append(f"Missing recommended directory: {dir}")
                health_report['structure']['max_score'] += 1
            
            # 2. Syntax Check
            python_files = list(module_path.rglob('*.py'))
            xml_files = list(module_path.rglob('*.xml'))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(py_file), 'exec')
                except SyntaxError as e:
                    health_report['syntax']['errors'].append(f"{py_file.name}: {str(e)}")
                except Exception as e:
                    health_report['syntax']['warnings'].append(f"{py_file.name}: {str(e)}")
            
            # 3. Dependency Check
            manifest_file = module_path / '__manifest__.py'
            if manifest_file.exists():
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    namespace = {}
                    exec(content, namespace)
                    
                    manifest = None
                    for key, value in namespace.items():
                        if isinstance(value, dict) and 'depends' in value:
                            manifest = value
                            break
                    
                    if manifest and 'depends' in manifest:
                        # Check for common missing dependencies
                        depends = manifest['depends']
                        if 'models' in [d.name for d in module_path.iterdir() if d.is_dir()]:
                            if 'base' not in depends:
                                health_report['dependencies']['missing'].append("'base' dependency missing")
                                
                except Exception as e:
                    health_report['syntax']['errors'].append(f"__manifest__.py: {str(e)}")
            
            # 4. Security Check
            security_dir = module_path / 'security'
            if not security_dir.exists() and (module_path / 'models').exists():
                health_report['security']['issues'].append("No security directory found")
            else:
                access_file = security_dir / 'ir.model.access.csv'
                if not access_file.exists():
                    health_report['security']['issues'].append("No ir.model.access.csv found")
            
            # 5. Performance Check
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for performance anti-patterns
                    if 'search([])' in content:
                        health_report['performance']['issues'].append(f"{py_file.name}: Unbounded search() call")
                    
                    if re.search(r'for.*in.*search\\(', content):
                        health_report['performance']['issues'].append(f"{py_file.name}: Loop with search() - consider search_read()")
                        
                except Exception:
                    pass
            
            # 6. Best Practices Check
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for best practice violations
                    if not content.startswith('# -*- coding: utf-8 -*-'):
                        health_report['best_practices']['violations'].append(f"{py_file.name}: Missing encoding declaration")
                    
                    if 'class ' in content and '@api.' not in content:
                        health_report['best_practices']['recommendations'].append(f"{py_file.name}: Consider using @api decorators")
                        
                except Exception:
                    pass
            
            # Generate health score
            total_issues = (
                len(health_report['structure']['issues']) +
                len(health_report['syntax']['errors']) +
                len(health_report['dependencies']['missing']) +
                len(health_report['security']['issues']) +
                len(health_report['performance']['issues']) +
                len(health_report['best_practices']['violations'])
            )
            
            structure_score = (health_report['structure']['score'] / health_report['structure']['max_score'] * 100) if health_report['structure']['max_score'] > 0 else 0
            
            overall_health = max(0, min(100, structure_score - (total_issues * 5)))
            
            # Generate result
            result_text = f"🏥 Module Health Check: {module_path.name}\\n\\n"
            
            # Health score with emoji
            if overall_health >= 90:
                health_emoji = "💚"
                health_status = "Excellent"
            elif overall_health >= 70:
                health_emoji = "💛" 
                health_status = "Good"
            elif overall_health >= 50:
                health_emoji = "🧡"
                health_status = "Fair"
            else:
                health_emoji = "❤️"
                health_status = "Poor"
            
            result_text += f"{health_emoji} **Overall Health: {overall_health:.1f}% ({health_status})**\\n\\n"
            
            # Structure Report
            result_text += f"🏗️ **Structure ({health_report['structure']['score']}/{health_report['structure']['max_score']}):**\\n"
            if health_report['structure']['issues']:
                for issue in health_report['structure']['issues']:
                    result_text += f"  ❌ {issue}\\n"
            else:
                result_text += f"  ✅ All required files and directories present\\n"
            result_text += "\\n"
            
            # Syntax Report
            if health_report['syntax']['errors'] or health_report['syntax']['warnings']:
                result_text += f"🐍 **Syntax Issues:**\\n"
                for error in health_report['syntax']['errors']:
                    result_text += f"  ❌ {error}\\n"
                for warning in health_report['syntax']['warnings']:
                    result_text += f"  ⚠️ {warning}\\n"
                result_text += "\\n"
            else:
                result_text += f"✅ **Syntax**: No issues found\\n\\n"
            
            # Dependencies Report
            if health_report['dependencies']['missing']:
                result_text += f"📦 **Dependencies:**\\n"
                for dep in health_report['dependencies']['missing']:
                    result_text += f"  ❌ {dep}\\n"
                result_text += "\\n"
            else:
                result_text += f"✅ **Dependencies**: No issues found\\n\\n"
            
            # Security Report
            if health_report['security']['issues']:
                result_text += f"🔒 **Security:**\\n"
                for issue in health_report['security']['issues']:
                    result_text += f"  ⚠️ {issue}\\n"
                result_text += "\\n"
            else:
                result_text += f"✅ **Security**: No issues found\\n\\n"
            
            # Performance Report
            if health_report['performance']['issues']:
                result_text += f"⚡ **Performance:**\\n"
                for issue in health_report['performance']['issues']:
                    result_text += f"  ⚠️ {issue}\\n"
                result_text += "\\n"
            else:
                result_text += f"✅ **Performance**: No issues found\\n\\n"
            
            # Best Practices Report
            if health_report['best_practices']['violations'] or health_report['best_practices']['recommendations']:
                result_text += f"🎯 **Best Practices:**\\n"
                for violation in health_report['best_practices']['violations']:
                    result_text += f"  ❌ {violation}\\n"
                for rec in health_report['best_practices']['recommendations']:
                    result_text += f"  💡 {rec}\\n"
                result_text += "\\n"
            else:
                result_text += f"✅ **Best Practices**: Following Odoo standards\\n\\n"
            
            # Improvement suggestions
            result_text += f"🚀 **Improvement Suggestions:**\\n"
            if overall_health < 70:
                result_text += f"1. Fix critical syntax and structure issues first\\n"
                result_text += f"2. Add missing security configurations\\n"
                result_text += f"3. Review and optimize performance bottlenecks\\n"
                result_text += f"4. Follow Odoo coding standards and best practices\\n"
            else:
                result_text += f"1. Continue following best practices\\n"
                result_text += f"2. Add comprehensive tests\\n"
                result_text += f"3. Consider adding documentation\\n"
                result_text += f"4. Monitor performance in production\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error checking module health: {str(e)}")]
            )