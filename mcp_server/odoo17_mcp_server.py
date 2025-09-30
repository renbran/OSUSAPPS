#!/usr/bin/env python3
"""
Odoo 17 Development MCP Server

This MCP (Model Context Protocol) server provides comprehensive tools for Odoo 17 development,
including module scaffolding, Docker operations, code quality checks, database management,
testing, and deployment automation.

Features:
- Module scaffolding and validation
- Docker container management
- Code quality tools (flake8, pylint, black)
- PostgreSQL database operations
- Odoo testing framework integration
- CI/CD pipeline automation
- Report generation and analysis

Author: OSUSAPPS Development Team
License: LGPL-3
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import tempfile
import shutil
import yaml

# MCP Server imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest, 
    CallToolResult, 
    ListToolsRequest, 
    TextContent, 
    Tool,
    JSONRPCError,
    INTERNAL_ERROR
)

# Import tool implementations
from tool_implementations import Odoo17ToolImplementations
from additional_tools import Odoo17AdditionalTools
from database_testing_tools import Odoo17DatabaseTools
from utility_tools import Odoo17UtilityTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("odoo17-mcp-server")

class Odoo17MCPServer:
    """Main MCP Server class for Odoo 17 development tools."""
    
    def __init__(self):
        self.server = Server("odoo17-dev-server")
        
        # Initialize tool implementation classes
        self.tool_impl = Odoo17ToolImplementations()
        self.additional_tools = Odoo17AdditionalTools()
        self.db_testing_tools = Odoo17DatabaseTools() 
        self.utility_tools = Odoo17UtilityTools()
        
        # Set logger reference
        self.tool_impl.logger = logger
        self.additional_tools.logger = logger
        self.db_testing_tools.logger = logger
        self.utility_tools.logger = logger
        
        self.setup_tools()
        
    def setup_tools(self):
        """Register all available tools with the MCP server."""
        
        # Module Management Tools
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
        
    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """List all available tools in the MCP server."""
        
        return [
            # Module Management
            Tool(
                name="scaffold_odoo_module",
                description="Create a new Odoo 17 module with proper structure, manifest, models, views, and security",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_name": {
                            "type": "string",
                            "description": "Name of the module (snake_case)"
                        },
                        "module_title": {
                            "type": "string", 
                            "description": "Human-readable module title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Module description"
                        },
                        "author": {
                            "type": "string",
                            "description": "Module author",
                            "default": "OSUSAPPS"
                        },
                        "website": {
                            "type": "string", 
                            "description": "Author website",
                            "default": "https://osusapps.com"
                        },
                        "depends": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of dependent modules",
                            "default": ["base"]
                        },
                        "include_models": {
                            "type": "boolean",
                            "description": "Include sample models",
                            "default": True
                        },
                        "include_views": {
                            "type": "boolean", 
                            "description": "Include sample views",
                            "default": True
                        },
                        "include_security": {
                            "type": "boolean",
                            "description": "Include security files", 
                            "default": True
                        },
                        "include_reports": {
                            "type": "boolean",
                            "description": "Include report templates",
                            "default": False
                        },
                        "include_controllers": {
                            "type": "boolean",
                            "description": "Include web controllers",
                            "default": False
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Output directory path",
                            "default": "."
                        }
                    },
                    "required": ["module_name", "module_title"]
                }
            ),
            
            Tool(
                name="validate_module_manifest",
                description="Validate Odoo module manifest file for Odoo 17 compatibility",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_path": {
                            "type": "string",
                            "description": "Path to the module directory"
                        }
                    },
                    "required": ["module_path"]
                }
            ),
            
            Tool(
                name="analyze_module_structure",
                description="Analyze Odoo module structure and provide recommendations",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "module_path": {
                            "type": "string",
                            "description": "Path to the module directory"
                        }
                    },
                    "required": ["module_path"]
                }
            ),
            
            # Docker Management Tools
            Tool(
                name="docker_odoo_status",
                description="Check status of Odoo Docker containers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "compose_file": {
                            "type": "string",
                            "description": "Path to docker-compose.yml file",
                            "default": "./docker-compose.yml"
                        }
                    }
                }
            ),
            
            Tool(
                name="docker_odoo_logs",
                description="Get logs from Odoo Docker container",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string", 
                            "description": "Docker service name",
                            "default": "odoo"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of log lines to retrieve",
                            "default": 50
                        },
                        "follow": {
                            "type": "boolean",
                            "description": "Follow logs in real-time",
                            "default": False
                        }
                    }
                }
            ),
            
            Tool(
                name="docker_odoo_restart",
                description="Restart Odoo Docker services",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service to restart (odoo, db, all)",
                            "default": "odoo"
                        }
                    }
                }
            ),
            
            Tool(
                name="docker_odoo_shell",
                description="Execute commands in Odoo Docker container",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute"
                        },
                        "service": {
                            "type": "string",
                            "description": "Docker service name",
                            "default": "odoo"
                        }
                    },
                    "required": ["command"]
                }
            ),
            
            # Code Quality Tools
            Tool(
                name="lint_python_code",
                description="Run Python linting tools (flake8, pylint) on Odoo modules",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to lint (file or directory)"
                        },
                        "tool": {
                            "type": "string",
                            "enum": ["flake8", "pylint", "both"],
                            "description": "Linting tool to use",
                            "default": "both"
                        },
                        "fix": {
                            "type": "boolean",
                            "description": "Attempt to auto-fix issues",
                            "default": False
                        }
                    },
                    "required": ["path"]
                }
            ),
            
            Tool(
                name="format_python_code", 
                description="Format Python code using black and isort",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to format (file or directory)"
                        },
                        "check_only": {
                            "type": "boolean",
                            "description": "Only check formatting, don't modify files",
                            "default": False
                        }
                    },
                    "required": ["path"]
                }
            ),
            
            Tool(
                name="validate_xml_syntax",
                description="Validate XML files in Odoo modules",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to validate (file or directory)"
                        }
                    },
                    "required": ["path"]
                }
            ),
            
            # Database Management Tools
            Tool(
                name="db_backup",
                description="Create backup of Odoo PostgreSQL database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "description": "Database name to backup"
                        },
                        "output_file": {
                            "type": "string", 
                            "description": "Output backup file path"
                        },
                        "compress": {
                            "type": "boolean",
                            "description": "Compress backup file",
                            "default": True
                        }
                    },
                    "required": ["database"]
                }
            ),
            
            Tool(
                name="db_restore", 
                description="Restore Odoo PostgreSQL database from backup",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "description": "Target database name"
                        },
                        "backup_file": {
                            "type": "string",
                            "description": "Backup file to restore from"
                        },
                        "drop_existing": {
                            "type": "boolean", 
                            "description": "Drop existing database if exists",
                            "default": False
                        }
                    },
                    "required": ["database", "backup_file"]
                }
            ),
            
            Tool(
                name="db_query",
                description="Execute SQL query on Odoo database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "description": "Database name"
                        },
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["table", "json", "csv"],
                            "description": "Output format",
                            "default": "table"
                        }
                    },
                    "required": ["database", "query"]
                }
            ),
            
            # Testing Tools
            Tool(
                name="run_odoo_tests",
                description="Run Odoo module tests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string", 
                            "description": "Module name to test"
                        },
                        "database": {
                            "type": "string",
                            "description": "Test database name"
                        },
                        "test_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Test tags to run"
                        },
                        "coverage": {
                            "type": "boolean",
                            "description": "Generate coverage report",
                            "default": False
                        }
                    },
                    "required": ["module"]
                }
            ),
            
            Tool(
                name="generate_test_data",
                description="Generate test data for Odoo modules", 
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string",
                            "description": "Module name"
                        },
                        "model": {
                            "type": "string", 
                            "description": "Model to generate data for"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of records to generate",
                            "default": 10
                        }
                    },
                    "required": ["module", "model"]
                }
            ),
            
            # Deployment Tools
            Tool(
                name="deploy_module",
                description="Deploy Odoo module to server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_path": {
                            "type": "string",
                            "description": "Path to module directory"
                        },
                        "target": {
                            "type": "string",
                            "enum": ["local", "staging", "production"],
                            "description": "Deployment target",
                            "default": "local"
                        },
                        "update_mode": {
                            "type": "string",
                            "enum": ["install", "update", "upgrade"],
                            "description": "Module update mode",
                            "default": "update"
                        }
                    },
                    "required": ["module_path"]
                }
            ),
            
            Tool(
                name="generate_requirements",
                description="Generate requirements.txt for Odoo module dependencies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_path": {
                            "type": "string", 
                            "description": "Path to module directory"
                        }
                    },
                    "required": ["module_path"]
                }
            ),
            
            # Utility Tools
            Tool(
                name="odoo_shell", 
                description="Execute Python code in Odoo shell environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute"
                        },
                        "database": {
                            "type": "string",
                            "description": "Database name"
                        }
                    },
                    "required": ["code", "database"]
                }
            ),
            
            Tool(
                name="check_odoo_logs",
                description="Analyze Odoo log files for errors and warnings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_file": {
                            "type": "string",
                            "description": "Path to log file",
                            "default": "/var/log/odoo/odoo.log"
                        },
                        "level": {
                            "type": "string",
                            "enum": ["ERROR", "WARNING", "INFO", "DEBUG"],
                            "description": "Minimum log level to show",
                            "default": "ERROR"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of recent lines to analyze",
                            "default": 100
                        }
                    }
                }
            ),
            
            Tool(
                name="check_module_health",
                description="Comprehensive health check for Odoo module including structure, syntax, security, and performance analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "module_path": {
                            "type": "string",
                            "description": "Path to the module directory"
                        }
                    },
                    "required": ["module_path"]
                }
            )
        ]

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool execution requests."""
        
        try:
            tool_name = request.params.name
            args = request.params.arguments or {}
            
            # Route to appropriate tool handler
            if tool_name == "scaffold_odoo_module":
                return await self.tool_impl._scaffold_odoo_module(**args)
            elif tool_name == "validate_module_manifest":
                return await self.additional_tools._validate_module_manifest(**args)
            elif tool_name == "analyze_module_structure":
                return await self.additional_tools._analyze_module_structure(**args)
            elif tool_name == "docker_odoo_status":
                return await self.additional_tools._docker_odoo_status(**args)
            elif tool_name == "docker_odoo_logs":
                return await self.additional_tools._docker_odoo_logs(**args)
            elif tool_name == "docker_odoo_restart":
                return await self.additional_tools._docker_odoo_restart(**args)
            elif tool_name == "docker_odoo_shell":
                return await self.additional_tools._docker_odoo_shell(**args)
            elif tool_name == "lint_python_code":
                return await self.additional_tools._lint_python_code(**args)
            elif tool_name == "format_python_code":
                return await self.additional_tools._format_python_code(**args)
            elif tool_name == "validate_xml_syntax":
                return await self.additional_tools._validate_xml_syntax(**args)
            elif tool_name == "db_backup":
                return await self.db_testing_tools._db_backup(**args)
            elif tool_name == "db_restore":
                return await self.db_testing_tools._db_restore(**args)
            elif tool_name == "db_query":
                return await self.db_testing_tools._db_query(**args)
            elif tool_name == "run_odoo_tests":
                return await self.db_testing_tools._run_odoo_tests(**args)
            elif tool_name == "generate_test_data":
                return await self.db_testing_tools._generate_test_data(**args)
            elif tool_name == "deploy_module":
                return await self.db_testing_tools._deploy_module(**args)
            elif tool_name == "generate_requirements":
                return await self.db_testing_tools._generate_requirements(**args)
            elif tool_name == "odoo_shell":
                return await self.utility_tools._odoo_shell(**args)
            elif tool_name == "check_odoo_logs":
                return await self.utility_tools._check_odoo_logs(**args)
            elif tool_name == "check_module_health":
                return await self.utility_tools._check_module_health(**args)
            else:
                raise JSONRPCError(code=INTERNAL_ERROR, message=f"Unknown tool: {tool_name}")
                
        except JSONRPCError:
            raise
        except Exception as e:
            logger.error(f"Error executing tool {request.params.name}: {str(e)}")
            raise JSONRPCError(code=INTERNAL_ERROR, message=str(e))


def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Odoo 17 MCP Server...")
        server = Odoo17MCPServer()
        logger.info("Server initialized successfully")
        logger.info("Available tools: scaffold_odoo_module, validate_module_manifest, analyze_module_structure, docker_odoo_status, docker_odoo_logs, docker_odoo_restart, docker_odoo_shell, lint_python_code, format_python_code, validate_xml_syntax, db_backup, db_restore, db_query, run_odoo_tests, generate_test_data, deploy_module, generate_requirements, odoo_shell, check_odoo_logs, check_module_health")
        asyncio.run(stdio_server(server.server))
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()