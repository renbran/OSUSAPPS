"""
Odoo 17 MCP Server - Exception Handling

This module provides custom exceptions and error handling utilities for:
- Specific error types for different failure scenarios
- Error context and debugging information
- Structured error responses
- Retry-able vs non-retry-able errors
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    EXECUTION = "execution"
    DOCKER = "docker"
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    PERMISSION = "permission"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    SYNTAX = "syntax"
    SECURITY = "security"


@dataclass
class ErrorContext:
    """Additional context information for errors."""
    tool_name: Optional[str] = None
    module_path: Optional[str] = None
    database: Optional[str] = None
    command: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    additional_info: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            k: v for k, v in {
                'tool_name': self.tool_name,
                'module_path': self.module_path,
                'database': self.database,
                'command': self.command,
                'file_path': self.file_path,
                'line_number': self.line_number,
                'additional_info': self.additional_info
            }.items() if v is not None
        }


class MCPServerException(Exception):
    """Base exception for all MCP server errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.EXECUTION,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        suggestions: Optional[List[str]] = None,
        retry_able: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.suggestions = suggestions or []
        self.retry_able = retry_able

    def format_error(self) -> str:
        """Format error message with context and suggestions."""
        severity_emoji = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.CRITICAL: "🔴"
        }

        lines = [
            f"{severity_emoji.get(self.severity, '❌')} {self.category.value.upper()} ERROR",
            f"",
            f"Message: {self.message}",
        ]

        # Add context if available
        context_dict = self.context.to_dict()
        if context_dict:
            lines.append("")
            lines.append("Context:")
            for key, value in context_dict.items():
                if key != 'additional_info':
                    lines.append(f"  • {key.replace('_', ' ').title()}: {value}")

            if self.context.additional_info:
                for key, value in self.context.additional_info.items():
                    lines.append(f"  • {key}: {value}")

        # Add suggestions if available
        if self.suggestions:
            lines.append("")
            lines.append("Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")

        # Add retry information
        if self.retry_able:
            lines.append("")
            lines.append("💡 This operation can be retried")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.format_error()


# Configuration Errors
class ConfigurationError(MCPServerException):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            suggestions=[
                "Check your .env file configuration",
                "Verify all required environment variables are set",
                "Review config.py for validation errors"
            ],
            **kwargs
        )


class MissingConfigurationError(ConfigurationError):
    """Missing required configuration."""

    def __init__(self, config_key: str, **kwargs):
        super().__init__(
            f"Missing required configuration: {config_key}",
            context=ErrorContext(additional_info={'config_key': config_key}),
            **kwargs
        )


# Validation Errors
class ValidationError(MCPServerException):
    """Input validation errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class InvalidPathError(ValidationError):
    """Invalid file or directory path."""

    def __init__(self, path: str, reason: str = "Path does not exist", **kwargs):
        super().__init__(
            f"Invalid path: {path} - {reason}",
            context=ErrorContext(file_path=path),
            suggestions=[
                "Verify the path exists",
                "Check file/directory permissions",
                "Ensure the path is accessible"
            ],
            **kwargs
        )


class InvalidModuleError(ValidationError):
    """Invalid Odoo module structure."""

    def __init__(self, module_path: str, reason: str, **kwargs):
        super().__init__(
            f"Invalid Odoo module at {module_path}: {reason}",
            context=ErrorContext(module_path=module_path),
            suggestions=[
                "Ensure __manifest__.py exists",
                "Check module structure follows Odoo standards",
                "Validate manifest file syntax"
            ],
            **kwargs
        )


# Execution Errors
class ExecutionError(MCPServerException):
    """Command or operation execution errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.MEDIUM,
            retry_able=True,
            **kwargs
        )


class CommandExecutionError(ExecutionError):
    """Command execution failed."""

    def __init__(self, command: str, returncode: int, stderr: str = "", **kwargs):
        super().__init__(
            f"Command failed with exit code {returncode}: {command}",
            context=ErrorContext(
                command=command,
                additional_info={'returncode': returncode, 'stderr': stderr[:500]}
            ),
            suggestions=[
                "Check if the command is available in PATH",
                "Verify command syntax and arguments",
                "Review error output for details"
            ],
            **kwargs
        )


class CommandNotFoundError(ExecutionError):
    """Command not found in PATH."""

    def __init__(self, command: str, **kwargs):
        super().__init__(
            f"Command not found: {command}",
            context=ErrorContext(command=command),
            severity=ErrorSeverity.HIGH,
            retry_able=False,
            suggestions=[
                f"Install {command} if not already installed",
                "Add command location to PATH",
                "Check if running in correct environment"
            ],
            **kwargs
        )


# Docker Errors
class DockerError(MCPServerException):
    """Docker-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DOCKER,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class DockerNotRunningError(DockerError):
    """Docker daemon is not running."""

    def __init__(self, **kwargs):
        super().__init__(
            "Docker daemon is not running",
            severity=ErrorSeverity.HIGH,
            retry_able=False,
            suggestions=[
                "Start Docker Desktop or Docker daemon",
                "Verify Docker is installed correctly",
                "Check Docker service status"
            ],
            **kwargs
        )


class DockerComposeError(DockerError):
    """Docker Compose operation failed."""

    def __init__(self, operation: str, details: str = "", **kwargs):
        super().__init__(
            f"Docker Compose {operation} failed: {details}",
            context=ErrorContext(additional_info={'operation': operation}),
            retry_able=True,
            suggestions=[
                "Check docker-compose.yml syntax",
                "Verify all services are configured correctly",
                "Review Docker Compose logs for errors"
            ],
            **kwargs
        )


class ContainerNotFoundError(DockerError):
    """Docker container not found."""

    def __init__(self, container: str, **kwargs):
        super().__init__(
            f"Container not found: {container}",
            context=ErrorContext(additional_info={'container': container}),
            retry_able=False,
            suggestions=[
                "Start the container with docker compose up",
                "Check if service name is correct",
                "Verify docker-compose.yml configuration"
            ],
            **kwargs
        )


# Database Errors
class DatabaseError(MCPServerException):
    """Database-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class DatabaseConnectionError(DatabaseError):
    """Cannot connect to database."""

    def __init__(self, database: str, details: str = "", **kwargs):
        super().__init__(
            f"Cannot connect to database '{database}': {details}",
            context=ErrorContext(database=database),
            retry_able=True,
            suggestions=[
                "Check if PostgreSQL is running",
                "Verify database connection parameters",
                "Check network connectivity",
                "Verify database user credentials"
            ],
            **kwargs
        )


class DatabaseNotFoundError(DatabaseError):
    """Database does not exist."""

    def __init__(self, database: str, **kwargs):
        super().__init__(
            f"Database does not exist: {database}",
            context=ErrorContext(database=database),
            retry_able=False,
            suggestions=[
                "Create the database first",
                "Check database name spelling",
                "Verify you have access to the database"
            ],
            **kwargs
        )


class DatabaseQueryError(DatabaseError):
    """SQL query execution error."""

    def __init__(self, query: str, details: str = "", **kwargs):
        super().__init__(
            f"Query execution failed: {details}",
            context=ErrorContext(command=query[:200]),
            retry_able=False,
            suggestions=[
                "Check SQL syntax",
                "Verify table and column names",
                "Review query permissions"
            ],
            **kwargs
        )


# Filesystem Errors
class FilesystemError(MCPServerException):
    """Filesystem operation errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.FILESYSTEM,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class FileNotFoundError(FilesystemError):
    """File or directory not found."""

    def __init__(self, path: str, **kwargs):
        super().__init__(
            f"File or directory not found: {path}",
            context=ErrorContext(file_path=path),
            retry_able=False,
            suggestions=[
                "Verify the path is correct",
                "Check if file exists",
                "Ensure you have read permissions"
            ],
            **kwargs
        )


class PermissionError(FilesystemError):
    """Permission denied for filesystem operation."""

    def __init__(self, path: str, operation: str = "access", **kwargs):
        super().__init__(
            f"Permission denied: Cannot {operation} {path}",
            context=ErrorContext(file_path=path),
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.HIGH,
            retry_able=False,
            suggestions=[
                "Check file/directory permissions",
                "Run with appropriate user permissions",
                "Verify ownership of the file/directory"
            ],
            **kwargs
        )


# Timeout Errors
class TimeoutError(MCPServerException):
    """Operation timeout."""

    def __init__(self, operation: str, timeout: float, **kwargs):
        super().__init__(
            f"Operation timed out after {timeout} seconds: {operation}",
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            retry_able=True,
            suggestions=[
                "Increase timeout value if operation is expected to take longer",
                "Check if operation is stuck or hanging",
                "Review system resources and performance"
            ],
            **kwargs
        )


# Security Errors
class SecurityError(MCPServerException):
    """Security-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            retry_able=False,
            **kwargs
        )


class DangerousOperationError(SecurityError):
    """Potentially dangerous operation blocked."""

    def __init__(self, operation: str, reason: str = "", **kwargs):
        super().__init__(
            f"Dangerous operation blocked: {operation}. {reason}",
            suggestions=[
                "Review the operation for safety",
                "Use appropriate safety flags if operation is intended",
                "Consider using safer alternatives"
            ],
            **kwargs
        )


class InvalidInputError(SecurityError):
    """Input validation failed for security reasons."""

    def __init__(self, input_name: str, reason: str, **kwargs):
        super().__init__(
            f"Invalid input for {input_name}: {reason}",
            severity=ErrorSeverity.HIGH,
            suggestions=[
                "Review input format requirements",
                "Check for invalid characters",
                "Ensure input meets security constraints"
            ],
            **kwargs
        )


# Syntax Errors
class SyntaxError(MCPServerException):
    """Code or configuration syntax errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.HIGH,
            retry_able=False,
            **kwargs
        )


class PythonSyntaxError(SyntaxError):
    """Python code syntax error."""

    def __init__(self, file_path: str, line: int, details: str, **kwargs):
        super().__init__(
            f"Python syntax error in {file_path} at line {line}: {details}",
            context=ErrorContext(file_path=file_path, line_number=line),
            suggestions=[
                "Check Python syntax",
                "Review the specific line mentioned",
                "Use a linter to identify issues"
            ],
            **kwargs
        )


class XMLSyntaxError(SyntaxError):
    """XML syntax error."""

    def __init__(self, file_path: str, details: str, **kwargs):
        super().__init__(
            f"XML syntax error in {file_path}: {details}",
            context=ErrorContext(file_path=file_path),
            suggestions=[
                "Validate XML structure",
                "Check for unclosed tags",
                "Verify XML namespaces"
            ],
            **kwargs
        )


def handle_exception(exc: Exception, tool_name: str = None) -> str:
    """
    Handle exceptions and format error messages.

    Args:
        exc: Exception to handle
        tool_name: Name of the tool where exception occurred

    Returns:
        Formatted error message
    """
    if isinstance(exc, MCPServerException):
        if tool_name and not exc.context.tool_name:
            exc.context.tool_name = tool_name
        return exc.format_error()
    else:
        # Generic exception handling
        return f"❌ Unexpected error: {str(exc)}\n\nPlease report this issue if it persists."


def create_error_context(
    tool_name: str = None,
    **kwargs
) -> ErrorContext:
    """
    Create error context from keyword arguments.

    Args:
        tool_name: Tool name
        **kwargs: Additional context fields

    Returns:
        ErrorContext instance
    """
    return ErrorContext(
        tool_name=tool_name,
        **{k: v for k, v in kwargs.items() if k in ErrorContext.__annotations__}
    )
