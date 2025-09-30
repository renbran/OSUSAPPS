"""
Odoo 17 MCP Server - Additional Tool Implementations

This module contains the remaining tool implementations for Docker operations,
code quality checks, database management, testing, and deployment tools.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
import psycopg2
import csv
import io

from mcp.types import CallToolResult, TextContent


class Odoo17AdditionalTools:
    """Additional tool implementations for Odoo 17 MCP server."""

    async def _validate_module_manifest(self, module_path: str) -> CallToolResult:
        """Validate Odoo module manifest file for Odoo 17 compatibility."""
        
        try:
            module_path = Path(module_path)
            manifest_file = module_path / "__manifest__.py"
            
            if not manifest_file.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Manifest file not found: {manifest_file}")]
                )
            
            # Read and validate manifest
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax check
                compile(content, str(manifest_file), 'exec')
                
                # Execute to get manifest dict
                namespace = {}
                exec(content, namespace)
                
                # Find the manifest dictionary
                manifest = None
                for key, value in namespace.items():
                    if isinstance(value, dict) and 'name' in value:
                        manifest = value
                        break
                
                if not manifest:
                    return CallToolResult(
                        content=[TextContent(type="text", text="❌ No manifest dictionary found in __manifest__.py")]
                    )
                
                # Validation checks
                issues = []
                warnings = []
                
                # Required fields
                required_fields = ['name', 'version', 'depends', 'data', 'installable']
                for field in required_fields:
                    if field not in manifest:
                        issues.append(f"Missing required field: '{field}'")
                
                # Version format check
                if 'version' in manifest:
                    version = manifest['version']
                    if not version.startswith('17.0'):
                        warnings.append(f"Version should start with '17.0', found: '{version}'")
                
                # Dependencies check
                if 'depends' in manifest:
                    depends = manifest['depends']
                    if not isinstance(depends, list):
                        issues.append("'depends' should be a list")
                    elif len(depends) == 0:
                        warnings.append("'depends' is empty, consider adding 'base'")
                
                # Data files check
                if 'data' in manifest:
                    data_files = manifest['data']
                    if isinstance(data_files, list):
                        for data_file in data_files:
                            file_path = module_path / data_file
                            if not file_path.exists():
                                issues.append(f"Data file not found: {data_file}")
                
                # Installable check
                if manifest.get('installable', True) is False:
                    warnings.append("Module is marked as not installable")
                
                # License check
                if 'license' not in manifest:
                    warnings.append("License field is missing")
                elif manifest['license'] not in ['LGPL-3', 'AGPL-3', 'GPL-3', 'MIT', 'BSD-2-Clause']:
                    warnings.append(f"Uncommon license: {manifest['license']}")
                
                # Generate result
                result_text = f"✅ Manifest validation for: {module_path.name}\\n\\n"
                result_text += f"📋 Module Info:\\n"
                result_text += f"- Name: {manifest.get('name', 'N/A')}\\n"
                result_text += f"- Version: {manifest.get('version', 'N/A')}\\n"
                result_text += f"- Author: {manifest.get('author', 'N/A')}\\n"
                result_text += f"- License: {manifest.get('license', 'N/A')}\\n"
                result_text += f"- Depends: {', '.join(manifest.get('depends', []))}\\n\\n"
                
                if issues:
                    result_text += "❌ Issues Found:\\n"
                    for issue in issues:
                        result_text += f"  • {issue}\\n"
                    result_text += "\\n"
                
                if warnings:
                    result_text += "⚠️ Warnings:\\n"
                    for warning in warnings:
                        result_text += f"  • {warning}\\n"
                    result_text += "\\n"
                
                if not issues and not warnings:
                    result_text += "✅ All checks passed!\\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
            except SyntaxError as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Syntax error in manifest: {str(e)}")]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error validating manifest: {str(e)}")]
            )

    async def _analyze_module_structure(self, module_path: str) -> CallToolResult:
        """Analyze Odoo module structure and provide recommendations."""
        
        try:
            module_path = Path(module_path)
            
            if not module_path.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Module path not found: {module_path}")]
                )
            
            analysis = {
                'files_found': [],
                'missing_files': [],
                'recommendations': [],
                'file_counts': {},
                'structure_score': 0
            }
            
            # Expected structure for Odoo 17
            expected_structure = {
                '__init__.py': 'required',
                '__manifest__.py': 'required',
                'models/': 'recommended',
                'views/': 'recommended',
                'security/': 'recommended',
                'static/src/js/': 'optional',
                'static/src/css/': 'optional',
                'static/src/xml/': 'optional',
                'data/': 'optional',
                'demo/': 'optional',
                'tests/': 'recommended',
                'controllers/': 'optional',
                'wizards/': 'optional',
                'reports/': 'optional',
                'README.md': 'recommended'
            }
            
            # Check for expected files/directories
            max_score = len([k for k, v in expected_structure.items() if v in ['required', 'recommended']])
            
            for item, importance in expected_structure.items():
                item_path = module_path / item
                exists = item_path.exists()
                
                if exists:
                    analysis['files_found'].append(item)
                    if importance in ['required', 'recommended']:
                        analysis['structure_score'] += 1
                else:
                    if importance == 'required':
                        analysis['missing_files'].append(f"{item} (REQUIRED)")
                    elif importance == 'recommended':
                        analysis['missing_files'].append(f"{item} (recommended)")
            
            # Count files in key directories
            for dir_name in ['models', 'views', 'security', 'static', 'data', 'tests']:
                dir_path = module_path / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    file_count = len(list(dir_path.rglob('*.py'))) + len(list(dir_path.rglob('*.xml'))) + len(list(dir_path.rglob('*.csv')))
                    analysis['file_counts'][dir_name] = file_count
            
            # Generate recommendations
            if 'models/' not in analysis['files_found']:
                analysis['recommendations'].append("Add models/ directory for data models")
            
            if 'views/' not in analysis['files_found']:
                analysis['recommendations'].append("Add views/ directory for UI definitions")
            
            if 'security/' not in analysis['files_found']:
                analysis['recommendations'].append("Add security/ directory with access rights")
            
            if 'tests/' not in analysis['files_found']:
                analysis['recommendations'].append("Add tests/ directory for unit tests")
            
            if 'README.md' not in analysis['files_found']:
                analysis['recommendations'].append("Add README.md for documentation")
            
            # Check for common anti-patterns
            python_files = list(module_path.rglob('*.py'))
            xml_files = list(module_path.rglob('*.xml'))
            
            if len(python_files) > 20:
                analysis['recommendations'].append("Consider splitting large modules into smaller ones")
            
            if len(xml_files) == 0:
                analysis['recommendations'].append("No XML files found - consider adding views or data files")
            
            # Security check
            security_csv = module_path / 'security' / 'ir.model.access.csv'
            if not security_csv.exists() and (module_path / 'models').exists():
                analysis['recommendations'].append("Add ir.model.access.csv for model permissions")
            
            # Calculate final score
            score_percentage = (analysis['structure_score'] / max_score * 100) if max_score > 0 else 0
            
            # Generate result
            result_text = f"📁 Module Structure Analysis: {module_path.name}\\n\\n"
            result_text += f"📊 Structure Score: {analysis['structure_score']}/{max_score} ({score_percentage:.1f}%)\\n\\n"
            
            result_text += "✅ Files Found:\\n"
            for file in analysis['files_found']:
                result_text += f"  • {file}\\n"
            result_text += "\\n"
            
            if analysis['missing_files']:
                result_text += "❌ Missing Files:\\n"
                for file in analysis['missing_files']:
                    result_text += f"  • {file}\\n"
                result_text += "\\n"
            
            if analysis['file_counts']:
                result_text += "📈 File Counts:\\n"
                for directory, count in analysis['file_counts'].items():
                    result_text += f"  • {directory}: {count} files\\n"
                result_text += "\\n"
            
            if analysis['recommendations']:
                result_text += "💡 Recommendations:\\n"
                for recommendation in analysis['recommendations']:
                    result_text += f"  • {recommendation}\\n"
                result_text += "\\n"
            
            # Overall assessment
            if score_percentage >= 90:
                result_text += "🌟 Excellent module structure!"
            elif score_percentage >= 70:
                result_text += "👍 Good module structure with minor improvements needed"
            elif score_percentage >= 50:
                result_text += "⚠️ Acceptable structure but several improvements recommended"
            else:
                result_text += "❌ Poor structure - significant improvements needed"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error analyzing module structure: {str(e)}")]
            )

    async def _docker_odoo_status(self, compose_file: str = "./docker-compose.yml") -> CallToolResult:
        """Check status of Odoo Docker containers."""
        
        try:
            if not Path(compose_file).exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Docker Compose file not found: {compose_file}")]
                )
            
            # Get container status
            result = subprocess.run(['docker-compose', '-f', compose_file, 'ps'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Error running docker-compose ps: {result.stderr}")]
                )
            
            # Parse output
            lines = result.stdout.strip().split('\\n')
            if len(lines) <= 1:
                return CallToolResult(
                    content=[TextContent(type="text", text="❌ No containers found or docker-compose not running")]
                )
            
            # Get detailed status for each service
            services_info = []
            
            # Get service names
            services_result = subprocess.run(['docker-compose', '-f', compose_file, 'config', '--services'], 
                                           capture_output=True, text=True)
            
            if services_result.returncode == 0:
                services = services_result.stdout.strip().split('\\n')
                
                for service in services:
                    if service:  # Skip empty lines
                        # Get service status
                        service_result = subprocess.run(
                            ['docker-compose', '-f', compose_file, 'ps', '-q', service],
                            capture_output=True, text=True
                        )
                        
                        if service_result.stdout.strip():
                            container_id = service_result.stdout.strip()
                            
                            # Get container details
                            inspect_result = subprocess.run(
                                ['docker', 'inspect', '--format', '{{.State.Status}}|{{.State.Health.Status}}|{{.Config.Image}}', container_id],
                                capture_output=True, text=True
                            )
                            
                            if inspect_result.returncode == 0:
                                parts = inspect_result.stdout.strip().split('|')
                                status = parts[0] if len(parts) > 0 else 'unknown'
                                health = parts[1] if len(parts) > 1 and parts[1] != '<no value>' else 'no healthcheck'
                                image = parts[2] if len(parts) > 2 else 'unknown'
                                
                                services_info.append({
                                    'service': service,
                                    'container_id': container_id[:12],
                                    'status': status,
                                    'health': health,
                                    'image': image
                                })
                        else:
                            services_info.append({
                                'service': service,
                                'container_id': 'N/A',
                                'status': 'not running',
                                'health': 'N/A',
                                'image': 'N/A'
                            })
            
            # Generate result
            result_text = "🐳 Docker Odoo Services Status\\n\\n"
            
            if services_info:
                result_text += "📋 Services:\\n"
                for service_info in services_info:
                    status_emoji = "✅" if service_info['status'] == 'running' else "❌"
                    health_emoji = "💚" if service_info['health'] == 'healthy' else "🔄" if service_info['health'] == 'starting' else "⚠️"
                    
                    result_text += f"{status_emoji} **{service_info['service']}**\\n"
                    result_text += f"   Container: {service_info['container_id']}\\n"
                    result_text += f"   Status: {service_info['status']}\\n"
                    result_text += f"   Health: {health_emoji} {service_info['health']}\\n"
                    result_text += f"   Image: {service_info['image']}\\n\\n"
            else:
                result_text += "❌ No services found\\n"
            
            # Add quick commands
            result_text += "🚀 Quick Commands:\\n"
            result_text += f"   Start all: `docker-compose -f {compose_file} up -d`\\n"
            result_text += f"   Stop all: `docker-compose -f {compose_file} down`\\n"
            result_text += f"   Restart: `docker-compose -f {compose_file} restart`\\n"
            result_text += f"   Logs: `docker-compose -f {compose_file} logs -f odoo`\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except FileNotFoundError:
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Docker or docker-compose not found. Please install Docker.")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error checking Docker status: {str(e)}")]
            )

    async def _docker_odoo_logs(self, service: str = "odoo", lines: int = 50, follow: bool = False) -> CallToolResult:
        """Get logs from Odoo Docker container."""
        
        try:
            cmd = ['docker-compose', 'logs']
            
            if not follow:
                cmd.extend(['--tail', str(lines)])
            else:
                cmd.append('-f')
            
            cmd.append(service)
            
            if follow:
                # For follow mode, we'll get initial logs only
                result = subprocess.run(cmd + ['--tail', str(lines)], 
                                      capture_output=True, text=True, timeout=5)
                
                logs = result.stdout if result.returncode == 0 else result.stderr
                
                result_text = f"📋 Last {lines} log entries from {service} (use --follow for real-time):\\n\\n"
                result_text += f"```\\n{logs}\\n```\\n\\n"
                result_text += f"💡 To follow logs in real-time, run:\\n"
                result_text += f"`docker-compose logs -f {service}`"
                
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"❌ Error getting logs: {result.stderr}")]
                    )
                
                logs = result.stdout
                result_text = f"📋 Last {lines} log entries from {service}:\\n\\n"
                result_text += f"```\\n{logs}\\n```"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text=f"⏱️ Timeout getting logs from {service}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error getting logs: {str(e)}")]
            )

    async def _docker_odoo_restart(self, service: str = "odoo") -> CallToolResult:
        """Restart Odoo Docker services."""
        
        try:
            if service == "all":
                cmd = ['docker-compose', 'restart']
                message = "all services"
            else:
                cmd = ['docker-compose', 'restart', service]
                message = f"service '{service}'"
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Error restarting {message}: {result.stderr}")]
                )
            
            result_text = f"✅ Successfully restarted {message}\\n\\n"
            
            # Check status after restart
            status_result = await self._docker_odoo_status()
            result_text += status_result.content[0].text
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error restarting service: {str(e)}")]
            )

    async def _docker_odoo_shell(self, command: str, service: str = "odoo") -> CallToolResult:
        """Execute commands in Odoo Docker container."""
        
        try:
            cmd = ['docker-compose', 'exec', '-T', service, 'bash', '-c', command]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            output = result.stdout
            error = result.stderr
            
            result_text = f"🐳 Executed in {service} container: `{command}`\\n\\n"
            
            if result.returncode == 0:
                result_text += "✅ Success\\n\\n"
                if output:
                    result_text += "**Output:**\\n```\\n" + output + "\\n```\\n"
            else:
                result_text += f"❌ Failed (exit code: {result.returncode})\\n\\n"
                if error:
                    result_text += "**Error:**\\n```\\n" + error + "\\n```\\n"
                if output:
                    result_text += "**Output:**\\n```\\n" + output + "\\n```\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text=f"⏱️ Command timed out after 30 seconds: {command}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error executing command: {str(e)}")]
            )

    async def _lint_python_code(self, path: str, tool: str = "both", fix: bool = False) -> CallToolResult:
        """Run Python linting tools (flake8, pylint) on Odoo modules."""
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Path not found: {path}")]
                )
            
            results = []
            
            # Run flake8
            if tool in ["flake8", "both"]:
                try:
                    flake8_cmd = ['flake8', '--max-line-length=88', '--extend-ignore=E203,W503', str(path_obj)]
                    flake8_result = subprocess.run(flake8_cmd, capture_output=True, text=True)
                    
                    results.append({
                        'tool': 'flake8',
                        'returncode': flake8_result.returncode,
                        'output': flake8_result.stdout,
                        'error': flake8_result.stderr
                    })
                except FileNotFoundError:
                    results.append({
                        'tool': 'flake8',
                        'returncode': -1,
                        'output': '',
                        'error': 'flake8 not installed'
                    })
            
            # Run pylint
            if tool in ["pylint", "both"]:
                try:
                    pylint_cmd = ['pylint', '--disable=C0114,C0115,C0116', '--output-format=text', str(path_obj)]
                    pylint_result = subprocess.run(pylint_cmd, capture_output=True, text=True)
                    
                    results.append({
                        'tool': 'pylint',
                        'returncode': pylint_result.returncode,
                        'output': pylint_result.stdout,
                        'error': pylint_result.stderr
                    })
                except FileNotFoundError:
                    results.append({
                        'tool': 'pylint',
                        'returncode': -1,
                        'output': '',
                        'error': 'pylint not installed'
                    })
            
            # Auto-fix with autopep8 if requested
            if fix:
                try:
                    autopep8_cmd = ['autopep8', '--in-place', '--aggressive', '--aggressive', str(path_obj)]
                    if path_obj.is_dir():
                        autopep8_cmd.extend(['--recursive'])
                    
                    autopep8_result = subprocess.run(autopep8_cmd, capture_output=True, text=True)
                    
                    results.append({
                        'tool': 'autopep8',
                        'returncode': autopep8_result.returncode,
                        'output': autopep8_result.stdout,
                        'error': autopep8_result.stderr
                    })
                except FileNotFoundError:
                    results.append({
                        'tool': 'autopep8',
                        'returncode': -1,
                        'output': '',
                        'error': 'autopep8 not installed'
                    })
            
            # Generate result
            result_text = f"🔍 Python Code Linting Results for: {path}\\n\\n"
            
            for result in results:
                tool_name = result['tool']
                if result['returncode'] == -1:
                    result_text += f"❌ {tool_name.upper()}: {result['error']}\\n"
                    result_text += f"   Install with: pip install {tool_name}\\n\\n"
                elif result['returncode'] == 0:
                    result_text += f"✅ {tool_name.upper()}: No issues found\\n\\n"
                else:
                    result_text += f"⚠️ {tool_name.upper()}: Issues found\\n"
                    if result['output']:
                        result_text += f"```\\n{result['output']}\\n```\\n\\n"
            
            if fix:
                result_text += "🔧 Auto-fix completed with autopep8\\n"
            
            # Add recommendations
            result_text += "💡 **Recommendations:**\\n"
            result_text += "- Install missing linting tools: `pip install flake8 pylint autopep8`\\n"
            result_text += "- Use `--fix` parameter to auto-fix common issues\\n"
            result_text += "- Consider adding pre-commit hooks for automatic linting\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error running linting: {str(e)}")]
            )

    async def _format_python_code(self, path: str, check_only: bool = False) -> CallToolResult:
        """Format Python code using black and isort."""
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Path not found: {path}")]
                )
            
            results = []
            
            # Run black
            try:
                black_cmd = ['black']
                if check_only:
                    black_cmd.append('--check')
                black_cmd.extend(['--line-length', '88', str(path_obj)])
                
                black_result = subprocess.run(black_cmd, capture_output=True, text=True)
                
                results.append({
                    'tool': 'black',
                    'returncode': black_result.returncode,
                    'output': black_result.stdout,
                    'error': black_result.stderr
                })
            except FileNotFoundError:
                results.append({
                    'tool': 'black',
                    'returncode': -1,
                    'output': '',
                    'error': 'black not installed'
                })
            
            # Run isort
            try:
                isort_cmd = ['isort']
                if check_only:
                    isort_cmd.append('--check-only')
                isort_cmd.extend(['--profile', 'black', str(path_obj)])
                
                isort_result = subprocess.run(isort_cmd, capture_output=True, text=True)
                
                results.append({
                    'tool': 'isort',
                    'returncode': isort_result.returncode,
                    'output': isort_result.stdout,
                    'error': isort_result.stderr
                })
            except FileNotFoundError:
                results.append({
                    'tool': 'isort',
                    'returncode': -1,
                    'output': '',
                    'error': 'isort not installed'
                })
            
            # Generate result
            mode = "checked" if check_only else "formatted"
            result_text = f"🎨 Python Code Formatting Results ({mode}): {path}\\n\\n"
            
            for result in results:
                tool_name = result['tool']
                if result['returncode'] == -1:
                    result_text += f"❌ {tool_name.upper()}: {result['error']}\\n"
                    result_text += f"   Install with: pip install {tool_name}\\n\\n"
                elif result['returncode'] == 0:
                    if check_only:
                        result_text += f"✅ {tool_name.upper()}: Code is properly formatted\\n\\n"
                    else:
                        result_text += f"✅ {tool_name.upper()}: Formatting completed\\n\\n"
                else:
                    if check_only:
                        result_text += f"⚠️ {tool_name.upper()}: Formatting issues found\\n"
                    else:
                        result_text += f"🔧 {tool_name.upper()}: Files were reformatted\\n"
                    
                    if result['output']:
                        result_text += f"```\\n{result['output']}\\n```\\n\\n"
            
            # Add recommendations
            result_text += "💡 **Recommendations:**\\n"
            result_text += "- Install formatters: `pip install black isort`\\n"
            result_text += "- Use `--check-only` to validate formatting without changes\\n"
            result_text += "- Add formatting to pre-commit hooks\\n"
            result_text += "- Configure your IDE to format on save\\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error formatting code: {str(e)}")]
            )

    async def _validate_xml_syntax(self, path: str) -> CallToolResult:
        """Validate XML files in Odoo modules."""
        
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ Path not found: {path}")]
                )
            
            xml_files = []
            
            if path_obj.is_file() and path_obj.suffix == '.xml':
                xml_files.append(path_obj)
            elif path_obj.is_dir():
                xml_files = list(path_obj.rglob('*.xml'))
            
            if not xml_files:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"❌ No XML files found in: {path}")]
                )
            
            results = {
                'valid': [],
                'invalid': [],
                'total': len(xml_files)
            }
            
            for xml_file in xml_files:
                try:
                    ET.parse(str(xml_file))
                    results['valid'].append(str(xml_file.relative_to(path_obj.parent if path_obj.is_file() else path_obj)))
                except ET.ParseError as e:
                    results['invalid'].append({
                        'file': str(xml_file.relative_to(path_obj.parent if path_obj.is_file() else path_obj)),
                        'error': str(e)
                    })
                except Exception as e:
                    results['invalid'].append({
                        'file': str(xml_file.relative_to(path_obj.parent if path_obj.is_file() else path_obj)),
                        'error': f"Unexpected error: {str(e)}"
                    })
            
            # Generate result
            result_text = f"📄 XML Validation Results for: {path}\\n\\n"
            result_text += f"📊 Summary: {len(results['valid'])}/{results['total']} files valid\\n\\n"
            
            if results['valid']:
                result_text += "✅ Valid Files:\\n"
                for file in results['valid'][:10]:  # Show first 10
                    result_text += f"  • {file}\\n"
                if len(results['valid']) > 10:
                    result_text += f"  ... and {len(results['valid']) - 10} more\\n"
                result_text += "\\n"
            
            if results['invalid']:
                result_text += "❌ Invalid Files:\\n"
                for file_error in results['invalid']:
                    result_text += f"  • {file_error['file']}\\n"
                    result_text += f"    Error: {file_error['error']}\\n"
                result_text += "\\n"
            
            # Overall status
            if not results['invalid']:
                result_text += "🎉 All XML files are valid!"
            else:
                result_text += f"⚠️ {len(results['invalid'])} files need attention"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error validating XML: {str(e)}")]
            )